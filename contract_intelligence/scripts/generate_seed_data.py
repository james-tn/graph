import os
import asyncio
import random
from datetime import datetime, timedelta
from pathlib import Path
from openai import AsyncOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OUTPUT_DIR = "data/input"
NUM_CONTRACTS = 545  # Generate contracts
CONTRACT_TYPES = [
    "Master Services Agreement", 
    "Statement of Work", 
    "Non-Disclosure Agreement",
    "Software License Agreement",
    "Consulting Agreement",
    "Employment Agreement",
    "Lease Agreement",
    "Purchase Agreement",
    "Partnership Agreement",
    "Data Processing Agreement",
    "Amendment",
    "Addendum",
    "Work Order",
    "Service Level Agreement",
    "Maintenance Agreement"
]
PARTIES = [
    "Acme Corp", "Beta Ltd", "Gamma Inc", "Delta LLC", "Epsilon Group",
    "Zenith Technologies", "Meridian Solutions", "Atlas Ventures", "Nova Systems",
    "Cascade Enterprises", "Phoenix Industries", "Quantum Labs", "Vertex Group",
    "Stellar Dynamics", "Horizon Partners", "Nexus Corporation", "Pinnacle Services",
    "Summit Tech", "Vanguard Solutions", "Titan Industries"
]
RISK_LEVELS = ["Low", "Medium", "High"]
JURISDICTIONS = ["California", "New York", "Delaware", "Texas", "Washington", "United Kingdom", "Singapore"]

# Track generated contracts for creating relationships
CONTRACT_REGISTRY = []  # List of {index, identifier, reference_number, type, party, date, jurisdiction, can_have_children, child_count}

# Azure OpenAI Configuration using DefaultAzureCredential
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://eastus2oai.openai.azure.com/openai/v1/")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5.1")

credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(
    credential, 
    "https://cognitiveservices.azure.com/.default"
)

client = AsyncOpenAI(
    base_url=endpoint,
    # api_key=token_provider()  # Call the function to get the initial token
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)


def get_last_contract_number():
    """Find the highest contract number in existing files."""
    input_dir = Path(OUTPUT_DIR)
    if not input_dir.exists():
        return 0
    
    existing_files = list(input_dir.glob("contract_*.md"))
    if not existing_files:
        return 0
    
    max_num = 0
    for file in existing_files:
        # Extract number from filename like "contract_042_..."
        parts = file.stem.split('_')
        if len(parts) >= 2 and parts[1].isdigit():
            num = int(parts[1])
            max_num = max(max_num, num)
    
    return max_num


def generate_reference_number(contract_type, party_name, date, index):
    """Generate a realistic contract reference number."""
    # Common formats: MSA-PARTY-YYYY-NNN, SOW-PARENT-NNN, AGR-YYYYMM-NNN
    year = date.year
    month = date.month
    
    # Type prefix mapping
    type_prefixes = {
        "Master Services Agreement": "MSA",
        "Statement of Work": "SOW",
        "Non-Disclosure Agreement": "NDA",
        "Software License Agreement": "SLA",
        "Consulting Agreement": "CSA",
        "Amendment": "AMD",
        "Addendum": "ADD",
        "Work Order": "WO",
        "Service Level Agreement": "SLA",
        "Maintenance Agreement": "MNT",
        "Purchase Agreement": "PUR",
        "Lease Agreement": "LSE",
        "Data Processing Agreement": "DPA"
    }
    
    prefix = type_prefixes.get(contract_type, "AGR")
    party_code = party_name[:3].upper().replace(' ', '').replace(',', '')
    
    return f"{prefix}-{party_code}-{year}{month:02d}-{index:03d}"


def generate_child_reference_number(parent_ref, child_type, index):
    """Generate a child contract reference that clearly links to parent."""
    # Examples: 
    # MSA-ABC-202401-005 -> SOW-ABC-202403-012 (references parent)
    # MSA-ABC-202401-005 -> AMD-ABC-202405-020 (amendment to parent)
    
    type_prefixes = {
        "Statement of Work": "SOW",
        "Amendment": "AMD",
        "Addendum": "ADD",
        "Work Order": "WO",
        "Service Level Agreement": "SLA",
        "Maintenance Agreement": "MNT"
    }
    
    prefix = type_prefixes.get(child_type, "REL")
    
    # Extract party code from parent (e.g., ABC from MSA-ABC-202401-005)
    parts = parent_ref.split('-')
    if len(parts) >= 2:
        party_code = parts[1]
        return f"{prefix}-{party_code}-{parts[2] if len(parts) >= 3 else datetime.now().strftime('%Y%m')}-{index:03d}"
    
    return f"{prefix}-{index:03d}"


