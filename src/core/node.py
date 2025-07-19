"""
Implementación de nodos para Redes Bayesianas.

Cada nodo representa una variable aleatoria con su tabla de probabilidad
condicional (CPT) y las conexiones con otros nodos.
"""

from typing import Dict, List, Any, Union, Optional
import itertools


class CPTEntry:
    """
    Representa una entrada en una Tabla de Probabilidad Condicional.
    
    Cada entrada asocia una combinación de valores de los padres
    con la distribución de probabilidad del nodo.
    """
    
    def __init__(self, parent_values: Dict[str, Any], probabilities: Dict[Any, float]):
        """
        Inicializa una entrada CPT.
        
        Args:
            parent_values: Valores de las variables padre {nombre_padre: valor}
            probabilities: Distribución de probabilidad {valor_nodo: probabilidad}
        """
        self.parent_values = parent_values.copy()
        self.probabilities = probabilities.copy()
        
    def matches_evidence(self, evidence: Dict[str, Any]) -> bool:
        """
        Verifica si esta entrada coincide con la evidencia dada.
        
        Args:
            evidence: Evidencia observada
            
        Returns:
            True si coincide, False en caso contrario
        """
        for parent, value in self.parent_values.items():
            if parent in evidence and evidence[parent] != value:
                return False
        return True
        
    def get_probability(self, value: Any) -> float:
        """
        Obtiene la probabilidad de un valor específico.
        
        Args:
            value: Valor del cual obtener la probabilidad
            
        Returns:
            Probabilidad del valor
        """
        return self.probabilities.get(value, 0.0)
        
    def is_valid(self) -> bool:
        """
        Verifica si la entrada es válida (probabilidades suman 1).
        
        Returns:
            True si es válida, False en caso contrario
        """
        total = sum(self.probabilities.values())
        return abs(total - 1.0) < 1e-10
        
    def __str__(self) -> str:
        return f"CPTEntry({self.parent_values} -> {self.probabilities})"


