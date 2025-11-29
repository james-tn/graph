#!/usr/bin/env python3
"""
Data Exploration and Analysis Script

Analyzes ingested contract data and generates a comprehensive Markdown report
with statistics, entity information, relationships, and visualizations.
"""

import os
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_NAME = os.getenv("POSTGRES_DATABASE", "contract_intelligence")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_ADMIN_PASSWORD")

def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require',
        cursor_factory=RealDictCursor
    )


def analyze_contracts(conn):
    """Analyze contract data."""
    with conn.cursor() as cur:
        # Total contracts
        cur.execute("SELECT COUNT(*) as count FROM contracts")
        total_contracts = cur.fetchone()['count']
        
        # Contracts by type
        cur.execute("""
            SELECT contract_type, COUNT(*) as count 
            FROM contracts 
            GROUP BY contract_type 
            ORDER BY count DESC
        """)
        contracts_by_type = cur.fetchall()
        
        # Contracts by status
        cur.execute("""
            SELECT status, COUNT(*) as count 
            FROM contracts 
            GROUP BY status 
            ORDER BY count DESC
        """)
        contracts_by_status = cur.fetchall()
        
        # Contracts by governing law
        cur.execute("""
            SELECT governing_law, COUNT(*) as count 
            FROM contracts 
            WHERE governing_law IS NOT NULL
            GROUP BY governing_law 
            ORDER BY count DESC
            LIMIT 10
        """)
        contracts_by_law = cur.fetchall()
        
        # Contract relationships
        cur.execute("""
            SELECT relationship_type, COUNT(*) as count 
            FROM contract_relationships 
            GROUP BY relationship_type 
            ORDER BY count DESC
        """)
        relationships = cur.fetchall()
        
        # Orphaned relationships (parent not yet ingested)
        cur.execute("""
            SELECT COUNT(*) as count 
            FROM contract_relationships 
            WHERE parent_contract_id IS NULL
        """)
        orphaned = cur.fetchone()['count']
        
        return {
            'total': total_contracts,
            'by_type': contracts_by_type,
            'by_status': contracts_by_status,
            'by_law': contracts_by_law,
            'relationships': relationships,
            'orphaned': orphaned
        }


def analyze_parties(conn):
    """Analyze party data."""
    with conn.cursor() as cur:
        # Total parties
        cur.execute("SELECT COUNT(*) as count FROM parties")
        total_parties = cur.fetchone()['count']
        
        # Top parties by contract count
        cur.execute("""
            SELECT p.name, COUNT(DISTINCT pc.contract_id) as contract_count
            FROM parties p
            JOIN parties_contracts pc ON p.id = pc.party_id
            GROUP BY p.name
            ORDER BY contract_count DESC
            LIMIT 10
        """)
        top_parties = cur.fetchall()
        
        # Parties by role
        cur.execute("""
            SELECT pr.name as role, COUNT(DISTINCT pc.party_id) as party_count
            FROM parties_contracts pc
            JOIN party_roles pr ON pc.role_id = pr.id
            GROUP BY pr.name
            ORDER BY party_count DESC
        """)
        parties_by_role = cur.fetchall()
        
        # Party types
        cur.execute("""
            SELECT party_type, COUNT(*) as count
            FROM parties
            WHERE party_type IS NOT NULL
            GROUP BY party_type
            ORDER BY count DESC
        """)
        party_types = cur.fetchall()
        
        return {
            'total': total_parties,
            'top_parties': top_parties,
            'by_role': parties_by_role,
            'by_type': party_types
        }


def analyze_clauses(conn):
    """Analyze clause data."""
    with conn.cursor() as cur:
        # Total clauses
        cur.execute("SELECT COUNT(*) as count FROM clauses")
        total_clauses = cur.fetchone()['count']
        
        # Clauses by type
        cur.execute("""
            SELECT ct.name as clause_type, COUNT(*) as count
            FROM clauses c
            JOIN clause_types ct ON c.clause_type_id = ct.id
            GROUP BY ct.name
            ORDER BY count DESC
        """)
        clauses_by_type = cur.fetchall()
        
        # Clauses by risk level
        cur.execute("""
            SELECT risk_level, COUNT(*) as count
            FROM clauses
            WHERE risk_level IS NOT NULL
            GROUP BY risk_level
            ORDER BY CASE risk_level 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
            END
        """)
        clauses_by_risk = cur.fetchall()
        
        # Average clauses per contract
        cur.execute("""
            SELECT AVG(clause_count) as avg_clauses
            FROM (
                SELECT contract_id, COUNT(*) as clause_count
                FROM clauses
                GROUP BY contract_id
            ) subq
        """)
        avg_clauses = cur.fetchone()['avg_clauses']
        
        return {
            'total': total_clauses,
            'by_type': clauses_by_type,
            'by_risk': clauses_by_risk,
            'avg_per_contract': float(avg_clauses) if avg_clauses else 0
        }


