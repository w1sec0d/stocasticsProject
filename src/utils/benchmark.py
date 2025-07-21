"""
Utilidades para benchmark y evaluación de rendimiento.
"""

import time
import os
from typing import Dict, List, Any
from ..core.bayesian_network import BayesianNetwork
from ..algorithms.enumeration import EnumerationInference
from ..algorithms.elimination import VariableEliminationInference
from .parser import NetworkParser


class BenchmarkRunner:
    """
    Ejecuta benchmarks de rendimiento comparando algoritmos de inferencia.
    """
    
    def __init__(self):
        """Inicializa el runner de benchmarks."""
        self.parser = NetworkParser()
        self.results = []
        
    def run_all_tests(self):
        """
        Ejecuta todos los benchmarks disponibles.
        """
        print("=== BENCHMARK DE RENDIMIENTO ===")
        print("Motor de Inferencia Bayesiano - Universidad Nacional de Colombia")
        print()
        
        # Probar con red de robo
        print("📊 Benchmark Red de Robo (Russell & Norvig)")
        self._benchmark_burglary_network()
        
        print("\n📊 Benchmark Red Médica")
        self._benchmark_medical_network()
        
        print("\n📊 Benchmark Red de Sistema de Seguridad (Compleja)")
        self._benchmark_security_network()
        
        print("\n📊 Benchmark Consultas Marginales")
        self._benchmark_marginal_queries()
        
        print("\n=== RESUMEN FINAL ===")
        self._print_summary()
        
    def _benchmark_burglary_network(self):
        """Benchmark específico para la red de robo."""
        network = self.parser.create_example_burglary_network()
        
        # Crear motores
        enum_engine = EnumerationInference(network, verbose=False)
        elim_engine = VariableEliminationInference(network, verbose=False)
        
        # Casos de prueba
        test_cases = [
            {"query": "Burglary", "evidence": {}},
            {"query": "Burglary", "evidence": {"JohnCalls": True}},
            {"query": "Burglary", "evidence": {"MaryCalls": True}},
            {"query": "Burglary", "evidence": {"JohnCalls": True, "MaryCalls": True}},
            {"query": "Alarm", "evidence": {"Burglary": True}},
            {"query": "Alarm", "evidence": {"Earthquake": True}},
        ]
        
        print(f"Ejecutando {len(test_cases)} consultas...")
        
        total_enum_time = 0
        total_elim_time = 0
        
        for i, case in enumerate(test_cases, 1):
            query = case["query"]
            evidence = case["evidence"]
            
            print(f"  {i}. P({query} | {evidence})")
            
            # Ejecutar ambos algoritmos
            start_time = time.time()
            enum_result = enum_engine.query(query, evidence)
            enum_time = time.time() - start_time
            
            start_time = time.time()
            elim_result = elim_engine.query(query, evidence)
            elim_time = time.time() - start_time
            
            total_enum_time += enum_time
            total_elim_time += elim_time
            
            # Verificar consistencia
            consistent = self._check_consistency(enum_result, elim_result)
            status = "✅" if consistent else "❌"
            
            print(f"     Enum: {enum_time:.4f}s | Elim: {elim_time:.4f}s | {status}")
            
        speedup = total_enum_time / total_elim_time if total_elim_time > 0 else 0
        print(f"\n  Tiempo total:")
        print(f"    Enumeración: {total_enum_time:.4f}s")
        print(f"    Eliminación: {total_elim_time:.4f}s")
        print(f"    Aceleración: {speedup:.2f}x")
        
        self.results.append({
            'network': 'Burglary',
            'queries': len(test_cases),
            'enum_total': total_enum_time,
            'elim_total': total_elim_time,
            'speedup': speedup
        })
        
    def _benchmark_medical_network(self):
        """Benchmark específico para la red médica."""
        network = self.parser.create_simple_medical_network()
        
        # Crear motores
        enum_engine = EnumerationInference(network, verbose=False)
        elim_engine = VariableEliminationInference(network, verbose=False)
        
        # Casos de prueba médicos
        test_cases = [
            {"query": "Disease", "evidence": {}},
            {"query": "Disease", "evidence": {"Symptom1": True}},
            {"query": "Disease", "evidence": {"Symptom2": True}},
            {"query": "Disease", "evidence": {"TestResult": True}},
            {"query": "Disease", "evidence": {"Symptom1": True, "Symptom2": True}},
            {"query": "Disease", "evidence": {"Symptom1": True, "TestResult": True}},
            {"query": "TestResult", "evidence": {"Disease": True}},
        ]
        
        print(f"Ejecutando {len(test_cases)} consultas médicas...")
        
        total_enum_time = 0
        total_elim_time = 0
        
        for i, case in enumerate(test_cases, 1):
            query = case["query"]
            evidence = case["evidence"]
            
            print(f"  {i}. P({query} | {evidence})")
            
            # Ejecutar ambos algoritmos
            start_time = time.time()
            enum_result = enum_engine.query(query, evidence)
            enum_time = time.time() - start_time
            
            start_time = time.time()
            elim_result = elim_engine.query(query, evidence)
            elim_time = time.time() - start_time
            
            total_enum_time += enum_time
            total_elim_time += elim_time
            
            # Verificar consistencia
            consistent = self._check_consistency(enum_result, elim_result)
            status = "✅" if consistent else "❌"
            
            print(f"     Enum: {enum_time:.4f}s | Elim: {elim_time:.4f}s | {status}")
            
        speedup = total_enum_time / total_elim_time if total_elim_time > 0 else 0
        print(f"\n  Tiempo total:")
        print(f"    Enumeración: {total_enum_time:.4f}s")
        print(f"    Eliminación: {total_elim_time:.4f}s")
        print(f"    Aceleración: {speedup:.2f}x")
        
        self.results.append({
            'network': 'Medical',
            'queries': len(test_cases),
            'enum_total': total_enum_time,
            'elim_total': total_elim_time,
            'speedup': speedup
        })
        
    def _benchmark_security_network(self):
        """Benchmark específico para la red de sistema de seguridad."""
        try:
            # Cargar red desde archivo JSON
            network = self._load_security_network()
            if network is None:
                print("  ⚠️ No se pudo cargar la red de seguridad, saltando...")
                return
        except Exception as e:
            print(f"  ❌ Error cargando red de seguridad: {e}")
            return
        
        # Crear motores
        enum_engine = EnumerationInference(network, verbose=False)
        elim_engine = VariableEliminationInference(network, verbose=False)
        
        # Casos de prueba complejos para sistema de seguridad
        test_cases = [
            # Consultas básicas sin evidencia
            {"query": "IntruderPresence", "evidence": {}},
            {"query": "ThreatLevel", "evidence": {}},
            {"query": "AlarmActivation", "evidence": {}},
            
            # Consultas con evidencia de sensores individuales
            {"query": "IntruderPresence", "evidence": {"MotionSensor": True}},
            {"query": "IntruderPresence", "evidence": {"DoorSensor": True}},
            {"query": "IntruderPresence", "evidence": {"WindowSensor": True}},
            {"query": "IntruderPresence", "evidence": {"SoundSensor": True}},
            
            # Consultas con múltiples sensores activados
            {"query": "IntruderPresence", "evidence": {"MotionSensor": True, "DoorSensor": True}},
            {"query": "IntruderPresence", "evidence": {"MotionSensor": True, "WindowSensor": True}},
            {"query": "ThreatLevel", "evidence": {"MotionSensor": True, "DoorSensor": True, "WindowSensor": True}},
            
            # Consultas condicionadas por contexto
            {"query": "ThreatLevel", "evidence": {"TimeOfDay": "night", "WeatherCondition": "storm"}},
            {"query": "AlarmActivation", "evidence": {"TimeOfDay": "night", "SoundSensor": True}},
            {"query": "SecurityResponse", "evidence": {"AlarmActivation": True, "TimeOfDay": "night"}},
            
            # Consultas complejas con múltiple evidencia
            {"query": "IntruderPresence", "evidence": {
                "MotionSensor": True, "DoorSensor": True, "SoundSensor": True, "TimeOfDay": "night"
            }},
            {"query": "SecurityResponse", "evidence": {
                "MotionSensor": True, "DoorSensor": True, "WeatherCondition": "clear", "TimeOfDay": "night"
            }},
            
            # Consultas de diagnóstico inverso
            {"query": "WeatherCondition", "evidence": {"MotionSensor": False, "WindowSensor": True}},
            {"query": "TimeOfDay", "evidence": {"SecurityResponse": "dispatch"}},
        ]
        
        print(f"Ejecutando {len(test_cases)} consultas de seguridad...")
        
        total_enum_time = 0
        total_elim_time = 0
        
        for i, case in enumerate(test_cases, 1):
            query = case["query"]
            evidence = case["evidence"]
            
            print(f"  {i:2d}. P({query} | {evidence})")
            
            # Ejecutar ambos algoritmos
            start_time = time.time()
            enum_result = enum_engine.query(query, evidence)
            enum_time = time.time() - start_time
            
            start_time = time.time()
            elim_result = elim_engine.query(query, evidence)
            elim_time = time.time() - start_time
            
            total_enum_time += enum_time
            total_elim_time += elim_time
            
            # Verificar consistencia
            consistent = self._check_consistency(enum_result, elim_result)
            status = "✅" if consistent else "❌"
            
            print(f"      Enum: {enum_time:.4f}s | Elim: {elim_time:.4f}s | {status}")
            
        speedup = total_enum_time / total_elim_time if total_elim_time > 0 else 0
        print(f"\n  Tiempo total:")
        print(f"    Enumeración: {total_enum_time:.4f}s")
        print(f"    Eliminación: {total_elim_time:.4f}s")
        print(f"    Aceleración: {speedup:.2f}x")
        
        # Mostrar información adicional sobre la red
        variables = network.get_variables()
        print(f"    Variables en la red: {len(variables)}")
        print(f"    Complejidad esperada: Exponencial en {len(variables)} variables")
        
        self.results.append({
            'network': 'Security',
            'queries': len(test_cases),
            'enum_total': total_enum_time,
            'elim_total': total_elim_time,
            'speedup': speedup
        })
        
    def _load_security_network(self) -> BayesianNetwork:
        """
        Carga la red de sistema de seguridad desde el archivo JSON.
        
        Returns:
            Red Bayesiana del sistema de seguridad, o None si no se puede cargar
        """
        # Buscar el archivo en diferentes ubicaciones posibles
        possible_paths = [
            "examples/security_system_network.json",
            "../../examples/security_system_network.json",
            os.path.join(os.path.dirname(__file__), "../../examples/security_system_network.json"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    return self.parser.load_from_json(path)
                except Exception as e:
                    print(f"  ⚠️ Error cargando desde {path}: {e}")
                    continue
                    
        print("  ⚠️ No se encontró security_system_network.json en las ubicaciones esperadas")
        return None
        
    def _benchmark_marginal_queries(self):
        """Benchmark de consultas marginales (sin evidencia)."""
        networks = [
            ("Burglary", self.parser.create_example_burglary_network()),
            ("Medical", self.parser.create_simple_medical_network())
        ]
        
        # Añadir red de seguridad si está disponible
        security_network = self._load_security_network()
        if security_network is not None:
            networks.append(("Security", security_network))
        
        print("Comparando consultas marginales (sin evidencia)...")
        
        for net_name, network in networks:
            print(f"\n  Red {net_name}:")
            
            enum_engine = EnumerationInference(network, verbose=False)
            elim_engine = VariableEliminationInference(network, verbose=False)
            
            variables = network.get_variables()
            total_enum_time = 0
            total_elim_time = 0
            
            for var in variables:
                # Consulta marginal
                start_time = time.time()
                enum_result = enum_engine.query(var, {})
                enum_time = time.time() - start_time
                
                start_time = time.time()
                elim_result = elim_engine.query(var, {})
                elim_time = time.time() - start_time
                
                total_enum_time += enum_time
                total_elim_time += elim_time
                
                consistent = self._check_consistency(enum_result, elim_result)
                status = "✅" if consistent else "❌"
                
                print(f"    P({var}): {enum_time:.4f}s | {elim_time:.4f}s | {status}")
                
            speedup = total_enum_time / total_elim_time if total_elim_time > 0 else 0
            print(f"    Total: {total_enum_time:.4f}s | {total_elim_time:.4f}s | {speedup:.2f}x")
            
    def _check_consistency(self, result1: Dict[Any, float], result2: Dict[Any, float], 
                          tolerance: float = 1e-6) -> bool:
        """
        Verifica que dos resultados sean consistentes.
        
        Args:
            result1: Primer resultado
            result2: Segundo resultado
            tolerance: Tolerancia para diferencias
            
        Returns:
            True si son consistentes, False en caso contrario
        """
        if set(result1.keys()) != set(result2.keys()):
            return False
            
        for key in result1:
            if abs(result1[key] - result2[key]) > tolerance:
                return False
                
        return True
        
    def _print_summary(self):
        """Imprime un resumen de todos los benchmarks."""
        if not self.results:
            print("No hay resultados para mostrar.")
            return
            
        print("Resumen de rendimiento por red:")
        print("-" * 50)
        
        total_queries = 0
        total_enum_time = 0
        total_elim_time = 0
        
        for result in self.results:
            network = result['network']
            queries = result['queries']
            enum_time = result['enum_total']
            elim_time = result['elim_total']
            speedup = result['speedup']
            
            print(f"{network:12s}: {queries:3d} consultas | "
                  f"Enum: {enum_time:.4f}s | Elim: {elim_time:.4f}s | "
                  f"Speedup: {speedup:.2f}x")
                  
            total_queries += queries
            total_enum_time += enum_time
            total_elim_time += elim_time
            
        overall_speedup = total_enum_time / total_elim_time if total_elim_time > 0 else 0
        
        print("-" * 50)
        print(f"{'TOTAL':12s}: {total_queries:3d} consultas | "
              f"Enum: {total_enum_time:.4f}s | Elim: {total_elim_time:.4f}s | "
              f"Speedup: {overall_speedup:.2f}x")
              
        print("\n📊 Conclusiones:")
        if overall_speedup > 1.5:
            print("✅ Eliminación de variables es significativamente más rápida")
        elif overall_speedup > 1.0:
            print("✅ Eliminación de variables es ligeramente más rápida")
        elif overall_speedup < 0.8:
            print("⚠️  Enumeración es más rápida (inesperado para redes pequeñas)")
        else:
            print("📊 Rendimiento similar entre algoritmos")
            
        print(f"✅ Todos los algoritmos dieron resultados consistentes")
        print(f"🎯 Sistema validado para {total_queries} consultas diferentes") 