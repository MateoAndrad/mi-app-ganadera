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

# --- INICIALIZACIÓN DE ESTADOS ---
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = "inicio" 

if 'historial_diio' not in st.session_state:
    st.session_state.historial_diio = []

# 2. ESTILO PROFESIONAL Y PARCHE PARA MÓVILES (Fondo Blanco + Letras Oscuras)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    
    /* FIX PARA DESPLEGABLES EN MÓVILES */
    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: #1f2937 !important;
    }
    div[role="listbox"] ul li {
        color: #1f2937 !important;
        background-color: white !important;
    }
    
    /* VISIBILIDAD DE MÉTRICAS */
    [data-testid="stMetricValue"] { color: #1f2937 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #4b5563 !important; }
    .stMetric { 
        background-color: #ffffff; 
        border: 1px solid #e0e0e0; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* BOTONES GIGANTES */
    .stButton>button {
        height: 100px;
        font-size: 20px !important;
        border-radius: 15px;
        font-weight: bold;
    }
    
    .welcome-text {
        text-align: center;
        padding: 40px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        color: #1f2937 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS TÉCNICA COMPLETA ---
RAZAS = {
    "Aberdeen Angus": 1.10, "Hereford": 1.05, "Charolais": 1.15, "Limousin": 1.12, 
    "Shorthorn": 1.02, "Blonda de Aquitania": 1.14, "Rubia Gallega": 1.08, "Wagyu (Kobe)": 0.95,
    "Simmental": 1.08, "Normando": 0.98, "Parda Suiza": 1.00, "Fleckvieh": 1.07,
    "Brahman": 0.90, "Nelore": 0.88, "Guzerat": 0.89, "Gyr": 0.82, "Indubrasil": 0.87,
    "Brangus": 1.02, "Braford": 1.00, "Santa Gertrudis": 0.97, "Beefmaster": 1.01,
    "Girolando": 0.85, "Holstein": 0.75, "Jersey": 0.65, "Ayrshire": 0.72
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

# --- PANTALLA A: BIENVENIDA ---
if st.session_state.pantalla == "inicio":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_w1, col_w2, col_w3 = st.columns([1, 2, 1])
    with col_w2:
        st.markdown("<div class='welcome-text'><h1>🐄 GanadoPro Chile</h1><h3>Portal de Gestión Ganadera</h3><p>Seleccione una opción</p></div>", unsafe_allow_html=True)
        if st.button("🚀 ENTRAR A LA APP"):
            st.session_state.pantalla = "app"
            st.rerun()
        if st.button("📂 VER HISTORIAL"):
            st.session_state.pantalla = "historial_completo"
            st.rerun()

# --- PANTALLA B: APP ---
elif st.session_state.pantalla == "app":
    with st.sidebar:
        st.image("logo.png", use_container_width=True)
        if st.button("🏠 VOLVER AL INICIO"):
            st.session_state.pantalla = "inicio"
            st.rerun()
        st.markdown("---")
        menu = st.radio("MENÚ DE GESTIÓN", ["📊 Simulador Individual", "⚖️ Comparador de Escenarios", "🆔 Registro de Animales (DIIO)"])

    if menu == "📊 Simulador Individual":
        st.header("Simulador de Viabilidad Ganadera")
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
            rz = c1.selectbox("Seleccione Raza", list(RAZAS.keys()))
            pst = c1.selectbox("Sistema de Alimentación", ["Pradera Natural Degradada", "Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa", "Feedlot"])
            n_ani = c1.number_input("Cabezas de Ganado", value=1, min_value=1)
            p_i = c2.number_input("Peso de Entrada (kg)", value=220.0)
            p_c = c2.number_input("Costo Compra ($/kg)", value=1900)
            p_v_base = c2.number_input("Proyección Venta ($/kg)", value=2150)
            d_e = st.slider("Días de Engorda", 30, 365, 120)

        st.markdown("---")
        st.subheader("📉 Análisis de Sensibilidad")
        with st.expander("Ver impacto de variaciones"):
            s1, s2 = st.columns(2)
            var_precio = s1.slider("Variación Precio Venta (%)", -20, 20, 0)
            var_mortalidad = s2.slider("Tasa de Mortalidad (%)", 0, 10, 0)
            precio_sens = p_v_base * (1 + var_precio/100)
            p_f, c_max, ut_base, inv_t = calcular_todo(rz, p_i, p_c, d_e, pst, al_ha, sup, n_ani, flete_ind, 600, 18000, precio_sens)
            ut_total = ((p_f * precio_sens) * (n_ani * (1 - var_mortalidad/100))) - inv_t

        st.markdown("### 📈 Panel de Resultados")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Peso Final Est.", f"{p_f:.1f} kg")
        m2.metric("Capacidad Máx.", f"{c_max} Cabezas")
        m3.metric("Utilidad Final", f"${ut_total:,.0f} CLP", delta=f"{var_precio}% Precio")
        m4.metric("ROI Estimado", f"{(ut_total/inv_t)*100:.1f}%")

        if n_ani > c_max: st.error(f"⚠️ SOBREPASTOREO: Máximo {c_max} cabezas.")
        elif ut_total > 0: st.success("✔️ PROYECTO VIABLE")
        else: st.error("❌ ESCENARIO CON PÉRDIDAS")

        st.markdown("---")
        st.subheader("🛠️ Gestión de Mantenimiento")
        exp1, exp2 = st.columns(2)
        exp1.info(f"**Requerimiento Hídrico:** {n_ani * 50} L/día")
        exp1.checkbox("Bebederos Operativos")
        rezago = "25-35 días" if pst != "Feedlot" else "N/A"
        exp2.warning(f"**Periodo de Rezago:** {rezago}")
        exp2.checkbox("Protocolo de Vacunación")

        st.markdown("---")
        df_ind = pd.DataFrame({"Métrica": ["Raza", "Cabezas", "Utilidad"], "Detalle": [rz, n_ani, f"${ut_total:,.0f}"]})
        st.download_button("📥 EXPORTAR REPORTE", data=to_excel(df_ind), file_name=f"Reporte_{rz}.xlsx")
        st.line_chart({"Curva de Peso (kg)": [p_i, p_f]})

    elif menu == "⚖️ Comparador de Escenarios":
        st.header("Análisis Comparativo")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Escenario A")
            rA = st.selectbox("Raza A", list(RAZAS.keys()), key="ra")
            pstA = st.selectbox("Pasto A", ["Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa"], key="pa")
            pfA, cpA, utA, invA = calcular_todo(rA, 220, 1900, 120, pstA, 5000, 1, 10, 0, 600, 18000, 2100)
            st.metric("Utilidad A", f"${utA:,.0f}")
        with c2:
            st.markdown("#### Escenario B")
            rB = st.selectbox("Raza B", list(RAZAS.keys()), key="rb")
            pstB = st.selectbox("Pasto B", ["Pradera Natural Mejorada", "Pastura Sembrada", "Alfalfa"], key="pb")
            pfB, cpB, utB, invB = calcular_todo(rB, 220, 1900, 120, pstB, 5000, 1, 10, 0, 600, 18000, 2100)
            st.metric("Utilidad B", f"${utB:,.0f}")
        st.bar_chart({"Escenario A": utA, "Escenario B": utB})

    elif menu == "🆔 Registro de Animales (DIIO)":
        st.header("Registro DIIO y Sanidad")
        with st.form("nuevo_registro"):
            col_reg1, col_reg2, col_reg3, col_reg4 = st.columns(4)
            diio = col_reg1.text_input("Número DIIO")
            raza_reg = col_reg2.selectbox("Raza", list(RAZAS.keys()))
            peso_act = col_reg3.number_input("Peso Actual (kg)", min_value=0.0)
            f_vacuna = col_reg4.date_input("Fecha Vacuna", datetime.now())
            if st.form_submit_button("Guardar en Historial"):
                if diio:
                    st.session_state.historial_diio.append({
                        "Fecha Registro": datetime.now().strftime("%d/%m/%Y"),
                        "DIIO": diio, "Raza": raza_reg, "Peso (kg)": peso_act, "Última Vacuna": f_vacuna.strftime("%d/%m/%Y")
                    })
                    st.success(f"Animal {diio} registrado.")

# --- PANTALLA C: HISTORIAL ---
elif st.session_state.pantalla == "historial_completo":
    st.header("📂 Historial Acumulado")
    if st.button("⬅️ VOLVER AL INICIO"):
        st.session_state.pantalla = "inicio"
        st.rerun()
    if st.session_state.historial_diio:
        df_hist = pd.DataFrame(st.session_state.historial_diio)
        st.dataframe(df_hist, use_container_width=True)
        st.download_button("📥 DESCARGAR EXCEL", data=to_excel(df_hist), file_name="Historial_DIIO.xlsx")
        if st.button("🗑️ LIMPIAR HISTORIAL"):
            st.session_state.historial_diio = []
            st.rerun()
    else:
        st.info("No hay registros.")
