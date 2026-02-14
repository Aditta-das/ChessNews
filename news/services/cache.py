from functools import lru_cache
from .engine import analyze_fen

@lru_cache(maxsize=128)
def cached_analyze_fen(fen):
    """Cache analysis results for identical FENs"""
    return analyze_fen(fen)