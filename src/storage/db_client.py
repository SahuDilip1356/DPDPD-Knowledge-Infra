from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, and_, update
from sqlalchemy.orm import sessionmaker
from src.storage.models import Base, KnowledgeObject, GraphEdge

class DatabaseClient:
    def __init__(self, database_url: str = "sqlite:///:memory:"):
        """
        Initializes the DB Client. Defaults to in-memory SQLite for testing/MVP.
        """
        self.engine = create_engine(database_url)
        Base.metadata.create_create_all = Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

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
            # 1. Look for a previous version to supersede in system time
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
                type=ko_data["source"]["layer"], # Storing layer for mapping or type
                title=ko_data["title"],
                summary=ko_data["summary"],
                confidence_score=ko_data["confidence_score"],
                system_time_start=system_time,
                system_time_end=None, # Active in system time
                legal_time_start=legal_start,
                legal_time_end=None,
                body=ko_data.get("body", {}),
                business_impact=ko_data["business_impact"],
                evidence=ko_data["evidence"],
                linked_objects=ko_data["linked_objects"]
            )
            # Override type with string mapping
            db_ko.type = ko_data["relations"][0]["edge_type"] if ko_data["relations"] else "node"
            db_ko.type = ko_data["type"] # Use standard schema type

            session.add(db_ko)

            # 3. Insert new Graph Edges
            for rel in ko_data["relations"]:
                edge = GraphEdge(
                    source_urn=urn,
                    source_version=version,
                    target_urn=rel["target_urn"],
                    edge_type=rel["edge_type"]
                )
                session.add(edge)

            session.commit()
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
