import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="GanadoPro Chile - Análisis de Viabilidad", page_icon="📈")

st.title("🐄 Simulador de Viabilidad Ganadera (CLP)")

# --- BASE DE DATOS DE RAZAS Y GENÉTICA ---
RAZAS = {
    # --- CARNICERAS EUROPEAS (Alta eficiencia) ---
    "Aberdeen Angus": 1.10, 
    "Hereford": 1.05, 
    "Charolais": 1.15, 
    "Limousin": 1.12, 
    "Shorthorn": 1.02,
    "Blonda de Aquitania": 1.14,
    "Rubia Gallega": 1.08,
    "Wagyu (Kobe)": 0.95,

    # --- DOBLE PROPÓSITO ---
    "Simmental": 1.08, 
    "Normando": 0.98,
    "Parda Suiza (Braunvieh)": 1.00,
    "Fleckvieh": 1.07,

    # --- CEBUINAS (Resistentes al calor) ---
    "Brahman": 0.90, 
    "Nelore": 0.88, 
    "Guzerat": 0.89,
    "Gyr": 0.82,
    "Indubrasil": 0.87,

    # --- SINTÉTICAS (Cruzas) ---
    "Brangus": 1.02, 
    "Braford": 1.00, 
    "Santa Gertrudis": 0.97,
    "Beefmaster": 1.01,
    "Girolando": 0.85,

    # --- LECHERAS (Baja ganancia de carne) ---
    "Holstein": 0.75, 
    "Jersey": 0.65,
    "Ayrshire": 0.72
}

# --- SIDEBAR: DATOS DEL CAMPO Y COSTOS (EN CLP) ---
st.sidebar.header("💰 Costos del Campo (CLP)")
# Ajustado a un valor promedio de talaje/manejo en Chile
costo_fijo_dia = st.sidebar.number_input("Costo operativo diario por animal ($ CLP)", value=600, help="Incluye personal, agua, mantenimiento.")
# Ajustado a costo de vacunas y desparasitación promedio
costo_sanidad = st.sidebar.number_input("Gasto en vacunas/medicina por animal ($ CLP)", value=18000)

tipo_pasto = st.sidebar.selectbox(
    "Calidad del Pasto", 
    ["Pobre (Natural)", "Media (Mejorado)", "Excelente (Pastura)"]
)
gdp_base = {"Pobre (Natural)": 0.35, "Media (Mejorado)": 0.65, "Excelente (Pastura)": 0.95}

# --- DATOS DEL ANIMAL ---
col1, col2 = st.columns(2)
with col1:
    raza = st.selectbox("Raza", list(RAZAS.keys()))
    peso_ini = st.number_input("Peso Inicial (kg)", value=220.0)
with col2:
    # Precio de compra por kilo vivo promedio en ferias chilenas
    precio_compra = st.number_input("Precio Compra ($ CLP/kg)", value=1900)
    dias = st.slider("Días de estadía", 30, 365, 120)

# --- CÁLCULOS CRÍTICOS ---
# 1. Crecimiento
gdp_final = gdp_base[tipo_pasto] * RAZAS[raza]
peso_fin = peso_ini + (gdp_final * dias)

# 2. Finanzas (Inversión vs Venta)
inversion_animal = peso_ini * precio_compra
costos_operativos = (costo_fijo_dia * dias) + costo_sanidad
total_invertido = inversion_animal + costos_operativos

# Proyectamos precio de venta (estimado conservador para Chile)
precio_venta_proyectado = precio_compra * 1.12 
ingreso_total = peso_fin * precio_venta_proyectado
utilidad_neta = ingreso_total - total_invertido
margen_porcentaje = (utilidad_neta / total_invertido) * 100 if total_invertido > 0 else 0

# --- RESULTADOS Y VEREDICTO ---
st.divider()
st.header("📊 Análisis de Rentabilidad")

# Métricas principales con formato de separador de miles para CLP
m1, m2, m3 = st.columns(3)
m1.metric("Peso Final Est.", f"{peso_fin:.1f} kg")
m2.metric("Inversión Total", f"${total_invertido:,.0f} CLP")
m3.metric("Ganancia Neta", f"${utilidad_neta:,.0f} CLP", f"{margen_porcentaje:.1f}% ROI")

# --- EL SEMÁFORO DE VIABILIDAD ---
if utilidad_neta > (total_invertido * 0.15): # Si ganas más del 15%
    st.success(f"✅ **PROYECTO VIABLE:** La rentabilidad es alta. Con {raza} en este pasto, el negocio es sólido.")
    st.balloons()
elif utilidad_neta > 0: # Si ganas pero muy poco
    st.warning(f"⚠️ **RIESGO MODERADO:** Hay ganancia, pero el margen es bajo ({margen_porcentaje:.1f}%). Un aumento en el precio del forraje o baja en la feria podría darte pérdidas.")
else: # Si pierdes dinero
    st.error(f"❌ **PROYECTO NO VIABLE:** Estás perdiendo ${abs(utilidad_neta):,.0f} CLP por animal. Los costos operativos superan el crecimiento del peso.")

# --- FUNCIÓN DE DESCARGA EXCEL ---
st.subheader("📥 Descargar Reporte")

# Crear tabla de datos para el Excel
df_reporte = pd.DataFrame({
    "Descripción": [
        "Raza seleccionada", "Pasto", "Días de estadía", "Peso inicial", 
        "Peso final estimado", "Ganancia de peso diaria", "Precio compra p/kg", 
        "Costo operativo total", "Inversión total", "Ingreso venta estimado", 
        "Utilidad Neta", "Rentabilidad (ROI)"
    ],
    "Valor": [
        raza, tipo_pasto, dias, f"{peso_ini} kg", 
        f"{peso_fin:.1f} kg", f"{gdp_final:.2f} kg/día", f"${precio_compra} CLP",
        f"${costos_operativos:,.0f} CLP", f"${total_invertido:,.0f} CLP", f"${ingreso_total:,.0f} CLP",
        f"${utilidad_neta:,.0f} CLP", f"{margen_porcentaje:.1f}%"
    ]
})

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

excel_data = to_excel(df_reporte)

st.download_button(
    label="📊 Descargar Informe en Excel",
    data=excel_data,
    file_name=f"Informe_{raza}_{dias}dias.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Gráfico de Punto de Equilibrio
st.write("### Crecimiento Proyectado")
st.line_chart({"Días": [0, dias], "Peso (kg)": [peso_ini, peso_fin]}, x="Días", y="Peso (kg)")