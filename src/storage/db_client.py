import os
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, and_, update
from sqlalchemy.orm import sessionmaker
from src.storage.models import Base, KnowledgeObject, GraphEdge

# Import Supabase
try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

class DatabaseClient:
    def __init__(self, database_url: str = "sqlite:///:memory:"):
        """
        Initializes the DB Client. Defaults to in-memory SQLite for testing/MVP.
        Syncs automatically to Supabase if environment variables are provided.
        """
        self.engine = create_engine(database_url)
        Base.metadata.create_create_all = Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Optional Supabase integration
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
        
        if create_client and supabase_url and supabase_key:
            try:
                self.supabase = create_client(supabase_url, supabase_key)
                print("[*] Supabase connection initialized successfully for DB sync.")
            except Exception as e:
                print(f"[!] Warning: Failed to init Supabase client: {e}")
                self.supabase = None
        else:
            self.supabase = None

    def publish_ko(self, ko_data: dict, system_time: Optional[datetime] = None) -> None:
        """
        Publishes/mirrors a Knowledge Object JSON into the relational database.
        Maintains bi-temporal timelines and updates predecessor system time.
        """
        if system_time is None:
            system_time = datetime.utcnow()

        urn = ko_data["urn"]
        version = ko_data["version"]
        legal_start = datetime.strptime(ko_data["date"], "%Y-%m-%d")

        session = self.Session()
        try:
            # 1. Look for a previous version to supersede in system time (local SQLite)
            if version > 1:
                prev_version = version - 1
                stmt = (
                    update(KnowledgeObject)
                    .where(and_(KnowledgeObject.urn == urn, KnowledgeObject.version == prev_version))
                    .values(system_time_end=system_time)
                )
                session.execute(stmt)

            # 2. Construct the DB object
            db_ko = KnowledgeObject(
                urn=urn,
                version=version,
                type=ko_data.get("type", "node"),
                title=ko_data["title"],
                summary=ko_data["summary"],
                confidence_score=ko_data["confidence_score"],
                system_time_start=system_time,
                system_time_end=None, # Active in system time
                legal_time_start=legal_start,
                legal_time_end=None,
                body=ko_data,
                business_impact=ko_data["business_impact"],
                evidence=ko_data["evidence"],
                linked_objects=ko_data["linked_objects"]
            )
            # Extract type from URN if default
            if db_ko.type == "node" or not db_ko.type:
                urn_parts = urn.split(":")
                db_ko.type = urn_parts[4].capitalize() if len(urn_parts) > 4 else "Node"

            session.add(db_ko)

            # 3. Insert new Graph Edges (local SQLite)
            for rel in ko_data.get("relations", []):
                edge = GraphEdge(
                    source_urn=urn,
                    source_version=version,
                    target_urn=rel["target_urn"],
                    edge_type=rel["edge_type"]
                )
                session.add(edge)

            session.commit()
            
            # 4. Mirror to Supabase Cloud if configured
            if self.supabase:
                try:
                    # Update previous version in system time
                    if version > 1:
                        prev_version = version - 1
                        self.supabase.table("knowledge_objects").update({
                            "system_time_end": system_time.isoformat() + "Z"
                        }).match({
                            "urn": urn,
                            "version": prev_version
                        }).execute()
                    
                    # Upsert current Knowledge Object
                    self.supabase.table("knowledge_objects").upsert({
                        "urn": urn,
                        "version": version,
                        "type": db_ko.type,
                        "title": ko_data["title"],
                        "summary": ko_data["summary"],
                        "confidence_score": float(ko_data["confidence_score"]),
                        "source_credibility": ko_data.get("source_credibility"),
                        "forum_published": ko_data.get("forum_published"),
                        "interpretation_stance": ko_data.get("interpretation_stance"),
                        "system_time_start": system_time.isoformat() + "Z",
                        "system_time_end": None,
                        "legal_time_start": legal_start.isoformat() + "Z",
                        "legal_time_end": None,
                        "body": ko_data,
                        "business_impact": ko_data["business_impact"],
                        "evidence": ko_data["evidence"],
                        "linked_objects": ko_data["linked_objects"],
                        "entities": ko_data.get("entities", []),
                        "relations": ko_data.get("relations", [])
                    }).execute()
                    
                    # Upsert graph edges
                    for rel in ko_data.get("relations", []):
                        self.supabase.table("graph_edges").upsert({
                            "source_urn": urn,
                            "source_version": version,
                            "target_urn": rel["target_urn"],
                            "edge_type": rel["edge_type"]
                        }).execute()
                    print(f"[+] Successfully synced URN '{urn}' (v{version}) to Supabase cloud.")
                except Exception as ex:
                    print(f"[!] Warning: Failed to sync URN '{urn}' to Supabase: {ex}")
                    
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_ko_at_time(
        self, 
        urn: str, 
        system_time: datetime, 
        legal_time: datetime
    ) -> Optional[KnowledgeObject]:
        """
        Bi-temporal Query: Fetches the state of a KO as it existed relative to:
        - System Time (Transaction time: when was it committed)
        - Legal Time (Validity time: when was it legally active)
        """
        session = self.Session()
        try:
            query = session.query(KnowledgeObject).filter(
                KnowledgeObject.urn == urn,
                # System Time range match
                KnowledgeObject.system_time_start <= system_time,
                (KnowledgeObject.system_time_end == None) | (KnowledgeObject.system_time_end > system_time),
                # Legal Time range match
                KnowledgeObject.legal_time_start <= legal_time,
                (KnowledgeObject.legal_time_end == None) | (KnowledgeObject.legal_time_end > legal_time)
            )
            return query.first()
        finally:
            session.close()

    def get_relations(self, urn: str, version: int) -> List[GraphEdge]:
        """
        Retrieves all outbound relationships (edges) for a given KO version.
        """
        session = self.Session()
        try:
            return session.query(GraphEdge).filter(
                GraphEdge.source_urn == urn,
                GraphEdge.source_version == version
            ).all()
        finally:
            session.close()
