"""
Mermaid Diagram Validator

This module provides utilities to validate and correct Mermaid diagram syntax.
It uses the actual Mermaid library via Node.js for validation and OpenAI for corrections.
"""

import re
import os
import subprocess
from pathlib import Path
from typing import Tuple, List, Dict, Optional
from openai import OpenAI


class MermaidValidator:
    """Validates and corrects Mermaid diagram syntax."""
    
    def __init__(self, openai_client: Optional[OpenAI] = None):
        """
        Initialize the validator with OpenAI credentials.
        
        Args:
            api_key: OpenAI API key (defaults to AZURE_OPENAI_API_KEY env var)
        """
        if not openai_client:
            api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
            base_url = base_url or os.environ.get("AZURE_OPENAI_ENDPOINT")

            if not api_key:
                raise ValueError("OpenAI API key required (AZURE_OPENAI_API_KEY)")
            self.openai_client = OpenAI(base_url=base_url, api_key=api_key)
        else:
            self.openai_client = openai_client
        
        self.llm_model = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5.1")
        
        # Path to the Node.js validator script
        self.validator_script = Path(__file__).parent / "validate_mermaid.js"
        if not self.validator_script.exists():
            raise FileNotFoundError(f"Mermaid validator script not found: {self.validator_script}")
    
    def extract_mermaid_blocks(self, markdown_text: str) -> List[Tuple[str, str]]:
        """
        Extract Mermaid code blocks from markdown text.
        
        Args:
            markdown_text: Markdown text potentially containing Mermaid blocks
            
        Returns:
            List of tuples (full_block_with_fences, mermaid_code)
        """
        # Pattern to match ```mermaid ... ``` blocks
        pattern = r'(```mermaid\s*\n(.*?)\n```)'
        matches = re.findall(pattern, markdown_text, re.DOTALL | re.IGNORECASE)
        return matches
    
    def validate_mermaid_syntax(self, mermaid_code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Mermaid diagram syntax using the actual Mermaid library via Node.js.
        
        Args:
            mermaid_code: The Mermaid diagram code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            result = subprocess.run(
                ["node", str(self.validator_script)],
                input=mermaid_code,
                text=True,
                capture_output=True,
                timeout=10,  # Increased to 10 seconds for complex diagrams
                encoding='utf-8',  # Explicitly use UTF-8 encoding for Unicode characters
                errors='replace'   # Replace unencodable characters instead of failing
            )
            
            if result.returncode == 0:
                return True, None
            else:
                # Parse error from stderr
                error_msg = result.stderr.strip() or "Unknown Mermaid syntax error"
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            return False, "Mermaid validation timed out"
        except FileNotFoundError:
            return False, "Node.js not found. Please ensure Node.js is installed."
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def correct_mermaid_with_llm(self, mermaid_code: str, error_message: str) -> str:
        """
        Use OpenAI to correct Mermaid syntax errors.
        
        Args:
            mermaid_code: The invalid Mermaid code
            error_message: The error message from Mermaid validation
            
        Returns:
            Corrected Mermaid code
        """
        system_prompt = """You are a Mermaid diagram syntax expert. Your task is to fix syntax errors in Mermaid diagrams.

Common issues to fix:
1. Remove HTML tags like <br/>, <b>, <i> - use plain text or Mermaid formatting instead
2. Quote labels that contain special characters (parentheses, commas, periods, colons, arrows, pipes, etc.)
3. Use valid node IDs (alphanumeric, underscore, hyphen only)
4. Ensure proper Mermaid syntax for the diagram type (graph, flowchart, sequenceDiagram, etc.)
5. Fix arrow syntax and connection formatting
6. Escape or quote special characters properly

CRITICAL: When node labels contain parentheses, commas, periods, or other special characters, you MUST wrap the entire label in double quotes.

Examples:
- WRONG: A[Prime Vendor (Gamma, Horizon, etc.)]
- RIGHT: A["Prime Vendor (Gamma, Horizon, etc.)"]

- WRONG: B[Pre-Existing IP (Sec. 6.3)]
- RIGHT: B["Pre-Existing IP (Sec. 6.3)"]

- WRONG: participant Vendor as Prime Vendor (Gamma, Horizon)
- RIGHT: participant Vendor as "Prime Vendor (Gamma, Horizon)"

Return ONLY the corrected Mermaid code, nothing else. Do not include markdown code fences or explanations."""

        user_prompt = f"""Fix this Mermaid diagram that has the following validation error:

Error: {error_message}

Original Mermaid code:
```
{mermaid_code}
```

Return only the corrected Mermaid code without any explanation, comments, or markdown formatting."""

        try:
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            )
            
            corrected_code = response.choices[0].message.content.strip()
            
            # Remove markdown code fences if LLM added them
            corrected_code = re.sub(r'^```(?:mermaid)?\s*\n?', '', corrected_code)
            corrected_code = re.sub(r'\n?```\s*$', '', corrected_code)
            
            return corrected_code
            
        except Exception as e:
            print(f"Error calling OpenAI for correction: {e}")
            # Return original code if correction fails
            return mermaid_code
    
    def validate_and_correct(self, markdown_text: str, auto_correct: bool = True, max_retries: int = 3) -> Tuple[str, List[Dict]]:
        """
        Validate and optionally correct all Mermaid diagrams in markdown text.
        
        Args:
            markdown_text: Markdown text containing Mermaid blocks
            auto_correct: If True, automatically correct invalid diagrams using OpenAI
            max_retries: Maximum number of correction attempts per diagram (default: 3)
            
        Returns:
            Tuple of (corrected_markdown, validation_results)
            - corrected_markdown: Updated markdown with corrections applied
            - validation_results: List of dicts with validation details for each block
        """
        import concurrent.futures
        
        blocks = self.extract_mermaid_blocks(markdown_text)
        if not blocks:
            return markdown_text, []
        
        # Process all blocks in parallel
        def process_block(block_data):
            full_block, code = block_data
            
            result = {
                "original_code": code,
                "is_valid": False,
                "error": None,
                "corrected_code": None,
                "correction_applied": False,
                "attempts": 0
            }
            
            # Initial validation
            is_valid, error_msg = self.validate_mermaid_syntax(code)
            result["is_valid"] = is_valid
            result["error"] = error_msg
            
            if is_valid or not auto_correct:
                return full_block, result
            
            # Attempt correction with retries
            current_code = code
            current_error = error_msg
            
            for attempt in range(1, max_retries + 1):
                result["attempts"] = attempt
                print(f"Correction attempt {attempt}/{max_retries} for block...")
                print(f"  Error: {current_error[:100]}...")  # Show first 100 chars of error
                
                # Try to correct
                corrected_code = self.correct_mermaid_with_llm(current_code, current_error)
                
                # Validate the correction
                corrected_valid, corrected_error = self.validate_mermaid_syntax(corrected_code)
                
                if corrected_valid:
                    # Success!
                    result["corrected_code"] = corrected_code
                    result["correction_applied"] = True
                    result["is_valid"] = True
                    result["error"] = None
                    print(f"✓ Correction successful on attempt {attempt}")
                    print(f"  Corrected code preview: {corrected_code[:100]}...")
                    # Return original full_block so we can find it for replacement
                    return full_block, result
                else:
                    # Still invalid, prepare for next attempt
                    print(f"✗ Attempt {attempt} failed: {corrected_error[:100]}...")
                    current_code = corrected_code
                    current_error = corrected_error
            
            # All retries exhausted
            result["corrected_code"] = current_code
            result["correction_applied"] = False
            result["error"] = f"Failed after {max_retries} attempts. Last error: {current_error}"
            print(f"✗ All {max_retries} correction attempts failed")
            
            return full_block, result
        
        # Process blocks in parallel (max 5 concurrent)
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(blocks), 5)) as executor:
            processed = list(executor.map(process_block, blocks))
        
        # Apply replacements to markdown
        corrected_text = markdown_text
        results = []

        for full_block, result in processed:
            results.append(result)
            if result["correction_applied"]:
                corrected_block = f"```mermaid\n{result['corrected_code']}\n```"
                # Debug: Check if the block exists in text
                if full_block in corrected_text:
                    corrected_text = corrected_text.replace(full_block, corrected_block, 1)
                    print(f"✓ Replaced block in final text")
                else:
                    print(f"✗ WARNING: Could not find block to replace!")
                    print(f"  Looking for: {full_block[:100]}...")
                    print(f"  In text: {corrected_text[:200]}...")
        
        return corrected_text, results
