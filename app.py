import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="GanadoPro Chile | Gestión Corporativa", 
    page_icon="logo.png", 
    layout="wide"
)

# Inicializar Historial en la sesión si no existe (Punto 5)
if 'historial_diio' not in st.session_state:
    st.session_state.historial_diio = []

# 2. ESTILO PROFESIONAL
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetricValue"] { color: #1f2937 !important; }
    [data-testid="stMetricLabel"] { color: #4b5563 !important; }
    .stMetric { 
        background-color: #ffffff; 
        border: 1px solid #e0e0e0; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("MENÚ DE GESTIÓN", ["📊 Simulador Individual", "⚖️ Comparador de Escenarios", "🆔 Registro de Animales (DIIO)"])
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
    
    peso_promedio = (peso_ini + peso_fin) / 2
    consumo_total = (peso_promedio * 0.03) * dias
    alimento_disponible = (alimento_ha * superficie) * 0.70
    capacidad_max = int(alimento_disponible / consumo_total) if consumo_total > 0 else 0
    
    inv_total = ((peso_ini * precio_compra) + (costo_fijo_dia * dias) + costo_sanidad) * num_animales + costo_flete
    ingreso_total = (peso_fin * precio_venta) * num_animales
    utilidad = ingreso_total - inv_total
    return peso_fin, capacidad_max, utilidad, inv_total

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
                p_v_base = st.number_input("Proyección Venta ($/kg)", value=2150)
                d_e = st.slider("Días de Engorda", 30, 365, 120)

    # --- PUNTO 2: ANÁLISIS DE SENSIBILIDAD ---
    st.markdown("---")
    st.subheader("📉 Análisis de Sensibilidad (Escenarios Críticos)")
    with st.expander("Ver impacto de variaciones de mercado"):
        sens_col1, sens_col2 = st.columns(2)
        with sens_col1:
            var_precio = st.slider("Variación Precio Venta (%)", -20, 20, 0)
            var_mortalidad = st.slider("Tasa de Mortalidad proyectada (%)", 0, 10, 0)
        
        precio_sens = p_v_base * (1 + var_precio/100)
        p_f, c_max, ut_base, inv_t = calcular_todo(rz, p_i, p_c, d_e, pst, al_ha, sup, n_ani, flete_ind, 600, 18000, precio_sens)
        
        animales_finales = n_ani * (1 - var_mortalidad/100)
        ingreso_real = (p_f * precio_sens) * animales_finales
        ut_total = ingreso_real - inv_t

    # Panel de Resultados
    st.markdown("### 📈 Panel de Resultados")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Peso Final Est.", f"{p_f:.1f} kg")
    m2.metric("Capacidad Máx.", f"{c_max} Cabezas")
    m3.metric("Utilidad Final", f"${ut_total:,.0f} CLP", delta=f"{var_precio}% Precio")
    m4.metric("ROI Estimado", f"{(ut_total/inv_t)*100:.1f}%")

    if n_ani > c_max: st.error(f"⚠️ SOBREPASTOREO: Máximo {c_max} cabezas.")
    elif ut_total > 0: st.success("✔️ PROYECTO VIABLE")
    else: st.error("❌ ESCENARIO CON PÉRDIDAS")

    # Checklist Técnico
    st.markdown("---")
    st.subheader("🛠️ Gestión de Mantenimiento")
    exp1, exp2 = st.columns(2)
    with exp1:
        litros_agua = n_ani * 50
        st.info(f"**Requerimiento Hídrico:** {litros_agua} L/día")
        st.checkbox("Bebederos y Suministro Operativo")
    with exp2:
        rezago = "25-35 días" if pst != "Feedlot" else "N/A"
        st.warning(f"**Periodo de Rezago:** {rezago}")
        st.checkbox("Protocolo de Vacunación al día")

    # Descargas y Gráficos
    st.markdown("---")
    df_ind = pd.DataFrame({"Métrica": ["Raza", "N° Cabezas", "Utilidad", "Mortalidad Calc."], 
                           "Detalle": [rz, n_ani, f"${ut_total:,.0f}", f"{var_mortalidad}%"]})
    st.download_button("📥 EXPORTAR REPORTE (EXCEL)", data=to_excel(df_ind), file_name=f"Informe_{rz}.xlsx")
    st.line_chart({"Curva de Peso (kg)": [p_i, p_f]})

# ---------------------------------------------------------
# APARTADO 2: COMPARADOR
# ---------------------------------------------------------
elif menu == "⚖️ Comparador de Escenarios":
    st.header("Análisis Comparativo de Escenarios")
    with st.sidebar:
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

    df_comp = pd.DataFrame({"Métrica": ["Raza", "Pasto", "Utilidad"], "A": [rA, pstA, f"${utA:,.0f}"], "B": [rB, pstB, f"${utB:,.0f}"]})
    st.download_button("📥 DESCARGAR COMPARATIVA", data=to_excel(df_comp), file_name="Comparativa.xlsx")
    st.bar_chart({"Escenario A": utA, "Escenario B": utB})

# ---------------------------------------------------------
# APARTADO 3: REGISTRO DIIO + SANIDAD (PUNTO 5 ACTUALIZADO)
# ---------------------------------------------------------
elif menu == "🆔 Registro de Animales (DIIO)":
    st.header("Base de Datos Individual (DIIO) y Sanidad")
    st.write("Registre el peso y la última fecha de tratamiento sanitario.")

    with st.form("nuevo_registro"):
        col_reg1, col_reg2, col_reg3, col_reg4 = st.columns(4)
        diio = col_reg1.text_input("Número DIIO (Arete)")
        raza_reg = col_reg2.selectbox("Raza", list(RAZAS.keys()))
        peso_act = col_reg3.number_input("Peso Actual (kg)", min_value=0.0)
        f_vacuna = col_reg4.date_input("Fecha Última Vacuna", datetime.now())
        btn_guardar = st.form_submit_button("Guardar en Historial")

    if btn_guardar and diio:
        nuevo_item = {
            "Fecha Registro": datetime.now().strftime("%d/%m/%Y"),
            "DIIO": diio,
            "Raza": raza_reg,
            "Peso (kg)": peso_act,
            "Última Vacuna": f_vacuna.strftime("%d/%m/%Y")
        }
        st.session_state.historial_diio.append(nuevo_item)
        st.success(f"Animal {diio} registrado correctamente.")

    if st.session_state.historial_diio:
        st.markdown("---")
        df_hist = pd.DataFrame(st.session_state.historial_diio)
        st.dataframe(df_hist, use_container_width=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button("📥 Descargar Base DIIO (Excel)", data=to_excel(df_hist), file_name="Inventario_DIIO.xlsx")
        with col_btn2:
            if st.button("Limpiar Historial de Sesión"):
                st.session_state.historial_diio = []
                st.rerun()
    else:
        st.info("No hay registros guardados en esta sesión.")
