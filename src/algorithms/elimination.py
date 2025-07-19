"""
Implementación del algoritmo de Eliminación de Variables.

Basado en el algoritmo ELIMINATION-ASK del libro Russell & Norvig,
Capítulo 13, Figura 13.13.
"""

from typing import Dict, List, Any, Optional
import time
from ..core.bayesian_network import BayesianNetwork
from ..core.factor import Factor, sum_out_var, pointwise_product_list


class VariableEliminationInference:
    """
    Implementa el algoritmo de eliminación de variables para Redes Bayesianas.
    
    Este algoritmo es más eficiente que la enumeración ya que evita
    recálculos mediante el uso de programación dinámica y factores.
    """
    
    def __init__(self, network: BayesianNetwork, verbose: bool = False):
        """
        Inicializa el motor de inferencia por eliminación de variables.
        
        Args:
            network: Red Bayesiana sobre la cual realizar inferencia
            verbose: Si mostrar información detallada del proceso
        """
        self.network = network
        self.verbose = verbose
        self.last_execution_time = 0.0
        self.last_max_factor_size = 0
        self.last_total_factors = 0
        
    def elimination_ask(self, query_var: str, evidence: Dict[str, Any]) -> Dict[Any, float]:
        """
        Calcula la distribución de probabilidad posterior usando eliminación de variables.
        
        Args:
            query_var: Variable de consulta
            evidence: Evidencia observada {variable: valor}
            
        Returns:
            Distribución de probabilidad {valor: probabilidad}
            
        Raises:
            ValueError: Si la variable de consulta no existe
        """
        start_time = time.time()
        
        if query_var not in self.network.nodes:
            raise ValueError(f"Variable de consulta '{query_var}' no existe en la red")
            
        if self.verbose:
            print(f"=== ELIMINATION-ASK ===")
            print(f"Consulta: P({query_var} | {evidence})")
            
        # Paso 1: Crear factores iniciales a partir de las CPTs
        factors = self._create_initial_factors(evidence)
        
        if self.verbose:
            print(f"\nFactores iniciales creados: {len(factors)}")
            for i, factor in enumerate(factors):
                print(f"  Factor {i}: {factor}")
                
        # Paso 2: Determinar orden de eliminación
        variables = self.network.get_variables()
        hidden_vars = [var for var in variables if var != query_var and var not in evidence]
        elimination_order = self._choose_elimination_order(hidden_vars)
        
        if self.verbose:
            print(f"\nVariables a eliminar: {hidden_vars}")
            print(f"Orden de eliminación: {elimination_order}")
            
        # Paso 3: Eliminar variables ocultas una por una
        for var in elimination_order:
            if self.verbose:
                print(f"\nEliminando variable: {var}")
                print(f"Factores antes: {len(factors)}")
                
            factors = sum_out_var(var, factors)
            
            if self.verbose:
                print(f"Factores después: {len(factors)}")
                
            # Actualizar estadísticas
            self.last_total_factors = max(self.last_total_factors, len(factors))
            for factor in factors:
                factor_size = len(factor.values)
                self.last_max_factor_size = max(self.last_max_factor_size, factor_size)
                
        # Paso 4: Multiplicar factores restantes
        if len(factors) > 1:
            if self.verbose:
                print(f"\nMultiplicando {len(factors)} factores restantes...")
            final_factor = pointwise_product_list(factors)
        elif len(factors) == 1:
            final_factor = factors[0]
        else:
            raise ValueError("No quedan factores después de la eliminación")
            
        # Paso 5: Extraer distribución de la variable de consulta
        query_node = self.network.get_node(query_var)
        distribution = {}
        
        # Manejar factor dummy especial
        if '__dummy__' in final_factor.variables:
            # Factor dummy significa que la consulta es independiente de la evidencia
            uniform_prob = 1.0 / len(query_node.domain)
            distribution = {value: uniform_prob for value in query_node.domain}
        else:
            for value in query_node.domain:
                if query_var in final_factor.variables:
                    assignment = {query_var: value}
                    # Añadir valores de evidencia que puedan estar en el factor final
                    for var in final_factor.variables:
                        if var in evidence and var != query_var:
                            assignment[var] = evidence[var]
                            
                    probability = final_factor.get_value(assignment)
                    distribution[value] = probability
                else:
                    # Si la variable de consulta no está en el factor final,
                    # significa que es independiente de la evidencia
                    distribution[value] = 1.0 / len(query_node.domain)
                
        # Paso 6: Normalizar
        total = sum(distribution.values())
        if total > 0:
            for value in distribution:
                distribution[value] /= total
        else:
            # Distribución uniforme si total es 0
            uniform_prob = 1.0 / len(query_node.domain)
            distribution = {value: uniform_prob for value in query_node.domain}
            
        self.last_execution_time = time.time() - start_time
        
        if self.verbose:
            print(f"\n=== RESULTADO ===")
            print(f"Distribución final: {distribution}")
            print(f"Tiempo de ejecución: {self.last_execution_time:.4f}s")
            print(f"Máximo tamaño de factor: {self.last_max_factor_size}")
            print(f"Máximo número de factores: {self.last_total_factors}")
            
        return distribution
        
    def _create_initial_factors(self, evidence: Dict[str, Any]) -> List[Factor]:
        """
        Crea factores iniciales a partir de las CPTs de la red.
        
        Args:
            evidence: Evidencia observada
            
        Returns:
            Lista de factores iniciales
        """
        factors = []
        
        for node_name, node in self.network.nodes.items():
            # Obtener dominios de padres
            parent_domains = {}
            for parent in node.parents:
                parent_node = self.network.get_node(parent)
                parent_domains[parent] = parent_node.domain
                
            # Crear factor a partir de la CPT
            factor = Factor.from_cpt(
                node_name=node_name,
                node_domain=node.domain,
                parents=node.parents,
                parent_domains=parent_domains,
                cpt_entries=node.cpt
            )
            
            # Restringir factor a la evidencia si es necesario
            if evidence:
                factor = factor.restrict(evidence)
                
            factors.append(factor)
            
        return factors
        
    def _choose_elimination_order(self, variables: List[str]) -> List[str]:
        """
        Elige un orden de eliminación para las variables.
        
        Implementa una heurística simple: eliminar variables en orden
        que minimice el producto de los tamaños de dominio de las
        variables conectadas.
        
        Args:
            variables: Variables a eliminar
            
        Returns:
            Lista de variables en orden de eliminación
        """
        # Por simplicidad, usar orden topológico inverso
        # Una heurística más sofisticada consideraría el ancho de árbol
        topological_order = self.network.get_topological_order()
        
        # Filtrar solo las variables que necesitamos eliminar
        elimination_order = [var for var in reversed(topological_order) 
                           if var in variables]
        
        return elimination_order
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de rendimiento de la última ejecución.
        
        Returns:
            Diccionario con estadísticas de rendimiento
        """
        return {
            'execution_time': self.last_execution_time,
            'max_factor_size': self.last_max_factor_size,
            'max_total_factors': self.last_total_factors,
            'algorithm': 'variable_elimination'
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
            
        return self.elimination_ask(query_var, evidence)
        
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
        return f"VariableEliminationInference(red='{self.network.name}')"
        
    def __repr__(self) -> str:
        """Representación para debugging."""
        return f"VariableEliminationInference(network={self.network}, verbose={self.verbose})" 