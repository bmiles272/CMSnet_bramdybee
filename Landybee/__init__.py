"""Documentation for the landybee package..."""

from ._version import VERSION
from .client import LanDB

__version__ = VERSION

__all__ = ["__version__", "LanDB"]