def analyze_risks(conn):
    """Analyze risk data."""
    with conn.cursor() as cur:
        # Total risks
        cur.execute("SELECT COUNT(*) as count FROM risks")
        total_risks = cur.fetchone()['count']
        
        # Risks by type
        cur.execute("""
            SELECT rt.name as risk_type, COUNT(*) as count
            FROM risks r
            JOIN risk_types rt ON r.risk_type_id = rt.id
            GROUP BY rt.name
            ORDER BY count DESC
        """)
        risks_by_type = cur.fetchall()
        
        # Risks by level
        cur.execute("""
            SELECT risk_level, COUNT(*) as count
            FROM risks
            GROUP BY risk_level
            ORDER BY CASE risk_level 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
            END
        """)
        risks_by_level = cur.fetchall()
        
        # Contracts with high-risk items
        cur.execute("""
            SELECT COUNT(DISTINCT contract_id) as count
            FROM risks
            WHERE risk_level = 'high'
        """)
        high_risk_contracts = cur.fetchone()['count']
        
        return {
            'total': total_risks,
            'by_type': risks_by_type,
            'by_level': risks_by_level,
            'high_risk_contracts': high_risk_contracts
        }


def analyze_obligations_rights(conn):
    """Analyze obligations and rights."""
    with conn.cursor() as cur:
        # Total obligations
        cur.execute("SELECT COUNT(*) as count FROM obligations")
        total_obligations = cur.fetchone()['count']
        
        # High-impact obligations
        cur.execute("""
            SELECT COUNT(*) as count 
            FROM obligations 
            WHERE is_high_impact = TRUE
        """)
        high_impact_obligations = cur.fetchone()['count']
        
        # Total rights
        cur.execute("SELECT COUNT(*) as count FROM rights")
        total_rights = cur.fetchone()['count']
        
        # Top parties by obligation count
        cur.execute("""
            SELECT p.name, COUNT(*) as obligation_count
            FROM obligations o
            JOIN parties p ON o.responsible_party_id = p.id
            GROUP BY p.name
            ORDER BY obligation_count DESC
            LIMIT 5
        """)
        top_obligated_parties = cur.fetchall()
        
        return {
            'total_obligations': total_obligations,
            'high_impact_obligations': high_impact_obligations,
            'total_rights': total_rights,
            'top_obligated_parties': top_obligated_parties
        }


def analyze_monetary_values(conn):
    """Analyze monetary values."""
    with conn.cursor() as cur:
        # Total monetary values
        cur.execute("SELECT COUNT(*) as count FROM monetary_values")
        total_values = cur.fetchone()['count']
        
        # Values by currency
        cur.execute("""
            SELECT currency, COUNT(*) as count, SUM(amount) as total_amount
            FROM monetary_values
            GROUP BY currency
            ORDER BY count DESC
        """)
        by_currency = cur.fetchall()
        
        # Values by type
        cur.execute("""
            SELECT value_type, COUNT(*) as count
            FROM monetary_values
            WHERE value_type IS NOT NULL
            GROUP BY value_type
            ORDER BY count DESC
            LIMIT 10
        """)
        by_type = cur.fetchall()
        
        return {
            'total': total_values,
            'by_currency': by_currency,
            'by_type': by_type
        }


def analyze_contract_families(conn):
    """Analyze contract family structures."""
    with conn.cursor() as cur:
        # Find master agreements with children
        cur.execute("""
            SELECT 
                c.reference_number,
                c.title,
                c.contract_type,
                COUNT(DISTINCT cr.child_contract_id) as child_count
            FROM contracts c
            JOIN contract_relationships cr ON c.id = cr.parent_contract_id
            GROUP BY c.reference_number, c.title, c.contract_type
            HAVING COUNT(DISTINCT cr.child_contract_id) > 0
            ORDER BY child_count DESC
            LIMIT 10
        """)
        master_agreements = cur.fetchall()
        
        # Get sample family tree for largest family
        if master_agreements:
            largest_ref = master_agreements[0]['reference_number']
            cur.execute("""
                WITH RECURSIVE contract_tree AS (
                    SELECT 
                        c.id, c.reference_number, c.title, c.contract_type,
                        0 as level,
                        CAST(c.reference_number AS VARCHAR) as path
                    FROM contracts c
                    WHERE c.reference_number = %s
                    
                    UNION ALL
                    
                    SELECT 
                        c.id, c.reference_number, c.title, c.contract_type,
                        ct.level + 1,
                        CAST(ct.path || ' → ' || c.reference_number AS VARCHAR)
                    FROM contracts c
                    JOIN contract_relationships cr ON c.id = cr.child_contract_id
                    JOIN contract_tree ct ON cr.parent_contract_id = ct.id
                    WHERE ct.level < 3
                )
                SELECT * FROM contract_tree ORDER BY level, reference_number
            """, (largest_ref,))
            sample_tree = cur.fetchall()
        else:
            sample_tree = []
        
        return {
            'master_agreements': master_agreements,
            'sample_tree': sample_tree
        }


