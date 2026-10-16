import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from utils.sistema_edos import resolver_sistema, get_metodos_disponibles
from utils.i18n import language_selector
from languages.sis_edos_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()

st.set_page_config(page_title="Sistema EDO con RK4", layout="wide")
# st.title("🧩 Sistemas de EDOs de Primer Orden (Runge‑Kutta)")
st.markdown("---")

# ============================================================
# INICIALIZACIÓN DEL ESTADO
# ============================================================
if 'num_eqs' not in st.session_state:
    st.session_state.num_eqs = 2
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 't_vals' not in st.session_state:
    st.session_state.t_vals = None
if 'y_vals' not in st.session_state:
    st.session_state.y_vals = None
if 't0' not in st.session_state:
    st.session_state.t0 = 0.0
if 't_final' not in st.session_state:
    st.session_state.t_final = 10.0
if 'h' not in st.session_state:
    st.session_state.h = 0.1
if 'metodo' not in st.session_state:
    st.session_state.metodo = 'rk4'
if 'func_strs' not in st.session_state:
    st.session_state.func_strs = ["y1 + y2", "y1 - y2"]
if 'y0_vals' not in st.session_state:
    st.session_state.y0_vals = [1.0, 0.0]
if 't_min' not in st.session_state:
    st.session_state.t_min = -1.0
if 't_max' not in st.session_state:
    st.session_state.t_max = 11.0
if 'y_min' not in st.session_state:
    st.session_state.y_min = -5.0
if 'y_max' not in st.session_state:
    st.session_state.y_max = 5.0

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

with st.expander(t("plot_expander_title"), expanded=False):
    st.markdown(t("plot_expander_text"))

with st.expander(t("axes_expander_title"), expanded=False):
    st.markdown(t("axes_expander_text"))

st.markdown("---")

# ============================================
# SINTAXIS Y NOTAS TÉCNICAS
# ============================================
st.header(t("syntax_header"))
st.markdown(t("syntax_text"))

st.markdown("---")

# ============================================
# ALCANCE Y APLICABILIDAD
# ============================================
st.header(t("applications_header"))
st.markdown(t("applications_text"))

st.caption(t("caption"))

# ============================================================
# INTERFAZ DE USUARIO (SIN BARRA LATERAL)
# ============================================================

# Organizar la entrada en columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader(t("sys_config_header"))
    
    num_eqs = st.number_input(
        t("sys_num_equations"),
        min_value=1, max_value=10,
        value=st.session_state.num_eqs, step=1,
        key="num_eqs_input"
    )
    if num_eqs != st.session_state.num_eqs:
        st.session_state.num_eqs = num_eqs
        # Reiniciar las funciones y condiciones iniciales
        st.session_state.func_strs = [f"y1 + y2" if i == 0 else f"y1 - y2" if i == 1 else "0" 
                                      for i in range(num_eqs)]
        st.session_state.y0_vals = [1.0 if i == 0 else 0.0 for i in range(num_eqs)]
        st.rerun()
    
    st.subheader(t("sys_functions_header"))
    
    func_strs = []
    for i in range(1, num_eqs + 1):
        default = st.session_state.func_strs[i-1] if i-1 < len(st.session_state.func_strs) else "0"
        f_str = st.text_input(
            t("sys_function_label").format(i=i, num_eqs=num_eqs),
            value=default,
            key=f"func_{i}"
        )
        func_strs.append(f_str)

with col2:
    st.subheader(t("sys_initial_conditions_header"))
    
    t0 = st.number_input(t("sys_t0_label"), value=st.session_state.t0, format="%.4f", key="t0_input")
    
    y0_vals = []
    for i in range(1, num_eqs + 1):
        default = st.session_state.y0_vals[i-1] if i-1 < len(st.session_state.y0_vals) else 0.0
        y0_i = st.number_input(
            t("sys_y0_label").format(i=i),
            value=default,
            format="%.4f",
            key=f"y0_{i}"
        )
        y0_vals.append(y0_i)
    
    st.subheader(t("sys_numeric_params_header"))
    col_a, col_b = st.columns(2)
    with col_a:
        t_final = st.number_input(t("sys_t_final"), value=st.session_state.t_final, format="%.4f", key="tf_input")
    with col_b:
        h = st.number_input(t("sys_step"), value=st.session_state.h, min_value=0.001, format="%.4f", key="h_input")
    
    # Método de integración
    metodos = get_metodos_disponibles()
    metodo = st.selectbox(
        t("sys_method"),
        options=list(metodos.keys()),
        format_func=lambda x: metodos[x],
        index=0,
        key="metodo_input"
    )

