#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Unified Ingestion Pipeline

Orchestrates PostgreSQL and GraphRAG ingestion processes.
"""

import sys
from pathlib import Path
from typing import Optional

# Ensure data_ingestion is in path
sys.path.insert(0, str(Path(__file__).parent))

from postgres_ingestion import run_postgres_ingestion, get_database_statistics
from graphrag_ingestion import run_graphrag_indexing, prepare_input


def run_full_pipeline(
    num_contracts: Optional[int] = None,
    n_parallel: int = 5,
    skip_postgres_schema: bool = False,
    graphrag_config_dir: Optional[Path] = None,
    graphrag_root_dir: Optional[Path] = None,
    graphrag_verbose: bool = True,
    mode: str = "both",
) -> dict:
    """
    Run ingestion pipeline with selectable mode.
    
    Args:
        num_contracts: Number of contracts to process (None = all)
        n_parallel: Parallel workers for PostgreSQL ingestion
        skip_postgres_schema: Skip PostgreSQL schema initialization
        graphrag_config_dir: Path to GraphRAG config
        graphrag_root_dir: Root directory for GraphRAG
        graphrag_verbose: Enable verbose GraphRAG output
        mode: Pipeline mode:
            - "postgres": PostgreSQL + Apache AGE only
            - "graphrag": GraphRAG indexing only (LanceDB vectors)
            - "both": Run both PostgreSQL and GraphRAG (default)
            - "byog": PostgreSQL first, then export graph → GraphRAG
                      for community summarization only
        
    Returns:
        Dict with pipeline results:
        {
            'postgres_success': bool,
            'graphrag_success': bool,
            'postgres_stats': dict,
            'graphrag_files_indexed': int,
            'mode': str
        }
    """
    print("=" * 70)
    print(f"UNIFIED INGESTION PIPELINE — Mode: {mode.upper()}")
    print("=" * 70)
    
    results = {
        'postgres_success': False,
        'graphrag_success': False,
        'postgres_stats': {},
        'graphrag_files_indexed': 0,
        'mode': mode,
    }
    
    run_postgres = mode in ("postgres", "both", "byog")
    run_graphrag = mode in ("graphrag", "both", "byog")
    
    # Phase 1: PostgreSQL Ingestion
    if run_postgres:
        print("\n" + "=" * 70)
        print("PHASE 1: PostgreSQL Ingestion")
        print("=" * 70)
        
        postgres_success = run_postgres_ingestion(
            num_contracts=num_contracts,
            n_parallel=n_parallel,
            skip_schema_init=skip_postgres_schema
        )
        
        results['postgres_success'] = postgres_success
        
        if postgres_success:
            results['postgres_stats'] = get_database_statistics()
        else:
            print("\n[!] PostgreSQL ingestion failed")
            if run_graphrag:
                print("    Continuing to GraphRAG...")
    else:
        print("\n[*] Skipping PostgreSQL ingestion (mode={})".format(mode))
    
    # Phase 2: GraphRAG Indexing
    if run_graphrag:
        print("\n" + "=" * 70)
        if mode == "byog":
            print("PHASE 2: GraphRAG BYOG (Bring Your Own Graph)")
            print("  → Skipping LLM extraction, using Postgres graph for community detection")
        else:
            print("PHASE 2: GraphRAG Knowledge Graph Indexing")
        print("=" * 70)
        
        num_files = prepare_input(num_contracts=num_contracts)
        results['graphrag_files_indexed'] = num_files
        
        if num_files == 0 and mode != "byog":
            print("\n[!] No contract files found for GraphRAG")
            results['graphrag_success'] = False
        else:
            graphrag_success = run_graphrag_indexing(
                config_dir=graphrag_config_dir,
                root_dir=graphrag_root_dir,
                verbose=graphrag_verbose
            )
            results['graphrag_success'] = graphrag_success
    else:
        print("\n[*] Skipping GraphRAG indexing (mode={})".format(mode))
    
    # Final Summary
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    
    print(f"\n[*] PostgreSQL Ingestion:")
    print(f"    Status: {'✓ SUCCESS' if results['postgres_success'] else '✗ FAILED'}")
    if results['postgres_stats']:
        for table, count in results['postgres_stats'].items():
            print(f"    {table}: {count}")
    
    print(f"\n[*] GraphRAG Indexing:")
    print(f"    Status: {'✓ SUCCESS' if results['graphrag_success'] else '✗ FAILED'}")
    print(f"    Files indexed: {results['graphrag_files_indexed']}")
    
    all_success = results['postgres_success'] and results['graphrag_success']
    print(f"\n{'=' * 70}")
    print(f"Overall: {'✓ ALL PIPELINES SUCCESSFUL' if all_success else '✗ SOME PIPELINES FAILED'}")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    """Standalone execution with interactive mode."""
    import sys
    
    print("\nUnified Ingestion Pipeline")
    print("=" * 40)
    print("1. Process 1 contract  (both)")
    print("2. Process 2 contracts (both)")
    print("3. Process 5 contracts (both)")
    print("4. Process all contracts (both)")
    print("5. GraphRAG only (2 contracts)")
    print("6. PostgreSQL only (2 contracts)")
    print("7. PostgreSQL only (all contracts)")
    print("8. BYOG: Postgres → GraphRAG community detection")
    
    choice = input("\nSelect option [1-8]: ").strip()
    
    if choice == "1":
        run_full_pipeline(num_contracts=1, mode="both")
    elif choice == "2":
        run_full_pipeline(num_contracts=2, mode="both")
    elif choice == "3":
        run_full_pipeline(num_contracts=5, mode="both")
    elif choice == "4":
        run_full_pipeline(num_contracts=None, mode="both")
    elif choice == "5":
        # GraphRAG only
        num_files = prepare_input(num_contracts=2)
        if num_files > 0:
            run_graphrag_indexing()
        else:
            print("\n[!] No contract files found")
    elif choice == "6":
        # PostgreSQL only (2 contracts)
        run_full_pipeline(num_contracts=2, mode="postgres")
    elif choice == "7":
        # PostgreSQL only (all contracts)
        run_full_pipeline(num_contracts=None, mode="postgres")
    elif choice == "8":
        # BYOG mode
        run_full_pipeline(num_contracts=None, mode="byog")
    else:
        print("\n[!] Invalid selection")
