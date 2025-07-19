"""
Implementación de la estructura de datos para Redes Bayesianas.

Esta clase representa una Red Bayesiana completa con nodos, aristas dirigidas
y tablas de probabilidad condicional (CPTs).
"""

from typing import Dict, List, Set, Optional, Any
import json
from .node import Node


class BayesianNetwork:
    """
    Representa una Red Bayesiana con nodos y sus relaciones probabilísticas.
    
    Una Red Bayesiana es un grafo dirigido acíclico (DAG) donde:
    - Cada nodo representa una variable aleatoria
    - Las aristas representan dependencias probabilísticas
    - Cada nodo tiene una CPT (Conditional Probability Table)
    """
    
    def __init__(self, name: str = "Red Bayesiana"):
        """
        Inicializa una nueva Red Bayesiana vacía.
        
        Args:
            name: Nombre descriptivo de la red
        """
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self._topological_order: Optional[List[str]] = None
        
    def add_node(self, node: Node) -> None:
        """
        Añade un nodo a la red.
        
        Args:
            node: Nodo a añadir
            
        Raises:
            ValueError: Si ya existe un nodo con ese nombre
        """
        if node.name in self.nodes:
            raise ValueError(f"Ya existe un nodo con nombre '{node.name}'")
            
        self.nodes[node.name] = node
        # Invalidar orden topológico ya que cambió la estructura
        self._topological_order = None
        
    def add_edge(self, parent_name: str, child_name: str) -> None:
        """
        Añade una arista dirigida entre dos nodos.
        
        Args:
            parent_name: Nombre del nodo padre
            child_name: Nombre del nodo hijo
            
        Raises:
            ValueError: Si algún nodo no existe o se crearía un ciclo
        """
        if parent_name not in self.nodes:
            raise ValueError(f"Nodo padre '{parent_name}' no existe")
        if child_name not in self.nodes:
            raise ValueError(f"Nodo hijo '{child_name}' no existe")
            
        parent_node = self.nodes[parent_name]
        child_node = self.nodes[child_name]
        
        # Verificar que no se cree un ciclo
        if self._would_create_cycle(parent_name, child_name):
            raise ValueError(f"La arista {parent_name} -> {child_name} crearía un ciclo")
            
        # Añadir relación bidireccional
        parent_node.add_child(child_name)
        child_node.add_parent(parent_name)
        
        # Invalidar orden topológico
        self._topological_order = None
        
    def get_node(self, name: str) -> Node:
        """
        Obtiene un nodo por su nombre.
        
        Args:
            name: Nombre del nodo
            
        Returns:
            El nodo correspondiente
            
        Raises:
            KeyError: Si el nodo no existe
        """
        if name not in self.nodes:
            raise KeyError(f"Nodo '{name}' no existe en la red")
        return self.nodes[name]
        
    def get_variables(self) -> List[str]:
        """
        Obtiene la lista de todas las variables en la red.
        
        Returns:
            Lista con los nombres de todas las variables
        """
        return list(self.nodes.keys())
        
    def get_topological_order(self) -> List[str]:
        """
        Obtiene un ordenamiento topológico de los nodos.
        
        Returns:
            Lista de nombres de nodos en orden topológico
        """
        if self._topological_order is None:
            self._topological_order = self._compute_topological_order()
        return self._topological_order.copy()
        
    def get_parents(self, node_name: str) -> List[str]:
        """
        Obtiene los padres de un nodo.
        
        Args:
            node_name: Nombre del nodo
            
        Returns:
            Lista de nombres de los nodos padre
        """
        return self.get_node(node_name).parents.copy()
        
    def get_children(self, node_name: str) -> List[str]:
        """
        Obtiene los hijos de un nodo.
        
        Args:
            node_name: Nombre del nodo
            
        Returns:
            Lista de nombres de los nodos hijo
        """
        return self.get_node(node_name).children.copy()
        
    def get_markov_blanket(self, node_name: str) -> Set[str]:
        """
        Obtiene la manta de Markov de un nodo.
        
        La manta de Markov incluye:
        - Los padres del nodo
        - Los hijos del nodo  
        - Los otros padres de los hijos (co-padres)
        
        Args:
            node_name: Nombre del nodo
            
        Returns:
            Conjunto con los nombres de los nodos en la manta de Markov
        """
        node = self.get_node(node_name)
        markov_blanket = set()
        
        # Añadir padres
        markov_blanket.update(node.parents)
        
        # Añadir hijos y sus otros padres
        for child_name in node.children:
            markov_blanket.add(child_name)
            child = self.get_node(child_name)
            for co_parent in child.parents:
                if co_parent != node_name:
                    markov_blanket.add(co_parent)
                    
        return markov_blanket
        
    def is_valid(self) -> bool:
        """
        Verifica si la red es válida (es un DAG y las CPTs son consistentes).
        
        Returns:
            True si la red es válida, False en caso contrario
        """
        try:
            # Verificar que sea un DAG
            self.get_topological_order()
            
            # Verificar que todas las CPTs sean válidas
            for node in self.nodes.values():
                if not node.is_cpt_valid():
                    return False
                    
            return True
        except:
            return False
            
    def _would_create_cycle(self, parent_name: str, child_name: str) -> bool:
        """
        Verifica si añadir una arista crearía un ciclo.
        
        Args:
            parent_name: Nombre del nodo padre
            child_name: Nombre del nodo hijo
            
        Returns:
            True si se crearía un ciclo, False en caso contrario
        """
        # Si ya hay un camino de child a parent, añadir parent->child crearía un ciclo
        return self._has_path(child_name, parent_name)
        
    def _has_path(self, start: str, end: str) -> bool:
        """
        Verifica si existe un camino dirigido de start a end.
        
        Args:
            start: Nodo de inicio
            end: Nodo destino
            
        Returns:
            True si existe un camino, False en caso contrario
        """
        if start == end:
            return True
            
        visited = set()
        stack = [start]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
                
            visited.add(current)
            
            if current == end:
                return True
                
            if current in self.nodes:
                stack.extend(self.nodes[current].children)
                
        return False
        
    def _compute_topological_order(self) -> List[str]:
        """
        Calcula un ordenamiento topológico usando el algoritmo de Kahn.
        
        Returns:
            Lista de nodos en orden topológico
            
        Raises:
            ValueError: Si la red contiene ciclos
        """
        # Calcular grado de entrada de cada nodo
        in_degree = {name: len(node.parents) for name, node in self.nodes.items()}
        
        # Cola con nodos sin padres
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Tomar un nodo sin padres
            current = queue.pop(0)
            result.append(current)
            
            # Reducir grado de entrada de sus hijos
            for child_name in self.nodes[current].children:
                in_degree[child_name] -= 1
                if in_degree[child_name] == 0:
                    queue.append(child_name)
                    
        # Verificar que se procesaron todos los nodos (no hay ciclos)
        if len(result) != len(self.nodes):
            raise ValueError("La red contiene ciclos - no es un DAG válido")
            
        return result
        
    @classmethod
    def from_json(cls, json_file: str) -> 'BayesianNetwork':
        """
        Carga una Red Bayesiana desde un archivo JSON.
        
        Args:
            json_file: Ruta al archivo JSON
            
        Returns:
            Nueva instancia de BayesianNetwork
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        network = cls(data.get('name', 'Red Cargada'))
        
        # Crear nodos
        for node_data in data['nodes']:
            node = Node.from_dict(node_data)
            network.add_node(node)
            
        # Crear aristas
        for edge in data.get('edges', []):
            network.add_edge(edge['parent'], edge['child'])
            
        return network
        
    def to_json(self, json_file: str) -> None:
        """
        Guarda la red en formato JSON.
        
        Args:
            json_file: Ruta donde guardar el archivo
        """
        data = {
            'name': self.name,
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'edges': []
        }
        
        # Añadir aristas
        for node_name, node in self.nodes.items():
            for child_name in node.children:
                data['edges'].append({
                    'parent': node_name,
                    'child': child_name
                })
                
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def __str__(self) -> str:
        """Representación en cadena de la red."""
        return f"BayesianNetwork('{self.name}', {len(self.nodes)} nodos)"
        
    def __repr__(self) -> str:
        """Representación para debugging."""
        return f"BayesianNetwork(name='{self.name}', nodes={list(self.nodes.keys())})" 