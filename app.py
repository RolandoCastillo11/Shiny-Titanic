"""
=============================================================================
DASHBOARD INTERACTIVO AVANZADO: ANÁLISIS DE PASAJEROS DEL TITANIC
=============================================================================
Materia: Programación para Ciencia de Datos
Arquitectura: Shiny for Python (PyShiny)
Dataset: Pasajeros del RMS Titanic (891 registros)
Diseño: Espacioso, moderno y responsivo con navegación por pestañas
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

# -----------------------------------------------------------------------------
# 0. Configuración de Matplotlib (Estabilidad en Windows y Estilo Limpio)
# -----------------------------------------------------------------------------
mpl_dir = Path(tempfile.gettempdir()) / "mpl_cache"
mpl_dir.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(mpl_dir)
matplotlib.use("Agg")

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica", "Segoe UI"]
plt.rcParams["axes.edgecolor"] = "#cbd5e1"
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["figure.autolayout"] = True

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
# 2. Estilos CSS Personalizados para Evitar el Amontonamiento
# -----------------------------------------------------------------------------
ESTILOS_CSS = ui.tags.style("""
    body {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
    }
    
    .sidebar {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
        padding: 1.5rem 1.25rem !important;
    }
    
    .card {
        border-radius: 14px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
        margin-bottom: 1.75rem !important;
        background-color: #ffffff;
        overflow: hidden;
    }
    
    .card-header {
        background-color: #f8fafc !important;
        border-bottom: 1px solid #e2e8f0 !important;
        font-weight: 700;
        font-size: 1.02rem;
        color: #0f172a;
        padding: 0.9rem 1.25rem !important;
    }
    
    .card-body {
        padding: 1.25rem !important;
    }
    
    .bslib-value-box {
        border-radius: 14px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        margin-bottom: 1.5rem !important;
        min-height: 110px;
    }
    
    .nav-tabs {
        border-bottom: 2px solid #e2e8f0 !important;
        margin-bottom: 1.5rem !important;
    }
    
    .nav-tabs .nav-link {
        font-weight: 600;
        font-size: 0.96rem;
        color: #64748b;
        padding: 0.8rem 1.35rem !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        transition: all 0.2s ease-in-out;
    }
    
    .nav-tabs .nav-link:hover {
        color: #1d4ed8;
    }
    
    .nav-tabs .nav-link.active {
        color: #1d4ed8 !important;
        background-color: transparent !important;
        border-bottom: 3px solid #1d4ed8 !important;
        font-weight: 700;
    }
    
    .header-titulo {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
""")

# -----------------------------------------------------------------------------
# 3. Interfaz de Usuario (UI) con fillable=False (Permite Scroll Natural)
# -----------------------------------------------------------------------------
app_ui = ui.page_sidebar(
    # --- PANEL LATERAL (SIDEBAR) ---
    ui.sidebar(
        ui.h4("⚙️ Panel de Control", class_="fw-bold text-primary mb-3", style="font-size: 1.15rem;"),
        ui.p("Ajusta los filtros para segmentar la población de pasajeros.", class_="text-muted small mb-4"),
        
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
        
        ui.div(
            ui.input_slider(
                "rango_edad",
                "Rango de Edad (Años):",
                min=0,
                max=80,
                value=[0, 80],
                step=1,
            ),
            class_="mb-3",
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
        
        ui.hr(class_="my-3"),
        
        ui.input_select(
            "paleta_color",
            "Paleta Cromática:",
            {
                "#1D4ED8": "Azul Marino Real",
                "#059669": "Verde Esmeralda",
                "#DC2626": "Rojo Carmesí",
                "#7C3AED": "Púrpura Imperial",
                "#D97706": "Ámbar Dorado",
            },
            selected="#1D4ED8",
        ),
        
        ui.download_button(
            "descargar_datos",
            "📥 Descargar CSV Filtrado",
            class_="btn btn-outline-primary btn-sm w-100 mt-2 fw-semibold",
        ),
        
        width=310,
    ),
    
    # Inyección de estilos CSS
    ESTILOS_CSS,
    
    # --- ENCABEZADO DEL DASHBOARD ---
    ui.div(
        ui.div(
            ui.h3("🚢 Dashboard de Exploración: Pasajeros del Titanic", class_="fw-bold text-dark mb-1"),
            ui.p("Análisis multifactorial de supervivencia, demografía, estratificación social y puertos de embarque.", class_="text-muted mb-0", style="font-size: 0.95rem;"),
        ),
        class_="header-titulo",
    ),
    
    # --- FILA DE INDICADORES (VALUE BOXES) ---
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
        class_="mb-2",
    ),
    
    # --- PESTAÑAS TEMÁTICAS AMPLIAS ---
    ui.navset_card_tab(
        # PESTAÑA 1
        ui.nav_panel(
            "📊 Resumen de Supervivencia y Demografía",
            ui.layout_columns(
                ui.card(
                    ui.card_header("Distribución de Supervivencia (Conteo y Proporción)", class_="fw-bold"),
                    ui.output_plot("grafico_supervivencia_barras", height="380px"),
                ),
                ui.card(
                    ui.card_header("Distribución de Edades por Condición de Desenlace", class_="fw-bold"),
                    ui.output_plot("grafico_distribucion_edad", height="380px"),
                ),
                col_widths=[6, 6],
            ),
        ),
        
        # PESTAÑA 2
        ui.nav_panel(
            "👥 Análisis por Clase y Género",
            ui.layout_columns(
                ui.card(
                    ui.card_header("Tasa de Supervivencia por Estrato y Género", class_="fw-bold"),
                    ui.output_plot("grafico_clase_genero", height="380px"),
                ),
                ui.card(
                    ui.card_header("Tarifa Promedio Pagada según la Clase", class_="fw-bold"),
                    ui.output_plot("grafico_tarifa_clase", height="380px"),
                ),
                col_widths=[6, 6],
            ),
        ),
        
        # PESTAÑA 3
        ui.nav_panel(
            "🗺️ Puertos y Dinámica Familiar",
            ui.layout_columns(
                ui.card(
                    ui.card_header("Supervivencia según Puerto de Embarque", class_="fw-bold"),
                    ui.output_plot("grafico_puertos", height="380px"),
                ),
                ui.card(
                    ui.card_header("Impacto del Acompañamiento Familiar", class_="fw-bold"),
                    ui.output_plot("grafico_familia", height="380px"),
                ),
                col_widths=[6, 6],
            ),
        ),
        
        # PESTAÑA 4
        ui.nav_panel(
            "📋 Explorador de Datos y Métricas",
            ui.card(
                ui.card_header("Registros Filtrados (Exploración Interactiva con Filtros en Línea)", class_="fw-bold"),
                ui.output_data_frame("tabla_pasajeros_completa"),
            ),
        ),
    ),
    
    title="Dashboard Titanic - Shiny",
    fillable=False,  # CRÍTICO: Permite que la página tenga scroll natural y no comprima los componentes
)

# -----------------------------------------------------------------------------
# 4. Lógica del Servidor (Server)
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
        
        fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=100)
        if len(df) == 0:
            ax.text(0.5, 0.5, "No hay pasajeros con los filtros seleccionados", ha="center", va="center", color="#64748b", fontsize=11)
            ax.axis("off")
            return fig
            
        conteo = df["survived"].value_counts().sort_index()
        no_sob = conteo.get(0, 0)
        sob = conteo.get(1, 0)
        
        etiquetas = ["Fallecidos", "Sobrevivientes"]
        valores = [no_sob, sob]
        colores = ["#94A3B8", color_primario]
        
        barras = ax.bar(etiquetas, valores, color=colores, width=0.45, edgecolor="#334155", linewidth=1.2)
        total = len(df)
        for b, v in zip(barras, valores):
            pct = (v / total) * 100 if total > 0 else 0
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + (max(valores) * 0.02 + 1),
                    f"{v} ({pct:.1f}%)", ha="center", va="bottom", fontsize=11, fontweight="bold")
                    
        ax.set_ylabel("Cantidad de Pasajeros", fontsize=10, fontweight="600")
        ax.set_ylim(0, max(valores) * 1.2 if max(valores) > 0 else 10)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        return fig

    @render.plot
    def grafico_distribucion_edad():
        df = filtrar_datos()
        color_primario = input.paleta_color()
        
        fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=100)
        if len(df) == 0:
            ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center", color="#64748b", fontsize=11)
            ax.axis("off")
            return fig
            
        edades_no_sob = df[df["survived"] == 0]["edad_redondeada"]
        edades_sob = df[df["survived"] == 1]["edad_redondeada"]
        
        bins = np.linspace(0, 80, 17)
        ax.hist(edades_no_sob, bins=bins, color="#94A3B8", alpha=0.6, label="Fallecidos", edgecolor="white", linewidth=1)
        ax.hist(edades_sob, bins=bins, color=color_primario, alpha=0.75, label="Sobrevivientes", edgecolor="white", linewidth=1)
        
        ax.set_xlabel("Edad (Años)", fontsize=10, fontweight="600")
        ax.set_ylabel("Frecuencia de Pasajeros", fontsize=10, fontweight="600")
        ax.legend(frameon=True, facecolor="white", edgecolor="#e2e8f0", fontsize=10)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        return fig

    # ---- Gráficas Pestaña 2 ----
    @render.plot
    def grafico_clase_genero():
        df = filtrar_datos()
        fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=100)
        if len(df) == 0:
            ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center", color="#64748b", fontsize=11)
            ax.axis("off")
            return fig
            
        resumen = df.groupby(["clase_texto", "sexo_texto"])["survived"].mean().unstack().fillna(0) * 100
        
        clases_orden = ["1ª Clase", "2ª Clase", "3ª Clase"]
        clases_presentes = [c for c in clases_orden if c in resumen.index]
        resumen = resumen.reindex(clases_presentes)
        
        colores_sexo = {"Mujer": "#EC4899", "Hombre": "#2563EB"}
        resumen.plot(kind="bar", ax=ax, color=[colores_sexo.get(col, "#64748B") for col in resumen.columns],
                     edgecolor="black", alpha=0.85, width=0.55)
                     
        ax.set_ylabel("Tasa de Supervivencia (%)", fontsize=10, fontweight="600")
        ax.set_xlabel("")
        ax.set_ylim(0, 110)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontweight="600")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.legend(title="Género", frameon=True, facecolor="white", edgecolor="#e2e8f0")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        return fig

    @render.plot
    def grafico_tarifa_clase():
        df = filtrar_datos()
        color_primario = input.paleta_color()
        
        fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=100)
        if len(df) == 0:
            ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center", color="#64748b", fontsize=11)
            ax.axis("off")
            return fig
            
        promedios_tarifa = df.groupby("clase_texto")["fare"].mean()
        clases_orden = ["1ª Clase", "2ª Clase", "3ª Clase"]
        clases_presentes = [c for c in clases_orden if c in promedios_tarifa.index]
        valores = [promedios_tarifa[c] for c in clases_presentes]
        
        barras = ax.bar(clases_presentes, valores, color=color_primario, edgecolor="black", alpha=0.85, width=0.45)
        for b, v in zip(barras, valores):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 2, f"${v:.1f}", ha="center", va="bottom", fontweight="bold")
            
        ax.set_ylabel("Tarifa Promedio ($ USD)", fontsize=10, fontweight="600")
        ax.set_xticklabels(clases_presentes, fontweight="600")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        return fig

    # ---- Gráficas Pestaña 3 ----
    @render.plot
    def grafico_puertos():
        df = filtrar_datos()
        fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=100)
        if len(df) == 0:
            ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center", color="#64748b", fontsize=11)
            ax.axis("off")
            return fig
            
        tasa_puerto = df.groupby("puerto_nombre")["survived"].agg(["count", "mean"]).reset_index()
        tasa_puerto["pct"] = tasa_puerto["mean"] * 100
        
        colores_puerto = ["#0284C7", "#10B981", "#F59E0B", "#94A3B8"]
        barras = ax.bar(tasa_puerto["puerto_nombre"], tasa_puerto["pct"], color=colores_puerto[:len(tasa_puerto)],
                        edgecolor="black", alpha=0.85, width=0.45)
                        
        for b, row in zip(barras, tasa_puerto.itertuples()):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 2,
                    f"{row.pct:.1f}%\n(N={row.count})", ha="center", va="bottom", fontsize=9, fontweight="bold")
                    
        ax.set_ylabel("Tasa de Supervivencia (%)", fontsize=10, fontweight="600")
        ax.set_ylim(0, 115)
        ax.set_xticklabels(tasa_puerto["puerto_nombre"], fontweight="600")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        return fig

    @render.plot
    def grafico_familia():
        df = filtrar_datos()
        color_primario = input.paleta_color()
        
        fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=100)
        if len(df) == 0:
            ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center", color="#64748b", fontsize=11)
            ax.axis("off")
            return fig
            
        resumen_fam = df.groupby("acompaniamiento")["survived"].agg(["count", "mean"]).reset_index()
        resumen_fam["pct"] = resumen_fam["mean"] * 100
        
        barras = ax.bar(resumen_fam["acompaniamiento"], resumen_fam["pct"], color=["#6366F1", color_primario],
                        edgecolor="black", alpha=0.85, width=0.42)
                        
        for b, row in zip(barras, resumen_fam.itertuples()):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 2,
                    f"{row.pct:.1f}%\n(N={row.count})", ha="center", va="bottom", fontsize=9, fontweight="bold")
                    
        ax.set_ylabel("Tasa de Supervivencia (%)", fontsize=10, fontweight="600")
        ax.set_ylim(0, 115)
        ax.set_xticklabels(resumen_fam["acompaniamiento"], fontweight="600")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
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
