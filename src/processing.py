import pandas as pd


def cargar_datos():
    ruta_archivo = 'data/DATASET_Denuncias_con_Comisaria_Cercana.zip'
    df = pd.read_csv(ruta_archivo, compression='zip', encoding='utf-8')
    return df


def cargar_comisarias_por_distrito():
    """
    Carga la tabla de referencia con TODAS las comisarías físicamente ubicadas
    en cada distrito (puede haber varias, ej. Ate tiene 4). Si un distrito no
    tiene ninguna comisaría propia, incluye la comisaría más cercana (fallback)
    marcada como ES_PRINCIPAL=True.
    """
    ruta_archivo = 'data/Comisarias_por_Distrito.csv'
    df = pd.read_csv(ruta_archivo, encoding='utf-8')
    return df


def limpiar_datos(df):
    df_limpio = df.drop_duplicates()
    df_limpio = df_limpio.dropna(subset=['P_MODALIDADES', 'cantidad'])
    df_limpio['cantidad'] = df_limpio['cantidad'].astype(int)
    return df_limpio


def top_5_delitos(df):
    top_5 = df.groupby('P_MODALIDADES')['cantidad'].sum().sort_values(ascending=False).head(5)
    return top_5.reset_index()


def expandir_por_comisaria(df, comisarias_ref):
    """
    Reparte la 'cantidad' de cada denuncia entre todas las comisarías reales
    del distrito correspondiente, de forma PROPORCIONAL al campo SECTORES
    (peso oficial de la PNP: cantidad de sectores administrativos que cubre
    cada comisaría). Una comisaría con más sectores recibe una porción mayor
    de las denuncias de ese distrito.

    Si el distrito solo tiene una comisaría asociada (la mayoría de casos),
    esa comisaría recibe el 100% de la cantidad, sin importar su peso.

    Devuelve un dataframe expandido con una fila por cada combinación
    denuncia-comisaría, y la columna 'cantidad_repartida' con la porción
    correspondiente.
    """
    peso_total = (
        comisarias_ref.groupby('UBIGEO_HECHO')['SECTORES']
        .sum()
        .rename('peso_total_distrito')
    )

    ref = comisarias_ref.merge(
        peso_total, left_on='UBIGEO_HECHO', right_index=True, how='left'
    )
    ref['proporcion'] = ref['SECTORES'] / ref['peso_total_distrito']

    expandido = df.merge(
        ref[['UBIGEO_HECHO', 'COMISARIA', 'COD_CPNP_LOCAL', 'LAT', 'LONG',
             'DEPTO_COMISARIA', 'PROV_COMISARIA', 'DIST_COMISARIA', 'proporcion']],
        on='UBIGEO_HECHO', how='left', suffixes=('_principal', '')
    )

    # Si algún distrito no aparece en la tabla de referencia (no debería pasar),
    # se usa como respaldo la comisaría ya asignada con el 100% de la cantidad.
    sin_ref = expandido['COMISARIA'].isna()
    expandido.loc[sin_ref, 'COMISARIA'] = expandido.loc[sin_ref, 'COMISARIA_MAS_CERCANA']
    expandido.loc[sin_ref, 'COD_CPNP_LOCAL'] = expandido.loc[sin_ref, 'COD_CPNP']
    expandido.loc[sin_ref, 'LAT'] = expandido.loc[sin_ref, 'LAT_COMISARIA']
    expandido.loc[sin_ref, 'LONG'] = expandido.loc[sin_ref, 'LONG_COMISARIA']
    expandido.loc[sin_ref, 'DEPTO_COMISARIA'] = expandido.loc[sin_ref, 'DPTO_HECHO_NEW']
    expandido.loc[sin_ref, 'PROV_COMISARIA'] = expandido.loc[sin_ref, 'PROV_HECHO']
    expandido.loc[sin_ref, 'DIST_COMISARIA'] = expandido.loc[sin_ref, 'DIST_HECHO']
    expandido.loc[sin_ref, 'proporcion'] = 1.0

    expandido['cantidad_repartida'] = expandido['cantidad'] * expandido['proporcion']

    return expandido


