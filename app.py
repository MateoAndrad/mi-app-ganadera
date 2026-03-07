import streamlit as st
import pandas as pd
from io import BytesIO

# 1. CONFIGURACIÓN DE PÁGINA (Cambia el logo de la pestaña aquí)
st.set_page_config(
    page_title="GanadoPro Chile - Gestión Total", 
    page_icon="logo.png", 
    layout="wide"
)

# 2. LOGO EN LA BARRA LATERAL
# Asegúrate de que el archivo se llame exactamente "logo.png" en GitHub
st.sidebar.image("logo.png", use_container_width=True)

st.title("🐄 Simulador de Viabilidad, Carga y Gestión")

# 3. BASE DE DATOS DE RAZAS (Priorizando razas chilenas)
RAZAS = {
    "Clavel / Overo Colorado": 1.08, "Aberdeen Angus": 1.10, "Hereford": 1.05, 
    "Holstein (Lechero)": 0.75, "Charolais": 1.15, "Limousin": 1.12, "Simmental": 1.08,
    "Normando": 0.98, "Parda Suiza": 1.00, "Brahman": 0.90, "Brangus": 1.02, "Wagyu": 0.95
}

# 4. SIDEBAR: DATOS DEL CAMPO
st.sidebar.header("💰 Datos del Campo y Alimento")
alimento_ha = st.sidebar.number_input("Alimento generado (kg MS/ha/año)", value=5000)
superficie = st.sidebar.number_input("Superficie del potrero (Hectáreas)", value=1.0, min_value=0.1)

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
    num_animales_usuario = st.number_input("Cantidad de animales a ingresar", value=1, min_value=1)
with col2:
    precio_compra = st.number_input("Precio Compra ($ CLP/kg)", value=1900)
    dias = st.slider("Días de estadía", 30, 365, 120)
    precio_venta_proy = st.number_input("Precio Venta Proyectado ($ CLP/kg)", value=2150)

# 6. CÁLCULOS TÉCNICOS (CORREGIDOS)
gdp_final = gdp_base[tipo_pasto] * RAZAS[raza]
peso_fin = peso_ini + (gdp_final * dias)

# Capacidad de Carga
peso_promedio = (peso_ini + peso_fin) / 2
consumo_total_periodo = (peso_promedio * 0.03) * dias
alimento_disponible = (alimento_ha * superficie) * 0.70
capacidad_max = int(alimento_disponible / consumo_total_periodo) if consumo_total_periodo > 0 else 0

# Finanzas
inversion_unidad = (peso_ini * precio_compra) + (costo_fijo_dia * dias) + costo_sanidad
utilidad_unidad = (peso_fin * precio_venta_proy) - inversion_unidad
roi = (utilidad_unidad / inversion_unidad) * 100 if inversion_unidad > 0 else 0

# 7. RESULTADOS
st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Peso Final", f"{peso_fin:.1f} kg")
c2.metric("Capacidad Máx.", f"{capacidad_max} Cabezas")
c3.metric("Utilidad/Animal", f"${utilidad_unidad:,.0f} CLP")
c4.metric("ROI", f"{roi:.1f}%")

# 8. ALERTAS (CORREGIDO: Ya no se queda pegado)
if num_animales_usuario > capacidad_max and capacidad_max > 0:
    st.error(f"⚠️ **SOBREPASTOREO:** El campo solo soporta {capacidad_max} animales.")
elif utilidad_unidad > (inversion_unidad * 0.15):
    st.success("✅ **PROYECTO VIABLE**")
    st.balloons()
elif utilidad_unidad > 0:
    st.warning("⚠️ **RIESGO MODERADO:** Margen bajo de ganancia.")
else:
    st.error("❌ **PÉRDIDA ECONÓMICA**")

# 9. DESCARGA EXCEL
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

df_rep = pd.DataFrame({"Dato": ["Raza", "Utilidad Total"], "Valor": [raza, f"${utilidad_unidad*num_animales_usuario:,.0f}"]})
st.download_button("📥 Descargar Reporte", data=to_excel(df_rep), file_name="reporte.xlsx")

st.line_chart({"Peso (kg)": [peso_ini, peso_fin]})