def validate_mermaid_in_markdown( markdown_text: str, auto_correct: bool = True,openai_client: Optional[OpenAI] = None, max_retries: int = 3) -> Tuple[str, List[Dict]]:
    """
    Convenience function to validate and correct Mermaid diagrams in markdown.
    
    Args:
        markdown_text: Markdown text containing Mermaid blocks
        auto_correct: If True, automatically correct invalid diagrams
        openai_client: Optional OpenAI client instance
        max_retries: Maximum number of correction attempts per diagram (default: 3)
        
    Returns:
        Tuple of (corrected_markdown, validation_results)
    """
    try:
        validator = MermaidValidator(openai_client=openai_client)
        return validator.validate_and_correct(markdown_text, auto_correct=auto_correct, max_retries=max_retries)
    except ValueError as e:
        # If OpenAI API key is not available, return original text
        print(f"Warning: {e}. Skipping Mermaid validation.")
        return markdown_text, []
    except FileNotFoundError as e:
        # If Node.js validator script is missing, return original text
        print(f"Warning: {e}. Skipping Mermaid validation.")
        return markdown_text, []
    except Exception as e:
        print(f"Exception during Mermaid validation: {e}")
        return markdown_text, []

# Test harness
if __name__ == "__main__":
    # Example markdown with problematic Mermaid syntax
    test_markdown = """
Here's a contract relationship diagram:

```mermaid
graph TD
    Contract-202403-200<br/>SOW (Contoso ↔ Zenith)<b> --> Party1[Contoso Corp]
    Contract-202403-200<br/>SOW (Contoso ↔ Zenith)<b> --> Party2[Zenith Inc]
    Party1 -->|Signs| Contract-202403-200<br/>SOW (Contoso ↔ Zenith)<b>
```

This shows the relationships.
"""
    
    print("Original markdown:")
    print(test_markdown)
    print("\n" + "="*80 + "\n")
    
    corrected, results = validate_mermaid_in_markdown(test_markdown, auto_correct=True)
    
    print("Validation results:")
    for i, result in enumerate(results, 1):
        print(f"\nBlock {i}:")
        print(f"  Valid: {result['is_valid']}")
        if result['error']:
            print(f"  Error: {result['error']}")
        if result['correction_applied']:
            print(f"  Correction applied: Yes")
            print(f"  Corrected code:\n{result['corrected_code']}")
    
    print("\n" + "="*80 + "\n")
    print("Corrected markdown:")
    print(corrected)
