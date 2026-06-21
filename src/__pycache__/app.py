import streamlit as st
import plotly.express as px
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

# Configuración de la página

st.set_page_config(
    page_title="Monitor de Denuncias Policiales",
    layout="wide"
)

st.title(" Monitor de Denuncias Policiales en Perú")
st.markdown("---")

# Carga y limpieza de datos

df_crudo = cargar_datos()
df_limpio = limpiar_datos(df_crudo)
comisarias_ref = cargar_comisarias_por_distrito()

# Panel Lateral - Filtros

st.sidebar.header(" Filtros")

lista_departamentos = sorted(
    df_limpio["DPTO_HECHO_NEW"].unique().tolist()
)

lista_departamentos.insert(0, "TODO EL PERÚ")

departamento_seleccionado = st.sidebar.selectbox(
    "Departamento",
    lista_departamentos
)

# El listado de distritos depende del departamento elegido (filtro en cascada)
if departamento_seleccionado != "TODO EL PERÚ":
    df_para_distritos = df_limpio[
        df_limpio["DPTO_HECHO_NEW"] == departamento_seleccionado
    ]
else:
    df_para_distritos = df_limpio

lista_distritos = sorted(
    df_para_distritos["DIST_HECHO"].unique().tolist()
)

lista_distritos.insert(0, "TODOS")

distrito_seleccionado = st.sidebar.selectbox(
    "Distrito",
    lista_distritos
)

lista_delitos = sorted(
    df_limpio["P_MODALIDADES"].unique().tolist()
)

lista_delitos.insert(0, "TODOS")

delito_seleccionado = st.sidebar.selectbox(
    "Modalidad del delito",
    lista_delitos
)

lista_anios = sorted(
    df_limpio["ANIO"].unique().tolist()
)

lista_anios.insert(0, "TODOS")

anio_seleccionado = st.sidebar.selectbox(
    "Año",
    lista_anios
)

# El listado de comisarías depende del departamento y distrito ya elegidos
# (cascada de 3 niveles: Departamento -> Distrito -> Comisaría)
df_para_comisarias = df_limpio.copy()

if departamento_seleccionado != "TODO EL PERÚ":
    df_para_comisarias = df_para_comisarias[
        df_para_comisarias["DPTO_HECHO_NEW"] == departamento_seleccionado
    ]

if distrito_seleccionado != "TODOS":
    df_para_comisarias = df_para_comisarias[
        df_para_comisarias["DIST_HECHO"] == distrito_seleccionado
    ]

lista_comisarias = sorted(
    df_para_comisarias["COMISARIA_MAS_CERCANA"].unique().tolist()
)

lista_comisarias.insert(0, "TODAS")

comisaria_seleccionada = st.sidebar.selectbox(
    "Comisaría más cercana",
    lista_comisarias
)

# Aplicación de filtros lógicos

df_filtrado = df_limpio.copy()

if departamento_seleccionado != "TODO EL PERÚ":
    df_filtrado = df_filtrado[
        df_filtrado["DPTO_HECHO_NEW"]
        == departamento_seleccionado
    ]

if distrito_seleccionado != "TODOS":
    df_filtrado = df_filtrado[
        df_filtrado["DIST_HECHO"]
        == distrito_seleccionado
    ]

if delito_seleccionado != "TODOS":
    df_filtrado = df_filtrado[
        df_filtrado["P_MODALIDADES"]
        == delito_seleccionado
    ]

if anio_seleccionado != "TODOS":
    df_filtrado = df_filtrado[
        df_filtrado["ANIO"]
        == anio_seleccionado
    ]

if comisaria_seleccionada != "TODAS":
    df_filtrado = df_filtrado[
        df_filtrado["COMISARIA_MAS_CERCANA"]
        == comisaria_seleccionada
    ]

# Indicadores Generales

st.subheader(" Indicadores Generales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total denuncias",
        f"{int(df_filtrado['cantidad'].sum()):,}"
    )

with col2:
    st.metric(
        "Modalidades",
        df_filtrado["P_MODALIDADES"].nunique()
    )

with col3:
    st.metric(
        "Departamentos",
        df_filtrado["DPTO_HECHO_NEW"].nunique()
    )

with col4:
    if df_filtrado["cantidad"].sum() > 0:
        distancia_prom_nacional = (
            (df_filtrado["DISTANCIA_KM"] * df_filtrado["cantidad"]).sum()
            / df_filtrado["cantidad"].sum()
        )
    else:
        distancia_prom_nacional = 0

    st.metric(
        "Distancia prom. a comisaría",
        f"{distancia_prom_nacional:,.2f} km"
    )

st.markdown("---")

