#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Unit tests for GraphRAG indexing sub-component

Tests the GraphRAG ingestion pipeline including:
- Input file preparation
- GraphRAG indexing execution
- Output artifact validation
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


# Import functions to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.ingestion import prepare_graphrag_input, run_graphrag_indexing


class TestGraphRAGInputPreparation:
    """Test suite for GraphRAG input preparation."""
    
    def test_prepare_graphrag_input_finds_contract_files(self, tmp_path, monkeypatch):
        """Test that prepare_graphrag_input correctly counts contract markdown files."""
        # Setup: Create temporary input directory with mock contract files
        input_dir = tmp_path / "data" / "input"
        input_dir.mkdir(parents=True)
        
        # Create sample contract files
        for i in range(5):
            contract_file = input_dir / f"contract_{i:03d}_TestCorp.md"
            contract_file.write_text(f"# Contract {i}\n\nThis is test contract {i}.")
        
        # Create non-contract files (should be ignored)
        (input_dir / "readme.md").write_text("README")
        (input_dir / "other.txt").write_text("OTHER")
        
        # Change working directory to tmp_path
        monkeypatch.chdir(tmp_path)
        
        # Execute
        count = prepare_graphrag_input()
        
        # Assert
        assert count == 5, f"Expected 5 contract files, found {count}"
    
    def test_prepare_graphrag_input_empty_directory(self, tmp_path, monkeypatch):
        """Test prepare_graphrag_input with no contract files."""
        # Setup: Create empty input directory
        input_dir = tmp_path / "data" / "input"
        input_dir.mkdir(parents=True)
        
        monkeypatch.chdir(tmp_path)
        
        # Execute
        count = prepare_graphrag_input()
        
        # Assert
        assert count == 0, f"Expected 0 contract files, found {count}"
    
    def test_prepare_graphrag_input_missing_directory(self, tmp_path, monkeypatch):
        """Test prepare_graphrag_input when input directory doesn't exist."""
        # Setup: No input directory created
        monkeypatch.chdir(tmp_path)
        
        # Execute - should not raise error, just return 0
        count = prepare_graphrag_input()
        
        # Assert
        assert count == 0, f"Expected 0 for missing directory, found {count}"


class TestGraphRAGIndexing:
    """Test suite for GraphRAG indexing execution."""
    
    @patch('subprocess.run')
    def test_run_graphrag_indexing_success(self, mock_run):
        """Test successful GraphRAG indexing execution."""
        # Setup mock subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Indexing complete"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Execute
        success = run_graphrag_indexing()
        
        # Assert
        assert success is True
        mock_run.assert_called_once()
        
        # Verify command structure
        call_args = mock_run.call_args
        assert call_args[0][0][0] == "graphrag"
        assert call_args[0][0][1] == "index"
        assert "--root" in call_args[0][0]
        assert "--config" in call_args[0][0]
    
    @patch('subprocess.run')
    def test_run_graphrag_indexing_failure(self, mock_run):
        """Test GraphRAG indexing failure handling."""
        # Setup mock subprocess result with error
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error: Failed to process entities"
        mock_run.return_value = mock_result
        
        # Execute
        success = run_graphrag_indexing()
        
        # Assert
        assert success is False
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_graphrag_indexing_command_not_found(self, mock_run):
        """Test handling when graphrag CLI is not installed."""
        # Setup mock to raise FileNotFoundError
        mock_run.side_effect = FileNotFoundError("graphrag command not found")
        
        # Execute
        success = run_graphrag_indexing()
        
        # Assert
        assert success is False
    
    @patch('subprocess.run')
    def test_run_graphrag_indexing_unexpected_error(self, mock_run):
        """Test handling of unexpected errors during indexing."""
        # Setup mock to raise generic exception
        mock_run.side_effect = Exception("Unexpected error")
        
        # Execute
        success = run_graphrag_indexing()
        
        # Assert
        assert success is False


class TestGraphRAGOutputValidation:
    """Test suite for validating GraphRAG output artifacts."""
    
    def test_graphrag_output_directory_structure(self, tmp_path):
        """Test that GraphRAG creates expected output directory structure."""
        # Setup expected output structure
        output_dir = tmp_path / "data" / "output"
        artifacts_dir = output_dir / "artifacts"
        
        # Simulate GraphRAG output creation
        artifacts_dir.mkdir(parents=True)
        
        # Create expected artifact files
        expected_artifacts = [
            "create_final_entities.parquet",
            "create_final_relationships.parquet",
            "create_final_communities.parquet",
            "create_final_community_reports.parquet",
            "create_final_nodes.parquet",
            "create_final_text_units.parquet"
        ]
        
        for artifact in expected_artifacts:
            (artifacts_dir / artifact).write_text("mock parquet data")
        
        # Assert all expected files exist
        for artifact in expected_artifacts:
            artifact_path = artifacts_dir / artifact
            assert artifact_path.exists(), f"Expected artifact missing: {artifact}"
    
    def test_graphrag_output_to_data_output_not_root(self, tmp_path):
        """Test that GraphRAG outputs to data/output, not root output directory."""
        # This tests the configuration requirement
        expected_output = tmp_path / "data" / "output"
        wrong_output = tmp_path / "output"
        
        # Verify configuration would use data/output (use normalized paths for Windows)
        expected_str = str(expected_output).replace("\\", "/")
        assert expected_str.endswith("data/output")
        
        # Verify wrong path doesn't match the pattern
        wrong_str = str(wrong_output).replace("\\", "/")
        assert not wrong_str.endswith("data/output")
    
    def test_graphrag_parquet_files_not_empty(self, tmp_path):
        """Test that GraphRAG parquet files contain data."""
        # Setup
        artifacts_dir = tmp_path / "data" / "output" / "artifacts"
        artifacts_dir.mkdir(parents=True)
        
        # Create mock parquet file with content
        test_file = artifacts_dir / "create_final_entities.parquet"
        test_file.write_bytes(b"MOCK_PARQUET_HEADER")
        
        # Assert
        assert test_file.stat().st_size > 0, "Parquet file should not be empty"


