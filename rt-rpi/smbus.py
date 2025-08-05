"""
smbus compatibility module.

This module provides a compatibility layer for packages that expect the 'smbus' module
but we're using the 'smbus2' drop-in replacement instead. This allows legacy code
to work without modification.

This file should be placed in the project directory so Python finds it first
in the module search path.
"""

# Import the main SMBus class and common constants from smbus2
from smbus2 import SMBus
from smbus2 import i2c_msg

# Re-export the main class for compatibility
__all__ = ['SMBus', 'i2c_msg']

# For compatibility with code that might check the module name
__version__ = '1.0.0-compat'
