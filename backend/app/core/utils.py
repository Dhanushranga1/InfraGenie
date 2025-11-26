"""
Core Utility Functions

This module provides shared utility functions used across different agents
to avoid code duplication and maintain consistency.
"""

import logging

logger = logging.getLogger(__name__)


def clean_llm_output(text: str, lang: str = "") -> str:
    """
    Remove markdown fences from LLM-generated code output.
    
    LLMs sometimes wrap code in markdown fences (```language...```) despite
    instructions not to. This function strips those fences while preserving
    the actual code content.
    
    Args:
        text (str): Raw LLM output that may contain markdown fences
        lang (str): Optional language hint (e.g., "hcl", "yaml") for logging
    
    Returns:
        str: Clean code without markdown formatting
    
    Example:
        >>> output = "```hcl\\nprovider \\"aws\\" {...}\\n```"
        >>> clean_llm_output(output, "hcl")
        'provider "aws" {...}'
    
    Behavior:
        - If text starts with ```, removes first line
        - If last line is ```, removes it
        - Returns original text if no fences found
        - Strips leading/trailing whitespace
    """
    text = text.strip()
    
    if not text.startswith("```"):
        return text
    
    logger.debug(f"Cleaning markdown fences from {lang} output")
    
    lines = text.split("\n")
    
    # Remove first line (e.g., ```hcl or just ```)
    lines = lines[1:]
    
    # Remove last line if it's a fence
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    
    cleaned = "\n".join(lines).strip()
    logger.debug(f"Removed markdown fences - {len(text)} → {len(cleaned)} chars")
    
    return cleaned
