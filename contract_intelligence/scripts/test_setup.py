"""
Test GraphRAG Indexing Setup and Configuration
This script verifies that all configurations are correct before running the full indexing.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        "GRAPHRAG_API_KEY",
        "GRAPHRAG_API_BASE",
        "GRAPHRAG_API_VERSION",
        "GRAPHRAG_LLM_DEPLOYMENT_NAME",
        "GRAPHRAG_EMBEDDING_DEPLOYMENT_NAME"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    print("✓ All required environment variables are set")
    return True

def check_input_files():
    """Check if input files exist."""
    input_dir = Path("data/input")
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return False
    
    md_files = list(input_dir.glob("*.md"))
    if not md_files:
        print(f"❌ No markdown files found in {input_dir}")
        return False
    
    print(f"✓ Found {len(md_files)} markdown files in {input_dir}")
    return True

def check_config_files():
    """Check if configuration files exist."""
    config_files = [
        "graphrag_config/settings.yaml",
        "graphrag_config/prompts/entity_extraction.txt",
        "graphrag_config/prompts/claim_extraction.txt",
        "graphrag_config/prompts/community_report.txt"
    ]
    
    missing = []
    for file in config_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing configuration files: {', '.join(missing)}")
        return False
    
    print("✓ All configuration files found")
    return True

def main():
    print("=" * 70)
    print("GRAPHRAG INDEXING - PRE-FLIGHT CHECK")
    print("=" * 70)
    
    checks = [
        ("Environment Variables", check_environment),
        ("Input Files", check_input_files),
        ("Configuration Files", check_config_files)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n[{name}]")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Ready to run GraphRAG indexing")
        print("\nTo start indexing, run:")
        print("  uv run python -m graphrag.index --root . --config graphrag_config/settings.yaml")
    else:
        print("❌ CHECKS FAILED - Please fix the issues above")
        sys.exit(1)
    print("=" * 70)

if __name__ == "__main__":
    main()
