"""
Utilidades para parsear y cargar Redes Bayesianas desde archivos.
"""

import json
from typing import Dict, Any, Optional, List
from ..core.bayesian_network import BayesianNetwork
from ..core.node import Node
from .validator import InputValidator


class NetworkParser:
    """
    Clase para parsear y cargar Redes Bayesianas desde diferentes formatos.
    """
    
    def __init__(self):
        """Inicializa el parser."""
        self.validator = InputValidator()
        
    def load_from_json(self, file_path: str) -> BayesianNetwork:
        """
        Carga una Red Bayesiana desde un archivo JSON.
        
        Args:
            file_path: Ruta al archivo JSON
            
        Returns:
            Nueva instancia de BayesianNetwork
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el formato del archivo es inválido
        """
        # Verificar que el archivo existe
        if not self.validator.validate_file_exists(file_path):
            raise FileNotFoundError(f"No se puede encontrar el archivo: {file_path}")
            
        # Verificar que es JSON válido
        if not self.validator.validate_json_file(file_path):
            raise ValueError(f"Archivo JSON inválido: {file_path}")
            
        # Cargar datos
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Validar estructura
        errors = self.validator.validate_network_structure(data)
        if errors:
            error_msg = "Errores en la estructura de la red:\n" + "\n".join(f"- {error}" for error in errors)
            raise ValueError(error_msg)
            
        # Crear red
        return self._build_network_from_data(data)
        
    def _build_network_from_data(self, data: Dict[str, Any]) -> BayesianNetwork:
        """
        Construye una Red Bayesiana a partir de datos validados.
        
        Args:
            data: Datos de la red ya validados
            
        Returns:
            Nueva instancia de BayesianNetwork
        """
        # Crear red
        network = BayesianNetwork(data.get('name', 'Red Cargada'))
        
        # Añadir nodos
        for node_data in data['nodes']:
            node = self._create_node_from_data(node_data)
            network.add_node(node)
            
        # Añadir aristas
        if 'edges' in data:
            for edge in data['edges']:
                network.add_edge(edge['parent'], edge['child'])
                
        # Verificar que la red resultante sea válida
        if not network.is_valid():
            raise ValueError("La red construida no es válida (puede contener ciclos)")
            
        return network
        
    def _create_node_from_data(self, node_data: Dict[str, Any]) -> Node:
        """
        Crea un nodo a partir de datos.
        
        Args:
            node_data: Datos del nodo
            
        Returns:
            Nueva instancia de Node
        """
        node = Node(
            name=node_data['name'],
            domain=node_data['domain'],
            description=node_data.get('description', '')
        )
        
        # Añadir entradas CPT si existen
        if 'cpt' in node_data:
            for entry_data in node_data['cpt']:
                parent_values = entry_data.get('parent_values', {})
                probabilities = entry_data['probabilities']
                
                # Convertir claves de probabilidades al tipo correcto
                converted_probabilities = {}
                for key, value in probabilities.items():
                    converted_key = self._convert_json_value_to_domain_type(key, node.domain)
                    converted_probabilities[converted_key] = value
                
                node.set_cpt_entry(parent_values, converted_probabilities)
                
        return node
        
    def save_to_json(self, network: BayesianNetwork, file_path: str) -> None:
        """
        Guarda una Red Bayesiana en formato JSON.
        
        Args:
            network: Red Bayesiana a guardar
            file_path: Ruta donde guardar el archivo
        """
        network.to_json(file_path)
        
    def create_example_burglary_network(self) -> BayesianNetwork:
        """
        Crea la red de ejemplo del robo (burglary network) del libro Russell & Norvig.
        
        Returns:
            Red Bayesiana del ejemplo de robo
        """
        network = BayesianNetwork("Red de Robo")
        
        # Crear nodos
        burglary = Node("Burglary", [True, False], "Ocurrencia de robo")
        earthquake = Node("Earthquake", [True, False], "Ocurrencia de terremoto")
        alarm = Node("Alarm", [True, False], "Alarma sonando")
        john_calls = Node("JohnCalls", [True, False], "John llama")
        mary_calls = Node("MaryCalls", [True, False], "Mary llama")
        
        # Configurar CPTs
        # Burglary (sin padres)
        burglary.set_cpt_entry({}, {True: 0.001, False: 0.999})
        
        # Earthquake (sin padres)
        earthquake.set_cpt_entry({}, {True: 0.002, False: 0.998})
        
        # Alarm (padres: Burglary, Earthquake)
        alarm.set_cpt_entry({"Burglary": True, "Earthquake": True}, {True: 0.95, False: 0.05})
        alarm.set_cpt_entry({"Burglary": True, "Earthquake": False}, {True: 0.94, False: 0.06})
        alarm.set_cpt_entry({"Burglary": False, "Earthquake": True}, {True: 0.29, False: 0.71})
        alarm.set_cpt_entry({"Burglary": False, "Earthquake": False}, {True: 0.001, False: 0.999})
        
        # JohnCalls (padre: Alarm)
        john_calls.set_cpt_entry({"Alarm": True}, {True: 0.90, False: 0.10})
        john_calls.set_cpt_entry({"Alarm": False}, {True: 0.05, False: 0.95})
        
        # MaryCalls (padre: Alarm)
        mary_calls.set_cpt_entry({"Alarm": True}, {True: 0.70, False: 0.30})
        mary_calls.set_cpt_entry({"Alarm": False}, {True: 0.01, False: 0.99})
        
        # Añadir nodos a la red
        network.add_node(burglary)
        network.add_node(earthquake)
        network.add_node(alarm)
        network.add_node(john_calls)
        network.add_node(mary_calls)
        
        # Añadir aristas
        network.add_edge("Burglary", "Alarm")
        network.add_edge("Earthquake", "Alarm")
        network.add_edge("Alarm", "JohnCalls")
        network.add_edge("Alarm", "MaryCalls")
        
        return network
        
    def create_simple_medical_network(self) -> BayesianNetwork:
        """
        Crea una red bayesiana simple para diagnóstico médico.
        
        Returns:
            Red Bayesiana para diagnóstico médico
        """
        network = BayesianNetwork("Red de Diagnóstico Médico")
        
        # Crear nodos
        disease = Node("Disease", [True, False], "Presencia de enfermedad")
        symptom1 = Node("Symptom1", [True, False], "Síntoma 1 (fiebre)")
        symptom2 = Node("Symptom2", [True, False], "Síntoma 2 (dolor)")
        test_result = Node("TestResult", [True, False], "Resultado de prueba")
        
        # Configurar CPTs
        # Disease (sin padres) - prevalencia baja
        disease.set_cpt_entry({}, {True: 0.1, False: 0.9})
        
        # Symptom1 (padre: Disease)
        symptom1.set_cpt_entry({"Disease": True}, {True: 0.8, False: 0.2})
        symptom1.set_cpt_entry({"Disease": False}, {True: 0.1, False: 0.9})
        
        # Symptom2 (padre: Disease)
        symptom2.set_cpt_entry({"Disease": True}, {True: 0.7, False: 0.3})
        symptom2.set_cpt_entry({"Disease": False}, {True: 0.05, False: 0.95})
        
        # TestResult (padre: Disease)
        test_result.set_cpt_entry({"Disease": True}, {True: 0.9, False: 0.1})  # Sensibilidad 90%
        test_result.set_cpt_entry({"Disease": False}, {True: 0.05, False: 0.95})  # Especificidad 95%
        
        # Añadir nodos a la red
        network.add_node(disease)
        network.add_node(symptom1)
        network.add_node(symptom2)
        network.add_node(test_result)
        
        # Añadir aristas
        network.add_edge("Disease", "Symptom1")
        network.add_edge("Disease", "Symptom2")
        network.add_edge("Disease", "TestResult")
        
        return network
         
    def _convert_json_value_to_domain_type(self, json_value: str, domain: List[Any]) -> Any:
        """
        Convierte un valor de JSON string al tipo apropiado según el dominio.
        
        Args:
            json_value: Valor como string del JSON
            domain: Lista de valores válidos en el dominio
            
        Returns:
            Valor convertido al tipo correcto
        """
        # Intentar convertir a booleano si el dominio contiene booleanos
        if True in domain or False in domain:
            if json_value.lower() == 'true':
                return True
            elif json_value.lower() == 'false':
                return False
                
        # Intentar convertir a número
        try:
            if '.' in str(json_value):
                converted = float(json_value)
                if converted in domain:
                    return converted
            else:
                converted = int(json_value)
                if converted in domain:
                    return converted
        except (ValueError, TypeError):
            pass
            
        # Buscar coincidencia exacta como string
        if json_value in domain:
            return json_value
            
        # Si no se puede convertir, devolver el valor original
        return json_value 