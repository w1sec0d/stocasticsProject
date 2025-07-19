#!/usr/bin/env python3
"""
Script básico de prueba para el Motor de Inferencia Bayesiano.

Este script verifica que los componentes principales funcionen correctamente
y que los resultados sean consistentes entre algoritmos.
"""

import sys
import os

# Añadir src al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.bayesian_network import BayesianNetwork
from src.algorithms.enumeration import EnumerationInference
from src.algorithms.elimination import VariableEliminationInference
from src.utils.parser import NetworkParser


def test_burglary_network():
    """Prueba la red clásica de robo."""
    print("=== PRUEBA RED DE ROBO ===")
    
    # Crear parser y cargar red
    parser = NetworkParser()
    network = parser.create_example_burglary_network()
    
    print(f"Red creada: {network.name}")
    print(f"Variables: {network.get_variables()}")
    print(f"Es válida: {network.is_valid()}")
    
    # Crear motores de inferencia
    enum_engine = EnumerationInference(network, verbose=False)
    elim_engine = VariableEliminationInference(network, verbose=False)
    
    # Consulta clásica del libro: P(Burglary | JohnCalls=true, MaryCalls=true)
    evidence = {"JohnCalls": True, "MaryCalls": True}
    
    print(f"\nConsulta: P(Burglary | {evidence})")
    
    # Ejecutar ambos algoritmos
    enum_result = enum_engine.query("Burglary", evidence)
    elim_result = elim_engine.query("Burglary", evidence)
    
    print(f"Resultado enumeración: {enum_result}")
    print(f"Resultado eliminación: {elim_result}")
    
    # Verificar consistencia
    consistent = True
    for value in enum_result:
        diff = abs(enum_result[value] - elim_result[value])
        if diff > 1e-6:
            print(f"INCONSISTENCIA en {value}: diferencia = {diff}")
            consistent = False
            
    if consistent:
        print("✓ Algoritmos consistentes")
    else:
        print("✗ Algoritmos inconsistentes")
        
    # Estadísticas de rendimiento
    enum_stats = enum_engine.get_performance_stats()
    elim_stats = elim_engine.get_performance_stats()
    
    print(f"\nRendimiento:")
    print(f"  Enumeración: {enum_stats['execution_time']:.4f}s")
    print(f"  Eliminación: {elim_stats['execution_time']:.4f}s")
    
    if elim_stats['execution_time'] > 0:
        speedup = enum_stats['execution_time'] / elim_stats['execution_time']
        print(f"  Aceleración: {speedup:.2f}x")
        
    return consistent


def test_medical_network():
    """Prueba la red médica simple."""
    print("\n=== PRUEBA RED MÉDICA ===")
    
    # Crear red médica
    parser = NetworkParser()
    network = parser.create_simple_medical_network()
    
    print(f"Red creada: {network.name}")
    print(f"Variables: {network.get_variables()}")
    
    # Crear motores
    enum_engine = EnumerationInference(network, verbose=False)
    elim_engine = VariableEliminationInference(network, verbose=False)
    
    # Varias consultas de prueba
    test_cases = [
        {"query": "Disease", "evidence": {}},
        {"query": "Disease", "evidence": {"Symptom1": True}},
        {"query": "Disease", "evidence": {"TestResult": True}},
        {"query": "Disease", "evidence": {"Symptom1": True, "Symptom2": True}},
    ]
    
    all_consistent = True
    
    for case in test_cases:
        query = case["query"]
        evidence = case["evidence"]
        
        print(f"\nConsulta: P({query} | {evidence})")
        
        enum_result = enum_engine.query(query, evidence)
        elim_result = elim_engine.query(query, evidence)
        
        # Verificar consistencia
        consistent = True
        for value in enum_result:
            diff = abs(enum_result[value] - elim_result[value])
            if diff > 1e-6:
                consistent = False
                all_consistent = False
                
        if consistent:
            print(f"  ✓ Consistente: P({query}=True) = {enum_result[True]:.4f}")
        else:
            print(f"  ✗ Inconsistente")
            print(f"    Enum: {enum_result}")
            print(f"    Elim: {elim_result}")
            
    return all_consistent


def test_file_loading():
    """Prueba la carga desde archivos JSON."""
    print("\n=== PRUEBA CARGA DE ARCHIVOS ===")
    
    parser = NetworkParser()
    
    # Probar carga de red de robo
    try:
        network = parser.load_from_json("examples/burglary_network.json")
        print(f"✓ Archivo burglary_network.json cargado: {network.name}")
    except Exception as e:
        print(f"✗ Error cargando burglary_network.json: {e}")
        return False
        
    # Probar carga de red médica
    try:
        network = parser.load_from_json("examples/medical_network.json")
        print(f"✓ Archivo medical_network.json cargado: {network.name}")
    except Exception as e:
        print(f"✗ Error cargando medical_network.json: {e}")
        return False
        
    return True


def main():
    """Función principal de pruebas."""
    print("MOTOR DE INFERENCIA BAYESIANO - PRUEBAS BÁSICAS")
    print("=" * 50)
    
    # Ejecutar todas las pruebas
    tests_passed = 0
    total_tests = 3
    
    if test_file_loading():
        tests_passed += 1
        
    if test_burglary_network():
        tests_passed += 1
        
    if test_medical_network():
        tests_passed += 1
        
    # Resumen
    print(f"\n=== RESUMEN ===")
    print(f"Pruebas pasadas: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✓ Todas las pruebas pasaron exitosamente")
        return 0
    else:
        print("✗ Algunas pruebas fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 