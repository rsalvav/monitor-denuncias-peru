"""
api_or_scraper.py

Módulo encargado de consumir la API Open-Meteo para obtener
información climática actual de los departamentos del Perú.
"""

import logging
import time
from functools import wraps

import requests

# --------------------------------------------------
# CONFIGURACIÓN DE LOGGING
# --------------------------------------------------

logging.basicConfig(
    filename="data/clima.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --------------------------------------------------
# COORDENADAS APROXIMADAS DE DEPARTAMENTOS
# --------------------------------------------------

COORDENADAS = {
    "AMAZONAS": (-6.23, -77.87),
    "ANCASH": (-9.53, -77.53),
    "APURIMAC": (-13.63, -72.88),
    "AREQUIPA": (-16.40, -71.53),
    "AYACUCHO": (-13.16, -74.22),
    "CAJAMARCA": (-7.16, -78.50),
    "CALLAO": (-12.06, -77.15),
    "PROV. CONST. DEL CALLAO": (-12.06, -77.15),
    "CUSCO": (-13.52, -71.97),
    "HUANCAVELICA": (-12.78, -74.97),
    "HUANUCO": (-9.93, -76.24),
    "ICA": (-14.06, -75.73),
    "JUNIN": (-12.06, -75.21),
    "LA LIBERTAD": (-8.11, -79.02),
    "LAMBAYEQUE": (-6.77, -79.84),
    "LIMA": (-12.05, -77.04),
    "LIMA METROPOLITANA": (-12.0464, -77.0428),
    "REGION LIMA": (-11.1067, -77.6050),
    "LORETO": (-3.75, -73.25),
    "MADRE DE DIOS": (-12.59, -69.18),
    "MOQUEGUA": (-17.19, -70.93),
    "PASCO": (-10.68, -76.26),
    "PIURA": (-5.19, -80.63),
    "PUNO": (-15.84, -70.02),
    "SAN MARTIN": (-6.49, -76.36),
    "TACNA": (-18.01, -70.25),
    "TUMBES": (-3.56, -80.45),
    "UCAYALI": (-8.38, -74.55),
}

# --------------------------------------------------
# DECORADOR
# --------------------------------------------------

def log_tiempo(func):
    """
    Mide tiempo de ejecución y registra logs.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        inicio = time.time()

        logging.info(f"Iniciando {func.__name__}")

        try:
            resultado = func(*args, **kwargs)

            fin = time.time()

            logging.info(
                f"{func.__name__} ejecutado en "
                f"{fin - inicio:.3f} segundos"
            )

            return resultado

        except Exception as e:

            logging.exception(
                f"Error en {func.__name__}: {e}"
            )

            return None

    return wrapper


# --------------------------------------------------
# API OPEN METEO
# --------------------------------------------------

@log_tiempo
def obtener_clima(departamento):
    """
    Obtiene clima actual desde Open-Meteo.

    Parameters
    ----------
    departamento : str

    Returns
    -------
    dict | None
    """

    if departamento not in COORDENADAS:
        logging.warning(
            f"Departamento no encontrado: {departamento}"
        )
        return None

    lat, lon = COORDENADAS[departamento]

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        "&current=temperature_2m,"
        "precipitation,"
        "wind_speed_10m"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        current = data["current"]

        return {
            "temperatura": current["temperature_2m"],
            "precipitacion": current["precipitation"],
            "viento": current["wind_speed_10m"]
        }

    except Exception as e:

        logging.exception(
            f"Error consumiendo Open-Meteo: {e}"
        )

        return None