import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from utils.integracion_numerica import integrar
from utils.i18n import language_selector
from languages.int_num_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()

st.set_page_config(page_title=t("page_title"), layout="wide")
# st.title("📐 Integración Numérica Avanzada")
st.markdown("---")

# ============================================================
# INICIALIZACIÓN DEL ESTADO
# ============================================================
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'integral' not in st.session_state:
    st.session_state.integral = None
if 'integral_exacta' not in st.session_state:
    st.session_state.integral_exacta = None
if 'x_vals' not in st.session_state:
    st.session_state.x_vals = None
if 'y_vals' not in st.session_state:
    st.session_state.y_vals = None
if 'n_efectivo' not in st.session_state:
    st.session_state.n_efectivo = None
if 'func_str' not in st.session_state:
    st.session_state.func_str = "x**2"
if 'a' not in st.session_state:
    st.session_state.a = 0.0
if 'b' not in st.session_state:
    st.session_state.b = 2.0
if 'n' not in st.session_state:
    st.session_state.n = 10
if 'metodo' not in st.session_state:
    st.session_state.metodo = "simpson"
if 'x_min' not in st.session_state:
    st.session_state.x_min = -0.5
if 'x_max' not in st.session_state:
    st.session_state.x_max = 2.5
if 'y_min' not in st.session_state:
    st.session_state.y_min = -1.0
if 'y_max' not in st.session_state:
    st.session_state.y_max = 6.0

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
    page_title="Integración Numérica Avanzada - Descripción",
    page_icon="∫",
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
# VARIABLES DE ENTRADA
# ============================================
st.header(t("inputs_header"))
st.markdown(t("inputs_text"))

st.markdown("---")

# ============================================
# RESULTADOS OBTENIDOS
# ============================================
st.header(t("results_header"))

with st.expander(t("results_expander_title"), expanded=False):
    st.markdown(t("results_expander_text"))

with st.expander(t("points_expander_title"), expanded=False):
    st.markdown(t("points_expander_text"))

with st.expander(t("visualization_expander_title"), expanded=False):
    st.markdown(t("visualization_expander_text"))

st.markdown("---")

# ============================================
# ASPECTOS TÉCNICOS Y SINTAXIS
# ============================================
st.header(t("syntax_header"))

with st.expander(t("syntax_expander_title"), expanded=False):
    st.markdown(t("syntax_expander_text"))

with st.expander(t("methods_expander_title"), expanded=False):
    st.markdown(t("methods_expander_text"))

st.markdown("---")

# ============================================
# ALCANCE Y APLICABILIDAD
# ============================================
st.header(t("applications_header"))
st.markdown(t("applications_text"))

st.caption(t("caption"))

st.header(t("config_header"))

# ============================================================
# INTERFAZ DE USUARIO (SIN BARRA LATERAL)
# ============================================================

# Organizar la entrada en columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader(t("int_function_header"))
    
    func_str = st.text_input(
        t("int_function_input"),
        value=st.session_state.func_str,
        help=t("int_function_help"),
        key="func_input"
    )
    
    st.subheader(t("int_limits_header"))
    col_a, col_b = st.columns(2)
    with col_a:
        a = st.number_input(t("int_lower_limit"), value=st.session_state.a, format="%.4f", key="a_input")
    with col_b:
        b = st.number_input(t("int_upper_limit"), value=st.session_state.b, format="%.4f", key="b_input")

with col2:
    st.subheader(t("int_numeric_params_header"))
    
    metodo = st.selectbox(
        t("int_method_label"),
        options=["simpson", "trapecio", "simpson_38", "gauss_2", "gauss_3", "gauss_4", 
                 "gauss_5", "gauss_6", "gauss_7", "gauss_8", "gauss_9", "gauss_10"],
        format_func=lambda x: {
            "simpson": t("int_method_simpson"),
            "trapecio": t("int_method_trapezoid"),
            "simpson_38": t("int_method_simpson_38"),
            "gauss_2": t("int_method_gauss_2"),
            "gauss_3": t("int_method_gauss_3"),
            "gauss_4": t("int_method_gauss_4"),
            "gauss_5": t("int_method_gauss_5"),
            "gauss_6": t("int_method_gauss_6"),
            "gauss_7": t("int_method_gauss_7"),
            "gauss_8": t("int_method_gauss_8"),
            "gauss_9": t("int_method_gauss_9"),
            "gauss_10": t("int_method_gauss_10")
        }[x],
        index=0,
        key="metodo_input"
    )
    
    # Para métodos que requieren n
    if not metodo.startswith('gauss_'):
        n = st.number_input(
            t("int_num_subintervals"),
            min_value=2,
            max_value=1000,
            value=st.session_state.n,
            step=1,
            help=t("int_num_subintervals_help"),
            key="n_input"
        )
        n = int(n)
    else:
        # Para Gauss, n se fija automáticamente
        n = int(metodo.split('_')[1])
        st.info(t("int_gauss_points_info").format(n))

# Controles de ejes
st.subheader(t("int_axes_header"))
col_e, col_f = st.columns(2)
with col_e:
    # Calcular rangos predeterminados basados en los límites
    default_x_min = a - 0.5
    default_x_max = b + 0.5
    x_min = st.number_input(t("int_x_min"), value=st.session_state.x_min, format="%.2f", key="xmin_input")
    x_max = st.number_input(t("int_x_max"), value=st.session_state.x_max, format="%.2f", key="xmax_input")
