"""
Red Team Lab - Adaptive LLM Security Testing Framework
"""

from .config import ATTACKER_MODEL, TARGET_MODEL, MAX_ITERATIONS
from .mutation_engine import MutationEngine, MutationStrategy, MutationResult
from .attack_orchestrator import AttackOrchestrator, AttackResult, CampaignResult
from .advanced_pair import AdvancedPAIR, TreeOfAttacks, JudgeVerdict

__version__ = "1.0.0"
__all__ = [
    "MutationEngine",
    "MutationStrategy", 
    "MutationResult",
    "AttackOrchestrator",
    "AttackResult",
    "CampaignResult",
    "AdvancedPAIR",
    "TreeOfAttacks",
    "JudgeVerdict",
    "ATTACKER_MODEL",
    "TARGET_MODEL",
    "MAX_ITERATIONS"
]

