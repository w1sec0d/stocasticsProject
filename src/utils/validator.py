"""
Utilidades para validación de entradas y datos.
"""

import os
import json
from typing import Dict, List, Any, Optional


class InputValidator:
    """
    Clase para validar entradas del usuario y consistencia de datos.
    """
    
    def __init__(self):
        """Inicializa el validador."""
        pass
        
    def validate_file_exists(self, file_path: str) -> bool:
        """
        Verifica si un archivo existe.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si el archivo existe, False en caso contrario
        """
        return os.path.isfile(file_path)
        
    def validate_json_file(self, file_path: str) -> bool:
        """
        Verifica si un archivo JSON es válido.
        
        Args:
            file_path: Ruta al archivo JSON
            
        Returns:
            True si el JSON es válido, False en caso contrario
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            return False
            
    def validate_network_structure(self, network_data: Dict[str, Any]) -> List[str]:
        """
        Valida la estructura de datos de una red bayesiana.
        
        Args:
            network_data: Datos de la red en formato diccionario
            
        Returns:
            Lista de errores encontrados (vacía si no hay errores)
        """
        errors = []
        
        # Verificar campos requeridos
        required_fields = ['name', 'nodes']
        for field in required_fields:
            if field not in network_data:
                errors.append(f"Campo requerido '{field}' no encontrado")
                
        if 'nodes' not in network_data:
            return errors
            
        # Verificar nodos
        if not isinstance(network_data['nodes'], list):
            errors.append("El campo 'nodes' debe ser una lista")
            return errors
            
        node_names = set()
        for i, node in enumerate(network_data['nodes']):
            node_errors = self._validate_node_structure(node, i)
            errors.extend(node_errors)
            
            if 'name' in node:
                if node['name'] in node_names:
                    errors.append(f"Nombre de nodo duplicado: '{node['name']}'")
                node_names.add(node['name'])
                
        # Verificar aristas si existen
        if 'edges' in network_data:
            edge_errors = self._validate_edges_structure(network_data['edges'], node_names)
            errors.extend(edge_errors)
            
        return errors
        
    def _validate_node_structure(self, node: Dict[str, Any], index: int) -> List[str]:
        """
        Valida la estructura de un nodo individual.
        
        Args:
            node: Datos del nodo
            index: Índice del nodo en la lista
            
        Returns:
            Lista de errores encontrados
        """
        errors = []
        prefix = f"Nodo {index}"
        
        # Verificar campos requeridos
        required_fields = ['name', 'domain']
        for field in required_fields:
            if field not in node:
                errors.append(f"{prefix}: Campo requerido '{field}' no encontrado")
                
        # Verificar dominio
        if 'domain' in node:
            if not isinstance(node['domain'], list):
                errors.append(f"{prefix}: El campo 'domain' debe ser una lista")
            elif len(node['domain']) == 0:
                errors.append(f"{prefix}: El dominio no puede estar vacío")
                
        # Verificar CPT si existe
        if 'cpt' in node:
            if not isinstance(node['cpt'], list):
                errors.append(f"{prefix}: El campo 'cpt' debe ser una lista")
            else:
                for j, entry in enumerate(node['cpt']):
                    if not isinstance(entry, dict):
                        errors.append(f"{prefix}, entrada CPT {j}: Debe ser un diccionario")
                        continue
                        
                    if 'probabilities' not in entry:
                        errors.append(f"{prefix}, entrada CPT {j}: Campo 'probabilities' requerido")
                        continue
                        
                    # Verificar que las probabilidades sumen 1
                    try:
                        probs = entry['probabilities']
                        if isinstance(probs, dict):
                            total = sum(probs.values())
                            if abs(total - 1.0) > 1e-6:
                                errors.append(f"{prefix}, entrada CPT {j}: Las probabilidades deben sumar 1 (suma actual: {total})")
                    except (TypeError, ValueError):
                        errors.append(f"{prefix}, entrada CPT {j}: Probabilidades deben ser números")
                        
        return errors
        
    def _validate_edges_structure(self, edges: List[Dict[str, str]], node_names: set) -> List[str]:
        """
        Valida la estructura de las aristas.
        
        Args:
            edges: Lista de aristas
            node_names: Conjunto de nombres de nodos válidos
            
        Returns:
            Lista de errores encontrados
        """
        errors = []
        
        if not isinstance(edges, list):
            errors.append("El campo 'edges' debe ser una lista")
            return errors
            
        for i, edge in enumerate(edges):
            if not isinstance(edge, dict):
                errors.append(f"Arista {i}: Debe ser un diccionario")
                continue
                
            if 'parent' not in edge or 'child' not in edge:
                errors.append(f"Arista {i}: Debe tener campos 'parent' y 'child'")
                continue
                
            parent = edge['parent']
            child = edge['child']
            
            if parent not in node_names:
                errors.append(f"Arista {i}: Nodo padre '{parent}' no existe")
                
            if child not in node_names:
                errors.append(f"Arista {i}: Nodo hijo '{child}' no existe")
                
            if parent == child:
                errors.append(f"Arista {i}: Un nodo no puede ser padre de sí mismo")
                
        return errors
        
    def parse_evidence_string(self, evidence_str: str) -> Dict[str, Any]:
        """
        Parsea una cadena de evidencia en formato "var1=val1,var2=val2".
        
        Args:
            evidence_str: Cadena de evidencia
            
        Returns:
            Diccionario con la evidencia parseada
            
        Raises:
            ValueError: Si el formato de evidencia es inválido
        """
        if not evidence_str or evidence_str.strip() == "":
            return {}
            
        evidence = {}
        
        try:
            pairs = evidence_str.split(',')
            for pair in pairs:
                pair = pair.strip()
                if '=' not in pair:
                    raise ValueError(f"Formato inválido en '{pair}'. Esperado: variable=valor")
                    
                var, val = pair.split('=', 1)
                var = var.strip()
                val = val.strip()
                
                if not var:
                    raise ValueError("Nombre de variable vacío")
                    
                # Convertir valor a tipo apropiado
                evidence[var] = self._parse_value(val)
                
        except Exception as e:
            raise ValueError(f"Error parseando evidencia '{evidence_str}': {e}")
            
        return evidence
        
    def _parse_value(self, value_str: str) -> Any:
        """
        Convierte una cadena a su tipo apropiado.
        
        Args:
            value_str: Cadena a convertir
            
        Returns:
            Valor convertido
        """
        value_str = value_str.strip()
        
        # Intentar convertir a booleano
        if value_str.lower() in ['true', 'false']:
            return value_str.lower() == 'true'
            
        # Intentar convertir a número
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass
            
        # Mantener como cadena
        return value_str
        
    def validate_query_parameters(self, query_var: str, evidence: Dict[str, Any], 
                                 network_data: Dict[str, Any]) -> List[str]:
        """
        Valida los parámetros de una consulta.
        
        Args:
            query_var: Variable de consulta
            evidence: Evidencia observada
            network_data: Datos de la red
            
        Returns:
            Lista de errores encontrados
        """
        errors = []
        
        # Obtener nombres de variables de la red
        if 'nodes' not in network_data:
            errors.append("Red sin nodos definidos")
            return errors
            
        node_names = {node['name'] for node in network_data['nodes'] if 'name' in node}
        
        # Verificar variable de consulta
        if not query_var:
            errors.append("Variable de consulta no puede estar vacía")
        elif query_var not in node_names:
            errors.append(f"Variable de consulta '{query_var}' no existe en la red")
            
        # Verificar evidencia
        for var, value in evidence.items():
            if var not in node_names:
                errors.append(f"Variable de evidencia '{var}' no existe en la red")
            elif var == query_var:
                errors.append(f"Variable de consulta '{query_var}' no puede tener evidencia")
                
        return errors 