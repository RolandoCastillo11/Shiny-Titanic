# Dashboard Interactivo Avanzado: Pasajeros del Titanic en Shiny for Python

Aplicación web analítica interactiva desarrollada con **Shiny for Python (PyShiny)** para explorar multifactorialmente la tasa de supervivencia, estratificación socioeconómica, puertos de embarque y variables demográficas de los pasajeros del RMS Titanic.

---

## 🚀 Cómo Ejecutar Localmente

Desde la terminal en esta carpeta:
```bash
shiny run --reload --port 8001 app.py
```
o ejecutando directamente con Python:
```bash
python app.py
```

Abre tu navegador en:
👉 **`http://127.0.0.1:8001`**

---

## 📊 Características y Arquitectura

### 1. Panel de Control Lateral (Filtros Reactivos Cruzados)
- **Clase de Pasaje:** 1ª Clase (Alta), 2ª Clase (Media), 3ª Clase (Económica) o Todas.
- **Sexo / Género:** Mujeres, Hombres o Todos.
- **Rango de Edad:** Slider interactivo continuo de 0 a 80 años.
- **Puerto de Embarque:** Southampton, Cherbourg y Queenstown.
- **Compañía a Bordo:** Pasajeros que viajaban solos vs. acompañados con familia/hijos.
- **Paleta Cromática:** 5 temas visuales para las gráficas.
- **Descarga de Datos:** Botón para exportar directamente el subconjunto filtrado a formato CSV.

### 2. Tarjetas de Indicadores Clave (Value Boxes)
- 🛟 **Tasa de Supervivencia:** Porcentaje en tiempo real según filtros seleccionados.
- 👥 **Pasajeros en Muestra:** Total de personas evaluadas y porcentaje del total de la tripulación.
- 🎂 **Edad Promedio:** Media de edad del grupo filtrado.
- 🎟️ **Tarifa Promedio Pagada:** Costo medio del pasaje en USD.

### 3. Navegación por Pestañas Temáticas
- **📊 Resumen de Supervivencia y Demografía:** Conteo exacto y porcentajes de desenlace, junto a un histograma comparativo de edades.
- **👥 Análisis por Clase y Género:** Supervivencia cruzada por estrato social y género, con distribución de tarifas por clase.
- **🗺️ Puertos y Dinámica Familiar:** Supervivencia según puerto de abordaje e impacto del acompañamiento familiar.
- **📋 Explorador de Datos y Métricas:** Tabla interactiva `DataGrid` con filtros por columna y formateo amigable en español.

---

## 🛠️ Tecnologías y Librerías
- `shiny` >= 1.0.0
- `pandas` >= 2.0.0
- `numpy` >= 1.24.0
- `matplotlib` >= 3.7.0
- `seaborn` >= 0.12.0