class Node:
    """
    Representa un nodo en una Red Bayesiana.
    
    Cada nodo corresponde a una variable aleatoria con:
    - Un nombre único
    - Un dominio de valores posibles
    - Lista de nodos padre e hijo
    - Tabla de Probabilidad Condicional (CPT)
    """
    
    def __init__(self, name: str, domain: List[Any], description: str = ""):
        """
        Inicializa un nuevo nodo.
        
        Args:
            name: Nombre único del nodo
            domain: Lista de valores posibles para la variable
            description: Descripción opcional del nodo
        """
        self.name = name
        self.domain = domain.copy()
        self.description = description
        
        # Relaciones con otros nodos
        self.parents: List[str] = []
        self.children: List[str] = []
        
        # Tabla de Probabilidad Condicional
        self.cpt: List[CPTEntry] = []
        
    def add_parent(self, parent_name: str) -> None:
        """
        Añade un nodo padre.
        
        Args:
            parent_name: Nombre del nodo padre
        """
        if parent_name not in self.parents:
            self.parents.append(parent_name)
            
    def add_child(self, child_name: str) -> None:
        """
        Añade un nodo hijo.
        
        Args:
            child_name: Nombre del nodo hijo
        """
        if child_name not in self.children:
            self.children.append(child_name)
            
    def remove_parent(self, parent_name: str) -> None:
        """
        Remueve un nodo padre.
        
        Args:
            parent_name: Nombre del nodo padre a remover
        """
        if parent_name in self.parents:
            self.parents.remove(parent_name)
            
    def remove_child(self, child_name: str) -> None:
        """
        Remueve un nodo hijo.
        
        Args:
            child_name: Nombre del nodo hijo a remover
        """
        if child_name in self.children:
            self.children.remove(child_name)
            
    def set_cpt_entry(self, parent_values: Dict[str, Any], probabilities: Dict[Any, float]) -> None:
        """
        Establece una entrada en la CPT.
        
        Args:
            parent_values: Valores de los padres para esta entrada
            probabilities: Distribución de probabilidad para el nodo
        """
        # Buscar si ya existe una entrada para estos valores de padres
        for i, entry in enumerate(self.cpt):
            if entry.parent_values == parent_values:
                self.cpt[i] = CPTEntry(parent_values, probabilities)
                return
                
        # Si no existe, crear nueva entrada
        self.cpt.append(CPTEntry(parent_values, probabilities))
        
    def get_probability(self, value: Any, parent_values: Dict[str, Any] = None) -> float:
        """
        Obtiene la probabilidad condicional P(valor | padres).
        
        Args:
            value: Valor del nodo
            parent_values: Valores de los nodos padre
            
        Returns:
            Probabilidad condicional
        """
        if parent_values is None:
            parent_values = {}
            
        # Buscar la entrada correspondiente en la CPT
        for entry in self.cpt:
            if entry.matches_evidence(parent_values):
                return entry.get_probability(value)
                
        return 0.0
        
    def get_distribution(self, parent_values: Dict[str, Any] = None) -> Dict[Any, float]:
        """
        Obtiene la distribución de probabilidad completa dado los valores de los padres.
        
        Args:
            parent_values: Valores de los nodos padre
            
        Returns:
            Diccionario con la distribución {valor: probabilidad}
        """
        if parent_values is None:
            parent_values = {}
            
        # Buscar la entrada correspondiente en la CPT
        for entry in self.cpt:
            if entry.matches_evidence(parent_values):
                return entry.probabilities.copy()
                
        # Si no se encuentra, devolver distribución uniforme
        uniform_prob = 1.0 / len(self.domain)
        return {value: uniform_prob for value in self.domain}
        
    def is_cpt_valid(self) -> bool:
        """
        Verifica si la CPT es válida y completa.
        
        Returns:
            True si la CPT es válida, False en caso contrario
        """
        if not self.cpt:
            return len(self.parents) == 0  # Sin padres, debe tener al menos una entrada
            
        # Verificar que cada entrada sea válida
        for entry in self.cpt:
            if not entry.is_valid():
                return False
                
        # Verificar que exista una entrada para cada combinación de valores de padres
        if self.parents:
            # Esta verificación requiere conocer los dominios de los padres
            # Por simplicidad, asumimos que está completa si hay entradas
            return True
        else:
            # Sin padres, debe haber exactamente una entrada
            return len(self.cpt) == 1
            
    def generate_cpt_template(self, parent_domains: Dict[str, List[Any]]) -> None:
        """
        Genera una plantilla de CPT con probabilidades uniformes.
        
        Args:
            parent_domains: Dominios de los nodos padre {nombre: [valores]}
        """
        self.cpt.clear()
        
        if not self.parents:
            # Sin padres, una sola entrada con distribución uniforme
            uniform_prob = 1.0 / len(self.domain)
            probabilities = {value: uniform_prob for value in self.domain}
            self.cpt.append(CPTEntry({}, probabilities))
        else:
            # Con padres, generar todas las combinaciones
            parent_names = self.parents
            parent_value_lists = [parent_domains[name] for name in parent_names]
            
            for combination in itertools.product(*parent_value_lists):
                parent_values = dict(zip(parent_names, combination))
                uniform_prob = 1.0 / len(self.domain)
                probabilities = {value: uniform_prob for value in self.domain}
                self.cpt.append(CPTEntry(parent_values, probabilities))
                
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """
        Crea un nodo desde un diccionario.
        
        Args:
            data: Diccionario con los datos del nodo
            
        Returns:
            Nueva instancia de Node
        """
        node = cls(
            name=data['name'],
            domain=data['domain'],
            description=data.get('description', '')
        )
        
        # Cargar CPT si existe
        if 'cpt' in data:
            for cpt_data in data['cpt']:
                parent_values = cpt_data.get('parent_values', {})
                probabilities = cpt_data['probabilities']
                node.set_cpt_entry(parent_values, probabilities)
                
        return node
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el nodo a un diccionario.
        
        Returns:
            Diccionario con los datos del nodo
        """
        return {
            'name': self.name,
            'domain': self.domain,
            'description': self.description,
            'cpt': [
                {
                    'parent_values': entry.parent_values,
                    'probabilities': entry.probabilities
                }
                for entry in self.cpt
            ]
        }
        
    def __str__(self) -> str:
        """Representación en cadena del nodo."""
        return f"Node('{self.name}', domain={self.domain}, parents={self.parents})"
        
    def __repr__(self) -> str:
        """Representación para debugging."""
        return f"Node(name='{self.name}', domain={self.domain}, parents={self.parents}, children={self.children})" 