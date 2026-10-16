"""
============================================================
SISTEMA DE INTERNACIONALIZACIÓN (i18n) ES / EN
Módulo centralizado para todas las páginas Streamlit.
============================================================
"""
import streamlit as st

# ============================================================
# DICCIONARIO DE TRADUCCIONES
# ============================================================
TRANSLATIONS = {
    "es": {
        # ========== Compartidas (todas las páginas) ==========
        "common_lang_selector":   " Idioma / Language",
        "common_run":             "🚀 Ejecutar",
        "common_calc":            "🔍 Calcular",
        "common_select":          "Seleccionar",
        "common_delete":          "Eliminar",
        "common_components_sel":  "Componentes seleccionados:",
        "common_no_components":   "Sin componentes seleccionados.",
        "common_model_config":    "⚙️ Configuración del Modelo",
        "common_results":         "📊 Resultados",
        "common_iterations":      "Iteraciones",
        "common_convergence":     "Convergencia",
        "common_yes":             "Sí",
        "common_no":              "No",
        "common_ok":              "Cumple",
        "common_fail":            "No cumple",
        "common_no_results":      "Sin resultados",
        "common_download_csv":    "📥 Descargar CSV",
        
        # ========================================================
        # ETIQUETAS DE LA BARRA LATERAL (NUEVO)
        # ========================================================
        "language_label":         " Idioma",
        "lang_es":                "🇲🇽 Español",
        "lang_en":                "🇺🇸 Inglés",
        
        # ========================================================
        # app.py (ya cubierto en respuesta anterior)
        # ========================================================
        # ---------- Configuración / títulos de página ----------
        "page_title":           "Análisis, Simulación y Optimización - Inicio",
        # ---------- Encabezados ----------
        "title_main":           "🏠 Análisis, Simulación & Optimización",
        "header_proposito":     "🎯 Propósito General",
        "header_modulos":       " Módulos disponibles",
        # ---------- Texto introductorio ----------
        "intro_text": (
            "Bienvenido al **Conjunto de Simulación, Análisis y Optimización**, un entorno integrado "
            "que reúne al rededor de 16 herramientas especializadas para la ingeniería, la "
            "termodinámica, la mecánica de fluidos, los métodos numéricos y la ciencia de datos.\n\n"
            "Esta plataforma ha sido diseñada para ofrecer soluciones prácticas a problemas "
            "comunes en el ámbito académico e industrial, permitiendo a ingenieros, "
            "investigadores y estudiantes realizar cálculos avanzados sin necesidad de "
            "recurrir a software comercial pesado.\n\n"
            "### ¿Qué puedes hacer aquí?\n\n"
            "- **Diseñar y simular columnas de destilación** (métodos cortos y rigurosos).\n"
            "- **Calcular propiedades termodinámicas** de fluidos puros y mezclas.\n"
            "- **Resolver problemas de equilibrio de fases** (Flash, envolvente de saturación).\n"
            "- **Analizar sistemas hidráulicos** con tuberías, accesorios, bombas, compresores y turbinas.\n"
            "- **Aplicar métodos numéricos** para resolver ecuaciones, sistemas, EDOs y EDPs.\n"
            "- **Realizar ajustes de datos** mediante regresión y optimización.\n"
            "- **Entrenar modelos de redes neuronales** con TensorFlow.\n\n"
            "Todo en una interfaz amigable, con descripciones claras y ejemplos ilustrativos."
        ),
        # ---------- Categorías de módulos ----------
        "subcat1":      "🔬 Termodinámica y Equilibrio de Fases",
        "cat1_desc": (
            "- **Método Corto (FUG + Kirkbride)**: Predimensionamiento de columnas de destilación "
            "utilizando Fenske, Underwood, Gilliland y Kirkbride. Calcula platos mínimos, reflujo "
            "mínimo y ubicación óptima de alimentación.\n\n"
            "- **Método Riguroso (Etapa por Etapa)**: Simulación detallada de columnas de destilación "
            "con resolución de ecuaciones MESH. Entrega perfiles de temperatura, composición y flujos "
            "en cada plato.\n\n"
            "- **Cálculo Flash**: Determina el equilibrio vapor‑líquido (VLE) de una mezcla "
            "multicomponente mediante el método de Rachford‑Rice y ecuaciones de estado (RK, SRK, PR). "
            "Proporciona composiciones de fases y fracción vaporizada.\n\n"
            "- **Envolvente Termodinámica**: Visualiza la curva de saturación de un fluido puro en "
            "diagramas T‑s o P‑h, con líneas auxiliares de isobaras, isotermas y calidad constante (x). "
            "Incluye propiedades en el punto de operación.\n\n"
            "- **Propiedades Fisico‑químicas**: Calcula propiedades como factor de compresibilidad, "
            "densidad, viscosidad, Cp, entalpía y energía libre de Gibbs para sustancias puras o mezclas, "
            "usando ecuaciones de estado cúbicas."
        ),
        "subcat2":      "💧 Hidráulica y Mecánica de Fluido",
        "cat2_desc": (
            "- **Análisis Hidráulico (General)**: Calcula caídas de presión en tuberías con accesorios, "
            "cambios de elevación y flujo adicional. Incluye perfiles de presión y elevación a lo largo "
            "del sistema.\n\n"
            "- **Sistemas de Rociadores**: Diseño hidráulico de redes de rociadores contra "
            "incendio, considerando el coeficiente K de cada rociador y el caudal requerido. Calcula "
            "presiones y caudales acumulados.\n\n"
            "- **Bombas Centrífugas**: Dimensionamiento y selección de bombas mediante el análisis de "
            "la curva del sistema y la curva de la bomba. Calcula NPSH disponible y potencia requerida.\n\n"
            "- **Compresor de Gas**: Compresión isentrópica o politrópica de gases, con cálculo de "
            "temperatura de descarga, cabeza de compresión, potencia y eficiencia. Incluye curvas de "
            "cabeza y eficiencia vs. caudal.\n\n"
            "- **Turbina de Gas**: Expansión isentrópica o politrópica en turbinas, con estimación de "
            "cabeza generada, temperatura de salida, potencia mecánica y eficiencia."
        ),
        "subcat3":      "📊 Métodos Numéricos y Matemáticos",
        "cat3_desc": (
            "- **Resolución de Ecuaciones y Sistemas**: Encuentra raíces de ecuaciones univariables "
            "(Bisección, Newton‑Raphson, Secante) y soluciones de sistemas multivariables "
            "(Newton‑Raphson y Punto Fijo). Incluye visualización de convergencia y tablas de iteraciones.\n\n"
            "- **Integración Numérica Avanzada**: Aproxima integrales definidas usando métodos del "
            "trapecio, Simpson 1/3, Simpson 3/8 y cuadratura de Gauss‑Legendre (2‑10 puntos). Compara "
            "con el valor exacto (SymPy) y muestra el error.\n\n"
            "- **EDOs de Primer Orden (Sistemas)**: Resuelve sistemas de EDOs acopladas mediante el "
            "método de Runge‑Kutta 4to orden. Visualiza la evolución temporal de todas las variables y "
            "presenta tablas numéricas.\n\n"
        ),
        "subcat4":      "🧠 Análisis de Datos y Optimización",
        "cat4_desc": (
            "- **Regresión por Mínimos Cuadrados**: Ajusta modelos lineales, polinomiales o "
            "multivariables a datos experimentales. Calcula métricas de bondad de ajuste (R², R² ajustado, "
            "MSE, RMSE) y genera gráficos de dispersión con la curva ajustada.\n\n"
            "- **Optimización Matemática**: Resuelve problemas de programación lineal (Simplex) y no "
            "lineal (SLSQP, BFGS, Nelder‑Mead). Permite definir restricciones y visualizar la región "
            "factible y el punto óptimo.\n\n"            
        ),
        "footer_caption":       "© 2026 Suite de Simulación y Análisis | Todos los derechos reservados",
        # ---------- Página post-login ----------
        "welcome":              "Bienvenido, {user}",
        "role":                 "**Rol:** {rol}",
        "success_plan":         "🎉 Tienes el **{plan}** activo",
        "warning_no_plan":      "⚠️ No tienes una suscripción activa. [Adquiere un plan aquí](/Pagos)",
        "info_donated":         "❤️ Has donado **${total:,.2f} USD** a nuestras causas. ¡Gracias!",
        "modulos_disponibles":  "Módulos Disponibles:",
        # ---------- Tarjetas de módulos ----------
        "module1_title":        "📈 Mínimos Cuadrados",
        "module1_desc":         "Análisis de regresión",
        "module2_title":        "⚙️ Optimización",
        "module2_desc":         "Simplex y No Lineal",
        "access_allowed":       "✅ Acceso permitido",
        "access_required":      "Requiere suscripción",
        "access_required_pro":  "Requiere Plan Pro",
        "module3_title":        "💳 Suscripciones",
        "module3_desc":         "Gestiona tu plan",
        "btn_pagos":            "Ir a Pagos",
        "module4_title":        "❤️ Donativos",
        "module4_desc":         "Apoya nuestras causas",
        "btn_donativo":         "Hacer Donativo",
        "btn_logout":           "Cerrar Sesión",
        # ---------- Selector ----------
        "lang_selector":        "🌐 Idioma / Language",

        # En la sección "es":
        "sidebar_title":        "Navegación",
        "nav_home":             "Inicio",
        "nav_thermo":           "Termodinámica",
        "nav_properties":       "Propiedades Mezclas",
        "nav_flash":            "Cálculo Flash",
        "nav_shortcut":         "Métodos Cortos",
        "nav_rigorous":         "Métodos Rigurosos",
        "nav_envelope":         "Envolventes",
        "nav_hydraulics":       "Hidráulica",
        "nav_hydraulic":        "Análisis Hidráulico",
        "nav_firewater":        "Rociadores",
        "nav_pumps":            "Bombas",
        "nav_compressors":      "Compresores",
        "nav_turbines":         "Turbinas",
        "nav_numerical":        "Métodos Numéricos",
        "nav_ode":              "Ecuaciones Diferenciales",
        "nav_integration":      "Integración Numérica",
        "nav_ode_system":       "Sistema EDOs",
        "nav_pde":              "EDPs 1D",
        "nav_polynomials":      "Solución Polinomios",
        "nav_ai":               "Datos",
        "nav_neural":           "Redes Neuronales",
        "nav_mc":               "Mínimos Cuadrados",
        "nav_opt":              "Optimización",
        "nav_external":         "Páginas Externas",
        "nav_payments":         "Pagos",
        "nav_donations":        "Donativos",
        "language_label":       "Idioma",
        "lang_es":              "🇲🇽 Español",
        "lang_en":              "🇺 Inglés",
    },
    # ============================================================
    # ENGLISH (mismas claves, valores en inglés)
    # ============================================================
    "en": {
        # ========== Shared (all pages) ==========
        "common_lang_selector":   "🌐 Language / Idioma",
        "common_run":             " Run",
        "common_calc":            "🔍 Calculate",
        "common_select":          "Select",
        "common_delete":          "Delete",
        "common_components_sel":  "Selected components:",
        "common_no_components":   "No components selected.",
        "common_model_config":    "⚙️ Model Configuration",
        "common_results":         "📊 Results",
        "common_iterations":      "Iterations",
        "common_convergence":     "Convergence",
        "common_yes":             "Yes",
        "common_no":              "No",
        "common_ok":              "OK",
        "common_fail":            "Fail",
        "common_no_results":      "No results",
        "common_download_csv":    "📥 Download CSV",
        
        # ========================================================
        # SIDEBAR LABELS (NEW)
        # ========================================================
        "language_label":         "🌐 Language",
        "lang_es":                "🇲🇽 Spanish",
        "lang_en":                "🇺🇸 English",
        
        # ========================================================
        # app.py
        # ========================================================
        "page_title":           "Analysis, Simulation and Optimization - Home",
        "title_main":           " Analysis, Simulation & Optimization",
        "header_proposito":     "🎯 General Purpose",
        "header_modulos":       "📂 Available Modules",
        "intro_text": (
            "Welcome to the **Simulation, Analysis & Optimization set**, an integrated environment bringing "
            "together around 16 specialized tools for engineering, thermodynamics, fluid mechanics, "
            "numerical methods, and data science.\n\n"
            "This platform is designed to provide practical solutions to common problems in both "
            "academic and industrial settings, allowing engineers, researchers, and students to perform "
            "advanced calculations without relying on heavy commercial software.\n\n"
            "### What can you do here?\n\n"
            "- **Design and simulate distillation columns** (short-cut and rigorous methods).\n"
            "- **Calculate thermodynamic properties** of pure fluids and mixtures.\n"
            "- **Solve phase equilibrium problems** (Flash, saturation envelope).\n"
            "- **Analyze hydraulic systems** with pipes, fittings, pumps, compressors, and turbines.\n"
            "- **Apply numerical methods** to solve equations, systems, ODEs, and PDEs.\n"
            "- **Fit data** through regression and optimization.\n"
            "- **Train neural network models** with TensorFlow.\n\n"
            "All within a friendly interface, with clear descriptions and illustrative examples."
        ),
        "subcat1":      "🔬 Thermodynamics and Phase Equilibrium",
        "cat1_desc": (
            "- **Short-Cut Method (FUG + Kirkbride)**: Preliminary design of distillation columns "
            "using Fenske, Underwood, Gilliland, and Kirkbride. Computes minimum stages, minimum reflux, "
            "and optimal feed location.\n\n"
            "- **Rigorous Method (Stage by Stage)**: Detailed simulation of distillation columns by "
            "solving MESH equations. Provides temperature, composition, and flow profiles for each stage.\n\n"
            "- **Flash Calculation**: Determines vapor‑liquid equilibrium (VLE) of a multicomponent "
            "mixture using the Rachford‑Rice method and equations of state (RK, SRK, PR). Provides phase "
            "compositions and vapor fraction.\n\n"
            "- **Thermodynamic Envelope**: Visualizes the saturation curve of a pure fluid in T‑s or "
            "P‑h diagrams, with auxiliary lines for isobars, isotherms, and constant quality (x). Includes "
            "properties at the operating point.\n\n"
            "- **Physicochemical Properties**: Computes properties such as compressibility factor, "
            "density, viscosity, Cp, enthalpy, and Gibbs free energy for pure substances or mixtures, "
            "using cubic equations of state."
        ),
        "subcat2":      "💧 Hydraulics and Fluid Mechanics",
        "cat2_desc": (
            "- **Hydraulic Analysis (General)**: Calculates pressure drops in pipes with fittings, "
            "elevation changes, and additional flow. Includes pressure and elevation profiles along the "
            "system.\n\n"
            "- **Sprinkler Systems (NFPA 15)**: Hydraulic design of fire sprinkler networks, considering "
            "the K coefficient of each sprinkler and the required flow rate. Computes accumulated pressures "
            "and flows.\n\n"
            "- **Centrifugal Pumps**: Sizing and selection of pumps through analysis of the system curve "
            "and pump curve. Calculates available NPSH and required power.\n\n"
            "- **Gas Compressor**: Isentropic or polytropic gas compression, with discharge temperature, "
            "compression head, power, and efficiency calculations. Includes head and efficiency curves vs. "
            "flow rate.\n\n"
            "- **Gas Turbine**: Isentropic or polytropic expansion in turbines, with estimates of "
            "generated head, outlet temperature, mechanical power, and efficiency."
        ),
        "subcat3":      "📊 Numerical and Mathematical Methods",
        "cat3_desc": (
            "- **Equation and System Solving**: Finds roots of single-variable equations (Bisection, "
            "Newton‑Raphson, Secant) and solutions of multivariable systems (Newton‑Raphson and Fixed "
            "Point). Includes convergence visualization and iteration tables.\n\n"
            "- **Advanced Numerical Integration**: Approximates definite integrals using trapezoidal, "
            "Simpson 1/3, Simpson 3/8, and Gauss‑Legendre quadrature (2‑10 points). Compares with the exact "
            "value (SymPy) and shows the error.\n\n"
            "- **First-Order ODEs (Systems)**: Solves systems of coupled ODEs using the 4th-order "
            "Runge‑Kutta method. Visualizes the time evolution of all variables and presents numerical "
            "tables.\n\n"            
        ),
        "subcat4":      "🧠 Data Analysis and Optimization",
        "cat4_desc": (
            "- **Least Squares Regression**: Fits linear, polynomial, or multivariable models to "
            "experimental data. Computes goodness-of-fit metrics (R², adjusted R², MSE, RMSE) and generates "
            "scatter plots with the fitted curve.\n\n"
            "- **Mathematical Optimization**: Solves linear programming (Simplex) and nonlinear "
            "(SLSQP, BFGS, Nelder‑Mead) problems. Allows defining constraints and visualizing the feasible "
            "region and optimum point.\n\n"            
        ),
        "footer_caption":       "© 2026 Simulation & Analysis Suite | All rights reserved",
        "welcome":              "Welcome, {user}",
        "role":                 "**Role:** {rol}",
        "success_plan":         "🎉 You have the **{plan}** plan active",
        "warning_no_plan":      "⚠️ You don't have an active subscription. [Get a plan here](/Pagos)",
        "info_donated":         "❤️ You have donated **${total:,.2f} USD** to our causes. Thank you!",
        "modulos_disponibles":  "Available Modules:",
        "module1_title":        "📈 Least Squares",
        "module1_desc":         "Regression analysis",
        "module2_title":        "⚙️ Optimization",
        "module2_desc":         "Simplex and Nonlinear",
        "access_allowed":       "✅ Access granted",
        "access_required":      "Subscription required",
        "access_required_pro":  "Pro Plan required",
        "module3_title":        "💳 Subscriptions",
        "module3_desc":         "Manage your plan",
        "btn_pagos":            "Go to Payments",
        "module4_title":        "❤️ Donations",
        "module4_desc":         "Support our causes",
        "btn_donativo":         "Make a Donation",
        "btn_logout":           "Log Out",
        "lang_selector":        "🌐 Language / Idioma",

        # En la sección "en":
        "sidebar_title":        "Navigation",
        "nav_home":             "Home",
        "nav_thermo":           "Thermodynamics",
        "nav_properties":       "Mixture Properties",
        "nav_flash":            "Flash Calculation",
        "nav_shortcut":         "Shortcut Methods",
        "nav_rigorous":         "Rigorous Methods",
        "nav_envelope":         "Envelopes",
        "nav_hydraulics":       "Hydraulics",
        "nav_hydraulic":        "Hydraulic Analysis",
        "nav_firewater":        "Sprinklers",
        "nav_pumps":            "Pumps",
        "nav_compressors":      "Compressors",
        "nav_turbines":         "Turbines",
        "nav_numerical":        "Numerical Methods",
        "nav_ode":              "Differential Equations",
        "nav_integration":      "Numerical Integration",
        "nav_ode_system":       "ODE Systems",
        "nav_pde":              "1D PDEs",
        "nav_polynomials":      "Polynomial Solutions",
        "nav_ai":               "Data",
        "nav_neural":           "Neural Networks",
        "nav_mc":               "Least Squares",
        "nav_opt":              "Optimization",
        "nav_external":         "External Pages",
        "nav_payments":         "Payments",
        "nav_donations":        "Donations",
        "language_label":       "Language",
        "lang_es":              "🇲🇽 Spanish",
        "lang_en":              "🇺🇸 English",
    },
}

