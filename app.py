"""
=============================================================================
DASHBOARD INTERACTIVO: ANÁLISIS DE SUPERVIVENCIA EN EL TITANIC
=============================================================================
Práctica de Programación en Ciencia de Datos
Arquitectura basada en Dashboard_Basico_Shiny:
  - Controles de entrada: Selector de clase, radio buttons de sexo, slider de edad.
  - Indicadores clave (Value Boxes): Tasa de supervivencia, total de pasajeros y tarifa media.
  - Visualización gráfica: Comparativa de supervivencia en tiempo real (Matplotlib).
  - Explorador de datos: DataGrid con los pasajeros filtrados.
=============================================================================
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from shiny import App, render, ui, reactive

# -----------------------------------------------------------------------------
# 0. Carga y preparación inicial del Dataset Titanic
# -----------------------------------------------------------------------------
RUTA_CSV = Path(__file__).parent / "titanic.csv"

def cargar_datos_base():
    """Carga el dataset desde el archivo local o desde seaborn como respaldo."""
    if RUTA_CSV.exists():
        df = pd.read_csv(RUTA_CSV)
    else:
        import seaborn as sns
        df = sns.load_dataset("titanic")
    
    # Limpieza básica para visualización amigable
    df["edad_redondeada"] = df["age"].fillna(df["age"].median())
    return df

DATOS_TITANIC = cargar_datos_base()

# -----------------------------------------------------------------------------
# 1. Interfaz de Usuario (UI)
# -----------------------------------------------------------------------------
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Panel de Control", class_="fw-bold text-primary mb-3"),
        
        # Filtro 1: Clase de boleto
        ui.input_select(
            "filtro_clase",
            "Clase de Pasajero:",
            {
                "todas": "Todas las Clases",
                "1": "1ª Clase (Alta)",
                "2": "2ª Clase (Media)",
                "3": "3ª Clase (Económica)",
            },
            selected="todas",
        ),
        
        # Filtro 2: Sexo
        ui.input_radio_buttons(
            "filtro_sexo",
            "Sexo del Pasajero:",
            {
                "todos": "Todos",
                "female": "Mujeres (Female)",
                "male": "Hombres (Male)",
            },
            selected="todos",
        ),
        
        # Filtro 3: Rango de Edad
        ui.input_slider(
            "rango_edad",
            "Rango de Edad (Años):",
            min=0,
            max=80,
            value=[0, 80],
            step=5,
        ),
        
        # Selector de Color para la gráfica
        ui.input_select(
            "color_grafica",
            "Color de Gráfica:",
            {
                "#2563EB": "Azul Marino",
                "#059669": "Verde Esmeralda",
                "#DC2626": "Rojo Carmesí",
                "#7C3AED": "Púrpura",
            },
            selected="#2563EB",
        ),
        
        ui.hr(),
        ui.p(
            "Modifica los filtros para observar cómo la clase y el género "
            "influyeron en la probabilidad de supervivencia.",
            class_="text-muted small",
        ),
        width=290,
    ),
    
    # Encabezado principal
    ui.h3("🚢 Dashboard de Exploración: Pasajeros del Titanic", class_="fw-bold mb-3"),
    
    # Indicadores Clave (Value Boxes)
    ui.layout_columns(
        ui.value_box(
            "Tasa de Supervivencia",
            ui.output_text("kpi_supervivencia"),
            showcase=ui.div("🛟", style="font-size: 2rem;"),
            theme="primary",
        ),
        ui.value_box(
            "Pasajeros Filtrados",
            ui.output_text("kpi_total_pasajeros"),
            showcase=ui.div("👥", style="font-size: 2rem;"),
            theme="info",
        ),
        ui.value_box(
            "Tarifa Promedio Pagada",
            ui.output_text("kpi_tarifa_promedio"),
            showcase=ui.div("🎟️", style="font-size: 2rem;"),
            theme="success",
        ),
        col_widths=[4, 4, 4],
    ),
    
    # Gráfico y Tabla interactiva
    ui.layout_columns(
        ui.card(
            ui.card_header("Distribución de Supervivencia del Grupo Seleccionado", class_="fw-bold"),
            ui.output_plot("grafico_supervivencia"),
        ),
        ui.card(
            ui.card_header("Muestra de Pasajeros Filtrados (Primeros 15)", class_="fw-bold"),
            ui.output_data_frame("tabla_pasajeros"),
        ),
        col_widths=[7, 5],
    ),
    
    title="Dashboard Titanic - Shiny",
    fillable=True,
)


# -----------------------------------------------------------------------------
# 2. Lógica del Servidor (Server)
# -----------------------------------------------------------------------------
def server(input, output, session):

    # Cálculo reactivo: filtra los datos en tiempo real según las selecciones del usuario
    @reactive.calc
    def filtrar_datos():
        df = DATOS_TITANIC.copy()
        
        # Filtro de Clase
        clase = input.filtro_clase()
        if clase != "todas":
            df = df[df["pclass"] == int(clase)]
        
        # Filtro de Sexo
        sexo = input.filtro_sexo()
        if sexo != "todos":
            df = df[df["sex"] == sexo]
            
        # Filtro de Edad
        rango = input.rango_edad()
        df = df[(df["edad_redondeada"] >= rango[0]) & (df["edad_redondeada"] <= rango[1])]
        
        return df

    # KPI 1: Tasa de supervivencia
    @render.text
    def kpi_supervivencia():
        df = filtrar_datos()
        if len(df) == 0:
            return "0.0%"
        pct = (df["survived"].sum() / len(df)) * 100
        return f"{pct:.1f}%"

    # KPI 2: Total de pasajeros filtrados
    @render.text
    def kpi_total_pasajeros():
        df = filtrar_datos()
        return f"{len(df)} personas"

    # KPI 3: Tarifa promedio
    @render.text
    def kpi_tarifa_promedio():
        df = filtrar_datos()
        if len(df) == 0:
            return "$0.00 USD"
        return f"${df['fare'].mean():.2f} USD"

    # Gráfico reactivo: barras de Supervivientes vs No Supervivientes
    @render.plot
    def grafico_supervivencia():
        df = filtrar_datos()
        color_base = input.color_grafica()
        
        fig, ax = plt.subplots(figsize=(6, 4))
        
        if len(df) == 0:
            ax.text(0.5, 0.5, "No hay pasajeros con los filtros seleccionados",
                    ha="center", va="center", fontsize=11, color="gray")
            ax.axis("off")
            return fig

        conteo = df["survived"].value_counts().sort_index()
        no_sobrevivio = conteo.get(0, 0)
        sobrevivio = conteo.get(1, 0)
        
        etiquetas = ["Fallecidos (0)", "Sobrevivientes (1)"]
        valores = [no_sobrevivio, sobrevivio]
        colores = ["#9CA3AF", color_base]  # Gris neutral vs Color seleccionado
        
        barras = ax.bar(etiquetas, valores, color=colores, edgecolor="black", alpha=0.85, width=0.55)
        
        # Agregar número y porcentaje encima de cada barra
        total = len(df)
        for barra, val in zip(barras, valores):
            pct = (val / total) * 100 if total > 0 else 0
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height() + (max(valores) * 0.02 + 0.5),
                f"{val} ({pct:.1f}%)",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )
            
        ax.set_title("Cantidad y Proporción de Supervivencia", fontsize=12, fontweight="bold")
        ax.set_ylabel("Número de Pasajeros", fontsize=10)
        ax.set_ylim(0, max(valores) * 1.18 if max(valores) > 0 else 10)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        
        plt.tight_layout()
        return fig

    # Tabla reactiva: lista detallada de pasajeros filtrados
    @render.data_frame
    def tabla_pasajeros():
        df = filtrar_datos()
        # Seleccionamos y renombramos columnas para mayor claridad
        columnas = {
            "pclass": "Clase",
            "sex": "Sexo",
            "age": "Edad",
            "fare": "Tarifa ($)",
            "survived": "Sobrevivió",
            "embark_town": "Puerto Embarque",
        }
        df_mostrar = df[[c for c in columnas.keys() if c in df.columns]].copy()
        df_mostrar["survived"] = df_mostrar["survived"].map({1: "Sí", 0: "No"})
        df_mostrar["fare"] = df_mostrar["fare"].round(2)
        df_mostrar["age"] = df_mostrar["age"].round(1)
        df_mostrar = df_mostrar.rename(columns=columnas)
        
        return render.DataGrid(df_mostrar.head(15))


# -----------------------------------------------------------------------------
# 3. Inicialización de la Aplicación
# -----------------------------------------------------------------------------
app = App(app_ui, server)

if __name__ == "__main__":
    app.run(port=8001)