# GRÁFICO 1 - TOP COMISARÍAS POR MODALIDAD DE DELITO

st.subheader(" Top 10 Comisarías con Más Denuncias, por Modalidad de Delito")

datos_top_comisarias, orden_comisarias = top_comisarias_por_modalidad(
    df_filtrado, comisarias_ref, top_n=10
)

if datos_top_comisarias.empty:
    st.info("No hay datos de comisarías para los filtros seleccionados.")
else:
    fig1 = px.bar(
        datos_top_comisarias,
        x="COMISARIA",
        y="cantidad_repartida",
        color="P_MODALIDADES",
        title="Top 10 comisarías con más denuncias estimadas, por modalidad",
        category_orders={"COMISARIA": orden_comisarias}
    )

    fig1.update_layout(
        barmode="stack",
        xaxis_title="Comisaría",
        yaxis_title="Denuncias estimadas",
        legend_title="Modalidad del delito"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.caption(
        "Las denuncias se reparten proporcionalmente entre las comisarías reales de cada "
        "distrito según el número de sectores administrativos que cubre cada una (dato oficial "
        "PNP). Este gráfico respeta los filtros activos del panel lateral."
    )

# Gráfico 2 - Departamentos con mayor y menor número de denuncias

st.subheader(" Departamentos con Mayor y Menor Número de Denuncias")

resumen_departamentos = (
    df_filtrado
    .groupby("DPTO_HECHO_NEW")["cantidad"]
    .sum()
    .reset_index()
)

top_3 = (
    resumen_departamentos
    .sort_values(
        by="cantidad",
        ascending=False
    )
    .head(3)
)

bottom_3 = (
    resumen_departamentos
    .sort_values(
        by="cantidad",
        ascending=True
    )
    .head(3)
)

col1, col2 = st.columns(2)

with col1:

    fig_top = px.bar(
        top_3,
        x="DPTO_HECHO_NEW",
        y="cantidad",
        title="Top 3 Departamentos con Más Denuncias",
        text="cantidad"
    )

    fig_top.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_top,
        use_container_width=True
    )

with col2:

    fig_bottom = px.bar(
        bottom_3,
        x="DPTO_HECHO_NEW",
        y="cantidad",
        title="Top 3 Departamentos con Menos Denuncias",
        text="cantidad"
    )

    fig_bottom.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_bottom,
        use_container_width=True
    )


# Gráfico 3 - Participación de Delitos

st.subheader("Participación de Delitos")

top5 = (
    df_filtrado
    .groupby("P_MODALIDADES")["cantidad"]
    .sum()
    .nlargest(5)
    .reset_index()
)

