"""
Implementación del algoritmo de Inferencia por Enumeración.

Basado en el algoritmo ENUMERATION-ASK del libro Russell & Norvig,
Capítulo 13, Figura 13.11.
"""

from typing import Dict, List, Any, Optional
import time
from ..core.bayesian_network import BayesianNetwork


class EnumerationInference:
    """
    Implementa el algoritmo de inferencia por enumeración para Redes Bayesianas.
    
    Este algoritmo calcula probabilidades posteriores mediante enumeración
    completa del espacio de estados, siguiendo la fórmula:
    P(X | e) = α * Σ_y P(X, e, y)
    """
    
    def __init__(self, network: BayesianNetwork, verbose: bool = False):
        """
        Inicializa el motor de inferencia por enumeración.
        
        Args:
            network: Red Bayesiana sobre la cual realizar inferencia
            verbose: Si mostrar información detallada del proceso
        """
        self.network = network
        self.verbose = verbose
        self.last_execution_time = 0.0
        self.last_operations_count = 0
        
    def enumeration_ask(self, query_var: str, evidence: Dict[str, Any]) -> Dict[Any, float]:
        """
        Calcula la distribución de probabilidad posterior para una variable.
        
        Args:
            query_var: Variable de consulta
            evidence: Evidencia observada {variable: valor}
            
        Returns:
            Distribución de probabilidad {valor: probabilidad}
            
        Raises:
            ValueError: Si la variable de consulta no existe
        """
        start_time = time.time()
        self.last_operations_count = 0
        
        if query_var not in self.network.nodes:
            raise ValueError(f"Variable de consulta '{query_var}' no existe en la red")
            
        if self.verbose:
            print(f"=== ENUMERATION-ASK ===")
            print(f"Consulta: P({query_var} | {evidence})")
            
        # Obtener dominio de la variable de consulta
        query_node = self.network.get_node(query_var)
        query_domain = query_node.domain
        
        # Inicializar distribución resultado
        result_distribution = {}
        
        # Para cada valor posible de la variable de consulta
        for query_value in query_domain:
            if self.verbose:
                print(f"\nCalculando P({query_var}={query_value} | evidencia)...")
                
            # Extender evidencia con valor de consulta
            extended_evidence = evidence.copy()
            extended_evidence[query_var] = query_value
            
            # Llamar a ENUMERATE-ALL
            variables = self.network.get_variables()
            probability = self._enumerate_all(variables, extended_evidence)
            result_distribution[query_value] = probability
            
            if self.verbose:
                print(f"Probabilidad no normalizada: {probability}")
                
        # Normalizar distribución
        total = sum(result_distribution.values())
        if total > 0:
            for value in result_distribution:
                result_distribution[value] /= total
        else:
            # Distribución uniforme si total es 0
            uniform_prob = 1.0 / len(query_domain)
            result_distribution = {value: uniform_prob for value in query_domain}
            
        self.last_execution_time = time.time() - start_time
        
        if self.verbose:
            print(f"\n=== RESULTADO ===")
            print(f"Distribución normalizada: {result_distribution}")
            print(f"Tiempo de ejecución: {self.last_execution_time:.4f}s")
            print(f"Operaciones realizadas: {self.last_operations_count}")
            
        return result_distribution
        
    def _enumerate_all(self, variables: List[str], evidence: Dict[str, Any]) -> float:
        """
        Función auxiliar recursiva que implementa ENUMERATE-ALL.
        
        Args:
            variables: Lista de variables restantes por procesar
            evidence: Evidencia actual (puede incluir asignaciones de variables ocultas)
            
        Returns:
            Probabilidad no normalizada
        """
        self.last_operations_count += 1
        
        # Caso base: si no quedan variables, devolver 1.0
        if not variables:
            return 1.0
            
        # Tomar la primera variable
        current_var = variables[0]
        remaining_vars = variables[1:]
        
        if self.verbose and len(variables) <= 3:  # Solo mostrar detalles para pocas variables
            print(f"  Procesando variable: {current_var}")
            
        if current_var in evidence:
            # Variable con evidencia: usar valor observado
            current_value = evidence[current_var]
            
            # Obtener probabilidad condicional P(valor | padres)
            node = self.network.get_node(current_var)
            parent_values = {parent: evidence[parent] for parent in node.parents 
                           if parent in evidence}
            
            conditional_prob = node.get_probability(current_value, parent_values)
            
            # Llamada recursiva con variables restantes
            recursive_result = self._enumerate_all(remaining_vars, evidence)
            
            result = conditional_prob * recursive_result
            
            if self.verbose and len(variables) <= 3:
                print(f"    Evidencia: {current_var}={current_value}")
                print(f"    P({current_value}|{parent_values}) = {conditional_prob}")
                print(f"    Resultado recursivo = {recursive_result}")
                print(f"    Producto = {result}")
                
            return result
            
        else:
            # Variable oculta: sumar sobre todos sus valores posibles
            node = self.network.get_node(current_var)
            total = 0.0
            
            if self.verbose and len(variables) <= 3:
                print(f"    Variable oculta: {current_var}, sumando sobre {node.domain}")
                
            for value in node.domain:
                # Extender evidencia con este valor
                extended_evidence = evidence.copy()
                extended_evidence[current_var] = value
                
                # Obtener probabilidad condicional
                parent_values = {parent: extended_evidence[parent] for parent in node.parents 
                               if parent in extended_evidence}
                
                conditional_prob = node.get_probability(value, parent_values)
                
                # Llamada recursiva
                recursive_result = self._enumerate_all(remaining_vars, extended_evidence)
                
                partial_result = conditional_prob * recursive_result
                total += partial_result
                
                if self.verbose and len(variables) <= 3:
                    print(f"      {current_var}={value}: P({value}|{parent_values}) = {conditional_prob}")
                    print(f"      Recursivo = {recursive_result}, Parcial = {partial_result}")
                    
            if self.verbose and len(variables) <= 3:
                print(f"    Total para {current_var} = {total}")
                
            return total
            
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de rendimiento de la última ejecución.
        
        Returns:
            Diccionario con estadísticas de rendimiento
        """
        return {
            'execution_time': self.last_execution_time,
            'operations_count': self.last_operations_count,
            'algorithm': 'enumeration'
        }
        
    def query(self, query_var: str, evidence: Dict[str, Any] = None) -> Dict[Any, float]:
        """
        Método de conveniencia para realizar consultas.
        
        Args:
            query_var: Variable de consulta
            evidence: Evidencia observada (opcional)
            
        Returns:
            Distribución de probabilidad posterior
        """
        if evidence is None:
            evidence = {}
            
        return self.enumeration_ask(query_var, evidence)
        
    def marginal_probability(self, variable: str, value: Any, evidence: Dict[str, Any] = None) -> float:
        """
        Calcula la probabilidad marginal de un valor específico.
        
        Args:
            variable: Variable de interés
            value: Valor específico
            evidence: Evidencia observada (opcional)
            
        Returns:
            Probabilidad marginal P(variable=value | evidence)
        """
        if evidence is None:
            evidence = {}
            
        distribution = self.query(variable, evidence)
        return distribution.get(value, 0.0)
        
    def most_probable_value(self, variable: str, evidence: Dict[str, Any] = None) -> Any:
        """
        Encuentra el valor más probable de una variable dada la evidencia.
        
        Args:
            variable: Variable de interés
            evidence: Evidencia observada (opcional)
            
        Returns:
            Valor con mayor probabilidad posterior
        """
        if evidence is None:
            evidence = {}
            
        distribution = self.query(variable, evidence)
        return max(distribution.keys(), key=lambda v: distribution[v])
        
    def __str__(self) -> str:
        """Representación en cadena del objeto."""
        return f"EnumerationInference(red='{self.network.name}')"
        
    def __repr__(self) -> str:
        """Representación para debugging."""
        return f"EnumerationInference(network={self.network}, verbose={self.verbose})" 