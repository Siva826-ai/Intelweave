import re
import uuid
from typing import List, Dict, Any
from app.ai.models import AnomalyModel
import pandas as pd

class ForensicAgent:
    def __init__(self):
        self.anomaly_model = AnomalyModel()
        
    def analyze_document(self, text: str) -> Dict[str, Any]:
        """
        Coordinated entry point for document analysis.
        """
        entities = self.discover_entities(text)
        relationships = self.reason_relationships(entities, text)
        insights = self.generate_insights(entities, relationships, text)
        
        return {
            "entities": entities,
            "relationships": relationships,
            "insights": insights
        }

    def discover_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Basic NER using regex and patterns for the forensic context.
        """
        entities = []
        
        # 1. Names (Simple Title Case heuristic for Mock)
        # In a real agent, we would use a spaCy or similar NER model here.
        name_pattern = r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b"
        names = set(re.findall(name_pattern, text))
        
        for name in names:
            # Avoid common false positives
            if name in ["Date", "Name", "Sex", "Age", "DOB", "Eyes", "Hair", "Teeth", "Medical Examiner"]:
                continue
                
            entities.append({
                "label": name,
                "type": "person",
                "risk_score": 0.0,
                "confidence_score": 85.0
            })

        # 2. Addresses
        address_pattern = r"\d+ [A-Z][a-z]+ (Ave|St|Rd|Blvd|Drive)"
        addresses = set(re.findall(address_pattern, text))
        for addr in addresses:
            entities.append({
                "label": addr,
                "type": "ip", # Mapping to existing IP/Device/Other types for now
                "risk_score": 0.0,
                "confidence_score": 90.0
            })
            
        return entities

    def reason_relationships(self, entities: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        """
        Infers links based on proximity and keywords.
        """
        relationships = []
        text_lower = text.lower()
        
        # Simple proximity-based relationship detection
        for i, e1 in enumerate(entities):
            for j, e2 in enumerate(entities):
                if i >= j: continue
                
                # Check if they appear near each other or specific keywords exist
                if e1["label"] in text and e2["label"] in text:
                    if "altercation" in text_lower or "party" in text_lower or "house" in text_lower:
                        relationships.append({
                            "source_label": e1["label"],
                            "target_label": e2["label"],
                            "basis": "Co-occurrence in Incident Report",
                            "strength_score": 75.0,
                            "confidence_score": 70.0
                        })
        
        return relationships

    def generate_insights(self, entities: List[Any], relationships: List[Any], text: str) -> List[Dict[str, Any]]:
        """
        Synthesizes findings into forensic insights.
        """
        insights = []
        text_lower = text.lower()
        
        # 1. Toxicology Check
        toxic_keywords = ["positive", "cocaine", "morphine", "heroin", "oxycodone"]
        if any(kw in text_lower for kw in toxic_keywords):
            insights.append({
                "severity": "critical",
                "summary": "Positive Toxicology Detected",
                "explanation": "Document indicates positive results for controlled substances (Cocaine/Morphine group).",
                "confidence_score": 95.0
            })
            
        # 2. Physical Trauma
        trauma_keywords = ["abrasion", "contusion", "laceration", "fracture"]
        if any(kw in text_lower for kw in trauma_keywords):
            insights.append({
                "severity": "high",
                "summary": "Recent Physical Trauma Observed",
                "explanation": "Medical report identifies multiple trauma points suggesting a physical altercation.",
                "confidence_score": 90.0
            })
            
        return insights
