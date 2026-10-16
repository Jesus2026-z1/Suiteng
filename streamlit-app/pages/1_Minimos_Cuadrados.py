import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations_with_replacement
from utils.i18n import init_lang, t, tw
from languages.min_cuad_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

# ============================================================================
# INICIALIZACIÓN DE IDIOMA (antes de set_page_config)
# ============================================================================
init_lang()

render_sidebar()

# ============================================================================
# FUNCIONES DE MÍNIMOS CUADRADOS
# ============================================================================

def generar_features_polinomiales(X, grado):
    """Genera todas las combinaciones polinomiales hasta el grado especificado."""
    n_muestras, n_variables = X.shape
    features = [np.ones(n_muestras)]
    
    for d in range(1, grado + 1):
        for indices in combinations_with_replacement(range(n_variables), d):
            termino = np.ones(n_muestras)
            for idx in indices:
                termino = termino * X[:, idx]
            features.append(termino)
    
    return np.column_stack(features)

def analisis_minimos_cuadrados(X, y, tipo='lineal', grado=1):
    """Algoritmo de Minimos Cuadrados con soporte para regresion lineal y polinomial."""
    if tipo not in ['lineal', 'polinomial']:
        raise ValueError("El parametro 'tipo' debe ser 'lineal' o 'polinomial'")
    if grado < 1:
        raise ValueError("El grado debe ser mayor o igual a 1")
    
    X = np.array(X, dtype=float)
    y = np.array(y, dtype=float)
    
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    n_muestras, n_variables_originales = X.shape
    
    if tipo == 'polinomial' and grado > 1:
        X_b = generar_features_polinomiales(X, grado)
        n_predictores_reales = X_b.shape[1] - 1
    else:
        X_b = np.column_stack((np.ones(n_muestras), X))
        n_predictores_reales = n_variables_originales
    
    beta, residuos_sum, rank, s = np.linalg.lstsq(X_b, y, rcond=None)
    
    intercepto = beta[0]
    coeficientes = beta[1:]
    
    y_pred = X_b @ beta
    residuos = y - y_pred
    
    media_y = np.mean(y)
    varianza_y = np.var(y, ddof=1)
    desviacion_y = np.std(y, ddof=1)
    
    media_residuos = np.mean(residuos)
    varianza_residuos = np.var(residuos, ddof=1)
    desviacion_residuos = np.std(residuos, ddof=1)
    
    ss_tot = np.sum((y - media_y) ** 2)
    ss_res = np.sum(residuos ** 2)
    
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    
    if n_muestras > n_predictores_reales + 1:
        r2_ajustado = 1 - (1 - r2) * (n_muestras - 1) / (n_muestras - n_predictores_reales - 1)
    else:
        r2_ajustado = np.nan
    
    mse = np.mean(residuos ** 2)
    rmse = np.sqrt(mse)
    
    return {
        'tipo': tipo,
        'grado': grado if tipo == 'polinomial' else 1,
        'intercepto': intercepto,
        'coeficientes': coeficientes,
        'n_coeficientes': len(coeficientes),
        'y_pred': y_pred,
        'residuos': residuos,
        'n_muestras': n_muestras,
        'n_variables_originales': n_variables_originales,
        'n_predictores_reales': n_predictores_reales,
        'r2': r2,
        'r2_ajustado': r2_ajustado,
        'mse': mse,
        'rmse': rmse,
        'estadisticos_y': {'media': media_y, 'varianza': varianza_y, 'desviacion_estandar': desviacion_y},
        'estadisticos_residuos': {'media': media_residuos, 'varianza': varianza_residuos, 'desviacion_estandar': desviacion_residuos}
    }

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
st.set_page_config(
    page_title=t("page_title"),
    page_icon="📉",
    layout="wide"
)

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

st.markdown("""<style>...</style>""", unsafe_allow_html=True)

st.title(t("title"))
st.markdown("---")

# ============================================
# PROPÓSITO Y FUNDAMENTOS
# ============================================
st.header(t("purpose_header"))
st.markdown(t("purpose_text"))

st.header(t("fundamentals_header"))
st.markdown(t("fundamentals_text"))

st.markdown("---")

# ============================================
# CAPACIDADES
# ============================================
st.header(t("capabilities_header"))
st.markdown(t("capabilities_text"))

st.markdown("---")

# ============================================
# RESULTADOS Y MÉTRICAS
# ============================================
st.header(t("results_header"))

with st.expander(t("metrics_expander"), expanded=False):
    st.markdown(t("metrics_text"))

with st.expander(t("visualization_expander"), expanded=False):
    st.markdown(t("visualization_text"))

st.markdown("---")

