"""Run the GraphRAG ingestion/indexing pipeline with the custom contract config."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
from pathlib import Path
from typing import Sequence

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from graphrag.api import build_index
from graphrag.config.load_config import load_config
from graphrag.index.typing.pipeline_run_result import PipelineRunResult

try:  # Console callbacks were removed in newer GraphRAG builds
    from graphrag.callbacks.console.callbacks import ConsoleWorkflowCallbacks
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    ConsoleWorkflowCallbacks = None  # type: ignore[assignment]


LOGGER = logging.getLogger("contract-ingestion")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the GraphRAG ingestion pipeline for contract intelligence data.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("graphrag_config") / "settings.yaml",
        help="Path to the GraphRAG settings file (default: %(default)s)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root for GraphRAG (default: current working directory)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose console callbacks",
    )
    return parser.parse_args()


async def _run_pipeline(root: Path, config_path: Path, verbose: bool) -> Sequence[PipelineRunResult]:
    LOGGER.info("Loading GraphRAG config from %s (root=%s)", config_path, root)
    config = load_config(root_dir=root, config_filepath=config_path)
    LOGGER.info(f"DEBUG: Loaded config models: {config.models}")
    callbacks = [ConsoleWorkflowCallbacks(verbose=verbose)] if ConsoleWorkflowCallbacks else []
    LOGGER.info("Starting GraphRAG build_index workflow")
    return await build_index(config=config, callbacks=callbacks, verbose=verbose)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # Set up Azure Auth
    try:
        LOGGER.info("Acquiring Azure OpenAI token...")
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential,
            "https://cognitiveservices.azure.com/.default"
        )
        token = token_provider()
        os.environ["AZURE_OPENAI_API_KEY"] = token
        LOGGER.info("Successfully acquired token and set AZURE_OPENAI_API_KEY")
    except Exception as e:
        LOGGER.warning("Failed to acquire Azure token: %s. Falling back to existing env var.", e)

    args = _parse_args()
    root = args.root.resolve()
    config_path = args.config.resolve()

    try:
        outputs = asyncio.run(_run_pipeline(root=root, config_path=config_path, verbose=args.verbose))
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("GraphRAG ingestion failed: %s", exc)
        raise SystemExit(1) from exc

    had_errors = any(result.errors for result in outputs)
    if had_errors:
        LOGGER.error("One or more workflows reported errors. See logs for details.")
        raise SystemExit(1)

    LOGGER.info("GraphRAG ingestion completed successfully.")


if __name__ == "__main__":
    main()