import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from utils.envolventes import (
    get_fluid_list, calcular_envolvente, preparar_datos_grafica,
    PropsSI
)
from utils.i18n import language_selector
from languages.envol_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()

# =============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =============================================================================
st.set_page_config(page_title="Envolvente Termodinámica - CoolProp", layout="wide")
# st.title("📊 Envolvente Termodinámica con Líneas Auxiliares")
# st.markdown("Selecciona un fluido y visualiza su envolvente de saturación con isobaras, isotermas y líneas de calidad.")
st.markdown("---")

# =============================================================================
# 2. INICIALIZACIÓN DEL ESTADO
# =============================================================================
if 'fluid' not in st.session_state:
    st.session_state.fluid = 'Water'
if 'plot_type' not in st.session_state:
    st.session_state.plot_type = 'Ts'
if 'op_point' not in st.session_state:
    st.session_state.op_point = {'T': 373.15, 'P': 101325}
if 'show_op_point' not in st.session_state:
    st.session_state.show_op_point = True
if 'show_isobars' not in st.session_state:
    st.session_state.show_isobars = True
if 'show_isotherms' not in st.session_state:
    st.session_state.show_isotherms = False
if 'show_quality' not in st.session_state:
    st.session_state.show_quality = True
if 'num_isobars' not in st.session_state:
    st.session_state.num_isobars = 5
if 'num_isotherms' not in st.session_state:
    st.session_state.num_isotherms = 5
if 'quality_vals' not in st.session_state:
    st.session_state.quality_vals = [0.1, 0.3, 0.5, 0.7, 0.9]
if 'T_min' not in st.session_state:
    st.session_state.T_min = 273.26
if 'T_max' not in st.session_state:
    st.session_state.T_max = 646.996
if 'resultados' not in st.session_state:
    st.session_state.resultados = None

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
    page_icon="📊",
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

with st.expander(t("graph_expander_title"), expanded=False):
    st.markdown(t("graph_expander_text"))

with st.expander(t("properties_expander_title"), expanded=False):
    st.markdown(t("properties_expander_text"))

with st.expander(t("saturation_expander_title"), expanded=False):
    st.markdown(t("saturation_expander_text"))

st.markdown("---")

# ============================================
# ALCANCE Y APLICABILIDAD
# ============================================
st.header(t("applications_header"))
st.markdown(t("applications_text"))

st.caption(t("caption"))

# =============================================================================
# 3. INTERFAZ DE USUARIO (SIN BARRA LATERAL)
# =============================================================================

# Organizar la entrada en columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader(t("thermo_fluid_config_header"))
    
    fluid_list = get_fluid_list()
    selected_fluid = st.selectbox(
        t("thermo_select_fluid"),
        fluid_list,
        index=fluid_list.index(st.session_state.fluid) if st.session_state.fluid in fluid_list else 0,
        key="fluid_selector"
    )
    if selected_fluid != st.session_state.fluid:
        st.session_state.fluid = selected_fluid
    
    plot_type = st.radio(
        t("thermo_diagram_type"),
        [t("thermo_diagram_ts"), t("thermo_diagram_ph")],
        index=0 if st.session_state.plot_type == 'Ts' else 1,
        key="plot_type_radio"
    )
    st.session_state.plot_type = 'Ts' if plot_type == t("thermo_diagram_ts") else 'Ph'

with col2:
    st.subheader(t("thermo_operation_point_header"))
    
    col_a, col_b = st.columns(2)
    with col_a:
        op_T = st.number_input(
            t("thermo_temperature_k"),
            value=float(st.session_state.op_point['T']),
            min_value=100.0,
            max_value=2000.0,
            step=0.1,
            format="%.2f",
            key="op_T"
        )
    with col_b:
        op_P = st.number_input(
            t("thermo_pressure_pa"),
            value=float(st.session_state.op_point['P']),
            min_value=100.0,
            max_value=1e8,
            step=1000.0,
            format="%.0f",
            key="op_P"
        )
    st.session_state.op_point = {'T': op_T, 'P': op_P}
    show_op = st.checkbox(t("thermo_show_operation_point"), value=st.session_state.show_op_point)
    st.session_state.show_op_point = show_op