def ranking_comisarias(df, comisarias_ref, top_n=15):
    """
    Ranking de comisarías con más denuncias estimadas, repartiendo
    proporcionalmente (según SECTORES) entre todas las comisarías reales de
    cada distrito.
    """
    expandido = expandir_por_comisaria(df, comisarias_ref)

    ranking = (
        expandido.groupby(['COMISARIA', 'DEPTO_COMISARIA', 'PROV_COMISARIA', 'DIST_COMISARIA'])['cantidad_repartida']
        .sum()
        .reset_index()
        .rename(columns={'cantidad_repartida': 'total_denuncias_estimado'})
    )
    ranking['total_denuncias_estimado'] = ranking['total_denuncias_estimado'].round(1)

    return (
        ranking
        .sort_values('total_denuncias_estimado', ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )


def datos_mapa_comisarias(df, comisarias_ref):
    """
    Agrega denuncias estimadas por comisaría (repartidas proporcionalmente
    según SECTORES entre todas las comisarías reales de cada distrito) junto
    con sus coordenadas, para graficar en el mapa.
    """
    expandido = expandir_por_comisaria(df, comisarias_ref)

    mapa = (
        expandido.groupby(['COMISARIA', 'COD_CPNP_LOCAL', 'LAT', 'LONG',
                            'DEPTO_COMISARIA', 'PROV_COMISARIA', 'DIST_COMISARIA'])['cantidad_repartida']
        .sum()
        .reset_index()
        .rename(columns={'cantidad_repartida': 'total_denuncias'})
    )
    mapa['total_denuncias'] = mapa['total_denuncias'].round(1)

    return mapa


def calcular_centro_zoom(df_mapa):
    """
    Calcula el centro y el nivel de zoom del mapa en función de la extensión
    geográfica de las comisarías a mostrar. Si no hay datos, devuelve la vista
    por defecto de todo el Perú.
    """
    centro_peru = {"lat": -9.19, "lon": -75.0152}
    zoom_peru = 4.3

    if df_mapa.empty:
        return centro_peru, zoom_peru

    # Caso especial: una sola comisaría -> marcar su ubicación exacta con zoom alto
    if len(df_mapa) == 1:
        centro = {
            "lat": df_mapa["LAT"].iloc[0],
            "lon": df_mapa["LONG"].iloc[0],
        }
        return centro, 14.5

    lat_min, lat_max = df_mapa["LAT"].min(), df_mapa["LAT"].max()
    lon_min, lon_max = df_mapa["LONG"].min(), df_mapa["LONG"].max()

    centro = {
        "lat": (lat_min + lat_max) / 2,
        "lon": (lon_min + lon_max) / 2,
    }

    lat_span = max(lat_max - lat_min, 0.02)
    lon_span = max(lon_max - lon_min, 0.02)
    max_span = max(lat_span, lon_span)

    # Heurística simple: a menor extensión geográfica, mayor zoom
    if max_span > 8:
        zoom = 4.3
    elif max_span > 4:
        zoom = 5.3
    elif max_span > 2:
        zoom = 6.3
    elif max_span > 1:
        zoom = 7.3
    elif max_span > 0.5:
        zoom = 8.3
    elif max_span > 0.2:
        zoom = 9.3
    else:
        zoom = 10.5

    return centro, zoom


def top_comisarias_por_modalidad(df, comisarias_ref, top_n=10):
    """
    Devuelve las denuncias estimadas (reparto proporcional por SECTORES) de
    las top_n comisarías con más denuncias en total, desagregadas por
    modalidad de delito. Pensado para graficar un gráfico de barras
    apiladas (comisaría en el eje X, una barra por modalidad).
    """
    expandido = expandir_por_comisaria(df, comisarias_ref)

    agregado = (
        expandido.groupby(['COMISARIA', 'P_MODALIDADES'])['cantidad_repartida']
        .sum()
        .reset_index()
    )

    top_comisarias = (
        agregado.groupby('COMISARIA')['cantidad_repartida']
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .index.tolist()
    )

    resultado = agregado[agregado['COMISARIA'].isin(top_comisarias)].copy()
    resultado['cantidad_repartida'] = resultado['cantidad_repartida'].round(1)

    return resultado, top_comisarias


def distancia_promedio_departamento(df):
    """
    Distancia promedio (ponderada por número de denuncias) entre el distrito
    donde ocurrió el hecho y su comisaría más cercana, agrupada por departamento.
    """
    temp = df.copy()
    temp['distancia_ponderada'] = temp['DISTANCIA_KM'] * temp['cantidad']

    resumen = (
        temp.groupby('DPTO_HECHO_NEW')
        .agg(
            distancia_ponderada_total=('distancia_ponderada', 'sum'),
            cantidad_total=('cantidad', 'sum')
        )
        .reset_index()
    )

    resumen['distancia_promedio_km'] = (
        resumen['distancia_ponderada_total'] / resumen['cantidad_total']
    ).round(2)

    return (
        resumen[['DPTO_HECHO_NEW', 'distancia_promedio_km', 'cantidad_total']]
        .sort_values('distancia_promedio_km', ascending=False)
        .reset_index(drop=True)
    )


if __name__ == '__main__':
    df_crudo = cargar_datos()
    df_procesado = limpiar_datos(df_crudo)
    top_delitos = top_5_delitos(df_procesado)
    print("--- Top 5 Delitos a Nivel Nacional ---")
    print(top_delitos)
