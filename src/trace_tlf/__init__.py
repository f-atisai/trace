"""Public package surface for TRACE for Python.

The v0.1.0-alpha supported top-level API intentionally exposes only
:class:`Trace`. Domain-model classes and renderer internals remain available
inside their implementation modules for TRACE development, but they are not
part of the alpha compatibility contract.
"""

from .trace import Trace

__all__ = ["Trace"]