# Líneas auxiliares
st.subheader(t("thermo_aux_lines_header"))
col3, col4, col5 = st.columns(3)

with col3:
    show_isobars = st.checkbox(t("thermo_show_isobars"), value=st.session_state.show_isobars)
    st.session_state.show_isobars = show_isobars
    if show_isobars:
        # Usar una clave diferente para evitar conflicto
        num_isobars = st.slider(
            t("thermo_num_isobars"), 
            1, 10, 
            st.session_state.num_isobars,
            key="num_isobars_slider"  # Clave diferente
        )
        st.session_state.num_isobars = num_isobars

with col4:
    show_isotherms = st.checkbox(t("thermo_show_isotherms"), value=st.session_state.show_isotherms)
    st.session_state.show_isotherms = show_isotherms
    if show_isotherms:
        num_isotherms = st.slider(
            t("thermo_num_isotherms"), 
            1, 10, 
            st.session_state.num_isotherms,
            key="num_isotherms_slider"  # Clave diferente
        )
        st.session_state.num_isotherms = num_isotherms

with col5:
    show_quality = st.checkbox(t("thermo_show_quality"), value=st.session_state.show_quality)
    st.session_state.show_quality = show_quality
    if show_quality:
        quality_vals = st.multiselect(
            t("thermo_quality_vals"),
            options=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            default=st.session_state.quality_vals,
            key="quality_vals_multiselect"  # Clave diferente
        )
        st.session_state.quality_vals = quality_vals

# Control de ejes
st.subheader(t("thermo_axes_header"))

def safe_float(value, decimals=4):
    """Redondea un float para evitar problemas de precisión."""
    return round(float(value), decimals)

try:
    T_crit = safe_float(PropsSI('Tcrit', st.session_state.fluid))
    T_triple = safe_float(PropsSI('Ttriple', st.session_state.fluid))
except:
    T_crit = 647.096
    T_triple = 273.16

# Asegurar que los valores de T_min y T_max estén dentro de los límites
min_t = safe_float(T_triple + 0.1)
max_t = safe_float(T_crit - 0.1)

col6, col7 = st.columns(2)
with col6:
    # Si el valor actual de T_min es menor que min_t, ajustarlo
    current_T_min = st.session_state.T_min
    if current_T_min < min_t:
        current_T_min = min_t
    
    # Usar una clave diferente para evitar conflicto con st.session_state.T_min
    T_min = st.number_input(
        t("thermo_t_min"),
        value=float(current_T_min),
        min_value=min_t,
        max_value=max_t,
        step=1.0,
        format="%.1f",
        key="T_min_input"  # Clave diferente
    )
    # Ahora podemos asignar manualmente sin conflicto
    st.session_state.T_min = T_min

with col7:
    # Si el valor actual de T_max es mayor que max_t, ajustarlo
    current_T_max = st.session_state.T_max
    if current_T_max > max_t:
        current_T_max = max_t
    if current_T_max < min_t + 10:  # Asegurar que T_max sea mayor que T_min
        current_T_max = min_t + 10
    
    T_max = st.number_input(
        t("thermo_t_max"),
        value=float(current_T_max),
        min_value=min_t + 1,
        max_value=float(T_crit + 100.0),
        step=1.0,
        format="%.1f",
        key="T_max_input"  # Clave diferente
    )
    st.session_state.T_max = T_max

# Validar que T_min < T_max
if T_min >= T_max:
    st.warning(t("thermo_warning_t_min_max"))
    T_max = T_min + 10
    st.session_state.T_max = T_max

# Botón de actualización
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    resolver = st.button(t("thermo_update_button"), type="primary", use_container_width=True)

# =============================================================================
# 4. LÓGICA PRINCIPAL Y GRÁFICAS
# =============================================================================

