# ABOUTME: Build script with mypyc compilation for performance-critical modules
# ABOUTME: Compiles typed Python to C extensions for faster execution

from setuptools import setup

# Only use mypyc if it's available and we're not just doing an editable install
try:
    from mypyc.build import mypycify

    # Modules to compile with mypyc (performance-critical code)
    MYPYC_MODULES = [
        "src/aldegonde/stats/ioc.py",
        "src/aldegonde/stats/kappa.py",
        "src/aldegonde/stats/ngrams.py",
        "src/aldegonde/stats/entropy.py",
        "src/aldegonde/stats/repeats.py",
        "src/aldegonde/masc.py",
        "src/aldegonde/pasc.py",
        "src/aldegonde/auto.py",
        "src/aldegonde/c3301.py",
    ]

    ext_modules = mypycify(MYPYC_MODULES, opt_level="3")
except ImportError:
    ext_modules = []

setup(ext_modules=ext_modules)
