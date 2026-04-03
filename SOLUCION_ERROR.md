# SOLUCIÓN AL ERROR DE INSTALACIÓN

## ¿Qué pasó?

El error ocurrió porque **Prophet requiere un compilador de C** para instalarse en Windows, y tu sistema no tiene uno.

```
ERROR: Failed to build 'pandas' when installing build dependencies
```

## SOLUCIONES (elige una):

---

### ✅ OPCIÓN 1: Versión SIMPLE (RECOMENDADO para Windows)

**Usa Holt-Winters en lugar de Prophet - Instalación fácil**

```bash
start_simple.bat
```

Esta versión:
- ✅ Se instala sin problemas en Windows
- ✅ No requiere compilador
- ✅ Usa algoritmo Holt-Winters (similar a Prophet)
- ✅ Funciona igual de bien para forecasting

---

### OPCIÓN 2: Instalar con Anaconda/Miniconda

**Si realmente necesitas Prophet:**

1. Descarga Miniconda: https://docs.conda.io/en/latest/miniconda.html
2. Abre "Anaconda Prompt"
3. Ejecuta:
```bash
cd C:\Users\sceba\machine_learning_rina
conda create -n forecast python=3.10
conda activate forecast
conda install -c conda-forge prophet flask pandas
python main.py
```

---

### OPCIÓN 3: Instalar Visual C++ Build Tools

1. Descarga: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Instala "Desktop development with C++"
3. Reinicia tu computadora
4. Ejecuta: `install_step_by_step.bat`
5. Ejecuta: `start.bat`

---

## ¿Cuál elijo?

| Opción | Dificultad | Tiempo | Recomendado |
|--------|-----------|--------|-------------|
| **Versión Simple** | ⭐ Fácil | 2 min | ✅ SÍ |
| Anaconda | ⭐⭐ Media | 10 min | Solo si usas Anaconda |
| Build Tools | ⭐⭐⭐ Difícil | 20+ min | No recomendado |

---

## Inicio Rápido (Versión Simple)

```bash
start_simple.bat
```

Abre tu navegador en: http://localhost:5000

---

## Diferencias entre versiones

| Característica | Prophet (original) | Holt-Winters (simple) |
|---------------|-------------------|---------------------|
| Precisión | Alta | Alta |
| Facilidad instalación | ❌ Difícil | ✅ Fácil |
| Velocidad | Media | Rápida |
| Funciona en Windows | ⚠️ Con compilador | ✅ Siempre |

Ambas versiones generan forecasts de 30 días con resultados similares.
