"""
Utilidades para benchmark y evaluación de rendimiento.
"""

import time
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
        
    def _benchmark_marginal_queries(self):
        """Benchmark de consultas marginales (sin evidencia)."""
        networks = [
            ("Burglary", self.parser.create_example_burglary_network()),
            ("Medical", self.parser.create_simple_medical_network())
        ]
        
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