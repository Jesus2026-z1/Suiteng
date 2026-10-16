"""
Aplicación Streamlit para el cálculo de bombas centrífugas con análisis hidráulico.
Permite ingresar datos manualmente o cargar el ejemplo de las imágenes.
Incluye visualización de la curva de la bomba y punto de operación.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from utils.bombas import PumpCalculator
from utils.i18n import language_selector
from languages.bombas_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()

# =============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Calculadora de Bombas con Análisis Hidráulico",
    page_icon="⚙️",
    layout="wide"
)

# st.markdown('<p class="main-header">⚙️ Calculadora de Bombas Centrífugas</p>', unsafe_allow_html=True)
st.markdown("---")

# =============================================================================
# 2. ESTILO
# =============================================================================
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

st.markdown("---")

# ============================================
# RESULTADOS OBTENIDOS
# ============================================
st.header(t("results_header"))

with st.expander(t("summary_expander_title"), expanded=False):
    st.markdown(t("summary_expander_text"))

with st.expander(t("curve_expander_title"), expanded=False):
    st.markdown(t("curve_expander_text"))

with st.expander(t("losses_expander_title"), expanded=False):
    st.markdown(t("losses_expander_text"))

with st.expander(t("operating_expander_title"), expanded=False):
    st.markdown(t("operating_expander_text"))

st.markdown("---")

# ============================================
# ALCANCE Y APLICABILIDAD
# ============================================
st.header(t("applications_header"))
st.markdown(t("applications_text"))

st.caption(t("caption"))

# =============================================================================
# 3. INICIALIZACIÓN DEL ESTADO
# =============================================================================
if 'calculator' not in st.session_state:
    st.session_state.calculator = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'pump_curve_df' not in st.session_state:
    st.session_state.pump_curve_df = pd.DataFrame({'Caudal (gpm)': [], 'Cabeza (ft)': []})
if 'tabla_succion' not in st.session_state:
    st.session_state.tabla_succion = pd.DataFrame(columns=[
        'Número de Línea', 'Diámetro', 'Cédula', 'Longitud', 'Accesorio', 'Elevación'
    ])
if 'tabla_descarga' not in st.session_state:
    st.session_state.tabla_descarga = pd.DataFrame(columns=[
        'Número de Línea', 'Diámetro', 'Cédula', 'Longitud', 'Accesorio', 'Elevación'
    ])
if 'control_valve_dp' not in st.session_state:
    st.session_state.control_valve_dp = 0.0

# =============================================================================
# 4. FUNCIONES DE CARGA DE DATOS
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
# 5. FUNCIONES DE CÁLCULO HIDRÁULICO
# =============================================================================
def haaland_friction_factor(Re, e_D):
    """Calcula el factor de fricción usando la ecuación de Haaland."""
    if Re == 0:
        return 0.02
    term1 = (e_D / 3.7) ** 1.11
    term2 = 6.9 / Re
    f = (1 / (-1.8 * math.log10(term1 + term2))) ** 2
    return f

def calcular_friccion_tuberia(df, sistema, flujo, densidad, viscosidad, diametro_nominal_func, longitud_equivalente_func):
    """
    Calcula la caída de presión por fricción en una tubería.
    """
    import math
    
    # Conversiones
    if sistema == "Imperial":
        Q = flujo / 3600.0  # ft³/s
        rho = densidad      # lb/ft³
        nu = viscosidad * 0.00107639  # Stokes a ft²/s
        epsilon = 0.00015   # ft (acero comercial)
        psi_to_lbft2 = 144.0
    else:
        Q = flujo / 3600.0  # m³/s
        rho = densidad      # kg/m³
        nu = viscosidad * 1e-6  # cSt a m²/s
        epsilon = 0.00004572  # m
        psi_to_lbft2 = 1.0
    
    friccion_total = 0.0
    detalles = []
    
    for idx, row in df.iterrows():
        # Diámetro interno
        D_in_pulg = diametro_nominal_func(row['Diámetro'], row['Cédula'])
        if sistema == "SI":
            D = D_in_pulg * 0.0254  # m
        else:
            D = D_in_pulg / 12.0    # ft
        
        # Área y velocidad
        A = math.pi * (D ** 2) / 4.0
        V = Q / A
        
        # Reynolds
        Re = (V * D) / nu if nu > 0 else 1e6
        
        # Factor de fricción
        e_D = epsilon / D
        f = haaland_friction_factor(Re, e_D)
        
        # Longitud equivalente
        Le_pies = longitud_equivalente_func(row['Diámetro'], row['Accesorio'])
        if sistema == "SI":
            Le = Le_pies * 0.3048  # m
        else:
            Le = Le_pies          # ft
        
        # Longitud total
        L_total = row['Longitud'] + Le
        
        # Caída por fricción
        if sistema == "SI":
            dP = f * (L_total / D) * (rho * V**2 / 2.0)  # Pa
            dP_psi = dP / 6894.76
        else:
            dP = f * (L_total / D) * (rho * V**2 / 2.0) / psi_to_lbft2  # psi
            dP_psi = dP
        
        friccion_total += dP_psi
        
        detalles.append({
            'Línea': row['Número de Línea'],
            'Diámetro': row['Diámetro'],
            'Longitud (ft)': row['Longitud'],
            'Accesorio': row['Accesorio'],
            'Le (ft)': Le,
            'L_total (ft)': L_total,
            'Velocidad (ft/s)': V,
            'Re': Re,
            'f': f,
            'dP (psi)': dP_psi
        })
    
    return friccion_total, pd.DataFrame(detalles)

# =============================================================================
# 6. INTERFAZ DE USUARIO
# =============================================================================

# =============================================================================
# 6.1 PARÁMETROS GENERALES
# =============================================================================
st.subheader(t("pump_general_params_header"))

col_g1, col_g2, col_g3 = st.columns(3)
with col_g1:
    sp_gr = st.number_input(
        t("pump_specific_gravity"),
        value=0.485,
        min_value=0.1,
        max_value=5.0,
        step=0.001,
        format="%.3f",
        help=t("pump_specific_gravity_help")
    )
with col_g2:
    atm_pressure = st.number_input(
        t("pump_atm_pressure"),
        value=14.7,
        min_value=10.0,
        max_value=20.0,
        step=0.1,
        help=t("pump_atm_pressure_help")
    )
with col_g3:
    design_flow = st.number_input(
        t("pump_design_flow"),
        value=100.0,
        min_value=0.1,
        max_value=10000.0,
        step=1.0,
        help=t("pump_design_flow_help")
    )

# =============================================================================
# 6.2 ANÁLISIS HIDRÁULICO - SUCCIÓN
# =============================================================================
st.markdown("---")
st.subheader(t("pump_suction_analysis_header"))

# Opciones para selects
try:
    col_data = columnas()
    opcion1 = col_data['DIAMETRO'].to_list() if 'DIAMETRO' in col_data.columns else []
    opcion2 = col_data['ACCESORIO'].to_list() if 'ACCESORIO' in col_data.columns else []
    opcion3 = col_data['CEDULA'].to_list() if 'CEDULA' in col_data.columns else []
except:
    opcion1, opcion2, opcion3 = [], [], []

# Datos de succión
col_s1, col_s2 = st.columns(2)

with col_s1:
    suction_vessel = st.number_input(
        t("pump_suction_vessel"),
        value=200.0,
        min_value=0.0,
        max_value=1000.0,
        step=0.1,
        key="suction_vessel"
    )
    
    suction_elevation = st.number_input(
        t("pump_suction_elevation"),
        value=20.0,
        min_value=-100.0,
        max_value=500.0,
        step=0.1,
        key="suction_elevation",
        help=t("pump_suction_elevation_help")
    )

with col_s2:
    vapor_pressure = st.number_input(
        t("pump_vapor_pressure"),
        value=200.0,
        min_value=0.0,
        max_value=1000.0,
        step=0.1,
        key="vapor_pressure",
        help=t("pump_vapor_pressure_help")
    )
    
    # Sistema de unidades para el análisis hidráulico
    sistema_hid = st.radio(
        t("pump_unit_system"),
        [t("pump_unit_imperial"), t("pump_unit_si")],
        horizontal=True,
        index=0,
        key="sistema_hid_succion"
    )

# Tabla de líneas de succión
st.caption(t("pump_suction_lines_caption"))

col_s3, col_s4 = st.columns(2)

with col_s3:
    numlinea_s = st.number_input(t("pump_line_number_suction"), step=1, key="numlinea_s")
    if sistema_hid == t("pump_unit_imperial"):
        longitud_s = st.number_input(t("pump_length_ft"), value=0.0, step=0.1, key="long_s")
        diametro_s = st.selectbox(t("pump_diameter_in"), opcion1, placeholder=t("pump_diameter_placeholder"), key="diam_s")
    else:
        longitud_s = st.number_input(t("pump_length_m"), value=0.0, step=0.1, key="long_s")
        diametro_s = st.selectbox(t("pump_diameter_mm"), opcion1, placeholder=t("pump_diameter_placeholder"), key="diam_s")

with col_s4:
    accesorio_s = st.selectbox(t("pump_accessories"), opcion2, placeholder=t("pump_accessories_placeholder"), key="acc_s")
    cedula_s = st.selectbox(t("pump_schedule"), opcion3, placeholder=t("pump_schedule_placeholder"), key="ced_s")
    if sistema_hid == t("pump_unit_imperial"):
        elevacion_s = st.number_input(t("pump_elevation_ft"), value=0.0, step=0.1, key="elev_s")
    else:
        elevacion_s = st.number_input(t("pump_elevation_m"), value=0.0, step=0.1, key="elev_s")

# Botón agregar fila succión
if st.button(t("pump_add_suction_button"), key="add_succion"):
    if not numlinea_s:
        st.warning(t("pump_warn_line_number"))
    elif longitud_s == 0.0:
        st.warning(t("pump_warn_length"))
    elif not diametro_s or diametro_s == t("pump_diameter_placeholder"):
        st.warning(t("pump_warn_diameter"))
    elif not accesorio_s or accesorio_s == t("pump_accessories"):
        st.warning(t("pump_warn_accessory"))
    elif not cedula_s or cedula_s == t("pump_schedule"):
        st.warning(t("pump_warn_schedule"))
    else:
        nueva_fila = pd.DataFrame({
            'Número de Línea': [numlinea_s],
            'Diámetro': [diametro_s],
            'Cédula': [cedula_s],
            'Longitud': [longitud_s],
            'Accesorio': [accesorio_s],
            'Elevación': [elevacion_s]
        })
        st.session_state.tabla_succion = pd.concat(
            [st.session_state.tabla_succion, nueva_fila], ignore_index=True
        )
        st.success(t("pump_success_section_added"))

# Mostrar tabla de succión
if not st.session_state.tabla_succion.empty:
    edited_df_s = st.data_editor(
        st.session_state.tabla_succion,
        use_container_width=True,
        num_rows="dynamic",
        key='editor_succion'
    )
    st.session_state.tabla_succion = edited_df_s

# =============================================================================
# 6.3 ANÁLISIS HIDRÁULICO - DESCARGA
# =============================================================================
st.markdown("---")
st.subheader(t("pump_discharge_analysis_header"))

col_d1, col_d2 = st.columns(2)

with col_d1:
    discharge_vessel = st.number_input(
        t("pump_discharge_vessel"),
        value=st.session_state.get('discharge_vessel', 220.0),
        min_value=0.0,
        max_value=1000.0,
        step=0.1,
        key="discharge_vessel_input"
    )
    
    discharge_elevation = st.number_input(
        t("pump_discharge_elevation"),
        value=st.session_state.get('discharge_elevation', 74.0),
        min_value=-100.0,
        max_value=500.0,
        step=0.1,
        key="discharge_elevation_input",
        help=t("pump_discharge_elevation_help")
    )

with col_d2:
    # Usar clave diferente para el widget
    control_valve_dp = st.number_input(
        t("pump_control_valve_dp"),
        value=st.session_state.get('control_valve_dp', 9.0),
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        key="control_valve_dp_widget",  # <-- Clave diferente
        help=t("pump_control_valve_dp_help")
    )
    # Ahora podemos asignar manualmente sin conflicto
    st.session_state.control_valve_dp = control_valve_dp

# Tabla de líneas de descarga
st.caption(t("pump_discharge_lines_caption"))

col_d3, col_d4 = st.columns(2)

with col_d3:
    numlinea_d = st.number_input(t("pump_line_number_discharge"), step=1, key="numlinea_d")
    if sistema_hid == t("pump_unit_imperial"):
        longitud_d = st.number_input(t("pump_length_ft"), value=0.0, step=0.1, key="long_d")
        diametro_d = st.selectbox(t("pump_diameter_in"), opcion1, placeholder=t("pump_diameter_placeholder"), key="diam_d")
    else:
        longitud_d = st.number_input(t("pump_length_m"), value=0.0, step=0.1, key="long_d")
        diametro_d = st.selectbox(t("pump_diameter_mm"), opcion1, placeholder=t("pump_diameter_placeholder"), key="diam_d")

with col_d4:
    accesorio_d = st.selectbox(t("pump_accessories"), opcion2, placeholder=t("pump_accessories_placeholder"), key="acc_d")
    cedula_d = st.selectbox(t("pump_schedule"), opcion3, placeholder=t("pump_schedule_placeholder"), key="ced_d")
    if sistema_hid == t("pump_unit_imperial"):
        elevacion_d = st.number_input(t("pump_elevation_ft"), value=0.0, step=0.1, key="elev_d")
    else:
        elevacion_d = st.number_input(t("pump_elevation_m"), value=0.0, step=0.1, key="elev_d")

# Botón agregar fila descarga
if st.button(t("pump_add_discharge_button"), key="add_discharge"):
    if not numlinea_d:
        st.warning(t("pump_warn_line_number"))
    elif longitud_d == 0.0:
        st.warning(t("pump_warn_length"))
    elif not diametro_d or diametro_d == t("pump_diameter_placeholder"):
        st.warning(t("pump_warn_diameter"))
    elif not accesorio_d or accesorio_d == t("pump_accessories"):
        st.warning(t("pump_warn_accessory"))
    elif not cedula_d or cedula_d == t("pump_schedule"):
        st.warning(t("pump_warn_schedule"))
    else:
        nueva_fila = pd.DataFrame({
            'Número de Línea': [numlinea_d],
            'Diámetro': [diametro_d],
            'Cédula': [cedula_d],
            'Longitud': [longitud_d],
            'Accesorio': [accesorio_d],
            'Elevación': [elevacion_d]
        })
        st.session_state.tabla_descarga = pd.concat(
            [st.session_state.tabla_descarga, nueva_fila], ignore_index=True
        )
        st.success(t("pump_success_section_added"))

# Mostrar tabla de descarga
if not st.session_state.tabla_descarga.empty:
    edited_df_d = st.data_editor(
        st.session_state.tabla_descarga,
        use_container_width=True,
        num_rows="dynamic",
        key='editor_descarga'
    )
    st.session_state.tabla_descarga = edited_df_d

# =============================================================================
# 6.4 BOTÓN DE CÁLCULO
# =============================================================================
st.markdown("---")
col_calc1, col_calc2, col_calc3 = st.columns([1, 2, 1])
with col_calc2:
    calcular = st.button(t("pump_calculate_button"), use_container_width=True, type="primary")

# =============================================================================
# 6.5 PROCESAR CÁLCULO
# =============================================================================
if calcular:
    # Crear instancia de la calculadora
    calc = PumpCalculator(sp_gr, atm_pressure)
    
    # ===== Calcular fricción en succión =====
    if not st.session_state.tabla_succion.empty:
        suction_friction, suction_detalles = calcular_friccion_tuberia(
            st.session_state.tabla_succion,
            sistema_hid,
            design_flow,
            sp_gr * 62.4 if sistema_hid == "Imperial" else sp_gr * 1000,
            1.0,  # viscosidad (valor por defecto)
            diametro_nominal,
            longitud_equivalente
        )
    else:
        suction_friction = 0.0
        suction_detalles = pd.DataFrame()
    
    # ===== Calcular fricción en descarga =====
    if not st.session_state.tabla_descarga.empty:
        discharge_friction, discharge_detalles = calcular_friccion_tuberia(
            st.session_state.tabla_descarga,
            sistema_hid,
            design_flow,
            sp_gr * 62.4 if sistema_hid == "Imperial" else sp_gr * 1000,
            1.0,
            diametro_nominal,
            longitud_equivalente
        )
    else:
        discharge_friction = 0.0
        discharge_detalles = pd.DataFrame()
    
    # ===== Agregar válvula de control =====
    discharge_friction_total = discharge_friction + control_valve_dp
    
    # ===== Calcular presiones =====
    suction_pressure = calc.calculate_suction_pressure(
        suction_vessel, suction_elevation, suction_friction
    )
    discharge_pressure = calc.calculate_discharge_pressure(
        discharge_vessel, discharge_elevation, discharge_friction_total
    )
    
    # ===== Cabeza diferencial =====
    differential_head = calc.calculate_differential_head(
        suction_pressure, discharge_pressure
    )
    
    # ===== Cabeza requerida =====
    safety_factor = 0.10  # 10% por defecto
    required_head = calc.calculate_required_head(differential_head, safety_factor)
    
    # ===== NPSHA =====
    npsha = calc.calculate_npsha(
        suction_vessel, suction_elevation,
        suction_friction, vapor_pressure
    )
    
    # ===== Guardar resultados =====
    st.session_state.results = {
        'calculator': calc,
        'sp_gr': sp_gr,
        'atm_pressure': atm_pressure,
        'design_flow_gpm': design_flow,
        'suction_vessel_pressure_psia': suction_vessel,
        'suction_elevation_ft': suction_elevation,
        'suction_friction_psi': suction_friction,
        'suction_friction_detalles': suction_detalles,
        'suction_pressure_psia': suction_pressure,
        'suction_pressure_psig': calc.psia_to_psig(suction_pressure),
        'discharge_vessel_pressure_psia': discharge_vessel,
        'discharge_elevation_ft': discharge_elevation,
        'discharge_friction_psi': discharge_friction_total,
        'discharge_friction_detalles': discharge_detalles,
        'control_valve_dp_psi': control_valve_dp,
        'discharge_pressure_psia': discharge_pressure,
        'discharge_pressure_psig': calc.psia_to_psig(discharge_pressure),
        'differential_pressure_psi': discharge_pressure - suction_pressure,
        'differential_head_ft': differential_head,
        'safety_factor': safety_factor,
        'required_head_ft': required_head,
        'npsha_ft': npsha,
        'vapor_pressure_psia': vapor_pressure,
        'static_head_ft': discharge_elevation - suction_elevation,
        'sistema_hid': sistema_hid,
    }
    
    st.rerun()

# =============================================================================
# 7. MOSTRAR RESULTADOS
# =============================================================================
if st.session_state.results is not None:
    r = st.session_state.results
    calc = r['calculator']

    st.markdown("---")
    st.markdown(f'<p class="sub-header">{t("pump_results_header")}</p>', unsafe_allow_html=True)

    # ===== RESUMEN EN TARJETAS =====
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)

    with col_res1:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("pump_card_suction_pressure")}</strong><br>
            <span class="highlight">{r['suction_pressure_psia']:.1f} psia</span><br>
            <small>{r['suction_pressure_psig']:.1f} psig</small>
        </div>
        """, unsafe_allow_html=True)

    with col_res2:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("pump_card_discharge_pressure")}</strong><br>
            <span class="highlight">{r['discharge_pressure_psia']:.1f} psia</span><br>
            <small>{r['discharge_pressure_psig']:.1f} psig</small>
        </div>
        """, unsafe_allow_html=True)

    with col_res3:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("pump_card_differential_head")}</strong><br>
            <span class="highlight">{r['differential_head_ft']:.1f} ft</span><br>
            <small>ΔP = {r['differential_pressure_psi']:.1f} psi</small>
        </div>
        """, unsafe_allow_html=True)

    with col_res4:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("pump_card_required_head")}</strong><br>
            <span class="highlight">{r['required_head_ft']:.1f} ft</span><br>
            <small>{t("pump_card_safety_factor").format(r['safety_factor']*100)}</small>
        </div>
        """, unsafe_allow_html=True)

    # ===== NPSHA =====
    st.markdown("---")
    col_n1, col_n2, col_n3 = st.columns(3)
    with col_n1:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("pump_card_npsha")}</strong><br>
            <span class="highlight">{r['npsha_ft']:.1f} ft</span>
        </div>
        """, unsafe_allow_html=True)

    with col_n2:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("pump_card_static_head")}</strong><br>
            <span>{r['static_head_ft']:.1f} ft</span>
        </div>
        """, unsafe_allow_html=True)

    with col_n3:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("pump_card_design_flow")}</strong><br>
            <span>{r['design_flow_gpm']:.0f} gpm</span>
        </div>
        """, unsafe_allow_html=True)

    # ===== DETALLE DE FRICCIÓN =====
    st.markdown("---")
    col_f1, col_f2 = st.columns(2)

    with col_f1:
        st.markdown(t("pump_friction_suction"))
        if not r['suction_friction_detalles'].empty:
            st.dataframe(r['suction_friction_detalles'], use_container_width=True)
        st.write(t("pump_friction_total_suction").format(r['suction_friction_psi']))

    with col_f2:
        st.markdown(t("pump_friction_discharge"))
        if not r['discharge_friction_detalles'].empty:
            st.dataframe(r['discharge_friction_detalles'], use_container_width=True)
        st.write(t("pump_friction_pipe_accessories").format(r['discharge_friction_psi'] - r['control_valve_dp_psi']))
        st.write(t("pump_friction_control_valve").format(r['control_valve_dp_psi']))
        st.write(t("pump_friction_total_discharge").format(r['discharge_friction_psi']))

    # ===== SECCIÓN DE CURVA DE BOMBA =====
    st.markdown("---")
    st.markdown(f'<p class="sub-header">{t("pump_pump_curve_header")}</p>', unsafe_allow_html=True)

    # Input para la curva de la bomba
    st.markdown(t("pump_curve_instructions"))

    col_curve1, col_curve2 = st.columns([2, 1])

    with col_curve1:
        curve_data = st.data_editor(
            st.session_state.pump_curve_df,
            num_rows="dynamic",
            column_config={
                t("pump_curve_col_flow"): st.column_config.NumberColumn(
                    t("pump_curve_col_flow"),
                    min_value=0,
                    step=1,
                ),
                t("pump_curve_col_head"): st.column_config.NumberColumn(
                    t("pump_curve_col_head"),
                    min_value=0,
                    step=1,
                ),
            },
            use_container_width=True,
            key="pump_curve_editor"
        )
        st.session_state.pump_curve_df = curve_data

    with col_curve2:
        st.caption(t("pump_curve_example_caption"))
        st.code("""
Caudal (gpm) | Cabeza (ft)
0           | 450
50          | 420
100         | 370
150         | 300
200         | 210
        """)

        if st.button(t("pump_curve_load_example_button"), use_container_width=True):
            st.session_state.pump_curve_df = pd.DataFrame({
                t("pump_curve_col_flow"): [0, 50, 100, 150, 200],
                t("pump_curve_col_head"): [450, 420, 370, 300, 210]
            })
            st.rerun()

    # ===== PROCESAR CURVA Y GENERAR GRÁFICA =====
    if len(curve_data) >= 2:
        try:
            flow_data = curve_data[t("pump_curve_col_flow")].tolist()
            head_data = curve_data[t("pump_curve_col_head")].tolist()

            if all(isinstance(x, (int, float)) for x in flow_data) and \
               all(isinstance(y, (int, float)) for y in head_data):

                pairs = sorted(zip(flow_data, head_data))
                flow_sorted, head_sorted = zip(*pairs)

                # Interpolar para obtener la cabeza al caudal de diseño
                design_head = calc.interpolate_pump_curve(
                    flow_data, head_data, r['design_flow_gpm']
                )

                # Generar curva del sistema
                static_head = r['static_head_ft']
                friction_head_at_design = r['differential_head_ft'] - static_head
                flow_range = np.linspace(0, max(flow_sorted) * 1.2, 100)
                system_head = calc.get_system_curve(
                    flow_range, static_head, friction_head_at_design, r['design_flow_gpm']
                )

                # Encontrar punto de operación
                op_flow, op_head = calc.find_operating_point(
                    flow_data, head_data, flow_range, system_head
                )

                # ===== GRÁFICA =====
                fig, ax = plt.subplots(figsize=(10, 6))

                ax.plot(flow_sorted, head_sorted, 'b-', linewidth=2.5, label=t("pump_curve_trace_pump"))
                ax.plot(flow_sorted, head_sorted, 'bo', markersize=6)
                ax.plot(flow_range, system_head, 'g--', linewidth=2, label=t("pump_curve_trace_system"))

                ax.plot(r['design_flow_gpm'], design_head, 'go', markersize=10,
                        label=t("pump_curve_label_design").format(r["design_flow_gpm"], design_head))

                if op_flow is not None and op_head is not None:
                    ax.plot(op_flow, op_head, 'ro', markersize=12,
                            label=t("pump_curve_label_operation").format(op_flow, op_head))

                ax.axhline(y=r['required_head_ft'], color='r', linestyle='--', linewidth=1.5,
                           label=t("pump_curve_label_required_head").format(r["required_head_ft"]))
                ax.axhline(y=r['differential_head_ft'], color='orange', linestyle=':', linewidth=1.5,
                           label=t("pump_curve_label_diff_head").format(r["differential_head_ft"]))

                ax.set_xlabel(t("pump_curve_axis_flow"), fontsize=12)
                ax.set_ylabel(t("pump_curve_axis_head"), fontsize=12)
                ax.set_title(t("pump_curve_title"), fontsize=14)
                ax.grid(True, alpha=0.3)
                ax.legend(loc='best', fontsize=10)

                st.pyplot(fig)

                # ===== INTERPRETACIÓN =====
                st.markdown("---")
                st.markdown(t("pump_interpretation_header"))

                col_op1, col_op2, col_op3 = st.columns(3)

                with col_op1:
                    if op_flow is not None:
                        st.metric(t("pump_metric_operation_flow"), f"{op_flow:.0f} gpm")
                    else:
                        st.warning(t("pump_warn_no_operation_point"))

                with col_op2:
                    if op_head is not None:
                        st.metric(t("pump_metric_operation_head"), f"{op_head:.0f} ft")
                    else:
                        st.warning(t("pump_warn_no_operation_point"))

                with col_op3:
                    if design_head is not None:
                        if design_head >= r['required_head_ft']:
                            st.success(t("pump_success_pump_adequate").format(design_head, r['required_head_ft']))
                        else:
                            st.error(t("pump_error_pump_not_adequate").format(design_head, r['required_head_ft']))
                    else:
                        st.warning(t("pump_warn_no_interpolation"))

            else:
                st.warning(t("pump_warn_numeric_values"))

        except Exception as e:
            st.error(t("pump_error_processing_curve").format(str(e)))
    else:
        st.info(t("pump_info_min_two_points"))

else:
    st.info(t("pump_info_initial_message"))

# =============================================================================
# 8. FOOTER
# =============================================================================
st.markdown("---")
st.caption(t("pump_footer"))