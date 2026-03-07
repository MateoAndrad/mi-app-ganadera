import streamlit as st
import pandas as pd
from io import BytesIO

# 1. CONFIGURACIÓN DE PÁGINA
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

# --- LÓGICA DE CÁLCULO GENERAL ---
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

# ---------------------------------------------------------
# APARTADO 1: SIMULADOR INDIVIDUAL (TODO LO ANTERIOR)
# ---------------------------------------------------------
if menu == "Simulador Individual":
    st.title("🐄 Simulador Individual de Viabilidad")
    
    st.sidebar.header("💰 Configuración Global")
    alimento_ha = st.sidebar.number_input("Alimento (kg MS/ha/año)", value=5000)
    superficie = st.sidebar.number_input("Hectáreas", value=1.0)
    
    # Flete Editable
    st.sidebar.subheader("🚚 Flete")
    distancia = st.sidebar.number_input("Distancia (km)", value=100)
    precio_diesel = st.sidebar.number_input("Diesel ($/L)", value=1100)
    rendimiento = st.sidebar.number_input("Rendimiento (km/L)", value=4.0)
    costo_flete = (distancia / rendimiento * precio_diesel)
    
    col1, col2 = st.columns(2)
    with col1:
        raza = st.selectbox("Raza", list(RAZAS.keys()))
        tipo_pasto = st.selectbox("Pasto", ["Pradera Natural Degradada", "Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa", "Feedlot"])
        num_ani = st.number_input("Animales", value=1, min_value=1)
    with col2:
        peso_i = st.number_input("Peso Ini (kg)", value=220.0)
        p_compra = st.number_input("Precio Compra ($/kg)", value=1900)
        p_venta = st.number_input("Precio Venta Proyectado ($/kg)", value=2150)
        dias_e = st.slider("Días", 30, 365, 120)

    p_fin, cap_max, util, inv = calcular_todo(raza, peso_i, p_compra, dias_e, tipo_pasto, alimento_ha, superficie, num_ani, costo_flete, 600, 18000, p_venta)
    
    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("Peso Final", f"{p_fin:.1f} kg")
    res2.metric("Capacidad Máx", f"{cap_max} Cabezas")
    res3.metric("Utilidad Total", f"${util:,.0f} CLP")

    if num_ani > cap_max: st.error(f"⚠️ SOBREPASTOREO: Máximo {cap_max}")
    elif util > 0: st.success("✅ VIABLE"); st.balloons()
    else: st.error("❌ PÉRDIDA")

# ---------------------------------------------------------
# APARTADO 2: COMPARADOR DE ESCENARIOS (NUEVO)
# ---------------------------------------------------------
elif menu == "Comparador de Escenarios":
    st.title("⚖️ Comparador de Negocios")
    st.write("Compara dos opciones distintas (diferentes razas, pastos o precios) con el mismo flete.")

    # Ajustes comunes (Flete)
    st.sidebar.header("🚚 Logística Común")
    dist = st.sidebar.number_input("Distancia (km)", value=100)
    dies = st.sidebar.number_input("Diesel ($/L)", value=1100)
    flete_comun = (dist / 4.0 * dies)

    c1, c2 = st.columns(2)
    
    with c1:
        st.header("Escenario A")
        rA = st.selectbox("Raza A", list(RAZAS.keys()), key="ra")
        pastoA = st.selectbox("Pasto A", ["Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa"], key="pa")
        vA = st.number_input("Precio Venta A ($/kg)", value=2100, key="va")
        pfA, cpA, utA, invA = calcular_todo(rA, 220, 1900, 120, pastoA, 5000, 1, 10, flete_comun, 600, 18000, vA)
        st.metric("Utilidad A", f"${utA:,.0f}")

    with c2:
        st.header("Escenario B")
        rB = st.selectbox("Raza B", list(RAZAS.keys()), key="rb")
        pastoB = st.selectbox("Pasto B", ["Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa"], key="pb")
        vB = st.number_input("Precio Venta B ($/kg)", value=2100, key="vb")
        pfB, cpB, utB, invB = calcular_todo(rB, 220, 1900, 120, pastoB, 5000, 1, 10, flete_comun, 600, 18000, vB)
        st.metric("Utilidad B", f"${utB:,.0f}")

    st.divider()
    st.subheader("🏆 Veredicto Ganador")
    if utA > utB: st.success(f"El Escenario A ({rA}) es más rentable por una diferencia de ${utA-utB:,.0f} CLP")
    else: st.success(f"El Escenario B ({rB}) es más rentable por una diferencia de ${utB-utA:,.0f} CLP")
    
    # Gráfico comparativo
    st.bar_chart({"Escenario A": utA, "Escenario B": utB})
