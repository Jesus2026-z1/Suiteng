import streamlit as st
import numpy as np
import pandas as pd  
import plotly.graph_objects as go
from utils.runge_kutta import resolver_edo
from utils.i18n import language_selector
from languages.edos_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()

st.set_page_config(page_title="EDO con Runge-Kutta", layout="wide")
# st.title("🧮 Resolución de EDOs de Primer Orden (dy/dx = f(x,y))")
st.markdown("---")

# ============================================================
# INICIALIZACIÓN DEL ESTADO
# ============================================================
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'xs' not in st.session_state:
    st.session_state.xs = None
if 'ys' not in st.session_state:
    st.session_state.ys = None
if 'func_str' not in st.session_state:
    st.session_state.func_str = "x**2 + y"
if 'x0' not in st.session_state:
    st.session_state.x0 = 0.0
if 'y0' not in st.session_state:
    st.session_state.y0 = 1.0
if 'h' not in st.session_state:
    st.session_state.h = 0.1
if 'x_final' not in st.session_state:
    st.session_state.x_final = 5.0
if 'x_min' not in st.session_state:
    st.session_state.x_min = -1.0
if 'x_max' not in st.session_state:
    st.session_state.x_max = 6.0
if 'y_min' not in st.session_state:
    st.session_state.y_min = -5.0
if 'y_max' not in st.session_state:
    st.session_state.y_max = 10.0
if 'metodo' not in st.session_state:
    st.session_state.metodo = "rk4"

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
    page_icon="📐",
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

with st.expander(t("success_expander_title"), expanded=False):
    st.markdown(t("success_expander_text"))

with st.expander(t("plot_expander_title"), expanded=False):
    st.markdown(t("plot_expander_text"))

with st.expander(t("table_expander_title"), expanded=False):
    st.markdown(t("table_expander_text"))

st.markdown("---")

# ============================================
# ALCANCE Y APLICABILIDAD
# ============================================
st.header(t("scope_header"))
st.markdown(t("scope_text"))

st.caption(t("caption"))

st.header(t("config_header"))

# ============================================================
# INTERFAZ DE USUARIO (SIN BARRA LATERAL)
# ============================================================

# Organizar la entrada en columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader(t("ode_equation_header"))
    
    func_str = st.text_input(
        t("ode_function_input"),
        value=st.session_state.func_str,
        help=t("ode_function_help"),
        key="func_input"
    )
    
    st.subheader(t("ode_initial_conditions_header"))
    col_a, col_b = st.columns(2)
    with col_a:
        x0 = st.number_input(t("ode_x0_label"), value=st.session_state.x0, format="%.4f", key="x0_input")
    with col_b:
        y0 = st.number_input(t("ode_y0_label"), value=st.session_state.y0, format="%.4f", key="y0_input")

with col2:
    st.subheader(t("ode_numeric_params_header"))
    
    col_c, col_d = st.columns(2)
    with col_c:
        h = st.number_input(t("ode_step_label"), value=st.session_state.h, min_value=0.0001, format="%.4f", key="h_input")
    with col_d:
        x_final = st.number_input(t("ode_x_final_label"), value=st.session_state.x_final, format="%.4f", key="xf_input")
    
    st.subheader(t("ode_method_header"))
    metodo = st.selectbox(
        t("ode_select_method"),
        options=["rk4", "rk2", "rk1", "euler_implicito"],
        format_func=lambda x: {
            "rk4": t("ode_method_rk4"),
            "rk2": t("ode_method_rk2"),
            "rk1": t("ode_method_rk1"),
            "euler_implicito": t("ode_method_euler_implicit")
        }[x],
        index=0,
        key="metodo_input"
    )

# Controles de ejes
st.subheader(t("ode_axes_header"))
col_e, col_f = st.columns(2)
with col_e:
    x_min = st.number_input(t("ode_x_min"), value=st.session_state.x_min, format="%.2f", key="xmin_input")
    y_min = st.number_input(t("ode_y_min"), value=st.session_state.y_min, format="%.2f", key="ymin_input")
