#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
GraphRAG Ingestion Module

Handles knowledge graph creation using Microsoft GraphRAG.
"""

import os
import sys
from pathlib import Path

# Force UTF-8 encoding for Windows console to handle Unicode characters
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Reconfigure stdout/stderr to use UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')


def prepare_input(input_dir: Path = None, num_contracts: int = None) -> int:
    """
    Prepare contract files for GraphRAG ingestion.
    
    Args:
        input_dir: Directory containing contract files
        num_contracts: Limit to first N contracts (None = all)
        
    Returns:
        Number of contract files found
    """
    if input_dir is None:
        # Resolve relative to project root
        project_root = Path(__file__).parent.parent
        input_dir = project_root / "data" / "input"
    
    print("\n[*] Preparing GraphRAG input...")
    contract_files = sorted(input_dir.glob("contract_*.md"))
    
    if num_contracts is not None:
        contract_files = contract_files[:num_contracts]
        print(f"    Found {len(contract_files)} contract files (limited to {num_contracts})")
    else:
        print(f"    Found {len(contract_files)} contract files")
    
    return len(contract_files)


def run_graphrag_indexing(
    config_dir: Path = None,
    root_dir: Path = None,
    verbose: bool = False,
    resume: str = None
) -> bool:
    """
    Run GraphRAG indexing pipeline.
    
    Args:
        config_dir: Path to GraphRAG config directory
        root_dir: Root directory for GraphRAG
        verbose: Enable verbose output
        resume: Resume from specific workflow
        
    Returns:
        True if all workflows succeeded
    """
    print("=" * 70)
    print("GraphRAG Knowledge Graph Indexing")
    print("=" * 70)
    
    try:
        from graphrag.api import build_index
        from graphrag.config.load_config import load_config
        import asyncio
        
        # Configuration
        if root_dir is None:
            root_dir = Path.cwd()
        if config_dir is None:
            config_dir = root_dir / "graphrag_config"
        
        print(f"\n[*] Configuration:")
        print(f"    Root: {root_dir}")
        print(f"    Config: {config_dir}")
        
        # Load config
        config = load_config(config_dir)
        
        print("\n[*] Starting indexing pipeline...")
        
        # Run indexing (async)
        async def run():
            return await build_index(config, verbose=verbose)
        
        results = asyncio.run(run())
        
        print(f"\n{'=' * 70}")
        print(f"Indexing Complete: {len(results)} workflows")
        print("=" * 70)
        
        # Show results
        workflows_with_errors = []
        for result in results:
            status = "ERROR" if result.errors else "SUCCESS"
            print(f"  {status:8} {result.workflow}")
            if result.errors:
                workflows_with_errors.append(result.workflow)
                for error in result.errors[:2]:  # Show first 2 errors
                    print(f"           {error}")
        
        # Check output
        output_dir = root_dir / "data" / "output"
        if output_dir.exists():
            parquet_files = list(output_dir.glob("*.parquet"))
            lance_dirs = [d for d in output_dir.iterdir() if d.is_dir() and d.name.endswith('.lance')]
            
            print(f"\n[*] Output Summary:")
            print(f"    Directory: {output_dir}")
            print(f"    Parquet files: {len(parquet_files)}")
            print(f"    LanceDB tables: {len(lance_dirs)}")
            
            if parquet_files:
                print(f"\n    Parquet files:")
                for f in sorted(parquet_files):
                    size_kb = f.stat().st_size / 1024
                    print(f"      - {f.name:<30} ({size_kb:>8.1f} KB)")
            
            if lance_dirs:
                print(f"\n    LanceDB tables:")
                for d in sorted(lance_dirs):
                    print(f"      - {d.name}")
        
        return len(workflows_with_errors) == 0
        
    except Exception as e:
        print(f"\n[X] GraphRAG indexing error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    """Standalone execution."""
    import sys
    
    # Check for command line argument
    num_contracts = None
    if len(sys.argv) > 1:
        try:
            num_contracts = int(sys.argv[1])
            print(f"[*] Processing limited to {num_contracts} contracts")
        except ValueError:
            print("[!] Invalid number, processing all contracts")
    
    num_files = prepare_input(num_contracts=num_contracts)
    
    if num_files == 0:
        print("\n[!] No contract files found")
        print("    Generate contracts first: uv run python scripts/generate_seed_data.py")
    else:
        print(f"\n[*] Ready to index {num_files} contracts")
        if num_files <= 5:
            print("    This will take 1-2 minutes...")
        else:
            print("    This will take 5-10 minutes...")
        
        success = run_graphrag_indexing()
        print("\n" + ("✓ Success!" if success else "✗ Had errors"))
