"""
API Gateway — Layer 3: Application Interface Layer

Purpose:
    Exposes the Regulatory Knowledge Infrastructure endpoints to downstream
    applications (like SaralPrivacy) via FastAPI.
    Supports bi-temporal object retrieval, grounded reasoning queries,
    and ledger differences extraction.
"""

import os
import secrets
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.storage.db_client import DatabaseClient
from src.reasoning.reasoning_engine import GroundedReasoningEngine
from src.reasoning.model_client import ModelClient

# Initialize FastAPI App
app = FastAPI(
    title="Regulatory Knowledge Infrastructure API Gateway",
    description="Bi-temporal API for querying and exploring DPDPA knowledge.",
    version="1.0.0"
)

# Enable CORS
#
# Origins are configurable so the same image serves local dev, Vercel preview
# builds and production. Set ALLOWED_ORIGINS to a comma-separated list, or to
# "*" to allow any origin.
#
# Note: the CORS spec forbids pairing a "*" origin with credentialed requests —
# browsers reject the response. So credentials are only enabled when an explicit
# origin allow-list is configured.
DEFAULT_ALLOWED_ORIGINS = [
    "https://dpdpa.wiki",
    "https://www.dpdpa.wiki",
    "https://dpdpa.shiksha",
    "https://www.dpdpa.shiksha",
    "http://localhost:5173",
    "http://localhost:4173",
    "http://localhost:4174",
    "http://localhost:4180",
]

_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
if _origins_env == "*":
    allowed_origins: List[str] = ["*"]
elif _origins_env:
    allowed_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]
else:
    allowed_origins = DEFAULT_ALLOWED_ORIGINS

# Vercel preview deployments get a generated subdomain per build.
allow_origin_regex = os.getenv("ALLOWED_ORIGIN_REGEX", r"https://.*\.vercel\.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=None if allowed_origins == ["*"] else allow_origin_regex,
    allow_credentials=allowed_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared clients (can be customized or injected during app startup)
#
# `or` rather than a getenv default: a blank DATABASE_URL= line in .env yields
# "" from the two-arg form, which SQLAlchemy cannot parse — the API would then
# crash on import rather than fall back to the in-memory database.
db_url = os.getenv("DATABASE_URL") or "sqlite:///:memory:"
db_client = DatabaseClient(db_url)
 
AUDIT_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "staging", "search_audit.log")


def _env_int(name: str, default: int) -> int:
    try:
        return max(1, int((os.getenv(name) or "").strip() or default))
    except ValueError:
        return default


def _serialize_knowledge_object(
    ko,
    include_relations: bool = True,
):
    """Serialize a persisted KnowledgeObject for API responses."""
    return {
        "urn": ko.urn,
        "version": ko.version,
        "type": ko.type,
        "title": ko.title,
        "summary": ko.summary,
        "confidence_score": float(ko.confidence_score),
        "system_time_start": ko.system_time_start.isoformat() if ko.system_time_start else None,
        "system_time_end": ko.system_time_end.isoformat() if ko.system_time_end else None,
        "legal_time_start": ko.legal_time_start.isoformat() if ko.legal_time_start else None,
        "legal_time_end": ko.legal_time_end.isoformat() if ko.legal_time_end else None,
        "status": "active" if ko.system_time_end is None else "superseded",
        "body": ko.body,
        "business_impact": ko.business_impact,
        "evidence": ko.evidence,
        "linked_objects": ko.linked_objects,
        "interpretation_stance": ko.interpretation_stance,
        "source_credibility": ko.source_credibility,
        "forum_published": ko.forum_published,
        "relations": [
            {"target_urn": edge.target_urn, "edge_type": edge.edge_type}
            for edge in db_client.get_relations(ko.urn, ko.version)
        ] if include_relations else []
    }


class SlidingWindowRateLimiter:
    """Small process-local limiter for the first deployment milestone."""

    def __init__(self):
        self._events = defaultdict(deque)
        self._lock = Lock()

    def enforce(self, scope: str, identifier: str, limit: int, window_seconds: int):
        now = time.monotonic()
        key = (scope, identifier)
        with self._lock:
            events = self._events[key]
            cutoff = now - window_seconds
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                retry_after = max(1, int(window_seconds - (now - events[0])))
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded.",
                    headers={"Retry-After": str(retry_after)},
                )
            events.append(now)

    def reset(self):
        with self._lock:
            self._events.clear()


query_rate_limiter = SlidingWindowRateLimiter()


def _client_identifier(request: Request) -> str:
    if os.getenv("TRUST_PROXY_HEADERS") == "1":
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def enforce_query_rate_limit(request: Request) -> None:
    if os.getenv("DISABLE_RATE_LIMITS") == "1":
        return
    identifier = _client_identifier(request)
    query_rate_limiter.enforce(
        "query-minute",
        identifier,
        _env_int("QUERY_RATE_LIMIT_PER_MINUTE", 10),
        60,
    )
    query_rate_limiter.enforce(
        "query-day",
        identifier,
        _env_int("QUERY_RATE_LIMIT_PER_DAY", 100),
        86_400,
    )


