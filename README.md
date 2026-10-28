# Dashboard Interactivo de Titanic en Shiny for Python

Aplicación web interactiva para explorar la tasa de supervivencia de los pasajeros del Titanic según su clase, sexo y rango de edad.

---

## 🚀 Cómo Ejecutar

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
- **Panel de Control Lateral (Sidebar)**:
  - Selector de Clase (1ª, 2ª, 3ª o todas).
  - Selector de Sexo (Mujeres, Hombres o todos).
  - Slider de Rango de Edad (0 a 80 años).
  - Selector de color de las gráficas.
- **Tarjetas de Indicadores (Value Boxes)**:
  - 🛟 Tasa de Supervivencia porcentual en tiempo real.
  - 👥 Total de Pasajeros seleccionados con los filtros.
  - 🎟️ Tarifa Promedio Pagada ($ USD).
- **Visualización y Datos**:
  - Gráfica interactiva de barras con porcentajes automáticos.
  - Tabla dinámica interactiva (`DataGrid`) con la muestra de pasajeros.
