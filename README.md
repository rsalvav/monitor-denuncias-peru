# Monitor de Denuncias Policiales en Perú

## Descripción del Proyecto

Aplicación web interactiva desarrollada en Python con Streamlit y Plotly para la exploración y análisis de la base de datos de denuncias policiales a nivel nacional. Esta herramienta permite identificar tendencias, modalidades delictivas frecuentes y realizar comparaciones entre departamentos mediante visualizaciones dinámicas.

A partir de la versión actual, el dataset de denuncias fue enriquecido con información geoespacial de las comisarías de la Policía Nacional del Perú (PNP), lo que permite además identificar la comisaría más cercana a cada distrito, estimar la carga de denuncias por comisaría y visualizar todo en un mapa interactivo.

Para la entrega final se incorporó el consumo de una API externa de clima (Open-Meteo) que muestra las condiciones meteorológicas actuales del departamento seleccionado, y una base de datos SQLite que registra el historial de consultas realizadas.

---

## Objetivos

- Analizar la distribución de denuncias policiales en el Perú.
- Identificar las modalidades de delito más frecuentes.
- Comparar la incidencia de denuncias entre departamentos.
- Identificar la comisaría más cercana a cada distrito y estimar su carga de denuncias.
- Facilitar la exploración de información mediante visualizaciones interactivas.
- Proporcionar una herramienta sencilla para el análisis descriptivo de datos.
- Mostrar el clima actual del departamento filtrado mediante una API gratuita y sin registro.

---

## Fuente de Datos

### Denuncias policiales
Los datos utilizados provienen de los registros oficiales del Estado Peruano, de denuncias policiales almacenados en formato CSV.

- **Fuente:** Plataforma Nacional de Datos Abiertos.
- **Formato en repositorio:** Archivo comprimido .zip (optimizado para el procesamiento ágil con Pandas y cumplimiento de límites de almacenamiento).

### Comisarías de la PNP (información geoespacial)
Para enriquecer el dataset de denuncias se utilizaron dos fuentes oficiales complementarias:

- **PNP / MININTER (noviembre 2019):** relación de 1,318 comisarías básicas con coordenadas GPS (latitud/longitud).
- **PNP (diciembre 2025):** relación de 1,332 comisarías operativas vigentes, con departamento, provincia, distrito y número de sectores administrativos que cubre cada una.

Ambas fuentes se cruzaron por código único de comisaría (COD_CPNP) para obtener una base depurada de 1,302 comisarías activas y georreferenciadas.

### Centroides de distritos
Para calcular la distancia entre cada distrito y su comisaría más cercana, se utilizó una base abierta de ubigeos con coordenadas de capitales distritales (cobertura de 1,891 distritos a nivel nacional), dado que los portales oficiales del Estado no permiten la descarga automatizada de este dato.