# ============================================================
# MOTOR i18n
# ============================================================

def init_lang():
    """Inicializa el idioma en session_state leyendo de la URL o usando 'es' por defecto.
    Debe llamarse UNA vez al inicio de cada página, ANTES de set_page_config()."""
    if "lang" not in st.session_state:
        lang = st.query_params.get("lang", "es")
        if lang not in TRANSLATIONS:
            lang = "es"
        st.session_state.lang = lang

def get_lang():
    """Devuelve el idioma actual ('es' o 'en')."""
    return st.session_state.get("lang", "es")

def t(key, **kwargs):
    """Traduce una clave al idioma actual. Si tiene placeholders, usar kwargs."""
    lang = get_lang()
    text = TRANSLATIONS.get(lang, {}).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text

def set_lang(lang):
    """Cambia el idioma y lo persiste en la URL."""
    if lang in TRANSLATIONS:
        st.session_state.lang = lang
        st.query_params["lang"] = lang

def language_selector(sidebar=True):
    """Dibuja el selector de idioma. Por defecto en el sidebar."""
    container = st.sidebar if sidebar else st
    options = {"Español": "es", "English": "en"}
    reverse = {v: k for k, v in options.items()}
    current_label = reverse.get(get_lang(), "Español")
    selected = container.selectbox(
        t("lang_selector"),
        list(options.keys()),
        index=list(options.keys()).index(current_label),
        key="lang_selector_widget"
    )
    new_lang = options[selected]
    if new_lang != get_lang():
        set_lang(new_lang)
        st.rerun()

def t_md(key, **kwargs):
    """Traduce texto largo con markdown. Alias de t() para claridad semántica."""
    return t(key, **kwargs)

def tw(key, **kwargs):
    """Traduce un string para usar en labels/placeholders/help de widgets."""
    return t(key, **kwargs)