def require_admin(x_admin_key: str = Header(default="")) -> None:
    """Fail-closed transitional protection for all administrative routes."""
    configured_key = (os.getenv("ADMIN_API_KEY") or "").strip()
    if not configured_key:
        raise HTTPException(status_code=503, detail="Admin surface not configured.")
    if not secrets.compare_digest(x_admin_key, configured_key):
        raise HTTPException(status_code=401, detail="Invalid or missing admin key.")


def log_search_query(
    query: str,
    grounded: bool = True,
    cited_urns: Optional[List[str]] = None,
    duration_ms: float = 0.0,
):
    try:
        os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
        import json
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "query": query,
            "grounded": grounded,
            "cited_urns": cited_urns or [],
            "duration_ms": duration_ms,
        }
        with open(AUDIT_LOG_PATH, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as le:
        print(f"[!] Warning: Failed to write search audit log: {le}")
model_client = ModelClient()
reasoning_engine = GroundedReasoningEngine(db_client=db_client, model_client=model_client)


# ─── Pydantic Schemas ────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=_env_int("QUERY_MAX_CHARS", 4000))

class QueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[Dict]
    grounded: bool
    cited_urns: List[str] = Field(default_factory=list)
    trace: Optional[Dict] = None


# ─── API Endpoints ──────────────────────────────────────────────────────────

@app.get("/health")
def get_health() -> Dict[str, str]:
    """
    Returns API gateway service status.
    """
    return {"status": "HEALTHY", "timestamp": datetime.utcnow().isoformat()}


@app.get("/health/ready")
def get_readiness() -> Dict:
    """Fail readiness in production when no live model route is configured."""
    environment = (os.getenv("APP_ENV") or "development").strip().lower()
    model_configured = model_client.is_configured
    if environment == "production" and not model_configured:
        raise HTTPException(
            status_code=503,
            detail="No production model provider is configured.",
        )
    return {
        "status": "READY",
        "timestamp": datetime.utcnow().isoformat(),
        "model_configured": model_configured,
        "mode": "live" if model_configured else "offline",
    }


@app.post(
    "/knowledge/query",
    response_model=QueryResponse,
    dependencies=[Depends(enforce_query_rate_limit)],
)
def post_query(request: QueryRequest) -> Dict:
    """
    Executes a query through the Grounded Reasoning Engine, returning a response
    guaranteed to be cited from database evidence coordinates.
    """
    try:
        response = reasoning_engine.query(request.query)
        log_search_query(
            request.query,
            response.get("grounded", False),
            response.get("cited_urns", []),
            response.get("trace", {}).get("total_duration_ms", 0.0),
        )
        return response
    except Exception as e:
        try:
            log_search_query(request.query, False)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Query execution failed.")


@app.get("/knowledge/objects/{urn}")
def get_knowledge_object(
    urn: str,
    system_time: Optional[str] = Query(None, description="ISO timestamp (system transaction state)"),
    legal_time: Optional[str] = Query(None, description="ISO timestamp (legal validity state)")
) -> Dict:
    """
    Fetches the bi-temporal state of a Knowledge Object.
    Defaults to the latest active version if timestamps are omitted.
    """
    session = db_client.Session()
    try:
        from src.storage.models import KnowledgeObject
        
        # 1. Parse search times
        sys_dt = datetime.fromisoformat(system_time) if system_time else datetime.utcnow()
        leg_dt = datetime.fromisoformat(legal_time) if legal_time else datetime.utcnow()

        # 2. Execute query
        db_ko = db_client.get_ko_at_time(urn, sys_dt, leg_dt)
        
        if not db_ko:
            # Check if URN exists at all
            exists = session.query(KnowledgeObject).filter(KnowledgeObject.urn == urn).first()
            if exists:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Knowledge Object URN '{urn}' exists but is not active at specified bi-temporal coordinates."
                )
            raise HTTPException(
                status_code=404, 
                detail=f"Knowledge Object URN '{urn}' not found."
            )

        return _serialize_knowledge_object(db_ko)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid timestamp format: {str(e)}")
    finally:
        session.close()


