import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils.edp_1d import resolver_edp
from utils.i18n import language_selector
from languages.dif_par_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()

st.set_page_config(page_title="EDP 1D - Calor / Onda (Neumann)", layout="wide")
# st.title("🌊 Ecuaciones Diferenciales Parciales (1D)")
# st.markdown("Resuelve la **ecuación del Calor** o la **ecuación de Onda** con condiciones de frontera **Dirichlet o Neumann**.")
st.markdown("---")

# ============================================================
# INICIALIZACIÓN DEL ESTADO
# ============================================================
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'x_vals' not in st.session_state:
    st.session_state.x_vals = None
if 't_vals' not in st.session_state:
    st.session_state.t_vals = None
if 'u_vals' not in st.session_state:
    st.session_state.u_vals = None
if 'param' not in st.session_state:
    st.session_state.param = None
if 'condicion' not in st.session_state:
    st.session_state.condicion = None
if 'estable' not in st.session_state:
    st.session_state.estable = None
if 'nombre_metodo' not in st.session_state:
    st.session_state.nombre_metodo = None

# Variables para los ejes de la gráfica
if 'u_min' not in st.session_state:
    st.session_state.u_min = -1.5
if 'u_max' not in st.session_state:
    st.session_state.u_max = 1.5
if 'x_min' not in st.session_state:
    st.session_state.x_min = 0.0
if 'x_max' not in st.session_state:
    st.session_state.x_max = 1.0

# Variables de la malla (para usarlas en los sliders)
if 'Nx' not in st.session_state:
    st.session_state.Nx = 50
if 'Nt' not in st.session_state:
    st.session_state.Nt = 500
if 'L' not in st.session_state:
    st.session_state.L = 1.0

# Tipo de EDP (para mantener consistencia)
if 'tipo_edp' not in st.session_state:
    st.session_state.tipo_edp = "Calor (∂u/∂t = α ∂²u/∂x² + f)"

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
    page_icon="🌊",
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

with st.expander(t("profile_expander_title"), expanded=False):
    st.markdown(t("profile_expander_text"))

with st.expander(t("data_expander_title"), expanded=False):
    st.markdown(t("data_expander_text"))

with st.expander(t("stability_info_expander_title"), expanded=False):
    st.markdown(t("stability_info_expander_text"))

st.markdown("---")

# ============================================
# ASPECTOS NUMÉRICOS Y ESTABILIDAD
# ============================================
st.header(t("numerical_header"))

with st.expander(t("stability_expander_title"), expanded=False):
    st.markdown(t("stability_expander_text"))

with st.expander(t("discretization_expander_title"), expanded=False):
    st.markdown(t("discretization_expander_text"))

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
    st.subheader(t("pde_config_header"))
    
    tipo_edp = st.selectbox(
        t("pde_equation_type"),
        [t("pde_heat_option"), t("pde_wave_option")],
        key="tipo_edp"
    )
    
    st.subheader(t("pde_physical_params_header"))
    
    if t("pde_heat_keyword") in tipo_edp:
        alpha = st.number_input(t("pde_alpha"), value=1.0, min_value=0.01, format="%.3f", key="alpha")
        c = None
        metodo_heat = st.radio(
            t("pde_numerical_method"),
            [t("pde_explicit_ftcs"), t("pde_implicit_cn")],
            key="metodo_heat"
        )
    else:
        c = st.number_input(t("pde_wave_speed"), value=1.0, min_value=0.01, format="%.3f", key="c")
        alpha = None
        metodo_heat = t("pde_explicit_centered")
    
    L = st.number_input(t("pde_domain_length"), value=1.0, min_value=0.1, format="%.3f", key="L")
    T = st.number_input(t("pde_final_time"), value=0.5, min_value=0.01, format="%.3f", key="T")

with col2:
    st.subheader(t("pde_mesh_header"))
    col_a, col_b = st.columns(2)
    with col_a:
        Nx = st.number_input(t("pde_nx_points"), value=50, min_value=5, max_value=200, step=1, key="Nx")
    with col_b:
        Nt = st.number_input(t("pde_nt_steps"), value=500, min_value=10, max_value=2000, step=1, key="Nt")
    
    st.subheader(t("pde_initial_source_header"))
    
    u0_str = st.text_input(t("pde_u0_input"), value="sin(pi*x)", key="u0")
    f_str = st.text_input(t("pde_f_input"), value="0", key="f")
    
    if t("pde_wave_keyword") in tipo_edp:
        v0_str = st.text_input(t("pde_v0_input"), value="0", key="v0")
    else:
        v0_str = None

# Condiciones de frontera
st.subheader(t("pde_boundaries_header"))
col3, col4 = st.columns(2)
with col3:
    st.markdown(t("pde_left_boundary"))
    bc_left_type = st.selectbox(t("pde_boundary_type"), [t("pde_bc_dirichlet"), t("pde_bc_neumann")], key="left_type")
    if bc_left_type == t("pde_bc_dirichlet"):
        bc_left_val = st.number_input(t("pde_u_left"), value=0.0, format="%.3f", key="left_val")
    else:
        bc_left_val = st.number_input(t("pde_du_left"), value=0.0, format="%.3f", key="left_neumann")
with col4:
    st.markdown(t("pde_right_boundary"))
    bc_right_type = st.selectbox(t("pde_boundary_type"), [t("pde_bc_dirichlet"), t("pde_bc_neumann")], key="right_type")
    if bc_right_type == t("pde_bc_dirichlet"):
        bc_right_val = st.number_input(t("pde_u_right"), value=0.0, format="%.3f", key="right_val")
    else:
        bc_right_val = st.number_input(t("pde_du_right"), value=0.0, format="%.3f", key="right_neumann")

