/* ============================================================
   SISTEMA DE INTERNACIONALIZACIÓN (i18n) ES / EN
   Diccionario centralizado para todas las páginas del sitio.
   ============================================================ */
const translations = {
  es: {
    /* ---------------- Títulos de página ---------------- */
    page_title_index:        "Sistema de Análisis y Optimización - Plataforma Profesional",
    page_title_donativos:    "Donativos - Apoya Nuestro Desarrollo",
    page_title_comentarios:  "Comentarios y Reseñas",
    page_title_pagos:        "Pagos y Suscripciones",
    page_title_registro:     "Registro - Sistema de Análisis",
    page_title_login:        "Iniciar Sesión - Sistema de Análisis y Optimización",

    /* ---------------- Logos / navegación compartida ---------------- */
    logo_text:               "Análisis, Simulación & Optimización",
    logo_text_short:         "Sistema de Análisis",
    nav_inicio:              "Inicio",
    nav_caracteristicas:     "Características",
    nav_modulos:             "Módulos",
    nav_contacto:            "Contacto",
    nav_login:               "Login",
    nav_comentarios:         "Comentarios",
    nav_donativos:           "Donativos",
    back_home:               "Volver al Inicio",

    /* ============================================================
       index.html
       ============================================================ */
    hero_title:              "Plataforma Profesional de Análisis y Optimización",
    hero_desc:               "Conjunto integral de herramientas para ingeniería de procesos: análisis de regresión, optimización matemática, termodinámica, hidráulica, ecuaciones diferenciales, equipos rotatorios e inteligencia artificial. Software profesional para ingenieros, investigadores y analistas de datos.",
    btn_acceder:             "Acceder a la Aplicación",
    btn_conocer:             "Conocer Más",

    feat_section_title:      "Características Principales",
    feat_section_sub:        "Una suite completa de herramientas matemáticas, termodinámicas y de optimización diseñadas para profesionales de la ingeniería de procesos, investigación y análisis de datos",
    feat1_title:             "Mínimos Cuadrados",
    feat1_desc:              "Análisis de regresión lineal y polinomial con métricas estadísticas completas (R², MSE, RMSE). Carga datos desde CSV/Excel o ingresa manualmente.",
    feat2_title:             "Optimización Avanzada",
    feat2_desc:              "Método Simplex para programación lineal y algoritmos no lineales (SLSQP, BFGS, Nelder-Mead) para problemas complejos de ingeniería.",
    feat3_title:             "Termodinámica y Procesos",
    feat3_desc:              "Cálculo de propiedades de mezclas, cálculo flash, métodos cortos y rigurosos de destilación, y análisis de procesos químicos.",
    feat4_title:             "Hidráulica y Flujo",
    feat4_desc:              "Análisis hidráulico de tuberías, hidráulica antifuego, y cálculo de redes de distribución de fluidos.",
    feat5_title:             "Ecuaciones Diferenciales",
    feat5_desc:              "Resolución de EDOs, ecuaciones diferenciales parciales 1D, integración numérica y sistemas de ecuaciones diferenciales.",
    feat6_title:             "Inteligencia Artificial",
    feat6_desc:              "Redes neuronales artificiales, envolventes de datos, y solución de polinomios para modelado predictivo avanzado.",
    feat7_title:             "Equipos Rotatorios",
    feat7_desc:              "Cálculo y selección de bombas, compresores y turbinas. Análisis de desempeño y curvas características.",
    feat8_title:             "Visualización Profesional",
    feat8_desc:              "Gráficos interactivos, mapas de contorno, regiones factibles y análisis de residuos para interpretar resultados.",

    cap_section_title:       "Módulos Disponibles",
    cap_section_sub:         "Cada módulo está diseñado para resolver problemas específicos de ingeniería de procesos, análisis y ciencia de datos con precisión y eficiencia profesional",
    cap1_title:              "📈 Análisis de Regresión",
    cap1_list:               "<li>Regresión lineal simple y múltiple</li><li>Regresión polinomial hasta grado 10</li><li>Análisis multivariable</li><li>Métricas de ajuste estadístico (R², MSE, RMSE)</li><li>Exportación de resultados</li>",
    cap2_title:              "⚙️ Optimización Lineal",
    cap2_list:               "<li>Método Simplex (HiGHS)</li><li>Funciones objetivo lineales</li><li>Restricciones de igualdad y desigualdad</li><li>Límites de variables</li><li>Visualización de región factible</li>",
    cap3_title:              "Optimización No Lineal",
    cap3_list:               "<li>Múltiples algoritmos (SLSQP, BFGS, etc.)</li><li>Funciones objetivo complejas</li><li>Restricciones no lineales</li><li>Mapas de contorno 2D</li><li>Punto inicial personalizable</li>",
    cap4_title:              "🧪 Termodinámica",
    cap4_list:               "<li>Propiedades de mezclas</li><li>Cálculo flash (equilibrio vapor-líquido)</li><li>Métodos cortos de destilación</li><li>Métodos rigurosos de separación</li><li>Balance de materia y energía</li>",
    cap5_title:              "Análisis Hidráulico",
    cap5_list:               "<li>Cálculo de caída de presión</li><li>Análisis de redes de tuberías</li><li>Hidráulica antifuego (NFPA)</li><li>Selección de diámetros</li><li>Cálculo de bombas requeridas</li>",
    cap6_title:              "📐 Ecuaciones Diferenciales",
    cap6_list:               "<li>Sistemas de EDOs</li><li>Ecuaciones diferenciales parciales 1D</li><li>Integración numérica avanzada</li><li>Métodos de Runge-Kutta</li><li>Condiciones iniciales y de frontera</li>",
    cap7_title:              "🧮 Métodos Numéricos",
    cap7_list:               "<li>Solución de polinomios</li><li>Cálculo de envolventes</li><li>Interpolación y extrapolación</li><li>Búsqueda de raíces</li><li>Optimización numérica</li>",
    cap8_title:              "🧠 Redes Neuronales",
    cap8_list:               "<li>Redes neuronales artificiales</li><li>Entrenamiento supervisado</li><li>Modelado predictivo</li><li>Validación cruzada</li><li>Ajuste de hiperparámetros</li>",
    cap9_title:              "🌀 Bombas",
    cap9_list:               "<li>Selección de bombas centrífugas</li><li>Curvas características</li><li>Cálculo de NPSH</li><li>Punto de operación</li><li>Análisis de eficiencia</li>",
    cap10_title:             "💨 Compresores",
    cap10_list:              "<li>Compresores centrífugos y reciprocantes</li><li>Cálculo de potencia requerida</li><li>Relación de compresión</li><li>Curvas de desempeño</li><li>Análisis termodinámico</li>",
    cap11_title:             "Turbinas",
    cap11_list:              "<li>Turbinas de vapor y gas</li><li>Cálculo de potencia generada</li><li>Eficiencia isentrópica</li><li>Balance energético</li><li>Selección de equipos</li>",
    cap12_title:             "💳 Gestión y Pagos",
    cap12_list:              "<li>Suscripciones por niveles</li><li>Pagos con PayPal y Stripe</li><li>Sistema de donativos</li><li>Historial de transacciones</li><li>Certificados de donación</li>",

    cta_title:               "Comienza a Optimizar Tus Proyectos Hoy",
    cta_desc:                "Únete a profesionales de la ingeniería de procesos, investigación y análisis de datos que ya utilizan nuestra plataforma integral para resolver problemas complejos de termodinámica, hidráulica, optimización y modelado matemático.",
    btn_lanzar:              "Lanzar Aplicación Ahora",
    btn_iniciar_sesion:      "Iniciar Sesión",
    btn_donativos:           "Donativos",

    footer_about_title:      "Sobre la Plataforma",
    footer_about_desc:       "Suite profesional de herramientas para ingeniería de procesos: análisis matemático, optimización, termodinámica, hidráulica, ecuaciones diferenciales, equipos rotatorios e inteligencia artificial. Desarrollado con tecnología de punta.",
    footer_modules_title:    "Módulos Principales",
    footer_modules_list:     '<a href="#">Mínimos Cuadrados</a><br><a href="#">Optimización Lineal/No Lineal</a><br><a href="#">Termodinámica y Procesos</a><br><a href="#">Análisis Hidráulico</a><br><a href="#">Ecuaciones Diferenciales</a><br><a href="#">Equipos Rotatorios</a>',
    footer_contact_title:    "Contacto",
    footer_contact_list:     "<i class='fab fa-linkedin-in'></i> Jesus Ulises Echeverría León<br><i class='fab fa-facebook-f'></i> Jesus Echeverría<br><i class='fas fa-map-marker-alt'></i> CDMX, México",
    footer_links_title:      "Enlaces Rápidos",
    footer_links_list:       '<a href="#">Documentación</a><br><a href="#">Términos y Condiciones</a><br><a href="#">Política de Privacidad</a><br><a href="#">Soporte Técnico</a>',
    footer_comments_title:   "Comentarios",
    footer_comments_desc:    "Lee opiniones de otros usuarios y comparte tu experiencia con la plataforma.",
    btn_comentarios:         "Ver Comentarios",
    footer_copyright:        "© 2026 Sistema de Análisis y Optimización. Todos los derechos reservados.",

    /* ============================================================
       donativos.html
       ============================================================ */
    don_hero_title:          "Apoya el Desarrollo del Software",
    don_hero_sub:            "Tu contribución nos ayuda a mantener y mejorar estas herramientas profesionales de forma gratuita para toda la comunidad",
    don_goal:                "Meta: $10,000 USD",
    don_tiers_title:         "Elige tu Nivel de Contribución",
    don_t1_name:             "Colaborador",
    don_t1_desc:             "Apoyo básico al desarrollo",
    don_t1_b1:               "Agradecimiento en el sitio web",
    don_t1_b2:               "Acceso a newsletter",
    don_t2_badge:            "Más Popular",
    don_t2_name:             "Patrocinador",
    don_t2_desc:             "Apoyo significativo al proyecto",
    don_t2_b1:               "Nombre en la lista de patrocinadores",
    don_t2_b2:               "Acceso prioritario a nuevas funciones",
    don_t2_b3:               "Certificado de donación",
    don_t2_b4:               "Soporte técnico prioritario",
    don_t3_name:             "Contribuyente",
    don_t3_desc:             "Contribución mayor al desarrollo",
    don_t3_b1:               "Todos los beneficios anteriores",
    don_t3_b2:               "Logo en la página de contribuyentes",
    don_t3_b3:               "Acceso beta a nuevas características",
    don_t3_b4:               "Consultoría técnica (1 hora)",
    don_t4_name:             "Personalizado",
    don_t4_price:            "Otro monto",
    don_t4_desc:             "La cantidad que tú decidas",
    don_t4_placeholder:      "Ingresa monto",
    don_btn_paypal:          "Donar con PayPal",
    don_impact_title:        "¿En qué se usan los donativos?",
    don_i1_title:            "Desarrollo de Software",
    don_i1_desc:             "Mantenimiento y mejora continua de las herramientas, corrección de bugs y desarrollo de nuevas características.",
    don_i2_title:            "Documentación",
    don_i2_desc:             "Creación de tutoriales, guías de usuario y material educativo para facilitar el uso del software.",
    don_i3_title:            "Infraestructura",
    don_i3_desc:             "Servidores, hosting, dominios y herramientas necesarias para mantener el servicio disponible 24/7.",
    don_i4_title:            "Comunidad",
    don_i4_desc:             "Soporte a la comunidad, foros de ayuda, y organización de eventos y webinars educativos.",
    don_recent_title:        "Donantes Recientes",
    don_d4_name:             "Donante Anónimo",
    don_time_2h:             "Hace 2 horas",
    don_time_5h:             "Hace 5 horas",
    don_time_1d:             "Hace 1 día",
    don_time_2d:             "Hace 2 días",
    don_cta_title:           "¿Prefieres otra forma de donar?",
    don_cta_desc:            "También aceptamos transferencias bancarias y otras formas de pago",
    don_btn_bank:            "Transferencia Bancaria",
    don_btn_other:           "Otros Métodos",
    don_footer_msg:          "Tu generosidad hace posible el software libre y de código abierto.",
    footer_copyright_short:  "© 2026 Sistema de Análisis y Optimización. Todos los derechos reservados.",
   
    /* ---------------- donativos.html (claves adicionales) ---------------- */
   donv_hero_title:        "❤️ Haz la Diferencia con tu Donativo",
   donv_hero_sub:          "Tu contribución nos ayuda a mantener y mejorar estas herramientas profesionales de forma gratuita",
   donv_chart_title:       "Donativos por Mes",
   donv_goal_label:        "Meta:",
   donv_progress_label:    "Progreso:",
   donv_form_title:        "❤️ Realiza tu Donativo",
   donv_amount_label:      "Monto a donar *",
   donv_amount_ph:         "Ej: 25",
   donv_currency_label:    "Moneda",
   donv_currency_usd:      "USD - Dólar estadounidense",
   donv_currency_eur:      "EUR - Euro",
   donv_currency_mxn:      "MXN - Peso mexicano",
   donv_method_label:      "Método de pago *",
   donv_method_paypal:     "PayPal",
   donv_method_crypto:     "Criptomonedas",
   donv_crypto_label:      "Criptomoneda",
   donv_name_label:        "Nombre",
   donv_name_ph:           "Tu nombre (opcional)",
   donv_email_label:       "Email",
   donv_email_ph:          "tu@email.com (opcional)",
   donv_anonymous_label:   "Hacer donativo anónimo",
   donv_message_label:     "Mensaje de apoyo (opcional)",
   donv_message_ph:        "Deja un mensaje...",
   donv_submit:            "Donar Ahora",
   donv_modal_title:       "Donativo con Criptomonedas",
   donv_modal_send:        "Envía:",
   donv_modal_network:     "Red:",
   donv_modal_address:     "Dirección:",
   donv_modal_copy:        "Copiar dirección",
   donv_modal_verify_title:"Verificar Transacción",
   donv_modal_verify_ph:   "Hash de transacción",
   donv_modal_verify_btn:  "Verificar",
   donv_recent_title:      "🌟 Donantes Recientes",
   donv_footer_copyright:  "© 2024 Sistema de Análisis y Optimización. Todos los derechos reservados.",

    /* ============================================================
       comentarios.html
       ============================================================ */
    com_hero_title:          "Comentarios y Reseñas",
    com_hero_sub:            "Comparte tu experiencia con nuestra plataforma",
    com_form_title:          "Deja tu Comentario",
    com_label_name:          "Nombre",
    com_label_email:         "Email",
    com_label_rating:        "Calificación",
    com_label_comment:       "Comentario",
    com_ph_name:             "Tu nombre",
    com_ph_email:            "tu@email.com",
    com_ph_comment:          "Escribe tu comentario...",
    com_btn_submit:          "Enviar Comentario",
    com_list_title:          "Comentarios Recientes",
    com_c1_text:             "Excelente plataforma. Las herramientas de optimización son muy potentes y fáciles de usar. Totalmente recomendada.",
    com_c2_text:             "Muy útil para mis proyectos de ingeniería. El módulo de mínimos cuadrados me ha ahorrado mucho tiempo.",
    com_c3_text:             "Buena herramienta. Sería genial agregar más ejemplos de uso en la documentación.",
    com_time_2d:             "Hace 2 días",
    com_time_5d:             "Hace 5 días",
    com_time_1w:             "Hace 1 semana",

    /* ============================================================
       pagos.html
       ============================================================ */
    pag_hero_title:          "Planes y Suscripciones",
    pag_hero_sub:            "Elige el plan que mejor se adapte a tus necesidades",
    pag_month:               "/mes",
    pag_badge_popular:       "Más Popular",
    pag_btn_select:          "Seleccionar Plan",
    pag_plan1_name:          "Básico",
    pag_plan1_desc:          "Ideal para estudiantes y principiantes",
    pag_plan1_f1:            "Acceso a Mínimos Cuadrados",
    pag_plan1_f2:            "Análisis de regresión lineal",
    pag_plan1_f3:            "Exportación básica",
    pag_plan1_f4:            "Soporte por email",
    pag_plan2_name:          "Profesional",
    pag_plan2_desc:          "Para profesionales y consultores",
    pag_plan2_f1:            "Todo lo del plan Básico",
    pag_plan2_f2:            "Optimización Lineal y No Lineal",
    pag_plan2_f3:            "Análisis multivariable",
    pag_plan2_f4:            "Exportación avanzada",
    pag_plan2_f5:            "Soporte prioritario",
    pag_plan3_name:          "Empresarial",
    pag_plan3_desc:          "Para empresas y equipos grandes",
    pag_plan3_f1:            "Todo lo del plan Pro",
    pag_plan3_f2:            "Usuarios ilimitados",
    pag_plan3_f3:            "API de acceso",
    pag_plan3_f4:            "Soporte 24/7",
    pag_plan3_f5:            "Personalización",
    pag_methods_title:       "Métodos de Pago Aceptados",
    pag_m1_title:            "PayPal",
    pag_m1_desc:             "Pago seguro con PayPal",
    pag_m2_title:            "Tarjeta de Crédito",
    pag_m2_desc:             "Visa, Mastercard, Amex",
    pag_m3_title:            "Transferencia",
    pag_m3_desc:             "Transferencia bancaria",
    pag_footer:              "© 2024 Sistema de Análisis y Optimización",

    /* ============================================================
       registro.html
       ============================================================ */
    reg_header_title:        "Crear Cuenta",
    reg_header_sub:          "Regístrate para acceder a las herramientas profesionales",
    reg_label_fullname:      "Nombre Completo",
    reg_ph_fullname:         "Tu nombre completo",
    reg_label_email:         "Email",
    reg_label_username:      "Nombre de Usuario",
    reg_ph_username:         "Elige un usuario",
    reg_label_password:      "Contraseña",
    reg_ph_password:         "Mínimo 8 caracteres",
    reg_pwd_hint:            "Debe contener mayúsculas, minúsculas y números",
    reg_label_confirm:       "Confirmar Contraseña",
    reg_ph_confirm:          "Repite tu contraseña",
    reg_terms:               "Acepto los términos y condiciones",
    reg_btn_create:          "Crear Cuenta",
    reg_divider:             "o",
    reg_btn_have_account:    "Ya tengo una cuenta",
    reg_benefits_title:      "Beneficios de registrarte:",
    reg_b1:                  "Acceso gratuito a herramientas básicas",
    reg_b2:                  "Guardar tus proyectos",
    reg_b3:                  "Soporte de la comunidad",
    reg_b4:                  "Actualizaciones gratuitas",

    /* ============================================================
       login.html
       ============================================================ */
    log_header_title:        "Sistema de Análisis y Optimización",
    log_header_sub:          "Inicia sesión para acceder a las herramientas profesionales",
    log_label_user:          "Usuario",
    log_ph_user:             "Ingresa tu usuario",
    log_label_password:      "Contraseña",
    log_ph_password:         "Ingresa tu contraseña",
    log_remember:            "Recordarme",
    log_forgot:              "¿Olvidaste tu contraseña?",
    log_btn_login:           "Iniciar Sesión",
    log_divider:             "o",
    log_btn_back:            "Volver al Inicio",
    log_no_account:          "¿No tienes una cuenta?",
    log_register:            "Regístrate aquí",
    log_benefits_title:      "Beneficios de acceder:",
    log_b1:                  "Acceso a módulos avanzados de optimización",
    log_b2:                  "Guardar y gestionar tus proyectos",
    log_b3:                  "Exportar resultados en múltiples formatos",
    log_b4:                  "Soporte técnico prioritario",

    /* ============================================================
       Nueva sección de donativos
       ============================================================ */
    don_currency_label: "Moneda de donativo",
    don_currency_hint: "Equivalencia aproximada. El cargo con PayPal se procesa en USD.",
    don_crypto_title: "Donativos con Criptomonedas",
    don_crypto_sub: "También puedes apoyarnos con criptomonedas. Selecciona la moneda de tu preferencia, copia la dirección y envía el monto que desees.",
    don_crypto_btc_note: "Envía únicamente BTC por la red Bitcoin.",
    don_crypto_eth_note: "Envía únicamente ETH por la red Ethereum (ERC-20).",
    don_crypto_usdt_note: "Envía únicamente USDT por la red Tron (TRC-20).",
    don_crypto_usdc_note: "Envía únicamente USDC por la red Ethereum (ERC-20).",
    don_conv_title: "Calculadora de donativo",
    don_conv_sub: "Ingresa el monto en tu moneda y mira su equivalente aproximado en criptomonedas.",
    don_conv_amount: "Monto a donar",
    don_conv_currency: "Moneda",
    don_conv_disclaimer: "Los equivalentes son aproximados y pueden variar según el tipo de cambio del momento.",
    don_crypto_warning: "Verifica siempre la red y la dirección antes de enviar. Las transacciones con criptomonedas son irreversibles."
  },

  en: {
    /* ---------------- Page titles ---------------- */
    page_title_index:        "Analysis & Optimization System - Professional Platform",
    page_title_donativos:    "Donations - Support Our Development",
    page_title_comentarios:  "Comments and Reviews",
    page_title_pagos:        "Plans and Subscriptions",
    page_title_registro:     "Sign Up - Analysis System",
    page_title_login:        "Sign In - Analysis & Optimization System",

    /* ---------------- Logos / shared nav ---------------- */
    logo_text:               "Analysis, Simulation & Optimization",
    logo_text_short:         "Analysis System",
    nav_inicio:              "Home",
    nav_caracteristicas:     "Features",
    nav_modulos:             "Modules",
    nav_contacto:            "Contact",
    nav_login:               "Login",
    nav_comentarios:         "Comments",
    nav_donativos:           "Donations",
    back_home:               "Back to Home",

    /* ============================================================
       index.html
       ============================================================ */
    hero_title:              "Professional Analysis and Optimization Platform",
    hero_desc:               "Comprehensive set of tools for process engineering: regression analysis, mathematical optimization, thermodynamics, hydraulics, differential equations, rotating equipment, and artificial intelligence. Professional software for engineers, researchers, and data analysts.",
    btn_acceder:             "Access the Application",
    btn_conocer:             "Learn More",

    feat_section_title:      "Main Features",
    feat_section_sub:        "A complete suite of mathematical, thermodynamic and optimization tools designed for process engineering, research and data analysis professionals",
    feat1_title:             "Least Squares",
    feat1_desc:              "Linear and polynomial regression analysis with complete statistical metrics (R², MSE, RMSE). Load data from CSV/Excel or enter it manually.",
    feat2_title:             "Advanced Optimization",
    feat2_desc:              "Simplex method for linear programming and nonlinear algorithms (SLSQP, BFGS, Nelder-Mead) for complex engineering problems.",
    feat3_title:             "Thermodynamics and Processes",
    feat3_desc:              "Mixture property calculations, flash calculations, short-cut and rigorous distillation methods, and chemical process analysis.",
    feat4_title:             "Hydraulics and Flow",
    feat4_desc:              "Hydraulic analysis of pipelines, fire protection hydraulics, and calculation of fluid distribution networks.",
    feat5_title:             "Differential Equations",
    feat5_desc:              "Solving ODEs, 1D partial differential equations, numerical integration and systems of differential equations.",
    feat6_title:             "Artificial Intelligence",
    feat6_desc:              "Artificial neural networks, data envelopes, and polynomial solving for advanced predictive modeling.",
    feat7_title:             "Rotating Equipment",
    feat7_desc:              "Calculation and selection of pumps, compressors and turbines. Performance analysis and characteristic curves.",
    feat8_title:             "Professional Visualization",
    feat8_desc:              "Interactive charts, contour maps, feasible regions and residual analysis to interpret results.",

    cap_section_title:       "Available Modules",
    cap_section_sub:         "Each module is designed to solve specific process engineering, analysis, and data science problems with professional accuracy and efficiency",
    cap1_title:              "📈 Regression Analysis",
    cap1_list:               "<li>Simple and multiple linear regression</li><li>Polynomial regression up to degree 10</li><li>Multivariable analysis</li><li>Statistical fit metrics (R², MSE, RMSE)</li><li>Export of results</li>",
    cap2_title:              "⚙️ Linear Optimization",
    cap2_list:               "<li>Simplex method (HiGHS)</li><li>Linear objective functions</li><li>Equality and inequality constraints</li><li>Variable bounds</li><li>Feasible region visualization</li>",
    cap3_title:              "Nonlinear Optimization",
    cap3_list:               "<li>Multiple algorithms (SLSQP, BFGS, etc.)</li><li>Complex objective functions</li><li>Nonlinear constraints</li><li>2D contour maps</li><li>Customizable starting point</li>",
    cap4_title:              "🧪 Thermodynamics",
    cap4_list:               "<li>Mixture properties</li><li>Flash calculation (vapor-liquid equilibrium)</li><li>Short-cut distillation methods</li><li>Rigorous separation methods</li><li>Material and energy balance</li>",
    cap5_title:              "Hydraulic Analysis",
    cap5_list:               "<li>Pressure drop calculation</li><li>Pipeline network analysis</li><li>Fire protection hydraulics (NFPA)</li><li>Diameter selection</li><li>Required pump calculation</li>",
    cap6_title:              "📐 Differential Equations",
    cap6_list:               "<li>Systems of ODEs</li><li>1D partial differential equations</li><li>Advanced numerical integration</li><li>Runge-Kutta methods</li><li>Initial and boundary conditions</li>",
    cap7_title:              "🧮 Numerical Methods",
    cap7_list:               "<li>Polynomial solving</li><li>Envelope calculation</li><li>Interpolation and extrapolation</li><li>Root finding</li><li>Numerical optimization</li>",
    cap8_title:              "🧠 Neural Networks",
    cap8_list:               "<li>Artificial neural networks</li><li>Supervised training</li><li>Predictive modeling</li><li>Cross-validation</li><li>Hyperparameter tuning</li>",
    cap9_title:              "🌀 Pumps",
    cap9_list:               "<li>Centrifugal pump selection</li><li>Characteristic curves</li><li>NPSH calculation</li><li>Operating point</li><li>Efficiency analysis</li>",
    cap10_title:             "💨 Compressors",
    cap10_list:              "<li>Centrifugal and reciprocating compressors</li><li>Required power calculation</li><li>Compression ratio</li><li>Performance curves</li><li>Thermodynamic analysis</li>",
    cap11_title:             "Turbines",
    cap11_list:              "<li>Steam and gas turbines</li><li>Generated power calculation</li><li>Isentropic efficiency</li><li>Energy balance</li><li>Equipment selection</li>",
    cap12_title:             "💳 Management and Payments",
    cap12_list:              "<li>Tiered subscriptions</li><li>PayPal and Stripe payments</li><li>Donation system</li><li>Transaction history</li><li>Donation certificates</li>",

    cta_title:               "Start Optimizing Your Projects Today",
    cta_desc:                "Join process engineering, research and data analysis professionals who already use our comprehensive platform to solve complex problems in thermodynamics, hydraulics, optimization and mathematical modeling.",
    btn_lanzar:              "Launch Application Now",
    btn_iniciar_sesion:      "Sign In",
    btn_donativos:           "Donations",

    footer_about_title:      "About the Platform",
    footer_about_desc:       "Professional suite of tools for process engineering: mathematical analysis, optimization, thermodynamics, hydraulics, differential equations, rotating equipment and artificial intelligence. Built with cutting-edge technology.",
    footer_modules_title:    "Main Modules",
    footer_modules_list:     '<a href="#">Least Squares</a><br><a href="#">Linear/Nonlinear Optimization</a><br><a href="#">Thermodynamics and Processes</a><br><a href="#">Hydraulic Analysis</a><br><a href="#">Differential Equations</a><br><a href="#">Rotating Equipment</a>',
    footer_contact_title:    "Contact",
    footer_contact_list:     "<i class='fab fa-linkedin-in'></i> Jesus Ulises Echeverría León<br><i class='fab fa-facebook-f'></i> Jesus Echeverría<br><i class='fas fa-map-marker-alt'></i> CDMX, México",
    footer_links_title:      "Quick Links",
    footer_links_list:       '<a href="#">Documentation</a><br><a href="#">Terms and Conditions</a><br><a href="#">Privacy Policy</a><br><a href="#">Technical Support</a>',
    footer_comments_title:   "Comments",
    footer_comments_desc:    "Read reviews from other users and share your experience with the platform.",
    btn_comentarios:         "View Comments",
    footer_copyright:        "© 2026 Analysis & Optimization System. All rights reserved.",

    /* ============================================================
       donativos.html
       ============================================================ */
    don_hero_title:          "Support Software Development",
    don_hero_sub:            "Your contribution helps us maintain and improve these professional tools for free for the entire community",
    don_goal:                "Goal: $10,000 USD",
    don_tiers_title:         "Choose Your Contribution Level",
    don_t1_name:             "Collaborator",
    don_t1_desc:             "Basic support for development",
    don_t1_b1:               "Acknowledgment on the website",
    don_t1_b2:               "Newsletter access",
    don_t2_badge:            "Most Popular",
    don_t2_name:             "Sponsor",
    don_t2_desc:             "Significant support for the project",
    don_t2_b1:               "Name on the sponsors list",
    don_t2_b2:               "Priority access to new features",
    don_t2_b3:               "Donation certificate",
    don_t2_b4:               "Priority technical support",
    don_t3_name:             "Contributor",
    don_t3_desc:             "Major contribution to development",
    don_t3_b1:               "All previous benefits",
    don_t3_b2:               "Logo on the contributors page",
    don_t3_b3:               "Beta access to new features",
    don_t3_b4:               "Technical consulting (1 hour)",
    don_t4_name:             "Custom",
    don_t4_price:            "Other amount",
    don_t4_desc:             "The amount you decide",
    don_t4_placeholder:      "Enter amount",
    don_btn_paypal:          "Donate with PayPal",
    don_impact_title:        "What are donations used for?",
    don_i1_title:            "Software Development",
    don_i1_desc:             "Ongoing maintenance and improvement of tools, bug fixes, and development of new features.",
    don_i2_title:            "Documentation",
    don_i2_desc:             "Creating tutorials, user guides, and educational material to make the software easier to use.",
    don_i3_title:            "Infrastructure",
    don_i3_desc:             "Servers, hosting, domains, and tools needed to keep the service available 24/7.",
    don_i4_title:            "Community",
    don_i4_desc:             "Community support, help forums, and organization of events and educational webinars.",
    don_recent_title:        "Recent Donors",
    don_d4_name:             "Anonymous Donor",
    don_time_2h:             "2 hours ago",
    don_time_5h:             "5 hours ago",
    don_time_1d:             "1 day ago",
    don_time_2d:             "2 days ago",
    don_cta_title:           "Prefer another way to donate?",
    don_cta_desc:            "We also accept bank transfers and other payment methods",
    don_btn_bank:            "Bank Transfer",
    don_btn_other:           "Other Methods",
    don_footer_msg:          "Your generosity makes free and open-source software possible.",
    footer_copyright_short:  "© 2026 Analysis & Optimization System. All rights reserved.",

    /* ---------------- donativos.html (additional keys) ---------------- */
   donv_hero_title:        "❤️ Make a Difference with Your Donation",
   donv_hero_sub:          "Your contribution helps us keep these professional tools free and improved for everyone",
   donv_chart_title:       "Donations per Month",
   donv_goal_label:        "Goal:",
   donv_progress_label:    "Progress:",
   donv_form_title:        "❤️ Make Your Donation",
   donv_amount_label:      "Amount to donate *",
   donv_amount_ph:         "e.g. 25",
   donv_currency_label:    "Currency",
   donv_currency_usd:      "USD - US Dollar",
   donv_currency_eur:      "EUR - Euro",
   donv_currency_mxn:      "MXN - Mexican Peso",
   donv_method_label:      "Payment method *",
   donv_method_paypal:     "PayPal",
   donv_method_crypto:     "Cryptocurrencies",
   donv_crypto_label:      "Cryptocurrency",
   donv_name_label:        "Name",
   donv_name_ph:           "Your name (optional)",
   donv_email_label:       "Email",
   donv_email_ph:          "you@email.com (optional)",
   donv_anonymous_label:   "Make anonymous donation",
   donv_message_label:     "Support message (optional)",
   donv_message_ph:        "Leave a message...",
   donv_submit:            "Donate Now",
   donv_modal_title:       "Cryptocurrency Donation",
   donv_modal_send:        "Send:",
   donv_modal_network:     "Network:",
   donv_modal_address:     "Address:",
   donv_modal_copy:        "Copy address",
   donv_modal_verify_title:"Verify Transaction",
   donv_modal_verify_ph:   "Transaction hash",
   donv_modal_verify_btn:  "Verify",
   donv_recent_title:      "🌟 Recent Donors",
   donv_footer_copyright:  "© 2024 Analysis & Optimization System. All rights reserved.",

    /* ============================================================
       comentarios.html
       ============================================================ */
    com_hero_title:          "Comments and Reviews",
    com_hero_sub:            "Share your experience with our platform",
    com_form_title:          "Leave Your Comment",
    com_label_name:          "Name",
    com_label_email:         "Email",
    com_label_rating:        "Rating",
    com_label_comment:       "Comment",
    com_ph_name:             "Your name",
    com_ph_email:            "you@email.com",
    com_ph_comment:          "Write your comment...",
    com_btn_submit:          "Submit Comment",
    com_list_title:          "Recent Comments",
    com_c1_text:             "Excellent platform. The optimization tools are very powerful and easy to use. Highly recommended.",
    com_c2_text:             "Very useful for my engineering projects. The least squares module has saved me a lot of time.",
    com_c3_text:             "Good tool. It would be great to add more usage examples in the documentation.",
    com_time_2d:             "2 days ago",
    com_time_5d:             "5 days ago",
    com_time_1w:             "1 week ago",

    /* ============================================================
       pagos.html
       ============================================================ */
    pag_hero_title:          "Plans and Subscriptions",
    pag_hero_sub:            "Choose the plan that best fits your needs",
    pag_month:               "/month",
    pag_badge_popular:       "Most Popular",
    pag_btn_select:          "Select Plan",
    pag_plan1_name:          "Basic",
    pag_plan1_desc:          "Ideal for students and beginners",
    pag_plan1_f1:            "Access to Least Squares",
    pag_plan1_f2:            "Linear regression analysis",
    pag_plan1_f3:            "Basic export",
    pag_plan1_f4:            "Email support",
    pag_plan2_name:          "Professional",
    pag_plan2_desc:          "For professionals and consultants",
    pag_plan2_f1:            "Everything in Basic",
    pag_plan2_f2:            "Linear and Nonlinear Optimization",
    pag_plan2_f3:            "Multivariable analysis",
    pag_plan2_f4:            "Advanced export",
    pag_plan2_f5:            "Priority support",
    pag_plan3_name:          "Enterprise",
    pag_plan3_desc:          "For companies and large teams",
    pag_plan3_f1:            "Everything in Pro",
    pag_plan3_f2:            "Unlimited users",
    pag_plan3_f3:            "API access",
    pag_plan3_f4:            "24/7 support",
    pag_plan3_f5:            "Customization",
    pag_methods_title:       "Accepted Payment Methods",
    pag_m1_title:            "PayPal",
    pag_m1_desc:             "Secure payment with PayPal",
    pag_m2_title:            "Credit Card",
    pag_m2_desc:             "Visa, Mastercard, Amex",
    pag_m3_title:            "Bank Transfer",
    pag_m3_desc:             "Bank transfer",
    pag_footer:              "© 2024 Analysis & Optimization System",

    /* ============================================================
       registro.html
       ============================================================ */
    reg_header_title:        "Create Account",
    reg_header_sub:          "Sign up to access professional tools",
    reg_label_fullname:      "Full Name",
    reg_ph_fullname:         "Your full name",
    reg_label_email:         "Email",
    reg_label_username:      "Username",
    reg_ph_username:         "Choose a username",
    reg_label_password:      "Password",
    reg_ph_password:         "Minimum 8 characters",
    reg_pwd_hint:            "Must contain uppercase, lowercase and numbers",
    reg_label_confirm:       "Confirm Password",
    reg_ph_confirm:          "Repeat your password",
    reg_terms:               "I accept the terms and conditions",
    reg_btn_create:          "Create Account",
    reg_divider:             "or",
    reg_btn_have_account:    "I already have an account",
    reg_benefits_title:      "Benefits of signing up:",
    reg_b1:                  "Free access to basic tools",
    reg_b2:                  "Save your projects",
    reg_b3:                  "Community support",
    reg_b4:                  "Free updates",

    /* ============================================================
       login.html
       ============================================================ */
    log_header_title:        "Analysis & Optimization System",
    log_header_sub:          "Sign in to access professional tools",
    log_label_user:          "Username",
    log_ph_user:             "Enter your username",
    log_label_password:      "Password",
    log_ph_password:         "Enter your password",
    log_remember:            "Remember me",
    log_forgot:              "Forgot your password?",
    log_btn_login:           "Sign In",
    log_divider:             "or",
    log_btn_back:            "Back to Home",
    log_no_account:          "Don't have an account?",
    log_register:            "Sign up here",
    log_benefits_title:      "Benefits of signing in:",
    log_b1:                  "Access to advanced optimization modules",
    log_b2:                  "Save and manage your projects",
    log_b3:                  "Export results in multiple formats",
    log_b4:                  "Priority technical support",

    /* ============================================================
       Nueva sección de donativos
       ============================================================ */
    don_currency_label: "Donation currency",
    don_currency_hint: "Approximate equivalence. PayPal charges are processed in USD.",
    don_crypto_title: "Cryptocurrency Donations",
    don_crypto_sub: "You can also support us with cryptocurrencies. Select your preferred coin, copy the address and send the amount you wish.",
    don_crypto_btc_note: "Send only BTC on the Bitcoin network.",
    don_crypto_eth_note: "Send only ETH on the Ethereum network (ERC-20).",
    don_crypto_usdt_note: "Send only USDT on the Tron network (TRC-20).",
    don_crypto_usdc_note: "Send only USDC on the Ethereum network (ERC-20).",
    don_conv_title: "Donation calculator",
    don_conv_sub: "Enter the amount in your currency and see its approximate equivalent in cryptocurrencies.",
    don_conv_amount: "Amount to donate",
    don_conv_currency: "Currency",
    don_conv_disclaimer: "Equivalents are approximate and may vary depending on the current exchange rate.",
    don_crypto_warning: "Always verify the network and address before sending. Cryptocurrency transactions are irreversible."
  }
};