fig3 = px.pie(
    top5,
    values="cantidad",
    names="P_MODALIDADES",
    title="Participación de los principales delitos"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# Gráfico 4 - Evolución Temporal Anual

st.subheader(" Evolución de Denuncias por Año")

evolucion = (
    df_limpio
    .groupby("ANIO")["cantidad"]
    .sum()
    .reset_index()
)

fig4 = px.line(
    evolucion,
    x="ANIO",
    y="cantidad",
    markers=True,
    title="Evolución anual de denuncias"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# Gráfico 5 - Top 10 Distritos de Lima Metropolitana por Tipo de Delito

st.subheader("Top 10 Distritos de Lima Metropolitana por Tipo de Delito")

lima_df = df_limpio[df_limpio["DPTO_HECHO_NEW"] == "LIMA METROPOLITANA"].copy()

if anio_seleccionado != "TODOS":
    lima_df = lima_df[lima_df["ANIO"] == anio_seleccionado]

if lima_df.empty:
    st.info("No hay datos de Lima Metropolitana para el año seleccionado.")
else:
    top10_distritos = (
        lima_df
        .groupby("DIST_HECHO")["cantidad"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .index.tolist()
    )

    lima_top10 = lima_df[lima_df["DIST_HECHO"].isin(top10_distritos)]

    datos_apilados = (
        lima_top10
        .groupby(["DIST_HECHO", "P_MODALIDADES"])["cantidad"]
        .sum()
        .reset_index()
    )

    fig5 = px.bar(
        datos_apilados,
        x="DIST_HECHO",
        y="cantidad",
        color="P_MODALIDADES",
        title="Denuncias acumuladas por tipo de delito - Top 10 distritos de Lima Metropolitana",
        category_orders={"DIST_HECHO": top10_distritos}
    )

    fig5.update_layout(
        barmode="stack",
        xaxis_title="Distrito",
        yaxis_title="Cantidad de denuncias",
        legend_title="Modalidad del delito",
        height=650
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

    st.caption(
        "Los 10 distritos se ordenan de mayor a menor según el total de denuncias en el "
        "período seleccionado. Esta vista se enfoca siempre en Lima Metropolitana y no se ve "
        "afectada por el filtro de Departamento ni de Modalidad del delito (para poder mostrar "
        "el desglose completo por tipo de delito)."
    )

st.markdown("---")

# Gráfico 6 - Mapa de Comisarías y Concentración de Denuncias

st.subheader(" Mapa de Comisarías y Concentración de Denuncias")

datos_mapa = datos_mapa_comisarias(df_filtrado, comisarias_ref)

if datos_mapa.empty:
    st.info("No hay datos de comisarías para los filtros seleccionados.")
else:
    centro_mapa, zoom_mapa = calcular_centro_zoom(datos_mapa)

    fig_mapa = px.scatter_mapbox(
        datos_mapa,
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
            "LONG": False,
        },
        color_continuous_scale="Reds",
        size_max=40,
        zoom=zoom_mapa,
        center=centro_mapa,
        title="Concentración de denuncias estimadas por comisaría (reparto proporcional por sectores)"
    )

    fig_mapa.update_layout(
        mapbox_style="open-street-map",
        height=650,
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )

    st.plotly_chart(
        fig_mapa,
        use_container_width=True
    )

    if distrito_seleccionado != "TODOS" and len(datos_mapa) > 1:
        st.caption(
            f"📍 El distrito **{distrito_seleccionado}** tiene **{len(datos_mapa)} comisarías reales** "
            "según el registro oficial de la PNP. Como el dataset de denuncias no especifica la "
            "comisaría exacta de cada caso, la cantidad se repartió proporcionalmente entre todas "
            "ellas según el número de sectores administrativos que cubre cada una (dato oficial PNP)."
        )

# Sección - Ranking de Comisarías con Más Denuncias

st.subheader(" Ranking de Comisarías con Más Denuncias Estimadas")

top_n_comisarias = st.slider(
    "Cantidad de comisarías a mostrar",
    min_value=5,
    max_value=30,
    value=15,
    step=5
)

ranking = ranking_comisarias(df_filtrado, comisarias_ref, top_n=top_n_comisarias)

if ranking.empty:
    st.info("No hay datos de comisarías para los filtros seleccionados.")
else:
    fig_ranking = px.bar(
        ranking,
        x="total_denuncias_estimado",
        y="COMISARIA",
        orientation="h",
        title=f"Top {top_n_comisarias} comisarías con más denuncias estimadas",
        text="total_denuncias_estimado",
        hover_data=["DEPTO_COMISARIA", "PROV_COMISARIA", "DIST_COMISARIA"]
    )

    fig_ranking.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=500
    )

    st.caption(
        "Las denuncias se reparten proporcionalmente entre las comisarías reales de cada "
        "distrito según el número de sectores administrativos que cubre cada una (dato oficial "
        "PNP). En distritos con una sola comisaría, el 100% se asigna a esa comisaría."
    )

    st.plotly_chart(
        fig_ranking,
        use_container_width=True
    )

    st.dataframe(
        ranking,
        use_container_width=True
    )

# Sección - Distancia Promedio Denuncia-Comisaría por Departamento

st.subheader(" Distancia Promedio entre Denuncia y Comisaría, por Departamento")

distancias_dpto = distancia_promedio_departamento(df_filtrado)

if distancias_dpto.empty:
    st.info("No hay datos suficientes para calcular la distancia promedio.")
else:
    fig_distancia = px.bar(
        distancias_dpto,
        x="distancia_promedio_km",
        y="DPTO_HECHO_NEW",
        orientation="h",
        title="Distancia promedio (km) entre el distrito del hecho y su comisaría más cercana",
        text="distancia_promedio_km",
        hover_data=["cantidad_total"]
    )

    fig_distancia.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=700
    )

    st.plotly_chart(
        fig_distancia,
        use_container_width=True
    )

st.markdown("---")

# Sección de Búsqueda y Descarga de Datos

st.subheader(" Buscar modalidad")

busqueda = st.text_input(
    "Ingrese una modalidad de delito"
)

if busqueda:
    tabla = df_filtrado[
        df_filtrado["P_MODALIDADES"]
        .str.contains(
            busqueda,
            case=False,
            na=False
        )
    ]
else:
    tabla = df_filtrado

st.subheader("📋 Tabla de datos")

st.dataframe(
    tabla,
    use_container_width=True
)

st.subheader(" Descargar información")

csv = tabla.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Descargar datos filtrados",
    data=csv,
    file_name="denuncias_filtradas.csv",
    mime="text/csv"
)
