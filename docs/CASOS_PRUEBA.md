# Casos de Prueba - Motor de Inferencia Bayesiano

## Introducción

Este documento describe los casos de prueba principales para validar el funcionamiento del Motor de Inferencia Bayesiano. Los casos cubren diferentes escenarios de uso y validan tanto la correctitud como el rendimiento de los algoritmos implementados.

## Caso de Prueba 1: Red de Robo (Burglary Network)

### Descripción

Validación del funcionamiento básico usando la red clásica del libro Russell & Norvig, Capítulo 13.

### Red Utilizada

- **Archivo**: `examples/burglary_network.json`
- **Variables**: Burglary, Earthquake, Alarm, JohnCalls, MaryCalls
- **Estructura**: DAG con 5 nodos y 4 aristas

### Subcasos

#### 1.1 Consulta Marginal Simple

**Objetivo**: Verificar consultas sin evidencia

**Comando**:

```bash
python main.py -n examples/burglary_network.json -q "Burglary" -a both
```

**Resultado Esperado**:

- P(Burglary=True) ≈ 0.001
- P(Burglary=False) ≈ 0.999
- Ambos algoritmos deben dar resultados idénticos

#### 1.2 Consulta con Evidencia Simple

**Objetivo**: Validar inferencia con una observación

**Comando**:

```bash
python main.py -n examples/burglary_network.json -q "Burglary" -e "JohnCalls=true" -a both
```

**Resultado Esperado**:

- P(Burglary=True | JohnCalls=true) > P(Burglary=True)
- Incremento significativo en probabilidad de robo

#### 1.3 Consulta Clásica del Libro

**Objetivo**: Reproducir el ejemplo exacto del libro Russell & Norvig

**Comando**:

```bash
python main.py -n examples/burglary_network.json -q "Burglary" -e "JohnCalls=true,MaryCalls=true" -a both -v
```

**Resultado Esperado**:

- P(Burglary=True | JohnCalls=true, MaryCalls=true) ≈ 0.284
- P(Burglary=False | JohnCalls=true, MaryCalls=true) ≈ 0.716
- Tiempo de ejecución < 0.1 segundos para ambos algoritmos

#### 1.4 Consulta con Evidencia Contradictoria

**Objetivo**: Probar manejo de evidencia que reduce probabilidades

**Comando**:

```bash
python main.py -n examples/burglary_network.json -q "Burglary" -e "JohnCalls=false,MaryCalls=false" -a both
```

**Resultado Esperado**:

- P(Burglary=True) debe disminuir considerablemente
- Resultados consistentes entre algoritmos

### Criterios de Éxito

- ✅ Diferencia entre algoritmos < 1e-6
- ✅ Resultados matemáticamente correctos
- ✅ Tiempo de ejecución razonable
- ✅ Manejo correcto de diferentes tipos de evidencia

---

## Caso de Prueba 2: Red de Diagnóstico Médico

### Descripción

Validación en dominio médico con aplicación práctica real.

### Red Utilizada

- **Archivo**: `examples/medical_network.json`
- **Variables**: Disease, Symptom1, Symptom2, TestResult
- **Estructura**: DAG tipo estrella con 4 nodos

### Subcasos

#### 2.1 Probabilidad Prior

**Objetivo**: Verificar probabilidades base sin evidencia

**Comando**:

```bash
python main.py -n examples/medical_network.json -q "Disease" -a both
```

**Resultado Esperado**:

- P(Disease=True) = 0.1 (prevalencia configurada)
- P(Disease=False) = 0.9

#### 2.2 Diagnóstico con Un Síntoma

**Objetivo**: Actualización bayesiana con fiebre

**Comando**:

```bash
python main.py -n examples/medical_network.json -q "Disease" -e "Symptom1=true" -a both
```

**Resultado Esperado**:

- P(Disease=True | Symptom1=true) > 0.1
- Incremento significativo pero no dramático

#### 2.3 Diagnóstico con Múltiples Síntomas

**Objetivo**: Acumulación de evidencia

**Comando**:

```bash
python main.py -n examples/medical_network.json -q "Disease" -e "Symptom1=true,Symptom2=true" -a both
```

**Resultado Esperado**:

- P(Disease=True) > P(Disease=True | Symptom1=true)
- Efecto acumulativo de múltiples síntomas

#### 2.4 Impacto de Prueba Médica

**Objetivo**: Evaluar peso de evidencia diagnóstica

**Comando**:

```bash
python main.py -n examples/medical_network.json -q "Disease" -e "TestResult=true" -a both
```

**Resultado Esperado**:

- Mayor incremento que síntomas individuales
- Reflejo de alta sensibilidad/especificidad de la prueba

#### 2.5 Escenario Completo

**Objetivo**: Integración de toda la evidencia disponible

**Comando**:

```bash
python main.py -n examples/medical_network.json -q "Disease" -e "Symptom1=true,Symptom2=true,TestResult=true" -a both
```

**Resultado Esperado**:

- Probabilidad muy alta de enfermedad
- Convergencia hacia certeza diagnóstica

### Criterios de Éxito

- ✅ Comportamiento médico intuitivo
- ✅ Monotonicidad de evidencia positiva
- ✅ Consistencia entre algoritmos
- ✅ Valores probabilísticos razonables

---

## Caso de Prueba 3: Benchmark de Rendimiento

### Descripción

