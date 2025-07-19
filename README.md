# Motor de Inferencia Bayesiano

## Información del Proyecto

**Universidad Nacional de Colombia**  
**Curso**: Modelos Estocásticos (ME01)  
**Profesor**: Jorge Eduardo Ortiz Triviño

### Integrantes del Grupo

## Resumen del Proyecto

Este proyecto implementa un **Motor de Inferencia Bayesiano** que permite realizar consultas probabilísticas sobre Redes Bayesianas utilizando dos algoritmos principales de inferencia exacta: **Inferencia por Enumeración** y **Eliminación de Variables**.

La aplicación está basada en el Capítulo 13 "Probabilistic Reasoning" del libro "Artificial Intelligence: A Modern Approach" (4th Ed.) de Russell & Norvig, implementando desde cero los algoritmos fundamentales para el razonamiento probabilístico bajo incertidumbre.

**Palabras clave**: Redes Bayesianas, Inferencia Probabilística, Inteligencia Artificial, Algoritmos de Enumeración, Eliminación de Variables.

## Problema a Resolver

Las Redes Bayesianas son un modelo fundamental para representar y razonar sobre información incierta en sistemas inteligentes. Sin embargo, realizar inferencia probabilística de manera eficiente requiere algoritmos especializados que puedan manejar la complejidad computacional inherente al problema.

Este proyecto aborda la necesidad de:

1. **Representar conocimiento incierto** mediante estructuras de datos eficientes
2. **Realizar consultas probabilísticas** sobre variables de interés dado evidencia observada
3. **Comparar algoritmos de inferencia** en términos de eficiencia y precisión
4. **Proporcionar una herramienta educativa** para entender el funcionamiento interno de estos algoritmos

## Objetivos

### Objetivo General

Desarrollar un sistema de software que implemente algoritmos de inferencia exacta en Redes Bayesianas para resolver consultas probabilísticas en dominios de aplicación real.

### Objetivos Específicos

1. Implementar la estructura de datos para representar Redes Bayesianas
2. Desarrollar el algoritmo de Inferencia por Enumeración (ENUMERATION-ASK)
3. Implementar el algoritmo de Eliminación de Variables (ELIMINATION-ASK)
4. Crear una interfaz de usuario para cargar redes y realizar consultas
5. Evaluar el rendimiento de ambos algoritmos en diferentes escenarios
6. Documentar casos de uso en dominios como diagnóstico médico y análisis de riesgo

## Arquitectura del Sistema

```
src/
├── core/
│   ├── bayesian_network.py    # Estructura principal de la red
│   ├── node.py               # Nodos y tablas de probabilidad
│   └── factor.py             # Factores para eliminación de variables
├── algorithms/
│   ├── enumeration.py        # Algoritmo de enumeración
│   └── elimination.py        # Algoritmo de eliminación de variables
├── utils/
│   ├── parser.py            # Carga de redes desde archivos
│   └── validator.py         # Validación de consultas
├── interface/
│   └── cli.py               # Interfaz de línea de comandos
└── examples/
    ├── burglary_network.json  # Red del ejemplo de robo
    └── medical_network.json   # Red de diagnóstico médico
```

## Tecnologías Utilizadas

- **Lenguaje**: Python 3.8+
- **Librerías**:
  - Estándar de Python (json, argparse, logging)
  - Una librería de estructuras de datos (a definir: NumPy o implementación propia)

## Instalación y Uso

### Requisitos Previos

```bash
python3.8+
```

### Instalación

```bash
git clone [repo-url]
cd stocasticsProject
python -m pip install -r requirements.txt
```

### Uso Básico

```bash
# Consulta usando enumeración
python main.py --network examples/burglary_network.json \
               --query "Burglary" \
               --evidence "JohnCalls=true,MaryCalls=true" \
               --algorithm enumeration

# Consulta usando eliminación de variables
python main.py --network examples/burglary_network.json \
               --query "Burglary" \
               --evidence "JohnCalls=true,MaryCalls=true" \
               --algorithm elimination
```

## Casos de Prueba

1. **Red de Robo (Burglary Network)**: Evaluación básica de funcionamiento
2. **Red de Diagnóstico Médico**: Aplicación en dominio real con múltiples síntomas
3. **Red de Análisis de Riesgo Financiero**: Escenario de alta complejidad computacional

## Estado del Desarrollo

- [ ] Estructura básica del proyecto
- [ ] Implementación de clases principales
- [ ] Algoritmo de enumeración
- [ ] Algoritmo de eliminación de variables
- [ ] Interfaz de usuario
- [ ] Casos de prueba
- [ ] Documentación completa

## Licencia

Proyecto académico - Universidad Nacional de Colombia

## Referencias

Russell, S., & Norvig, P. (2020). _Artificial Intelligence: A Modern Approach_ (4th Global ed.). Pearson.
