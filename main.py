#!/usr/bin/env python3
"""
Motor de Inferencia Bayesiano
Proyecto Final - Modelos Estocásticos
Universidad Nacional de Colombia

Punto de entrada principal de la aplicación.
"""

import argparse
import sys
import json
from src.interface.cli import CLIInterface
from src.utils.validator import InputValidator

def main():
    """Función principal del programa."""
    parser = argparse.ArgumentParser(
        description='Motor de Inferencia Bayesiano - Consultas en Redes Bayesianas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

1. Consulta básica con enumeración:
   python main.py --network examples/burglary_network.json 
                  --query "Burglary" 
                  --evidence "JohnCalls=true,MaryCalls=true" 
                  --algorithm enumeration

2. Consulta con eliminación de variables:
   python main.py --network examples/medical_network.json 
                  --query "Disease" 
                  --evidence "Symptom1=true,Symptom2=false" 
                  --algorithm elimination

3. Modo interactivo:
   python main.py --interactive
        """
    )
    
    # Argumentos principales
    parser.add_argument(
        '--network', '-n',
        type=str,
        help='Archivo JSON con la definición de la Red Bayesiana'
    )
    
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Variable de consulta (ej: "Burglary")'
    )
    
    parser.add_argument(
        '--evidence', '-e',
        type=str,
        help='Evidencia observada (ej: "JohnCalls=true,MaryCalls=true")'
    )
    
    parser.add_argument(
        '--algorithm', '-a',
        choices=['enumeration', 'elimination', 'both'],
        default='enumeration',
        help='Algoritmo de inferencia a utilizar'
    )
    
    # Modos de operación
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Modo interactivo para múltiples consultas'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar información detallada del proceso'
    )
    
    parser.add_argument(
        '--benchmark', '-b',
        action='store_true',
        help='Ejecutar benchmark de rendimiento'
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    validator = InputValidator()
    
    if args.interactive:
        # Modo interactivo
        cli = CLIInterface(verbose=args.verbose)
        cli.run_interactive_mode()
    elif args.benchmark:
        # Modo benchmark
        from src.utils.benchmark import BenchmarkRunner
        benchmark = BenchmarkRunner()
        benchmark.run_all_tests()
    else:
        # Modo línea de comandos
        if not all([args.network, args.query]):
            print("Error: En modo línea de comandos se requieren --network y --query")
            parser.print_help()
            sys.exit(1)
            
        if not validator.validate_file_exists(args.network):
            print(f"Error: No se puede encontrar el archivo de red: {args.network}")
            sys.exit(1)
            
        # Ejecutar consulta
        cli = CLIInterface(verbose=args.verbose)
        try:
            result = cli.execute_query(
                network_file=args.network,
                query_var=args.query,
                evidence_str=args.evidence or "",
                algorithm=args.algorithm
            )
            
            print("\n=== RESULTADO ===")
            print(f"Consulta: P({args.query} | {args.evidence or 'sin evidencia'})")
            print(f"Algoritmo: {args.algorithm}")
            print(f"Resultado: {result}")
            
        except Exception as e:
            print(f"Error ejecutando consulta: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    main() 