Evaluación comparativa de eficiencia entre algoritmos de inferencia.

### Pruebas de Rendimiento

#### 3.1 Consultas Marginales Completas

**Objetivo**: Comparar tiempo para todas las variables

**Comando**:

```bash
python main.py --benchmark
```

**Métricas Evaluadas**:

- Tiempo total de ejecución
- Tiempo promedio por consulta
- Aceleración (speedup) de eliminación vs enumeración
- Uso de memoria (factores máximos)

#### 3.2 Escalabilidad con Evidencia

**Objetivo**: Evaluar impacto de evidencia en rendimiento

**Comandos de Prueba**:

```bash
# Sin evidencia
python main.py -n examples/burglary_network.json -q "Alarm" -a both

# Con evidencia mínima
python main.py -n examples/burglary_network.json -q "Alarm" -e "Burglary=true" -a both

# Con evidencia máxima
python main.py -n examples/burglary_network.json -q "Alarm" -e "Burglary=true,Earthquake=true,JohnCalls=true" -a both
```

**Resultado Esperado**:

- Eliminación de variables más rápida en todos los casos
- Diferencia de rendimiento aumenta con complejidad
- Reducción de tiempo con más evidencia (menos variables ocultas)

### Criterios de Éxito

- ✅ Eliminación de variables > 2x más rápida que enumeración
- ✅ Escalabilidad predecible
- ✅ Sin degradación significativa con evidencia

---

## Caso de Prueba 4: Validación de Entradas

### Descripción

Verificación del manejo robusto de entradas incorrectas y casos límite.

### Subcasos

#### 4.1 Archivos Inválidos

**Objetivo**: Manejo de errores de archivo

**Comandos de Prueba**:

```bash
# Archivo inexistente
python main.py -n archivo_inexistente.json -q "Variable"

# JSON malformado
python main.py -n examples/archivo_malformado.json -q "Variable"
```

**Resultado Esperado**:

- Mensajes de error claros
- No crashes del programa
- Códigos de salida apropiados

#### 4.2 Variables Inexistentes

**Objetivo**: Validación de nombres de variables

**Comando**:

```bash
python main.py -n examples/burglary_network.json -q "VariableInexistente" -a enumeration
```

**Resultado Esperado**:

- Error explicativo sobre variable no encontrada
- Lista de variables disponibles

#### 4.3 Evidencia Malformada

**Objetivo**: Parsing robusto de evidencia

**Comandos de Prueba**:

```bash
# Formato incorrecto
python main.py -n examples/burglary_network.json -q "Burglary" -e "JohnCalls:true"

# Variable inexistente en evidencia
python main.py -n examples/burglary_network.json -q "Burglary" -e "VariableInexistente=true"

# Valor inválido
python main.py -n examples/burglary_network.json -q "Burglary" -e "JohnCalls=maybe"
```

**Resultado Esperado**:

- Mensajes específicos para cada tipo de error
- Sugerencias de formato correcto
- Validación previa a ejecución

### Criterios de Éxito

- ✅ Ningún crash no manejado
- ✅ Mensajes de error informativos
- ✅ Recuperación elegante de errores

---

## Caso de Prueba 5: Modo Interactivo

### Descripción

Validación de la interfaz de usuario interactiva.

### Flujo de Prueba

#### 5.1 Navegación Básica

**Pasos**:

1. Ejecutar `python main.py --interactive`
2. Probar cada opción del menú
3. Verificar manejo de entradas inválidas

#### 5.2 Flujo Completo de Trabajo

**Escenario**:

1. Cargar red de ejemplo (opción 2)
2. Mostrar información de red (opción 5)
3. Realizar consulta (opción 4)
4. Comparar algoritmos (opción 6)
5. Salir (opción 7)

#### 5.3 Manejo de Errores Interactivo

**Pruebas**:

- Entradas no numéricas en menú
- Rutas de archivo incorrectas
- Variables inexistentes en consultas
- Interrupciones con Ctrl+C

### Criterios de Éxito

- ✅ Interfaz intuitiva y clara
- ✅ Manejo robusto de errores
- ✅ Flujo de trabajo completo sin problemas
- ✅ Salida elegante en todas las condiciones

---

## Resumen de Validación

### Lista de Verificación General

Para considerar el sistema completamente validado, todos los siguientes criterios deben cumplirse:

#### Funcionalidad

- [ ] Carga correcta de redes desde JSON
- [ ] Algoritmos dan resultados idénticos
- [ ] Resultados matemáticamente correctos
- [ ] Manejo completo de evidencia

#### Rendimiento

- [ ] Eliminación de variables más eficiente que enumeración
- [ ] Tiempos de respuesta razonables (< 1s para redes pequeñas)
- [ ] Escalabilidad predecible

#### Robustez

- [ ] Manejo elegante de todos los errores identificados
- [ ] Validación completa de entradas
- [ ] Recuperación sin crashes

#### Usabilidad

- [ ] Interfaz CLI clara y consistente
- [ ] Modo interactivo completamente funcional
- [ ] Documentación completa y ejemplos trabajando

### Procedimiento de Validación

1. **Ejecutar script de prueba automatizado**:

   ```bash
   python test_basic.py
   ```

2. **Validar casos específicos manualmente**

3. **Probar modo interactivo completamente**

4. **Verificar documentación con ejemplos reales**

5. **Confirmar criterios de rendimiento**