with col_f:
    x_max = st.number_input(t("ode_x_max"), value=st.session_state.x_max, format="%.2f", key="xmax_input")
    y_max = st.number_input(t("ode_y_max"), value=st.session_state.y_max, format="%.2f", key="ymax_input")

# Botón de resolución
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    resolver = st.button(t("ode_solve_button"), type="primary", use_container_width=True)

# ============================================================
# LÓGICA PRINCIPAL (AL PRESIONAR EL BOTÓN)
# ============================================================
if resolver:
    # Actualizar estado
    st.session_state.func_str = func_str
    st.session_state.x0 = x0
    st.session_state.y0 = y0
    st.session_state.h = h
    st.session_state.x_final = x_final
    st.session_state.x_min = x_min
    st.session_state.x_max = x_max
    st.session_state.y_min = y_min
    st.session_state.y_max = y_max
    st.session_state.metodo = metodo
    
    # Resolver la EDO
    with st.spinner(t("ode_spinner_solving")):
        xs, ys, error = resolver_edo(func_str, x0, y0, x_final, h, metodo)
    
    if error:
        st.error(t("ode_error_prefix").format(error))
        st.session_state.resultados = None
        st.session_state.xs = None
        st.session_state.ys = None
    else:
        st.session_state.resultados = True
        st.session_state.xs = xs
        st.session_state.ys = ys
        st.success(t("ode_success").format(len(xs)))

# ============================================================
# MOSTRAR RESULTADOS (SI EXISTEN)
# ============================================================
if st.session_state.resultados and st.session_state.xs is not None:
    xs = st.session_state.xs
    ys = st.session_state.ys
    func_str = st.session_state.func_str
    x0 = st.session_state.x0
    y0 = st.session_state.y0
    x_min = st.session_state.x_min
    x_max = st.session_state.x_max
    y_min = st.session_state.y_min
    y_max = st.session_state.y_max
    metodo = st.session_state.metodo
    h = st.session_state.h
    x_final = st.session_state.x_final
    
    # Crear gráfica con Plotly
    fig = go.Figure()
    
    # Línea de la solución
    fig.add_trace(go.Scatter(
        x=xs, 
        y=ys,
        mode='lines+markers',
        name=t("ode_trace_solution"),
        line=dict(color='royalblue', width=3),
        marker=dict(size=4, color='darkblue')
    ))
    
    # Punto inicial (destacado)
    fig.add_trace(go.Scatter(
        x=[x0], 
        y=[y0],
        mode='markers',
        name=t("ode_trace_initial").format(x0, y0),
        marker=dict(size=12, color='red', symbol='x')
    ))
    
    # Configuración de los ejes
    titulo_metodo = {
        "rk4": t("ode_method_rk4"),
        "rk2": t("ode_method_rk2"),
        "rk1": t("ode_method_rk1"),
        "euler_implicito": t("ode_method_euler_implicit")
    }[metodo]
    
    fig.update_layout(
        title=t("ode_title_solution").format(func_str, titulo_metodo),
        xaxis_title=t("ode_axis_x"),
        yaxis_title=t("ode_axis_y"),
        xaxis=dict(range=[x_min, x_max], autorange=False),
        yaxis=dict(range=[y_min, y_max], autorange=False),
        hovermode="x unified",
        template="plotly_white",
        height=600,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar tabla de datos (opcional)
    with st.expander(t("ode_expander_data")):
        # Mostrar solo los primeros 50 para no saturar
        display_n = min(50, len(xs))
        datos = np.column_stack((xs[:display_n], ys[:display_n]))
        df_datos = pd.DataFrame(datos, columns=[t("ode_col_x"), t("ode_col_y")])
        st.dataframe(df_datos, use_container_width=True)
    
    # Mostrar información adicional
    st.info(t("ode_info_summary").format(len(xs), h, x0, y0, x_final))

else:
    # Mensaje inicial
    st.info(t("ode_initial_message"))

# ============================================================
# FOOTER CON INFORMACIÓN
# ============================================================
st.markdown("---")
st.caption(t("ode_footer_syntax"))