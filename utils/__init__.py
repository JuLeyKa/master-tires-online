"""
Utils Package für Ramsperger Reifen System
Enthält alle Helper-Module für die Cloud-Version
"""

from .data_manager import data_manager, DataManager
from .cart_manager import cart_manager, CartManager
from .styles import (
    MAIN_CSS, 
    apply_main_css, 
    get_efficiency_emoji, 
    get_stock_display,
    create_metric_card,
    create_status_badge
)

__all__ = [
    'data_manager',
    'DataManager', 
    'cart_manager',
    'CartManager',
    'MAIN_CSS',
    'apply_main_css',
    'get_efficiency_emoji',
    'get_stock_display', 
    'create_metric_card',
    'create_status_badge'
]

# Version Info
__version__ = "1.0.0"
__author__ = "Master Chief & Claude"
__description__ = "Ramsperger Reifen Management System - Cloud Version"