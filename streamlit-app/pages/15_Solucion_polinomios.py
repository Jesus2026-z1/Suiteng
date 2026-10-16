import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from utils.solucion_ecuaciones import (
    resolver_univariable, resolver_multivariable,
    metodos_univariables_disponibles, metodos_multivariables_disponibles
)
from utils.i18n import language_selector
from languages.sol_pol_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar() 

st.set_page_config(page_title="Raíces de Ecuaciones", layout="wide")
# st.title("🔍 Resolución de Ecuaciones y Sistemas")
# st.markdown("Selecciona el método y define la ecuación o sistema.")
st.markdown("---")

# ============================================================
# INICIALIZACIÓN DEL ESTADO
# ============================================================
if 'tipo' not in st.session_state:
    st.session_state.tipo = "Ecuación univariable"
if 'func_str' not in st.session_state:
    st.session_state.func_str = "x**3 - x - 2"
if 'metodo_univ' not in st.session_state:
    st.session_state.metodo_univ = "Bisección"
if 'a' not in st.session_state:
    st.session_state.a = 1.0
if 'b' not in st.session_state:
    st.session_state.b = 2.0
if 'x0' not in st.session_state:
    st.session_state.x0 = 1.5
if 'tol' not in st.session_state:
    st.session_state.tol = 1e-6
if 'max_iter' not in st.session_state:
    st.session_state.max_iter = 100
if 'n_vars' not in st.session_state:
    st.session_state.n_vars = 2
if 'func_strs' not in st.session_state:
    st.session_state.func_strs = ["x1**2 + x2 - 1", "x1 - x2**2 - 1"]
if 'x0_vals' not in st.session_state:
    st.session_state.x0_vals = [0.5, 0.5]
if 'metodo_mult' not in st.session_state:
    st.session_state.metodo_mult = "Newton-Raphson (Jacobiano)"
if 'resultado' not in st.session_state:
    st.session_state.resultado = None

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
    page_icon="🧮",
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

st.subheader(t("univariate_subheader"))
st.markdown(t("univariate_text"))

st.subheader(t("multivariate_subheader"))
st.markdown(t("multivariate_text"))

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

with st.expander(t("solution_expander_title"), expanded=False):
    st.markdown(t("solution_expander_text"))

with st.expander(t("iterations_expander_title"), expanded=False):
    st.markdown(t("iterations_expander_text"))

with st.expander(t("plots_expander_title"), expanded=False):
    st.markdown(t("plots_expander_text"))

st.markdown("---")

# ============================================
# ASPECTOS NUMÉRICOS Y CONVERGENCIA
# ============================================
st.header(t("numerical_header"))

with st.expander(t("method_choice_expander_title"), expanded=False):
    st.markdown(t("method_choice_expander_text"))

with st.expander(t("divergence_expander_title"), expanded=False):
    st.markdown(t("divergence_expander_text"))

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

# Tipo de problema
tipo = st.radio(
    t("root_problem_type"),
    [t("root_type_univariate"), t("root_type_multivariate")],
    horizontal=True,
    key="tipo_radio"
)

st.markdown("---")

