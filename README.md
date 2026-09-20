# S08-26-equipo-25-HealthDemand-Sistema-de-Prediccion-y-Gestion-de-Demanda-de-Turnos

# 🏥 HealthDemand: Ecosistema Predictivo y Prescriptivo para la Gestión de Capacidad Médica

![Status](https://img.shields.io/badge/Status-Production_Ready-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Machine_Learning-XGBoost_%7C_LightGBM-orange?style=for-the-badge)
![Power BI](https://img.shields.io/badge/Power_BI-DAX_%7C_Data_Modeling-yellow?style=for-the-badge&logo=powerbi&logoColor=black)
![Streamlit](https://img.shields.io/badge/Streamlit-Prescriptive_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Data_Engineering-Pandas_%7C_NumPy-150458?style=for-the-badge&logo=pandas&logoColor=white)

> **De la gestión reactiva a la anticipación estratégica.**
> HealthDemand es una solución analítica *End-to-End* diseñada para redes hospitalarias. Combina modelos de Machine Learning y Business Intelligence para predecir la demanda de pacientes, mitigar el impacto del ausentismo médico (No-Show) y simular la reasignación operativa de recursos en tiempo real.

---

## 🚀 Impacto y Valor de Negocio

La planificación tradicional de turnos suele ser a ciegas, basándose en la experiencia en lugar de la evidencia. Esto genera agendas médicas saturadas, tiempos de espera insostenibles o, por el contrario, consultorios vacíos que representan fugas de capital.

**HealthDemand resuelve esto respondiendo tres preguntas críticas:**
1. **¿Cuántos pacientes reales cruzarán la puerta?** (Pronóstico de demanda neta).
2. **¿Quiénes tienen mayor riesgo de no asistir?** (Clasificación probabilística de No-Show).
3. **¿Qué hacemos hoy para evitar el colapso de la próxima semana?** (Simulación operativa "What-If").

---

## 🧠 Arquitectura del Sistema (Pipeline Analítico)

El proyecto aborda el ciclo completo del dato, desde la extracción transaccional hasta la toma de decisiones gerenciales, dividido en 4 pilares:

### 1. Data Engineering & Feature Engineering
*   **Procesamiento Transaccional:** Limpieza y consolidación de un historial de 150,000 registros (2023-2025).
*   **Target Encoding & Lags Temporales:** Construcción de variables complejas como el *Lead Time* (anticipación de reserva), promedios móviles semanales y riesgo histórico ponderado por especialidad médica.

### 2. Dual Machine Learning Modeling
Para capturar la naturaleza del problema, se implementó una arquitectura de doble modelo:
*   **Modelo de Riesgo (XGBoost Classifier):** Entrenado con `scale_pos_weight` para lidiar con el desbalance de clases, predice la probabilidad individual de que un paciente falte a su cita, permitiendo a la clínica ejecutar estrategias de *overbooking* seguro.
*   **Modelo de Demanda (LightGBM Regressor):** Algoritmo de series temporales que pronostica el volumen bruto diario de solicitudes por Sede y Especialidad médica.

### 3. Capa de Business Intelligence (Power BI)
*   **Modelado Dimensional:** Diseño de un esquema de estrella (Star Schema) óptimo para filtrado cruzado.
*   **Métricas Dinámicas (DAX):** Cálculo en tiempo real de la *Brecha de Capacidad*, *Tasa de Utilización* y un motor de semaforización condicional que alerta sobre la inminente saturación o subutilización de las sedes.

### 4. Entorno de Simulación Prescriptiva (Streamlit)
*   **Control Room Interactivo:** Una aplicación web donde el responsable de planificación no solo visualiza las alertas de colapso, sino que puede inyectar capacidad virtual (ej. sumar +2 médicos a la guardia) a través de controles deslizantes, observando cómo la curva de recursos se estabiliza instantáneamente sobre la curva de demanda.

---

## 📊 Vistas del Sistema

*(Nota: Agrega aquí las capturas de pantalla de tu proyecto)*

### 1. Dashboard Ejecutivo (Power BI)
![Dashboard Ejecutivo Placeholder](https://via.placeholder.com/800x400/150458/FFFFFF?text=Insertar+Captura+del+Dashboard+de+Power+BI+Aqui)
> *Monitoreo macroscópico de la tasa de ocupación global, crecimiento proyectado de especialidades y déficit de turnos a 30 días.*

### 2. Simulador Operativo (Streamlit)
![Streamlit App Placeholder](https://via.placeholder.com/800x400/FF4B4B/FFFFFF?text=Insertar+Captura+de+la+App+de+Streamlit+Aqui)
> *Interfaz de ajuste de recursos. Las líneas rojas de saturación se neutralizan dinámicamente al asignar personal de refuerzo.*

---

## 📂 Estructura del Repositorio

```bash
HealthDemand/
│
├── 📁 data/
│   ├── raw/                        # Historial transaccional bruto
│   └── processed/                  # Datasets con Feature Engineering aplicado
│
├── 📁 notebooks/
│   ├── 01_Exploratory_Data_Analysis.ipynb  # Detección de estacionalidad y patrones de No-Show
│   ├── 02_Feature_Engineering.ipynb        # Creación de variables rezagadas y cíclicas
│   ├── 03_XGBoost_Classification.ipynb     # Entrenamiento y evaluación (AUC/ROC)
│   └── 04_LightGBM_Forecasting.ipynb       # Pronóstico temporal de demanda de pacientes
│
├── 📁 bi_dashboard/
│   └── HealthDemand_ControlRoom.pbix       # Archivo fuente del tablero en Power BI
│
├── 📁 app/
│   ├── app.py                      # Código fuente de la aplicación Streamlit
│   └── requirements.txt            # Dependencias del entorno virtual
│
└── 📄 README.md                    # Documentación del proyecto