# Controles de ejes
st.subheader(t("sys_axes_header"))
col_e, col_f = st.columns(2)
with col_e:
    t_min = st.number_input(t("sys_t_min"), value=st.session_state.t_min, format="%.2f", key="tmin_input")
    y_min = st.number_input(t("sys_y_min"), value=st.session_state.y_min, format="%.2f", key="ymin_input")
with col_f:
    t_max = st.number_input(t("sys_t_max"), value=st.session_state.t_max, format="%.2f", key="tmax_input")
    y_max = st.number_input(t("sys_y_max"), value=st.session_state.y_max, format="%.2f", key="ymax_input")

# Botón de resolución
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    resolver = st.button(t("sys_solve_button"), type="primary", use_container_width=True)

# ============================================================
# LÓGICA DE RESOLUCIÓN
# ============================================================
if resolver:
    # Actualizar estado
    st.session_state.num_eqs = num_eqs
    st.session_state.func_strs = func_strs
    st.session_state.y0_vals = y0_vals
    st.session_state.t0 = t0
    st.session_state.t_final = t_final
    st.session_state.h = h
    st.session_state.metodo = metodo
    st.session_state.t_min = t_min
    st.session_state.t_max = t_max
    st.session_state.y_min = y_min
    st.session_state.y_max = y_max
    
    # Resolver el sistema
    with st.spinner(t("sys_spinner")):
        t_vals, y_vals, error = resolver_sistema(
            func_strs, num_eqs, t0, y0_vals, t_final, h, metodo
        )
    
    if error:
        st.error(t("sys_error_prefix").format(error))
        st.session_state.resultados = None
        st.session_state.t_vals = None
        st.session_state.y_vals = None
    else:
        st.session_state.resultados = True
        st.session_state.t_vals = t_vals
        st.session_state.y_vals = y_vals
        st.success(t("sys_success").format(len(t_vals)))

# ============================================================
# MOSTRAR RESULTADOS (SI EXISTEN)
# ============================================================
if st.session_state.resultados and st.session_state.t_vals is not None:
    t_vals = st.session_state.t_vals
    y_vals = st.session_state.y_vals
    num_eqs = st.session_state.num_eqs
    t_final = st.session_state.t_final
    t_min = st.session_state.t_min
    t_max = st.session_state.t_max
    y_min = st.session_state.y_min
    y_max = st.session_state.y_max
    metodo = st.session_state.metodo
    
    # Métricas finales
    cols = st.columns(min(num_eqs, 4))
    for i, col in enumerate(cols):
        with col:
            st.metric(t("sys_metric_final").format(i+1, t_final), f"{y_vals[-1, i]:.6f}")
    
    # --- Gráfica ---
    fig = go.Figure()
    colors = ['royalblue', 'firebrick', 'forestgreen', 'darkorange',
              'purple', 'crimson', 'teal', 'goldenrod', 'pink', 'navy']
    
    metodos_nombres = get_metodos_disponibles()
    
    for i in range(num_eqs):
        fig.add_trace(go.Scatter(
            x=t_vals,
            y=y_vals[:, i],
            mode='lines',
            name=t("sys_trace_label").format(i+1),
            line=dict(color=colors[i % len(colors)], width=2)
        ))
    
    fig.update_layout(
        title=t("sys_title_system").format(num_eqs, metodos_nombres[metodo]),
        xaxis_title=t("sys_axis_t"),
        yaxis_title=t("sys_axis_vars"),
        xaxis=dict(range=[t_min, t_max], autorange=False),
        yaxis=dict(range=[y_min, y_max], autorange=False),
        hovermode="x unified",
        template="plotly_white",
        height=600,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # --- Tabla de datos ---
    with st.expander(t("sys_expander_data")):
        data = {t("sys_col_t"): t_vals}
        for i in range(num_eqs):
            data[t("sys_col_y").format(i+1)] = y_vals[:, i]
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=300)

else:
    st.info(t("sys_initial_message"))

# ============================================================
# FOOTER CON INFORMACIÓN Y AYUDA RÁPIDA
# ============================================================
st.markdown("---")
st.caption(t("sys_footer_syntax"))

# Expandable con ejemplos
with st.expander(t("sys_examples_expander")):
    st.markdown(t("sys_examples_content"))

st.caption(t("sys_footer_methods"))