def generate_mermaid_contract_hierarchy(sample_tree):
    """Generate Mermaid diagram for contract hierarchy."""
    if not sample_tree or len(sample_tree) < 2:
        return None
    
    lines = ["```mermaid", "graph TD"]
    
    # Create nodes with safe IDs
    node_map = {}
    for i, row in enumerate(sample_tree):
        node_id = f"N{i}"
        node_map[row['reference_number']] = node_id
        
        # Style based on level
        ref = row['reference_number'] or f"Contract_{i}"
        contract_type = row['contract_type'] or 'Unknown'
        label = f"{ref}<br/>{contract_type}"
        
        lines.append(f"    {node_id}[\"{label}\"]")
        
        # Add styling
        if row['level'] == 0:
            lines.append(f"    style {node_id} fill:#e1f5ff,stroke:#0066cc,stroke-width:3px")
        elif 'SOW' in contract_type or 'Statement of Work' in contract_type:
            lines.append(f"    style {node_id} fill:#fff4e6,stroke:#ff9800")
        elif 'Amendment' in contract_type:
            lines.append(f"    style {node_id} fill:#ffe6e6,stroke:#d32f2f")
    
    # Create edges
    for row in sample_tree[1:]:  # Skip root
        parts = row['path'].split(' → ')
        if len(parts) >= 2:
            parent_ref = parts[-2]
            child_ref = parts[-1]
            if parent_ref in node_map and child_ref in node_map:
                lines.append(f"    {node_map[parent_ref]} --> {node_map[child_ref]}")
    
    lines.append("```")
    return "\n".join(lines)


def generate_mermaid_pie_chart(data, title):
    """Generate Mermaid pie chart."""
    if not data:
        return None
    
    lines = ["```mermaid", f"pie title {title}"]
    for item in data:
        # Handle different key names (count vs party_count, etc.)
        count = item.get('count') or item.get('party_count') or item.get('contract_count') or 0
        # Get the first non-count key for the label
        label_keys = [k for k in item.keys() if 'count' not in k.lower()]
        if label_keys:
            label = item[label_keys[0]]
            lines.append(f'    "{label}" : {count}')
    lines.append("```")
    return "\n".join(lines)


