import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime
import sys
import os

# Ensure the project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock SQLAlchemy Session and Models
from app.db.models import Relationship, EvidenceItem, Export, IngestJob
from app.db.schemas import RelationshipCreate, EvidenceCreate, IngestJobCreate
from app.services import relationship_service, evidence_service, audit_service, export_service, ingest_service

class TestServices(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.user_id = uuid4()
        self.case_id = uuid4()

    def test_log_action(self):
        audit_service.log_action(
            self.mock_db, self.user_id, "create", "test_target", "123", self.case_id
        )
        # Verify db.add was called
        self.mock_db.add.assert_called()
        # Verify commit
        self.mock_db.commit.assert_called()

    def test_create_relationship(self):
        payload = RelationshipCreate(
            source_entity_id=uuid4(),
            target_entity_id=uuid4(),
            basis="Test Basis",
            strength_score=80.0,
            confidence_score=90.0
        )
        
        rel = relationship_service.create_relationship(
            self.mock_db, self.case_id, payload, self.user_id
        )
        
        self.mock_db.add.assert_called()
        self.assertEqual(rel.basis, "Test Basis")
        self.assertEqual(rel.confidence_score, 90.0)

    def test_create_evidence_hashing(self):
        payload = EvidenceCreate(
            evidence_type="Document",
            description="Important file"
        )
        
        evidence = evidence_service.create_evidence(
            self.mock_db, self.case_id, payload, self.user_id
        )
        
        self.mock_db.add.assert_called()
        self.assertTrue(evidence.evidence_hash) # Hash should be generated

    def test_create_export_record(self):
        # Mocking sha256_file to avoid file IO dependencies in unit test if needed, 
        # but here we just test record creation logic
        export = export_service.create_export_record(
            self.mock_db, self.case_id, "pdf", self.user_id, "mock_hash_123"
        )
        self.assertEqual(export.export_hash, "mock_hash_123")
        self.mock_db.add.assert_called()

    def test_ingest_job_flow(self):
        job_data = IngestJobCreate(source_type="csv")
        job = ingest_service.create_ingest_job(
            self.mock_db, self.case_id, job_data, self.user_id
        )
        self.assertEqual(job.status, "queued")
        
        # Add file
        ingest_service.add_file_to_job(
            self.mock_db, job.job_id, "test.csv", "text/csv", "hash123", 100
        )
        self.assertEqual(self.mock_db.add.call_count, 2) # 1 for job, 1 for file

if __name__ == "__main__":
    unittest.main()
