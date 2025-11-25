"""Postgres Graph Agent sample for the Contract Intelligence Platform.

This script lives inside the application repo (graph/contract_intelligence)
and demonstrates how to specialize an LLM agent that produces SQL or graph
(Cypher) plans over the ontology captured in DESIGN.md. It does **not** run any
queries; instead it emits structured JSON that downstream components can
execute safely.
"""

from __future__ import annotations

import asyncio
from typing import Final

from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

ONTOLOGY_BRIEF: Final[str] = """
Key tables
----------
contracts(contract_id, contract_type, effective_date, expiration_date, status,
          governing_law, term_type, risk_score_overall)
parties(party_id, name, normalized_name, is_internal, jurisdiction_country,
        jurisdiction_state, risk_profile)
clauses(clause_id, contract_id, clause_type, section_label, title, text,
        risk_level, is_standard, embedding, full_text_vector)
obligations(obligation_id, clause_id, short_label, description,
            responsible_party_role, beneficiary_party_role, trigger_event,
            due_timing, due_days, frequency, penalty_type, is_high_impact)
rights(right_id, clause_id, holder_role, description, condition_text,
       is_termination_right, is_renewal_right)
monetary_values(monetary_value_id, contract_id, clause_id, amount, currency,
                value_type, context, multiple_of_fees)
risks(risk_id, clause_id, risk_type, risk_level, rationale, detected_by,
      is_confirmed)
Edges
-----
contract_party_edges(contract_id, party_id, role)
contract_clause_edges(contract_id, clause_id)
clause_obligation_edges(clause_id, obligation_id)
clause_right_edges(clause_id, right_id)
clause_risk_edges(clause_id, risk_id)
contract_amendment_edges(parent_contract_id, child_contract_id, amendment_type)
"""

ROUTING_RULES: Final[str] = """
- Use SQL when the user asks for counts, sums, averages, or filtering by
  structured attributes (dates, party, contract type, risk level, monetary
  thresholds).
- Use Graph (Cypher) when multi-hop relationships or conditional paths are
  required, e.g., party -> contract -> clause -> risk, amendment chains, or
  shared obligations.
- Use Hybrid (multiple steps) when both structured filters and graph traversal
  are necessary.
- If the user asks for "similar" or fuzzy clause discovery, note that a
  semantic search call is required before issuing SQL filters.
"""

AGENT_INSTRUCTIONS: Final[str] = f"""
You are the Postgres Graph Agent for the Contract Intelligence Platform.
Analyze the user question and produce SQL and/or graph (Cypher) statements that
can run against the Azure PostgreSQL ontology.

Ontology:
{ONTOLOGY_BRIEF}

Routing guidance:
{ROUTING_RULES}

Return JSON ONLY with this schema:
{{
  "primary_mode": "sql" | "graph" | "hybrid",
  "steps": [
    {{
      "step": 1,
      "executor": "sql" | "graph",
      "description": "Intent for this step",
      "statement": "SQL or Cypher with named parameters",
      "parameters": {{"param_name": "value or placeholder"}},
      "expected_fields": ["contract_id", "clause_id", "risk_level"],
      "notes": "Assumptions / follow-ups"
    }}
  ],
  "citation_keys": ["contract_id", "clause_id", "section_label"],
  "confidence": "high" | "medium" | "low",
  "justification": "Why this plan answers the question"
}}

Rules:
1. Always apply tenant filters when the user mentions an organization.
2. Use named parameters (e.g., :party_name) instead of inlining user input.
3. Cap SQL result sets with LIMIT unless aggregates are requested.
4. Graph queries must reference node/edge labels mirroring the ontology.
5. When ontology support is missing, describe the limitation in notes.
"""


async def run_question(agent, question: str) -> None:
    print(f"\nUser: {question}")
    result = await agent.run(question)
    print("Plan:\n", result)


async def main() -> None:
    client = AzureOpenAIChatClient(credential=AzureCliCredential())
    agent = client.create_agent(instructions=AGENT_INSTRUCTIONS)

    sample_questions = [
        "List active vendor contracts handling EU personal data where the liability cap exceeds 2x fees and there is no DPA clause.",
        "Which amendments modified limitation of liability clauses for Contoso in the last 12 months?",
        "Show clauses similar to this data breach notification text that also explicitly mention GDPR notification timing.",
    ]

    for question in sample_questions:
        await run_question(agent, question)


if __name__ == "__main__":
    asyncio.run(main())
