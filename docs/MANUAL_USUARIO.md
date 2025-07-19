# Manual de Usuario - Motor de Inferencia Bayesiano

## Introducción

El Motor de Inferencia Bayesiano es una aplicación que permite realizar consultas probabilísticas sobre Redes Bayesianas utilizando algoritmos de inferencia exacta. Este manual le guiará a través de las funcionalidades principales del sistema.

## Instalación

### Requisitos del Sistema

- Python 3.8 o superior
- Sistema operativo: Linux, macOS, Windows

### Pasos de Instalación

1. Clone o descargue el proyecto a su directorio local
2. Navegue al directorio del proyecto:
   ```bash
   cd stocasticsProject
   ```
3. (Opcional) Instale dependencias si las hay:
   ```bash
   pip install -r requirements.txt
   ```

## Uso Básico

### Modo Línea de Comandos

El modo más directo para realizar consultas específicas:

```bash
python main.py --network archivo_red.json --query Variable --evidence "Var1=valor1,Var2=valor2" --algorithm algoritmo
```

**Parámetros:**

- `--network` (-n): Archivo JSON con la definición de la Red Bayesiana
- `--query` (-q): Variable sobre la cual consultar
- `--evidence` (-e): Evidencia observada (opcional)
- `--algorithm` (-a): Algoritmo a usar (enumeration, elimination, both)

**Ejemplos:**

```bash
# Consulta básica sin evidencia
python main.py -n examples/burglary_network.json -q "Burglary" -a enumeration

# Consulta con evidencia
python main.py -n examples/burglary_network.json -q "Burglary" -e "JohnCalls=true,MaryCalls=true" -a elimination

# Comparar algoritmos
python main.py -n examples/medical_network.json -q "Disease" -e "Symptom1=true" -a both
```

### Modo Interactivo

Para explorar redes y realizar múltiples consultas:

```bash
python main.py --interactive
```

Este modo ofrece un menú con las siguientes opciones:

1. **Cargar red desde archivo**: Permite cargar cualquier archivo JSON válido
2. **Crear red de ejemplo (Robo)**: Carga la red clásica del libro Russell & Norvig
3. **Crear red de ejemplo (Médica)**: Carga una red simple de diagnóstico médico
4. **Realizar consulta**: Interface para hacer consultas paso a paso
5. **Mostrar información de la red**: Estadísticas y estructura de la red actual
6. **Comparar algoritmos**: Ejecuta benchmark de rendimiento
7. **Salir**: Termina el programa

## Formato de Redes Bayesianas

Las redes se definen en formato JSON con la siguiente estructura:

```json
{
  "name": "Nombre de la Red",
  "description": "Descripción opcional",
  "nodes": [
    {
      "name": "NombreVariable",
      "domain": [valor1, valor2, ...],
      "description": "Descripción del nodo",
      "cpt": [
        {
          "parent_values": {"Padre1": valor, "Padre2": valor},
          "probabilities": {
            "valor1": 0.8,
            "valor2": 0.2
          }
        }
      ]
    }
  ],
  "edges": [
    {"parent": "NombrePadre", "child": "NombreHijo"}
  ]
}
```

### Tipos de Valores Soportados

- **Booleanos**: `true`, `false`
- **Números**: Enteros y decimales
- **Cadenas**: Texto entre comillas

## Algoritmos de Inferencia

### 1. Inferencia por Enumeración

- **Cuándo usar**: Redes pequeñas, propósitos educativos
- **Ventajas**: Simple, siempre funciona
- **Desventajas**: Exponencialmente lento para redes grandes
- **Comando**: `--algorithm enumeration`

### 2. Eliminación de Variables

- **Cuándo usar**: Redes medianas a grandes
- **Ventajas**: Mucho más eficiente que enumeración
- **Desventajas**: Uso de memoria puede ser alto
- **Comando**: `--algorithm elimination`

### Comparación de Algoritmos

Use `--algorithm both` para ejecutar ambos algoritmos y comparar:

- Resultados (deben ser idénticos)
- Tiempo de ejecución
- Estadísticas de rendimiento

## Ejemplos de Consultas

### Red de Robo (Burglary Network)

```bash
# ¿Cuál es la probabilidad de robo sin evidencia?
python main.py -n examples/burglary_network.json -q "Burglary"

# ¿Probabilidad de robo si John llama?
python main.py -n examples/burglary_network.json -q "Burglary" -e "JohnCalls=true"

# ¿Probabilidad de robo si ambos vecinos llaman?
python main.py -n examples/burglary_network.json -q "Burglary" -e "JohnCalls=true,MaryCalls=true"

# ¿Probabilidad de que suene la alarma dado evidencia?
python main.py -n examples/burglary_network.json -q "Alarm" -e "Burglary=true"
```

### Red Médica

```bash
# Probabilidad de enfermedad sin síntomas
python main.py -n examples/medical_network.json -q "Disease"

# Probabilidad con fiebre
python main.py -n examples/medical_network.json -q "Disease" -e "Symptom1=true"

# Probabilidad con múltiples síntomas
python main.py -n examples/medical_network.json -q "Disease" -e "Symptom1=true,Symptom2=true"

# Probabilidad con resultado de prueba positivo
python main.py -n examples/medical_network.json -q "Disease" -e "TestResult=true"
```

## Interpretación de Resultados

Los resultados se muestran como distribuciones de probabilidad:

```
Consulta: P(Disease | Symptom1=true)
Resultado: {True: 0.4706, False: 0.5294}
```

Esto significa:

- P(Disease=True | Symptom1=true) = 47.06%
- P(Disease=False | Symptom1=true) = 52.94%

### Estadísticas de Rendimiento

```
Estadísticas:
  Tiempo de ejecución: 0.0023 segundos
  Operaciones: 42
  Tamaño máximo de factor: 8
```

- **Tiempo de ejecución**: Duración del cálculo
- **Operaciones**: Número de llamadas recursivas (solo enumeración)
- **Tamaño máximo de factor**: Factor más grande creado (solo eliminación)

## Opciones Avanzadas

### Modo Verbose

Añada `-v` o `--verbose` para ver el proceso paso a paso:

```bash
python main.py -n examples/burglary_network.json -q "Burglary" -e "JohnCalls=true" -a enumeration -v
```

### Benchmark

Ejecute pruebas de rendimiento automáticas:

```bash
python main.py --benchmark
```

## Solución de Problemas

### Errores Comunes

1. **"Variable 'X' no existe en la red"**

   - Verifique que el nombre de la variable sea exacto (sensible a mayúsculas)
   - Use la opción "Mostrar información de la red" para ver variables disponibles

2. **"Error parseando evidencia"**

   - Use el formato exacto: `Variable=valor,Variable2=valor2`
   - No use espacios alrededor del signo `=`
   - Use `true`/`false` para valores booleanos

3. **"Archivo JSON inválido"**

   - Verifique la sintaxis JSON con un validador
   - Asegúrese de que las probabilidades sumen 1.0 en cada entrada CPT

4. **"La red construida no es válida"**
   - Verifique que no haya ciclos en la estructura
   - Asegúrese de que todos los padres mencionados en CPTs existen como nodos

### Archivos de Log

En caso de errores, use el modo verbose (`-v`) para obtener información detallada del proceso.

## Contacto y Soporte

Este es un proyecto académico de la Universidad Nacional de Colombia para el curso de Modelos Estocásticos. Para preguntas sobre el código o reportar problemas, contacte al equipo de desarrollo del proyecto.