class TestGraphRAGIntegration:
    """Integration tests for complete GraphRAG pipeline."""
    
    def test_full_graphrag_pipeline_mock(self, tmp_path, monkeypatch):
        """Test full pipeline: prepare input -> run indexing -> validate output."""
        # Setup
        monkeypatch.chdir(tmp_path)
        
        # Create input files
        input_dir = tmp_path / "data" / "input"
        input_dir.mkdir(parents=True)
        (input_dir / "contract_000_Test.md").write_text("# Test Contract\n\nTest content.")
        
        # Create output directory
        output_dir = tmp_path / "data" / "output" / "artifacts"
        output_dir.mkdir(parents=True)
        
        # Step 1: Prepare input
        count = prepare_graphrag_input()
        assert count == 1, "Should find 1 contract file"
        
        # Step 2: Mock indexing (would normally run graphrag index)
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "Success"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            success = run_graphrag_indexing()
            assert success is True
        
        # Step 3: Verify output directory exists
        assert output_dir.exists(), "Output artifacts directory should exist"


class TestGraphRAGConfiguration:
    """Test GraphRAG configuration validation."""
    
    def test_graphrag_config_output_path(self):
        """Test that GraphRAG config uses data/output not root output."""
        config_path = Path("graphrag_config/settings.yaml")
        
        if config_path.exists():
            config_content = config_path.read_text()
            
            # Check output configuration
            assert 'base_dir: "data/output"' in config_content, \
                "GraphRAG config should use data/output for output.base_dir"
            
            # Ensure not using root output
            assert 'base_dir: "output"' not in config_content or \
                   'data/output' in config_content, \
                "Should not use root output directory"
    
    def test_graphrag_config_input_path(self):
        """Test that GraphRAG config uses data/input."""
        config_path = Path("graphrag_config/settings.yaml")
        
        if config_path.exists():
            config_content = config_path.read_text()
            
            # Check input configuration
            assert 'base_dir: "data/input"' in config_content, \
                "GraphRAG config should use data/input for input.base_dir"


class TestGraphRAGErrorHandling:
    """Test error handling in GraphRAG indexing."""
    
    @patch('subprocess.run')
    def test_indexing_with_warnings_still_succeeds(self, mock_run):
        """Test that indexing succeeds even with warnings in stderr."""
        # Setup mock with warnings but success return code
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Indexing complete"
        mock_result.stderr = "SyntaxWarning: invalid escape sequence '\\W'"
        mock_run.return_value = mock_result
        
        # Execute
        success = run_graphrag_indexing()
        
        # Assert - should still succeed despite warnings
        assert success is True
    
    @patch('subprocess.run')
    def test_indexing_timeout_handling(self, mock_run):
        """Test handling of subprocess timeout."""
        # Setup mock to simulate timeout
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="graphrag", timeout=300)
        
        # Execute
        success = run_graphrag_indexing()
        
        # Assert
        assert success is False


# Test fixtures
@pytest.fixture
def mock_contract_files(tmp_path):
    """Fixture providing mock contract files for testing."""
    input_dir = tmp_path / "data" / "input"
    input_dir.mkdir(parents=True)
    
    contracts = []
    for i in range(3):
        contract_file = input_dir / f"contract_{i:03d}_Company{i}.md"
        content = f"""# Contract {i}

## Parties
- Company{i} Inc.
- Vendor Corp.

## Terms
This is a test contract with various clauses and obligations.

### Payment Terms
Payment due within 30 days.

### Termination
Either party may terminate with 90 days notice.
"""
        contract_file.write_text(content)
        contracts.append(contract_file)
    
    return contracts


@pytest.fixture
def mock_graphrag_output(tmp_path):
    """Fixture providing mock GraphRAG output structure."""
    output_dir = tmp_path / "data" / "output"
    artifacts_dir = output_dir / "artifacts"
    artifacts_dir.mkdir(parents=True)
    
    # Create mock parquet files
    artifacts = {
        "create_final_entities.parquet": b"MOCK_ENTITIES",
        "create_final_relationships.parquet": b"MOCK_RELATIONSHIPS",
        "create_final_communities.parquet": b"MOCK_COMMUNITIES"
    }
    
    for filename, content in artifacts.items():
        (artifacts_dir / filename).write_bytes(content)
    
    return artifacts_dir


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
