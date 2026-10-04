import pandas as pd
import numpy as np

# 1. Carga de datos y parseo de fechas
df = pd.read_csv('healthdemand_historico_23_25.csv', parse_dates=['fecha_solicitud', 'fecha_hora_turno'])

# ==============================================================================
# FRENTE 1: FEATURES PARA MODELO DE CLASIFICACIÓN (Predicción de Ausentismo)
# ==============================================================================

# A. Componentes Temporales Cíclicos
df['mes'] = df['fecha_hora_turno'].dt.month
df['dia_semana'] = df['fecha_hora_turno'].dt.weekday  # 0=Lunes, 6=Domingo
df['hora_dia'] = df['fecha_hora_turno'].dt.hour
df['es_fin_semana'] = np.where(df['dia_semana'] >= 5, 1, 0)

# B. Características Comportamentales (Lead Time)
df['lead_time_dias'] = (df['fecha_hora_turno'] - df['fecha_solicitud']).dt.days

# C. Target Encoding Preventivo (Tasas Históricas)
# Calcula la tasa de ausentismo global por especialidad para inyectar contexto
tasa_ausentismo = df[df['estado_turno'] == 'Ausente'].groupby('especialidad').size() / df.groupby('especialidad').size()
df['tasa_hist_ausentismo_esp'] = df['especialidad'].map(tasa_ausentismo)

# D. Optimización de Tipos para LightGBM/XGBoost
# Convertir strings a variables categóricas nativas
cat_cols = ['sede', 'especialidad', 'id_profesional', 'tipo_atencion', 'estado_turno']
for col in cat_cols:
    df[col] = df[col].astype('category')

# ==============================================================================
# FRENTE 2: FEATURES PARA MODELO DE DEMANDA (Series Temporales)
# ==============================================================================

# A. Agrupación por Fecha, Sede y Especialidad
# Ignoramos turnos cancelados/ausentes para predecir la demanda real que requiere atención
df_atendidos = df[df['estado_turno'].isin(['Atendido', 'Reprogramado'])]

df_demanda = df_atendidos.groupby(
    [df_atendidos['fecha_hora_turno'].dt.date, 'sede', 'especialidad'],
    observed=True
).size().reset_index(name='demanda_total')

df_demanda.rename(columns={'fecha_hora_turno': 'fecha'}, inplace=True)
df_demanda['fecha'] = pd.to_datetime(df_demanda['fecha'])

# B. Creación de Variables Rezagadas (Lags)
# Ordenar cronológicamente es crítico antes de hacer shifts
df_demanda = df_demanda.sort_values(by=['sede', 'especialidad', 'fecha'])

# ¿Cuántos pacientes tuvimos hace 1 día, 7 días (misma semana pasada) y 14 días?
grupos_serie = df_demanda.groupby(['sede', 'especialidad'], observed=True)['demanda_total']

df_demanda['demanda_lag_1'] = grupos_serie.shift(1)
df_demanda['demanda_lag_7'] = grupos_serie.shift(7)
df_demanda['demanda_lag_14'] = grupos_serie.shift(14)

# C. Suavizado Estadístico (Rolling Windows)
# Promedio móvil de los últimos 7 días para capturar la tendencia de la semana
df_demanda['media_movil_7d'] = grupos_serie.transform(
    lambda x: x.rolling(window=7, min_periods=1).mean()
)

# Llenado de nulos generados por los desplazamientos temporales (solo en columnas numéricas/lag)
lag_cols = ['demanda_lag_1', 'demanda_lag_7', 'demanda_lag_14', 'media_movil_7d']
df_demanda[lag_cols] = df_demanda[lag_cols].fillna(0)

# Replicar características temporales en el dataset agregado
df_demanda['mes'] = df_demanda['fecha'].dt.month
df_demanda['dia_semana'] = df_demanda['fecha'].dt.weekday

print("Feature Engineering completado.")
print(f"Dimensiones del dataset de Clasificación (Transaccional): {df.shape}")
print(f"Dimensiones del dataset de Demanda (Series Temporales): {df_demanda.shape}")