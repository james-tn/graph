"""
Mermaid Diagram Corrector

Simplified correction service for Mermaid diagrams.
Relies on frontend for validation, backend only does LLM-based correction.
"""

import os
import re
from typing import Optional
from openai import OpenAI


class MermaidCorrector:
    """Corrects Mermaid diagram syntax using LLM."""
    
    def __init__(self, openai_client: Optional[OpenAI] = None):
        """
        Initialize the corrector with OpenAI client.
        
        Args:
            openai_client: Optional OpenAI client instance
        """
        if not openai_client:
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")
            base_url = os.environ.get("AZURE_OPENAI_ENDPOINT")

            if not api_key:
                raise ValueError("OpenAI API key required (AZURE_OPENAI_API_KEY)")
            self.openai_client = OpenAI(base_url=base_url, api_key=api_key)
        else:
            self.openai_client = openai_client
        
        self.llm_model = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5.1")
    
    def correct_mermaid(self, mermaid_code: str, error_message: str) -> str:
        """
        Use LLM to correct Mermaid syntax errors.
        
        Args:
            mermaid_code: The invalid Mermaid code
            error_message: The error message from frontend Mermaid rendering
            
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


# Convenience function
def correct_mermaid_diagram(
    mermaid_code: str,
    error_message: str,
    openai_client: Optional[OpenAI] = None
) -> str:
    """
    Convenience function to correct a Mermaid diagram.
    
    Args:
        mermaid_code: The invalid Mermaid code
        error_message: Error message from frontend validation
        openai_client: Optional OpenAI client instance
        
    Returns:
        Corrected Mermaid code
    """
    try:
        corrector = MermaidCorrector(openai_client=openai_client)
        return corrector.correct_mermaid(mermaid_code, error_message)
    except ValueError as e:
        print(f"Warning: {e}. Cannot correct Mermaid diagram.")
        return mermaid_code
    except Exception as e:
        print(f"Exception during Mermaid correction: {e}")
        return mermaid_code
