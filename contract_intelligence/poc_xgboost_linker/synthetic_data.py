"""
Synthetic Contract Corpus Generator

Generates a realistic synthetic dataset of contracts with hierarchical relationships
(MSAs -> SOWs, Amendments, Addendums) for the XGBoost POC.

The synthetic data deliberately includes the kind of noise that breaks rule-based
hierarchy detection:
- Missing parent references in some children
- Inconsistent reference formats
- Reference number variations (typos, format drift)
- Multiple plausible parents (same client, different MSAs)
- Implicit relationships (no explicit reference, but clear from context)
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# Pools used to build realistic-looking contracts
CLIENTS = [
    "Contoso Enterprises", "Acme Corporation", "Globex Inc",
    "Initech LLC", "Umbrella Technologies", "Stark Industries",
    "Wayne Enterprises", "Hooli", "Pied Piper", "Massive Dynamic",
    "Cyberdyne Systems", "Tyrell Corporation", "Wonka Industries",
    "Soylent Corp", "Oscorp",
]

VENDORS = [
    "Zenith Solutions", "Quantum Labs", "Apex Consulting", "Nimbus Systems",
    "Vertex Partners", "Catalyst Group", "Helix Technologies", "Beacon Advisors",
    "Pinnacle Services", "Summit Software", "Horizon Networks", "Atlas Ventures",
]

CONTRACT_TYPES = ["MSA", "SOW", "Amendment", "Addendum", "WorkOrder"]

GOVERNING_LAWS = ["Delaware", "California", "New York", "Texas", "Massachusetts"]

CURRENCIES = ["USD", "EUR", "GBP"]

CLAUSE_KEYWORDS = {
    "MSA": [
        "this Master Services Agreement governs all subsequent statements of work",
        "the parties hereby establish a framework",
        "general terms and conditions applicable to all engagements",
    ],
    "SOW": [
        "this Statement of Work is executed pursuant to the Master Services Agreement",
        "the deliverables described in this SOW",
        "scope of services for this engagement",
    ],
    "Amendment": [
        "this Amendment modifies the terms of the original agreement",
        "the parties hereby amend the prior agreement",
        "supersedes the previous provisions of section",
    ],
    "Addendum": [
        "this Addendum is appended to and becomes part of the agreement",
        "additional terms supplementing the base contract",
    ],
    "WorkOrder": [
        "this Work Order is issued under the terms of the master agreement",
        "specific tasks and deliverables for this assignment",
    ],
}


@dataclass
class SyntheticContract:
    """A synthetic contract with all fields needed for feature extraction."""

    id: int
    contract_identifier: str
    reference_number: str
    title: str
    contract_type: str
    effective_date: date
    expiration_date: Optional[date]
    governing_law: str
    currency: str
    total_value: Optional[float]
    parties: list[dict]  # [{"canonical_name": str, "role": str}, ...]
    full_text: str
    status: str = "active"

    # Ground truth for evaluation - NOT used by the linker
    true_parent_id: Optional[int] = None

    # What an LLM extractor would surface (may be wrong/missing)
    extracted_parent_reference: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "contract_identifier": self.contract_identifier,
            "reference_number": self.reference_number,
            "title": self.title,
            "contract_type": self.contract_type,
            "effective_date": self.effective_date,
            "expiration_date": self.expiration_date,
            "governing_law": self.governing_law,
            "currency": self.currency,
            "total_value": self.total_value,
            "parties": self.parties,
            "full_text": self.full_text,
            "status": self.status,
            "true_parent_id": self.true_parent_id,
            "extracted_parent_reference": self.extracted_parent_reference,
        }


def _make_reference_number(contract_type: str, client: str, year: int, seq: int) -> str:
    """Build a realistic reference number like 'MSA-CON-202403-001'."""
    client_abbrev = "".join(w[0] for w in client.split()[:3]).upper()[:3].ljust(3, "X")
    return f"{contract_type.upper()}-{client_abbrev}-{year}{random.randint(1, 12):02d}-{seq:03d}"


def _maybe_corrupt_reference(ref: str, corrupt_prob: float = 0.3) -> Optional[str]:
    """
    Simulate the messy reality of LLM-extracted parent references.
    Returns:
      - None (missing reference) ~15% of the time
      - Slightly mangled reference ~15% of the time
      - Exact reference otherwise
    """
    if random.random() < corrupt_prob * 0.5:
        # Reference completely missing - the killer case for rule-based linkers
        return None

    if random.random() < corrupt_prob:
        # Mangle the reference: typos, format drift
        mutations = [
            lambda r: r.replace("-", " "),                           # spaces instead of dashes
            lambda r: r.lower(),                                     # case drift
            lambda r: r.replace("MSA", "Master Service Agreement"),  # spelled out
            lambda r: r[:-1] + str(random.randint(0, 9)),            # OCR-style digit error
            lambda r: r.replace("-", "/"),                           # different separator
        ]
        mutator = random.choice(mutations)
        return mutator(ref)

    return ref


def _build_contract_text(
    contract_type: str,
    parties: list[dict],
    parent: Optional["SyntheticContract"] = None,
    parent_ref_in_text: bool = True,
) -> str:
    """Build a plausible contract body text."""
    party_names = ", ".join(p["canonical_name"] for p in parties)
    keywords = random.choice(CLAUSE_KEYWORDS.get(contract_type, ["this agreement is entered into"]))

    parent_clause = ""
    if parent and parent_ref_in_text:
        # Parent reference appears in text most of the time when it should
        if random.random() < 0.7:
            parent_clause = f" This agreement is executed under {parent.reference_number} dated {parent.effective_date.strftime('%B %d, %Y')}."
        else:
            # Sometimes parent is referenced more loosely
            parent_clause = f" Pursuant to the {parent.contract_type} between the parties dated {parent.effective_date.strftime('%B %d, %Y')}."

    body = (
        f"AGREEMENT between {party_names}. "
        f"This {contract_type} is effective as of the date set forth herein. "
        f"{keywords}.{parent_clause} "
        f"The parties agree to the terms set forth in the schedules and exhibits attached hereto. "
        f"This agreement contains standard provisions relating to confidentiality, "
        f"intellectual property, indemnification, and termination."
    )
    return body


def generate_corpus(
    num_msas: int = 60,
    children_per_msa_range: tuple[int, int] = (2, 8),
    seed: int = 42,
) -> list[SyntheticContract]:
    """
    Generate a synthetic contract corpus with realistic hierarchical structure.

    Each MSA spawns 2-8 child contracts (SOWs, Amendments, Addendums, WorkOrders).
    About 30% of children have noisy/missing parent references in their extracted
    metadata - this is the case the XGBoost model needs to handle.
    """
    random.seed(seed)
    corpus: list[SyntheticContract] = []
    next_id = 1

    for _ in range(num_msas):
        # Pick a client/vendor pair for this contract family
        client = random.choice(CLIENTS)
        vendor = random.choice(VENDORS)
        gov_law = random.choice(GOVERNING_LAWS)
        currency = random.choice(CURRENCIES)

        msa_year = random.randint(2018, 2024)
        msa_eff = date(msa_year, random.randint(1, 12), random.randint(1, 28))
        msa_exp = msa_eff + timedelta(days=random.choice([365, 730, 1095]))  # 1-3 yr term
        seq = random.randint(1, 999)

        msa_parties = [
            {"canonical_name": client, "role": "Client"},
            {"canonical_name": vendor, "role": "Vendor"},
        ]

        msa = SyntheticContract(
            id=next_id,
            contract_identifier=f"contract_{next_id:04d}",
            reference_number=_make_reference_number("MSA", client, msa_year, seq),
            title=f"Master Services Agreement between {client} and {vendor}",
            contract_type="MSA",
            effective_date=msa_eff,
            expiration_date=msa_exp,
            governing_law=gov_law,
            currency=currency,
            total_value=round(random.uniform(500_000, 5_000_000), 2),
            parties=msa_parties,
            full_text=_build_contract_text("MSA", msa_parties),
            true_parent_id=None,
            extracted_parent_reference=None,
        )
        corpus.append(msa)
        next_id += 1

        # Generate child contracts under this MSA
        num_children = random.randint(*children_per_msa_range)
        for _ in range(num_children):
            child_type = random.choices(
                ["SOW", "Amendment", "Addendum", "WorkOrder"],
                weights=[0.55, 0.15, 0.10, 0.20],
            )[0]

            # Children come AFTER the parent
            child_eff = msa_eff + timedelta(days=random.randint(15, 600))
            if child_eff >= (msa_exp or msa_eff + timedelta(days=730)):
                child_eff = msa_eff + timedelta(days=random.randint(30, 365))

            child_exp = child_eff + timedelta(days=random.choice([90, 180, 365]))

            # Child usually shares parties with parent, occasionally adds a subcontractor
            child_parties = list(msa_parties)
            if random.random() < 0.15:
                child_parties.append(
                    {"canonical_name": random.choice(VENDORS), "role": "Subcontractor"}
                )

            # Build extracted reference - often noisy or missing
            extracted_ref = _maybe_corrupt_reference(msa.reference_number, corrupt_prob=0.3)
            # If reference is missing in extraction, sometimes also drop it from text
            text_has_ref = extracted_ref is not None or random.random() < 0.5

            child = SyntheticContract(
                id=next_id,
                contract_identifier=f"contract_{next_id:04d}",
                reference_number=_make_reference_number(child_type, client, child_eff.year, random.randint(1, 999)),
                title=f"{child_type} - {client}/{vendor}",
                contract_type=child_type,
                effective_date=child_eff,
                expiration_date=child_exp,
                governing_law=gov_law,                                    # usually inherits
                currency=currency,                                        # usually inherits
                total_value=round(random.uniform(10_000, 200_000), 2),    # SOWs much smaller
                parties=child_parties,
                full_text=_build_contract_text(child_type, child_parties, parent=msa, parent_ref_in_text=text_has_ref),
                true_parent_id=msa.id,
                extracted_parent_reference=extracted_ref,
            )
            corpus.append(child)
            next_id += 1

    # Add a few decoy MSAs for the same clients (to create ambiguous candidate sets)
    for _ in range(num_msas // 5):
        client = random.choice(CLIENTS)
        vendor = random.choice(VENDORS)
        msa_year = random.randint(2018, 2024)
        msa_eff = date(msa_year, random.randint(1, 12), random.randint(1, 28))
        msa_parties = [
            {"canonical_name": client, "role": "Client"},
            {"canonical_name": vendor, "role": "Vendor"},
        ]
        msa = SyntheticContract(
            id=next_id,
            contract_identifier=f"contract_{next_id:04d}",
            reference_number=_make_reference_number("MSA", client, msa_year, random.randint(1, 999)),
            title=f"Master Services Agreement between {client} and {vendor}",
            contract_type="MSA",
            effective_date=msa_eff,
            expiration_date=msa_eff + timedelta(days=730),
            governing_law=random.choice(GOVERNING_LAWS),
            currency=random.choice(CURRENCIES),
            total_value=round(random.uniform(500_000, 5_000_000), 2),
            parties=msa_parties,
            full_text=_build_contract_text("MSA", msa_parties),
        )
        corpus.append(msa)
        next_id += 1

    return corpus


def corpus_stats(corpus: list[SyntheticContract]) -> dict:
    """Summarize the corpus."""
    type_counts: dict[str, int] = {}
    for c in corpus:
        type_counts[c.contract_type] = type_counts.get(c.contract_type, 0) + 1

    children = [c for c in corpus if c.true_parent_id is not None]
    children_with_ref = [c for c in children if c.extracted_parent_reference is not None]
    children_with_clean_ref = [
        c for c in children
        if c.extracted_parent_reference is not None
        and any(p.reference_number == c.extracted_parent_reference for p in corpus)
    ]

    return {
        "total_contracts": len(corpus),
        "by_type": type_counts,
        "child_contracts": len(children),
        "children_with_extracted_ref": len(children_with_ref),
        "children_with_clean_ref": len(children_with_clean_ref),
        "children_with_missing_ref": len(children) - len(children_with_ref),
        "children_with_corrupted_ref": len(children_with_ref) - len(children_with_clean_ref),
    }


if __name__ == "__main__":
    corpus = generate_corpus(num_msas=60, seed=42)
    stats = corpus_stats(corpus)

    print("=" * 70)
    print("Synthetic Contract Corpus Generated")
    print("=" * 70)
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print()
    print("Sample MSA:")
    msa = next(c for c in corpus if c.contract_type == "MSA")
    print(f"  ID: {msa.id}, Ref: {msa.reference_number}")
    print(f"  Title: {msa.title}")
    print(f"  Parties: {[p['canonical_name'] for p in msa.parties]}")

    sample_child = next(c for c in corpus if c.true_parent_id is not None)
    print()
    print("Sample Child:")
    print(f"  ID: {sample_child.id}, Type: {sample_child.contract_type}")
    print(f"  True parent: {sample_child.true_parent_id}")
    print(f"  Extracted parent ref: {sample_child.extracted_parent_reference!r}")
