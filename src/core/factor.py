"""
Implementación de Factores para Eliminación de Variables.

Los factores son tablas multidimensionales que representan funciones
sobre un conjunto de variables. Son fundamentales para el algoritmo
de eliminación de variables.
"""

from typing import Dict, List, Set, Any, Tuple, Iterator
import itertools


class Factor:
    """
    Representa un factor (tabla multidimensional) sobre un conjunto de variables.
    
    Un factor f(X1, X2, ..., Xn) asigna un valor numérico a cada combinación
    posible de valores de las variables X1, X2, ..., Xn.
    """
    
    def __init__(self, variables: List[str], domains: Dict[str, List[Any]]):
        """
        Inicializa un nuevo factor.
        
        Args:
            variables: Lista de nombres de variables en el factor
            domains: Dominios de cada variable {variable: [valores]}
        """
        self.variables = variables.copy()
        self.domains = {var: domains[var].copy() for var in variables}
        
        # Tabla de valores del factor: {(val1, val2, ...): valor}
        self.values: Dict[Tuple[Any, ...], float] = {}
        
        # Inicializar con ceros
        for assignment in self._generate_assignments():
            self.values[assignment] = 0.0
            
    def set_value(self, assignment: Dict[str, Any], value: float) -> None:
        """
        Establece el valor del factor para una asignación específica.
        
        Args:
            assignment: Asignación de valores {variable: valor}
            value: Valor a asignar
        """
        tuple_assignment = self._dict_to_tuple(assignment)
        self.values[tuple_assignment] = value
        
    def get_value(self, assignment: Dict[str, Any]) -> float:
        """
        Obtiene el valor del factor para una asignación específica.
        
        Args:
            assignment: Asignación de valores {variable: valor}
            
        Returns:
            Valor del factor para la asignación
        """
        tuple_assignment = self._dict_to_tuple(assignment)
        return self.values.get(tuple_assignment, 0.0)
        
    def pointwise_product(self, other: 'Factor') -> 'Factor':
        """
        Calcula el producto punto a punto con otro factor.
        
        Args:
            other: Otro factor para multiplicar
            
        Returns:
            Nuevo factor resultado del producto
        """
        # Variables del factor resultado (unión)
        result_vars = list(set(self.variables + other.variables))
        
        # Dominios del factor resultado
        result_domains = {}
        for var in result_vars:
            if var in self.domains:
                result_domains[var] = self.domains[var]
            else:
                result_domains[var] = other.domains[var]
                
        # Crear factor resultado
        result = Factor(result_vars, result_domains)
        
        # Calcular producto para cada asignación
        for assignment in result._generate_assignment_dicts():
            # Extraer valores relevantes para cada factor
            self_assignment = {var: assignment[var] for var in self.variables}
            other_assignment = {var: assignment[var] for var in other.variables}
            
            # Multiplicar valores
            self_value = self.get_value(self_assignment)
            other_value = other.get_value(other_assignment)
            result.set_value(assignment, self_value * other_value)
            
        return result
        
    def sum_out(self, variable: str) -> 'Factor':
        """
        Suma (marginaliza) una variable del factor.
        
        Args:
            variable: Variable a eliminar por suma
            
        Returns:
            Nuevo factor sin la variable especificada
        """
        if variable not in self.variables:
            return self.copy()
            
        # Variables del factor resultado
        result_vars = [var for var in self.variables if var != variable]
        
        if not result_vars:
            # Si no quedan variables, devolver factor constante
            total = sum(self.values.values())
            dummy_factor = Factor(['__dummy__'], {'__dummy__': [True]})
            dummy_factor.set_value({'__dummy__': True}, total)
            return dummy_factor
            
        # Dominios del factor resultado
        result_domains = {var: self.domains[var] for var in result_vars}
        
        # Crear factor resultado
        result = Factor(result_vars, result_domains)
        
        # Sumar sobre la variable eliminada
        for assignment in result._generate_assignment_dicts():
            total = 0.0
            
            for value in self.domains[variable]:
                extended_assignment = assignment.copy()
                extended_assignment[variable] = value
                total += self.get_value(extended_assignment)
                
            result.set_value(assignment, total)
            
        return result
        
    def normalize(self) -> 'Factor':
        """
        Normaliza el factor para que sus valores sumen 1.
        
        Returns:
            Nuevo factor normalizado
        """
        total = sum(self.values.values())
        
        if total == 0:
            return self.copy()
            
        result = self.copy()
        for assignment in result.values:
            result.values[assignment] /= total
            
        return result
        
    def copy(self) -> 'Factor':
        """
        Crea una copia del factor.
        
        Returns:
            Nueva instancia idéntica del factor
        """
        result = Factor(self.variables, self.domains)
        result.values = self.values.copy()
        return result
        
    def restrict(self, evidence: Dict[str, Any]) -> 'Factor':
        """
        Restringe el factor a una evidencia específica.
        
        Args:
            evidence: Evidencia observada {variable: valor}
            
        Returns:
            Nuevo factor restringido a la evidencia
        """
        # Variables que no están en la evidencia
        remaining_vars = [var for var in self.variables if var not in evidence]
        
        if not remaining_vars:
            # Todas las variables están en evidencia
            value = self.get_value(evidence)
            dummy_factor = Factor(['__dummy__'], {'__dummy__': [True]})
            dummy_factor.set_value({'__dummy__': True}, value)
            return dummy_factor
            
        # Crear factor restringido
        result_domains = {var: self.domains[var] for var in remaining_vars}
        result = Factor(remaining_vars, result_domains)
        
        # Copiar valores que coinciden con la evidencia
        for assignment in result._generate_assignment_dicts():
            full_assignment = assignment.copy()
            full_assignment.update(evidence)
            
            if self._is_valid_assignment(full_assignment):
                value = self.get_value(full_assignment)
                result.set_value(assignment, value)
                
        return result
        
    def _generate_assignments(self) -> Iterator[Tuple[Any, ...]]:
        """
        Genera todas las asignaciones posibles como tuplas.
        
        Yields:
            Tuplas con asignaciones de valores
        """
        if not self.variables:
            yield ()
            return
            
        value_lists = [self.domains[var] for var in self.variables]
        for combination in itertools.product(*value_lists):
            yield combination
            
    def _generate_assignment_dicts(self) -> Iterator[Dict[str, Any]]:
        """
        Genera todas las asignaciones posibles como diccionarios.
        
        Yields:
            Diccionarios con asignaciones {variable: valor}
        """
        for assignment_tuple in self._generate_assignments():
            yield dict(zip(self.variables, assignment_tuple))
            
    def _dict_to_tuple(self, assignment: Dict[str, Any]) -> Tuple[Any, ...]:
        """
        Convierte una asignación de diccionario a tupla.
        
        Args:
            assignment: Asignación como diccionario
            
        Returns:
            Asignación como tupla en el orden de self.variables
        """
        return tuple(assignment[var] for var in self.variables)
        
    def _is_valid_assignment(self, assignment: Dict[str, Any]) -> bool:
        """
        Verifica si una asignación es válida para este factor.
        
        Args:
            assignment: Asignación a verificar
            
        Returns:
            True si es válida, False en caso contrario
        """
        for var in self.variables:
            if var not in assignment:
                return False
            if assignment[var] not in self.domains[var]:
                return False
        return True
        
    @classmethod
    def from_cpt(cls, node_name: str, node_domain: List[Any], 
                 parents: List[str], parent_domains: Dict[str, List[Any]],
                 cpt_entries: List) -> 'Factor':
        """
        Crea un factor a partir de una CPT.
        
        Args:
            node_name: Nombre del nodo
            node_domain: Dominio del nodo
            parents: Lista de padres
            parent_domains: Dominios de los padres
            cpt_entries: Entradas de la CPT
            
        Returns:
            Factor correspondiente a la CPT
        """
        variables = parents + [node_name]
        domains = parent_domains.copy()
        domains[node_name] = node_domain
        
        factor = cls(variables, domains)
        
        # Llenar factor con valores de la CPT
        for entry in cpt_entries:
            for node_value, probability in entry.probabilities.items():
                assignment = entry.parent_values.copy()
                assignment[node_name] = node_value
                factor.set_value(assignment, probability)
                
        return factor
        
    def __str__(self) -> str:
        """Representación en cadena del factor."""
        return f"Factor(variables={self.variables}, size={len(self.values)})"
        
    def __repr__(self) -> str:
        """Representación para debugging."""
        return f"Factor(variables={self.variables}, domains={self.domains})"
        
    def print_table(self) -> None:
        """Imprime la tabla del factor de forma legible."""
        print(f"Factor sobre variables: {self.variables}")
        print("-" * 50)
        
        for assignment_dict in self._generate_assignment_dicts():
            assignment_str = ", ".join(f"{var}={val}" for var, val in assignment_dict.items())
            value = self.get_value(assignment_dict)
            print(f"{assignment_str} -> {value:.6f}")


