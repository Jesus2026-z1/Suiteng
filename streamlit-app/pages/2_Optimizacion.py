import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog, minimize
import sympy as sp
import re
import matplotlib.pyplot as plt
from utils.i18n import language_selector
from languages.optim_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar() 

# ============================================================================
# FUNCIONES DE NORMALIZACION Y PARSEO
# ============================================================================

def normalizar_expresion(expr):
    """
    Normaliza una expresion matematica para que sea parseable por sympy.
    Inserta asteriscos donde faltan y reemplaza ^ por **.
    
    Ejemplos:
        "2x1 + x2"       -> "2*x1 + x2"
        "x1x2"           -> "x1*x2"
        "2(x1+x2)"       -> "2*(x1+x2)"
        "(x1+x2)3"       -> "(x1+x2)*3"
        "x1^2 + 3x2"     -> "x1**2 + 3*x2"
    """
    if not expr or not expr.strip():
        return expr
    
    # Reemplazar ^ por **
    expr = expr.replace('^', '**')
    
    # Eliminar espacios para facilitar el regex
    expr = expr.replace(' ', '')
    
    # 1. Numero seguido de letra/parentesis: 2x1 -> 2*x1, 2( -> 2*(
    expr = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expr)
    
    # 2. Letra/numero seguido de parentesis abierto: x1( -> x1*(, 3( -> 3*(
    expr = re.sub(r'([a-zA-Z0-9])\(', r'\1*(', expr)
    
    # 3. Parentesis cerrado seguido de letra/numero/parentesis: )x1 -> )*x1, )3 -> )*3, )( -> )*(
    expr = re.sub(r'\)([a-zA-Z0-9(])', r')*\1', expr)
    
    # 4. Variable seguida de numero (caso especial): x12 no debe tocarse si es variable x12
    #    Pero x1 2 debe ser x1*2 (ya cubierto por espacios eliminados)
    
    return expr

def parsear_expresion(expresion_str, variables):
    """
    Parsea una expresion matematica en string y la convierte en funcion ejecutable.
    Retorna: (funcion_lambda, expresion_sympy)
    """
    try:
        # Normalizar la expresion
        expr_limpia = normalizar_expresion(expresion_str)
        
        if not expr_limpia or not expr_limpia.strip():
            raise ValueError("La expresion esta vacia")
        
        # Crear simbolos de sympy
        simbolos = {v: sp.Symbol(v) for v in variables}
        
        # Parsear con sympy
        expr_sympy = sp.sympify(expr_limpia, locals=simbolos)
        
        # Convertir a funcion lambda
        func_args = [simbolos[v] for v in variables]
        func_lambda = sp.lambdify(func_args, expr_sympy, modules=['numpy'])
        
        return func_lambda, expr_sympy
    except Exception as e:
        raise ValueError(
            "Error al parsear '{}'. "
            "Sintaxis sugerida: usa '*' para multiplicar (ej: '2*x1' en vez de '2x1'). "
            "Detalles: {}".format(expresion_str, str(e))
        )

def extraer_coeficientes_lineales(expresion_str, variables):
    """
    Extrae coeficientes de una expresion lineal.
    Ejemplo: "2*x1 + 3*x2 - 5" con variables ["x1", "x2"] retorna [2, 3, -5]
    """
    try:
        # Normalizar la expresion
        expr_limpia = normalizar_expresion(expresion_str)
        
        if not expr_limpia or not expr_limpia.strip():
            raise ValueError("La expresion esta vacia")
        
        simbolos = {v: sp.Symbol(v) for v in variables}
        expr_sympy = sp.sympify(expr_limpia, locals=simbolos)
        
        # Expandir para separar terminos
        expr_expandida = sp.expand(expr_sympy)
        
        coeficientes = []
        for var in variables:
            coef = expr_expandida.coeff(simbolos[var])
            coeficientes.append(float(coef))
        
        # Termino independiente
        termino_indep = expr_expandida.subs({simbolos[v]: 0 for v in variables})
        coeficientes.append(float(termino_indep))
        
        return coeficientes
    except Exception as e:
        raise ValueError(
            "Error al extraer coeficientes de '{}'. "
            "Asegurate de usar '*' para multiplicar (ej: '2*x1' en vez de '2x1'). "
            "Detalles: {}".format(expresion_str, str(e))
        )