### API de clima (Open-Meteo)
Para mostrar el clima actual del departamento seleccionado se consume la API pública de [Open-Meteo](https://open-meteo.com), que es gratuita, no requiere registro ni API key, y devuelve datos en tiempo real de temperatura, precipitación y viento.

---

## Variables Principales

### Dataset original de denuncias

| Variable | Descripción |
|---|---|
| ANIO | Año del registro |
| MES | Mes del registro |
| DPTO_HECHO_NEW | Departamento donde ocurrió el hecho |
| PROV_HECHO | Provincia donde ocurrió el hecho |
| DIST_HECHO | Distrito donde ocurrió el hecho |
| UBIGEO_HECHO | Código UBIGEO de la ubicación |
| P_MODALIDADES | Modalidad del delito |
| cantidad | Cantidad de denuncias registradas |

### Variables agregadas (enriquecimiento con comisarías)

| Variable | Descripción |
|---|---|
| COMISARIA_MAS_CERCANA | Comisaría asignada al distrito (vecino más cercano) |
| COD_CPNP | Código único de la comisaría asignada |
| DEPTO_COMISARIA / PROV_COMISARIA / DIST_COMISARIA | Ubicación oficial de la comisaría asignada |
| LAT_COMISARIA / LONG_COMISARIA | Coordenadas de la comisaría asignada |
| LAT_DISTRITO_HECHO / LONG_DISTRITO_HECHO | Coordenadas del centroide del distrito del hecho |
| DISTANCIA_KM | Distancia (Haversine) entre el distrito y su comisaría asignada |
| OTRAS_COMISARIAS_DISTRITO | Otras comisarías reales ubicadas en el mismo distrito, si existen |

---

## Procesamiento de Datos

Se realizaron las siguientes actividades de preparación, limpieza y enriquecimiento de datos:

- Eliminación de registros duplicados.
- Tratamiento de valores faltantes.
- Validación de tipos de datos.
- Estandarización de campos utilizados en filtros y gráficos.
- Extracción y limpieza de la relación de comisarías PNP (Excel 2019 y PDF 2025).
- Cruce de ambas fuentes de comisarías por código CPNP, excluyendo comisarías cerradas o sin coordenadas reportadas.
- Cálculo de la comisaría más cercana a cada distrito mediante distancia de Haversine (vecino más cercano).
- Identificación de distritos con más de una comisaría real, y reparto proporcional de denuncias entre ellas según el número de sectores administrativos que cubre cada una (dato oficial PNP).
- Agrupación y agregación de datos para métricas descriptivas.
- Cálculo de indicadores estadísticos básicos.
- Consumo de API externa (Open-Meteo) para obtener clima en tiempo real según el departamento seleccionado.
- Persistencia de consultas de clima en base de datos SQLite local.

---

## Funcionalidades Implementadas

### Filtros Interactivos
- Filtro por departamento.
- Filtro por distrito (en cascada, según el departamento elegido).
- Filtro por modalidad del delito.
- Filtro por año.
- Filtro por comisaría más cercana (en cascada, según departamento y distrito elegidos).

### Indicadores KPI
- Total de denuncias.
- Número de modalidades registradas.
- Número de departamentos analizados.
- Distancia promedio (ponderada por cantidad de denuncias) entre el distrito del hecho y su comisaría asignada.

### Clima en Tiempo Real (API Open-Meteo)
Al seleccionar un departamento, el sidebar muestra automáticamente el clima actual de esa zona obtenido desde la API de Open-Meteo:
- Temperatura (°C).
- Precipitación (mm).
- Velocidad del viento (km/h).

Cada consulta queda registrada en la base de datos SQLite con la fecha y hora de consulta.

### Visualizaciones Dinámicas
- **Top 10 comisarías con más denuncias, por modalidad de delito.** Gráfico de barras acumuladas que identifica las comisarías con mayor carga estimada de denuncias y el tipo de delito con mayor participación en cada una.
- **Departamentos con Mayor y Menor Número de Denuncias.** Gráfico de barras que permite identificar los departamentos con mayor y menor cantidad de denuncias registradas.
- **Top 10 distritos de Lima Metropolitana, por tipo de delito.** Gráfico de barras acumuladas que identifica qué distrito de Lima Metropolitana tiene mayor número de denuncias y el tipo de denuncia con mayor participación.
- **Participación de Delitos.** Gráfico circular que representa la participación de las principales modalidades de delito.
- **Evolución de Denuncias por Año.** Gráfico de líneas que marca tendencias y variaciones a lo largo del tiempo.
- **Mapa de Comisarías y Concentración de Denuncias.** Mapa interactivo que ubica cada comisaría y su carga estimada de denuncias; el centro y el nivel de zoom se ajustan automáticamente según los filtros activos.
- **Ranking de Comisarías.** Top N configurable (mediante control deslizante) de comisarías con más denuncias estimadas.
- **Distancia Promedio por Departamento.** Gráfico de barras que muestra qué tan lejos está, en promedio, una denuncia de su comisaría asignada, por departamento.
- **Alertas de variación de denuncias.** Compara los dos últimos años completos y muestra los distritos con mayor crecimiento y mayor caída de denuncias.
- **Comparador de zonas.** Gráfico de líneas que permite comparar la evolución anual de denuncias entre dos departamentos a elección.

### Herramientas Adicionales
- Buscador de texto integrado para modalidades específicas.
- Visualizador de tabla de datos.
- Botón de exportación para descargar los datos filtrados en un nuevo archivo en formato CSV.

---

## Tecnologías Utilizadas

- Python
- Streamlit
- Pandas
- Plotly
- Requests
- SQLite3

---

## Estructura del Proyecto

```
monitor-denuncias-peru/
│
├── README.md
├── requirements.txt
│
├── data/
│   ├── DATASET_Denuncias_con_Comisaria_Cercana.csv
│   ├── Comisarias_por_Distrito.csv
│   └── denuncias.db                  ← base de datos SQLite (se genera automáticamente)
│
├── src/
│   ├── app.py                        ← aplicación principal Streamlit
│   ├── processing.py                 ← funciones de limpieza y procesamiento
│   ├── api_or_scraper.py             ← consumo de API de clima (Open-Meteo)
│   └── db.py                         ← gestión de base de datos SQLite
│
└── docs/
    ├── parcial.pdf
    └── Documentacion_Proyecto_Denuncias_Policiales.docx
```

---

## Instalación y Ejecución

### 1. Descargar el repositorio
```bash
git clone https://github.com/rsalvav/monitor-denuncias-peru.git
```

### 2. Ingresar al proyecto
```bash
cd monitor-denuncias-peru
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
streamlit run src/app.py
```

### 5. Abrir en el navegador
```
http://localhost:8501
```

> La base de datos SQLite (`data/denuncias.db`) se crea automáticamente la primera vez que se ejecuta la aplicación. No es necesario ningún paso adicional.

---

## Referencias

- Ministerio del Interior. (2026). Denuncias policiales - 1 (Conjunto de datos). Portal de Datos Abiertos del Estado Peruano. datosabiertos.gob.pe. *Licencia: Datos Abiertos (Dominio Público).*
- Observatorio Nacional de Seguridad Ciudadana. (2025). Reporte de denuncias registradas en el SIDPOL 2025. Ministerio del Interior. https://www.gob.pe/institucion/mininter/informes-publicaciones/6539903-reporte-denuncias-registradas-en-el-sidpol-2025
- Jaitman, L., & Anamaría, G. (2020). ¿Por qué se denuncian delitos patrimoniales ante la policía en el Perú? Revista Criminalidad, 62(3), 25-41. http://www.scielo.org.co/pdf/crim/v62n3/1794-3108-crim-62-03-25.pdf
- Ministerio del Interior. (2026). Reporte del primer trimestre de 2026 de la Incidencia Delictiva en la Macro Región Norte. Informes y publicaciones - Ministerio del Interior.
- Policía Nacional del Perú / Ministerio del Interior. (2019). Relación de comisarías básicas a nivel nacional (Conjunto de datos georreferenciado). Plataforma Nacional de Datos Abiertos. *Licencia: Datos Abiertos (Dominio Público).*
- Policía Nacional del Perú. (2025). Relación de comisarías operativas a nivel nacional al 15DIC2025. Informes y publicaciones - PNP.
- Open-Meteo. (2024). Free Weather API. https://open-meteo.com

---

## Integrantes

- Palma Dolmos, Clara Jimena
- Pereyra Jara, Mateo Gabriel
- Salva Vasquez, Rosalinda
- Torres Llerena, Marcelo Antonio
- Medina de la Cruz, Alejandra Valeria

