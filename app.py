import streamlit as st
import plotly.express as px
from processing import cargar_datos, limpiar_datos, top_5_delitos

# ==================================
# CONFIGURACIÓN
# ==================================

st.set_page_config(
    page_title="Monitor de Denuncias Policiales",
    layout="wide"
)

st.title("🚨 Monitor de Denuncias Policiales en Perú")
st.markdown("---")

# ==================================
# CARGA Y LIMPIEZA DE DATOS
# ==================================

df_crudo = cargar_datos()
df_limpio = limpiar_datos(df_crudo)

# ==================================
# FILTROS
# ==================================

st.sidebar.header("🎯 Filtros")

# Departamento

lista_departamentos = sorted(
    df_limpio["DPTO_HECHO_NEW"].unique().tolist()
)

lista_departamentos.insert(0, "TODO EL PERÚ")

departamento_seleccionado = st.sidebar.selectbox(
    "Departamento",
    lista_departamentos
)

# Modalidad

lista_delitos = sorted(
    df_limpio["P_MODALIDADES"].unique().tolist()
)

lista_delitos.insert(0, "TODOS")

delito_seleccionado = st.sidebar.selectbox(
    "Modalidad del delito",
    lista_delitos
)

# Año

lista_anios = sorted(
    df_limpio["ANIO"].unique().tolist()
)

lista_anios.insert(0, "TODOS")

anio_seleccionado = st.sidebar.selectbox(
    "Año",
    lista_anios
)

# ==================================
# APLICAR FILTROS
# ==================================

df_filtrado = df_limpio.copy()

if departamento_seleccionado != "TODO EL PERÚ":
    df_filtrado = df_filtrado[
        df_filtrado["DPTO_HECHO_NEW"]
        == departamento_seleccionado
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

# ==================================
# KPI
# ==================================

st.subheader("📌 Indicadores Generales")

col1, col2, col3 = st.columns(3)

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

st.markdown("---")

# ==================================
# GRÁFICO 1 - TOP DELITOS
# ==================================

st.subheader("📊 Top 5 Modalidades de Delito")

top_filtrado = top_5_delitos(df_filtrado)

fig1 = px.bar(
    top_filtrado,
    x="P_MODALIDADES",
    y="cantidad",
    title="Top 5 Delitos"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ==================================
# GRÁFICO 2 - TOP DEPARTAMENTOS
# ==================================

# ==================================
# GRÁFICO 2 - DEPARTAMENTOS CON MÁS Y MENOS DENUNCIAS
# ==================================

st.subheader("📍 Departamentos con Mayor y Menor Número de Denuncias")

resumen_departamentos = (
    df_filtrado
    .groupby("DPTO_HECHO_NEW")["cantidad"]
    .sum()
    .reset_index()
)

# Top 3 departamentos con más denuncias
top_3 = (
    resumen_departamentos
    .sort_values(
        by="cantidad",
        ascending=False
    )
    .head(3)
)

# Top 3 departamentos con menos denuncias
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


##########################################3


# ==================================
# GRÁFICO 3 - PARTICIPACIÓN
# ==================================

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

# ==================================
# GRÁFICO 4 - EVOLUCIÓN ANUAL
# ==================================

st.subheader("📈 Evolución de Denuncias por Año")

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

# ==================================
# GRÁFICO 5 - COMPARACIÓN
# ==================================

st.subheader("Comparación de Departamentos")

departamentos = sorted(
    df_limpio["DPTO_HECHO_NEW"].unique()
)

colA, colB = st.columns(2)

with colA:
    dep1 = st.selectbox(
        "Departamento 1",
        departamentos,
        key="dep1"
    )

with colB:
    dep2 = st.selectbox(
        "Departamento 2",
        departamentos,
        index=1,
        key="dep2"
    )

comparacion = (
    df_limpio[
        df_limpio["DPTO_HECHO_NEW"]
        .isin([dep1, dep2])
    ]
    .groupby("DPTO_HECHO_NEW")["cantidad"]
    .sum()
    .reset_index()
)

fig5 = px.bar(
    comparacion,
    x="DPTO_HECHO_NEW",
    y="cantidad",
    color="DPTO_HECHO_NEW",
    title=f"Comparación: {dep1} vs {dep2}"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

# ==================================
# BUSCADOR
# ==================================

st.subheader("🔎 Buscar modalidad")

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

# ==================================
# TABLA
# ==================================

st.subheader("📋 Tabla de datos")

st.dataframe(
    tabla,
    use_container_width=True
)

# ==================================
# DESCARGA CSV
# ==================================

st.subheader("⬇️ Descargar información")

csv = tabla.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Descargar datos filtrados",
    data=csv,
    file_name="denuncias_filtradas.csv",
    mime="text/csv"
)