def es_lineal(expresion_str, variables):
    """
    Verifica si una expresion es lineal (todas las variables tienen potencia 1
    y no hay productos entre variables).
    """
    try:
        expr_limpia = normalizar_expresion(expresion_str)
        simbolos = {v: sp.Symbol(v) for v in variables}
        expr_sympy = sp.sympify(expr_limpia, locals=simbolos)
        expr_expandida = sp.expand(expr_sympy)
        
        # Verificar cada termino
        terminos = sp.Add.make_args(expr_expandida)
        for termino in terminos:
            for var in variables:
                potencia = sp.degree(termino, simbolos[var])
                if potencia > 1:
                    return False
            # Verificar productos entre variables
            if len([v for v in variables if termino.has(simbolos[v])]) > 1:
                return False
        return True
    except:
        return False

# ============================================================================
# FUNCIONES DE OPTIMIZACION
# ============================================================================

def optimizacion_simplex(c, A_ub, b_ub, A_eq, b_eq, bounds, maximizar=True):
    """
    Resuelve problema de programacion lineal usando metodo Simplex.
    """
    try:
        # linprog minimiza por defecto, si queremos maximizar, negamos c
        c_opt = -np.array(c) if maximizar else np.array(c)
        
        resultado = linprog(
            c_opt,
            A_ub=A_ub if len(A_ub) > 0 else None,
            b_ub=b_ub if len(b_ub) > 0 else None,
            A_eq=A_eq if len(A_eq) > 0 else None,
            b_eq=b_eq if len(b_eq) > 0 else None,
            bounds=bounds,
            method='highs'
        )
        
        if resultado.success:
            valor_optimo = -resultado.fun if maximizar else resultado.fun
            return {
                'exito': True,
                'valor_optimo': valor_optimo,
                'variables': resultado.x,
                'mensaje': resultado.message,
                'iteraciones': resultado.nit if hasattr(resultado, 'nit') else 0
            }
        else:
            return {
                'exito': False,
                'mensaje': resultado.message,
                'valor_optimo': None,
                'variables': None
            }
    except Exception as e:
        return {
            'exito': False,
            'mensaje': str(e),
            'valor_optimo': None,
            'variables': None
        }

def optimizacion_no_lineal(func_obj, restricciones, x0, bounds, metodo='SLSQP', maximizar=True):
    """
    Resuelve problema de optimizacion no lineal.
    """
    try:
        # Si queremos maximizar, negamos la funcion
        if maximizar:
            func_opt = lambda x: -func_obj(*x)
        else:
            func_opt = func_obj
        
        # Preparar restricciones para scipy
        scipy_constraints = []
        for res in restricciones:
            if res['tipo'] == '<=':
                scipy_constraints.append({
                    'type': 'ineq',
                    'fun': lambda x, r=res: r['b'] - r['func'](*x)
                })
            elif res['tipo'] == '>=':
                scipy_constraints.append({
                    'type': 'ineq',
                    'fun': lambda x, r=res: r['func'](*x) - r['b']
                })
            elif res['tipo'] == '==':
                scipy_constraints.append({
                    'type': 'eq',
                    'fun': lambda x, r=res: r['func'](*x) - r['b']
                })
        
        resultado = minimize(
            func_opt,
            x0,
            method=metodo,
            bounds=bounds,
            constraints=scipy_constraints if len(scipy_constraints) > 0 else (),
            options={'maxiter': 1000, 'disp': False}
        )
        
        if resultado.success or resultado.fun < 1e10:
            valor_optimo = -resultado.fun if maximizar else resultado.fun
            return {
                'exito': True,
                'valor_optimo': valor_optimo,
                'variables': resultado.x,
                'mensaje': resultado.message,
                'iteraciones': resultado.nit,
                'convergencia': resultado.success
            }
        else:
            return {
                'exito': False,
                'mensaje': resultado.message,
                'valor_optimo': None,
                'variables': None
            }
    except Exception as e:
        return {
            'exito': False,
            'mensaje': str(e),
            'valor_optimo': None,
            'variables': None
        }