if resolver:
    with st.spinner(t("thermo_spinner")):
        sat_data, op_props, aux_lines, critical_point, error = calcular_envolvente(
            fluid=st.session_state.fluid,
            T_min=T_min,
            T_max=T_max,
            plot_type=st.session_state.plot_type,
            show_isobars=show_isobars,
            num_isobars=num_isobars if show_isobars else 0,
            show_isotherms=show_isotherms,
            num_isotherms=num_isotherms if show_isotherms else 0,
            show_quality=show_quality,
            quality_vals=quality_vals if show_quality else [],
            op_point=st.session_state.op_point if show_op else None,
            show_op_point=show_op
        )
        
        if error:
            st.error(t("thermo_error_prefix").format(error))
            st.session_state.resultados = None
        else:
            st.session_state.resultados = {
                'sat_data': sat_data,
                'op_props': op_props,
                'aux_lines': aux_lines,
                'critical_point': critical_point
            }
            st.success(t("thermo_success"))

# =============================================================================
# 5. MOSTRAR RESULTADOS
# =============================================================================

if st.session_state.resultados is not None:
    sat_data = st.session_state.resultados['sat_data']
    op_props = st.session_state.resultados['op_props']
    aux_lines = st.session_state.resultados['aux_lines']
    critical_point = st.session_state.resultados['critical_point']
    
    # Preparar datos para graficar
    datos_grafica = preparar_datos_grafica(
        sat_data, op_props, aux_lines, critical_point,
        st.session_state.fluid, st.session_state.plot_type
    )
    
    # Crear gráfica
    fig = go.Figure()
    
    # Envolvente
    fig.add_trace(go.Scatter(
        x=datos_grafica['x_liquid'],
        y=datos_grafica['y_vals'],
        mode='lines',
        name=t("thermo_trace_saturated_liquid"),
        line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=datos_grafica['x_vapor'],
        y=datos_grafica['y_vals'],
        mode='lines',
        name=t("thermo_trace_saturated_vapor"),
        line=dict(color='red', width=2)
    ))
    
    # Relleno de la envolvente
    x_envelope = np.concatenate([datos_grafica['x_liquid'], datos_grafica['x_vapor'][::-1]])
    y_envelope = np.concatenate([datos_grafica['y_vals'], datos_grafica['y_vals'][::-1]])
    fig.add_trace(go.Scatter(
        x=x_envelope,
        y=y_envelope,
        fill='toself',
        fillcolor='rgba(100, 150, 200, 0.15)',
        line=dict(width=0),
        name=t("thermo_trace_envelope"),
        showlegend=True
    ))
    
    # Punto crítico
    if datos_grafica['x_crit'] is not None:
        fig.add_trace(go.Scatter(
            x=[datos_grafica['x_crit']],
            y=[datos_grafica['y_crit']],
            mode='markers',
            marker=dict(size=12, color='black', symbol='star'),
            name=t("thermo_trace_critical_point")
        ))
    
    # Líneas auxiliares - Isobaras
    if st.session_state.plot_type == 'Ts':
        for isobar in aux_lines['isobars']:
            fig.add_trace(go.Scatter(
                x=isobar['s'] / 1000,
                y=isobar['T'],
                mode='lines',
                name=t("thermo_trace_isobar").format(isobar["P"]/1e5),
                line=dict(dash='dash', width=1, color='gray')
            ))
    
    # Líneas auxiliares - Isotermas
    if st.session_state.plot_type == 'Ph':
        for isotherm in aux_lines['isotherms']:
            fig.add_trace(go.Scatter(
                x=isotherm['h'] / 1000,
                y=isotherm['P'] / 1e5,
                mode='lines',
                name=t("thermo_trace_isotherm").format(isotherm["T"]),
                line=dict(dash='dot', width=1, color='orange')
            ))
    
    # Líneas auxiliares - Calidad
    if st.session_state.plot_type == 'Ts':
        for q_line in aux_lines['quality_lines']:
            fig.add_trace(go.Scatter(
                x=q_line['s'] / 1000,
                y=q_line['T'],
                mode='lines',
                name=t("thermo_trace_quality").format(q_line["q"]),
                line=dict(dash='dashdot', width=1.5, color='green')
            ))
    
    # Punto de operación
    if st.session_state.show_op_point and datos_grafica['op_x'] is not None:
        fig.add_trace(go.Scatter(
            x=[datos_grafica['op_x']],
            y=[datos_grafica['op_y']],
            mode='markers',
            marker=dict(size=14, color='red', symbol='x', line=dict(width=2, color='darkred')),
            name=t("thermo_trace_operation_point").format(op_props["T"], op_props["P"]/1e5)
        ))
        fig.add_hline(y=datos_grafica['op_y'], line_width=1, line_dash="dash", opacity=0.3)
        fig.add_vline(x=datos_grafica['op_x'], line_width=1, line_dash="dash", opacity=0.3)
    
    # Configuración del layout
    fig.update_layout(
        title=dict(text=datos_grafica['title'], font=dict(size=20)),
        xaxis_title=dict(text=datos_grafica['x_label'], font=dict(size=14)),
        yaxis_title=dict(text=datos_grafica['y_label'], font=dict(size=14)),
        hovermode='closest',
        template='plotly_white',
        height=700,
        width=None,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.8)'
        )
    )
    
    # Ajustar rangos
    x_min = min(np.nanmin(datos_grafica['x_liquid']), np.nanmin(datos_grafica['x_vapor']))
    x_max = max(np.nanmax(datos_grafica['x_liquid']), np.nanmax(datos_grafica['x_vapor']))
    x_margin = (x_max - x_min) * 0.05 if x_max > x_min else 1
    fig.update_xaxes(range=[x_min - x_margin, x_max + x_margin])
    
    y_min = min(datos_grafica['y_vals'])
    y_max = max(datos_grafica['y_vals'])
    y_margin = (y_max - y_min) * 0.05 if y_max > y_min else 1
    fig.update_yaxes(range=[y_min - y_margin, y_max + y_margin])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar propiedades del punto de operación
    if op_props:
        st.subheader(t("thermo_props_header"))
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t("thermo_metric_temperature"), f"{op_props['T']:.2f} K")
            st.metric(t("thermo_metric_pressure"), f"{op_props['P']/1e5:.3f} bar")
        with col2:
            st.metric(t("thermo_metric_density"), f"{op_props['D']:.3f} kg/m³")
            st.metric(t("thermo_metric_enthalpy"), f"{op_props['H']/1000:.3f} kJ/kg")
        with col3:
            st.metric(t("thermo_metric_entropy"), f"{op_props['S']/1000:.3f} kJ/kgK")
            st.metric(t("thermo_metric_internal_energy"), f"{op_props['U']/1000:.3f} kJ/kg")
        with col4:
            st.metric(t("thermo_metric_cp"), f"{op_props['Cp']/1000:.3f} kJ/kgK")
            st.metric(t("thermo_metric_viscosity"), f"{op_props['Visc']*1e6:.3f} μPa·s")
        
        if 0 <= op_props['Q'] <= 1:
            st.info(t("thermo_info_vapor_quality").format(op_props['Q']*100))
        elif op_props['Q'] < 0:
            st.info(t("thermo_info_subcooled_liquid"))
        elif op_props['Q'] > 1:
            st.info(t("thermo_info_superheated_vapor"))
    
    # Mostrar datos de la curva de saturación
    with st.expander(t("thermo_data_expander")):
        data = {
            t("thermo_data_col_t"): sat_data['T'],
            t("thermo_data_col_p"): sat_data['P_liquid'] / 1e5,
            t("thermo_data_col_s_liquid"): sat_data['s_liquid'] / 1000,
            t("thermo_data_col_s_vapor"): sat_data['s_vapor'] / 1000,
            t("thermo_data_col_h_liquid"): sat_data['h_liquid'] / 1000,
            t("thermo_data_col_h_vapor"): sat_data['h_vapor'] / 1000,
        }
        df = pd.DataFrame(data)
        st.dataframe(df.head(50), use_container_width=True)

else:
    st.info(t("thermo_initial_message"))

# =============================================================================
# 6. FOOTER CON AYUDA RÁPIDA
# =============================================================================
st.markdown("---")
st.caption(t("thermo_footer_aux_lines"))
st.caption(t("thermo_footer_isobars"))
st.caption(t("thermo_footer_isotherms"))
st.caption(t("thermo_footer_quality"))
st.caption(t("thermo_footer_instructions"))

st.caption(t("thermo_footer_fluids"))