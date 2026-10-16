"""
Aplicación Streamlit para compresores centrífugos.
Soporta compresión isentrópica y politrópica.
Incluye curvas de compresor y eficiencia, puntos de operación.
Con análisis hidráulico para succión y descarga.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Compresores import CompressorCalculator
from utils.hidraulica_gases import calcular_analisis_hidraulico, convertir_presion
from utils.i18n import language_selector
from languages.compresor_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()
# Al inicio de cada archivo

# st.set_page_config(page_title="Compresor Centrífugo", page_icon="⚙️", layout="wide")

# Estilos
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; }
    .sub-header { font-size: 1.3rem; font-weight: bold; color: #2c3e50; margin-top: 20px; }
    .result-card { background-color: #f8f9fa; border-radius: 10px; padding: 15px; margin: 10px 0; }
    .highlight { color: #d35400; font-weight: bold; }
    .success { color: #27ae60; font-weight: bold; }
    .warning { color: #f39c12; font-weight: bold; }
    .danger { color: #e74c3c; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# st.markdown('<p class="main-header">⚙️ Compresor Centrífugo</p>', unsafe_allow_html=True)
st.markdown("---")

# Formato CSS
st.markdown(
    """
    <style>
    /* Fondo de toda la app */
    .stApp {
        background-color: #080426 !important;
        color: #547FEB !important; /* Color de texto por defecto */
    }

    /* Título Principal */
    .stApp h1 {
        color: #2E8B57 !important; /* Azul */
        font-family: 'Arial', sans-serif;
        text-align: center;
    }

    /* Subtítulos */
        .stApp h2, .stApp h3 {
            color: #2E8B57 !important; /* Azul */
            font-family: 'Arial', sans-serif;            
        }

    /* Texto de párrafos */
    .stMarkdown p {
        color: #90EE90 !important; /* Verde */
        font-size: 18px;
        text-align: justify;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(
    page_title=t("page_title"),
    page_icon="⚙️",
    layout="wide"
)

st.title(t("title"))
st.markdown("---")

# ============================================
# PROPÓSITO Y FUNDAMENTOS (sin expander)
# ============================================
st.header(t("purpose_header"))
st.markdown(t("purpose_text"))

st.header(t("fundamentals_header"))
st.markdown(t("fundamentals_text"))

st.markdown("---")

# ============================================
# CAPACIDADES DEL MÓDULO
# ============================================
st.header(t("capabilities_header"))
st.markdown(t("capabilities_text"))

st.markdown("---")

# ============================================
# VARIABLES DE ENTRADA
# ============================================
st.header(t("inputs_header"))

st.subheader(t("inputs_subheader_A"))
st.markdown(t("inputs_text_A"))

st.subheader(t("inputs_subheader_B"))
st.markdown(t("inputs_text_B"))

st.subheader(t("inputs_subheader_C"))
st.markdown(t("inputs_text_C"))

st.subheader(t("inputs_subheader_D"))
st.markdown(t("inputs_text_D"))

st.subheader(t("inputs_subheader_E"))
st.markdown(t("inputs_text_E"))

st.markdown("---")

# ============================================
# RESULTADOS OBTENIDOS
# ============================================
st.header(t("results_header"))

with st.expander(t("thermo_expander_title"), expanded=False):
    st.markdown(t("thermo_expander_text"))

with st.expander(t("hydraulic_expander_title"), expanded=False):
    st.markdown(t("hydraulic_expander_text"))

with st.expander(t("curves_expander_title"), expanded=False):
    st.markdown(t("curves_expander_text"))

with st.expander(t("power_expander_title"), expanded=False):
    st.markdown(t("power_expander_text"))

with st.expander(t("eval_expander_title"), expanded=False):
    st.markdown(t("eval_expander_text"))

st.markdown("---")

# ============================================
# ALCANCE Y APLICABILIDAD
# ============================================
st.header(t("applications_header"))
st.markdown(t("applications_text"))

st.caption(t("caption"))

# Inicialización
if 'comp_results' not in st.session_state:
    st.session_state.comp_results = None
if 'comp_curve_df' not in st.session_state:
    st.session_state.comp_curve_df = pd.DataFrame({'Caudal (m³/h)': [], 'Cabeza (J/kg)': []})
if 'eff_curve_df' not in st.session_state:
    st.session_state.eff_curve_df = pd.DataFrame({'Caudal (m³/h)': [], 'Eficiencia (%)': []})
if 'tabla_succion' not in st.session_state:
    st.session_state.tabla_succion = pd.DataFrame(columns=[
        'Número de Línea', 'Diámetro', 'Cédula', 'Longitud', 'Accesorio', 'Elevación', 'Flujo adicional'
    ])
if 'tabla_descarga' not in st.session_state:
    st.session_state.tabla_descarga = pd.DataFrame(columns=[
        'Número de Línea', 'Diámetro', 'Cédula', 'Longitud', 'Accesorio', 'Elevación', 'Flujo adicional'
    ])

# =============================================================================
# FUNCIONES DE CARGA DE DATOS
# =============================================================================
@st.cache_data
def diametro_nominal(diametro, cedula):
    """Obtiene el diámetro nominal de una tabla de referencia."""
    try:
        df1 = pd.read_excel(r'C:\Users\varia\OneDrive\Documentos\Accesorios\diametro.xlsx')
        df1.columns = df1.columns.str.strip()
        valor = df1.loc[df1['DIAMETRO'] == diametro, cedula].values[0]
        return valor
    except:
        return 0.0

@st.cache_data
def longitud_equivalente(diametro, accesorio):
    """Obtiene la longitud equivalente de un accesorio."""
    try:
        df = pd.read_csv(r'C:\Users\varia\OneDrive\Documentos\Accesorios\equiv.csv')
        df.columns = df.columns.str.strip()
        valor = df.loc[df['DIAMETRO'] == diametro, accesorio].values[0]
        return valor
    except:
        return 0.0

@st.cache_data
def columnas():
    """Obtiene las columnas disponibles para selects."""
    try:
        df = pd.read_excel(r'C:\Users\varia\OneDrive\Documentos\Accesorios\columnas.xlsx')
        df.dropna(inplace=True, how='all')
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

# =============================================================================
# PARÁMETROS DEL GAS Y CONDICIONES
# =============================================================================
st.subheader(t("comp_gas_params_header"))

# Primera fila: Parámetros del gas
col_g1, col_g2, col_g3 = st.columns(3)

with col_g1:
    R = st.number_input(t("comp_gas_constant"), value=8.314, step=0.001, format="%.3f")
    MW = st.number_input(t("comp_molecular_weight"), value=28.97, min_value=1.0, max_value=100.0, step=0.01)

with col_g2:
    Z_avg = st.number_input(t("comp_z_avg"), value=0.98, min_value=0.5, max_value=1.5, step=0.01)
    k = st.number_input(t("comp_k_ratio"), value=1.4, min_value=1.0, max_value=2.0, step=0.01)

with col_g3:
    # SELECTOR DEL MÉTODO DE CÁLCULO - AHORA EN LA INTERFAZ PRINCIPAL
    comp_type = st.selectbox(
        t("comp_calc_method"),
        options=['isentropic', 'polytropic'],
        format_func=lambda x: t("comp_method_isentropic") if x == 'isentropic' else t("comp_method_polytropic"),
        help=t("comp_calc_method_help")
    )
    
    if comp_type == 'isentropic':
        eta_label = t("comp_eta_isentropic")
    else:
        eta_label = t("comp_eta_polytropic")
    eta = st.number_input(eta_label, value=78.0, min_value=10.0, max_value=95.0, step=0.5) / 100.0

# Segunda fila: Condiciones de operación
st.markdown("---")
st.subheader(t("comp_op_conditions_header"))

col_op1, col_op2, col_op3 = st.columns(3)

with col_op1:
    T1 = st.number_input(t("comp_suction_temp"), value=25.0, step=0.5)
    P1 = st.number_input(t("comp_suction_pressure"), value=101.325, min_value=1.0, step=0.5)

with col_op2:
    P2 = st.number_input(t("comp_discharge_pressure"), value=350.0, min_value=1.0, step=0.5)
    Q_design = st.number_input(t("comp_design_flow"), value=5000.0, min_value=1.0, step=10.0)

with col_op3:
    st.markdown(t("comp_op_points_header"))
    rated_pct = st.number_input(t("comp_rated_pct"), value=100.0, min_value=10.0, max_value=150.0, step=1.0, key="rated_pct")
    normal_pct = st.number_input(t("comp_normal_pct"), value=85.0, min_value=5.0, max_value=100.0, step=1.0, key="normal_pct")
    min_pct = st.number_input(t("comp_min_pct"), value=50.0, min_value=5.0, max_value=100.0, step=1.0, key="min_pct")

# =============================================================================
# SISTEMA DE UNIDADES PARA ANÁLISIS HIDRÁULICO
# =============================================================================
st.markdown("---")
st.subheader(t("comp_unit_system_header"))

sistema_hid = st.radio(
    t("comp_unit_system"),
    [t("comp_unit_imperial"), t("comp_unit_si")],
    horizontal=True,
    index=0,
    key="sistema_hid_comp"
)

# =============================================================================
# ANÁLISIS HIDRÁULICO - SUCCIÓN
# =============================================================================
st.markdown("---")
st.subheader(t("comp_suction_analysis_header"))

# Opciones para selects
try:
    col_data = columnas()
    opcion1 = col_data['DIAMETRO'].to_list() if 'DIAMETRO' in col_data.columns else []
    opcion2 = col_data['ACCESORIO'].to_list() if 'ACCESORIO' in col_data.columns else []
    opcion3 = col_data['CEDULA'].to_list() if 'CEDULA' in col_data.columns else []
except:
    opcion1, opcion2, opcion3 = [], [], []

col_s1, col_s2 = st.columns(2)

with col_s1:
    suction_vessel = st.number_input(
        t("comp_suction_vessel"),
        value=st.session_state.get('suction_vessel', 14.7),
        min_value=0.0,
        max_value=1000.0,
        step=0.1,
        key="suction_vessel_comp"
    )
    
    suction_elevation = st.number_input(
        t("comp_suction_elevation"),
        value=st.session_state.get('suction_elevation', 10.0),
        min_value=-100.0,
        max_value=500.0,
        step=0.1,
        key="suction_elevation_comp"
    )

with col_s2:
    densidad_gas = st.number_input(
        t("comp_gas_density_lbft3") if sistema_hid == t("comp_unit_imperial") else t("comp_gas_density_kgm3"),
        value=0.075 if sistema_hid == t("comp_unit_imperial") else 1.2,
        min_value=0.001,
        max_value=100.0,
        step=0.001,
        key="densidad_gas_comp",
        help=t("comp_gas_density_help")
    )
    
    viscosidad_gas = st.number_input(
        t("comp_gas_viscosity_stokes") if sistema_hid == t("comp_unit_imperial") else t("comp_gas_viscosity_cst"),
        value=1.5e-4 if sistema_hid == t("comp_unit_imperial") else 0.15,
        min_value=1e-6,
        max_value=10.0,
        step=1e-6,
        format="%.6f",
        key="viscosidad_gas_comp"
    )

# Tabla de líneas de succión
st.caption(t("comp_suction_lines_caption"))

col_s3, col_s4 = st.columns(2)

with col_s3:
    numlinea_s = st.number_input(t("comp_line_number_suction"), step=1, key="numlinea_s_comp")
    if sistema_hid == t("comp_unit_imperial"):
        longitud_s = st.number_input(t("comp_length_ft"), value=0.0, step=0.1, key="long_s_comp")
        diametro_s = st.selectbox(t("comp_diameter_in"), opcion1, placeholder=t("comp_diameter_placeholder"), key="diam_s_comp")
    else:
        longitud_s = st.number_input(t("comp_length_m"), value=0.0, step=0.1, key="long_s_comp")
        diametro_s = st.selectbox(t("comp_diameter_mm"), opcion1, placeholder=t("comp_diameter_placeholder"), key="diam_s_comp")

with col_s4:
    accesorio_s = st.selectbox(t("comp_accessories"), opcion2, placeholder=t("comp_accessories_placeholder"), key="acc_s_comp")
    cedula_s = st.selectbox(t("comp_schedule"), opcion3, placeholder=t("comp_schedule_placeholder"), key="ced_s_comp")
    if sistema_hid == t("comp_unit_imperial"):
        elevacion_s = st.number_input(t("comp_elevation_ft"), value=0.0, step=0.1, key="elev_s_comp")
    else:
        elevacion_s = st.number_input(t("comp_elevation_m"), value=0.0, step=0.1, key="elev_s_comp")
    flujo_adicional_s = st.number_input(t("comp_additional_flow"), value=0.0, step=0.1, key="flujo_adicional_s_comp")

# Botón agregar fila succión
if st.button(t("comp_add_suction_button"), key="add_succion_comp"):
    if not numlinea_s:
        st.warning(t("comp_warn_line_number"))
    elif longitud_s == 0.0:
        st.warning(t("comp_warn_length"))
    elif not diametro_s or diametro_s == t("comp_diameter_placeholder"):
        st.warning(t("comp_warn_diameter"))
    elif not accesorio_s or accesorio_s == t("comp_accessories"):
        st.warning(t("comp_warn_accessory"))
    elif not cedula_s or cedula_s == t("comp_schedule"):
        st.warning(t("comp_warn_schedule"))
    else:
        nueva_fila = pd.DataFrame({
            'Número de Línea': [numlinea_s],
            'Diámetro': [diametro_s],
            'Cédula': [cedula_s],
            'Longitud': [longitud_s],
            'Accesorio': [accesorio_s],
            'Elevación': [elevacion_s],
            'Flujo adicional': [flujo_adicional_s]
        })
        st.session_state.tabla_succion = pd.concat(
            [st.session_state.tabla_succion, nueva_fila], ignore_index=True
        )
        st.success(t("comp_success_section_added"))

# Mostrar tabla de succión
if not st.session_state.tabla_succion.empty:
    edited_df_s = st.data_editor(
        st.session_state.tabla_succion,
        use_container_width=True,
        num_rows="dynamic",
        key='editor_succion_comp'
    )
    st.session_state.tabla_succion = edited_df_s

# =============================================================================
# ANÁLISIS HIDRÁULICO - DESCARGA
# =============================================================================
st.markdown("---")
st.subheader(t("comp_discharge_analysis_header"))

col_d1, col_d2 = st.columns(2)

with col_d1:
    discharge_vessel = st.number_input(
        t("comp_discharge_vessel"),
        value=st.session_state.get('discharge_vessel', 14.7),
        min_value=0.0,
        max_value=1000.0,
        step=0.1,
        key="discharge_vessel_comp"
    )
    
    discharge_elevation = st.number_input(
        t("comp_discharge_elevation"),
        value=st.session_state.get('discharge_elevation', 10.0),
        min_value=-100.0,
        max_value=500.0,
        step=0.1,
        key="discharge_elevation_comp"
    )

with col_d2:
    st.markdown(t("comp_density_viscosity_discharge"))
    densidad_gas_desc = st.number_input(
        t("comp_gas_density_lbft3") if sistema_hid == t("comp_unit_imperial") else t("comp_gas_density_kgm3"),
        value=0.075 if sistema_hid == t("comp_unit_imperial") else 1.2,
        min_value=0.001,
        max_value=100.0,
        step=0.001,
        key="densidad_gas_desc_comp"
    )
    
    viscosidad_gas_desc = st.number_input(
        t("comp_gas_viscosity_stokes") if sistema_hid == t("comp_unit_imperial") else t("comp_gas_viscosity_cst"),
        value=1.5e-4 if sistema_hid == t("comp_unit_imperial") else 0.15,
        min_value=1e-6,
        max_value=10.0,
        step=1e-6,
        format="%.6f",
        key="viscosidad_gas_desc_comp"
    )

# Tabla de líneas de descarga
st.caption(t("comp_discharge_lines_caption"))

col_d3, col_d4 = st.columns(2)

with col_d3:
    numlinea_d = st.number_input(t("comp_line_number_discharge"), step=1, key="numlinea_d_comp")
    if sistema_hid == t("comp_unit_imperial"):
        longitud_d = st.number_input(t("comp_length_ft"), value=0.0, step=0.1, key="long_d_comp")
        diametro_d = st.selectbox(t("comp_diameter_in"), opcion1, placeholder=t("comp_diameter_placeholder"), key="diam_d_comp")
    else:
        longitud_d = st.number_input(t("comp_length_m"), value=0.0, step=0.1, key="long_d_comp")
        diametro_d = st.selectbox(t("comp_diameter_mm"), opcion1, placeholder=t("comp_diameter_placeholder"), key="diam_d_comp")

with col_d4:
    accesorio_d = st.selectbox(t("comp_accessories"), opcion2, placeholder=t("comp_accessories_placeholder"), key="acc_d_comp")
    cedula_d = st.selectbox(t("comp_schedule"), opcion3, placeholder=t("comp_schedule_placeholder"), key="ced_d_comp")
    if sistema_hid == t("comp_unit_imperial"):
        elevacion_d = st.number_input(t("comp_elevation_ft"), value=0.0, step=0.1, key="elev_d_comp")
    else:
        elevacion_d = st.number_input(t("comp_elevation_m"), value=0.0, step=0.1, key="elev_d_comp")
    flujo_adicional_d = st.number_input(t("comp_additional_flow"), value=0.0, step=0.1, key="flujo_adicional_d_comp")

# Botón agregar fila descarga
if st.button(t("comp_add_discharge_button"), key="add_discharge_comp"):
    if not numlinea_d:
        st.warning(t("comp_warn_line_number"))
    elif longitud_d == 0.0:
        st.warning(t("comp_warn_length"))
    elif not diametro_d or diametro_d == t("comp_diameter_placeholder"):
        st.warning(t("comp_warn_diameter"))
    elif not accesorio_d or accesorio_d == t("comp_accessories"):
        st.warning(t("comp_warn_accessory"))
    elif not cedula_d or cedula_d == t("comp_schedule"):
        st.warning(t("comp_warn_schedule"))
    else:
        nueva_fila = pd.DataFrame({
            'Número de Línea': [numlinea_d],
            'Diámetro': [diametro_d],
            'Cédula': [cedula_d],
            'Longitud': [longitud_d],
            'Accesorio': [accesorio_d],
            'Elevación': [elevacion_d],
            'Flujo adicional': [flujo_adicional_d]
        })
        st.session_state.tabla_descarga = pd.concat(
            [st.session_state.tabla_descarga, nueva_fila], ignore_index=True
        )
        st.success(t("comp_success_section_added"))

# Mostrar tabla de descarga
if not st.session_state.tabla_descarga.empty:
    edited_df_d = st.data_editor(
        st.session_state.tabla_descarga,
        use_container_width=True,
        num_rows="dynamic",
        key='editor_descarga_comp'
    )
    st.session_state.tabla_descarga = edited_df_d

# =============================================================================
# BOTÓN DE CÁLCULO
# =============================================================================
st.markdown("---")
col_calc1, col_calc2, col_calc3 = st.columns([1, 2, 1])
with col_calc2:
    calcular = st.button(t("comp_calculate_button"), use_container_width=True, type="primary")

# =============================================================================
# PROCESAR CÁLCULO
# =============================================================================
if calcular:
    T1_K = T1 + 273.15
    
    # Crear calculadora
    calc = CompressorCalculator(R=R, MW=MW, Z_avg=Z_avg, k=k, eta=eta,
                                T1=T1_K, P1=P1, P2=P2, Q_vol=Q_design,
                                comp_type=comp_type)
    
    # Cálculos del compresor
    H_calc = calc.head()
    m_dot = calc.mass_flow(Q_design, P1, T1_K)
    P_pow = calc.power()
    rp = P2 / P1
    T2 = calc.discharge_temperature()
    T2_ideal = calc.discharge_temperature_ideal() if comp_type == 'isentropic' else None
    n = getattr(calc, 'n', None)
    
    # --- Análisis hidráulico de succión ---
    if not st.session_state.tabla_succion.empty:
        # Convertir caudal a las unidades del sistema hidráulico
        if sistema_hid == t("comp_unit_imperial"):
            # 1 m³/h = 0.5886 ft³/min
            Q_hid = Q_design * 0.5886  # ft³/min
        else:
            Q_hid = Q_design  # m³/h
        
        df_succion, P_succion_salida, long_acum_s, presion_nodos_s, elevacion_nodos_s, P_succion_entrada = calcular_analisis_hidraulico(
            st.session_state.tabla_succion,
            sistema_hid,
            Q_hid,
            densidad_gas if sistema_hid == t("comp_unit_imperial") else densidad_gas,
            viscosidad_gas if sistema_hid == t("comp_unit_imperial") else viscosidad_gas,
            suction_vessel,
            diametro_nominal,
            longitud_equivalente,
            "psi" if sistema_hid == t("comp_unit_imperial") else "kPa",
            es_gas=True
        )
    else:
        df_succion = None
        P_succion_salida = suction_vessel
        long_acum_s = []
        presion_nodos_s = []
        elevacion_nodos_s = []
        P_succion_entrada = suction_vessel
    
    # --- Análisis hidráulico de descarga ---
    if not st.session_state.tabla_descarga.empty:
        if sistema_hid == t("comp_unit_imperial"):
            Q_hid_d = Q_design * 0.5886  # ft³/min
        else:
            Q_hid_d = Q_design  # m³/h
        
        df_descarga, P_descarga_salida, long_acum_d, presion_nodos_d, elevacion_nodos_d, P_descarga_entrada = calcular_analisis_hidraulico(
            st.session_state.tabla_descarga,
            sistema_hid,
            Q_hid_d,
            densidad_gas_desc if sistema_hid == t("comp_unit_imperial") else densidad_gas_desc,
            viscosidad_gas_desc if sistema_hid == t("comp_unit_imperial") else viscosidad_gas_desc,
            discharge_vessel,
            diametro_nominal,
            longitud_equivalente,
            "psi" if sistema_hid == t("comp_unit_imperial") else "kPa",
            es_gas=True
        )
    else:
        df_descarga = None
        P_descarga_salida = discharge_vessel
        long_acum_d = []
        presion_nodos_d = []
        elevacion_nodos_d = []
        P_descarga_entrada = discharge_vessel
    
    # Guardar resultados
    st.session_state.comp_results = {
        'calc': calc,
        'comp_type': comp_type,
        'R': R,
        'MW': MW,
        'Z_avg': Z_avg,
        'k': k,
        'eta': eta,
        'T1_C': T1,
        'T1_K': T1_K,
        'P1': P1,
        'P2': P2,
        'rp': rp,
        'Q_design': Q_design,
        'H_calc_Jkg': H_calc,
        'H_calc_m': H_calc / 9.81,
        'mass_flow_kgs': m_dot,
        'power_kW': P_pow,
        'T2_K': T2,
        'T2_C': T2 - 273.15,
        'T2_ideal_K': T2_ideal,
        'T2_ideal_C': T2_ideal - 273.15 if T2_ideal else None,
        'n': n,
        # Puntos de operación
        'rated_pct': rated_pct,
        'normal_pct': normal_pct,
        'min_pct': min_pct,
        # Análisis hidráulico
        'df_succion': df_succion,
        'df_descarga': df_descarga,
        'P_succion_entrada': P_succion_entrada,
        'P_succion_salida': P_succion_salida,
        'P_descarga_entrada': P_descarga_entrada,
        'P_descarga_salida': P_descarga_salida,
        'long_acum_s': long_acum_s,
        'presion_nodos_s': presion_nodos_s,
        'elevacion_nodos_s': elevacion_nodos_s,
        'long_acum_d': long_acum_d,
        'presion_nodos_d': presion_nodos_d,
        'elevacion_nodos_d': elevacion_nodos_d,
        'sistema_hid': sistema_hid,
    }
    st.rerun()

# =============================================================================
# MOSTRAR RESULTADOS
# =============================================================================
if st.session_state.comp_results is not None:
    res = st.session_state.comp_results
    calc = res['calc']

    st.markdown("---")
    results_title = t("comp_results_isentropic") if res["comp_type"] == "isentropic" else t("comp_results_polytropic")
    st.markdown(f'<p class="sub-header">{results_title}</p>', unsafe_allow_html=True)

    # Tarjetas resumen
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    with col_r1:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("comp_card_pressure_ratio")}</strong><br>
            <span class="highlight">{res['rp']:.3f}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_r2:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("comp_card_head")}</strong><br>
            <span class="highlight">{res['H_calc_Jkg']:.0f} J/kg</span><br>
            <small>{t("comp_card_head_air_col").format(f"{res['H_calc_m']:.1f}")}</small>
        </div>
        """, unsafe_allow_html=True)
    with col_r3:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("comp_card_mass_flow")}</strong><br>
            <span class="highlight">{res['mass_flow_kgs']:.3f} kg/s</span>
        </div>
        """, unsafe_allow_html=True)
    with col_r4:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("comp_card_power")}</strong><br>
            <span class="highlight">{res['power_kW']:.1f} kW</span>
        </div>
        """, unsafe_allow_html=True)

    # Detalles adicionales
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        if res['comp_type'] == 'polytropic' and res['n'] is not None:
            st.markdown(t("comp_polytropic_exponent").format(res['n']))
        else:
            st.markdown(t("comp_k_label").format(res['k']))
    with col_d2:
        st.markdown(t("comp_efficiency_label").format(res['eta']*100))
    with col_d3:
        st.markdown(t("comp_z_avg_label").format(res['Z_avg']))

    # Temperaturas
    st.markdown("---")
    st.markdown(t("comp_temperatures_header"))
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.metric(t("comp_temp_suction"), f"{res['T1_C']:.1f} °C")
    with col_t2:
        if res['comp_type'] == 'isentropic' and res['T2_ideal_C'] is not None:
            st.metric(t("comp_temp_discharge_ideal"), f"{res['T2_ideal_C']:.1f} °C")
        else:
            st.metric(t("comp_temp_discharge_polytropic"), f"{res['T2_C']:.1f} °C")
    with col_t3:
        st.metric(t("comp_temp_discharge_real"), f"{res['T2_C']:.1f} °C")

    # ===== RESULTADOS DEL ANÁLISIS HIDRÁULICO =====
    st.markdown("---")
    st.markdown(f'<p class="sub-header">{t("comp_hydraulic_analysis_header")}</p>', unsafe_allow_html=True)

    col_h1, col_h2 = st.columns(2)

    with col_h1:
        st.markdown(t("comp_suction_label"))
        if res['df_succion'] is not None and not res['df_succion'].empty:
            st.dataframe(res['df_succion'], use_container_width=True)
            unit_label = 'psi' if res['sistema_hid'] == t('comp_unit_imperial') else 'kPa'
            st.write(t("comp_inlet_pressure").format(res['P_succion_entrada'], unit_label))
            st.write(t("comp_outlet_pressure").format(res['P_succion_salida'], unit_label))
            st.write(t("comp_pressure_drop").format(res['P_succion_entrada'] - res['P_succion_salida'], unit_label))
        else:
            st.info(t("comp_no_suction_sections"))

    with col_h2:
        st.markdown(t("comp_discharge_label"))
        if res['df_descarga'] is not None and not res['df_descarga'].empty:
            st.dataframe(res['df_descarga'], use_container_width=True)
            unit_label = 'psi' if res['sistema_hid'] == t('comp_unit_imperial') else 'kPa'
            st.write(t("comp_inlet_pressure").format(res['P_descarga_entrada'], unit_label))
            st.write(t("comp_outlet_pressure").format(res['P_descarga_salida'], unit_label))
            st.write(t("comp_pressure_drop").format(res['P_descarga_entrada'] - res['P_descarga_salida'], unit_label))
        else:
            st.info(t("comp_no_discharge_sections"))

    # ===== CURVAS DEL COMPRESOR =====
    st.markdown("---")
    st.markdown(f'<p class="sub-header">{t("comp_compressor_curves_header")}</p>', unsafe_allow_html=True)

    col_curve1, col_curve2 = st.columns([2, 1])
    with col_curve1:
        st.markdown(t("comp_head_vs_flow_header"))
        curve_data = st.data_editor(
            st.session_state.comp_curve_df,
            num_rows="dynamic",
            column_config={
                t("comp_curve_col_flow"): st.column_config.NumberColumn(t("comp_curve_col_flow"), min_value=0, step=1),
                t("comp_curve_col_head"): st.column_config.NumberColumn(t("comp_curve_col_head"), min_value=0, step=1),
            },
            use_container_width=True,
            key="comp_curve_editor"
        )
        st.session_state.comp_curve_df = curve_data

        st.markdown(t("comp_eff_curve_header"))
        eff_data = st.data_editor(
            st.session_state.eff_curve_df,
            num_rows="dynamic",
            column_config={
                t("comp_eff_curve_col_flow"): st.column_config.NumberColumn(t("comp_eff_curve_col_flow"), min_value=0, step=1),
                t("comp_eff_curve_col_eff"): st.column_config.NumberColumn(t("comp_eff_curve_col_eff"), min_value=0, max_value=100, step=0.1),
            },
            use_container_width=True,
            key="eff_curve_editor"
        )
        st.session_state.eff_curve_df = eff_data

    with col_curve2:
        st.caption(t("comp_curve_example_caption"))
        st.code("""
