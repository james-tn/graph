#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Contract Extraction Core Logic

LLM-powered extraction of contract metadata, clauses, and analysis.
Uses OpenAI structured outputs with Pydantic models for robust parsing.
"""

import os
from pathlib import Path
from typing import Any, Optional, Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Configuration
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
if not AZURE_OPENAI_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
print(AZURE_OPENAI_ENDPOINT.endswith("/"))
if not AZURE_OPENAI_ENDPOINT:
    raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
base_url=AZURE_OPENAI_ENDPOINT + "/openai/v1/" if not AZURE_OPENAI_ENDPOINT.endswith("v1/") else AZURE_OPENAI_ENDPOINT 
print("base_url ", base_url)
# OpenAI client
openai_client = OpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    base_url=base_url
)

LLM_MODEL = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-small")

# Standardized enumerations matching database schema
CLAUSE_TYPES = [
    "Definitions",
    "Indemnification",
    "Limitation of Liability",
    "Confidentiality",
    "Intellectual Property",
    "Termination",
    "Payment Terms",
    "Warranties",
    "Data Protection",
    "Force Majeure",
    "Dispute Resolution",
    "Service Level Agreement",
    "Change Management",
    "Acceptance Criteria",
    "Insurance",
    "Other"
]

RISK_LEVELS = ["low", "medium", "high"]

RELATIONSHIP_TYPES = [
    "amendment",
    "sow",
    "addendum",
    "work_order",
    "maintenance",
    "related"
]

CONTRACT_TYPES = [
    "Master Services Agreement",
    "Statement of Work",
    "Data Processing Agreement",
    "Service Level Agreement",
    "Non-Disclosure Agreement",
    "Amendment",
    "Addendum",
    "Work Order",
    "Consulting Agreement",
    "License Agreement",
    "Maintenance Agreement",
    "Purchase Order",
    "Other"
]

PARTY_ROLES = [
    "Client",
    "Vendor",
    "Licensor",
    "Licensee",
    "Consultant",
    "Partner",
    "Employer",
    "Employee",
    "Landlord",
    "Tenant"
]

CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"]


# Pydantic models for structured outputs
class Party(BaseModel):
    name: str
    role: Literal["Client", "Vendor", "Licensor", "Licensee", "Consultant", "Partner", "Employer", "Employee", "Landlord", "Tenant"]
    address: Optional[str] = None
    jurisdiction: Optional[str] = None


class TotalValue(BaseModel):
    amount: Optional[float] = None
    currency: Optional[Literal["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"]] = "USD"
    description: Optional[str] = None


class KeyDate(BaseModel):
    date: str
    description: str


class DefinedTerm(BaseModel):
    term: str
    definition: str


class ContractMetadata(BaseModel):
    title: str
    contract_type: Literal[
        "Master Services Agreement", "Statement of Work", "Data Processing Agreement",
        "Service Level Agreement", "Non-Disclosure Agreement", "Amendment", "Addendum",
        "Work Order", "Consulting Agreement", "License Agreement", "Maintenance Agreement",
        "Purchase Order", "Other"
    ]
    reference_number: Optional[str] = None  # E.g., MSA-ABC-202401-005
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    governing_law: Optional[str] = None
    parties: list[Party] = Field(default_factory=list)
    total_value: Optional[TotalValue] = None
    key_dates: list[KeyDate] = Field(default_factory=list)
    defined_terms: list[DefinedTerm] = Field(default_factory=list)
    # Relationship information
    parent_contract_reference: Optional[str] = None  # E.g., MSA-ABC-202401-005
    relationship_type: Optional[Literal["amendment", "sow", "addendum", "work_order", "maintenance", "related"]] = None
    relationship_description: Optional[str] = None


class ClauseSegment(BaseModel):
    section_label: str = Field(description="Section number/label like 'Article I' or '1.0' or 'Preamble'")
    title: str = Field(description="Section title/heading")
    text_content: str = Field(description="Full text of the clause")
    position: int = Field(description="Order in document (0-indexed)")


class ClauseSegmentation(BaseModel):
    clauses: list[ClauseSegment]


class Obligation(BaseModel):
    description: str
    responsible_party: str
    beneficiary_party: Optional[str] = None
    due_date_description: Optional[str] = None
    penalty_description: Optional[str] = None
    is_high_impact: bool = False


class Right(BaseModel):
    description: str
    holder_party: str
    condition_description: Optional[str] = None
    expiration_description: Optional[str] = None


class MonetaryValue(BaseModel):
    amount: Optional[float] = None
    currency: Literal["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"] = "USD"
    value_type: str
    context: str
    multiple_of_fees: Optional[float] = None


class Condition(BaseModel):
    description: str
    trigger_event: str


class ClauseAnalysis(BaseModel):
    clause_type: Literal[
        "Definitions", "Indemnification", "Limitation of Liability", "Confidentiality",
        "Intellectual Property", "Termination", "Payment Terms", "Warranties",
        "Data Protection", "Force Majeure", "Dispute Resolution", "Service Level Agreement",
        "Change Management", "Acceptance Criteria", "Insurance", "Other"
    ] = Field(description="Clause classification - must exactly match one of the predefined types")
    risk_level: Literal["low", "medium", "high"] = Field(description="Risk level classification")
    is_standard: bool
    risk_rationale: Optional[str] = None
    obligations: list[Obligation] = Field(default_factory=list)
    rights: list[Right] = Field(default_factory=list)
    monetary_values: list[MonetaryValue] = Field(default_factory=list)
    conditions: list[Condition] = Field(default_factory=list)


def get_embedding(text: str) -> list[float]:
    """Generate embedding vector for text using Azure OpenAI."""
    response = openai_client.embeddings.create(
        input=text[:8000],
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def extract_contract_metadata(markdown_content: str, filename: str) -> dict[str, Any]:
    """Extract comprehensive contract metadata using LLM with structured outputs."""
    
    system_prompt = f"""You are a legal contract analyzer specialized in extracting structured metadata.
