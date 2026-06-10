# 🚨 Monitor de Denuncias Policiales en Perú

## Descripción del Proyecto
Aplicación web interactiva desarrollada en Python con Streamlit y Plotly para la exploración y análisis de la base de datos de denuncias policiales a nivel nacional. Esta herramienta permite identificar tendencias, modalidades delictivas frecuentes y realizar comparaciones entre departamentos mediante visualizaciones dinámicas.

## Objetivos
- Analizar la distribución de denuncias policiales en el Perú.
- Identificar las modalidades de delito más frecuentes.
- Comparar la incidencia de denuncias entre departamentos.
- Facilitar la exploración de información mediante visualizaciones interactivas.
- Proporcionar una herramienta sencilla para el análisis descriptivo de datos.

## Fuente de Datos

Los datos utilizados provienen de los registros oficiales del Estado Peruano, de denuncias policiales almacenados en formato CSV.
- **Fuente:** Plataforma Nacional de Datos Abiertos
- **Formato en repositorio:** Archivo comprimido `.zip` (optimizado para el procesamiento ágil con Pandas y cumplimiento de límites de almacenamiento).

### Variables Principales
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

### Visualizaciones Dinámicas

#### 1. Top 5 Modalidades de Delito

Gráfico de barras que permite identificar las modalidades con mayor cantidad de denuncias registradas.

#### 2. Departamentos con Mayor y Menor Número de Denuncias

Análisis de los 3 departamentos con mayor y menor registro de denuncias.

#### 3. Participación de Delitos

Gráfico circular que representa la participación de las principales modalidades de delito.

#### 4. Evolución de Denuncias por Año

Gráfico de líneas que marca tendencias y variaciones a lo largo del tiempo.

#### 5. Comparación de Departamentos

Herramienta para comparar visualmente el volumen de denuncias entre dos departamentos seleccionados por el usuario.

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

---

## Estructura del Proyecto

```text
monitor-denuncias-peru/
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
│
└── docs/
    └── parcial.pdf
```

## Instalación y Ejecución

### 1. Descargar el repositorio
```
bash
git clone https://github.com/rsalvav/monitor-denuncias-peru.git
```

### 2. Ingresar al proyecto
```
bash
cd monitor-denuncias-peru
```

### 3. Instalar dependencias
```
bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```
bash
streamlit run src/app.py
```

### 5. Abrir en el navegador
```
text
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

## Integrantes

- Palma Dolmos, Clara Jimena
- Pereyra Jara, Mateo Gabriel
- Salva Vasquez, Rosalinda
- Torres Llerena, Marcelo Antonio
- Medina de la Cruz, Alejandra Valeria

---