Caudal (m³/h) | Cabeza (J/kg)
0            | 120000
2000         | 115000
4000         | 108000
6000         | 98000
8000         | 85000
10000        | 70000
        """)
        st.caption(t("comp_eff_example_caption"))
        st.code("""
Caudal (m³/h) | Eficiencia (%)
2000         | 70
4000         | 78
6000         | 80
8000         | 76
10000        | 70
        """)
        if st.button(t("comp_load_examples_button"), use_container_width=True):
            st.session_state.comp_curve_df = pd.DataFrame({
                t("comp_curve_col_flow"): [0, 2000, 4000, 6000, 8000, 10000],
                t("comp_curve_col_head"): [120000, 115000, 108000, 98000, 85000, 70000]
            })
            st.session_state.eff_curve_df = pd.DataFrame({
                t("comp_eff_curve_col_flow"): [2000, 4000, 6000, 8000, 10000],
                t("comp_eff_curve_col_eff"): [70, 78, 80, 76, 70]
            })
            st.rerun()

    # ===== PROCESAR CURVAS =====
    if len(curve_data) >= 2:
        try:
            Q_data = curve_data[t("comp_curve_col_flow")].tolist()
            H_data = curve_data[t("comp_curve_col_head")].tolist()
            if all(isinstance(x, (int, float)) for x in Q_data) and all(isinstance(y, (int, float)) for y in H_data):
                pairs = sorted(zip(Q_data, H_data))
                Q_sorted, H_sorted = zip(*pairs)

                Q_design = res['Q_design']
                Q_rated = Q_design * (res['rated_pct'] / 100.0)
                Q_normal = Q_design * (res['normal_pct'] / 100.0)  # NUEVO PUNTO NORMAL
                Q_min = Q_design * (res['min_pct'] / 100.0)

                # Interpolar cabeza
                H_design = calc.interpolate_curve(Q_data, H_data, Q_design)
                H_rated = calc.interpolate_curve(Q_data, H_data, Q_rated)
                H_normal = calc.interpolate_curve(Q_data, H_data, Q_normal)  # NUEVO
                H_min = calc.interpolate_curve(Q_data, H_data, Q_min)

                # Interpolar eficiencia
                eff_design = eff_rated = eff_normal = eff_min = None
                if len(eff_data) >= 2:
                    Q_eff = eff_data[t("comp_eff_curve_col_flow")].tolist()
                    Eff_eff = eff_data[t("comp_eff_curve_col_eff")].tolist()
                    if all(isinstance(x, (int, float)) for x in Q_eff) and all(isinstance(y, (int, float)) for y in Eff_eff):
                        eff_design = calc.interpolate_curve(Q_eff, Eff_eff, Q_design) / 100.0
                        eff_rated = calc.interpolate_curve(Q_eff, Eff_eff, Q_rated) / 100.0
                        eff_normal = calc.interpolate_curve(Q_eff, Eff_eff, Q_normal) / 100.0  # NUEVO
                        eff_min = calc.interpolate_curve(Q_eff, Eff_eff, Q_min) / 100.0

                # Calcular potencia usando cabeza de curva
                def power_from_curve(Q, H, eff=None):
                    if H is None:
                        return None
                    if eff is None:
                        eff = res['eta']
                    m_dot = calc.mass_flow(Q, res['P1'], res['T1_K'])
                    return (m_dot * H) / (eff * 1000) if eff > 0 else None

                P_design = power_from_curve(Q_design, H_design, eff_design)
                P_rated = power_from_curve(Q_rated, H_rated, eff_rated)
                P_normal = power_from_curve(Q_normal, H_normal, eff_normal)  # NUEVO
                P_min = power_from_curve(Q_min, H_min, eff_min)

                # Guardar
                res['H_design'] = H_design
                res['H_rated'] = H_rated
                res['H_normal'] = H_normal  # NUEVO
                res['H_min'] = H_min
                res['P_design'] = P_design
                res['P_rated'] = P_rated
                res['P_normal'] = P_normal  # NUEVO
                res['P_min'] = P_min
                res['eff_design'] = eff_design
                res['eff_rated'] = eff_rated
                res['eff_normal'] = eff_normal  # NUEVO
                res['eff_min'] = eff_min

                # ===== TABLA DE POTENCIA =====
                st.markdown("---")
                st.markdown(t("comp_power_points_header"))

                power_data = []
                for label, q, h, p, e in [
                    (t("comp_point_design"), Q_design, H_design, P_design, eff_design),
                    (t("comp_point_rated"), Q_rated, H_rated, P_rated, eff_rated),
                    (t("comp_point_normal"), Q_normal, H_normal, P_normal, eff_normal),
                    (t("comp_point_min"), Q_min, H_min, P_min, eff_min)
                ]:
                    if h is not None and p is not None:
                        power_data.append({
                            t("comp_col_point"): label,
                            t("comp_col_flow"): f"{q:.1f}",
                            t("comp_col_head"): f"{h:.0f}",
                            t("comp_col_efficiency"): f"{e*100:.1f}" if e else t("comp_eff_global_format").format(res['eta']*100),
                            t("comp_col_power"): f"{p:.1f}"
                        })
                if power_data:
                    st.table(pd.DataFrame(power_data))
                else:
                    st.warning(t("comp_warn_no_power"))

                # ===== GRÁFICA =====
                # Curva del sistema (simple, asumiendo H_static=0 para este ejemplo)
                if H_design is not None and Q_design > 0:
                    K = H_design / (Q_design ** 2)
                    Q_range = np.linspace(0, max(Q_sorted)*1.1, 100)
                    H_sys = K * Q_range ** 2
                else:
                    Q_range = np.linspace(0, max(Q_sorted)*1.1, 100)
                    H_sys = np.zeros_like(Q_range)

                op_Q, op_H = calc.find_operating_point(Q_data, H_data, Q_range, H_sys)

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(Q_sorted, H_sorted, 'b-', linewidth=2.5, label=t("comp_curve_compressor_trace"))
                ax.plot(Q_sorted, H_sorted, 'bo', markersize=6)

                if H_design:
                    ax.plot(Q_design, H_design, 'go', markersize=10, label=t("comp_curve_design_trace").format(Q_design, H_design))
                if H_rated:
                    ax.plot(Q_rated, H_rated, 'mo', markersize=10, label=t("comp_curve_rated_trace").format(Q_rated, H_rated))
                if H_normal:
                    ax.plot(Q_normal, H_normal, 'co', markersize=10, label=t("comp_curve_normal_trace").format(Q_normal, H_normal))
                if H_min:
                    ax.plot(Q_min, H_min, 'yo', markersize=10, label=t("comp_curve_min_trace").format(Q_min, H_min))

                if op_Q is not None and op_H is not None:
                    ax.plot(op_Q, op_H, 'ro', markersize=12, label=t("comp_curve_operation_trace").format(op_Q, op_H))

                # Eficiencia en eje secundario
                if len(eff_data) >= 2:
                    Q_eff = eff_data[t("comp_eff_curve_col_flow")].tolist()
                    Eff_eff = eff_data[t("comp_eff_curve_col_eff")].tolist()
                    if all(isinstance(x, (int, float)) for x in Q_eff) and all(isinstance(y, (int, float)) for y in Eff_eff):
                        ax2 = ax.twinx()
                        ax2.plot(Q_eff, Eff_eff, 'r--', linewidth=2, label=t("comp_curve_eff_trace"))
                        ax2.set_ylabel(t("comp_curve_axis_eff"), color='r')
                        ax2.tick_params(axis='y', labelcolor='r')
                        lines, labels = ax.get_legend_handles_labels()
                        lines2, labels2 = ax2.get_legend_handles_labels()
                        ax.legend(lines + lines2, labels + labels2, loc='best')

                ax.set_xlabel(t("comp_curve_axis_flow"), fontsize=12)
                ax.set_ylabel(t("comp_curve_axis_head"), fontsize=12)
                comp_type_label = t("comp_method_isentropic") if res["comp_type"] == "isentropic" else t("comp_method_polytropic")
                ax.set_title(t("comp_curve_title").format(comp_type_label), fontsize=14)
                ax.grid(True, alpha=0.3)
                if len(eff_data) < 2:
                    ax.legend(loc='best')
                st.pyplot(fig)

                # ===== INTERPRETACIÓN =====
                st.markdown("---")
                st.markdown(t("comp_evaluation_header"))
                col_eval1, col_eval2 = st.columns(2)
                with col_eval1:
                    if H_design:
                        st.success(t("comp_eval_design").format(H_design, Q_design))
                    else:
                        st.warning(t("comp_warn_no_interpolation_design"))
                    
                    if H_normal:
                        st.info(t("comp_eval_normal").format(H_normal, Q_normal))
                    else:
                        st.warning(t("comp_warn_no_interpolation_normal"))
                with col_eval2:
                    if op_Q is not None and op_H is not None:
                        st.info(t("comp_eval_operation").format(op_Q, op_H))
                    else:
                        st.warning(t("comp_warn_no_intersection"))

            else:
                st.warning(t("comp_warn_valid_numeric_head"))

        except Exception as e:
            st.error(t("comp_error_processing_curve").format(str(e)))
    else:
        st.info(t("comp_info_min_two_points"))

    # ===== TABLA DETALLADA =====
    st.markdown("---")
    with st.expander(t("comp_all_params_expander")):
        param_dict = {
            t("comp_param_comp_type"): t("comp_method_isentropic") if res['comp_type']=='isentropic' else t("comp_method_polytropic"),
            t("comp_param_R"): res['R'],
            t("comp_param_MW"): res['MW'],
            t("comp_param_Zavg"): res['Z_avg'],
            t("comp_param_k"): res['k'],
            t("comp_param_efficiency"): f"{res['eta']*100:.1f}",
            t("comp_param_n") if res['comp_type']=='polytropic' else t("comp_param_k"): res['n'] if res['comp_type']=='polytropic' else res['k'],
            t("comp_param_T1"): res['T1_C'],
            t("comp_param_P1"): res['P1'],
            t("comp_param_P2"): res['P2'],
            t("comp_param_rp"): res['rp'],
            t("comp_param_Q_design"): res['Q_design'],
            t("comp_param_head_calc"): res['H_calc_Jkg'],
            t("comp_param_head_air_col"): res['H_calc_m'],
            t("comp_param_mass_flow"): res['mass_flow_kgs'],
            t("comp_param_power"): res['power_kW'],
            t("comp_param_T2_real"): res['T2_C'],
        }
        if res['comp_type'] == 'isentropic' and res['T2_ideal_C'] is not None:
            param_dict[t("comp_param_T2_ideal")] = res['T2_ideal_C']
        if 'H_design' in res and res['H_design'] is not None:
            param_dict[t("comp_param_head_design")] = res['H_design']
        if 'H_rated' in res and res['H_rated'] is not None:
            param_dict[t("comp_param_head_rated")] = res['H_rated']
        if 'H_normal' in res and res['H_normal'] is not None:
            param_dict[t("comp_param_head_normal")] = res['H_normal']
        if 'H_min' in res and res['H_min'] is not None:
            param_dict[t("comp_param_head_min")] = res['H_min']
        if 'P_design' in res and res['P_design'] is not None:
            param_dict[t("comp_param_power_design")] = res['P_design']
        if 'P_rated' in res and res['P_rated'] is not None:
            param_dict[t("comp_param_power_rated")] = res['P_rated']
        if 'P_normal' in res and res['P_normal'] is not None:
            param_dict[t("comp_param_power_normal")] = res['P_normal']
        if 'P_min' in res and res['P_min'] is not None:
            param_dict[t("comp_param_power_min")] = res['P_min']
        if 'eff_design' in res and res['eff_design'] is not None:
            param_dict[t("comp_param_eff_design")] = f"{res['eff_design']*100:.1f}"
        if 'eff_rated' in res and res['eff_rated'] is not None:
            param_dict[t("comp_param_eff_rated")] = f"{res['eff_rated']*100:.1f}"
        if 'eff_normal' in res and res['eff_normal'] is not None:
            param_dict[t("comp_param_eff_normal")] = f"{res['eff_normal']*100:.1f}"
        if 'eff_min' in res and res['eff_min'] is not None:
            param_dict[t("comp_param_eff_min")] = f"{res['eff_min']*100:.1f}"

        df_params = pd.DataFrame(list(param_dict.items()), columns=[t("comp_param_col_name"), t("comp_param_col_value")])
        st.dataframe(df_params, use_container_width=True, hide_index=True)

else:
    st.info(t("comp_initial_message"))

st.markdown("---")
st.caption(t("comp_footer"))