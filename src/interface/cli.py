"""
Interfaz de línea de comandos para el Motor de Inferencia Bayesiano.
"""

import os
import sys
from typing import Dict, Any, Optional
from ..core.bayesian_network import BayesianNetwork
from ..algorithms.enumeration import EnumerationInference
from ..algorithms.elimination import VariableEliminationInference
from ..utils.parser import NetworkParser
from ..utils.validator import InputValidator


class CLIInterface:
    """
    Interfaz de línea de comandos para interactuar con el motor de inferencia.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Inicializa la interfaz CLI.
        
        Args:
            verbose: Si mostrar información detallada
        """
        self.verbose = verbose
        self.parser = NetworkParser()
        self.validator = InputValidator()
        self.current_network: Optional[BayesianNetwork] = None
        self.enum_inference: Optional[EnumerationInference] = None
        self.elim_inference: Optional[VariableEliminationInference] = None
        
    def run_interactive_mode(self) -> None:
        """
        Ejecuta el modo interactivo de la CLI.
        """
        print("=== MOTOR DE INFERENCIA BAYESIANO ===")
        print("Universidad Nacional de Colombia - Modelos Estocásticos")
        print("")
        
        while True:
            try:
                print("\nOpciones disponibles:")
                print("1. Cargar red desde archivo")
                print("2. Crear red de ejemplo (Robo)")
                print("3. Crear red de ejemplo (Médica)")
                print("4. Realizar consulta")
                print("5. Mostrar información de la red")
                print("6. Comparar algoritmos")
                print("7. Salir")
                
                choice = input("\nSeleccione una opción (1-7): ").strip()
                
                if choice == '1':
                    self._load_network_interactive()
                elif choice == '2':
                    self._create_burglary_network()
                elif choice == '3':
                    self._create_medical_network()
                elif choice == '4':
                    self._perform_query_interactive()
                elif choice == '5':
                    self._show_network_info()
                elif choice == '6':
                    self._compare_algorithms()
                elif choice == '7':
                    print("¡Gracias por usar el Motor de Inferencia Bayesiano!")
                    break
                else:
                    print("Opción inválida. Por favor seleccione 1-7.")
                    
            except KeyboardInterrupt:
                print("\n\nInterrumpido por el usuario. ¡Hasta luego!")
                break
            except Exception as e:
                print(f"Error: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                    
    def _load_network_interactive(self) -> None:
        """Carga una red desde archivo en modo interactivo."""
        file_path = input("Ingrese la ruta del archivo JSON: ").strip()
        
        try:
            self.current_network = self.parser.load_from_json(file_path)
            self._setup_inference_engines()
            print(f"✓ Red '{self.current_network.name}' cargada exitosamente")
            print(f"  Nodos: {len(self.current_network.nodes)}")
            print(f"  Variables: {', '.join(self.current_network.get_variables())}")
        except Exception as e:
            print(f"✗ Error cargando la red: {e}")
            
    def _create_burglary_network(self) -> None:
        """Crea la red de ejemplo del robo."""
        self.current_network = self.parser.create_example_burglary_network()
        self._setup_inference_engines()
        print("✓ Red de ejemplo 'Robo' creada exitosamente")
        print("  Esta es la red clásica del libro Russell & Norvig")
        print(f"  Variables: {', '.join(self.current_network.get_variables())}")
        
    def _create_medical_network(self) -> None:
        """Crea la red de ejemplo médica."""
        self.current_network = self.parser.create_simple_medical_network()
        self._setup_inference_engines()
        print("✓ Red de ejemplo 'Diagnóstico Médico' creada exitosamente")
        print("  Red simple para diagnóstico con síntomas y pruebas")
        print(f"  Variables: {', '.join(self.current_network.get_variables())}")
        
    def _setup_inference_engines(self) -> None:
        """Configura los motores de inferencia para la red actual."""
        if self.current_network:
            self.enum_inference = EnumerationInference(self.current_network, self.verbose)
            self.elim_inference = VariableEliminationInference(self.current_network, self.verbose)
            
    def _perform_query_interactive(self) -> None:
        """Realiza una consulta en modo interactivo."""
        if not self.current_network:
            print("✗ Primero debe cargar una red")
            return
            
        print(f"\nVariables disponibles: {', '.join(self.current_network.get_variables())}")
        
        # Obtener variable de consulta
        query_var = input("Variable de consulta: ").strip()
        if query_var not in self.current_network.get_variables():
            print(f"✗ Variable '{query_var}' no existe en la red")
            return
            
        # Obtener evidencia
        evidence_str = input("Evidencia (formato: var1=val1,var2=val2) [opcional]: ").strip()
        
        try:
            evidence = self.validator.parse_evidence_string(evidence_str)
        except ValueError as e:
            print(f"✗ Error en formato de evidencia: {e}")
            return
            
        # Obtener algoritmo
        print("\nAlgoritmos disponibles:")
        print("1. Enumeración")
        print("2. Eliminación de Variables")
        print("3. Ambos (comparar)")
        
        algo_choice = input("Seleccione algoritmo (1-3): ").strip()
        
        if algo_choice == '1':
            self._run_single_algorithm('enumeration', query_var, evidence)
        elif algo_choice == '2':
            self._run_single_algorithm('elimination', query_var, evidence)
        elif algo_choice == '3':
            self._run_both_algorithms(query_var, evidence)
        else:
            print("Opción inválida")
            
    def _run_single_algorithm(self, algorithm: str, query_var: str, evidence: Dict[str, Any]) -> None:
        """Ejecuta un solo algoritmo."""
        print(f"\n=== EJECUTANDO {algorithm.upper()} ===")
        
        if algorithm == 'enumeration':
            result = self.enum_inference.query(query_var, evidence)
            stats = self.enum_inference.get_performance_stats()
        else:
            result = self.elim_inference.query(query_var, evidence)
            stats = self.elim_inference.get_performance_stats()
            
        self._print_results(query_var, evidence, result, stats)
        
    def _run_both_algorithms(self, query_var: str, evidence: Dict[str, Any]) -> None:
        """Ejecuta ambos algoritmos y compara resultados."""
        print("\n=== COMPARANDO ALGORITMOS ===")
        
        # Ejecutar enumeración
        print("\n--- Enumeración ---")
        enum_result = self.enum_inference.query(query_var, evidence)
        enum_stats = self.enum_inference.get_performance_stats()
        
        # Ejecutar eliminación
        print("\n--- Eliminación de Variables ---")
        elim_result = self.elim_inference.query(query_var, evidence)
        elim_stats = self.elim_inference.get_performance_stats()
        
        # Mostrar comparación
        print("\n=== COMPARACIÓN ===")
        print(f"Consulta: P({query_var} | {evidence})")
        print("\nResultados:")
        for value in enum_result:
            print(f"  {query_var}={value}: {enum_result[value]:.6f}")
            
        print(f"\nRendimiento:")
        print(f"  Enumeración:     {enum_stats['execution_time']:.4f}s")
        print(f"  Eliminación:     {elim_stats['execution_time']:.4f}s")
        
        if enum_stats['execution_time'] > 0 and elim_stats['execution_time'] > 0:
            speedup = enum_stats['execution_time'] / elim_stats['execution_time']
            print(f"  Aceleración:     {speedup:.2f}x")
            
    def _show_network_info(self) -> None:
        """Muestra información sobre la red actual."""
        if not self.current_network:
            print("✗ No hay red cargada")
            return
            
        print(f"\n=== INFORMACIÓN DE LA RED ===")
        print(f"Nombre: {self.current_network.name}")
        print(f"Número de nodos: {len(self.current_network.nodes)}")
        print(f"Es válida: {'Sí' if self.current_network.is_valid() else 'No'}")
        
        print("\nVariables y dominios:")
        for name, node in self.current_network.nodes.items():
            print(f"  {name}: {node.domain}")
            
        print("\nEstructura:")
        for name, node in self.current_network.nodes.items():
            if node.parents:
                print(f"  {name} ← {', '.join(node.parents)}")
            else:
                print(f"  {name} (nodo raíz)")
                
    def _compare_algorithms(self) -> None:
        """Ejecuta benchmark comparando ambos algoritmos."""
        if not self.current_network:
            print("✗ Primero debe cargar una red")
            return
            
        print("\n=== BENCHMARK DE ALGORITMOS ===")
        variables = self.current_network.get_variables()
        
        # Ejecutar varias consultas
        total_enum_time = 0
        total_elim_time = 0
        num_queries = 0
        
        for query_var in variables:
            print(f"\nProbando consulta marginal para {query_var}...")
            
            # Sin evidencia
            enum_result = self.enum_inference.query(query_var, {})
            enum_stats = self.enum_inference.get_performance_stats()
            
            elim_result = self.elim_inference.query(query_var, {})
            elim_stats = self.elim_inference.get_performance_stats()
            
            total_enum_time += enum_stats['execution_time']
            total_elim_time += elim_stats['execution_time']
            num_queries += 1
            
            print(f"  Enumeración: {enum_stats['execution_time']:.4f}s")
            print(f"  Eliminación: {elim_stats['execution_time']:.4f}s")
            
        print(f"\n=== RESUMEN ===")
        print(f"Consultas realizadas: {num_queries}")
        print(f"Tiempo total enumeración: {total_enum_time:.4f}s")
        print(f"Tiempo total eliminación: {total_elim_time:.4f}s")
        print(f"Tiempo promedio enumeración: {total_enum_time/num_queries:.4f}s")
        print(f"Tiempo promedio eliminación: {total_elim_time/num_queries:.4f}s")
        
        if total_elim_time > 0:
            speedup = total_enum_time / total_elim_time
            print(f"Aceleración promedio: {speedup:.2f}x")
            
    def _print_results(self, query_var: str, evidence: Dict[str, Any], 
                      result: Dict[Any, float], stats: Dict[str, Any]) -> None:
        """Imprime los resultados de una consulta."""
        print(f"\nConsulta: P({query_var} | {evidence})")
        print("Resultado:")
        
        for value, probability in result.items():
            print(f"  P({query_var}={value}) = {probability:.6f}")
            
        print(f"\nEstadísticas:")
        print(f"  Tiempo de ejecución: {stats['execution_time']:.4f} segundos")
        
        if 'operations_count' in stats:
            print(f"  Operaciones: {stats['operations_count']}")
        if 'max_factor_size' in stats:
            print(f"  Tamaño máximo de factor: {stats['max_factor_size']}")
            
    def execute_query(self, network_file: str, query_var: str, 
                     evidence_str: str, algorithm: str) -> Dict[Any, float]:
        """
        Ejecuta una consulta desde línea de comandos.
        
        Args:
            network_file: Archivo de la red
            query_var: Variable de consulta
            evidence_str: Cadena de evidencia
            algorithm: Algoritmo a usar
            
        Returns:
            Distribución de probabilidad resultado
        """
        # Cargar red
        self.current_network = self.parser.load_from_json(network_file)
        self._setup_inference_engines()
        
        # Parsear evidencia
        evidence = self.validator.parse_evidence_string(evidence_str)
        
        # Ejecutar consulta
        if algorithm == 'enumeration':
            return self.enum_inference.query(query_var, evidence)
        elif algorithm == 'elimination':
            return self.elim_inference.query(query_var, evidence)
        elif algorithm == 'both':
            enum_result = self.enum_inference.query(query_var, evidence)
            elim_result = self.elim_inference.query(query_var, evidence)
            
            # Verificar que los resultados coinciden
            for value in enum_result:
                if abs(enum_result[value] - elim_result[value]) > 1e-6:
                    print(f"ADVERTENCIA: Diferencia en resultados para {value}")
                    
            return enum_result
        else:
            raise ValueError(f"Algoritmo desconocido: {algorithm}") 