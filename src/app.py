import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
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

# ── Configuración de la página ──────────────────────────────────────────────
st.set_page_config(
    page_title="Monitor de Denuncias Policiales - PNP",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos PNP ─────────────────────────────────────────────────────────────
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

    section[data-testid="stSidebar"] { background: #1a4731 !important; }
    section[data-testid="stSidebar"] * { color: #e8f5e9 !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #c8a84b !important; font-weight: 600 !important; }
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: #2d6a4f !important; border: 1px solid #c8a84b !important; color: #ffffff !important;
    }

    [data-testid="metric-container"] {
        background: #ffffff; border: 1px solid #e0e0e0;
        border-left: 4px solid #1a4731; border-radius: 8px;
        padding: 16px 20px !important; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    [data-testid="metric-container"] label {
        color: #333 !important; font-size: 13px !important;
        font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.5px;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #1a4731 !important; font-size: 28px !important; font-weight: 700 !important;
    }

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

    .section-title {
        color: #1a4731; font-size: 16px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.8px;
        border-left: 4px solid #c8a84b; padding-left: 10px;
        margin: 24px 0 16px 0;
    }

    .alerta-card {
        background: #fff8e1; border: 1px solid #c8a84b;
        border-left: 5px solid #e53935; border-radius: 8px;
        padding: 14px 18px; margin-bottom: 10px;
    }
    .alerta-card-titulo {
        color: #b71c1c; font-weight: 700; font-size: 15px; margin: 0 0 4px 0;
    }
    .alerta-card-detalle { color: #333; font-size: 13px; margin: 0; }

    .stDownloadButton > button {
        background: #1a4731 !important; color: white !important;
        border: 2px solid #c8a84b !important; border-radius: 6px !important;
        font-weight: 600 !important; padding: 10px 24px !important;
    }
    .stDownloadButton > button:hover {
        background: #c8a84b !important; color: #1a4731 !important;
    }
    hr { border-color: #c8a84b !important; opacity: 0.3; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
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

# ── Layout base de gráficos (texto negro) ─────────────────────────────────────
LAYOUT_BASE = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color="#111111", family="Inter, sans-serif"),
    title_font=dict(color="#1a4731", size=15, family="Inter, sans-serif"),
    legend_font=dict(color="#111111"),
    xaxis=dict(title_font=dict(color="#111111"), tickfont=dict(color="#111111")),
    yaxis=dict(title_font=dict(color="#111111"), tickfont=dict(color="#111111")),
)

COLOR_PNP = ["#1a4731","#2d6a4f","#52b788","#c8a84b","#e9c46a",
             "#40916c","#95d5b2","#b7e4c7","#d4a017","#74c69d"]

# ── Carga de datos ────────────────────────────────────────────────────────────
df_crudo = cargar_datos()
df_limpio = limpiar_datos(df_crudo)
comisarias_ref = cargar_comisarias_por_distrito()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🔍 Filtros")

lista_dptos = sorted(df_limpio["DPTO_HECHO_NEW"].unique().tolist())
lista_dptos.insert(0, "TODO EL PERÚ")
dpto_sel = st.sidebar.selectbox("Departamento", lista_dptos)

df_para_dist = df_limpio if dpto_sel == "TODO EL PERÚ" else df_limpio[df_limpio["DPTO_HECHO_NEW"] == dpto_sel]
lista_dist = sorted(df_para_dist["DIST_HECHO"].unique().tolist())
lista_dist.insert(0, "TODOS")
dist_sel = st.sidebar.selectbox("Distrito", lista_dist)

lista_delitos = sorted(df_limpio["P_MODALIDADES"].unique().tolist())
lista_delitos.insert(0, "TODOS")
delito_sel = st.sidebar.selectbox("Modalidad del delito", lista_delitos)

lista_anios = sorted(df_limpio["ANIO"].unique().tolist())
lista_anios.insert(0, "TODOS")
anio_sel = st.sidebar.selectbox("Año", lista_anios)

df_para_com = df_limpio.copy()
if dpto_sel != "TODO EL PERÚ":
    df_para_com = df_para_com[df_para_com["DPTO_HECHO_NEW"] == dpto_sel]
if dist_sel != "TODOS":
    df_para_com = df_para_com[df_para_com["DIST_HECHO"] == dist_sel]
lista_com = sorted(df_para_com["COMISARIA_MAS_CERCANA"].unique().tolist())
lista_com.insert(0, "TODAS")
com_sel = st.sidebar.selectbox("Comisaría más cercana", lista_com)

st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#c8a84b'>Datos: MININTER / PNP · Ene 2018 – Abr 2026</small>", unsafe_allow_html=True)

# ── Filtrado ──────────────────────────────────────────────────────────────────
df_f = df_limpio.copy()
if dpto_sel != "TODO EL PERÚ":
    df_f = df_f[df_f["DPTO_HECHO_NEW"] == dpto_sel]
if dist_sel != "TODOS":
    df_f = df_f[df_f["DIST_HECHO"] == dist_sel]
if delito_sel != "TODOS":
    df_f = df_f[df_f["P_MODALIDADES"] == delito_sel]
if anio_sel != "TODOS":
    df_f = df_f[df_f["ANIO"] == anio_sel]
if com_sel != "TODAS":
    df_f = df_f[df_f["COMISARIA_MAS_CERCANA"] == com_sel]

# ── Indicadores ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total de denuncias", f"{int(df_f['cantidad'].sum()):,}")
with c2:
    st.metric("Modalidades", df_f["P_MODALIDADES"].nunique())
with c3:
    st.metric("Departamentos", df_f["DPTO_HECHO_NEW"].nunique())
with c4:
    dist_prom = (
        (df_f["DISTANCIA_KM"] * df_f["cantidad"]).sum() / df_f["cantidad"].sum()
        if df_f["cantidad"].sum() > 0 else 0
    )
    st.metric("Distancia prom. a comisaría", f"{dist_prom:,.2f} km")

st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PESTAÑAS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Resumen",
    "🏢  Comisarías",
    "🗺️  Mapa",
    "📋  Datos",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 · RESUMEN
# ─────────────────────────────────────────────────────────────────────────────
with tab1:

    # -- Departamentos más / menos denuncias
    st.markdown('<p class="section-title">Departamentos con mayor y menor número de denuncias</p>', unsafe_allow_html=True)
    res_dptos = df_f.groupby("DPTO_HECHO_NEW")["cantidad"].sum().reset_index()
    top3 = res_dptos.sort_values("cantidad", ascending=False).head(3)
    bot3 = res_dptos.sort_values("cantidad", ascending=True).head(3)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(top3, x="DPTO_HECHO_NEW", y="cantidad",
                     title="Top 3 · Más denuncias", text="cantidad",
                     color_discrete_sequence=["#1a4731"])
        fig.update_traces(textposition="outside", textfont_color="#111111")
        fig.update_layout(**LAYOUT_BASE, xaxis_title="", yaxis_title="Denuncias")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(bot3, x="DPTO_HECHO_NEW", y="cantidad",
                     title="Top 3 · Menos denuncias", text="cantidad",
                     color_discrete_sequence=["#c8a84b"])
        fig.update_traces(textposition="outside", textfont_color="#111111")
        fig.update_layout(**LAYOUT_BASE, xaxis_title="", yaxis_title="Denuncias")
        st.plotly_chart(fig, use_container_width=True)

    # -- Participación de delitos
    st.markdown('<p class="section-title">Participación de delitos</p>', unsafe_allow_html=True)
    top5 = df_f.groupby("P_MODALIDADES")["cantidad"].sum().nlargest(5).reset_index()
    fig3 = px.pie(top5, values="cantidad", names="P_MODALIDADES",
                  title="Top 5 modalidades de delito",
                  color_discrete_sequence=COLOR_PNP)
    fig3.update_traces(textfont_color="#111111")
    fig3.update_layout(**{k: v for k, v in LAYOUT_BASE.items() if k not in ("xaxis","yaxis")})
    st.plotly_chart(fig3, use_container_width=True)

    # -- Evolución anual
    st.markdown('<p class="section-title">Evolución anual de denuncias</p>', unsafe_allow_html=True)
    evolucion = df_limpio.groupby("ANIO")["cantidad"].sum().reset_index()
    fig4 = px.line(evolucion, x="ANIO", y="cantidad", markers=True,
                   title="Evolución 2018–2026",
                   color_discrete_sequence=["#1a4731"])
    fig4.update_layout(**LAYOUT_BASE, xaxis_title="Año", yaxis_title="Denuncias")
    st.plotly_chart(fig4, use_container_width=True)

    # -- Heatmap: delitos por mes y año
    st.markdown('<p class="section-title">Mapa de calor · Denuncias por mes y año</p>', unsafe_allow_html=True)
    heat_data = (
        df_f.groupby(["ANIO", "MES"])["cantidad"]
        .sum().reset_index()
    )
    if not heat_data.empty:
        heat_pivot = heat_data.pivot(index="MES", columns="ANIO", values="cantidad").fillna(0)
        meses = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
                 7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
        heat_pivot.index = [meses.get(m, m) for m in heat_pivot.index]
        fig_heat = go.Figure(data=go.Heatmap(
            z=heat_pivot.values,
            x=[str(c) for c in heat_pivot.columns],
            y=heat_pivot.index,
            colorscale=[[0,"#e8f5e9"],[0.5,"#2d6a4f"],[1,"#1a4731"]],
            text=heat_pivot.values.astype(int),
            texttemplate="%{text:,}",
            textfont={"size":11, "color":"#111111"},
            hoverongaps=False,
        ))
        fig_heat.update_layout(
            **{k: v for k, v in LAYOUT_BASE.items() if k not in ("xaxis","yaxis")},
            title="Denuncias por mes y año",
            xaxis=dict(title="Año", tickfont=dict(color="#111111")),
            yaxis=dict(title="Mes", tickfont=dict(color="#111111")),
            height=420,
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # -- Lima top 10
    st.markdown('<p class="section-title">Top 10 distritos de Lima Metropolitana</p>', unsafe_allow_html=True)
    lima_df = df_limpio[df_limpio["DPTO_HECHO_NEW"] == "LIMA METROPOLITANA"].copy()
    if anio_sel != "TODOS":
        lima_df = lima_df[lima_df["ANIO"] == anio_sel]
    if not lima_df.empty:
        top10_dist = (
            lima_df.groupby("DIST_HECHO")["cantidad"]
            .sum().sort_values(ascending=False).head(10).index.tolist()
        )
        datos_ap = (
            lima_df[lima_df["DIST_HECHO"].isin(top10_dist)]
            .groupby(["DIST_HECHO","P_MODALIDADES"])["cantidad"].sum().reset_index()
        )
        fig5 = px.bar(datos_ap, x="DIST_HECHO", y="cantidad", color="P_MODALIDADES",
                      title="Denuncias por tipo de delito · Top 10 distritos Lima Metropolitana",
                      category_orders={"DIST_HECHO": top10_dist},
                      color_discrete_sequence=COLOR_PNP)
        fig5.update_layout(**LAYOUT_BASE, barmode="stack",
                           xaxis_title="Distrito", yaxis_title="Denuncias",
                           legend_title="Modalidad", height=550)
        st.plotly_chart(fig5, use_container_width=True)
        st.caption("Vista fija en Lima Metropolitana. No se ve afectada por el filtro de Departamento ni Modalidad.")

    # -- ALERTAS: distritos con mayor crecimiento
    st.markdown('<p class="section-title">🚨 Alertas · Distritos con mayor crecimiento de denuncias</p>', unsafe_allow_html=True)
    anios_disp = sorted(df_limpio["ANIO"].unique().tolist())
    if len(anios_disp) >= 2:
        anio_ant = anios_disp[-2]
        anio_rec = anios_disp[-1]
        den_ant = (
            df_limpio[df_limpio["ANIO"] == anio_ant]
            .groupby(["DPTO_HECHO_NEW","DIST_HECHO"])["cantidad"].sum()
            .reset_index().rename(columns={"cantidad":"cant_ant"})
        )
        den_rec = (
            df_limpio[df_limpio["ANIO"] == anio_rec]
            .groupby(["DPTO_HECHO_NEW","DIST_HECHO"])["cantidad"].sum()
            .reset_index().rename(columns={"cantidad":"cant_rec"})
        )
        crecimiento = den_ant.merge(den_rec, on=["DPTO_HECHO_NEW","DIST_HECHO"], how="inner")
        crecimiento["variacion_pct"] = (
            (crecimiento["cant_rec"] - crecimiento["cant_ant"]) / crecimiento["cant_ant"] * 100
        ).round(1)
        crecimiento = crecimiento[crecimiento["cant_ant"] >= 50]
        top_alertas = crecimiento.sort_values("variacion_pct", ascending=False).head(5)

        st.markdown(f"Comparando **{anio_ant}** vs **{anio_rec}** (distritos con al menos 50 denuncias en {anio_ant}):")
        for _, row in top_alertas.iterrows():
            signo = "▲" if row["variacion_pct"] > 0 else "▼"
            color = "#b71c1c" if row["variacion_pct"] > 0 else "#1a4731"
            st.markdown(f"""
            <div class="alerta-card">
                <p class="alerta-card-titulo">{signo} {row['DIST_HECHO']} ({row['DPTO_HECHO_NEW']})</p>
                <p class="alerta-card-detalle">
                    Denuncias {anio_ant}: <b>{int(row['cant_ant']):,}</b> →
                    {anio_rec}: <b>{int(row['cant_rec']):,}</b> &nbsp;|&nbsp;
                    <span style='color:{color};font-weight:700'>{row['variacion_pct']:+.1f}%</span>
                </p>
            </div>
            """, unsafe_allow_html=True)

    # -- COMPARADOR de dos zonas
    st.markdown('<p class="section-title">🔁 Comparador de zonas</p>', unsafe_allow_html=True)
    lista_zonas = sorted(df_limpio["DPTO_HECHO_NEW"].unique().tolist())
    cc1, cc2 = st.columns(2)
    with cc1:
        zona1 = st.selectbox("Zona A", lista_zonas, key="zona1")
    with cc2:
        zona2 = st.selectbox("Zona B", lista_zonas,
                             index=min(1, len(lista_zonas)-1), key="zona2")

    if zona1 and zona2:
        def serie_zona(zona):
            return (
                df_limpio[df_limpio["DPTO_HECHO_NEW"] == zona]
                .groupby("ANIO")["cantidad"].sum().reset_index()
                .assign(zona=zona)
            )
        comp_df = pd.concat([serie_zona(zona1), serie_zona(zona2)])
        fig_comp = px.line(comp_df, x="ANIO", y="cantidad", color="zona",
                           markers=True,
                           title=f"Evolución comparada: {zona1} vs {zona2}",
                           color_discrete_sequence=["#1a4731","#c8a84b"],
                           labels={"ANIO":"Año","cantidad":"Denuncias","zona":"Zona"})
        fig_comp.update_layout(**LAYOUT_BASE)
        st.plotly_chart(fig_comp, use_container_width=True)

        # Tabla resumen comparativo
        resumen_comp = comp_df.pivot(index="ANIO", columns="zona", values="cantidad").fillna(0).astype(int)
        resumen_comp.columns.name = None
        resumen_comp.index.name = "Año"
        st.dataframe(resumen_comp, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 · COMISARÍAS
# ─────────────────────────────────────────────────────────────────────────────
with tab2:

    st.markdown('<p class="section-title">Top 10 comisarías con más denuncias por modalidad</p>', unsafe_allow_html=True)
    datos_top, orden_com = top_comisarias_por_modalidad(df_f, comisarias_ref, top_n=10)
    if datos_top.empty:
        st.info("No hay datos de comisarías para los filtros seleccionados.")
    else:
        fig1 = px.bar(datos_top, x="COMISARIA", y="cantidad_repartida",
                      color="P_MODALIDADES",
                      title="Top 10 comisarías con más denuncias estimadas, por modalidad",
                      category_orders={"COMISARIA": orden_com},
                      color_discrete_sequence=COLOR_PNP)
        fig1.update_layout(**LAYOUT_BASE, barmode="stack",
                           xaxis_title="Comisaría", yaxis_title="Denuncias estimadas",
                           legend_title="Modalidad")
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("Denuncias repartidas proporcionalmente según número de sectores administrativos (dato oficial PNP).")

    st.markdown('<p class="section-title">Ranking de comisarías</p>', unsafe_allow_html=True)
    top_n = st.slider("Cantidad de comisarías a mostrar", 5, 30, 15, 5)
    ranking = ranking_comisarias(df_f, comisarias_ref, top_n=top_n)
    if ranking.empty:
        st.info("No hay datos de comisarías para los filtros seleccionados.")
    else:
        fig_rank = px.bar(ranking,
                          x="total_denuncias_estimado", y="COMISARIA",
                          orientation="h",
                          title=f"Top {top_n} comisarías con más denuncias estimadas",
                          text="total_denuncias_estimado",
                          hover_data=["DEPTO_COMISARIA","PROV_COMISARIA","DIST_COMISARIA"],
                          color_discrete_sequence=["#1a4731"])
        fig_rank.update_traces(textfont_color="#111111")
        fig_rank.update_layout(**LAYOUT_BASE, height=500)
        fig_rank.update_yaxes(categoryorder="total ascending", tickfont=dict(color="#111111"))
        st.plotly_chart(fig_rank, use_container_width=True)
        st.dataframe(ranking, use_container_width=True)

    st.markdown('<p class="section-title">Distancia promedio denuncia–comisaría por departamento</p>', unsafe_allow_html=True)
    distancias = distancia_promedio_departamento(df_f)
    if distancias.empty:
        st.info("No hay datos suficientes para calcular la distancia promedio.")
    else:
        fig_dist = px.bar(distancias,
                          x="distancia_promedio_km", y="DPTO_HECHO_NEW",
                          orientation="h",
                          title="Distancia promedio (km) entre el distrito del hecho y su comisaría más cercana",
                          text="distancia_promedio_km",
                          hover_data=["cantidad_total"],
                          color_discrete_sequence=["#c8a84b"])
        fig_dist.update_traces(textfont_color="#111111")
        fig_dist.update_layout(**LAYOUT_BASE, height=700)
        fig_dist.update_yaxes(categoryorder="total ascending", tickfont=dict(color="#111111"))
        st.plotly_chart(fig_dist, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 · MAPA
# ─────────────────────────────────────────────────────────────────────────────
with tab3:

    st.markdown('<p class="section-title">Mapa de comisarías y concentración de denuncias</p>', unsafe_allow_html=True)
    datos_mapa = datos_mapa_comisarias(df_f, comisarias_ref)
    if datos_mapa.empty:
        st.info("No hay datos de comisarías para los filtros seleccionados.")
    else:
        centro_mapa, zoom_mapa = calcular_centro_zoom(datos_mapa)
        fig_mapa = px.scatter_mapbox(
            datos_mapa, lat="LAT", lon="LONG",
            size="total_denuncias", color="total_denuncias",
            hover_name="COMISARIA",
            hover_data={"DEPTO_COMISARIA":True,"PROV_COMISARIA":True,
                        "DIST_COMISARIA":True,"total_denuncias":True,
                        "LAT":False,"LONG":False},
            color_continuous_scale=[[0,"#c8e6c9"],[0.5,"#2d6a4f"],[1,"#1a4731"]],
            size_max=40, zoom=zoom_mapa, center=centro_mapa,
            title="Concentración de denuncias estimadas por comisaría"
        )
        fig_mapa.update_layout(
            mapbox_style="open-street-map", height=680,
            margin={"r":0,"t":40,"l":0,"b":0},
            title_font=dict(color="#1a4731"),
            font=dict(color="#111111"),
        )
        st.plotly_chart(fig_mapa, use_container_width=True)
        if dist_sel != "TODOS" and len(datos_mapa) > 1:
            st.caption(
                f"📍 El distrito **{dist_sel}** tiene **{len(datos_mapa)} comisarías reales** "
                "según el registro oficial de la PNP."
            )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 · DATOS
# ─────────────────────────────────────────────────────────────────────────────
with tab4:

    st.markdown('<p class="section-title">Buscar por modalidad de delito</p>', unsafe_allow_html=True)
    busqueda = st.text_input("Ingrese una modalidad de delito", placeholder="Ej: robo, hurto, violencia...")
    tabla = (
        df_f[df_f["P_MODALIDADES"].str.contains(busqueda, case=False, na=False)]
        if busqueda else df_f
    )

    st.markdown(f'<p class="section-title">Tabla de datos · {len(tabla):,} registros</p>', unsafe_allow_html=True)
    st.dataframe(tabla, use_container_width=True, height=450)

    st.markdown('<p class="section-title">Descargar datos filtrados</p>', unsafe_allow_html=True)
    csv = tabla.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Descargar CSV",
        data=csv,
        file_name="denuncias_filtradas.csv",
        mime="text/csv"
    )