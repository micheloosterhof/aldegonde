"""Aldegonde library for cryptography and cryptanalysis."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("aldegonde")
except PackageNotFoundError:
    __version__ = "unknown"
