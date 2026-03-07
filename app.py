import streamlit as st
import pandas as pd
from io import BytesIO

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="GanadoPro Chile - Gestión Total", page_icon="logo.png", layout="wide")

# 2. LOGO EN LA BARRA LATERAL
st.sidebar.image("logo.png", use_container_width=True)

st.title("🐄 Simulador de Viabilidad, Carga y Logística")

# 3. BASE DE DATOS DE RAZAS
RAZAS = {
    "Clavel / Overo Colorado": 1.08, "Aberdeen Angus": 1.10, "Hereford": 1.05, 
    "Holstein (Lechero)": 0.75, "Charolais": 1.15, "Limousin": 1.12, "Simmental": 1.08,
    "Normando": 0.98, "Parda Suiza": 1.00, "Brahman": 0.90, "Brangus": 1.02, "Wagyu": 0.95
}

# 4. SIDEBAR: DATOS DEL CAMPO Y LOGÍSTICA
st.sidebar.header("💰 Datos del Campo y Alimento")
alimento_ha = st.sidebar.number_input("Alimento generado (kg MS/ha/año)", value=5000)
superficie = st.sidebar.number_input("Superficie del potrero (Hectáreas)", value=1.0, min_value=0.1)

# --- NUEVA SECCIÓN: CALCULADORA DE FLETE EDITABLE ---
st.sidebar.subheader("🚚 Calculadora de Flete")
metodo_flete = st.sidebar.radio("Método de costo:", ["Monto Fijo", "Calcular por Distancia"])

if metodo_flete == "Monto Fijo":
    costo_flete_total = st.sidebar.number_input("Costo total flete $", value=0)
else:
    distancia = st.sidebar.number_input("Distancia ida y vuelta (km)", value=100)
    precio_diesel = st.sidebar.number_input("Precio Diesel ($/Litro)", value=1100) # Editable
    rendimiento = st.sidebar.number_input("Rendimiento Camión (km/L)", value=4.0)
    peajes = st.sidebar.number_input("Gastos Peajes/Otros $", value=0)
    
    # Fórmula: (Distancia / Rendimiento * Precio Diesel) + Peajes
    costo_flete_total = (distancia / rendimiento * precio_diesel) + peajes
    st.sidebar.info(f"Costo estimado: ${costo_flete_total:,.0f} CLP")

# ----------------------------------------------------

tipo_pasto = st.sidebar.selectbox(
    "Calidad y Tipo de Pastura", 
    ["Pradera Natural Degradada", "Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa", "Feedlot"]
)

gdp_base = {
    "Pradera Natural Degradada": 0.30, "Pradera Natural Mejorada": 0.55, 
    "Pastura Sembrada": 0.85, "Alfalfa": 1.05, "Feedlot": 1.30
}

costo_fijo_dia = st.sidebar.number_input("Costo diario x animal ($ CLP)", value=600)
costo_sanidad = st.sidebar.number_input("Gasto sanidad x animal ($ CLP)", value=18000)

# 5. ENTRADA DE DATOS DEL ANIMAL
col1, col2 = st.columns(2)
with col1:
    raza = st.selectbox("Selecciona la Raza", list(RAZAS.keys()))
    peso_ini = st.number_input("Peso Inicial (kg)", value=220.0)
    num_animales = st.number_input("Cantidad de animales a ingresar", value=1, min_value=1)
with col2:
    precio_compra = st.number_input("Precio Compra ($ CLP/kg)", value=1900)
    dias = st.slider("Días de estadía", 30, 365, 120)
    precio_venta_proy = st.number_input("Precio Venta Proyectado ($ CLP/kg)", value=2150)

# 6. CÁLCULOS
gdp_final = gdp_base[tipo_pasto] * RAZAS[raza]
peso_fin = peso_ini + (gdp_final * dias)

# Capacidad de Carga
peso_promedio = (peso_ini + peso_fin) / 2
consumo_total_periodo = (peso_promedio * 0.03) * dias
alimento_disponible = (alimento_ha * superficie) * 0.70
capacidad_max = int(alimento_disponible / consumo_total_periodo) if consumo_total_periodo > 0 else 0

# Finanzas Reales
inversion_base = ((peso_ini * precio_compra) + (costo_fijo_dia * dias) + costo_sanidad) * num_animales
inversion_con_flete = inversion_base + costo_flete_total

ingreso_total = (peso_fin * precio_venta_proy) * num_animales
utilidad_total = ingreso_total - inversion_con_flete
utilidad_animal = utilidad_total / num_animales if num_animales > 0 else 0
roi = (utilidad_total / inversion_con_flete) * 100 if inversion_con_flete > 0 else 0

# 7. RESULTADOS
st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Peso Final", f"{peso_fin:.1f} kg")
c2.metric("Capacidad Máx.", f"{capacidad_max} Cabezas")
c3.metric("Utilidad/Animal (Post-Flete)", f"${utilidad_animal:,.0f} CLP")
c4.metric("Utilidad Total Lote", f"${utilidad_total:,.0f} CLP")

# 8. ALERTAS
if num_animales > capacidad_max and capacidad_max > 0:
    st.error(f"⚠️ **SOBREPASTOREO:** Solo tienes pasto para {capacidad_max} animales.")
elif utilidad_total > (inversion_con_flete * 0.15):
    st.success(f"✅ **PROYECTO VIABLE** (ROI: {roi:.1f}%)")
    st.balloons()
elif utilidad_total > 0:
    st.warning(f"⚠️ **RIESGO MODERADO** (ROI: {roi:.1f}%)")
else:
    st.error("❌ **PÉRDIDA ECONÓMICA**")

# 9. EXCEL Y GRÁFICO
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

df_rep = pd.DataFrame({
    "Dato": ["Raza", "Animales", "Costo Flete", "Peso Final", "Utilidad Total"],
    "Valor": [raza, num_animales, f"${costo_flete_total:,.0f}", f"{peso_fin:.1f} kg", f"${utilidad_total:,.0f}"]
})
st.download_button("📥 Descargar Informe", data=to_excel(df_rep), file_name="analisis_ganadero.xlsx")
st.line_chart({"Evolución Peso (kg)": [peso_ini, peso_fin]})
