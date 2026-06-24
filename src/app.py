import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# importamos las funciones que creamos en processing.py
from processing import (
    cargar_datos,
    cargar_comisarias_por_distrito,
    limpiar_datos,
    top_comisarias_por_modalidad,
    ranking_comisarias,
    datos_mapa_comisarias,
    calcular_centro_zoom,
    distancia_promedio_departamento,
)

# importamos la funcion para obtener el clima desde la API
from api_or_scraper import obtener_clima

# importamos las funciones de base de datos
from db import crear_bd, guardar_consulta_clima


# configuracion general de la pagina
st.set_page_config(
    page_title="Monitor de Denuncias Policiales - PNP",
    layout="wide",
    initial_sidebar_state="expanded",
)


# estilos css personalizados para que se vea como la PNP
# usamos los colores verde oscuro (#1a4731) y dorado (#c8a84b)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f5f5f5; }

    .pnp-header {
        background: linear-gradient(135deg, #1a4731 0%, #2d6a4f 60%, #1a4731 100%);
        padding: 0;
        margin: -1rem -1rem 1.5rem -1rem;
        border-bottom: 4px solid #c8a84b;
    }
    .pnp-header-inner {
        display: flex; align-items: center;
        padding: 14px 28px; gap: 20px;
    }
    .pnp-header-logo {
        width: 72px; height: 72px; background: white;
        border-radius: 50%; display: flex; align-items: center;
        justify-content: center; font-size: 32px; flex-shrink: 0;
        border: 3px solid #c8a84b;
    }
    .pnp-header-text { flex: 1; }
    .pnp-header-title {
        color: #ffffff; font-size: 22px; font-weight: 700;
        letter-spacing: 0.5px; line-height: 1.2; margin: 0;
    }
    .pnp-header-subtitle {
        color: #c8a84b; font-size: 13px; font-weight: 500;
        letter-spacing: 1.5px; text-transform: uppercase; margin: 4px 0 0 0;
    }
    .pnp-header-badge {
        background: rgba(200,168,75,0.15); border: 1px solid #c8a84b;
        color: #c8a84b; font-size: 11px; font-weight: 600;
        padding: 4px 12px; border-radius: 20px;
        letter-spacing: 1px; text-transform: uppercase;
    }

    /* ---- SIDEBAR: solo afecta al sidebar, nada mas ---- */
    section[data-testid="stSidebar"] { background: #1a4731 !important; }

    /* texto general del sidebar en verde claro */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] small,
    section[data-testid="stSidebar"] label { color: #e8f5e9 !important; }

    /* titulos del sidebar en dorado */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stSelectbox label { color: #c8a84b !important; font-weight: 600 !important; }

    /* selectboxes del sidebar */
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: #2d6a4f !important; border: 1px solid #c8a84b !important; color: #ffffff !important;
    }

    /* metricas del sidebar (clima) */
    section[data-testid="stSidebar"] [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #c8a84b !important; font-size: 22px !important; font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] [data-testid="metric-container"] label {
        color: #e8f5e9 !important; font-size: 12px !important;
    }

    /* ---- CONTENIDO PRINCIPAL: todo en negro ---- */

    /* metricas KPI - sin prefijo .main para que siempre se aplique */
    /* excluimos las del sidebar con :not para no pisar esas */
    [data-testid="metric-container"]:not(section[data-testid="stSidebar"] [data-testid="metric-container"]) {
        background: #ffffff !important; border: 1px solid #e0e0e0 !important;
        border-left: 4px solid #1a4731 !important; border-radius: 8px !important;
        padding: 16px 20px !important; box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
    }

    /* valor grande de la metrica (el numero) */
    [data-testid="stMetricValue"] div,
    [data-testid="stMetricValue"] {
        color: #1a4731 !important; font-size: 28px !important; font-weight: 700 !important;
    }
    /* sobreescribimos el del sidebar para que quede dorado */
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] div,
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #c8a84b !important; font-size: 22px !important;
    }

    /* etiqueta de la metrica */
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] span,
    [data-testid="stMetricLabel"] {
        color: #333333 !important; font-size: 13px !important;
        font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.5px;
    }
    /* sobreescribimos etiqueta del sidebar */
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] p,
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] span {
        color: #e8f5e9 !important; font-size: 12px !important; text-transform: none;
    }

    /* slider fuera del sidebar */
    .main .stSlider label, .main .stSlider p, .main .stSlider span,
    .stSlider [data-testid="stTickBarMin"], .stSlider [data-testid="stTickBarMax"],
    .stSlider [data-testid="stThumbValue"] { color: #111111 !important; }

    /* text input fuera del sidebar */
    .main .stTextInput label, .main .stTextInput p,
    .main .stTextInput span { color: #111111 !important; }

    /* captions y parrafos del contenido principal */
    .main p { color: #111111 !important; }
    .main span { color: #111111 !important; }
    .main .stCaptionContainer p,
    .main [data-testid="stCaptionContainer"] p { color: #444444 !important; }

    /* selectbox label fuera del sidebar */
    .main .stSelectbox label { color: #111111 !important; }

    /* pestañas */
    .stTabs [data-baseweb="tab-list"] {
        background: #1a4731; border-radius: 8px 8px 0 0;
        padding: 4px 8px 0 8px; gap: 4px;
        border-bottom: 3px solid #c8a84b;
    }
    .stTabs [data-baseweb="tab"] {
        color: #c8d8c8 !important; font-weight: 500; font-size: 14px;
        padding: 10px 22px; border-radius: 6px 6px 0 0;
        border: none !important; background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: #c8a84b !important; color: #1a4731 !important; font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: #ffffff; border: 1px solid #e0e0e0;
        border-top: none; border-radius: 0 0 8px 8px; padding: 24px;
    }

    /* texto dentro de las tabs */
    .stTabs [data-baseweb="tab-panel"] p,
    .stTabs [data-baseweb="tab-panel"] span,
    .stTabs [data-baseweb="tab-panel"] label,
    .stTabs [data-baseweb="tab-panel"] div { color: #111111 !important; }

    /* titulo de cada seccion */
    .section-title {
        color: #1a4731 !important; font-size: 16px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.8px;
        border-left: 4px solid #c8a84b; padding-left: 10px;
        margin: 24px 0 16px 0;
    }

    /* tarjetas de alertas */
    .alerta-card {
        background: #fff8e1; border: 1px solid #c8a84b;
        border-left: 5px solid #e53935; border-radius: 8px;
        padding: 14px 18px; margin-bottom: 10px;
    }
    .alerta-card-titulo {
        color: #b71c1c !important; font-weight: 700; font-size: 15px; margin: 0 0 4px 0;
    }
    .alerta-card-detalle { color: #333333 !important; font-size: 13px; margin: 0; }

    /* boton de descarga */
    .stDownloadButton > button {
        background: #1a4731 !important; color: white !important;
        border: 2px solid #c8a84b !important; border-radius: 6px !important;
        font-weight: 600 !important; padding: 10px 24px !important;
    }
    .stDownloadButton > button:hover {
        background: #c8a84b !important; color: #1a4731 !important;
    }
    hr { border-color: #c8a84b !important; opacity: 0.3; }

    /* tabla de datos (dataframe) */
    .main [data-testid="stDataFrame"] span,
    .main [data-testid="stDataFrame"] p { color: #111111 !important; }
</style>
""", unsafe_allow_html=True)


# header principal con logo y titulo
st.markdown("""
<div class="pnp-header">
  <div class="pnp-header-inner">
    <div class="pnp-header-logo">🚔</div>
    <div class="pnp-header-text">
      <p class="pnp-header-title">Monitor de Denuncias Policiales</p>
      <p class="pnp-header-subtitle">Policía Nacional del Perú · Ministerio del Interior</p>
    </div>
    <div class="pnp-header-badge">2018 – 2026</div>
  </div>
</div>
""", unsafe_allow_html=True)


# colores que usamos en todos los graficos para mantener consistencia
COLORES_PNP = [
    "#1a4731", "#2d6a4f", "#52b788", "#c8a84b", "#e9c46a",
    "#40916c", "#95d5b2", "#b7e4c7", "#d4a017", "#74c69d"
]

# configuracion base para todos los graficos de plotly
# lo pusimos aparte para no repetir esto en cada grafico
CONFIG_GRAFICO = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color="#111111", family="Inter, sans-serif"),
    title_font=dict(color="#1a4731", size=15, family="Inter, sans-serif"),
    legend_font=dict(color="#111111"),
)

# funcion que aplica colores negros a los ejes de cualquier figura
# la usamos despues de update_layout para que no se pierdan los colores
def aplicar_colores_ejes(fig, titulo_x="", titulo_y=""):
    fig.update_xaxes(
        title_text=titulo_x,
        title_font=dict(color="#111111"),
        tickfont=dict(color="#111111")
    )
    fig.update_yaxes(
        title_text=titulo_y,
        title_font=dict(color="#111111"),
        tickfont=dict(color="#111111")
    )
    return fig


# cargamos los datos al inicio
df_crudo = cargar_datos()
df_limpio = limpiar_datos(df_crudo)
comisarias_ref = cargar_comisarias_por_distrito()

# creamos la base de datos si no existe todavia
crear_bd()


# -------------------------------------------------------
# SIDEBAR - filtros
# -------------------------------------------------------

st.sidebar.markdown("## 🔍 Filtros")

# filtro de departamento
lista_dptos = sorted(df_limpio["DPTO_HECHO_NEW"].unique().tolist())
lista_dptos.insert(0, "TODO EL PERÚ")
dpto_sel = st.sidebar.selectbox("Departamento", lista_dptos)

# filtro de distrito (depende del departamento elegido)
if dpto_sel == "TODO EL PERÚ":
    df_para_dist = df_limpio
else:
    df_para_dist = df_limpio[df_limpio["DPTO_HECHO_NEW"] == dpto_sel]

lista_dist = sorted(df_para_dist["DIST_HECHO"].unique().tolist())
lista_dist.insert(0, "TODOS")
dist_sel = st.sidebar.selectbox("Distrito", lista_dist)

# filtro de modalidad de delito
lista_delitos = sorted(df_limpio["P_MODALIDADES"].unique().tolist())
lista_delitos.insert(0, "TODOS")
delito_sel = st.sidebar.selectbox("Modalidad del delito", lista_delitos)

# filtro de año
lista_anios = sorted(df_limpio["ANIO"].unique().tolist())
lista_anios.insert(0, "TODOS")
anio_sel = st.sidebar.selectbox("Año", lista_anios)

# filtro de comisaria (depende del departamento y distrito)
df_para_com = df_limpio.copy()
if dpto_sel != "TODO EL PERÚ":
    df_para_com = df_para_com[df_para_com["DPTO_HECHO_NEW"] == dpto_sel]
if dist_sel != "TODOS":
    df_para_com = df_para_com[df_para_com["DIST_HECHO"] == dist_sel]

lista_com = sorted(df_para_com["COMISARIA_MAS_CERCANA"].unique().tolist())
lista_com.insert(0, "TODAS")
com_sel = st.sidebar.selectbox("Comisaría más cercana", lista_com)


# -------------------------------------------------------
# CLIMA - solo mostramos si eligieron un departamento
# -------------------------------------------------------

if dpto_sel != "TODO EL PERÚ":

    st.sidebar.markdown("---")
    st.sidebar.subheader("🌦 Clima Actual")

    # llamamos a la API de Open-Meteo para obtener el clima
    clima = obtener_clima(dpto_sel)

    if clima:
        st.sidebar.metric("Temperatura", f"{clima['temperatura']} °C")
        st.sidebar.metric("Precipitación", f"{clima['precipitacion']} mm")
        st.sidebar.metric("Viento", f"{clima['viento']} km/h")

        # guardamos la consulta en la base de datos
        guardar_consulta_clima(
            dpto_sel,
            clima["temperatura"],
            clima["precipitacion"],
            clima["viento"]
        )
    else:
        st.sidebar.warning("No se pudo obtener información climática.")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<small style='color:#c8a84b'>Datos: MININTER / PNP · Ene 2018 – Abr 2026</small>",
    unsafe_allow_html=True
)


# -------------------------------------------------------
# APLICAMOS LOS FILTROS AL DATAFRAME
# -------------------------------------------------------

df_filtrado = df_limpio.copy()

if dpto_sel != "TODO EL PERÚ":
    df_filtrado = df_filtrado[df_filtrado["DPTO_HECHO_NEW"] == dpto_sel]

if dist_sel != "TODOS":
    df_filtrado = df_filtrado[df_filtrado["DIST_HECHO"] == dist_sel]

if delito_sel != "TODOS":
    df_filtrado = df_filtrado[df_filtrado["P_MODALIDADES"] == delito_sel]

if anio_sel != "TODOS":
    df_filtrado = df_filtrado[df_filtrado["ANIO"] == anio_sel]

if com_sel != "TODAS":
    df_filtrado = df_filtrado[df_filtrado["COMISARIA_MAS_CERCANA"] == com_sel]


# -------------------------------------------------------
# KPIs - indicadores principales
# -------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_denuncias = int(df_filtrado["cantidad"].sum())
    st.metric("Total de denuncias", f"{total_denuncias:,}")

with col2:
    num_modalidades = df_filtrado["P_MODALIDADES"].nunique()
    st.metric("Modalidades", num_modalidades)

with col3:
    num_dptos = df_filtrado["DPTO_HECHO_NEW"].nunique()
    st.metric("Departamentos", num_dptos)

with col4:
    # distancia promedio ponderada por cantidad de denuncias
    total_cant = df_filtrado["cantidad"].sum()
    if total_cant > 0:
        dist_prom = (df_filtrado["DISTANCIA_KM"] * df_filtrado["cantidad"]).sum() / total_cant
    else:
        dist_prom = 0
    st.metric("Distancia prom. a comisaría", f"{dist_prom:,.2f} km")

st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)


# -------------------------------------------------------
# PESTAÑAS
# -------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Resumen",
    "🏢  Comisarías",
    "🗺️  Mapa",
    "📋  Datos",
])


# =======================================================
# TAB 1 - RESUMEN GENERAL
# =======================================================

with tab1:

    # --- grafico de departamentos con mas y menos denuncias ---
    st.markdown('<p class="section-title">Departamentos con mayor y menor número de denuncias</p>', unsafe_allow_html=True)

    resumen_dptos = df_filtrado.groupby("DPTO_HECHO_NEW")["cantidad"].sum().reset_index()

    top3_mas = resumen_dptos.sort_values("cantidad", ascending=False).head(3)
    top3_menos = resumen_dptos.sort_values("cantidad", ascending=True).head(3)

    col_mas, col_menos = st.columns(2)

    with col_mas:
        fig_mas = px.bar(
            top3_mas,
            x="DPTO_HECHO_NEW",
            y="cantidad",
            title="Top 3 · Más denuncias",
            text="cantidad",
            color_discrete_sequence=["#1a4731"]
        )
        fig_mas.update_traces(textposition="outside", textfont_color="#111111")
        fig_mas.update_layout(**CONFIG_GRAFICO)
        aplicar_colores_ejes(fig_mas, titulo_x="", titulo_y="Denuncias")
        st.plotly_chart(fig_mas, use_container_width=True)

    with col_menos:
        fig_menos = px.bar(
            top3_menos,
            x="DPTO_HECHO_NEW",
            y="cantidad",
            title="Top 3 · Menos denuncias",
            text="cantidad",
            color_discrete_sequence=["#c8a84b"]
        )
        fig_menos.update_traces(textposition="outside", textfont_color="#111111")
        fig_menos.update_layout(**CONFIG_GRAFICO)
        aplicar_colores_ejes(fig_menos, titulo_x="", titulo_y="Denuncias")
        st.plotly_chart(fig_menos, use_container_width=True)

    # --- grafico de participacion de delitos (pie) ---
    st.markdown('<p class="section-title">Participación de delitos</p>', unsafe_allow_html=True)

    top5_delitos = df_filtrado.groupby("P_MODALIDADES")["cantidad"].sum().nlargest(5).reset_index()

    fig_pie = px.pie(
        top5_delitos,
        values="cantidad",
        names="P_MODALIDADES",
        title="Top 5 modalidades de delito",
        color_discrete_sequence=COLORES_PNP
    )
    fig_pie.update_traces(textfont_color="#111111")
    fig_pie.update_layout(**CONFIG_GRAFICO)
    st.plotly_chart(fig_pie, use_container_width=True)

    # --- evolucion anual de denuncias ---
    st.markdown('<p class="section-title">Evolución anual de denuncias</p>', unsafe_allow_html=True)

    evolucion_anual = df_limpio.groupby("ANIO")["cantidad"].sum().reset_index()

    fig_linea = px.line(
        evolucion_anual,
        x="ANIO",
        y="cantidad",
        markers=True,
        title="Evolución 2018–2026",
        color_discrete_sequence=["#1a4731"]
    )
    fig_linea.update_layout(**CONFIG_GRAFICO)
    aplicar_colores_ejes(fig_linea, titulo_x="Año", titulo_y="Denuncias")
    st.plotly_chart(fig_linea, use_container_width=True)

    # --- heatmap de denuncias por mes y año ---
    st.markdown('<p class="section-title">Mapa de calor · Denuncias por mes y año</p>', unsafe_allow_html=True)

    datos_heat = df_filtrado.groupby(["ANIO", "MES"])["cantidad"].sum().reset_index()

    if not datos_heat.empty:
        # pivoteamos para que los meses queden en filas y los años en columnas
        tabla_heat = datos_heat.pivot(index="MES", columns="ANIO", values="cantidad").fillna(0)

        nombres_meses = {
            1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
            5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
            9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
        }
        tabla_heat.index = [nombres_meses.get(m, m) for m in tabla_heat.index]

        fig_heat = go.Figure(data=go.Heatmap(
            z=tabla_heat.values,
            x=[str(c) for c in tabla_heat.columns],
            y=tabla_heat.index,
            colorscale=[[0, "#e8f5e9"], [0.5, "#2d6a4f"], [1, "#1a4731"]],
            text=tabla_heat.values.astype(int),
            texttemplate="%{text:,}",
            textfont={"size": 11, "color": "#111111"},
            hoverongaps=False,
        ))
        fig_heat.update_layout(
            **CONFIG_GRAFICO,
            title="Denuncias por mes y año",
            height=420,
            coloraxis_colorbar=dict(
                tickfont=dict(color="#111111"),
                title=dict(font=dict(color="#111111"))
            )
        )
        aplicar_colores_ejes(fig_heat, titulo_x="Año", titulo_y="Mes")
        st.plotly_chart(fig_heat, use_container_width=True)

    # --- top 10 distritos de lima metropolitana ---
    # esta seccion siempre muestra lima sin importar el filtro de departamento
    st.markdown('<p class="section-title">Top 10 distritos de Lima Metropolitana</p>', unsafe_allow_html=True)

    df_lima = df_limpio[df_limpio["DPTO_HECHO_NEW"] == "LIMA METROPOLITANA"].copy()

    # si hay filtro de año lo aplicamos tambien aqui
    if anio_sel != "TODOS":
        df_lima = df_lima[df_lima["ANIO"] == anio_sel]

    if not df_lima.empty:
        # sacamos los 10 distritos con mas denuncias
        top10_distritos = (
            df_lima.groupby("DIST_HECHO")["cantidad"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .index.tolist()
        )

        df_lima_top10 = df_lima[df_lima["DIST_HECHO"].isin(top10_distritos)]

        datos_lima = (
            df_lima_top10
            .groupby(["DIST_HECHO", "P_MODALIDADES"])["cantidad"]
            .sum()
            .reset_index()
        )

        fig_lima = px.bar(
            datos_lima,
            x="DIST_HECHO",
            y="cantidad",
            color="P_MODALIDADES",
            title="Denuncias por tipo de delito · Top 10 distritos Lima Metropolitana",
            category_orders={"DIST_HECHO": top10_distritos},
            color_discrete_sequence=COLORES_PNP
        )
        fig_lima.update_layout(
            **CONFIG_GRAFICO,
            barmode="stack",
            legend_title="Modalidad",
            height=550
        )
        aplicar_colores_ejes(fig_lima, titulo_x="Distrito", titulo_y="Denuncias")
        st.plotly_chart(fig_lima, use_container_width=True)
        st.markdown(
            "<p style='color:#444444 !important; font-size:13px;'>Vista fija en Lima Metropolitana. "
            "No se ve afectada por el filtro de Departamento ni Modalidad.</p>",
            unsafe_allow_html=True
        )

    # --- alertas de variacion de denuncias ---
    # corregido: antes mostraba solo caidas porque 2026 esta incompleto
    # ahora filtramos solo años con los 12 meses y separamos subidas de caidas
    st.markdown('<p class="section-title">🚨 Alertas · Distritos con mayor variación de denuncias</p>', unsafe_allow_html=True)

    todos_los_anios = sorted(df_limpio["ANIO"].unique().tolist())

    if len(todos_los_anios) >= 2:

        # solo comparamos años que tengan los 12 meses completos
        anios_completos = []
        for a in todos_los_anios:
            meses_en_anio = df_limpio[df_limpio["ANIO"] == a]["MES"].nunique()
            if meses_en_anio == 12:
                anios_completos.append(a)

        if len(anios_completos) < 2:
            st.warning("No hay suficientes años completos para comparar.")
        else:
            anio_anterior = anios_completos[-2]
            anio_reciente = anios_completos[-1]

            # agrupamos denuncias por distrito para cada año
            den_anio_ant = (
                df_limpio[df_limpio["ANIO"] == anio_anterior]
                .groupby(["DPTO_HECHO_NEW", "DIST_HECHO"])["cantidad"]
                .sum()
                .reset_index()
                .rename(columns={"cantidad": "cant_anterior"})
            )

            den_anio_rec = (
                df_limpio[df_limpio["ANIO"] == anio_reciente]
                .groupby(["DPTO_HECHO_NEW", "DIST_HECHO"])["cantidad"]
                .sum()
                .reset_index()
                .rename(columns={"cantidad": "cant_reciente"})
            )

            # unimos los dos dataframes
            df_variacion = den_anio_ant.merge(
                den_anio_rec,
                on=["DPTO_HECHO_NEW", "DIST_HECHO"],
                how="inner"
            )

            # calculamos el porcentaje de variacion
            df_variacion["variacion_pct"] = (
                (df_variacion["cant_reciente"] - df_variacion["cant_anterior"])
                / df_variacion["cant_anterior"] * 100
            ).round(1)

            # filtramos distritos con poca actividad para evitar ruido
            df_variacion = df_variacion[df_variacion["cant_anterior"] >= 50]

            # separamos los que subieron y los que bajaron
            df_subida = df_variacion[df_variacion["variacion_pct"] > 0].sort_values(
                "variacion_pct", ascending=False
            ).head(5)

            df_caida = df_variacion[df_variacion["variacion_pct"] < 0].sort_values(
                "variacion_pct", ascending=True
            ).head(5)

            # subtitulo explicativo
            st.markdown(
                f"<p style='color:#1a4731 !important; font-size:14px; margin-bottom:12px;'>"
                f"Comparando <b>{anio_anterior}</b> vs <b>{anio_reciente}</b> "
                f"(distritos con al menos 50 denuncias en {anio_anterior})</p>",
                unsafe_allow_html=True
            )

            col_subida, col_caida = st.columns(2)

            with col_subida:
                st.markdown(
                    "<p style='color:#1a4731 !important; font-weight:700; font-size:14px;'>▲ Mayor crecimiento</p>",
                    unsafe_allow_html=True
                )
                if df_subida.empty:
                    st.info("No hubo distritos con aumento.")
                else:
                    for _, fila in df_subida.iterrows():
                        st.markdown(f"""
                        <div class="alerta-card" style="border-left-color:#1a4731;">
                            <p class="alerta-card-titulo" style="color:#1a4731 !important;">
                                ▲ {fila['DIST_HECHO']} ({fila['DPTO_HECHO_NEW']})
                            </p>
                            <p class="alerta-card-detalle" style="color:#333333 !important;">
                                {anio_anterior}: <b>{int(fila['cant_anterior']):,}</b> →
                                {anio_reciente}: <b>{int(fila['cant_reciente']):,}</b> &nbsp;|&nbsp;
                                <span style='color:#1a4731 !important; font-weight:700'>{fila['variacion_pct']:+.1f}%</span>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

            with col_caida:
                st.markdown(
                    "<p style='color:#b71c1c !important; font-weight:700; font-size:14px;'>▼ Mayor caída</p>",
                    unsafe_allow_html=True
                )
                if df_caida.empty:
                    st.info("No hubo distritos con caída.")
                else:
                    for _, fila in df_caida.iterrows():
                        st.markdown(f"""
                        <div class="alerta-card">
                            <p class="alerta-card-titulo" style="color:#b71c1c !important;">
                                ▼ {fila['DIST_HECHO']} ({fila['DPTO_HECHO_NEW']})
                            </p>
                            <p class="alerta-card-detalle" style="color:#333333 !important;">
                                {anio_anterior}: <b>{int(fila['cant_anterior']):,}</b> →
                                {anio_reciente}: <b>{int(fila['cant_reciente']):,}</b> &nbsp;|&nbsp;
                                <span style='color:#b71c1c !important; font-weight:700'>{fila['variacion_pct']:+.1f}%</span>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

    # --- comparador de dos zonas ---
    st.markdown('<p class="section-title">🔁 Comparador de zonas</p>', unsafe_allow_html=True)

    lista_zonas = sorted(df_limpio["DPTO_HECHO_NEW"].unique().tolist())

    col_zona1, col_zona2 = st.columns(2)
    with col_zona1:
        zona_a = st.selectbox("Zona A", lista_zonas, key="zona1")
    with col_zona2:
        zona_b = st.selectbox("Zona B", lista_zonas, index=min(1, len(lista_zonas) - 1), key="zona2")

    if zona_a and zona_b:

        # funcion auxiliar para sacar la serie de un departamento
        def get_serie_zona(nombre_zona):
            df_zona = df_limpio[df_limpio["DPTO_HECHO_NEW"] == nombre_zona]
            serie = df_zona.groupby("ANIO")["cantidad"].sum().reset_index()
            serie["zona"] = nombre_zona
            return serie

        df_comparacion = pd.concat([get_serie_zona(zona_a), get_serie_zona(zona_b)])

        fig_comp = px.line(
            df_comparacion,
            x="ANIO",
            y="cantidad",
            color="zona",
            markers=True,
            title=f"Evolución comparada: {zona_a} vs {zona_b}",
            color_discrete_sequence=["#1a4731", "#c8a84b"],
            labels={"ANIO": "Año", "cantidad": "Denuncias", "zona": "Zona"}
        )
        fig_comp.update_layout(**CONFIG_GRAFICO)
        aplicar_colores_ejes(fig_comp, titulo_x="Año", titulo_y="Denuncias")
        st.plotly_chart(fig_comp, use_container_width=True)

        # tabla resumen de la comparacion
        tabla_comp = df_comparacion.pivot(
            index="ANIO", columns="zona", values="cantidad"
        ).fillna(0).astype(int)
        tabla_comp.columns.name = None
        tabla_comp.index.name = "Año"
        st.dataframe(tabla_comp, use_container_width=True)


# =======================================================
# TAB 2 - COMISARIAS
# =======================================================

with tab2:

    # --- top 10 comisarias por modalidad de delito ---
    st.markdown('<p class="section-title">Top 10 comisarías con más denuncias por modalidad</p>', unsafe_allow_html=True)

    datos_top_com, orden_com = top_comisarias_por_modalidad(df_filtrado, comisarias_ref, top_n=10)

    if datos_top_com.empty:
        st.info("No hay datos de comisarías para los filtros seleccionados.")
    else:
        fig_top_com = px.bar(
            datos_top_com,
            x="COMISARIA",
            y="cantidad_repartida",
            color="P_MODALIDADES",
            title="Top 10 comisarías con más denuncias estimadas, por modalidad",
            category_orders={"COMISARIA": orden_com},
            color_discrete_sequence=COLORES_PNP
        )
        fig_top_com.update_layout(
            **CONFIG_GRAFICO,
            barmode="stack",
            legend_title="Modalidad"
        )
        aplicar_colores_ejes(fig_top_com, titulo_x="Comisaría", titulo_y="Denuncias estimadas")
        st.plotly_chart(fig_top_com, use_container_width=True)
        st.markdown(
            "<p style='color:#444444 !important; font-size:13px;'>Denuncias repartidas proporcionalmente "
            "según número de sectores administrativos (dato oficial PNP).</p>",
            unsafe_allow_html=True
        )

    # --- ranking de comisarias con slider ---
    st.markdown('<p class="section-title">Ranking de comisarías</p>', unsafe_allow_html=True)

    cuantas_comisarias = st.slider("Cantidad de comisarías a mostrar", 5, 30, 15, 5)

    df_ranking = ranking_comisarias(df_filtrado, comisarias_ref, top_n=cuantas_comisarias)

    if df_ranking.empty:
        st.info("No hay datos de comisarías para los filtros seleccionados.")
    else:
        fig_ranking = px.bar(
            df_ranking,
            x="total_denuncias_estimado",
            y="COMISARIA",
            orientation="h",
            title=f"Top {cuantas_comisarias} comisarías con más denuncias estimadas",
            text="total_denuncias_estimado",
            hover_data=["DEPTO_COMISARIA", "PROV_COMISARIA", "DIST_COMISARIA"],
            color_discrete_sequence=["#1a4731"]
        )
        fig_ranking.update_traces(textfont_color="#111111")
        fig_ranking.update_layout(**CONFIG_GRAFICO, height=500)
        aplicar_colores_ejes(fig_ranking, titulo_x="Denuncias estimadas", titulo_y="")
        fig_ranking.update_yaxes(categoryorder="total ascending", tickfont=dict(color="#111111"))
        st.plotly_chart(fig_ranking, use_container_width=True)
        st.dataframe(df_ranking, use_container_width=True)

    # --- distancia promedio por departamento ---
    st.markdown('<p class="section-title">Distancia promedio denuncia–comisaría por departamento</p>', unsafe_allow_html=True)

    df_distancias = distancia_promedio_departamento(df_filtrado)

    if df_distancias.empty:
        st.info("No hay datos suficientes para calcular la distancia promedio.")
    else:
        fig_dist = px.bar(
            df_distancias,
            x="distancia_promedio_km",
            y="DPTO_HECHO_NEW",
            orientation="h",
            title="Distancia promedio (km) entre el distrito del hecho y su comisaría más cercana",
            text="distancia_promedio_km",
            hover_data=["cantidad_total"],
            color_discrete_sequence=["#c8a84b"]
        )
        fig_dist.update_traces(textfont_color="#111111")
        fig_dist.update_layout(**CONFIG_GRAFICO, height=700)
        aplicar_colores_ejes(fig_dist, titulo_x="Distancia promedio (km)", titulo_y="")
        fig_dist.update_yaxes(categoryorder="total ascending", tickfont=dict(color="#111111"))
        st.plotly_chart(fig_dist, use_container_width=True)


# =======================================================
# TAB 3 - MAPA
# =======================================================

with tab3:

    st.markdown('<p class="section-title">Mapa de comisarías y concentración de denuncias</p>', unsafe_allow_html=True)

    df_mapa = datos_mapa_comisarias(df_filtrado, comisarias_ref)

    if df_mapa.empty:
        st.info("No hay datos de comisarías para los filtros seleccionados.")
    else:
        centro_mapa, zoom_mapa = calcular_centro_zoom(df_mapa)

        fig_mapa = px.scatter_mapbox(
            df_mapa,
            lat="LAT",
            lon="LONG",
            size="total_denuncias",
            color="total_denuncias",
            hover_name="COMISARIA",
            hover_data={
                "DEPTO_COMISARIA": True,
                "PROV_COMISARIA": True,
                "DIST_COMISARIA": True,
                "total_denuncias": True,
                "LAT": False,
                "LONG": False
            },
            color_continuous_scale=[[0, "#c8e6c9"], [0.5, "#2d6a4f"], [1, "#1a4731"]],
            size_max=40,
            zoom=zoom_mapa,
            center=centro_mapa,
            title="Concentración de denuncias estimadas por comisaría"
        )
        fig_mapa.update_layout(
            mapbox_style="open-street-map",
            height=680,
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            title_font=dict(color="#1a4731"),
            font=dict(color="#111111"),
        )
        st.plotly_chart(fig_mapa, use_container_width=True)

        if dist_sel != "TODOS" and len(df_mapa) > 1:
            st.markdown(
                f"<p style='color:#444444 !important; font-size:13px;'>📍 El distrito <b>{dist_sel}</b> "
                f"tiene <b>{len(df_mapa)} comisarías reales</b> según el registro oficial de la PNP.</p>",
                unsafe_allow_html=True
            )


# =======================================================
# TAB 4 - DATOS Y DESCARGA
# =======================================================

with tab4:

    # buscador por modalidad
    st.markdown('<p class="section-title">Buscar por modalidad de delito</p>', unsafe_allow_html=True)

    texto_busqueda = st.text_input(
        "Ingrese una modalidad de delito",
        placeholder="Ej: robo, hurto, violencia..."
    )

    # filtramos si escribieron algo
    if texto_busqueda:
        df_tabla = df_filtrado[
            df_filtrado["P_MODALIDADES"].str.contains(texto_busqueda, case=False, na=False)
        ]
    else:
        df_tabla = df_filtrado

    # tabla de datos
    st.markdown(
        f'<p class="section-title">Tabla de datos · {len(df_tabla):,} registros</p>',
        unsafe_allow_html=True
    )
    st.dataframe(df_tabla, use_container_width=True, height=450)

    # boton para descargar los datos filtrados
    st.markdown('<p class="section-title">Descargar datos filtrados</p>', unsafe_allow_html=True)

    datos_csv = df_tabla.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️  Descargar CSV",
        data=datos_csv,
        file_name="denuncias_filtradas.csv",
        mime="text/csv"
    )
