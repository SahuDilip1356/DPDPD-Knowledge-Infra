from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, JSON, PrimaryKeyConstraint, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class KnowledgeObject(Base):
    __tablename__ = "knowledge_objects"

    urn = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(512), nullable=False)
    summary = Column(String, nullable=False)
    confidence_score = Column(Numeric(3, 2), nullable=False)
    
    # Bi-temporal coordinates
    system_time_start = Column(DateTime, nullable=False, default=datetime.utcnow)
    system_time_end = Column(DateTime, nullable=True) # Null indicates the active version
    
    legal_time_start = Column(DateTime, nullable=False)
    legal_time_end = Column(DateTime, nullable=True)

    # Dynamic JSON payloads
    body = Column(JSON, nullable=False)
    business_impact = Column(JSON, nullable=False)
    evidence = Column(JSON, nullable=False)
    linked_objects = Column(JSON, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("urn", "version"),
    )

class GraphEdge(Base):
    __tablename__ = "graph_edges"

    source_urn = Column(String(255), nullable=False)
    source_version = Column(Integer, nullable=False)
    target_urn = Column(String(255), nullable=False)
    edge_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        PrimaryKeyConstraint("source_urn", "source_version", "target_urn", "edge_type"),
    )