@app.get("/knowledge/graph/diff")
def get_graph_diff(
    since_timestamp: str = Query(..., description="ISO 8601 timestamp to check for changes since")
) -> Dict:
    """
    Returns all updates to the graph (newly published KOs) since a given timestamp.
    """
    try:
        since_dt = datetime.fromisoformat(since_timestamp)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid since_timestamp format. Use ISO 8601.")

    session = db_client.Session()
    try:
        from src.storage.models import KnowledgeObject
        
        # Query active KOs created since the timestamp
        updates = session.query(KnowledgeObject).filter(
            KnowledgeObject.system_time_start >= since_dt
        ).all()
        
        return {
            "since_timestamp": since_timestamp,
            "updates_count": len(updates),
            "updates": [
                {
                    "urn": ko.urn,
                    "version": ko.version,
                    "title": ko.title,
                    "published_at": ko.system_time_start.isoformat()
                } for ko in updates
            ]
        }
    finally:
        session.close()


@app.get("/knowledge/search")
def search_knowledge_objects(
    q: str = Query("", min_length=0, description="Case-insensitive phrase match in title and summary"),
    type_: str = Query(None, alias="type", description="Filter by KO type, e.g. Act or Rule"),
    include_inactive: bool = Query(False, description="Include superseded versions"),
    min_confidence: Optional[float] = Query(None, ge=0, le=1, description="Minimum confidence score"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Result offset"),
    order_by: str = Query("system", description="system|legal|confidence"),
    since: Optional[str] = Query(None, description="Optional ISO date-time to include only items touched after"),
) -> Dict:
    """
    Full-text-like discovery endpoint for content surfaces (Acts, Rules, Interpretations,
    Discussions). Designed for timeline and category pages.
    """
    from src.storage.models import KnowledgeObject

    session = db_client.Session()
    try:
        query = session.query(KnowledgeObject)

        if q:
            like_expr = f"%{q}%"
            query = query.filter(
                (KnowledgeObject.title.ilike(like_expr))
                | (KnowledgeObject.summary.ilike(like_expr))
            )

        if type_:
            query = query.filter(KnowledgeObject.type.ilike(type_))

        if not include_inactive:
            query = query.filter(KnowledgeObject.system_time_end == None)  # noqa: E711

        if min_confidence is not None:
            query = query.filter(KnowledgeObject.confidence_score >= min_confidence)

        if since:
            try:
                since_dt = datetime.fromisoformat(since)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid since format: {str(e)}")
            query = query.filter(KnowledgeObject.system_time_start >= since_dt)

        if order_by == "legal":
            query = query.order_by(KnowledgeObject.legal_time_start.desc())
        elif order_by == "confidence":
            query = query.order_by(KnowledgeObject.confidence_score.desc())
        else:
            query = query.order_by(KnowledgeObject.system_time_start.desc())

        total = query.count()
        items = query.offset(offset).limit(limit).all()
        return {
            "query": q,
            "count": total,
            "limit": limit,
            "offset": offset,
            "items": [
                _serialize_knowledge_object(ko)
                for ko in items
            ]
        }
    finally:
        session.close()


@app.get("/knowledge/changes")
def get_changes(
    since_timestamp: Optional[str] = Query(None, description="ISO 8601 timestamp to check for changes since")
) -> Dict:
    """
    Returns all knowledge object versions with a transaction touchpoint since a given timestamp.
    """
    if not since_timestamp:
        since_timestamp = (datetime.utcnow() - timedelta(days=30)).isoformat()

    try:
        since_dt = datetime.fromisoformat(since_timestamp)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid since_timestamp format. Use ISO 8601.")

    session = db_client.Session()
    try:
        from src.storage.models import KnowledgeObject

        updates = session.query(KnowledgeObject).filter(
            (KnowledgeObject.system_time_start >= since_dt)
            | ((KnowledgeObject.system_time_end != None) & (KnowledgeObject.system_time_end >= since_dt))  # noqa: E711
        ).order_by(KnowledgeObject.system_time_start.desc()).all()

        return {
            "since_timestamp": since_timestamp,
            "updates_count": len(updates),
            "updates": [
                {
                    "urn": ko.urn,
                    "version": ko.version,
                    "title": ko.title,
                    "event": "published" if ko.system_time_start >= since_dt else "superseded",
                    "system_time_start": ko.system_time_start.isoformat() if ko.system_time_start else None,
                    "system_time_end": ko.system_time_end.isoformat() if ko.system_time_end else None,
                    "legal_time_start": ko.legal_time_start.isoformat() if ko.legal_time_start else None,
                    "legal_time_end": ko.legal_time_end.isoformat() if ko.legal_time_end else None,
                    "type": ko.type
                }
                for ko in updates
            ]
        }
    finally:
        session.close()


@app.get("/knowledge/sections/{urn}/history")
def get_section_history(urn: str) -> Dict:
    """
    Fetches all published versions for a Knowledge Object grouped by URN.
    Use this on legal timeline screens and interpretation supersession views.
    """
    session = db_client.Session()
    try:
        from src.storage.models import KnowledgeObject

        versions = session.query(KnowledgeObject).filter(
            KnowledgeObject.urn == urn
        ).order_by(KnowledgeObject.version.desc(), KnowledgeObject.system_time_start.desc()).all()

        if not versions:
            raise HTTPException(status_code=404, detail=f"Knowledge Object URN '{urn}' not found.")

        return {
            "urn": urn,
            "history_count": len(versions),
            "versions": [
                {
                    "version": ko.version,
                    "status": "active" if ko.system_time_end is None else "superseded",
                    "system_time_start": ko.system_time_start.isoformat() if ko.system_time_start else None,
                    "system_time_end": ko.system_time_end.isoformat() if ko.system_time_end else None,
                    "legal_time_start": ko.legal_time_start.isoformat() if ko.legal_time_start else None,
                    "legal_time_end": ko.legal_time_end.isoformat() if ko.legal_time_end else None,
                    "type": ko.type,
                    "title": ko.title,
                    "summary": ko.summary,
                    "confidence_score": float(ko.confidence_score),
                    "relations": [
                        {"target_urn": edge.target_urn, "edge_type": edge.edge_type}
                        for edge in db_client.get_relations(ko.urn, ko.version)
                    ]
                }
                for ko in versions
            ]
        }
    finally:
        session.close()
 
 
@app.get("/admin/search-audit", dependencies=[Depends(require_admin)])
def get_search_audit() -> Dict:
    """
    Returns the recent search queries logged by users for administrative auditing.
    """
    logs = []
    if os.path.exists(AUDIT_LOG_PATH):
        try:
            with open(AUDIT_LOG_PATH, "r") as f:
                lines = f.readlines()
            import json
            for line in reversed(lines[-100:]):
                line_str = line.strip()
                if line_str:
                    logs.append(json.loads(line_str))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read audit log: {str(e)}")
    return {"logs": logs}
 
 
@app.get("/admin/stats", dependencies=[Depends(require_admin)])
def get_admin_stats() -> Dict:
    """
    Computes and returns database statistics categorizing KOs by their trust layer:
    - Layer 1: Core (Primary Authority - Act & Rules)
    - Layer 4: Opinions (Expert Opinions)
    - Others: Judicial, Regulatory, Industry guidelines
    """
    session = db_client.Session()
    try:
        from src.storage.models import KnowledgeObject
        active_kos = session.query(KnowledgeObject).filter(
            KnowledgeObject.system_time_end == None
        ).all()
        
        core_count = 0
        opinion_count = 0
        other_count = 0
        
        for ko in active_kos:
            layer = ko.body.get("source", {}).get("layer", 1)
            if layer == 1:
                core_count += 1
            elif layer == 4:
                opinion_count += 1
            else:
                other_count += 1
                
        return {
            "total_knowledge_objects": len(active_kos),
            "core_layer_count": core_count,
            "opinion_layer_count": opinion_count,
            "other_layers_count": other_count
        }
    finally:
        session.close()


INGESTION_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "staging", "ingestion_audit.log"))
BIBLE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "DPDPA_BIBLE.md"))