/* ============================================================
   MOTOR i18n (idéntico en todas las páginas)
   ============================================================ */
function applyLang(lang) {
  const dict = translations[lang] || translations.es;

  // Texto plano
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key] !== undefined) el.textContent = dict[key];
  });

  // HTML interno (listas, <br>, iconos)
  document.querySelectorAll('[data-i18n-html]').forEach(el => {
    const key = el.getAttribute('data-i18n-html');
    if (dict[key] !== undefined) el.innerHTML = dict[key];
  });

  // Placeholders
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (dict[key] !== undefined) el.placeholder = dict[key];
  });

  // Título de pestaña según data-page
  const pageKey = document.body.getAttribute('data-page');
  if (pageKey && dict['page_title_' + pageKey]) {
    document.title = dict['page_title_' + pageKey];
  }

  document.documentElement.lang = lang;

  // El toggle muestra el idioma al que se puede cambiar
  const toggle = document.getElementById('lang-toggle');
  if (toggle) toggle.textContent = (lang === 'es') ? 'EN' : 'ES';

  localStorage.setItem('lang', lang);
}

function detectInitialLang() {
  const saved = localStorage.getItem('lang');
  if (saved && translations[saved]) return saved;
  const browser = (navigator.language || 'es').slice(0, 2).toLowerCase();
  return translations[browser] ? browser : 'es';
}

let currentLang = detectInitialLang();
applyLang(currentLang);

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('lang-toggle');
  if (toggle) {
    toggle.addEventListener('click', e => {
      e.preventDefault();
      currentLang = (currentLang === 'es') ? 'en' : 'es';
      applyLang(currentLang);
    });
  }
});