# ============================================
# APLICACIONES
# ============================================
st.header(t("applications_header"))
st.markdown(t("applications_text"))

st.caption(t("caption"))

# ============================================================================
# CONFIGURACIÓN DEL MODELO (SIN BARRA LATERAL)
# ============================================================================

st.subheader(t("config_modelo"))

# Organización en columnas para la configuración
col_config1, col_config2, col_config3, col_config4 = st.columns(4)

with col_config1:
    metodo_entrada = st.radio(
        t("metodo_entrada"),
        t("metodo_entrada_opciones"),
        key="metodo_entrada"
    )

with col_config2:
    tipo_variables = st.radio(
        t("tipo_variables"),
        t("tipo_variables_opciones"),
        key="tipo_variables"
    )

with col_config3:
    tipo_modelo = st.selectbox(
        t("tipo_regresion"),
        t("tipo_regresion_opciones"),
        key="tipo_modelo"
    )

with col_config4:
    if tipo_modelo == t("tipo_regresion_polinomial"):
        grado = st.slider(
            t("grado_polinomio"),
            min_value=2, max_value=10, value=2,
            key="grado_polinomio"
        )
    else:
        grado = 1
        st.info(t("regresion_lineal_info"))

# Si es multivariable y entrada manual, permitir elegir cuantas X
num_variables_manual = 1
if tipo_variables == t("tipo_variables_multivariable") and metodo_entrada == t("metodo_entrada_manual"):
    st.markdown("---")
    col_extra1, col_extra2, col_extra3 = st.columns([1, 1, 1])
    with col_extra2:
        num_variables_manual = st.slider(
            t("num_variables_manual"),
            min_value=2, max_value=5, value=2,
            key="num_variables_manual"
        )

st.markdown("---")

# ============================================================================
# CARGA DE DATOS
# ============================================================================

df = None

if metodo_entrada == t("metodo_entrada_archivo"):
    st.header(t("cargar_datos_header"))
    
    archivo = st.file_uploader(t("subir_archivo"), type=['csv', 'xlsx', 'xls'])
    
    if archivo is not None:
        try:
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            st.success(t("archivo_cargado_ok") + archivo.name)
            st.write(t("vista_previa"))
            st.dataframe(df.head(10))
            
        except Exception as e:
            st.error(t("error_cargar_archivo") + str(e))

else:  # Entrada Manual
    st.header(t("entrada_manual_header"))
    
    col_n, col_empty = st.columns([1, 2])
    with col_n:
        num_muestras = st.number_input(
            t("num_muestras"),
            min_value=3, max_value=1000, value=20,
            key="num_muestras"
        )
    
    # Crear tabla editable según el tipo de variables
    if tipo_variables == t("tipo_variables_univariable"):
        columnas = ["X", "Y"]
    else:
        columnas = ["X" + str(i+1) for i in range(num_variables_manual)] + ["Y"]
    
    datos_iniciales = np.zeros((num_muestras, len(columnas)))
    df_manual = pd.DataFrame(datos_iniciales, columns=columnas)
    
    st.write(t("edita_tabla"))
    df = st.data_editor(df_manual, num_rows="dynamic", use_container_width=True)

# ============================================================================
# PROCESAMIENTO Y ANÁLISIS
# ============================================================================

