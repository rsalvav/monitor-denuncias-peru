# 🚨 Monitor de Denuncias Policiales en Perú

## Descripción del Proyecto

Monitor de Denuncias Policiales en Perú es una aplicación web desarrollada en Streamlit que permite visualizar y analizar información sobre denuncias policiales registradas en diferentes departamentos del país.

La aplicación ofrece filtros interactivos, indicadores clave y gráficos dinámicos que facilitan la exploración de los datos y apoyan la identificación de tendencias, patrones y comparaciones entre regiones.

---

## Objetivos

- Analizar la distribución de denuncias policiales en el Perú.
- Identificar las modalidades de delito más frecuentes.
- Comparar la incidencia de denuncias entre departamentos.
- Facilitar la exploración de información mediante visualizaciones interactivas.
- Proporcionar una herramienta sencilla para el análisis descriptivo de datos.

---

## Fuente de Datos

Los datos utilizados corresponden a registros de denuncias policiales almacenados en formato CSV.

**Fuente:** [Completar con la fuente utilizada]

### Variables principales

| Variable | Descripción |
|-----------|------------|
| ANIO | Año del registro |
| MES | Mes del registro |
| DPTO_HECHO_NEW | Departamento donde ocurrió el hecho |
| PROV_HECHO | Provincia donde ocurrió el hecho |
| DIST_HECHO | Distrito donde ocurrió el hecho |
| UBIGEO_HECHO | Código UBIGEO de la ubicación |
| P_MODALIDADES | Modalidad del delito |
| cantidad | Cantidad de denuncias registradas |

---

## Procesamiento de Datos

Se realizaron las siguientes actividades de preparación y limpieza de datos:

- Eliminación de registros duplicados.
- Tratamiento de valores faltantes.
- Validación de tipos de datos.
- Estandarización de campos utilizados en filtros y gráficos.
- Agrupación y agregación de datos para métricas descriptivas.
- Cálculo de indicadores estadísticos básicos.

---

## Funcionalidades Implementadas

### Filtros Interactivos

- Filtro por departamento.
- Filtro por modalidad del delito.
- Filtro por año.

### Indicadores KPI

- Total de denuncias.
- Número de modalidades registradas.
- Número de departamentos analizados.

### Visualizaciones

#### 1. Top 5 Modalidades de Delito

Permite identificar las modalidades con mayor cantidad de denuncias registradas.

#### 2. Departamentos con Mayor y Menor Número de Denuncias

Muestra los tres departamentos con más denuncias y los tres departamentos con menos denuncias.

#### 3. Participación de Delitos

Gráfico circular que representa la participación de las principales modalidades de delito.

#### 4. Evolución de Denuncias por Año

Permite observar tendencias y variaciones a lo largo del tiempo.

#### 5. Comparación de Departamentos

Facilita la comparación directa entre dos departamentos seleccionados por el usuario.

### Herramientas Adicionales

- Buscador de modalidades.
- Tabla interactiva de datos.
- Descarga de datos filtrados en formato CSV.

---

## Tecnologías Utilizadas

- Python
- Streamlit
- Pandas
- Plotly

---

## Estructura del Proyecto

```text
project-root/
│
├── README.md
├── requirements.txt
│
├── data/
│   └── denuncias.csv
│
├── src/
│   ├── app.py
│   ├── processing.py
│   └── viz.py
│
├── docs/
│   └── parcial.pdf
│
└── tests/
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

```text
http://localhost:8501
```

---

## Métricas Descriptivas

La aplicación permite obtener información descriptiva básica como:

- Total de denuncias registradas.
- Cantidad de modalidades de delito.
- Cantidad de departamentos analizados.
- Ranking de modalidades con mayor incidencia.
- Ranking de departamentos con mayor y menor incidencia.
- Evolución temporal de las denuncias.

---

## Referencias

### Streamlit Gallery

https://streamlit.io/gallery

Se tomó como referencia para la implementación de dashboards interactivos, filtros laterales e indicadores KPI.

### Plotly Python Documentation

https://plotly.com/python/

Se utilizó como referencia para la construcción de gráficos interactivos de barras, líneas y gráficos circulares.

---

## Integrantes

- Rosalinda 
- Clara
- Mateo
- Marcelo

---

## Repositorio

https://github.com/rsalvav/monitor-denuncias-peru
