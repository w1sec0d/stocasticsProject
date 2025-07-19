"""
Módulo core - Estructuras de datos fundamentales
"""

from .bayesian_network import BayesianNetwork
from .node import Node, CPTEntry
from .factor import Factor

__all__ = ['BayesianNetwork', 'Node', 'CPTEntry', 'Factor'] 