def load_parent_contract(parent_identifier):
    """Load the content of a parent contract from disk."""
    input_dir = Path(OUTPUT_DIR)
    
    # Find the parent contract file
    pattern = f"{parent_identifier}_*.md"
    matching_files = list(input_dir.glob(pattern))
    
    if not matching_files:
        print(f"⚠️ Warning: Could not find parent contract file matching {pattern}")
        return None
    
    parent_file = matching_files[0]
    try:
        with open(parent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Truncate if too long (keep first 8000 words to fit in context)
        words = content.split()
        if len(words) > 8000:
            content = ' '.join(words[:8000]) + "\n\n[... remainder of document truncated for brevity ...]"
        
        return content
    except Exception as e:
        print(f"⚠️ Warning: Error reading parent contract {parent_file}: {e}")
        return None


def should_create_related_contract(index, total):
    """Determine if this contract should be related to an existing one."""
    # Don't create relationships for first 10 contracts (need a base)
    if index < 10 or not CONTRACT_REGISTRY:
        return False
    
    # Higher probability (40%) to ensure multiple children per parent
    return random.random() < 0.40


def select_parent_contract():
    """Select a parent contract for relationship, preferring those with fewer children."""
    # Filter contracts that can have children
    eligible = [c for c in CONTRACT_REGISTRY if c.get("can_have_children", True)]
    
    if not eligible:
        return None
    
    # Prefer more recent contracts (last 50)
    recent = eligible[-50:] if len(eligible) > 50 else eligible
    
    # Weight selection by inverse of child count (prefer parents with fewer children)
    # but still allow randomness so popular parents can have multiple children
    weights = []
    for contract in recent:
        child_count = contract.get('child_count', 0)
        # Give higher weight to contracts with 0-2 children, lower but non-zero for 3+
        if child_count == 0:
            weight = 10  # Highest priority: no children yet
        elif child_count == 1:
            weight = 8   # Still high: first child created
        elif child_count == 2:
            weight = 5   # Medium: second child created
        elif child_count == 3:
            weight = 3   # Lower: third child
        else:
            weight = 1   # Lowest but possible: 4+ children
        weights.append(weight)
    
    # Use weighted random selection
    return random.choices(recent, weights=weights, k=1)[0]


def determine_relationship_type(parent_type):
    """Determine what type of related contract to create."""
    relationships = {
        "Master Services Agreement": [
            ("Statement of Work", "This SOW is executed pursuant to the Master Services Agreement"),
            ("Work Order", "This Work Order is issued under the Master Services Agreement"),
            ("Amendment", "This Amendment modifies the Master Services Agreement"),
            ("Service Level Agreement", "This SLA supplements the Master Services Agreement")
        ],
        "Statement of Work": [
            ("Amendment", "This Amendment modifies the Statement of Work"),
            ("Addendum", "This Addendum supplements the Statement of Work"),
            ("Work Order", "This Work Order adds scope to the Statement of Work")
        ],
        "Software License Agreement": [
            ("Maintenance Agreement", "This Maintenance Agreement supports the Software License"),
            ("Amendment", "This Amendment modifies the Software License Agreement"),
            ("Addendum", "This Addendum adds licensed users/modules")
        ],
        "Non-Disclosure Agreement": [
            ("Amendment", "This Amendment extends or modifies the NDA"),
            ("Addendum", "This Addendum adds covered information to the NDA")
        ],
        "Consulting Agreement": [
            ("Statement of Work", "This SOW defines specific consulting deliverables"),
            ("Amendment", "This Amendment changes terms of the Consulting Agreement"),
            ("Work Order", "This Work Order authorizes additional consulting work")
        ],
        "Purchase Agreement": [
            ("Amendment", "This Amendment modifies quantities or pricing"),
            ("Addendum", "This Addendum adds products or services")
        ],
        "Lease Agreement": [
            ("Amendment", "This Amendment modifies lease terms"),
            ("Addendum", "This Addendum adds or modifies leased space")
        ],
        "Data Processing Agreement": [
            ("Amendment", "This Amendment updates data processing terms"),
            ("Addendum", "This Addendum adds processing activities")
        ]
    }
    
    options = relationships.get(parent_type, [("Amendment", "This Amendment modifies the original agreement")])
    return random.choice(options)

async def generate_contract(index, starting_index):
    """Generate a standalone or related contract."""
    
    # Determine if this should be a related contract
    parent_contract = None
    relationship_type = None
    relationship_description = None
    contract_reference = None
    
    if should_create_related_contract(index, NUM_CONTRACTS):
        parent_contract = select_parent_contract()
        if parent_contract:
            # Increment the parent's child count
            parent_contract['child_count'] = parent_contract.get('child_count', 0) + 1
            
            relationship_type, relationship_description = determine_relationship_type(parent_contract["type"])
            contract_type = relationship_type
            party_b = parent_contract["party"]
            # Generate child reference number linked to parent
            contract_reference = generate_child_reference_number(parent_contract["reference_number"], contract_type, index)
            print(f"[{index+1}/{starting_index + NUM_CONTRACTS}] Generating {contract_type} ({contract_reference}) related to {parent_contract['reference_number']} (child #{parent_contract['child_count']}) with {party_b}...")
        else:
            # Fallback to standalone
            contract_type = random.choice(CONTRACT_TYPES)
            party_b = random.choice(PARTIES)
            print(f"[{index+1}/{starting_index + NUM_CONTRACTS}] Generating standalone {contract_type} with {party_b}...")
    else:
        # Standalone contract
        contract_type = random.choice(CONTRACT_TYPES)
        party_b = random.choice(PARTIES)
        print(f"[{index+1}/{starting_index + NUM_CONTRACTS}] Generating standalone {contract_type} with {party_b}...")
    
    party_a = "Contoso Enterprises"  # Our company
    risk = random.choice(RISK_LEVELS)
    jurisdiction = random.choice(JURISDICTIONS)
    
    # Date logic - if related, date should be after parent
    if parent_contract:
        parent_date = parent_contract.get("date", datetime.now())
        date_start = parent_date + timedelta(days=random.randint(30, 365))
    else:
        date_start = datetime.now() + timedelta(days=random.randint(-730, 0))
    
    # Generate reference number if not already set (for standalone contracts)
    if not contract_reference:
        contract_reference = generate_reference_number(contract_type, party_b, date_start, index)
    
    date_end = date_start + timedelta(days=random.randint(365, 1825))
    
    contract_value = random.randint(50000, 5000000)
    liability_cap_multiplier = random.choice([1, 2, 3, 5]) if risk != "High" else None
    payment_terms = random.choice(["Net 30", "Net 45", "Net 60"])
    
    # Build relationship context for prompt
    relationship_context = ""
    parent_contract_content = None
    
    if parent_contract:
        # Load the actual parent contract content
        parent_contract_content = load_parent_contract(parent_contract['identifier'])
        
        if parent_contract_content:
            parent_content_section = f"""
    
    **PARENT CONTRACT CONTENT FOR REFERENCE:**
    Below is the content of the parent contract that this document relates to. You MUST read and reference specific details from it.
    
    ```
    {parent_contract_content}
    ```
    
    END OF PARENT CONTRACT
    """
        else:
            parent_content_section = ""
        
        relationship_context = f"""
    
    **CRITICAL RELATIONSHIP REQUIREMENT:**
    This {contract_type} is related to an existing contract:
    - Parent Contract Reference: {parent_contract['reference_number']}
    - Parent Contract Identifier: {parent_contract['identifier']}
    - Parent Contract Type: {parent_contract['type']}
    - This Contract Reference: {contract_reference}
    - Relationship: {relationship_description}
    {parent_content_section}
    
    YOU MUST:
    1. Include this contract's reference number "{contract_reference}" prominently in the title/header
    2. Reference the parent contract by BOTH its reference number "{parent_contract['reference_number']}" AND identifier "{parent_contract['identifier']}" in the preamble
    3. Include language like "{relationship_description} dated {parent_contract.get('date', datetime.now()).strftime('%B %d, %Y')} (Ref: {parent_contract['reference_number']})"
    4. State that this document "is entered into pursuant to" or "amends" or "supplements" the parent contract
    5. Include a dedicated section titled "Reference to Master/Parent Agreement" that explicitly states: "This {contract_type} is executed under and subject to the terms of {parent_contract['type']} reference number {parent_contract['reference_number']}"
    6. **CRITICALLY IMPORTANT**: Reference SPECIFIC sections, terms, parties, values, and clauses from the parent contract above. Make the relationship concrete and detailed.
    7. Use consistent party names, addresses, and terms from the parent contract
    8. If Amendment/Addendum: Cite specific article numbers, section titles, and clause text from the parent that are being modified/added
    9. If SOW/Work Order: Reference the scope, payment terms, and deliverable framework established in the parent MSA
    10. If Maintenance Agreement: Reference the specific software/services covered in the parent license agreement
    11. Maintain the same governing law and jurisdiction as parent: {parent_contract.get('jurisdiction', jurisdiction)}
    12. In the signature block, include a line referencing the parent: "Executed pursuant to {parent_contract['reference_number']}"
    """
        jurisdiction = parent_contract.get('jurisdiction', jurisdiction)
    
    prompt = f"""
    Generate a highly realistic, detailed, and professional {contract_type} between {party_a} (the "Client" or "Company") and {party_b} (the "Vendor" or "Service Provider").
    {relationship_context}
    
    **CRITICAL REQUIREMENTS:**
    - This must be a LONG, COMPREHENSIVE legal document of at least 6-7 PAGES (approximately 3500-5000 words).
    - Use proper legal language, structure, and formatting.
    - Write in Markdown format with proper headings (##, ###).
    - INCLUDE the contract reference number "{contract_reference}" prominently at the top of the document.
    
    **CONTRACT PARAMETERS:**
    - Contract Reference Number: {contract_reference}
    - Effective Date: {date_start.strftime('%B %d, %Y')}
    - Expiration Date: {date_end.strftime('%B %d, %Y')}
    - Contract Value: ${contract_value:,}
    - Payment Terms: {payment_terms}
    - Governing Law: {jurisdiction}
    - Risk Level: {risk}
    
    **REQUIRED SECTIONS (Be Comprehensive):**
    
    1. **Preamble & Recitals:** Include the contract reference number "{contract_reference}" at the very top. Include the full legal names, addresses, and background context ("WHEREAS" clauses).
       {f"MUST reference parent contract {parent_contract['reference_number']} (File: {parent_contract['identifier']})" if parent_contract else ""}
    
    2. **Definitions (Article I):** Define at least 15-20 key terms used in the agreement (e.g., "Services", "Deliverables", "Confidential Information", "Force Majeure", "Business Day").
       {f"Include 'Parent Agreement' or 'Master Agreement' definition referencing {parent_contract['identifier']}" if parent_contract else ""}
    
    3. **Scope of Services/Work (Article II):** Detailed description of what is being provided. Include specific deliverables, timelines, and performance standards. Make this section at least 500 words.
       {f"Clearly describe how this work relates to or extends the parent agreement" if parent_contract else ""}
    
    4. **Fees and Payment Terms (Article III):**
       - Detailed fee schedule
       - Payment milestones
       - Late payment penalties
       - Expenses and reimbursement policies
    
    5. **Term and Termination (Article IV):**
       - Initial term and renewal provisions
       - Termination for convenience (notice period: {"180 days" if risk == "High" else "30-60 days"})
       - Termination for cause
       - Effects of termination
       {f"- Address what happens to this agreement if parent agreement terminates" if parent_contract else ""}
    
    6. **Confidentiality (Article V):**
       - Define confidential information
       - Obligations of both parties
       - Exceptions to confidentiality
       - Survival period (typically 3-5 years)
    
    7. **Intellectual Property Rights (Article VI):**
       - Ownership of work product
       - License grants
       - Pre-existing IP
       - Use restrictions
    
    8. **Representations and Warranties (Article VII):**
       - Authority to enter into agreement
       - Compliance with laws
       - Quality of services/products
       - No conflicts
    
    9. **Indemnification (Article VIII):**
       - Each party's indemnification obligations
       - Procedures for indemnification claims
       - Defense obligations
    
    10. **Limitation of Liability (Article IX):**
        {"- NO CAP on liability (High Risk)" if risk == "High" else f"- Liability capped at {liability_cap_multiplier}x the fees paid in the 12 months preceding the claim"}
        - Exclusion of consequential damages {"(INCLUDE consequential damages if High Risk)" if risk == "High" else ""}
        - Exceptions to limitations
    
    11. **Insurance (Article X):**
        - Required insurance types and coverage amounts
        - Certificate of insurance requirements
    
    12. **Data Protection and Privacy (Article XI):**
        - GDPR/CCPA compliance requirements
        - Data breach notification obligations
        - Data retention and deletion policies
    
    13. **Service Level Agreements (Article XII):** (If applicable to this contract type)
        - Uptime guarantees (e.g., 99.9%)
        - Response times
        - Remedies for SLA breaches
    
    14. **Change Management (Article XIII):**
        - Process for requesting changes
        - Approval procedures
        - Impact on fees and timeline
    
    15. **Dispute Resolution (Article XIV):**
        - Negotiation and escalation procedures
        - Mediation requirements
        - Arbitration or litigation venue
    
    16. **Force Majeure (Article XV):**
        - Definition of force majeure events
        - Notice requirements
        - Rights and obligations during force majeure
    
    17. **General Provisions (Article XVI):**
        - Entire agreement {f"(or how this relates to parent agreement)" if parent_contract else ""}
        - Amendments (must be in writing)
        - Severability
        - Waiver
        - Notices (include specific addresses)
        - Assignment restrictions
        - Independent contractor relationship
        - Survival of terms
        - Counterparts
    
    18. **Signature Block:**
        Include proper signature blocks for both parties with:
        - Company name
        - Signatory name and title
        - Date line
        - Witness line (if applicable)
    
    **STYLE GUIDELINES:**
    - Use formal legal language ("hereinafter", "whereas", "hereby").
    - Number all sections and subsections clearly (e.g., 1.1, 1.2).
    - Include cross-references between sections where appropriate.
    - Make the document realistic enough that it could be used as a template.
    - Vary the specific terms and conditions to make each contract unique.
    
    **RISK-SPECIFIC INSTRUCTIONS:**
    - If Risk = "High": Include aggressive terms favoring the Vendor (long termination notice, uncapped liability, broad indemnification by Client, restrictive IP terms).
    - If Risk = "Medium": Include balanced terms with some areas of negotiation.
    - If Risk = "Low": Include client-friendly terms (short termination notice, reasonable caps, mutual obligations).
    
    Generate the complete contract now. Make it comprehensive and professional.
    """
    
    try:
        response = await client.chat.completions.create(
            model=deployment_name,
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert corporate attorney with 20 years of experience drafting commercial contracts. You write comprehensive, detailed, and legally sound agreements. You are meticulous about contract relationships and references. When provided with a parent contract, you carefully read it and reference specific sections, terms, parties, values, and provisions to create a coherent relationship between documents. You cite article numbers, section titles, and specific language from related contracts."
                },
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=16000  # Allow for long responses
        )
        
        content = response.choices[0].message.content
        
        # Create safe filename
        safe_party_name = party_b.replace(' ', '').replace(',', '')[:20]
        safe_contract_type = contract_type.replace(' ', '')[:30]
        contract_identifier = f"contract_{index:03d}"
        filename = f"{OUTPUT_DIR}/{contract_identifier}_{safe_party_name}_{safe_contract_type}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        word_count = len(content.split())
        print(f"✓ Saved: {filename} ({word_count} words)")
        
        # Register this contract for potential relationships
        can_have_children = contract_type in ["Master Services Agreement", "Software License Agreement", 
                                               "Consulting Agreement", "Statement of Work", "Purchase Agreement",
                                               "Lease Agreement", "Data Processing Agreement"]
        
        CONTRACT_REGISTRY.append({
            "index": index,
            "identifier": contract_identifier,
            "reference_number": contract_reference,
            "type": contract_type,
            "party": party_b,
            "date": date_start,
            "jurisdiction": jurisdiction,
            "can_have_children": can_have_children,
            "child_count": 0  # Track how many children this contract has
        })
        
    except Exception as e:
        print(f"✗ Error generating contract {index}: {str(e)}")
        raise

