#!/usr/bin/env python3
"""Run GraphRAG indexing"""

import asyncio
from pathlib import Path
from graphrag.api import build_index
from graphrag.config.load_config import load_config

async def main():
    print("🚀 Starting GraphRAG indexing...")
    config_dir = Path("graphrag_config")
    config = load_config(config_dir)
    
    print(f"   Root dir: {config.root_dir}")
    print(f"   Output dir: {config.output.base_dir}")
    print(f"   Input dir: {config.input.storage.base_dir}")
    
    await build_index(config)
    print("\n✅ GraphRAG indexing complete!")

if __name__ == "__main__":
    asyncio.run(main())
