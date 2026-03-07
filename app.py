import streamlit as st
import pandas as pd
from io import BytesIO

# 1. CONFIGURACIÓN DE PÁGINA (Mantiene layout ancho)
st.set_page_config(page_title="GanadoPro Chile - Gestión Total", page_icon="📈", layout="wide")

st.title("🐄 Simulador de Viabilidad, Carga y Gestión (CLP)")

# 2. BASE DE DATOS DE RAZAS (Mantiene las 25 razas)
RAZAS = {
    "Aberdeen Angus": 1.10, "Hereford": 1.05, "Charolais": 1.15, "Limousin": 1.12, 
    "Shorthorn": 1.02, "Blonda de Aquitania": 1.14, "Rubia Gallega": 1.08, "Wagyu (Kobe)": 0.95,
    "Simmental": 1.08, "Normando": 0.98, "Parda Suiza": 1.00, "Fleckvieh": 1.07,
    "Brahman": 0.90, "Nelore": 0.88, "Guzerat": 0.89, "Gyr": 0.82, "Indubrasil": 0.87,
    "Brangus": 1.02, "Braford": 1.00, "Santa Gertrudis": 0.97, "Beefmaster": 1.01,
    "Girolando": 0.85, "Holstein": 0.75, "Jersey": 0.65, "Ayrshire": 0.72
}

# 3. SIDEBAR: DATOS DEL CAMPO (Nuevas funciones de exactitud y alimento)
st.sidebar.header("💰 Datos del Campo y Alimento")

alimento_ha = st.sidebar.number_input("Alimento generado (kg MS/ha/año)", value=5000, help="Producción total de materia seca por hectárea.")
superficie = st.sidebar.number_input("Superficie del potrero (Hectáreas)", value=1.0, min_value=0.1)

tipo_pasto = st.sidebar.selectbox(
    "Calidad y Tipo de Pastura", 
    [
        "Pradera Natural Degradada (Baja)", 
        "Pradera Natural Mejorada (Media)", 
        "Pastura Sembrada (Ballica/Trébol)", 
        "Alfalfa o Forraje de Corte", 
        "Suplementación Total (Feedlot)"
    ]
)

# Coeficientes GDP exactos
gdp_base = {
    "Pradera Natural Degradada (Baja)": 0.30, 
    "Pradera Natural Mejorada (Media)": 0.55, 
    "Pastura Sembrada (Ballica/Trébol)": 0.85, 
    "Alfalfa o Forraje de Corte": 1.05, 
    "Suplementación Total (Feedlot)": 1.30
}

costo_fijo_dia = st.sidebar.number_input("Costo operativo diario por animal ($ CLP)", value=600)
costo_sanidad = st.sidebar.number_input("Gasto en vacunas/medicina por animal ($ CLP)", value=18000)

# 4. ENTRADA DE DATOS DEL ANIMAL
col_a, col_b = st.columns(2)
with col_a:
    raza = st.selectbox("Raza", list(RAZAS.keys()))
    peso_ini = st.number_input("Peso Inicial (kg)", value=220.0)
    num_animales_usuario = st.number_input("Cantidad de animales que deseas meter", value=1, min_value=1)
with col_b:
    precio_compra = st.number_input("Precio Compra ($ CLP/kg)", value=1900)
    dias = st.slider("Días de estadía", 30, 365, 120)
    precio_venta_proy = st.number_input("Precio Venta Proyectado ($ CLP/kg)", value=2150)

# 5. CÁLCULOS TÉCNICOS
# Crecimiento
gdp_final = gdp_base[tipo_pasto] * RAZAS[raza]
peso_fin = peso_ini + (gdp_final * dias)

# Capacidad de Carga (Consumo 3% peso vivo y 70% eficiencia)
peso_promedio = (peso_ini + peso_fin) / 2
consumo_diario_ms = peso_promedio * 0.03
consumo_total_periodo_animal = consumo_diario_ms * dias
alimento_disponible_real = (alimento_ha * superficie) * 0.70
capacidad_max = int(alimento_disponible_real / consumo_total_periodo_animal) if consumo_total_periodo_animal > 0 else 0

# Finanzas
inversion_unidad = (peso_ini * precio_compra) + (costo_fijo_dia * dias) + costo_sanidad
ingreso_unidad = peso_fin * precio_venta_proy
utilidad_unidad = ingreso_unidad - inversion_unidad
roi = (utilidad_unidad / inversion_unidad) * 100 if inversion_animal > 0 else 0

# 6. RESULTADOS VISUALES
st.divider()
st.header("📊 Resultado de la Proyección")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Peso Final", f"{peso_fin:.1f} kg", f"+{peso_fin-peso_ini:.1f} kg")
c2.metric("Capacidad Máxima", f"{capacidad_max} Cabezas", help="Animales que tu pasto puede soportar.")
c3.metric("Utilidad/Animal", f"${utilidad_unidad:,.0f} CLP", f"{roi:.1f}% ROI")
c4.metric("Utilidad Total Lote", f"${(utilidad_unidad * num_animales_usuario):,.0f} CLP")

# 7. ALERTAS Y SEMÁFORO (Incluye Alerta de Sobrepastoreo)
if num_animales_usuario > capacidad_max and capacidad_max > 0:
    st.error(f"⚠️ **ALERTA DE SOBREPASTOREO:** Estás intentando meter {num_animales_usuario} animales, pero tu campo solo soporta {capacidad_max} para este periodo. El ganado perderá peso por falta de comida.")
elif utilidad_unidad > (inversion_unidad * 0.15):
    st.success(f"✅ **PROYECTO VIABLE:** Gran margen de utilidad y carga animal equilibrada.")
    st.balloons()
elif utilidad_neta > 0:
    st.warning("⚠️ **RIESGO MODERADO:** Hay ganancia, pero revisa la carga o los costos operativos.")
else:
    st.error("❌ **PÉRDIDA ECONÓMICA:** Los costos superan el crecimiento proyectado.")

# 8. EXPORTACIÓN A EXCEL (Mantiene la función)
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

df_reporte = pd.DataFrame({
    "Variable": ["Raza", "Tipo Pasto", "Capacidad Campo", "Animales a ingresar", "Utilidad/Animal", "Utilidad Total"],
    "Valor": [raza, tipo_pasto, capacidad_max, num_animales_usuario, f"${utilidad_unidad:,.0f}", f"${(utilidad_unidad * num_animales_usuario):,.0f}"]
})

st.download_button("📥 Descargar Reporte Excel", data=to_excel(df_reporte), file_name=f"Reporte_{raza}.xlsx")

# 9. GRÁFICO DE CRECIMIENTO
st.write("### Proyección de Peso")
st.line_chart({"Peso (kg)": [peso_ini, peso_fin]})