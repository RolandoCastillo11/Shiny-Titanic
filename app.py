"""
=============================================================================
DASHBOARD INTERACTIVO AVANZADO: ANÁLISIS DE PASAJEROS DEL TITANIC
=============================================================================
Materia: Programación para Ciencia de Datos
Arquitectura: Shiny for Python (PyShiny)
Dataset: Pasajeros del RMS Titanic (891 registros)
Características:
  - Panel lateral con múltiples filtros cruzados (Clase, Género, Edad, Puerto, Acompañamiento).
  - 4 Indicadores clave de rendimiento (Value Boxes).
  - Navegación por pestañas temáticas (Supervivencia, Clases y Género, Puertos, Explorador).
  - 6 Gráficas analíticas detalladas de alta resolución.
  - Exportación de datos filtrados en formato CSV.
=============================================================================
"""

import os
import io
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# Configuración de backend sin interfaz gráfica para estabilidad en Windows
mpl_dir = Path(tempfile.gettempdir()) / "mpl_cache"
mpl_dir.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(mpl_dir)
matplotlib.use("Agg")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#cbd5e1"
plt.rcParams["axes.linewidth"] = 0.8

from shiny import App, render, ui, reactive

# -----------------------------------------------------------------------------
# 1. Carga y Preparación de Datos
# -----------------------------------------------------------------------------
RUTA_CSV = Path(__file__).parent / "titanic.csv"

