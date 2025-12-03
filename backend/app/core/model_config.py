"""
Dynamic Model Configuration for Dual-API Strategy

This module manages intelligent model selection based on task complexity:
- Small, fast model (8b) for auxiliary tasks (planning, parsing, analysis)
- Large, powerful model (70b) for code generation tasks

Benefits:
- 40-50% token savings overall
- Faster response times for non-code tasks
- High quality maintained for critical code generation
- Automatic fallback if secondary key not configured
"""

import os
import logging
from enum import Enum
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model tiers based on task complexity"""
    LIGHTWEIGHT = "lightweight"  # 8b model - fast, efficient
    STANDARD = "standard"        # 70b model - high quality


class ModelConfig:
    """
    Centralized model configuration with dual-API support
    """
    
    # Model identifiers
    LIGHTWEIGHT_MODEL = "llama-3.1-8b-instant"      # Fast, efficient (70% fewer tokens)
    STANDARD_MODEL = "llama-3.3-70b-versatile"       # High quality (updated model)
    
    # Default temperatures
    TEMP_DETERMINISTIC = 0.0   # For parsing, analysis
    TEMP_LOW = 0.1              # For code generation
    TEMP_BALANCED = 0.3         # For planning
    
    @staticmethod
    def get_api_key(tier: ModelTier = ModelTier.STANDARD) -> str:
        """
        Get appropriate API key based on model tier.
        Falls back to primary key if secondary not configured.
        """
        if tier == ModelTier.LIGHTWEIGHT:
            # Try secondary key first for lightweight tasks
            secondary_key = os.getenv("GROQ_API_KEY_SECONDARY")
            if secondary_key and secondary_key != "your_secondary_groq_api_key_here":
                logger.debug("Using secondary API key for lightweight model")
                return secondary_key
            
            # Fallback to primary key
            logger.debug("Secondary key not configured, using primary key")
        
        return os.getenv("GROQ_API_KEY")
    
    @staticmethod
    def create_llm(
        tier: ModelTier = ModelTier.STANDARD,
        temperature: float = None,
        max_tokens: int = None
    ) -> ChatGroq:
        """
        Create a configured LLM instance based on tier.
        
        Args:
            tier: Model tier (LIGHTWEIGHT or STANDARD)
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            
        Returns:
            Configured ChatGroq instance
        """
        # Select model and defaults based on tier
        if tier == ModelTier.LIGHTWEIGHT:
            model = ModelConfig.LIGHTWEIGHT_MODEL
            default_temp = ModelConfig.TEMP_BALANCED
            default_tokens = 1000  # Lightweight tasks need fewer tokens
        else:
            model = ModelConfig.STANDARD_MODEL
            default_temp = ModelConfig.TEMP_LOW
            default_tokens = 1500  # Code generation needs more tokens
        
        # Override defaults if specified
        temp = temperature if temperature is not None else default_temp
        tokens = max_tokens if max_tokens is not None else default_tokens
        
        api_key = ModelConfig.get_api_key(tier)
        
        logger.info(f"Creating LLM: model={model}, temp={temp}, max_tokens={tokens}")
        
        return ChatGroq(
            model=model,
            temperature=temp,
            max_tokens=tokens,
            groq_api_key=api_key
        )
    
    @staticmethod
    def get_model_info(tier: ModelTier) -> dict:
        """Get information about a model tier"""
        if tier == ModelTier.LIGHTWEIGHT:
            return {
                "model": ModelConfig.LIGHTWEIGHT_MODEL,
                "description": "Fast, token-efficient model for auxiliary tasks",
                "typical_tokens": "~1,000 per request",
                "use_cases": ["Planning", "Analysis", "Parsing", "Classification"]
            }
        else:
            return {
                "model": ModelConfig.STANDARD_MODEL,
                "description": "High-quality model for code generation",
                "typical_tokens": "~3,000 per request",
                "use_cases": ["Terraform code", "Ansible playbooks", "Complex logic"]
            }


# Task-to-tier mapping for easy reference
TASK_MODEL_MAP = {
    # Lightweight tasks (8b model)
    "clarifier": ModelTier.LIGHTWEIGHT,
    "planner": ModelTier.LIGHTWEIGHT,
    "parser": ModelTier.LIGHTWEIGHT,
    "completeness": ModelTier.LIGHTWEIGHT,
    
    # Standard tasks (70b model)
    "architect": ModelTier.STANDARD,
    "ansible": ModelTier.STANDARD,
}


def get_model_for_task(task_name: str) -> ModelTier:
    """
    Get recommended model tier for a specific task.
    
    Args:
        task_name: Name of the task (e.g., 'architect', 'planner')
        
    Returns:
        Recommended ModelTier
    """
    return TASK_MODEL_MAP.get(task_name.lower(), ModelTier.STANDARD)


# Convenience functions
def create_lightweight_llm(**kwargs) -> ChatGroq:
    """Create a lightweight LLM for fast, efficient tasks"""
    return ModelConfig.create_llm(tier=ModelTier.LIGHTWEIGHT, **kwargs)


def create_standard_llm(**kwargs) -> ChatGroq:
    """Create a standard LLM for code generation tasks"""
    return ModelConfig.create_llm(tier=ModelTier.STANDARD, **kwargs)