Extract information accurately from the contract provided. Pay special attention to:
- Contract reference numbers (e.g., MSA-ABC-202401-005, SOW-XYZ-202403-012)
- References to parent/master agreements with their reference numbers
- Use ONLY these standardized contract types: {', '.join(CONTRACT_TYPES)}
- Use ONLY these relationship types: {', '.join(RELATIONSHIP_TYPES)}
- Use ONLY these party roles: {', '.join(PARTY_ROLES)}
- Use ISO currency codes: {', '.join(CURRENCIES)}
- Language like "executed pursuant to", "amends", "supplements", "issued under"

IMPORTANT FORMATTING RULES:
- Governing law: Use SHORT forms like "California", "New York", "Delaware", "England and Wales" (max 100 chars)
- Party jurisdictions: Use SHORT forms like "Delaware", "California", "UK" (max 100 chars)  
- Party names: Use official business names without excessive legal suffixes (max 200 chars)
- DO NOT include full legal descriptions like "State of California, United States of America"
- DO NOT include address information in jurisdiction fields
"""

    user_prompt = f"""Analyze this contract and extract all metadata including title, type, dates, parties, values, defined terms, and any relationships to parent contracts.

Look for:
- This contract's own reference number (usually at the top)
- References to parent contracts by reference number (e.g., "pursuant to MSA-ABC-202401-005")
- Relationship language indicating if this is an amendment, SOW, addendum, work order, or maintenance agreement

PARTY EXTRACTION REQUIREMENTS:
- Extract party names from the preamble (e.g., "Contoso Enterprises, Inc.", "Summit Tech, LLC")
- Extract jurisdiction from party descriptions like:
  * "a Delaware corporation" → jurisdiction: "Delaware"
  * "a Washington corporation" → jurisdiction: "Washington"  
  * "a Delaware limited liability company" → jurisdiction: "Delaware"
  * "a company incorporated in England and Wales" → jurisdiction: "England and Wales"
- Extract roles from context (Client, Vendor, Licensor, Licensee, etc.)
- Extract full addresses if provided

FORMATTING REQUIREMENTS:
- Governing law: Extract ONLY the jurisdiction name (e.g., "California", "New York", "Delaware", "England and Wales")
- Party jurisdictions: Use SHORT forms (e.g., "Delaware", "California", "Texas", "UK", "Singapore")
- DO NOT use verbose forms like "State of California, United States of America"
- Keep all text fields concise and focused

Contract (first 6000 characters):
{markdown_content[:6000]}

