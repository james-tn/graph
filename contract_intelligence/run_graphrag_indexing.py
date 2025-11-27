#!/usr/bin/env python3
"""Debug GraphRAG indexing with verbose output"""

import asyncio
import logging
from pathlib import Path
from graphrag.api import build_index
from graphrag.config.load_config import load_config

# Enable verbose logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    print("=" * 70)
    print("DEBUG: GraphRAG Indexing with 1 Test Document")
    print("=" * 70)
    
    config_dir = Path("graphrag_config")
    config = load_config(config_dir)
    
    print(f"\n[Configuration]")
    print(f"   Root dir: {config.root_dir}")
    print(f"   Input base_dir: {config.input.storage.base_dir}")
    print(f"   Output base_dir: {config.output.base_dir}")
    print(f"   Output type: {config.output.type}")
    print(f"   Cache base_dir: {config.cache.base_dir}")
    
    # Check if output is file-based
    if config.output.type == "file":
        output_path = Path(config.root_dir) / config.output.base_dir
        print(f"   Full output path: {output_path}")
        print(f"   Output path exists: {output_path.exists()}")
    
    print(f"\n[Starting indexing...]")
    print(f"   (Check logs above for workflow execution details)")
    print()
    
    results = await build_index(config, verbose=True)
    
    print(f"\n[Indexing completed!]")
    print(f"   Workflows executed: {len(results)}")
    
    for result in results:
        print(f"   - {result.workflow}: {'SUCCESS' if not result.errors else 'ERRORS'}")
        if result.errors:
            for error in result.errors:
                print(f"     Error: {error}")
    
    # Check what files were created
    print(f"\n[Checking output directory...]")
    output_path = Path(config.root_dir) / config.output.base_dir
    
    if output_path.exists():
        print(f"   Output directory: {output_path}")
        
        # List all files
        all_files = list(output_path.rglob("*"))
        parquet_files = list(output_path.rglob("*.parquet"))
        json_files = list(output_path.rglob("*.json"))
        lance_dirs = list(output_path.rglob("*.lance"))
        
        print(f"   Total items: {len(all_files)}")
        print(f"   Parquet files: {len(parquet_files)}")
        print(f"   JSON files: {len(json_files)}")
        print(f"   Lance directories: {len(lance_dirs)}")
        
        if parquet_files:
            print(f"\n   [SUCCESS] Parquet files found:")
            for f in parquet_files[:10]:  # Show first 10
                print(f"     - {f.relative_to(output_path)}")
        else:
            print(f"\n   [FAILURE] NO PARQUET FILES FOUND")
        
        if json_files:
            print(f"\n   JSON files:")
            for f in json_files:
                print(f"     - {f.relative_to(output_path)}")
    else:
        print(f"   [ERROR] Output directory does not exist: {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
