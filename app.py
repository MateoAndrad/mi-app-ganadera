import streamlit as st
import pandas as pd
from io import BytesIO

# 1. CONFIGURACIÓN DE PÁGINA (Favicon y Título)
st.set_page_config(
    page_title="GanadoPro Chile | Gestión Corporativa", 
    page_icon="logo.png", 
    layout="wide"
)

# 2. ESTILO PROFESIONAL (CSS corregido para visibilidad de letras)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    /* Estilo de las tarjetas de métricas */
    [data-testid="stMetricValue"] { color: #1f2937 !important; } /* Color del número principal */
    [data-testid="stMetricLabel"] { color: #4b5563 !important; } /* Color de la etiqueta superior */
    .stMetric { 
        background-color: #ffffff; 
        border: 1px solid #e0e0e0; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL (Navegación y Logo)
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("MENÚ DE GESTIÓN", ["📊 Simulador Individual", "⚖️ Comparador de Escenarios"])
    st.markdown("---")

# --- BASE DE DATOS TÉCNICA ---
RAZAS = {
    "Clavel / Overo Colorado": 1.08, "Aberdeen Angus": 1.10, "Hereford": 1.05, 
    "Holstein (Lechero)": 0.75, "Charolais": 1.15, "Limousin": 1.12, "Simmental": 1.08,
    "Normando": 0.98, "Parda Suiza": 1.00, "Brahman": 0.90, "Brangus": 1.02, "Wagyu": 0.95
}

# --- MOTOR DE CÁLCULO ---
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

# --- EXPORTACIÓN ---
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte_Tecnico')
    return output.getvalue()

# ---------------------------------------------------------
# APARTADO 1: SIMULADOR INDIVIDUAL
# ---------------------------------------------------------
if menu == "📊 Simulador Individual":
    st.header("Simulador de Viabilidad Ganadera")
    
    # Entradas en columnas organizadas
    with st.container():
        col_setup, col_ani = st.columns([1, 2])
        
        with col_setup:
            st.subheader("🌐 Parámetros de Campo")
            al_ha = st.number_input("Rendimiento (kg MS/ha/año)", value=5000)
            sup = st.number_input("Superficie Total (ha)", value=1.0)
            st.markdown("---")
            st.subheader("🚚 Logística")
            dist = st.number_input("Distancia (km)", value=100)
            dies = st.number_input("Precio Diesel ($/L)", value=1100)
            flete_ind = (dist / 4.0 * dies)
            st.caption(f"Costo Flete Est.: ${flete_ind:,.0f}")

        with col_ani:
            st.subheader("🐄 Especificaciones del Lote")
            c1, c2 = st.columns(2)
            with c1:
                rz = st.selectbox("Seleccione Raza", list(RAZAS.keys()))
                pst = st.selectbox("Sistema de Alimentación", ["Pradera Natural Degradada", "Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa", "Feedlot"])
                n_ani = st.number_input("Cabezas de Ganado", value=1, min_value=1)
            with c2:
                p_i = st.number_input("Peso de Entrada (kg)", value=220.0)
                p_c = st.number_input("Costo Compra ($/kg)", value=1900)
                p_v = st.number_input("Proyección Venta ($/kg)", value=2150)
                d_e = st.slider("Días de Engorda / Estadía", 30, 365, 120)

    # Cálculos
    p_f, c_max, ut_total, inv_t = calcular_todo(rz, p_i, p_c, d_e, pst, al_ha, sup, n_ani, flete_ind, 600, 18000, p_v)
    roi_val = (ut_total/inv_t)*100 if inv_t > 0 else 0

    # Panel de Resultados (Dashboard)
    st.markdown("### 📈 Panel de Resultados")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Peso Final Est.", f"{p_f:.1f} kg")
    m2.metric("Capacidad Máx.", f"{c_max} Cabezas")
    m3.metric("Utilidad Neta", f"${ut_total:,.0f} CLP")
    m4.metric("ROI s/Inversión", f"{roi_val:.1f}%")

    # Estado de Viabilidad
    if n_ani > c_max:
        st.error(f"⚠️ ADVERTENCIA DE SOBREPASTOREO: La capacidad máxima es de {c_max} cabezas.")
    elif ut_total > 0:
        st.success("✔️ PROYECTO FINANCIERAMENTE VIABLE")
    else:
        st.error("❌ EL ESCENARIO PROYECTA PÉRDIDAS")

    # Checklist Técnico
    st.markdown("---")
    st.subheader("🛠️ Gestión de Mantenimiento")
    exp1, exp2 = st.columns(2)
    with exp1:
        litros_agua = n_ani * 50
        st.info(f"**Requerimiento Hídrico:** {litros_agua} L/día")
        st.checkbox("Bebederos y Suministro Operativo")
        st.checkbox("Infraestructura de Sombra")
    with exp2:
        rezago = "25-35 días" if pst != "Feedlot" else "N/A"
        st.warning(f"**Periodo de Rezago:** {rezago}")
        st.checkbox("Protocolo de Vacunación al día")
        st.checkbox("Control Parasitario realizado")

    # Descargas y Gráficos
    st.markdown("---")
    df_ind = pd.DataFrame({"Métrica": ["Raza", "N° Cabezas", "Peso Salida", "Utilidad", "Agua Req."], 
                           "Detalle": [rz, n_ani, f"{p_f:.1f} kg", f"${ut_total:,.0f}", f"{litros_agua} L/d"]})
    st.download_button("📥 EXPORTAR REPORTE (EXCEL)", data=to_excel(df_ind), file_name=f"Informe_GanadoPro_{rz}.xlsx")
    st.line_chart({"Curva de Peso (kg)": [p_i, p_f]})

# ---------------------------------------------------------
# APARTADO 2: COMPARADOR DE ESCENARIOS
# ---------------------------------------------------------
elif menu == "⚖️ Comparador de Escenarios":
    st.header("Análisis Comparativo de Escenarios")
    
    with st.sidebar:
        st.subheader("Logística Transversal")
        dist_c = st.number_input("Distancia (km)", value=100)
        dies_c = st.number_input("Diesel ($/L)", value=1100)
        flete_c = (dist_c / 4.0 * dies_c)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Escenario A")
        rA = st.selectbox("Raza A", list(RAZAS.keys()), key="ra")
        pstA = st.selectbox("Pasto A", ["Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa"], key="pa")
        pfA, cpA, utA, invA = calcular_todo(rA, 220, 1900, 120, pstA, 5000, 1, 10, flete_c, 600, 18000, 2100)
        st.metric("Utilidad Lote A", f"${utA:,.0f}")
        
    with c2:
        st.markdown("#### Escenario B")
        rB = st.selectbox("Raza B", list(RAZAS.keys()), key="rb")
        pstB = st.selectbox("Pasto B", ["Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa"], key="pb")
        pfB, cpB, utB, invB = calcular_todo(rB, 220, 1900, 120, pstB, 5000, 1, 10, flete_c, 600, 18000, 2100)
        st.metric("Utilidad Lote B", f"${utB:,.0f}")

    st.markdown("---")
    if utA > utB:
        st.info(f"ANÁLISIS: El Escenario A presenta una mayor rentabilidad (${utA-utB:,.0f} de diferencia).")
    else:
        st.info(f"ANÁLISIS: El Escenario B presenta una mayor rentabilidad (${utB-utA:,.0f} de diferencia).")

    df_comp = pd.DataFrame({
        "Métrica": ["Raza", "Utilidad Total", "Diferencia"],
        "Escenario A": [rA, pstA, f"${utA:,.0f}", f"${utA-utB:,.0f}"],
        "Escenario B": [rB, pstB, f"${utB:,.0f}", f"${utB-utA:,.0f}"]
    })
    st.download_button("📥 DESCARGAR COMPARATIVA", data=to_excel(df_comp), file_name="Comparativa_Tecnica.xlsx")
    st.bar_chart({"Utilidad Escenario A": utA, "Utilidad Escenario B": utB})