Extract all available information accurately, especially party jurisdictions and relationship references."""

    try:
        response = openai_client.chat.completions.parse(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=ContractMetadata
        )
        
        metadata = response.choices[0].message.parsed
        return metadata.model_dump()
    
    except Exception as e:
        print(f"  ⚠ Structured output error: {e}")
        
        # Fallback to basic extraction with simple regex patterns
        import re
        
        # Try to extract reference number (e.g., MSA-ABC-202401-005)
        ref_pattern = r'(?:Reference|Ref\.|Contract)\s*(?:Number|No\.?|#)?\s*:?\s*([A-Z]{2,4}-[A-Z]{3}-\d{6}-\d{3})'
        ref_match = re.search(ref_pattern, markdown_content[:2000], re.IGNORECASE)
        reference_number = ref_match.group(1) if ref_match else None
        
        # Try to extract parent reference
        parent_ref_pattern = r'pursuant to.*?(?:Reference|Ref\.|Contract)\s*(?:Number|No\.?)?\s*:?\s*([A-Z]{2,4}-[A-Z]{3}-\d{6}-\d{3})'
        parent_ref_match = re.search(parent_ref_pattern, markdown_content[:3000], re.IGNORECASE)
        parent_reference = parent_ref_match.group(1) if parent_ref_match else None
        
        parts = filename.replace(".md", "").split("_")
        return {
            "title": " ".join(parts[2:]) if len(parts) > 2 else filename,
            "contract_type": parts[2] if len(parts) > 2 else "Unknown",
            "reference_number": reference_number,
            "effective_date": None,
            "expiration_date": None,
            "governing_law": None,
            "parties": [],
            "total_value": None,
            "key_dates": [],
            "defined_terms": [],
            "parent_contract_reference": parent_reference,
            "relationship_type": None,
            "relationship_description": None
        }




def _segment_clauses_basic(markdown_content: str) -> list[dict[str, Any]]:
    """Fast path: Segment based on markdown headers."""
    import re
    
    clauses = []
    lines = markdown_content.split('\n')
    
    current_section = None
    current_title = None
    current_content = []
    position = 0
    
    for line in lines:
        # Match any level of markdown header
        if re.match(r'^#{1,6}\s+', line):
            # Save previous clause
            if current_content:
                text = '\n'.join(current_content).strip()
                if text and len(text) > 50:
                    clauses.append({
                        "section_label": current_section or f"Section {position+1}",
                        "title": current_title or "Untitled Section",
                        "text_content": text,
                        "position": position
                    })
                    position += 1
            
            # Start new clause
            header_text = re.sub(r'^#{1,6}\s+', '', line).strip()
            current_section = header_text
            current_title = header_text
            current_content = []
        else:
            current_content.append(line)
    
    # Save final clause
    if current_content:
        text = '\n'.join(current_content).strip()
        if text and len(text) > 50:
            clauses.append({
                "section_label": current_section or f"Section {position+1}",
                "title": current_title or "Untitled Section",
                "text_content": text,
                "position": position
            })
    
    return clauses


def segment_clauses(markdown_content: str) -> list[dict[str, Any]]:
    """Segment contract into logical clauses using intelligent two-tier approach."""
        
    system_prompt = """You are a legal document analyzer. Segment the contract into logical clauses/sections.
Identify major sections like Preamble, Definitions, Payment Terms, Termination, Liability, etc.
Each clause should be a meaningful, self-contained section."""

    # Truncate if too long
    content = markdown_content[:25000] if len(markdown_content) > 25000 else markdown_content
    
    user_prompt = f"""Segment this contract into logical clauses. Identify section labels (Article I, Section 1, etc.), titles, and full text content.

Contract:
{content}

Segment into major clauses/sections."""

    try:
        response = openai_client.chat.completions.parse(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=ClauseSegmentation
        )
        
        segmentation = response.choices[0].message.parsed
        return [clause.model_dump() for clause in segmentation.clauses]
    
    except Exception as e:
        print(f"  ⚠ LLM segmentation error: {e}")
        # Fallback to basic if LLM fails
        return _segment_clauses_basic(markdown_content)


def classify_and_analyze_clause(clause_text: str, clause_title: str) -> dict[str, Any]:
    """Comprehensive clause analysis using LLM with structured outputs."""
    
    system_prompt = f"""You are a legal contract analyzer. Classify clauses accurately and identify risks, obligations, rights, and monetary values.

IMPORTANT: Use ONLY these exact clause types: {', '.join(CLAUSE_TYPES)}
Use ONLY these risk levels: {', '.join(RISK_LEVELS)}
Use ONLY these currency codes: {', '.join(CURRENCIES)}
"""

    user_prompt = f"""Analyze this contract clause and extract all obligations, rights, monetary values, conditions, and assess risk level.

Title: {clause_title}
Text: {clause_text[:2000]}

Provide comprehensive analysis."""

    try:
        response = openai_client.chat.completions.parse(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=ClauseAnalysis,
        )
        
        analysis = response.choices[0].message.parsed
        return analysis.model_dump()
    
    except Exception as e:
        print(f"  ⚠ Structured clause analysis error: {e}")
        
        # Fallback to basic classification
        return {
            "clause_type": "Other",
            "risk_level": "low",
            "is_standard": True,
            "risk_rationale": None,
            "obligations": [],
            "rights": [],
            "monetary_values": [],
            "conditions": []
        }
