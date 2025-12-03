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
        print("=" * 70)
        print("MERMAID CORRECTION REQUEST")
        print("=" * 70)
        print(f"Error message: {error_message}")
        print(f"\nOriginal code ({len(mermaid_code)} chars):")
        print(mermaid_code)
        print("-" * 70)
        
        system_prompt = """You are a Mermaid diagram syntax expert. Your task is to fix syntax errors in Mermaid diagrams.

CRITICAL RULES FOR MERMAID SYNTAX:

1. **Node Labels with Special Characters MUST BE QUOTED:**
   - If a label contains: ( ) , . : | & " or any special character
   - Wrap the ENTIRE label in double quotes
   - Use this format: NodeID["Label text with (special) chars"]
   
2. **MindMap Syntax (starts with `mindmap`):**
   - Root node and child nodes must be on separate lines
   - Indent child nodes with spaces (2 spaces per level)
   - NO quotes around node text in mindmaps
   - Format: 
     ```
     mindmap
       root((Root))
         Child1
           Subchild1
         Child2
     ```

3. **Graph/Flowchart Syntax:**
   - Node format: NodeID[Label] or NodeID["Label with (special) chars"]
   - Connection format: A --> B or A -->|"label text"| B
   - Arrow labels with special chars must be quoted: -->|"text (with) chars"|

4. **Common Errors to Fix:**
   - "Expecting 'SPACELINE', 'NL', 'EOF', got 'NODE_ID'" → Missing quotes around labels with parentheses
   - "Expecting 'AMP', 'COLON', got 'STR'" → Arrow label needs quotes
   - Remove ALL HTML tags (<br/>, <b>, <i>, etc.) - use plain text only

**Examples:**
WRONG: A[Service (data, APIs, hardware)]
RIGHT:  A["Service (data, APIs, hardware)"]

WRONG: A -->|backed by| Service Levels & DR\nCapabilities
RIGHT:  A -->|"backed by"| B["Service Levels & DR Capabilities"]

WRONG: participant User as Prime Vendor (Gamma)
RIGHT:  participant User as "Prime Vendor (Gamma)"

Return ONLY the corrected Mermaid code. No markdown fences, no explanations."""

        user_prompt = f"""Fix this Mermaid diagram that has the following validation error:

Error: {error_message}

Original Mermaid code:
```
{mermaid_code}
```

Return only the corrected Mermaid code without any explanation, comments, or markdown formatting."""

        try:
            print("Calling LLM for Mermaid correction...")
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
            
            print(f"\nCorrected code ({len(corrected_code)} chars):")
            print(corrected_code)
            print("=" * 70)
            
            return corrected_code
            
        except Exception as e:
            print(f"ERROR calling OpenAI for correction: {e}")
            print("=" * 70)
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