@app.get("/admin/ingestion-audit", dependencies=[Depends(require_admin)])
def get_ingestion_audit() -> Dict:
    """
    Returns the recent document ingestion pipeline execution runs for auditing.
    """
    logs = []
    if os.path.exists(INGESTION_LOG_PATH):
        try:
            with open(INGESTION_LOG_PATH, "r") as f:
                lines = f.readlines()
            import json
            for line in reversed(lines[-100:]):
                line_str = line.strip()
                if line_str:
                    logs.append(json.loads(line_str))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read ingestion audit log: {str(e)}")
    return {"logs": logs}


@app.get("/knowledge/bible")
def get_bible_content() -> Dict:
    """
    Returns the raw markdown contents of the DPDPA Bible reference document.
    """
    if not os.path.exists(BIBLE_PATH):
        raise HTTPException(status_code=404, detail="DPDPA Bible document not found.")
    try:
        with open(BIBLE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read DPDPA Bible: {str(e)}")


@app.get("/api/v1/diff")
def compute_text_diff(source_a: str = Query(...), source_b: str = Query(...)) -> Dict:
    """
    Computes a side-by-side color-coded legal redline diff between two document texts or URNs.
    """
    import difflib
    lines_a = source_a.splitlines()
    lines_b = source_b.splitlines()
    matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
    
    diff_output = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for line in lines_a[i1:i2]:
                diff_output.append({"type": "unchanged", "text": line})
        elif tag == 'replace':
            for line in lines_a[i1:i2]:
                diff_output.append({"type": "deletion", "text": line})
            for line in lines_b[j1:j2]:
                diff_output.append({"type": "addition", "text": line})
        elif tag == 'delete':
            for line in lines_a[i1:i2]:
                diff_output.append({"type": "deletion", "text": line})
        elif tag == 'insert':
            for line in lines_b[j1:j2]:
                diff_output.append({"type": "addition", "text": line})
                
    return {"diff": diff_output}