def generate_report(data, output_file):
    """Generate Markdown report."""
    report = []
    
    # Header
    report.append("# Contract Intelligence Database Analysis Report")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n**Database:** {DB_NAME}")
    report.append("\n---\n")
    
    # Executive Summary
    report.append("## 📊 Executive Summary\n")
    report.append(f"- **Total Contracts:** {data['contracts']['total']}")
    report.append(f"- **Total Parties:** {data['parties']['total']}")
    report.append(f"- **Total Clauses:** {data['clauses']['total']}")
    report.append(f"- **Total Risks Identified:** {data['risks']['total']}")
    report.append(f"- **Total Obligations:** {data['obligations_rights']['total_obligations']}")
    report.append(f"- **Total Rights:** {data['obligations_rights']['total_rights']}")
    report.append(f"- **Total Monetary Values:** {data['monetary_values']['total']}")
    report.append("\n---\n")
    
    # Contracts Section
    report.append("## 📄 Contracts Analysis\n")
    
    report.append(f"### Contract Types (Total: {data['contracts']['total']})\n")
    if data['contracts']['by_type']:
        report.append("| Contract Type | Count |")
        report.append("|---------------|-------|")
        for item in data['contracts']['by_type']:
            report.append(f"| {item['contract_type'] or 'Unknown'} | {item['count']} |")
        report.append("")
        
        # Pie chart for contract types
        pie = generate_mermaid_pie_chart(data['contracts']['by_type'][:8], "Contract Types Distribution")
        if pie:
            report.append(pie)
            report.append("")
    
    report.append(f"### Contract Status\n")
    if data['contracts']['by_status']:
        report.append("| Status | Count |")
        report.append("|--------|-------|")
        for item in data['contracts']['by_status']:
            report.append(f"| {item['status']} | {item['count']} |")
        report.append("")
    
    report.append(f"### Top Governing Laws\n")
    if data['contracts']['by_law']:
        report.append("| Jurisdiction | Contract Count |")
        report.append("|--------------|----------------|")
        for item in data['contracts']['by_law']:
            report.append(f"| {item['governing_law']} | {item['count']} |")
        report.append("")
    
    # Contract Relationships
    report.append("### 🔗 Contract Relationships\n")
    if data['contracts']['relationships']:
        report.append("| Relationship Type | Count |")
        report.append("|-------------------|-------|")
        for item in data['contracts']['relationships']:
            report.append(f"| {item['relationship_type']} | {item['count']} |")
        report.append("")
    
    if data['contracts']['orphaned'] > 0:
        report.append(f"⚠️ **Orphaned Relationships:** {data['contracts']['orphaned']} (parent contracts not yet ingested)")
        report.append("")
    
    # Contract Families
    if data['families']['master_agreements']:
        report.append("### 🌳 Major Contract Families\n")
        report.append("| Master Agreement | Title | Type | Children |")
        report.append("|------------------|-------|------|----------|")
        for ma in data['families']['master_agreements']:
            report.append(f"| {ma['reference_number'] or 'N/A'} | {ma['title'][:50]}... | {ma['contract_type']} | {ma['child_count']} |")
        report.append("")
        
        # Sample hierarchy
        if data['families']['sample_tree']:
            report.append("#### Sample Contract Hierarchy\n")
            mermaid = generate_mermaid_contract_hierarchy(data['families']['sample_tree'])
            if mermaid:
                report.append(mermaid)
                report.append("")
    
    report.append("---\n")
    
    # Parties Section
    report.append("## 👥 Parties Analysis\n")
    
    report.append(f"### Top Parties by Contract Count\n")
    if data['parties']['top_parties']:
        report.append("| Party Name | Contracts |")
        report.append("|------------|-----------|")
        for party in data['parties']['top_parties']:
            report.append(f"| {party['name']} | {party['contract_count']} |")
        report.append("")
    
    report.append(f"### Party Roles Distribution\n")
    if data['parties']['by_role']:
        report.append("| Role | Unique Parties |")
        report.append("|------|----------------|")
        for item in data['parties']['by_role']:
            report.append(f"| {item['role']} | {item['party_count']} |")
        report.append("")
        
        # Pie chart for roles
        pie = generate_mermaid_pie_chart(data['parties']['by_role'][:6], "Party Roles")
        if pie:
            report.append(pie)
            report.append("")
    
    if data['parties']['by_type']:
        report.append(f"### Party Types\n")
        report.append("| Party Type | Count |")
        report.append("|------------|-------|")
        for item in data['parties']['by_type']:
            report.append(f"| {item['party_type']} | {item['count']} |")
        report.append("")
    
    report.append("---\n")
    
    # Clauses Section
    report.append("## 📋 Clauses Analysis\n")
    
    report.append(f"**Total Clauses:** {data['clauses']['total']}")
    report.append(f"\n**Average Clauses per Contract:** {data['clauses']['avg_per_contract']:.1f}\n")
    
    report.append(f"### Clause Types Distribution\n")
    if data['clauses']['by_type']:
        report.append("| Clause Type | Count |")
        report.append("|-------------|-------|")
        for item in data['clauses']['by_type']:
            report.append(f"| {item['clause_type']} | {item['count']} |")
        report.append("")
    
    report.append(f"### Risk Levels\n")
    if data['clauses']['by_risk']:
        report.append("| Risk Level | Clause Count |")
        report.append("|------------|--------------|")
        for item in data['clauses']['by_risk']:
            emoji = "⚠️" if item['risk_level'] == 'high' else "⚡" if item['risk_level'] == 'medium' else "✓"
            report.append(f"| {emoji} {item['risk_level'].capitalize()} | {item['count']} |")
        report.append("")
        
        # Pie chart for risk levels
        pie = generate_mermaid_pie_chart(data['clauses']['by_risk'], "Clause Risk Distribution")
        if pie:
            report.append(pie)
            report.append("")
    
    report.append("---\n")
    
    # Risks Section
    report.append("## ⚠️ Risks Analysis\n")
    
    report.append(f"**Total Risk Items:** {data['risks']['total']}")
    report.append(f"\n**Contracts with High Risks:** {data['risks']['high_risk_contracts']}\n")
    
    if data['risks']['by_type']:
        report.append(f"### Risk Types\n")
        report.append("| Risk Type | Count |")
        report.append("|-----------|-------|")
        for item in data['risks']['by_type']:
            report.append(f"| {item['risk_type']} | {item['count']} |")
        report.append("")
    
    if data['risks']['by_level']:
        report.append(f"### Risk Severity Distribution\n")
        report.append("| Risk Level | Count |")
        report.append("|------------|-------|")
        for item in data['risks']['by_level']:
            emoji = "⚠️" if item['risk_level'] == 'high' else "⚡" if item['risk_level'] == 'medium' else "✓"
            report.append(f"| {emoji} {item['risk_level'].capitalize()} | {item['count']} |")
        report.append("")
    
    report.append("---\n")
    
    # Obligations and Rights
    report.append("## ⚖️ Obligations & Rights Analysis\n")
    
    report.append(f"**Total Obligations:** {data['obligations_rights']['total_obligations']}")
    report.append(f"\n**High-Impact Obligations:** {data['obligations_rights']['high_impact_obligations']}")
    report.append(f"\n**Total Rights:** {data['obligations_rights']['total_rights']}\n")
    
    if data['obligations_rights']['top_obligated_parties']:
        report.append(f"### Top Parties by Obligation Count\n")
        report.append("| Party | Obligations |")
        report.append("|-------|-------------|")
        for party in data['obligations_rights']['top_obligated_parties']:
            report.append(f"| {party['name']} | {party['obligation_count']} |")
        report.append("")
    
    report.append("---\n")
    
    # Monetary Values
    report.append("## 💰 Monetary Values Analysis\n")
    
    report.append(f"**Total Monetary References:** {data['monetary_values']['total']}\n")
    
    if data['monetary_values']['by_currency']:
        report.append(f"### Currency Distribution\n")
        report.append("| Currency | Count | Total Amount |")
        report.append("|----------|-------|--------------|")
        for item in data['monetary_values']['by_currency']:
            total = f"{item['total_amount']:,.2f}" if item['total_amount'] else "N/A"
            report.append(f"| {item['currency']} | {item['count']} | {total} |")
        report.append("")
    
    if data['monetary_values']['by_type']:
        report.append(f"### Value Types\n")
        report.append("| Value Type | Count |")
        report.append("|------------|-------|")
        for item in data['monetary_values']['by_type']:
            report.append(f"| {item['value_type']} | {item['count']} |")
        report.append("")
    
    report.append("---\n")
    
    # Footer
    report.append("## 📈 Data Quality Notes\n")
    report.append("- All data extracted using LLM-based contract analysis")
    report.append("- Embeddings generated for semantic search capabilities")
    report.append("- Full-text search vectors created for keyword matching")
    report.append("- Graph relationships established for multi-hop reasoning")
    report.append(f"\n*Report generated automatically on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*")
    
    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Report generated: {output_file}")


