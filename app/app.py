import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="HealthDemand | Simulador Operativo", layout="wide")
st.title("🏥 HealthDemand: Simulador de Capacidad (What-If)")
st.markdown("Ajusta la capacidad instalada en tiempo real para mitigar los cuellos de botella previstos por los modelos de Machine Learning.")

# 2. Ingesta de Datos (Caché para optimizar rendimiento)
@st.cache_data
def cargar_datos():
    # Cargar el archivo exportado en la Fase 3
    df = pd.read_csv('output_operativo_powerbi.csv')
    return df

df_operativo = cargar_datos()

# 3. Panel Lateral (Filtros Estratégicos)
st.sidebar.header("Filtros de Escenario")
sede_sel = st.sidebar.selectbox("Seleccione Sede:", df_operativo['sede'].unique())
esp_sel = st.sidebar.selectbox("Seleccione Especialidad:", df_operativo['especialidad'].unique())

# Filtrar el dataset según la selección
df_filtrado = df_operativo[(df_operativo['sede'] == sede_sel) & (df_operativo['especialidad'] == esp_sel)].copy()

# Seleccionar un día en particular para el análisis profundo
fecha_sel = st.sidebar.selectbox("Seleccione Fecha Crítica:", df_filtrado['fecha'].unique())
df_dia = df_filtrado[df_filtrado['fecha'] == fecha_sel].iloc[0]

# 4. Variables Actuales (El problema)
demanda_neta = df_dia['demanda_neta_esperada']
capacidad_actual = df_dia['capacidad_diaria']
ocupacion_actual = df_dia['tasa_utilizacion']
alerta_actual = df_dia['alerta_operativa']

# 5. Simulador "What-If" (La solución)
st.subheader(f"Diagnóstico para {esp_sel} en {sede_sel} ({fecha_sel})")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Ajuste de Personal")
    # Cada médico extra aporta, por ejemplo, 15 turnos diarios a la capacidad
    turnos_por_medico = 15 
    medicos_extra = st.slider("Asignar Médicos Adicionales:", min_value=0, max_value=5, value=0, step=1)
    
    capacidad_simulada = capacidad_actual + (medicos_extra * turnos_por_medico)
    ocupacion_simulada = demanda_neta / capacidad_simulada

with col2:
    st.markdown("### Impacto Operativo")
    kpi1, kpi2, kpi3 = st.columns(3)
    
    kpi1.metric(label="Demanda Neta (Proyectada)", value=int(demanda_neta))
    
    # Usamos delta para mostrar la mejora
    delta_cap = int(capacidad_simulada - capacidad_actual)
    kpi2.metric(label="Capacidad Diaria", value=int(capacidad_simulada), delta=delta_cap)
    
    # Delta negativo es bueno en la saturación
    delta_ocupacion = (ocupacion_simulada - ocupacion_actual) * 100
    kpi3.metric(label="Tasa de Ocupación", value=f"{ocupacion_simulada:.1%}", delta=f"{delta_ocupacion:.1f}%", delta_color="inverse")

# 6. Visualización del impacto
st.markdown("---")
st.markdown("### Proyección de Capacidad vs Demanda")

# Preparar datos para el gráfico
datos_grafico = pd.DataFrame({
    'Escenario': ['1. Original (Sin Intervención)', '2. Simulado (Con Ajuste)'],
    'Capacidad': [capacidad_actual, capacidad_simulada],
    'Demanda Constante': [demanda_neta, demanda_neta]
})

fig = px.bar(datos_grafico, x='Escenario', y=['Capacidad', 'Demanda Constante'], 
             barmode='group', title="Cierre de la Brecha Operativa",
             color_discrete_sequence=['#1f77b4', '#d62728'])
st.plotly_chart(fig, use_container_width=True)

if ocupacion_simulada > 0.90:
    st.error("⚠️ La operación sigue en riesgo de saturación. Necesitas asignar más médicos.")
elif ocupacion_simulada < 0.50:
    st.warning("⚠️ Subutilización de recursos. Estás asignando demasiados médicos para la demanda proyectada.")
else:
    st.success("✅ Operación estabilizada. La tasa de ocupación es óptima.")