def cargar_datos():
    """Carga el dataset local o desde seaborn como respaldo."""
    if RUTA_CSV.exists():
        df = pd.read_csv(RUTA_CSV)
    else:
        import seaborn as sns
        df = sns.load_dataset("titanic")
    
    # Imputación de edad para análisis continuo
    df["edad_redondeada"] = df["age"].fillna(df["age"].median())
    
    # Mapeos descriptivos en español
    df["clase_texto"] = df["pclass"].map({1: "1ª Clase", 2: "2ª Clase", 3: "3ª Clase"})
    df["sexo_texto"] = df["sex"].map({"female": "Mujer", "male": "Hombre"})
    df["supervivencia_texto"] = df["survived"].map({1: "Sobrevivió", 0: "No Sobrevivió"})
    
    puertos = {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"}
    if "embark_town" in df.columns:
        df["puerto_nombre"] = df["embark_town"].fillna("Desconocido")
    elif "embarked" in df.columns:
        df["puerto_nombre"] = df["embarked"].map(puertos).fillna("Desconocido")
    else:
        df["puerto_nombre"] = "Desconocido"
        
    if "alone" in df.columns:
        df["acompaniamiento"] = df["alone"].map({True: "Viajaba Solo", False: "Con Familia"})
    else:
        df["acompaniamiento"] = np.where((df.get("sibsp", 0) + df.get("parch", 0)) > 0, "Con Familia", "Viajaba Solo")
        
    return df

DATOS_TITANIC = cargar_datos()

# -----------------------------------------------------------------------------
# 2. Interfaz de Usuario (UI)
# -----------------------------------------------------------------------------
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("⚙️ Filtros Analíticos", class_="fw-bold text-primary mb-3"),
        
        ui.input_select(
            "filtro_clase",
            "Clase de Pasaje:",
            {
                "todas": "Todas las Clases",
                "1": "1ª Clase (Alta / Camarotes)",
                "2": "2ª Clase (Media)",
                "3": "3ª Clase (Económica)",
            },
            selected="todas",
        ),
        
        ui.input_radio_buttons(
            "filtro_sexo",
            "Sexo / Género:",
            {
                "todos": "Todos",
                "female": "Mujeres (Female)",
                "male": "Hombres (Male)",
            },
            selected="todos",
        ),
        
        ui.input_slider(
            "rango_edad",
            "Rango de Edad (Años):",
            min=0,
            max=80,
            value=[0, 80],
            step=1,
        ),
        
        ui.input_select(
            "filtro_puerto",
            "Puerto de Embarque:",
            {
                "todos": "Todos los Puertos",
                "Southampton": "Southampton (Reino Unido)",
                "Cherbourg": "Cherbourg (Francia)",
                "Queenstown": "Queenstown (Irlanda)",
            },
            selected="todos",
        ),
        
        ui.input_select(
            "filtro_familia",
            "Compañía a Bordo:",
            {
                "todos": "Todos",
                "Viajaba Solo": "Viajaba Solo",
                "Con Familia": "Acompañado (Familia / Niños)",
            },
            selected="todos",
        ),
        
        ui.hr(),
        ui.input_select(
            "paleta_color",
            "Tema de Color Gráfico:",
            {
                "#1D4ED8": "Azul Real Oceánico",
                "#059669": "Verde Esmeralda",
                "#DC2626": "Rojo Carmesí",
                "#7C3AED": "Púrpura Amatista",
                "#D97706": "Ámbar Dorado",
            },
            selected="#1D4ED8",
        ),
        
        ui.download_button("descargar_datos", "📥 Descargar CSV Filtrado", class_="btn-outline-primary btn-sm w-100 mt-2"),
        
        ui.hr(),
        ui.p(
            "Filtros reactivos en tiempo real. Permite evaluar hipótesis históricas sobre el rescate de mujeres y niños.",
            class_="text-muted small",
        ),
        width=300,
    ),
    
    # Encabezado principal
    ui.div(
        ui.h3("🚢 Dashboard Analítico Detallado: Pasajeros del RMS Titanic", class_="fw-bold text-dark mb-1"),
        ui.p("Exploración multifactorial de supervivencia, demografía, estratificación social y puertos de embarque.", class_="text-muted mb-3"),
    ),
    
    # Fila de Indicadores (Value Boxes)
    ui.layout_columns(
        ui.value_box(
            "Tasa de Supervivencia",
            ui.output_text("kpi_tasa_supervivencia"),
            showcase=ui.div("🛟", style="font-size: 2.2rem;"),
            theme="primary",
        ),
        ui.value_box(
            "Pasajeros en Muestra",
            ui.output_text("kpi_total_pasajeros"),
            showcase=ui.div("👥", style="font-size: 2.2rem;"),
            theme="info",
        ),
        ui.value_box(
            "Edad Promedio",
            ui.output_text("kpi_edad_promedio"),
            showcase=ui.div("🎂", style="font-size: 2.2rem;"),
            theme="warning",
        ),
        ui.value_box(
            "Tarifa Promedio Pagada",
            ui.output_text("kpi_tarifa_promedio"),
            showcase=ui.div("🎟️", style="font-size: 2.2rem;"),
            theme="success",
        ),
        col_widths=[3, 3, 3, 3],
    ),
    
    # Contenedor central con Pestañas
    ui.navset_card_tab(
        ui.nav_panel(
            "📊 Resumen de Supervivencia y Demografía",
            ui.layout_columns(
                ui.card(
                    ui.card_header("Distribución de Supervivencia (Conteo y Porcentaje)", class_="fw-bold"),
                    ui.output_plot("grafico_supervivencia_barras", height="340px"),
                ),
                ui.card(
                    ui.card_header("Distribución de Edades por Desenlace", class_="fw-bold"),
                    ui.output_plot("grafico_distribucion_edad", height="340px"),
                ),
                col_widths=[6, 6],
            ),
        ),
        
        ui.nav_panel(
            "👥 Análisis por Clase y Género",
            ui.layout_columns(
                ui.card(
                    ui.card_header("Tasa de Supervivencia por Clase Social y Género", class_="fw-bold"),
                    ui.output_plot("grafico_clase_genero", height="340px"),
                ),
                ui.card(
                    ui.card_header("Tarifa Pagada según la Clase de Boleto", class_="fw-bold"),
                    ui.output_plot("grafico_tarifa_clase", height="340px"),
                ),
                col_widths=[6, 6],
            ),
        ),
        
        ui.nav_panel(
            "🗺️ Puertos y Dinámica Familiar",
            ui.layout_columns(
                ui.card(
                    ui.card_header("Supervivencia según Puerto de Embarque", class_="fw-bold"),
                    ui.output_plot("grafico_puertos", height="340px"),
                ),
                ui.card(
                    ui.card_header("Impacto del Acompañamiento Familiar", class_="fw-bold"),
                    ui.output_plot("grafico_familia", height="340px"),
                ),
                col_widths=[6, 6],
            ),
        ),
        
        ui.nav_panel(
            "📋 Explorador de Datos y Métricas",
            ui.card(
                ui.card_header("Tabla de Registros Filtrados (Exploración Interactiva)", class_="fw-bold"),
                ui.output_data_frame("tabla_pasajeros_completa"),
            ),
        ),
    ),
    
    title="Dashboard Titanic Avanzado - Shiny",
    fillable=True,
)

