"""
Aplicación Streamlit para turbinas centrífugas.
Soporta expansión isentrópica y politrópica.
Incluye curvas de turbina y eficiencia, puntos de operación.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.turbinas import TurbineCalculator
from utils.i18n import language_selector
from languages.turbina_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()

# st.set_page_config(page_title="Turbina Centrífuga", page_icon="⚡", layout="wide")

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

# st.markdown('<p class="main-header">⚡ Turbina Centrífuga</p>', unsafe_allow_html=True)
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
    page_icon="⚡",
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

st.markdown("---")

# ============================================
# RESULTADOS OBTENIDOS
# ============================================
st.header(t("results_header"))

with st.expander(t("thermo_expander_title"), expanded=False):
    st.markdown(t("thermo_expander_text"))

with st.expander(t("curves_expander_title"), expanded=False):
    st.markdown(t("curves_expander_text"))

with st.expander(t("power_expander_title"), expanded=False):
    st.markdown(t("power_expander_text"))

with st.expander(t("eval_expander_title"), expanded=False):
    st.markdown(t("eval_expander_text"))

with st.expander(t("all_params_expander_title"), expanded=False):
    st.markdown(t("all_params_expander_text"))

st.markdown("---")

# ============================================
# ALCANCE Y APLICABILIDAD
# ============================================
st.header(t("applications_header"))
st.markdown(t("applications_text"))

st.caption(t("caption"))

# Inicialización
if 'turb_results' not in st.session_state:
    st.session_state.turb_results = None
if 'turb_curve_df' not in st.session_state:
    st.session_state.turb_curve_df = pd.DataFrame({'Caudal (m³/h)': [], 'Cabeza (J/kg)': []})
if 'eff_curve_df' not in st.session_state:
    st.session_state.eff_curve_df = pd.DataFrame({'Caudal (m³/h)': [], 'Eficiencia (%)': []})

# =============================================================================
# PARÁMETROS DEL GAS Y CONDICIONES
# =============================================================================
st.subheader(t("turb_gas_params_header"))

# Primera fila: Parámetros del gas
col_g1, col_g2, col_g3 = st.columns(3)

with col_g1:
    R = st.number_input(t("turb_gas_constant"), value=8.314, step=0.001, format="%.3f")
    MW = st.number_input(t("turb_molecular_weight"), value=28.97, min_value=1.0, max_value=100.0, step=0.01)

with col_g2:
    Z_avg = st.number_input(t("turb_z_avg"), value=0.98, min_value=0.5, max_value=1.5, step=0.01)
    k = st.number_input(t("turb_k_ratio"), value=1.4, min_value=1.0, max_value=2.0, step=0.01)

with col_g3:
    # SELECTOR DEL MÉTODO DE CÁLCULO
    comp_type = st.selectbox(
        t("turb_calc_method"),
        options=['isentropic', 'polytropic'],
        format_func=lambda x: t("turb_method_isentropic") if x == 'isentropic' else t("turb_method_polytropic"),
        help=t("turb_calc_method_help")
    )
    
    if comp_type == 'isentropic':
        eta_label = t("turb_eta_isentropic")
        eta_default = 85.0
    else:
        eta_label = t("turb_eta_polytropic")
        eta_default = 85.0
    eta = st.number_input(eta_label, value=eta_default, min_value=10.0, max_value=95.0, step=0.5) / 100.0

# Segunda fila: Condiciones de operación
st.markdown("---")
st.subheader(t("turb_op_conditions_header"))

col_op1, col_op2, col_op3 = st.columns(3)

with col_op1:
    T1 = st.number_input(t("turb_inlet_temp"), value=500.0, step=0.5)
    P1 = st.number_input(t("turb_inlet_pressure"), value=1000.0, min_value=1.0, step=0.5)

with col_op2:
    P2 = st.number_input(t("turb_outlet_pressure"), value=350.0, min_value=1.0, step=0.5)
    Q_design = st.number_input(t("turb_design_flow"), value=5000.0, min_value=1.0, step=10.0)

with col_op3:
    st.markdown(t("turb_op_points_header"))
    rated_pct = st.number_input(t("turb_rated_pct"), value=100.0, min_value=10.0, max_value=150.0, step=1.0, key="rated_pct")
    normal_pct = st.number_input(t("turb_normal_pct"), value=85.0, min_value=5.0, max_value=100.0, step=1.0, key="normal_pct")
    min_pct = st.number_input(t("turb_min_pct"), value=50.0, min_value=5.0, max_value=100.0, step=1.0, key="min_pct")

# =============================================================================
# BOTÓN DE CARGA DE EJEMPLO Y LIMPIEZA
# =============================================================================
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn1:
    if st.button(t("turb_load_example_button"), use_container_width=True):
        st.session_state.use_example = True
        st.session_state.T1_ex = 500.0
        st.session_state.P1_ex = 1000.0
        st.session_state.P2_ex = 350.0
        st.session_state.Q_design_ex = 5000.0
        st.session_state.eta_ex = 85.0
        st.session_state.turb_curve_df = pd.DataFrame({
            t("turb_curve_col_flow"): [0, 2000, 4000, 6000, 8000, 10000],
            t("turb_curve_col_head"): [250000, 240000, 220000, 190000, 150000, 100000]
        })
        st.session_state.eff_curve_df = pd.DataFrame({
            t("turb_eff_curve_col_flow"): [2000, 4000, 6000, 8000, 10000],
            t("turb_eff_curve_col_eff"): [82, 86, 88, 84, 78]
        })
        st.rerun()

with col_btn2:
    if st.button(t("turb_clear_button"), use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ('turb_results', 'turb_curve_df', 'eff_curve_df'):
                del st.session_state[key]
        st.session_state.turb_curve_df = pd.DataFrame({t("turb_curve_col_flow"): [], t("turb_curve_col_head"): []})
        st.session_state.eff_curve_df = pd.DataFrame({t("turb_eff_curve_col_flow"): [], t("turb_eff_curve_col_eff"): []})
        st.rerun()

# Recuperar valores de ejemplo si existen
if 'use_example' in st.session_state and st.session_state.use_example:
    T1 = st.session_state.get('T1_ex', 500.0)
    P1 = st.session_state.get('P1_ex', 1000.0)
    P2 = st.session_state.get('P2_ex', 350.0)
    Q_design = st.session_state.get('Q_design_ex', 5000.0)
    eta = st.session_state.get('eta_ex', 85.0) / 100.0
else:
    # Usar valores de los widgets (ya están definidos arriba)
    pass

# =============================================================================
# BOTÓN DE CÁLCULO
# =============================================================================
st.markdown("---")
col_calc1, col_calc2, col_calc3 = st.columns([1, 2, 1])
with col_calc2:
    calcular = st.button(t("turb_calculate_button"), use_container_width=True, type="primary")

# =============================================================================
# PROCESAR CÁLCULO
# =============================================================================
if calcular:
    T1_K = T1 + 273.15
    
    # Crear calculadora
    calc = TurbineCalculator(R=R, MW=MW, Z_avg=Z_avg, k=k, eta=eta,
                             T1=T1_K, P1=P1, P2=P2, Q_vol=Q_design,
                             comp_type=comp_type)
    # Calcular cabeza y potencia
    H_calc = calc.head()
    m_dot = calc.mass_flow(Q_design, P1, T1_K)
    P_pow = calc.power()
    rp = P1 / P2  # relación de expansión
    T2 = calc.discharge_temperature()
    T2_ideal = calc.discharge_temperature_ideal() if comp_type == 'isentropic' else None
    n = getattr(calc, 'n', None)

    st.session_state.turb_results = {
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
        'rated_pct': rated_pct,
        'normal_pct': normal_pct,
        'min_pct': min_pct,
    }
    st.rerun()

# =============================================================================
# MOSTRAR RESULTADOS
# =============================================================================
if st.session_state.turb_results is not None:
    res = st.session_state.turb_results
    calc = res['calc']

    st.markdown("---")
    results_title = t("turb_results_isentropic") if res["comp_type"] == "isentropic" else t("turb_results_polytropic")
    st.markdown(f'<p class="sub-header">{results_title}</p>', unsafe_allow_html=True)

    # Tarjetas resumen
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    with col_r1:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("turb_card_expansion_ratio")}</strong><br>
            <span class="highlight">{res['rp']:.3f}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_r2:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("turb_card_head_work")}</strong><br>
            <span class="highlight">{res['H_calc_Jkg']:.0f} J/kg</span><br>
            <small>{t("turb_card_head_fluid_col").format(f"{res['H_calc_m']:.1f}")}</small>
        </div>
        """, unsafe_allow_html=True)
    with col_r3:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("turb_card_mass_flow")}</strong><br>
            <span class="highlight">{res['mass_flow_kgs']:.3f} kg/s</span>
        </div>
        """, unsafe_allow_html=True)
    with col_r4:
        st.markdown(f"""
        <div class="result-card">
            <strong>{t("turb_card_power_generated")}</strong><br>
            <span class="highlight">{res['power_kW']:.1f} kW</span>
        </div>
        """, unsafe_allow_html=True)

    # Detalles adicionales
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        if res['comp_type'] == 'polytropic' and res['n'] is not None:
            st.markdown(t("turb_polytropic_exponent").format(res['n']))
        else:
            st.markdown(t("turb_k_label").format(res['k']))
    with col_d2:
        st.markdown(t("turb_efficiency_label").format(res['eta']*100))
    with col_d3:
        st.markdown(t("turb_z_avg_label").format(res['Z_avg']))

    # Temperaturas
    st.markdown("---")
    st.markdown(t("turb_temperatures_header"))
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.metric(t("turb_temp_inlet"), f"{res['T1_C']:.1f} °C")
    with col_t2:
        if res['comp_type'] == 'isentropic' and res['T2_ideal_C'] is not None:
            st.metric(t("turb_temp_outlet_ideal"), f"{res['T2_ideal_C']:.1f} °C")
        else:
            st.metric(t("turb_temp_outlet_polytropic"), f"{res['T2_C']:.1f} °C")
    with col_t3:
        st.metric(t("turb_temp_outlet_real"), f"{res['T2_C']:.1f} °C")

    # ================== CURVAS DE LA TURBINA ==================
    st.markdown("---")
    st.markdown(f'<p class="sub-header">{t("turb_turbine_curves_header")}</p>', unsafe_allow_html=True)

    col_curve1, col_curve2 = st.columns([2, 1])
    with col_curve1:
        st.markdown(t("turb_head_vs_flow_header"))
        curve_data = st.data_editor(
            st.session_state.turb_curve_df,
            num_rows="dynamic",
            column_config={
                t("turb_curve_col_flow"): st.column_config.NumberColumn(t("turb_curve_col_flow"), min_value=0, step=1),
                t("turb_curve_col_head"): st.column_config.NumberColumn(t("turb_curve_col_head"), min_value=0, step=1),
            },
            use_container_width=True,
            key="turb_curve_editor"
        )
        st.session_state.turb_curve_df = curve_data

        st.markdown(t("turb_eff_curve_header"))
        eff_data = st.data_editor(
            st.session_state.eff_curve_df,
            num_rows="dynamic",
            column_config={
                t("turb_eff_curve_col_flow"): st.column_config.NumberColumn(t("turb_eff_curve_col_flow"), min_value=0, step=1),
                t("turb_eff_curve_col_eff"): st.column_config.NumberColumn(t("turb_eff_curve_col_eff"), min_value=0, max_value=100, step=0.1),
            },
            use_container_width=True,
            key="eff_curve_editor"
        )
        st.session_state.eff_curve_df = eff_data

    with col_curve2:
        st.caption(t("turb_curve_example_caption"))
        st.code("""
