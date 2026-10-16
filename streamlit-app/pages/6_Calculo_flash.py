import streamlit as st
import pandas as pd
import numpy as np
from utils.eqstate import *          # necesario para los modelos
from utils.flash import flash, relative_volatility   # nuevo módulo
from utils.i18n import language_selector
from languages.flash_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()

# ---------- 1. Carga de datos ----------
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv(r'C:\Users\varia\OneDrive\Documentos\Database\data.csv')
        df_filtrado = df.iloc[4:,[1,2,5,6,9,2]]
        df_filtrado.columns = ['Componente', 'Composición_inicial', 'Tc', 'Pc', 'Omega', 'PM']
        for col in ['Composición_inicial', 'Tc', 'Pc', 'Omega', 'PM']:
            df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0.0)
        return df_filtrado
    except FileNotFoundError:
        return pd.DataFrame({
            'Componente': ['A', 'B', 'C', 'D'],
            'Composición_inicial': [0.0, 0.0, 0.0, 0.0],
            'Tc': [10, 20, 30, 40],
            'Pc': [100, 200, 300, 400],
            'Omega': [1, 2, 3, 4],
            'PM': [1, 2, 3, 4],
        })

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
    page_icon="💧",
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
st.header(t("outputs_header"))

with st.expander(t("status_expander_title"), expanded=False):
    st.markdown(t("status_text"))

with st.expander(t("table_expander_title"), expanded=False):
    st.markdown(t("table_text"))

st.markdown("---")

# ============================================
# ALCANCE Y APLICABILIDAD
# ============================================
st.header(t("scope_header"))
st.markdown(t("scope_text"))

st.caption(t("caption"))

st.header(t("config_header"))

# ---------- 2. Inicialización del estado ----------
if 'tabla' not in st.session_state:
    st.session_state.tabla = pd.DataFrame(columns=['Componente', 'Composición', 'Tc', 'Pc', 'Omega', 'PM'])

if 'df_completo' not in st.session_state:
    st.session_state.df_completo = cargar_datos()

# Variables para resultados (se usarán después)
if 'resultados_flash' not in st.session_state:
    st.session_state.resultados_flash = None
if 'beta_flash' not in st.session_state:
    st.session_state.beta_flash = None

# Contenedor para selección de componentes
with st.container(border=True):
    st.subheader(t("flash_components_header"))
    col1, col2 = st.columns(2)
    with col1:
        opciones = st.session_state.df_completo['Componente'].tolist()
        seleccionado = st.selectbox(t("flash_select_component"), opciones, index=None, placeholder=t("flash_components_placeholder"))

        if st.button(t("flash_select_button")):
            fila = st.session_state.df_completo[st.session_state.df_completo['Componente'] == seleccionado]
            if not fila.empty:
                tc = fila['Tc'].values[0]
                pc = fila['Pc'].values[0]
                omega = fila['Omega'].values[0]
                pm = fila['PM'].values[0]
                nueva_fila = pd.DataFrame({
                    'Componente': [seleccionado],
                    'Composición': [0.0],
                    'Tc': [tc],
                    'Pc': [pc],
                    'Omega': [omega],
                    'PM': [pm],
                })
                st.session_state.tabla = pd.concat([st.session_state.tabla, nueva_fila], ignore_index=True)

        if not st.session_state.tabla.empty:
            opciones_eliminar = [f"{i} - {row['Componente']}" for i, row in st.session_state.tabla.iterrows()]
            seleccion_eliminar = st.selectbox(t("flash_select_row_delete"), opciones_eliminar)
            if st.button(t("flash_delete_button")):
                indice = int(seleccion_eliminar.split(" - ")[0])
                st.session_state.tabla = st.session_state.tabla.drop(indice).reset_index(drop=True)
                st.rerun()
        else:
            st.info(t("flash_no_components"))

    with col2:
        st.write(t("flash_selected_components"))
        tabla_editada = st.data_editor(
            st.session_state.tabla,
            num_rows="fixed",
            column_order=["Componente", "Composición"],
            column_config={
                "Componente": st.column_config.TextColumn(t("flash_component_col"), disabled=True),
                "Composición": st.column_config.NumberColumn(t("flash_fraction_col"), format="%.4f", min_value=0.00, max_value=1.00),
            },
            key="editor_tabla"
        )
        st.session_state.tabla = tabla_editada

# Introducción de condiciones de operación y modelo
with st.container(border=True):
    st.write(t("flash_operating_conditions"))
    col3, col4 = st.columns(2)
    with col3:
        presion = st.number_input(t("flash_pressure"), value=1.0, min_value=0.0, step=0.1)
        temperatura = st.number_input(t("flash_temperature"), value=25.0, min_value=-273.15, step=0.1)

    with col4:
        modelo = st.selectbox(
            t("flash_select_model"),
            ("REDLICH-KWONG", "SOAVE-REDLICH-KWONG", "PENG-ROBINSON"),
            index=None,
            placeholder=t("flash_models_placeholder"),
        )
        if modelo == 'REDLICH-KWONG':
            st.write(t("flash_rk_selected"))
        elif modelo == 'SOAVE-REDLICH-KWONG':
            st.write(t("flash_srk_selected"))
        elif modelo == 'PENG-ROBINSON':
            st.write(t("flash_pr_selected"))
        else:
            st.info(t("flash_no_model_selected"))

    # Botón para ejecutar el flash
    if st.button(t("flash_calculate_button")):
        # Validaciones
        errores = []
        if st.session_state.tabla.empty:
            errores.append(t("flash_error_no_components"))
        if modelo is None:
            errores.append(t("flash_error_no_model"))
        if presion <= 0:
            errores.append(t("flash_error_pressure"))
        if temperatura <= -273.15:
            errores.append(t("flash_error_temperature"))

        if errores:
            for err in errores:
                st.error(err)
            st.session_state.resultados_flash = None
            st.session_state.beta_flash = None
        else:
            # Preparar datos (presión en bar)
            y = st.session_state.tabla['Composición'].values
            Tc = st.session_state.tabla['Tc'].values
            Pc = st.session_state.tabla['Pc'].values * 1.01325   # convertir a bar (si el csv está en atm)
            omega = st.session_state.tabla['Omega'].values
            nombre = st.session_state.tabla['Componente'].tolist()
            T = temperatura + 273.15
            P = presion   # bar

            try:
                beta, x_liquido, y_vapor, K, it = flash(T, P, y, Tc, Pc, omega, modelo=modelo, kij=None)
                # Guardar resultados en session_state
                df_res = pd.DataFrame({
                    t("flash_component_col"): nombre,
                    t("flash_col_k"): K,
                    t("flash_col_x_liquid"): x_liquido if x_liquido is not None else np.nan,
                    t("flash_col_y_vapor"): y_vapor if y_vapor is not None else np.nan
                })
                st.session_state.resultados_flash = df_res
                st.session_state.beta_flash = beta
                st.success(t("flash_success").format(beta))
            except Exception as e:
                st.error(t("flash_error_calc").format(e))
                st.session_state.resultados_flash = None
                st.session_state.beta_flash = None

# Mostrar resultados si existen
st.write(t("flash_header"))
if st.session_state.resultados_flash is not None:
    st.data_editor(st.session_state.resultados_flash)
    st.write(t("flash_beta").format(st.session_state.beta_flash))
else:
    st.info(t("flash_no_results"))