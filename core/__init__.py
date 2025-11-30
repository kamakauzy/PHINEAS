"""
PHINEAS - Profound HUMINT Intelligence Network & Enrichment Automated System
Core module initialization
"""

__version__ = "1.0.0"
__author__ = "PHINEAS Team"
__description__ = "Comprehensive OSINT automation framework"

from .orchestrator import PhineasOrchestrator
from .config_manager import ConfigManager
from .result_aggregator import ResultAggregator

__all__ = ['PhineasOrchestrator', 'ConfigManager', 'ResultAggregator']