with col_f:
    y_min = st.number_input(t("int_y_min"), value=st.session_state.y_min, format="%.2f", key="ymin_input")
    y_max = st.number_input(t("int_y_max"), value=st.session_state.y_max, format="%.2f", key="ymax_input")

# Botón de cálculo
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    calcular = st.button(t("int_calculate_button"), type="primary", use_container_width=True)

# ============================================================
# LÓGICA PRINCIPAL (AL PRESIONAR EL BOTÓN)
# ============================================================
if calcular:
    # Validar límites
    if a >= b:
        st.error(t("int_error_limits"))
        st.stop()
    
    # Actualizar estado
    st.session_state.func_str = func_str
    st.session_state.a = a
    st.session_state.b = b
    st.session_state.n = n
    st.session_state.metodo = metodo
    st.session_state.x_min = x_min
    st.session_state.x_max = x_max
    st.session_state.y_min = y_min
    st.session_state.y_max = y_max
    
    # Realizar la integración
    with st.spinner(t("int_spinner_calculating")):
        integral, integral_exacta, x_vals, y_vals, error, n_efectivo = integrar(
            func_str, a, b, n, metodo
        )
    
    if error:
        st.error(t("int_error_prefix").format(error))
        st.session_state.resultados = False
    else:
        st.session_state.resultados = True
        st.session_state.integral = integral
        st.session_state.integral_exacta = integral_exacta
        st.session_state.x_vals = x_vals
        st.session_state.y_vals = y_vals
        st.session_state.n_efectivo = n_efectivo
        st.success(t("int_success"))

# ============================================================
# MOSTRAR RESULTADOS (SI EXISTEN)
# ============================================================
if st.session_state.resultados:
    integral = st.session_state.integral
    integral_exacta = st.session_state.integral_exacta
    x_vals = st.session_state.x_vals
    y_vals = st.session_state.y_vals
    n_efectivo = st.session_state.n_efectivo
    func_str = st.session_state.func_str
    a = st.session_state.a
    b = st.session_state.b
    metodo = st.session_state.metodo
    x_min = st.session_state.x_min
    x_max = st.session_state.x_max
    y_min = st.session_state.y_min
    y_max = st.session_state.y_max
    
    # Mostrar métricas
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric(t("int_metric_approx"), f"{integral:.8f}")
    
    if integral_exacta is not None:
        error_abs = abs(integral_exacta - integral)
        with col_res2:
            st.metric(t("int_metric_exact"), f"{integral_exacta:.8f}")
        with col_res3:
            st.metric(t("int_metric_abs_error"), f"{error_abs:.2e}")
    else:
        with col_res2:
            st.metric(t("int_metric_subintervals"), f"{n_efectivo}")
        with col_res3:
            st.metric(t("int_metric_method"), {
                "simpson": t("int_method_short_simpson"),
                "trapecio": t("int_method_short_trapezoid"),
                "simpson_38": t("int_method_short_simpson_38"),
                "gauss_2": t("int_method_short_gauss_2"),
                "gauss_3": t("int_method_short_gauss_3"),
                "gauss_4": t("int_method_short_gauss_4"),
                "gauss_5": t("int_method_short_gauss_5"),
                "gauss_6": t("int_method_short_gauss_6"),
                "gauss_7": t("int_method_short_gauss_7"),
                "gauss_8": t("int_method_short_gauss_8"),
                "gauss_9": t("int_method_short_gauss_9"),
                "gauss_10": t("int_method_short_gauss_10")
            }[metodo])
    
    # Graficar
    fig = go.Figure()
    
    # Área sombreada (solo para métodos que generan puntos en el intervalo)
    if not metodo.startswith('gauss_'):
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=np.zeros_like(x_vals),
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='lines',
            name=t("int_trace_function").format(func_str),
            fill='tonexty',
            fillcolor='rgba(0, 100, 200, 0.3)',
            line=dict(color='royalblue', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='markers',
            name=t("int_trace_points").format(n_efectivo),
            marker=dict(size=5, color='darkred', symbol='circle')
        ))
    else:
        # Para Gauss, graficamos la curva y los puntos de integración
        # La función integrar ya devuelve x_vals como puntos de la curva
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='lines',
            name=t("int_trace_function").format(func_str),
            line=dict(color='royalblue', width=3)
        ))
        
        # Puntos de Gauss
        # Necesitamos evaluar la función en los puntos de Gauss
        # Para simplificar, mostramos la curva sin marcadores de puntos
        # ya que Gauss usa puntos específicos
    
    # Configuración de los ejes
    fig.update_layout(
        title=t("int_title_integral").format(func_str, a, b, integral),
        xaxis_title=t("int_axis_x"),
        yaxis_title=t("int_axis_fx"),
        xaxis=dict(range=[x_min, x_max], autorange=False),
        yaxis=dict(range=[y_min, y_max], autorange=False),
        hovermode="x unified",
        template="plotly_white",
        height=600,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de datos
    with st.expander(t("int_expander_points")):
        if not metodo.startswith('gauss_'):
            step_display = max(1, len(x_vals) // 50)
            indices = slice(0, len(x_vals), step_display)
            datos = np.column_stack((x_vals[indices], y_vals[indices]))
            df_datos = pd.DataFrame(datos, columns=[t("int_col_x"), t("int_col_fx")])
            st.dataframe(df_datos, use_container_width=True, height=300)
        else:
            st.info(t("int_info_gauss_points"))

else:
    st.info(t("int_initial_message"))

# ============================================================
# FOOTER CON INFORMACIÓN
# ============================================================
st.markdown("---")
st.caption(t("int_footer_syntax"))
st.caption(t("int_footer_methods"))