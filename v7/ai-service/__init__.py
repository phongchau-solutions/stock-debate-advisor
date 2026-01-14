"""
CrewAI Stock Debate Advisor v6

Multi-agent AI debate system for Vietnamese stock analysis using CrewAI orchestration.

Main Components:
- orchestrator: DebateOrchestrator - Main orchestration engine
- agents: DebateAgents, AnalysisTasks - Agent and task factories
- data_loader: DataLoader, NumberFormatter - Data loading utilities
- config: Config - Configuration management
- constants: System constants and enums

Example Usage:
    from orchestrator import DebateOrchestrator
    
    orchestrator = DebateOrchestrator()
    result = orchestrator.run_debate("MBB", rounds=3)
    print(result['verdict'])
"""

__version__ = "6.0.0"
__author__ = "Stock Debate Advisor Team"
__license__ = "MIT"

from orchestrator import DebateOrchestrator
from config import config
from constants import (
    AgentRole,
    InvestmentAction,
    ConfidenceLevel,
    DebateDecision
)

__all__ = [
    "DebateOrchestrator",
    "config",
    "AgentRole",
    "InvestmentAction",
    "ConfidenceLevel",
    "DebateDecision",
]