Caudal (m³/h) | Cabeza (J/kg)
0            | 250000
2000         | 240000
4000         | 220000
6000         | 190000
8000         | 150000
10000        | 100000
        """)
        st.caption(t("turb_eff_example_caption"))
        st.code("""
Caudal (m³/h) | Eficiencia (%)
2000         | 82
4000         | 86
6000         | 88
8000         | 84
10000        | 78
        """)
        if st.button(t("turb_load_examples_button"), use_container_width=True):
            st.session_state.turb_curve_df = pd.DataFrame({
                t("turb_curve_col_flow"): [0, 2000, 4000, 6000, 8000, 10000],
                t("turb_curve_col_head"): [250000, 240000, 220000, 190000, 150000, 100000]
            })
            st.session_state.eff_curve_df = pd.DataFrame({
                t("turb_eff_curve_col_flow"): [2000, 4000, 6000, 8000, 10000],
                t("turb_eff_curve_col_eff"): [82, 86, 88, 84, 78]
            })
            st.rerun()

    # ================== PROCESAR CURVAS ==================
    if len(curve_data) >= 2:
        try:
            Q_data = curve_data[t("turb_curve_col_flow")].tolist()
            H_data = curve_data[t("turb_curve_col_head")].tolist()
            if all(isinstance(x, (int, float)) for x in Q_data) and all(isinstance(y, (int, float)) for y in H_data):
                pairs = sorted(zip(Q_data, H_data))
                Q_sorted, H_sorted = zip(*pairs)

                Q_design = res['Q_design']
                Q_rated = Q_design * (res['rated_pct'] / 100.0)
                Q_normal = Q_design * (res['normal_pct'] / 100.0)
                Q_min = Q_design * (res['min_pct'] / 100.0)

                # Interpolar cabeza
                H_design = calc.interpolate_curve(Q_data, H_data, Q_design)
                H_rated = calc.interpolate_curve(Q_data, H_data, Q_rated)
                H_normal = calc.interpolate_curve(Q_data, H_data, Q_normal)
                H_min = calc.interpolate_curve(Q_data, H_data, Q_min)

                # Interpolar eficiencia
                eff_design = eff_rated = eff_normal = eff_min = None
                if len(eff_data) >= 2:
                    Q_eff = eff_data[t("turb_eff_curve_col_flow")].tolist()
                    Eff_eff = eff_data[t("turb_eff_curve_col_eff")].tolist()
                    if all(isinstance(x, (int, float)) for x in Q_eff) and all(isinstance(y, (int, float)) for y in Eff_eff):
                        eff_design = calc.interpolate_curve(Q_eff, Eff_eff, Q_design) / 100.0
                        eff_rated = calc.interpolate_curve(Q_eff, Eff_eff, Q_rated) / 100.0
                        eff_normal = calc.interpolate_curve(Q_eff, Eff_eff, Q_normal) / 100.0
                        eff_min = calc.interpolate_curve(Q_eff, Eff_eff, Q_min) / 100.0

                # Calcular potencia usando cabeza de curva (potencia generada)
                def power_from_curve(Q, H, eff=None):
                    if H is None:
                        return None
                    if eff is None:
                        eff = res['eta']
                    m_dot = calc.mass_flow(Q, res['P1'], res['T1_K'])
                    return (m_dot * H) / 1000.0  # kW (H en J/kg)

                P_design = power_from_curve(Q_design, H_design, eff_design)
                P_rated = power_from_curve(Q_rated, H_rated, eff_rated)
                P_normal = power_from_curve(Q_normal, H_normal, eff_normal)
                P_min = power_from_curve(Q_min, H_min, eff_min)

                # Guardar
                res['H_design'] = H_design
                res['H_rated'] = H_rated
                res['H_normal'] = H_normal
                res['H_min'] = H_min
                res['P_design'] = P_design
                res['P_rated'] = P_rated
                res['P_normal'] = P_normal
                res['P_min'] = P_min
                res['eff_design'] = eff_design
                res['eff_rated'] = eff_rated
                res['eff_normal'] = eff_normal
                res['eff_min'] = eff_min

                # ===== TABLA DE POTENCIA =====
                st.markdown("---")
                st.markdown(t("turb_power_points_header"))

                power_data = []
                for label, q, h, p, e in [
                    (t("turb_point_design"), Q_design, H_design, P_design, eff_design),
                    (t("turb_point_rated"), Q_rated, H_rated, P_rated, eff_rated),
                    (t("turb_point_normal"), Q_normal, H_normal, P_normal, eff_normal),
                    (t("turb_point_min"), Q_min, H_min, P_min, eff_min)
                ]:
                    if h is not None and p is not None:
                        power_data.append({
                            t("turb_col_point"): label,
                            t("turb_col_flow"): f"{q:.1f}",
                            t("turb_col_head"): f"{h:.0f}",
                            t("turb_col_efficiency"): f"{e*100:.1f}" if e else t("turb_eff_global_format").format(res['eta']*100),
                            t("turb_col_power"): f"{p:.1f}"
                        })
                if power_data:
                    st.table(pd.DataFrame(power_data))
                else:
                    st.warning(t("turb_warn_no_power"))

                # ===== GRÁFICA =====
                # Curva del sistema (simple, H_sys = K * Q^2) usando punto de diseño
                if H_design is not None and Q_design > 0:
                    K = H_design / (Q_design ** 2)
                    Q_range = np.linspace(0, max(Q_sorted)*1.1, 100)
                    H_sys = K * Q_range ** 2
                else:
                    Q_range = np.linspace(0, max(Q_sorted)*1.1, 100)
                    H_sys = np.zeros_like(Q_range)

                op_Q, op_H = calc.find_operating_point(Q_data, H_data, Q_range, H_sys)

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(Q_sorted, H_sorted, 'b-', linewidth=2.5, label=t("turb_curve_turbine_trace"))
                ax.plot(Q_sorted, H_sorted, 'bo', markersize=6)

                if H_design:
                    ax.plot(Q_design, H_design, 'go', markersize=10, label=t("turb_curve_design_trace").format(Q_design, H_design))
                if H_rated:
                    ax.plot(Q_rated, H_rated, 'mo', markersize=10, label=t("turb_curve_rated_trace").format(Q_rated, H_rated))
                if H_normal:
                    ax.plot(Q_normal, H_normal, 'co', markersize=10, label=t("turb_curve_normal_trace").format(Q_normal, H_normal))
                if H_min:
                    ax.plot(Q_min, H_min, 'yo', markersize=10, label=t("turb_curve_min_trace").format(Q_min, H_min))

                if op_Q is not None and op_H is not None:
                    ax.plot(op_Q, op_H, 'ro', markersize=12, label=t("turb_curve_operation_trace").format(op_Q, op_H))

                # Eficiencia en eje secundario
                if len(eff_data) >= 2:
                    Q_eff = eff_data[t("turb_eff_curve_col_flow")].tolist()
                    Eff_eff = eff_data[t("turb_eff_curve_col_eff")].tolist()
                    if all(isinstance(x, (int, float)) for x in Q_eff) and all(isinstance(y, (int, float)) for y in Eff_eff):
                        ax2 = ax.twinx()
                        ax2.plot(Q_eff, Eff_eff, 'r--', linewidth=2, label=t("turb_curve_eff_trace"))
                        ax2.set_ylabel(t("turb_curve_axis_eff"), color='r')
                        ax2.tick_params(axis='y', labelcolor='r')
                        lines, labels = ax.get_legend_handles_labels()
                        lines2, labels2 = ax2.get_legend_handles_labels()
                        ax.legend(lines + lines2, labels + labels2, loc='best')

                ax.set_xlabel(t("turb_curve_axis_flow"), fontsize=12)
                ax.set_ylabel(t("turb_curve_axis_head"), fontsize=12)
                comp_type_label = t("turb_method_isentropic") if res["comp_type"] == "isentropic" else t("turb_method_polytropic")
                ax.set_title(t("turb_curve_title").format(comp_type_label), fontsize=14)
                ax.grid(True, alpha=0.3)
                if len(eff_data) < 2:
                    ax.legend(loc='best')
                st.pyplot(fig)

                # ===== INTERPRETACIÓN =====
                st.markdown("---")
                st.markdown(t("turb_evaluation_header"))
                col_eval1, col_eval2 = st.columns(2)
                with col_eval1:
                    if H_design:
                        st.success(t("turb_eval_design").format(H_design, Q_design))
                    else:
                        st.warning(t("turb_warn_no_interpolation_design"))
                    
                    if H_normal:
                        st.info(t("turb_eval_normal").format(H_normal, Q_normal))
                    else:
                        st.warning(t("turb_warn_no_interpolation_normal"))
                with col_eval2:
                    if op_Q is not None and op_H is not None:
                        st.info(t("turb_eval_operation").format(op_Q, op_H))
                    else:
                        st.warning(t("turb_warn_no_intersection"))

            else:
                st.warning(t("turb_warn_valid_numeric_head"))

        except Exception as e:
            st.error(t("turb_error_processing_curve").format(str(e)))
    else:
        st.info(t("turb_info_min_two_points"))

    # ===== TABLA DETALLADA =====
    st.markdown("---")
    with st.expander(t("turb_all_params_expander")):
        param_dict = {
            t("turb_param_expansion_type"): t("turb_method_isentropic") if res['comp_type']=='isentropic' else t("turb_method_polytropic"),
            t("turb_param_R"): res['R'],
            t("turb_param_MW"): res['MW'],
            t("turb_param_Zavg"): res['Z_avg'],
            t("turb_param_k"): res['k'],
            t("turb_param_efficiency"): f"{res['eta']*100:.1f}",
            t("turb_param_n") if res['comp_type']=='polytropic' else t("turb_param_k"): res['n'] if res['comp_type']=='polytropic' else res['k'],
            t("turb_param_T1"): res['T1_C'],
            t("turb_param_P1"): res['P1'],
            t("turb_param_P2"): res['P2'],
            t("turb_param_expansion_ratio"): res['rp'],
            t("turb_param_Q_design"): res['Q_design'],
            t("turb_param_head_calc"): res['H_calc_Jkg'],
            t("turb_param_head_fluid_col"): res['H_calc_m'],
            t("turb_param_mass_flow"): res['mass_flow_kgs'],
            t("turb_param_power"): res['power_kW'],
            t("turb_param_T2_real"): res['T2_C'],
        }
        if res['comp_type'] == 'isentropic' and res['T2_ideal_C'] is not None:
            param_dict[t("turb_param_T2_ideal")] = res['T2_ideal_C']
        if 'H_design' in res and res['H_design'] is not None:
            param_dict[t("turb_param_head_design")] = res['H_design']
        if 'H_rated' in res and res['H_rated'] is not None:
            param_dict[t("turb_param_head_rated")] = res['H_rated']
        if 'H_normal' in res and res['H_normal'] is not None:
            param_dict[t("turb_param_head_normal")] = res['H_normal']
        if 'H_min' in res and res['H_min'] is not None:
            param_dict[t("turb_param_head_min")] = res['H_min']
        if 'P_design' in res and res['P_design'] is not None:
            param_dict[t("turb_param_power_design")] = res['P_design']
        if 'P_rated' in res and res['P_rated'] is not None:
            param_dict[t("turb_param_power_rated")] = res['P_rated']
        if 'P_normal' in res and res['P_normal'] is not None:
            param_dict[t("turb_param_power_normal")] = res['P_normal']
        if 'P_min' in res and res['P_min'] is not None:
            param_dict[t("turb_param_power_min")] = res['P_min']
        if 'eff_design' in res and res['eff_design'] is not None:
            param_dict[t("turb_param_eff_design")] = f"{res['eff_design']*100:.1f}"
        if 'eff_rated' in res and res['eff_rated'] is not None:
            param_dict[t("turb_param_eff_rated")] = f"{res['eff_rated']*100:.1f}"
        if 'eff_normal' in res and res['eff_normal'] is not None:
            param_dict[t("turb_param_eff_normal")] = f"{res['eff_normal']*100:.1f}"
        if 'eff_min' in res and res['eff_min'] is not None:
            param_dict[t("turb_param_eff_min")] = f"{res['eff_min']*100:.1f}"

        df_params = pd.DataFrame(list(param_dict.items()), columns=[t("turb_param_col_name"), t("turb_param_col_value")])
        st.dataframe(df_params, use_container_width=True, hide_index=True)

else:
    st.info(t("turb_initial_message"))

st.markdown("---")
st.caption(t("turb_footer"))