# ============================================================================
# INTERFAZ DE STREAMLIT
# ============================================================================

st.set_page_config(page_title="Optimizacion - Simplex y No Lineal", layout="wide")

# st.markdown("<h1 style='color:#2E8B57; text-align: center'>Análisis de Optimización</h1>", unsafe_allow_html=True)
# st.title("Analisis de Optimizacion", text_alignment='center')
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

import streamlit as st

st.set_page_config(
    page_title=t("page_title"),
    page_icon="📈",
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
# RESULTADOS Y APLICABILIDAD
# ============================================
st.header(t("results_header"))

with st.expander(t("supported_types_expander"), expanded=False):
    st.markdown(t("supported_types_text"))

with st.expander(t("visualization_expander"), expanded=False):
    st.markdown(t("visualization_text"))

st.markdown("---")

# ============================================
# ALCANCE Y APLICABILIDAD
# ============================================
st.header(t("utility_header"))
st.markdown(t("utility_text"))

st.caption(t("caption"))

# Sidebar - Configuracion
st.header(t("config_header"))

# Metodo de optimizacion
metodo_opt = st.selectbox(
    tw("method_label"),
    [t("method_options_1"), t("method_options_2")]
)

# Tipo de optimizacion
tipo_opt = st.radio(
    t("type_label"),
    ["Maximizar", "Minimizar", "Igualar a Cero"]
)

# ============================================================================
# CONFIGURACION DE VARIABLES
# ============================================================================

st.header(t("opt_var_def_header"))

num_variables = st.number_input(
    t("opt_num_decision_vars"),
    min_value=1, max_value=10, value=2,
    key="num_vars"
)

# Crear nombres de variables
nombres_vars = []
for i in range(num_variables):
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write(t("opt_variable_label").format(i+1))
    with col2:
        nombre = st.text_input(
            t("opt_name_label"),
            value="x{}".format(i+1),
            key="var_name_{}".format(i),
            label_visibility="collapsed"
        )
        nombres_vars.append(nombre)

st.markdown("---")

# ============================================================================
# FUNCION OBJETIVO
# ============================================================================

st.header(t("opt_objective_header"))

st.write(t("opt_objective_instruction").format(", ".join(nombres_vars)))

# Sugerencias de sintaxis
with st.expander(t("opt_syntax_examples_expander")):
    st.write("""
    **Sintaxis aceptada (se normaliza automaticamente):**
    - `2x1 + 3x2` o `2*x1 + 3*x2` (ambas funcionan)
    - `x1^2 + x2^2` o `x1**2 + x2**2`
    - `2(x1 + x2)` o `2*(x1 + x2)`
    - `sin(x1) + cos(x2)`
    - `x1*x2 + 3*x1`
    
    **Funciones disponibles:**
    - Trig: `sin()`, `cos()`, `tan()`, `asin()`, `acos()`, `atan()`
    - Exp/Log: `exp()`, `log()`, `sqrt()`
    - Otras: `abs()`, `pi`, `e`
    """)

funcion_objetivo_str = st.text_area(
    t("opt_objective_header"),
    value="2*x1 + 3*x2" if num_variables == 2 else " + ".join(["x{}".format(i+1) for i in range(num_variables)]),
    height=100,
    key="func_obj"
)

# Mostrar la expresion normalizada
if funcion_objetivo_str:
    expr_normalizada = normalizar_expresion(funcion_objetivo_str)
    if expr_normalizada != funcion_objetivo_str.replace(' ', ''):
        st.info(t("opt_normalized_expression").format(expr_normalizada))

st.markdown("---")

# ============================================================================
# RESTRICCIONES
# ============================================================================

st.header(t("opt_constraints_header"))

num_restricciones = st.number_input(
    t("opt_num_constraints"),
    min_value=0, max_value=20, value=2,
    key="num_rest"
)

restricciones_input = []

for i in range(num_restricciones):
    st.write(t("opt_constraint_label").format(i+1))
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        expr = st.text_input(
            t("opt_expression_label"),
            value="x1 + x2" if num_variables >= 2 else "x1",
            key="rest_expr_{}".format(i),
            label_visibility="collapsed"
        )
    
    with col2:
        tipo = st.selectbox(
            t("opt_type_label"),
            ["<=", ">=", "=="],
            key="rest_tipo_{}".format(i),
            label_visibility="collapsed"
        )
    
    with col3:
        valor = st.number_input(
            t("opt_value_label"),
            value=10.0,
            key="rest_valor_{}".format(i),
            label_visibility="collapsed"
        )
    
    restricciones_input.append({
        'expresion': expr,
        'tipo': tipo,
        'valor': valor
    })

st.markdown("---")

# ============================================================================
# LIMITES DE VARIABLES
# ============================================================================

st.header(t("opt_bounds_header"))

st.write(t("opt_bounds_instruction"))

bounds = []
for i, var in enumerate(nombres_vars):
    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        st.write("**{}:**".format(var))
    with col2:
        lower = st.number_input(
            t("opt_min_label"),
            value=0.0,
            key="bound_lower_{}".format(i),
            label_visibility="collapsed"
        )
    with col3:
        upper = st.number_input(
            t("opt_max_label"),
            value=100.0,
            key="bound_upper_{}".format(i),
            label_visibility="collapsed"
        )
    bounds.append((lower, upper))

st.markdown("---")

# ============================================================================
# CONFIGURACION ADICIONAL PARA NO LINEAL
# ============================================================================

if metodo_opt == t("opt_nonlinear"):
    st.header(t("opt_nonlinear_config_header"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        metodo_numerico = st.selectbox(
            t("opt_optimization_algorithm"),
            ["SLSQP", "BFGS", "Nelder-Mead", "Powell", "CG"],
            key="metodo_num"
        )
    
    with col2:
        st.write(t("opt_initial_point"))
        x0 = []
        for i in range(num_variables):
            val = st.number_input(
                nombres_vars[i],
                value=1.0,
                key="x0_{}".format(i),
                label_visibility="collapsed"
            )
            x0.append(val)

st.markdown("---")

# ============================================================================
# EJECUCION DE OPTIMIZACION
# ============================================================================

if st.button(t("opt_run_optimization_button"), type="primary"):
    try:
        # Validar funcion objetivo
        if not funcion_objetivo_str or not funcion_objetivo_str.strip():
            st.error(t("opt_error_empty_objective"))
            st.stop()
        
        # Parsear funcion objetivo
        func_obj, expr_sympy = parsear_expresion(funcion_objetivo_str, nombres_vars)
        
        # Determinar si es maximizar
        maximizar = (tipo_opt == t("opt_maximize"))
        igualar_cero = (tipo_opt == t("opt_equal_to_zero"))
        
        # =====================================================================
        # CASO SIMPLEX (LINEAL)
        # =====================================================================
        if metodo_opt == t("opt_simplex_linear"):
            st.header(t("opt_results_simplex_header"))
            
            # Validar que sea lineal
            if not es_lineal(funcion_objetivo_str, nombres_vars):
                st.error(t("opt_error_objective_not_linear"))
                st.stop()
            
            for res in restricciones_input:
                if not es_lineal(res['expresion'], nombres_vars):
                    st.error(t("opt_error_constraint_not_linear").format(res['expresion']))
                    st.stop()
            
            # Extraer coeficientes de la funcion objetivo
            c = extraer_coeficientes_lineales(funcion_objetivo_str, nombres_vars)
            c_coef = c[:-1]
            c_indep = c[-1]
            
            # Parsear restricciones
            A_ub = []
            b_ub = []
            A_eq = []
            b_eq = []
            
            for res in restricciones_input:
                coef_res = extraer_coeficientes_lineales(res['expresion'], nombres_vars)
                coef_vars = coef_res[:-1]
                termino_ind = coef_res[-1]
                
                lado_der = res['valor'] - termino_ind
                
                if res['tipo'] == '<=':
                    A_ub.append(coef_vars)
                    b_ub.append(lado_der)
                elif res['tipo'] == '>=':
                    A_ub.append([-c for c in coef_vars])
                    b_ub.append(-lado_der)
                elif res['tipo'] == '==':
                    A_eq.append(coef_vars)
                    b_eq.append(lado_der)
            
            A_ub = np.array(A_ub) if len(A_ub) > 0 else np.array([])
            b_ub = np.array(b_ub) if len(b_ub) > 0 else np.array([])
            A_eq = np.array(A_eq) if len(A_eq) > 0 else np.array([])
            b_eq = np.array(b_eq) if len(b_eq) > 0 else np.array([])
            
            # Ejecutar optimizacion
            resultado = optimizacion_simplex(
                c_coef, A_ub, b_ub, A_eq, b_eq, bounds, maximizar
            )
            
            # Mostrar resultados
            if resultado['exito']:
                st.success(t("opt_success_optimization"))
                
                col1, col2, col3 = st.columns(3)
                col1.metric(t("opt_optimal_value"), "{:.4f}".format(resultado['valor_optimo'] + c_indep))
                col2.metric(t("opt_iterations"), resultado['iteraciones'])
                col3.metric(t("opt_status"), t("opt_convergence"))
                
                st.markdown("---")
                
                st.subheader(t("opt_optimized_variables_header"))
                for i, var in enumerate(nombres_vars):
                    st.write("**{}:** {:.6f}".format(var, resultado['variables'][i]))
                
                st.markdown("---")
                
                st.subheader(t("opt_constraint_verification_header"))
                for i, res in enumerate(restricciones_input):
                    valor_calc = sum(c_coef[j] * resultado['variables'][j] for j in range(num_variables))
                    cumple = False
                    if res['tipo'] == '<=':
                        cumple = valor_calc <= res['valor'] + 1e-6
                    elif res['tipo'] == '>=':
                        cumple = valor_calc >= res['valor'] - 1e-6
                    elif res['tipo'] == '==':
                        cumple = abs(valor_calc - res['valor']) < 1e-6
                    
                    estado = t("opt_complies") if cumple else t("opt_does_not_comply")
                    st.write(t("opt_constraint_check_format").format(
                        i+1, res['expresion'], res['tipo'], res['valor'], valor_calc, estado
                    ))
                
                # Visualizacion para 2 variables
                if num_variables == 2:
                    st.markdown("---")
                    st.subheader(t("opt_visualization_feasible_regions"))
                    
                    x1_range = np.linspace(bounds[0][0], bounds[0][1], 200)
                    x2_range = np.linspace(bounds[1][0], bounds[1][1], 200)
                    X1, X2 = np.meshgrid(x1_range, x2_range)
                    
                    # Crear mascara de region factible
                    factible = np.ones_like(X1, dtype=bool)
                    
                    for res in restricciones_input:
                        coef_res = extraer_coeficientes_lineales(res['expresion'], nombres_vars)
                        valor_calc = coef_res[0] * X1 + coef_res[1] * X2 + coef_res[2]
                        
                        if res['tipo'] == '<=':
                            factible &= (valor_calc <= res['valor'] + 1e-6)
                        elif res['tipo'] == '>=':
                            factible &= (valor_calc >= res['valor'] - 1e-6)
                        elif res['tipo'] == '==':
                            factible &= (np.abs(valor_calc - res['valor']) < 1e-3)
                    
                    # Funcion objetivo para colores
                    Z = c_coef[0] * X1 + c_coef[1] * X2 + c_indep
                    
                    fig, ax = plt.subplots(figsize=(10, 8))
                    
                    # Dibujar region factible
                    Z_plot = np.where(factible, Z, np.nan)
                    contour = ax.contourf(X1, X2, Z_plot, levels=30, cmap='viridis', alpha=0.7)
                    plt.colorbar(contour, ax=ax, label=t("opt_objective_header"))
                    
                    # Dibujar lineas de restriccion
                    for i, res in enumerate(restricciones_input):
                        coef_res = extraer_coeficientes_lineales(res['expresion'], nombres_vars)
                        if abs(coef_res[1]) > 1e-10:
                            x2_line = (res['valor'] - coef_res[2] - coef_res[0] * x1_range) / coef_res[1]
                            mask = (x2_line >= bounds[1][0]) & (x2_line <= bounds[1][1])
                            ax.plot(x1_range[mask], x2_line[mask], 'r-', linewidth=2, 
                                   label=t("opt_restriction_label").format(i+1))
                        elif abs(coef_res[0]) > 1e-10:
                            x1_line = (res['valor'] - coef_res[2]) / coef_res[0]
                            mask = (x1_line >= bounds[0][0]) & (x1_line <= bounds[0][1])
                            ax.axvline(x1_line, color='red', linestyle='-', linewidth=2,
                                      label=t("opt_restriction_label").format(i+1))
                    
                    # Marcar punto optimo
                    ax.plot(resultado['variables'][0], resultado['variables'][1], 
                           'r*', markersize=20, label=t("opt_optimum_label").format(resultado['valor_optimo'] + c_indep))
                    
                    ax.set_xlabel(nombres_vars[0])
                    ax.set_ylabel(nombres_vars[1])
                    ax.set_title(t("opt_feasible_region_and_optimal_solution"))
                    ax.legend(loc='best')
                    ax.set_xlim(bounds[0])
                    ax.set_ylim(bounds[1])
                    
                    st.pyplot(fig)
            else:
                st.error(t("opt_error_optimization").format(resultado['mensaje']))
        
        # =====================================================================
        # CASO NO LINEAL
        # =====================================================================
        else:
            st.header(t("opt_results_nonlinear_header"))
            
            # Parsear restricciones
            restricciones_parseadas = []
            for res in restricciones_input:
                func_res, _ = parsear_expresion(res['expresion'], nombres_vars)
                restricciones_parseadas.append({
                    'func': func_res,
                    'tipo': res['tipo'],
                    'b': res['valor']
                })
            
            # Ejecutar optimizacion
            resultado = optimizacion_no_lineal(
                func_obj, restricciones_parseadas, np.array(x0), 
                bounds, metodo_numerico, maximizar
            )
            
            # Mostrar resultados
            if resultado['exito']:
                st.success(t("opt_success_optimization"))
                
                col1, col2, col3 = st.columns(3)
                col1.metric(t("opt_optimal_value"), "{:.6f}".format(resultado['valor_optimo']))
                col2.metric(t("opt_iterations"), resultado['iteraciones'])
                col3.metric(t("opt_convergence"), t("opt_yes") if resultado['convergencia'] else t("opt_no"))
                
                st.markdown("---")
                
                st.subheader(t("opt_optimized_variables_header"))
                for i, var in enumerate(nombres_vars):
                    st.write("**{}:** {:.6f}".format(var, resultado['variables'][i]))
                
                st.markdown("---")
                
                st.subheader(t("opt_constraint_verification_header"))
                for i, res in enumerate(restricciones_input):
                    func_res, _ = parsear_expresion(res['expresion'], nombres_vars)
                    valor_calc = func_res(*resultado['variables'])
                    
                    cumple = False
                    if res['tipo'] == '<=':
                        cumple = valor_calc <= res['valor'] + 1e-6
                    elif res['tipo'] == '>=':
                        cumple = valor_calc >= res['valor'] - 1e-6
                    elif res['tipo'] == '==':
                        cumple = abs(valor_calc - res['valor']) < 1e-6
                    
                    estado = t("opt_complies") if cumple else t("opt_does_not_comply")
                    st.write(t("opt_constraint_check_format").format(
                        i+1, res['expresion'], res['tipo'], res['valor'], valor_calc, estado
                    ))
                
                # Visualizacion para 2 variables
                if num_variables == 2:
                    st.markdown("---")
                    st.subheader(t("opt_visualization_objective_contour"))
                    
                    x1_range = np.linspace(bounds[0][0], bounds[0][1], 100)
                    x2_range = np.linspace(bounds[1][0], bounds[1][1], 100)
                    X1, X2 = np.meshgrid(x1_range, x2_range)
                    
                    Z = np.zeros_like(X1)
                    for i in range(X1.shape[0]):
                        for j in range(X1.shape[1]):
                            try:
                                Z[i, j] = func_obj(X1[i, j], X2[i, j])
                            except:
                                Z[i, j] = np.nan
                    
                    fig, ax = plt.subplots(figsize=(10, 8))
                    contour = ax.contourf(X1, X2, Z, levels=50, cmap='viridis')
                    plt.colorbar(contour, ax=ax)
                    
                    # Marcar punto optimo
                    ax.plot(resultado['variables'][0], resultado['variables'][1], 
                           'r*', markersize=20, label=t("opt_optimal_value"))
                    
                    ax.set_xlabel(nombres_vars[0])
                    ax.set_ylabel(nombres_vars[1])
                    ax.set_title(t("opt_contour_map_title").format(resultado['valor_optimo']))
                    ax.legend()
                    
                    st.pyplot(fig)
            else:
                st.error(t("opt_error_optimization").format(resultado['mensaje']))
    
    except Exception as e:
        st.error(t("opt_error_general").format(str(e)))

else:
    st.info(t("opt_info_configure_problem"))

# ============================================================================
# INFORMACION ADICIONAL
# ============================================================================

st.markdown("---")
with st.expander(t("opt_info_examples_expander")):
    st.write("""
    **Sintaxis de la Funcion Objetivo y Restricciones:**
    
    - La normalizacion es automatica, puedes escribir:
      - `2x1 + 3x2` o `2*x1 + 3*x2` (ambas funcionan)
      - `x1^2` o `x1**2`
      - `2(x1+x2)` o `2*(x1+x2)`
    
    - Operadores basicos: `+`, `-`, `*`, `/`, `**` (potencia) o `^`
    - Funciones matematicas: `sin()`, `cos()`, `tan()`, `exp()`, `log()`, `sqrt()`
    
    **Metodo Simplex:**
    - Solo funciona con funciones objetivo y restricciones LINEALES
    - El sistema detecta automaticamente si tu problema es lineal
    - Si no es lineal, te sugiere usar el metodo No Lineal
    
    **Metodo No Lineal:**
    - Funciona con cualquier funcion continua y diferenciable
    - Requiere un punto inicial (x0)
    - Puede converger a optimos locales (no siempre globales)
    - Prueba diferentes algoritmos si no converge
    
    **Tipos de Optimizacion:**
    - Maximizar: encuentra el valor maximo
    - Minimizar: encuentra el valor minimo
    - Igualar a Cero: encuentra raices (solo no lineal)
    """)