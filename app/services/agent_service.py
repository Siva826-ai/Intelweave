from sqlalchemy.orm import Session
from uuid import UUID
from app.ai.agent import ForensicAgent
from app.db import models
from app.repositories import entity_repository, relationship_repository, insight_repository
from app.services import entity_service
from app.db.schemas import EntityCreate, InsightCreate

class AgentService:
    def __init__(self):
        self.agent = ForensicAgent()

    def run_forensic_discovery(self, db: Session, job_id: UUID, text_content: str):
        """
        Coordinates the agent's reasoning and persists findings to the database.
        """
        # 1. Get Job and Case Details
        job = db.get(models.IngestJob, job_id)
        if not job:
            return
        
        case_id = job.case_id
        
        # 2. Run AI Agent Analysis
        findings = self.agent.analyze_document(text_content)
        
        # 3. Persist Entities
        entity_map = {} # Map labels to created Entity IDs for relationships
        for entity_data in findings["entities"]:
            # Check if exists in case already (optional, simple version creates if not in case)
            db_entity = entity_repository.create_entity(
                db, 
                entity_type=entity_data["type"],
                label=entity_data["label"],
                risk_score=entity_data["risk_score"],
                confidence_score=entity_data["confidence_score"]
            )
            # Link to case
            case_entity = models.CaseEntity(case_id=case_id, entity_id=db_entity.entity_id)
            db.add(case_entity)
            entity_map[entity_data["label"]] = db_entity.entity_id

        # 4. Persist Relationships
        for rel_data in findings["relationships"]:
            source_id = entity_map.get(rel_data["source_label"])
            target_id = entity_map.get(rel_data["target_label"])
            
            if source_id and target_id:
                relationship_repository.create_relationship(
                    db,
                    case_id=case_id,
                    source_id=source_id,
                    target_id=target_id,
                    basis=rel_data["basis"],
                    strength=rel_data["strength_score"],
                    confidence=rel_data["confidence_score"]
                )

        # 5. Persist Insights
        for insight_data in findings["insights"]:
            insight_repository.create_insight(
                db,
                case_id=case_id,
                severity=insight_data["severity"],
                summary=insight_data["summary"],
                explanation=insight_data["explanation"],
                confidence_score=insight_data["confidence_score"],
                created_by=None # System generated
            )
            
        db.commit()

agent_service = AgentService()
