import pandas as pd
import numpy as np
import uuid

# Configuración inicial para reproducibilidad
np.random.seed(42)
n_registros = 150000

# 1. Definición de rangos de fechas (2023 a 2025)
fecha_inicio = pd.to_datetime('2023-01-01')
fecha_fin = pd.to_datetime('2025-12-31')
dias_totales = (fecha_fin - fecha_inicio).days

# Generación de fechas aleatorias
dias_aleatorios = np.random.randint(0, dias_totales + 1, n_registros)
fechas_base = fecha_inicio + pd.to_timedelta(dias_aleatorios, unit='D')

# Generación de horas operativas (8:00 a 19:45)
horas = np.random.randint(8, 20, n_registros)
minutos = np.random.choice([0, 15, 30, 45], n_registros)
fechas_hora_turno = fechas_base + pd.to_timedelta(horas, unit='h') + pd.to_timedelta(minutos, unit='m')

# 2. Variables categóricas
sedes = ['Sede Central', 'Sede Norte', 'Sede Sur', 'Sede Este']
especialidades = ['Cardiología', 'Pediatría', 'Clínica Médica', 'Psiquiatría', 'Oncología', 'Traumatología', 'Dermatología', 'Ginecología']
tipos_atencion = ['Primera vez', 'Control', 'Urgencia', 'Receta']

# 3. Construcción del DataFrame base
df = pd.DataFrame({
    'id_turno': [str(uuid.uuid4()) for _ in range(n_registros)], # Sin duplicados
    'fecha_hora_turno': fechas_hora_turno,
    'sede': np.random.choice(sedes, n_registros, p=[0.4, 0.25, 0.2, 0.15]), # Central tiene más volumen
    'especialidad': np.random.choice(especialidades, n_registros),
    'id_profesional': ['MED-' + str(np.random.randint(100, 199)) for _ in range(n_registros)],
    'tipo_atencion': np.random.choice(tipos_atencion, n_registros, p=[0.3, 0.5, 0.1, 0.1])
})

# 4. Inyección de Lead Time (Días de anticipación)
# Las urgencias se piden con 0-1 días, los controles pueden tener hasta 60 días.
dias_anticipacion = np.where(
    df['tipo_atencion'] == 'Urgencia', 
    np.random.randint(0, 2, n_registros), 
    np.random.randint(1, 60, n_registros)
)
df['fecha_solicitud'] = df['fecha_hora_turno'] - pd.to_timedelta(dias_anticipacion, unit='D')

# 5. Lógica Vectorizada para Estado del Turno (Inyección de Patrones Reales)
# Esto simula el comportamiento de ausentismo y cancelaciones basándose en variables reales.
condiciones = [
    # Condición 1: Urgencias casi nunca faltan, a veces cancelan
    (df['tipo_atencion'] == 'Urgencia'),
    
    # Condición 2: Turnos con mucha anticipación (Lead Time > 30) tienen alto No-Show
    (df['fecha_hora_turno'] - df['fecha_solicitud']).dt.days > 30,
    
    # Condición 3: Psiquiatría tiene mayor tasa de ausentismo histórico
    (df['especialidad'] == 'Psiquiatría'),
    
    # Condición 4: Viernes por la tarde (día 4, hora >= 15) tienen más cancelaciones
    (df['fecha_hora_turno'].dt.weekday == 4) & (df['fecha_hora_turno'].dt.hour >= 15),
    
    # Condición 5: Oncología tiene un nivel de asistencia casi perfecto
    (df['especialidad'] == 'Oncología')
]

# Opciones de probabilidad por cada condición (Atendido, Ausente, Cancelado, Reprogramado)
opciones = [
    np.random.choice(['Atendido', 'Ausente', 'Cancelado', 'Reprogramado'], n_registros, p=[0.90, 0.02, 0.05, 0.03]), # Urgencias
    np.random.choice(['Atendido', 'Ausente', 'Cancelado', 'Reprogramado'], n_registros, p=[0.55, 0.25, 0.10, 0.10]), # Lead time alto
    np.random.choice(['Atendido', 'Ausente', 'Cancelado', 'Reprogramado'], n_registros, p=[0.60, 0.20, 0.10, 0.10]), # Psiquiatría
    np.random.choice(['Atendido', 'Ausente', 'Cancelado', 'Reprogramado'], n_registros, p=[0.65, 0.10, 0.20, 0.05]), # Viernes PM
    np.random.choice(['Atendido', 'Ausente', 'Cancelado', 'Reprogramado'], n_registros, p=[0.95, 0.01, 0.02, 0.02])  # Oncología
]

# Estado por defecto si no cae en ninguna condición específica (Comportamiento normal)
estado_default = np.random.choice(['Atendido', 'Ausente', 'Cancelado', 'Reprogramado'], n_registros, p=[0.75, 0.10, 0.10, 0.05])

df['estado_turno'] = np.select(condiciones, opciones, default=estado_default)

# 6. Ordenar cronológicamente y limpiar columnas
df = df.sort_values(['fecha_hora_turno']).reset_index(drop=True)

# Reordenar columnas para mejor lectura
columnas_orden = ['id_turno', 'fecha_solicitud', 'fecha_hora_turno', 'sede', 'especialidad', 'id_profesional', 'tipo_atencion', 'estado_turno']
df = df[columnas_orden]

# 7. Validaciones
assert df.isnull().sum().sum() == 0, "Hay valores nulos en el dataset."
assert df['id_turno'].nunique() == len(df), "Hay IDs duplicados."

# Exportar a CSV
nombre_archivo = 'healthdemand_historico_23_25.csv'
df.to_csv(nombre_archivo, index=False)

print(f"✅ Dataset exportado exitosamente: {nombre_archivo}")
print(f"📊 Total de registros: {len(df)}")
print(f"📅 Rango de fechas: {df['fecha_hora_turno'].min().date()} al {df['fecha_hora_turno'].max().date()}")
print("\nDistribución de Estados:")
print(df['estado_turno'].value_counts(normalize=True) * 100)