if tipo == t("root_type_univariate"):
    # Configuración para ecuación univariable
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(t("root_equation_header"))
        func_str = st.text_input(t("root_function_input"), value=st.session_state.func_str, key="func_str_input")
        
        metodo_univ = st.selectbox(
            t("root_method"),
            metodos_univariables_disponibles(),
            index=0,
            key="metodo_univ_input"
        )
    
    with col2:
        st.subheader(t("root_params_header"))
        
        if metodo_univ == t("root_method_bisection"):
            col_a, col_b = st.columns(2)
            with col_a:
                a = st.number_input(t("root_interval_a"), value=st.session_state.a, format="%.4f", key="a_input")
            with col_b:
                b = st.number_input(t("root_interval_b"), value=st.session_state.b, format="%.4f", key="b_input")
            x0 = None
        elif metodo_univ == t("root_method_secant"):
            col_a, col_b = st.columns(2)
            with col_a:
                x0 = st.number_input(t("root_x0_initial"), value=st.session_state.x0, format="%.4f", key="x0_input")
            with col_b:
                b = st.number_input(t("root_x1_initial"), value=st.session_state.b, format="%.4f", key="b_secante")
            a = None
        else:  # Newton-Raphson
            x0 = st.number_input(t("root_x0_value"), value=st.session_state.x0, format="%.4f", key="x0_input")
            a = None
            b = None
        
        col_tol, col_iter = st.columns(2)
        with col_tol:
            tol = st.number_input(t("root_tolerance"), value=st.session_state.tol, format="%.1e", key="tol_input")
        with col_iter:
            max_iter = st.number_input(t("root_max_iter"), value=st.session_state.max_iter, step=10, key="max_iter_input")
    
    # Botón de resolución
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        resolver = st.button(t("root_solve_button"), type="primary", use_container_width=True)
    
    # Resultados
    if resolver:
        with st.spinner(t("root_spinner_solving")):
            raiz, iteraciones, converg, error = resolver_univariable(
                func_str, metodo_univ, a, b, x0, tol, max_iter
            )
        
        if error:
            st.error(t("root_error_prefix").format(error))
        elif raiz is None:
            st.error(t("root_error_no_convergence"))
        else:
            st.session_state.resultado = {
                'raiz': raiz,
                'iteraciones': iteraciones,
                'converg': converg,
                'func_str': func_str,
                'metodo': metodo_univ,
                'a': a,
                'b': b,
                'x0': x0,
                'tol': tol,
                'max_iter': max_iter
            }
    
    # Mostrar resultados
    if st.session_state.resultado and st.session_state.resultado.get('raiz') is not None:
        res = st.session_state.resultado
        raiz = res['raiz']
        iteraciones = res['iteraciones']
        converg = res['converg']
        func_str = res['func_str']
        metodo = res['metodo']
        
        st.success(t("root_success_root").format(raiz))
        
        col_met1, col_met2 = st.columns(2)
        with col_met1:
            st.metric(t("root_metric_iterations"), len(iteraciones))
        with col_met2:
            st.metric(t("root_metric_convergence"), t("root_yes") if converg else t("root_no_max_iter"))
        
        # Graficar
        if metodo == t("root_method_bisection") and res['a'] is not None and res['b'] is not None:
            x_vals = np.linspace(res['a']-1, res['b']+1, 500)
        elif res['x0'] is not None:
            x_vals = np.linspace(raiz-2, raiz+2, 500)
        else:
            x_vals = np.linspace(-3, 3, 500)
        
        # Evaluar la función para graficar
        try:
            from sympy import sympify, lambdify, symbols
            x_sym = symbols('x')
            f_num = lambdify(x_sym, sympify(func_str), modules=['numpy'])
            y_vals = f_num(x_vals)
        except:
            y_vals = np.zeros_like(x_vals)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name=t("root_trace_fx"), line=dict(color='royalblue', width=2)))
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.add_vline(x=raiz, line_dash="dot", line_color="red")
        fig.add_trace(go.Scatter(x=[raiz], y=[0], mode='markers', marker=dict(color='red', size=12), name=t("root_trace_root")))
        fig.update_layout(
            title=t("root_title_root").format(func_str),
            xaxis_title=t("root_axis_x"),
            yaxis_title=t("root_axis_fx"),
            height=500,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de iteraciones
        with st.expander(t("root_iterations_expander")):
            if metodo == t("root_method_bisection"):
                df_iter = pd.DataFrame(iteraciones, columns=[t("root_iter_col"), t("root_iter_col_a"), t("root_iter_col_b"), t("root_iter_col_c"), t("root_iter_col_fc")])
            elif metodo == t("root_method_secant"):
                df_iter = pd.DataFrame(iteraciones, columns=[t("root_iter_col"), t("root_iter_col_x_prev"), t("root_iter_col_x_curr"), t("root_iter_col_x_new"), t("root_iter_col_fx_new")])
            else:
                df_iter = pd.DataFrame(iteraciones, columns=[t("root_iter_col"), t("root_iter_col_x"), t("root_iter_col_fx"), t("root_iter_col_x_new")])
            st.dataframe(df_iter, use_container_width=True)

else:  # Sistema multivariable
    st.subheader(t("root_system_config_header"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        n = st.number_input(
            t("root_num_equations"),
            min_value=2, max_value=5, value=st.session_state.n_vars, step=1,
            key="n_vars_input"
        )
        n = int(n)
        
        # Funciones F_i
        st.markdown(t("root_functions_header"))
        func_strs = []
        for i in range(1, n+1):
            default = st.session_state.func_strs[i-1] if i-1 < len(st.session_state.func_strs) else "0"
            f_str = st.text_input(
                t("root_function_f_label").format(i=i),
                value=default,
                key=f"F{i}_input"
            )
            func_strs.append(f_str)
        
        metodo_mult = st.selectbox(
            t("root_method"),
            metodos_multivariables_disponibles(),
            index=0,
            key="metodo_mult_input"
        )
    
    with col2:
        st.markdown(t("root_initial_conditions_header"))
        x0_vals = []
        for i in range(1, n+1):
            default = st.session_state.x0_vals[i-1] if i-1 < len(st.session_state.x0_vals) else 0.5
            x0_i = st.number_input(
                t("root_initial_xi_label").format(i=i),
                value=default,
                format="%.4f",
                key=f"x0{i}_input"
            )
            x0_vals.append(x0_i)
        
        col_tol, col_iter = st.columns(2)
        with col_tol:
            tol = st.number_input(t("root_tolerance"), value=st.session_state.tol, format="%.1e", key="tol_mult_input")
        with col_iter:
            max_iter = st.number_input(t("root_max_iter"), value=st.session_state.max_iter, step=10, key="max_iter_mult_input")
    
    # Botón de resolución
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        resolver = st.button(t("root_solve_system_button"), type="primary", use_container_width=True)
    
    # Resultados
    if resolver:
        with st.spinner(t("root_spinner_solving_system")):
            sol, iteraciones, converg, error = resolver_multivariable(
                func_strs, n, metodo_mult, x0_vals, tol, max_iter
            )
        
        if error:
            st.error(t("root_error_prefix").format(error))
        elif sol is None:
            st.error(t("root_error_no_convergence"))
        else:
            st.success(t("root_success_system"))
            
            cols = st.columns(min(n, 4))
            for i, (col, val) in enumerate(zip(cols, sol), start=1):
                with col:
                    st.metric(t("root_metric_xi").format(i), f"{val:.8f}")
            
            col_met1, col_met2 = st.columns(2)
            with col_met1:
                st.metric(t("root_metric_iterations"), len(iteraciones))
            with col_met2:
                st.metric(t("root_metric_convergence"), t("root_yes") if converg else t("root_no_max_iter"))
            
            # Graficar solo para 2 variables
            if n == 2:
                try:
                    x1_vals = np.linspace(sol[0]-2, sol[0]+2, 50)
                    x2_vals = np.linspace(sol[1]-2, sol[1]+2, 50)
                    X1, X2 = np.meshgrid(x1_vals, x2_vals)
                    Z1 = np.zeros_like(X1)
                    Z2 = np.zeros_like(X1)
                    
                    # Parsear funciones para graficar
                    from sympy import sympify, lambdify, symbols
                    vars_sym = symbols([f'x{i}' for i in range(1, n+1)])
                    F1 = lambdify(vars_sym, sympify(func_strs[0]), modules=['numpy'])
                    F2 = lambdify(vars_sym, sympify(func_strs[1]), modules=['numpy'])
                    
                    for i in range(X1.shape[0]):
                        for j in range(X1.shape[1]):
                            try:
                                Z1[i,j] = F1(X1[i,j], X2[i,j])
                                Z2[i,j] = F2(X1[i,j], X2[i,j])
                            except:
                                Z1[i,j] = np.nan
                                Z2[i,j] = np.nan
                    
                    fig = go.Figure()
                    fig.add_trace(go.Contour(
                        x=x1_vals, y=x2_vals, z=Z1,
                        contours=dict(showlabels=True),
                        name=t("root_contour_f1"),
                        colorscale='Blues'
                    ))
                    fig.add_trace(go.Contour(
                        x=x1_vals, y=x2_vals, z=Z2,
                        contours=dict(showlabels=True),
                        name=t("root_contour_f2"),
                        colorscale='Reds'
                    ))
                    fig.add_trace(go.Scatter(
                        x=[sol[0]], y=[sol[1]],
                        mode='markers',
                        marker=dict(color='green', size=14, symbol='x'),
                        name=t("root_trace_solution")
                    ))
                    fig.update_layout(
                        title=t("root_contour_title"),
                        xaxis_title=t("root_axis_x1"),
                        yaxis_title=t("root_axis_x2"),
                        height=500,
                        template="plotly_white"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(t("root_warning_no_plot").format(e))
            
            # Tabla de iteraciones
            with st.expander(t("root_iterations_expander")):
                if metodo_mult == t("root_method_newton_jacobian"):
                    cols = [t("root_iter_col")] + [t("root_iter_col_xi").format(i) for i in range(1,n+1)] + [t("root_iter_col_fi").format(i) for i in range(1,n+1)] + [t("root_iter_col_dx_norm")]
                    data = []
                    for it, x, Fx, dx in iteraciones:
                        row = [it] + list(x) + list(Fx) + [np.linalg.norm(dx)]
                        data.append(row)
                else:
                    cols = [t("root_iter_col")] + [t("root_iter_col_xi").format(i) for i in range(1,n+1)] + [t("root_iter_col_xi_new").format(i) for i in range(1,n+1)]
                    data = []
                    for it, x, x_new in iteraciones:
                        row = [it] + list(x) + list(x_new)
                        data.append(row)
                df_iter = pd.DataFrame(data, columns=cols)
                st.dataframe(df_iter, use_container_width=True)

# ============================================================
# FOOTER CON EJEMPLOS
# ============================================================
st.markdown("---")
st.caption(t("root_footer_syntax"))

with st.expander(t("root_examples_expander")):
    st.markdown(t("root_examples_content"))

st.caption(t("root_footer_methods"))