# Controles de ejes
st.subheader(t("pde_axes_header"))
col5, col6 = st.columns(2)
with col5:
    x_min = st.number_input(t("pde_x_min"), value=0.0, format="%.2f", key="xmin")
    u_min = st.number_input(t("pde_u_min"), value=-1.5, format="%.2f", key="umin")
with col6:
    x_max = st.number_input(t("pde_x_max"), value=L, format="%.2f", key="xmax")
    u_max = st.number_input(t("pde_u_max"), value=1.5, format="%.2f", key="umax")

# Botón de resolución
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    resolver = st.button(t("pde_solve_button"), type="primary", use_container_width=True)

# ============================================================
# LÓGICA PRINCIPAL
# ============================================================
if resolver:
    with st.spinner(t("pde_spinner")):
        x_vals, t_vals, u_vals, param, condicion, estable, nombre_metodo, error = resolver_edp(
            tipo_edp=tipo_edp,
            alpha=alpha,
            c=c,
            L=L,
            T=T,
            Nx=Nx,
            Nt=Nt,
            u0_str=u0_str,
            f_str=f_str,
            v0_str=v0_str,
            bc_left_type=bc_left_type,
            bc_left_val=bc_left_val,
            bc_right_type=bc_right_type,
            bc_right_val=bc_right_val,
            metodo_heat=metodo_heat
        )
    
    if error:
        st.error(t("pde_error_prefix").format(error))
        st.session_state.resultados = None
    else:
        st.session_state.resultados = True
        st.session_state.x_vals = x_vals
        st.session_state.t_vals = t_vals
        st.session_state.u_vals = u_vals
        st.session_state.param = param
        st.session_state.condicion = condicion
        st.session_state.estable = estable
        st.session_state.nombre_metodo = nombre_metodo
        
        if not estable:
            st.warning(t("pde_warning_stability").format(condicion))
        else:
            st.success(t("pde_success_stability").format(condicion))

# ============================================================
# MOSTRAR RESULTADOS (SI EXISTEN)
# ============================================================
if st.session_state.resultados:
    x_vals = st.session_state.x_vals
    t_vals = st.session_state.t_vals
    u_vals = st.session_state.u_vals
    condicion = st.session_state.condicion
    nombre_metodo = st.session_state.nombre_metodo
    u_min = st.session_state.u_min
    u_max = st.session_state.u_max
    x_min = st.session_state.x_min
    x_max = st.session_state.x_max
    Nx = st.session_state.Nx
    Nt = st.session_state.Nt
    L = st.session_state.L
    
    st.subheader(t("pde_solution_header").format(tipo_edp))
    
    # Superficie 3D
    fig_surf = go.Figure(data=[
        go.Surface(z=u_vals.T, x=x_vals, y=t_vals, colorscale='Viridis')
    ])
    fig_surf.update_layout(
        title=f"{nombre_metodo} | {condicion}",
        scene=dict(
            xaxis_title=t("pde_axis_x"),
            yaxis_title=t("pde_axis_t"),
            zaxis_title=t("pde_axis_u_xt"),
            xaxis=dict(range=[x_min, x_max]),
            zaxis=dict(range=[u_min, u_max]),
        ),
        height=600,
        template="plotly_white"
    )
    st.plotly_chart(fig_surf, use_container_width=True)
    
    # Perfil 2D con slider
    st.subheader(t("pde_time_slice_header"))
    t_index = st.slider(t("pde_time_index_slider"), 0, Nt-1, Nt//2, step=max(1, Nt//100))
    
    fig_2d = go.Figure()
    fig_2d.add_trace(go.Scatter(
        x=x_vals,
        y=u_vals[:, t_index],
        mode='lines+markers',
        name=t("pde_profile_trace").format(t_vals[t_index]),
        line=dict(color='firebrick', width=3),
        marker=dict(size=4)
    ))
    fig_2d.add_hline(y=0, line_width=1, line_dash="dash", opacity=0.5)
    fig_2d.add_vline(x=0, line_width=1, line_dash="dot", opacity=0.3)
    fig_2d.add_vline(x=L, line_width=1, line_dash="dot", opacity=0.3)
    
    fig_2d.update_layout(
        title=t("pde_profile_title").format(t_vals[t_index]),
        xaxis_title=t("pde_axis_x"),
        yaxis_title=t("pde_axis_u_x"),
        xaxis=dict(range=[x_min, x_max]),
        yaxis=dict(range=[u_min, u_max]),
        hovermode="x",
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig_2d, use_container_width=True)
    
    # Tabla de datos
    with st.expander(t("pde_data_expander")):
        step_t = max(1, Nt // 10)
        indices_t = list(range(0, Nt, step_t))
        data = {t("pde_data_col_x"): x_vals}
        for idx in indices_t:
            data[t("pde_data_col_t").format(t_vals[idx])] = u_vals[:, idx]
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=300)
    
    # Información adicional
    st.info(t("pde_stability_info").format(condicion))

else:
    st.info(t("pde_initial_message"))

# ============================================================
# FOOTER CON EJEMPLOS
# ============================================================
st.markdown("---")
st.caption(t("pde_footer_syntax"))

with st.expander(t("pde_examples_expander")):
    st.markdown(t("pde_examples_content"))

st.caption(t("pde_footer_methods"))