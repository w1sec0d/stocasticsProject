"""
Módulo algorithms - Algoritmos de inferencia en Redes Bayesianas
"""

from .enumeration import EnumerationInference
from .elimination import VariableEliminationInference

__all__ = ['EnumerationInference', 'VariableEliminationInference'] 