def pointwise_product_list(factors: List[Factor]) -> Factor:
    """
    Calcula el producto punto a punto de una lista de factores.
    
    Args:
        factors: Lista de factores a multiplicar
        
    Returns:
        Factor resultado del producto
    """
    if not factors:
        raise ValueError("Lista de factores vacía")
        
    result = factors[0].copy()
    
    for factor in factors[1:]:
        result = result.pointwise_product(factor)
        
    return result


def sum_out_var(variable: str, factors: List[Factor]) -> List[Factor]:
    """
    Elimina una variable de una lista de factores.
    
    Args:
        variable: Variable a eliminar
        factors: Lista de factores
        
    Returns:
        Nueva lista de factores con la variable eliminada
    """
    # Separar factores que contienen la variable y los que no
    factors_with_var = [f for f in factors if variable in f.variables]
    factors_without_var = [f for f in factors if variable not in f.variables]
    
    if not factors_with_var:
        return factors.copy()
        
    # Multiplicar factores que contienen la variable
    if len(factors_with_var) == 1:
        product = factors_with_var[0]
    else:
        product = pointwise_product_list(factors_with_var)
        
    # Sumar la variable
    marginalized = product.sum_out(variable)
    
    # Retornar nueva lista con el factor marginalizado
    return factors_without_var + [marginalized] 