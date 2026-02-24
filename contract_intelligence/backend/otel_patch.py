"""
Patch for agent-framework rc1 + opentelemetry-semantic-conventions-ai >= 0.4.13

agent-framework rc1 references several SpanAttributes that were removed/renamed
in opentelemetry-semantic-conventions-ai 0.4.13+.

This file monkey-patches the missing attributes so agent-framework can load.
Import this before importing agent_framework.
"""


def patch_otel_semconv_ai():
    """Add missing attributes to SpanAttributes for agent-framework rc1 compat."""
    try:
        from opentelemetry.semconv_ai import SpanAttributes

        # Map of missing attribute name -> fallback value
        # These are gen_ai semantic convention attribute keys
        missing_attrs = {
            "LLM_SYSTEM": "gen_ai.system",
            "LLM_REQUEST_MODEL": "gen_ai.request.model",
            "LLM_REQUEST_MAX_TOKENS": "gen_ai.request.max_tokens",
            "LLM_REQUEST_TEMPERATURE": "gen_ai.request.temperature",
            "LLM_REQUEST_TOP_P": "gen_ai.request.top_p",
            "LLM_RESPONSE_MODEL": "gen_ai.response.model",
            "LLM_USAGE_COMPLETION_TOKENS": "gen_ai.usage.output_tokens",
            "LLM_USAGE_PROMPT_TOKENS": "gen_ai.usage.input_tokens",
            "LLM_PROMPTS": "gen_ai.prompt",
            "LLM_COMPLETIONS": "gen_ai.completion",
            "LLM_TOKEN_TYPE": "gen_ai.token.type",
        }

        for attr_name, default_value in missing_attrs.items():
            if not hasattr(SpanAttributes, attr_name):
                setattr(SpanAttributes, attr_name, default_value)

    except ImportError:
        pass


# Auto-patch on import
patch_otel_semconv_ai()
