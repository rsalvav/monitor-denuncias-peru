import pandas as pd

def cargar_datos():
    ruta_archivo = 'data/DATASET_Denuncias_Policiales_Ene 2018 a Abr 2026.zip'
    df = pd.read_csv(ruta_archivo, encoding='utf-8', compression='zip')
    return df

def limpiar_datos(df):
    df_limpio = df.drop_duplicates()
    df_limpio = df_limpio.dropna(subset=['P_MODALIDADES', 'cantidad'])
    df_limpio['cantidad'] = df_limpio['cantidad'].astype(int)
    return df_limpio

def top_5_delitos(df):
    top_5 = df.groupby('P_MODALIDADES')['cantidad'].sum().sort_values(ascending=False).head(5)
    return top_5.reset_index()

if __name__ == '__main__':
    df_crudo = cargar_datos()
    df_procesado = limpiar_datos(df_crudo)
    top_delitos = top_5_delitos(df_procesado)

    print("--- Top 5 Delitos a Nivel Nacional ---")
    print(top_delitos)