async def main():
    # Find the last contract number to resume from
    starting_index = get_last_contract_number() + 1
    
    print("=" * 70)
    print("CONTRACT INTELLIGENCE PLATFORM - SEED DATA GENERATOR")
    print("=" * 70)
    print(f"Target: {NUM_CONTRACTS} new contracts")
    if starting_index > 0:
        print(f"Resuming from: contract_{starting_index:03d}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Model: {deployment_name}")
    print("=" * 70)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}\n")
    
    # Generate contracts in batches to avoid rate limits
    batch_size = 5
    for i in range(0, NUM_CONTRACTS, batch_size):
        batch_end = min(i + batch_size, NUM_CONTRACTS)
        actual_start = starting_index + i
        actual_end = starting_index + batch_end - 1
        print(f"\n--- Batch {i//batch_size + 1}: Generating contracts {actual_start:03d} to {actual_end:03d} ---")
        
        tasks = [generate_contract(starting_index + j, starting_index) for j in range(i, batch_end)]
        await asyncio.gather(*tasks)
        
        # Small delay between batches to avoid rate limiting
        if batch_end < NUM_CONTRACTS:
            print("Waiting 5 seconds before next batch...")
            await asyncio.sleep(5)
    
    print("\n" + "=" * 70)
    print("✓ SEED DATA GENERATION COMPLETE")
    print(f"✓ Generated {NUM_CONTRACTS} new contracts in {OUTPUT_DIR}")
    print(f"✓ Total contracts now: {starting_index + NUM_CONTRACTS}")
    print(f"✓ Contracts with relationships: {len([c for c in CONTRACT_REGISTRY if 'parent' in str(c)])} (approximately)")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