def main():
    """Main execution."""
    print("=" * 70)
    print("Contract Intelligence Database Explorer")
    print("=" * 70)
    print()
    
    print("📊 Connecting to database...")
    conn = get_db_connection()
    
    print("🔍 Analyzing contracts...")
    contracts_data = analyze_contracts(conn)
    
    print("👥 Analyzing parties...")
    parties_data = analyze_parties(conn)
    
    print("📋 Analyzing clauses...")
    clauses_data = analyze_clauses(conn)
    
    print("⚠️ Analyzing risks...")
    risks_data = analyze_risks(conn)
    
    print("⚖️ Analyzing obligations & rights...")
    obligations_rights_data = analyze_obligations_rights(conn)
    
    print("💰 Analyzing monetary values...")
    monetary_data = analyze_monetary_values(conn)
    
    print("🌳 Analyzing contract families...")
    families_data = analyze_contract_families(conn)
    
    conn.close()
    
    # Compile all data
    all_data = {
        'contracts': contracts_data,
        'parties': parties_data,
        'clauses': clauses_data,
        'risks': risks_data,
        'obligations_rights': obligations_rights_data,
        'monetary_values': monetary_data,
        'families': families_data
    }
    
    # Generate report
    output_dir = Path(__file__).parent.parent / 'data' / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f'database_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    
    print(f"\n📝 Generating report...")
    generate_report(all_data, output_file)
    
    print("\n" + "=" * 70)
    print("✅ Analysis Complete!")
    print(f"📄 Report saved to: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
