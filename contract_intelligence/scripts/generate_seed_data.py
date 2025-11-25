import os
import asyncio
import random
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OUTPUT_DIR = "data/input"
NUM_CONTRACTS = 45  # Generate 45 contracts
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
    "Data Processing Agreement"
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
    api_key=token_provider()  # Call the function to get the initial token
)

async def generate_contract(index):
    contract_type = random.choice(CONTRACT_TYPES)
    party_a = "Contoso Enterprises" # Our company
    party_b = random.choice(PARTIES)
    risk = random.choice(RISK_LEVELS)
    jurisdiction = random.choice(JURISDICTIONS)
    
    date_start = datetime.now() + timedelta(days=random.randint(-730, 0))  # Contracts from up to 2 years ago
    date_end = date_start + timedelta(days=random.randint(365, 1825))  # 1-5 year terms
    
    contract_value = random.randint(50000, 5000000)
    liability_cap_multiplier = random.choice([1, 2, 3, 5]) if risk != "High" else None
    payment_terms = random.choice(["Net 30", "Net 45", "Net 60"])
    
    print(f"[{index+1}/{NUM_CONTRACTS}] Generating {contract_type} with {party_b} (Risk: {risk})...")
    
    prompt = f"""
    Generate a highly realistic, detailed, and professional {contract_type} between {party_a} (the "Client" or "Company") and {party_b} (the "Vendor" or "Service Provider").
    
    **CRITICAL REQUIREMENTS:**
    - This must be a LONG, COMPREHENSIVE legal document of at least 6-7 PAGES (approximately 3500-5000 words).
    - Use proper legal language, structure, and formatting.
    - Write in Markdown format with proper headings (##, ###).
    
    **CONTRACT PARAMETERS:**
    - Effective Date: {date_start.strftime('%B %d, %Y')}
    - Expiration Date: {date_end.strftime('%B %d, %Y')}
    - Contract Value: ${contract_value:,}
    - Payment Terms: {payment_terms}
    - Governing Law: {jurisdiction}
    - Risk Level: {risk}
    
    **REQUIRED SECTIONS (Be Comprehensive):**
    
    1. **Preamble & Recitals:** Include the full legal names, addresses, and background context ("WHEREAS" clauses).
    
    2. **Definitions (Article I):** Define at least 15-20 key terms used in the agreement (e.g., "Services", "Deliverables", "Confidential Information", "Force Majeure", "Business Day").
    
    3. **Scope of Services/Work (Article II):** Detailed description of what is being provided. Include specific deliverables, timelines, and performance standards. Make this section at least 500 words.
    
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
        - Entire agreement
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
                    "content": "You are an expert corporate attorney with 20 years of experience drafting commercial contracts. You write comprehensive, detailed, and legally sound agreements."
                },
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=16000  # Allow for long responses
        )
        
        content = response.choices[0].message.content
        
        # Create safe filename
        safe_party_name = party_b.replace(' ', '').replace(',', '')[:20]
        safe_contract_type = contract_type.replace(' ', '')[:30]
        filename = f"{OUTPUT_DIR}/contract_{index:03d}_{safe_party_name}_{safe_contract_type}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        word_count = len(content.split())
        print(f"✓ Saved: {filename} ({word_count} words)")
        
    except Exception as e:
        print(f"✗ Error generating contract {index}: {str(e)}")
        raise

async def main():
    print("=" * 70)
    print("CONTRACT INTELLIGENCE PLATFORM - SEED DATA GENERATOR")
    print("=" * 70)
    print(f"Target: {NUM_CONTRACTS} contracts")
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
        print(f"\n--- Batch {i//batch_size + 1}: Generating contracts {i+1} to {batch_end} ---")
        
        tasks = [generate_contract(j) for j in range(i, batch_end)]
        await asyncio.gather(*tasks)
        
        # Small delay between batches to avoid rate limiting
        if batch_end < NUM_CONTRACTS:
            print("Waiting 5 seconds before next batch...")
            await asyncio.sleep(5)
    
    print("\n" + "=" * 70)
    print("✓ SEED DATA GENERATION COMPLETE")
    print(f"✓ Generated {NUM_CONTRACTS} contracts in {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