# -----------------------------------------------------------------------------
# 3. Lógica del Servidor (Server)
# -----------------------------------------------------------------------------
def server(input, output, session):

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
        
        # Filtro de Puerto
        puerto = input.filtro_puerto()
        if puerto != "todos":
            df = df[df["puerto_nombre"] == puerto]
            
        # Filtro de Familia
        familia = input.filtro_familia()
        if familia != "todos":
            df = df[df["acompaniamiento"] == familia]
            
        return df

    # ---- KPIs ----
    @render.text
    def kpi_tasa_supervivencia():
        df = filtrar_datos()
        if len(df) == 0:
            return "0.0%"
        pct = (df["survived"].sum() / len(df)) * 100
        return f"{pct:.1f}%"

    @render.text
    def kpi_total_pasajeros():
        df = filtrar_datos()
        total_gral = len(DATOS_TITANIC)
        pct = (len(df) / total_gral) * 100
        return f"{len(df):,} ({pct:.0f}% del total)"

    @render.text
    def kpi_edad_promedio():
        df = filtrar_datos()
        if len(df) == 0:
            return "N/A"
        return f"{df['edad_redondeada'].mean():.1f} años"

    @render.text
    def kpi_tarifa_promedio():
        df = filtrar_datos()
        if len(df) == 0:
            return "$0.00 USD"
        return f"${df['fare'].mean():.2f} USD"

    # ---- Gráficas Pestaña 1 ----
    @render.plot
    def grafico_supervivencia_barras():
        df = filtrar_datos()
        color_primario = input.paleta_color()
        
        fig, ax = plt.subplots(figsize=(6, 4))
        if len(df) == 0:
            ax.text(0.5, 0.5, "No hay pasajeros con los filtros seleccionados", ha="center", va="center", color="gray")
            ax.axis("off")
            return fig
            
        conteo = df["survived"].value_counts().sort_index()
        no_sob = conteo.get(0, 0)
        sob = conteo.get(1, 0)
        
        etiquetas = ["Fallecidos (0)", "Sobrevivientes (1)"]
        valores = [no_sob, sob]
        colores = ["#94A3B8", color_primario]
        
        barras = ax.bar(etiquetas, valores, color=colores, width=0.5, edgecolor="#334155", linewidth=1)
        total = len(df)
        for b, v in zip(barras, valores):
            pct = (v / total) * 100 if total > 0 else 0
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + (max(valores) * 0.02 + 1),
                    f"{v} ({pct:.1f}%)", ha="center", va="bottom", fontsize=10, fontweight="bold")
                    
        ax.set_ylabel("Cantidad de Pasajeros")
        ax.set_ylim(0, max(valores) * 1.2 if max(valores) > 0 else 10)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        return fig

    @render.plot
    def grafico_distribucion_edad():
        df = filtrar_datos()
        color_primario = input.paleta_color()
        
        fig, ax = plt.subplots(figsize=(6, 4))
        if len(df) == 0:
            ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center", color="gray")
            ax.axis("off")
            return fig
            
        edades_no_sob = df[df["survived"] == 0]["edad_redondeada"]
        edades_sob = df[df["survived"] == 1]["edad_redondeada"]
        
        bins = np.linspace(0, 80, 17)
        ax.hist(edades_no_sob, bins=bins, color="#94A3B8", alpha=0.6, label="Fallecidos", edgecolor="white")
        ax.hist(edades_sob, bins=bins, color=color_primario, alpha=0.75, label="Sobrevivientes", edgecolor="white")
        
        ax.set_xlabel("Edad (Años)")
        ax.set_ylabel("Frecuencia de Pasajeros")
        ax.legend(frameon=True, facecolor="white")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        return fig

    # ---- Gráficas Pestaña 2 ----
    @render.plot
    def grafico_clase_genero():
        df = filtrar_datos()
        fig, ax = plt.subplots(figsize=(6, 4))
        if len(df) == 0:
            ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center", color="gray")
            ax.axis("off")
            return fig
            
        resumen = df.groupby(["clase_texto", "sexo_texto"])["survived"].mean().unstack().fillna(0) * 100
        
        clases_orden = ["1ª Clase", "2ª Clase", "3ª Clase"]
        clases_presentes = [c for c in clases_orden if c in resumen.index]
        resumen = resumen.reindex(clases_presentes)
        
        colores_sexo = {"Mujer": "#EC4899", "Hombre": "#2563EB"}
        resumen.plot(kind="bar", ax=ax, color=[colores_sexo.get(col, "#64748B") for col in resumen.columns],
                     edgecolor="black", alpha=0.85, width=0.6)
                     
        ax.set_title("Tasa de Supervivencia (%) por Estrato", fontsize=11, fontweight="bold")
        ax.set_ylabel("Supervivencia (%)")
        ax.set_xlabel("")
        ax.set_ylim(0, 105)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.legend(title="Género", frameon=True)
        plt.tight_layout()
        return fig

    @render.plot
    def grafico_tarifa_clase():
        df = filtrar_datos()
        color_primario = input.paleta_color()
        
        fig, ax = plt.subplots(figsize=(6, 4))
        if len(df) == 0:
            ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center", color="gray")
            ax.axis("off")
            return fig
            
        promedios_tarifa = df.groupby("clase_texto")["fare"].mean()
        clases_orden = ["1ª Clase", "2ª Clase", "3ª Clase"]
        clases_presentes = [c for c in clases_orden if c in promedios_tarifa.index]
        valores = [promedios_tarifa[c] for c in clases_presentes]
        
        barras = ax.bar(clases_presentes, valores, color=color_primario, edgecolor="black", alpha=0.8, width=0.5)
        for b, v in zip(barras, valores):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 2, f"${v:.1f}", ha="center", va="bottom", fontweight="bold")
            
        ax.set_ylabel("Tarifa Promedio ($ USD)")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        return fig

    # ---- Gráficas Pestaña 3 ----
    @render.plot
    def grafico_puertos():
        df = filtrar_datos()
        fig, ax = plt.subplots(figsize=(6, 4))
        if len(df) == 0:
            ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center", color="gray")
            ax.axis("off")
            return fig
            
        tasa_puerto = df.groupby("puerto_nombre")["survived"].agg(["count", "mean"]).reset_index()
        tasa_puerto["pct"] = tasa_puerto["mean"] * 100
        
        colores_puerto = ["#0284C7", "#10B981", "#F59E0B", "#94A3B8"]
        barras = ax.bar(tasa_puerto["puerto_nombre"], tasa_puerto["pct"], color=colores_puerto[:len(tasa_puerto)],
                        edgecolor="black", alpha=0.85, width=0.5)
                        
        for b, row in zip(barras, tasa_puerto.itertuples()):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 2,
                    f"{row.pct:.1f}%\n(N={row.count})", ha="center", va="bottom", fontsize=9, fontweight="bold")
                    
        ax.set_ylabel("Tasa de Supervivencia (%)")
        ax.set_ylim(0, 110)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        return fig

    @render.plot
    def grafico_familia():
        df = filtrar_datos()
        color_primario = input.paleta_color()
        
        fig, ax = plt.subplots(figsize=(6, 4))
        if len(df) == 0:
            ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center", color="gray")
            ax.axis("off")
            return fig
            
        resumen_fam = df.groupby("acompaniamiento")["survived"].agg(["count", "mean"]).reset_index()
        resumen_fam["pct"] = resumen_fam["mean"] * 100
        
        barras = ax.bar(resumen_fam["acompaniamiento"], resumen_fam["pct"], color=["#6366F1", color_primario],
                        edgecolor="black", alpha=0.85, width=0.45)
                        
        for b, row in zip(barras, resumen_fam.itertuples()):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 2,
                    f"{row.pct:.1f}%\n(N={row.count})", ha="center", va="bottom", fontsize=9, fontweight="bold")
                    
        ax.set_ylabel("Tasa de Supervivencia (%)")
        ax.set_ylim(0, 110)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        return fig

    # ---- Pestaña 4: Tabla de Datos ----
    @render.data_frame
    def tabla_pasajeros_completa():
        df = filtrar_datos()
        columnas = {
            "clase_texto": "Clase",
            "sexo_texto": "Sexo",
            "edad_redondeada": "Edad",
            "fare": "Tarifa ($)",
            "supervivencia_texto": "Estado",
            "puerto_nombre": "Puerto",
            "acompaniamiento": "Compañía",
        }
        df_mostrar = df[list(columnas.keys())].copy()
        df_mostrar["fare"] = df_mostrar["fare"].round(2)
        df_mostrar["edad_redondeada"] = df_mostrar["edad_redondeada"].round(1)
        df_mostrar = df_mostrar.rename(columns=columnas)
        return render.DataGrid(df_mostrar, filters=True)

    # ---- Descarga de CSV ----
    @render.download(filename=lambda: "pasajeros_titanic_filtrados.csv")
    def descargar_datos():
        df = filtrar_datos()
        yield df.to_csv(index=False, encoding="utf-8-sig")


app = App(app_ui, server)

if __name__ == "__main__":
    app.run(port=8001)