if df is not None and not df.empty:
    st.markdown("---")
    st.header(t("seleccion_variables_header"))
    
    # Obtener columnas numéricas
    columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(columnas_numericas) < 2:
        st.error(t("error_min_columnas"))
    else:
        # =====================================================================
        # CASO UNIVARIABLE
        # =====================================================================
        if tipo_variables == t("tipo_variables_univariable"):
            col_x_sel, col_y_sel = st.columns(2)
            
            with col_x_sel:
                col_x = st.selectbox(t("var_indep"), columnas_numericas, index=0)
            
            # Filtrar Y para que no sea igual a X
            opciones_y = [c for c in columnas_numericas if c != col_x]
            if len(opciones_y) == 0:
                st.error(t("error_no_y"))
            else:
                with col_y_sel:
                    col_y = st.selectbox(t("var_dep"), opciones_y, index=0)
                
                X = df[col_x].values
                y = df[col_y].values
                
                # Ejecutar análisis AUTOMÁTICAMENTE (sin botón)
                tipo_regresion = 'polinomial' if tipo_modelo == t("tipo_regresion_polinomial") else 'lineal'
                resultados = analisis_minimos_cuadrados(X, y, tipo=tipo_regresion, grado=grado)
                
                # Mostrar resultados
                st.markdown("---")
                st.header(t("resultados_header"))
                
                # Métricas principales
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(t("r2"), "{:.4f}".format(resultados['r2']))
                col2.metric(t("r2_ajustado"), "{:.4f}".format(resultados['r2_ajustado']))
                col3.metric(t("rmse"), "{:.4f}".format(resultados['rmse']))
                col4.metric(t("mse"), "{:.4f}".format(resultados['mse']))
                
                st.markdown("---")
                
                # Coeficientes
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(t("coeficientes_subheader"))
                    st.write(t("intercepto").format(resultados['intercepto']))
                    
                    if tipo_modelo == t("tipo_regresion_polinomial"):
                        for i, coef in enumerate(resultados['coeficientes']):
                            st.write(t["coef_poli"].format(i+1, i+1, coef))
                    else:
                        st.write(t("coef_b1_x").format(resultados['coeficientes'][0]))
                
                with col2:
                    st.subheader(t("estadisticos_y"))
                    st.write(t("media_md").format(resultados['estadisticos_y']['media']))
                    st.write(t("varianza_md").format(resultados['estadisticos_y']['varianza']))
                    st.write(t("desv_est_md").format(resultados['estadisticos_y']['desviacion_estandar']))
                
                st.markdown("---")
                
                # Gráficas
                st.header(t("visualizacion_header"))
                
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
                
                # Gráfica de ajuste
                x_plot = np.linspace(X.min(), X.max(), 200)
                
                if tipo_modelo == t("tipo_regresion_polinomial"):
                    y_plot = resultados['intercepto'] * np.ones_like(x_plot)
                    for i, coef in enumerate(resultados['coeficientes']):
                        y_plot = y_plot + coef * (x_plot ** (i+1))
                else:
                    y_plot = resultados['intercepto'] + resultados['coeficientes'][0] * x_plot
                
                ax1.scatter(X, y, color='black', alpha=0.6, label=t("datos_reales"), zorder=5)
                ax1.plot(x_plot, y_plot, color='red', linewidth=2, 
                        label='{}{} (R²={:.3f})'.format(t("regresion_titulo"), tipo_modelo, resultados["r2"]))
                ax1.set_xlabel(col_x)
                ax1.set_ylabel(col_y)
                ax1.set_title(t("regresion_titulo") + tipo_modelo)
                ax1.legend()
                ax1.grid(True, alpha=0.3)
                
                # Gráfica de residuos
                ax2.scatter(resultados['y_pred'], resultados['residuos'], 
                           color='green', alpha=0.6)
                ax2.axhline(0, color='red', linestyle='--', linewidth=2)
                ax2.set_xlabel(t("valores_predichos"))
                ax2.set_ylabel(t("residuos"))
                ax2.set_title(t("grafico_residuos"))
                ax2.grid(True, alpha=0.3)
                
                plt.tight_layout()
                st.pyplot(fig)
                
                # Tabla de comparación
                st.markdown("---")
                st.subheader(t("comparacion_subheader"))
                df_comparacion = pd.DataFrame({
                    t("col_valor_real"): y,
                    t("col_valor_predicho"): resultados['y_pred'],
                    t("col_residuo"): resultados['residuos']
                })
                st.dataframe(df_comparacion, use_container_width=True)
                
                # Estadísticos de residuos
                st.markdown("---")
                st.subheader(t("estadisticos_residuos"))
                col1, col2, col3 = st.columns(3)
                col1.metric(t("media_residuos"), "{:.6f}".format(resultados['estadisticos_residuos']['media']))
                col2.metric(t("varianza"), "{:.4f}".format(resultados['estadisticos_residuos']['varianza']))
                col3.metric(t("desv_est"), "{:.4f}".format(resultados['estadisticos_residuos']['desviacion_estandar']))
                
        # =====================================================================
        # CASO MULTIVARIABLE
        # =====================================================================
        else:  # Multivariable
            st.info(t("info_multivariable"))
            
            # Seleccionar cuántas variables X quiere usar
            max_x_disponibles = len(columnas_numericas) - 1  # Al menos 1 para Y
            num_x_seleccionadas = st.slider(
                t("num_x_seleccionadas"),
                min_value=1, max_value=max_x_disponibles, 
                value=min(2, max_x_disponibles),
                key="num_x_seleccionadas"
            )
            
            # Seleccionar las columnas X
            cols_x = st.multiselect(
                t("cols_x"),
                columnas_numericas,
                default=columnas_numericas[:num_x_seleccionadas],
                key="cols_x_multivariable"
            )
            
            # Filtrar opciones para Y (que no estén en X)
            opciones_y = [c for c in columnas_numericas if c not in cols_x]
            
            if len(cols_x) == 0:
                st.warning(t("warning_min_x"))
            elif len(opciones_y) == 0:
                st.error(t("error_no_y_multi"))
            else:
                col_y = st.selectbox(t("var_dep"), opciones_y, index=0)
                
                # Ejecutar análisis AUTOMÁTICAMENTE (sin botón)
                X = df[cols_x].values
                y = df[col_y].values
                
                tipo_regresion = 'polinomial' if tipo_modelo == t["tipo_regresion_polinomial"] else 'lineal'
                resultados = analisis_minimos_cuadrados(X, y, tipo=tipo_regresion, grado=grado)
                
                # Mostrar resultados
                st.markdown("---")
                st.header(t("resultados_multi_header"))
                
                st.write(t("modelo_info").format(
                    tipo_modelo, ", ".join(cols_x), col_y))
                
                # Métricas principales
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(t("r2"), "{:.4f}".format(resultados['r2']))
                col2.metric(t("r2_ajustado"), "{:.4f}".format(resultados['r2_ajustado']))
                col3.metric(t("rmse"), "{:.4f}".format(resultados['rmse']))
                col4.metric(t("mse"), "{:.4f}".format(resultados['mse']))
                
                st.markdown("---")
                
                # Coeficientes
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(t("coeficientes_subheader"))
                    st.write(t("intercepto").format(resultados['intercepto']))
                    
                    if resultados['n_variables_originales'] == 1:
                        # Caso especial: multivariable seleccionado pero solo 1 X
                        if tipo_modelo == t["tipo_regresion_polinomial"]:
                            for i, coef in enumerate(resultados['coeficientes']):
                                st.write(t("coef_poli").format(i+1, i+1, coef))
                        else:
                            st.write(t("coef_b1_nombre").format(cols_x[0], resultados['coeficientes'][0]))
                    else:
                        # Caso multivariable real
                        if tipo_modelo == t("tipo_regresion_polinomial"):
                            # Mostrar los coeficientes con sus nombres
                            st.write(t("total_coeficientes").format(resultados['n_coeficientes']))
                            for i, coef in enumerate(resultados['coeficientes']):
                                st.write(t("coef_b").format(i+1, coef))
                        else:
                            # Lineal multivariable: mostrar cada variable con su coef
                            for i, col_nombre in enumerate(cols_x):
                                st.write(t["coef_b_nombre"].format(
                                    i+1, col_nombre, resultados['coeficientes'][i]))
                
                with col2:
                    st.subheader(t["estadisticos_y"])
                    st.write(t("media_md").format(resultados['estadisticos_y']['media']))
                    st.write(t("varianza_md").format(resultados['estadisticos_y']['varianza']))
                    st.write(t("desv_est_md").format(resultados['estadisticos_y']['desviacion_estandar']))
                
                st.markdown("---")
                
                # Gráficas para multivariable
                st.header(t("visualizacion_header"))
                
                # Gráfica 1: Valores reales vs predichos
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
                
                ax1.scatter(y, resultados['y_pred'], color='blue', alpha=0.6)
                min_val = min(y.min(), resultados['y_pred'].min())
                max_val = max(y.max(), resultados['y_pred'].max())
                ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, 
                        label=t("linea_perfecta"))
                ax1.set_xlabel(t("valores_reales_y"))
                ax1.set_ylabel(t("valores_predichos"))
                ax1.set_title(t("reales_vs_predichos").format(resultados['r2']))
                ax1.legend()
                ax1.grid(True, alpha=0.3)
                
                # Gráfica 2: Residuos
                ax2.scatter(resultados['y_pred'], resultados['residuos'], 
                           color='green', alpha=0.6)
                ax2.axhline(0, color='red', linestyle='--', linewidth=2)
                ax2.set_xlabel(t("valores_predichos"))
                ax2.set_ylabel(t("residuos"))
                ax2.set_title(t("grafico_residuos"))
                ax2.grid(True, alpha=0.3)
                
                plt.tight_layout()
                st.pyplot(fig)
                
                # Tabla de comparación
                st.markdown("---")
                st.subheader(t("comparacion_subheader"))
                df_comparacion = pd.DataFrame({
                    t("col_valor_real"): y,
                    t("col_valor_predicho"): resultados['y_pred'],
                    t("col_residuo"): resultados['residuos']
                })
                st.dataframe(df_comparacion, use_container_width=True)
                
                # Estadísticos de residuos
                st.markdown("---")
                st.subheader(t["estadisticos_residuos"])
                col1, col2, col3 = st.columns(3)
                col1.metric(t("media_residuos"), "{:.6f}".format(resultados['estadisticos_residuos']['media']))
                col2.metric(t("varianza"), "{:.4f}".format(resultados['estadisticos_residuos']['varianza']))
                col3.metric(t("desv_est"), "{:.4f}".format(resultados['estadisticos_residuos']['desviacion_estandar']))

else:
    st.info(t("info_carga_datos"))

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption(t("footer"))