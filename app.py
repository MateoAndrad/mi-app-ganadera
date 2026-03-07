import streamlit as st
import pandas as pd
from io import BytesIO

# 1. CONFIGURACIÓN DE PÁGINA Y FAVICON
st.set_page_config(page_title="GanadoPro Chile - Gestión Total", page_icon="logo.png", layout="wide")

# 2. LOGO Y NAVEGACIÓN
st.sidebar.image("logo.png", use_container_width=True)
menu = st.sidebar.radio("Ir a:", ["Simulador Individual", "Comparador de Escenarios"])

# --- BASE DE DATOS DE RAZAS ---
RAZAS = {
    "Clavel / Overo Colorado": 1.08, "Aberdeen Angus": 1.10, "Hereford": 1.05, 
    "Holstein (Lechero)": 0.75, "Charolais": 1.15, "Limousin": 1.12, "Simmental": 1.08,
    "Normando": 0.98, "Parda Suiza": 1.00, "Brahman": 0.90, "Brangus": 1.02, "Wagyu": 0.95
}

# --- FUNCIÓN DE CÁLCULO MAESTRA ---
def calcular_todo(raza, peso_ini, precio_compra, dias, tipo_pasto, alimento_ha, superficie, num_animales, costo_flete, costo_fijo_dia, costo_sanidad, precio_venta):
    gdp_base = {"Pradera Natural Degradada": 0.30, "Pradera Natural Mejorada": 0.55, "Pastura Sembrada": 0.85, "Alfalfa": 1.05, "Feedlot": 1.30}
    gdp_final = gdp_base[tipo_pasto] * RAZAS[raza]
    peso_fin = peso_ini + (gdp_final * dias)
    
    # Capacidad de Carga
    peso_promedio = (peso_ini + peso_fin) / 2
    consumo_total = (peso_promedio * 0.03) * dias
    alimento_disponible = (alimento_ha * superficie) * 0.70
    capacidad_max = int(alimento_disponible / consumo_total) if consumo_total > 0 else 0
    
    # Finanzas
    inv_total = ((peso_ini * precio_compra) + (costo_fijo_dia * dias) + costo_sanidad) * num_animales + costo_flete
    ingreso_total = (peso_fin * precio_venta) * num_animales
    utilidad = ingreso_total - inv_total
    return peso_fin, capacidad_max, utilidad, inv_total

# --- FUNCIÓN PARA EXCEL ---
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

# ---------------------------------------------------------
# APARTADO 1: SIMULADOR INDIVIDUAL
# ---------------------------------------------------------
if menu == "Simulador Individual":
    st.title("🐄 Simulador Individual de Viabilidad")
    
    st.sidebar.header("💰 Configuración Global")
    al_ha = st.sidebar.number_input("Alimento (kg MS/ha/año)", value=5000)
    sup = st.sidebar.number_input("Hectáreas", value=1.0)
    
    st.sidebar.subheader("🚚 Flete Editable")
    dist = st.sidebar.number_input("Distancia (km)", value=100)
    dies = st.sidebar.number_input("Diesel ($/L)", value=1100)
    flete_ind = (dist / 4.0 * dies)
    
    col1, col2 = st.columns(2)
    with col1:
        rz = st.selectbox("Raza", list(RAZAS.keys()))
        pst = st.selectbox("Pasto", ["Pradera Natural Degradada", "Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa", "Feedlot"])
        n_ani = st.number_input("Cantidad de Animales", value=1, min_value=1)
    with col2:
        p_i = st.number_input("Peso Inicial (kg)", value=220.0)
        p_c = st.number_input("Precio Compra ($/kg)", value=1900)
        p_v = st.number_input("Precio Venta Proyectado ($/kg)", value=2150)
        d_e = st.slider("Días de estadía", 30, 365, 120)

    p_f, c_max, ut_total, inv_t = calcular_todo(rz, p_i, p_c, d_e, pst, al_ha, sup, n_ani, flete_ind, 600, 18000, p_v)
    
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Peso Final", f"{p_f:.1f} kg")
    m2.metric("Capacidad Máx", f"{c_max} Cabezas")
    m3.metric("Utilidad Total", f"${ut_total:,.0f} CLP")
    m4.metric("ROI", f"{(ut_total/inv_t)*100:.1f}%")

    if n_ani > c_max: st.error(f"⚠️ SOBREPASTOREO: Máximo {c_max}")
    elif ut_total > 0: st.success("✅ PROYECTO VIABLE"); st.balloons()
    else: st.error("❌ PÉRDIDA")

    # REPORTE EXCEL INDIVIDUAL
    df_ind = pd.DataFrame({"Dato": ["Raza", "Animales", "Peso Final", "Utilidad", "Flete"], 
                           "Valor": [rz, n_ani, f"{p_f:.1f} kg", f"${ut_total:,.0f}", f"${flete_ind:,.0f}"]})
    st.download_button("📥 Descargar Reporte Individual", data=to_excel(df_ind), file_name=f"Reporte_{rz}.xlsx")
    st.line_chart({"Peso (kg)": [p_i, p_f]})

# ---------------------------------------------------------
# APARTADO 2: COMPARADOR DE ESCENARIOS
# ---------------------------------------------------------
elif menu == "Comparador de Escenarios":
    st.title("⚖️ Comparador de Negocios")
    
    st.sidebar.header("🚚 Logística Común")
    dist_c = st.sidebar.number_input("Distancia (km)", value=100)
    dies_c = st.sidebar.number_input("Diesel ($/L)", value=1100)
    flete_c = (dist_c / 4.0 * dies_c)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Escenario A")
        rA = st.selectbox("Raza A", list(RAZAS.keys()), key="ra")
        pstA = st.selectbox("Pasto A", ["Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa"], key="pa")
        pfA, cpA, utA, invA = calcular_todo(rA, 220, 1900, 120, pstA, 5000, 1, 10, flete_c, 600, 18000, 2100)
        st.metric("Utilidad A", f"${utA:,.0f}")
    with c2:
        st.subheader("Escenario B")
        rB = st.selectbox("Raza B", list(RAZAS.keys()), key="rb")
        pstB = st.selectbox("Pasto B", ["Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa"], key="pb")
        pfB, cpB, utB, invB = calcular_todo(rB, 220, 1900, 120, pstB, 5000, 1, 10, flete_c, 600, 18000, 2100)
        st.metric("Utilidad B", f"${utB:,.0f}")

    # REPORTE EXCEL COMPARATIVO
    df_comp = pd.DataFrame({
        "Métrica": ["Raza", "Pasto", "Utilidad Total", "Diferencia"],
        "Escenario A": [rA, pstA, f"${utA:,.0f}", f"${utA-utB:,.0f}"],
        "Escenario B": [rB, pstB, f"${utB:,.0f}", f"${utB-utA:,.0f}"]
    })
    st.download_button("📥 Descargar Comparación (Excel)", data=to_excel(df_comp), file_name="Comparativa_Ganadera.xlsx")
    st.bar_chart({"Escenario A": utA, "Escenario B": utB})
