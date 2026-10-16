import streamlit as st
import pandas as pd
from utils.eqstate import *
from utils.flash import *
from utils.metodos_cortos import *
from utils.i18n import language_selector
from languages.met_cortos_translate import init_lang, t, tw
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

# ---------- 2. Inicialización del estado ----------
if 'tabla' not in st.session_state:
    st.session_state.tabla = pd.DataFrame(columns=['Componente', 'Composición', 'Tc', 'Pc', 'Omega', 'PM'])

if 'df_completo' not in st.session_state:
    st.session_state.df_completo = cargar_datos()

# Variables para resultados (se definen fuera para que existan siempre)
tabla1 = None
tabla2 = None

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
    page_icon="⚗️",
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

with st.expander(t("global_params_expander_title"), expanded=False):
    st.markdown(t("global_params_text"))

with st.expander(t("material_balance_expander_title"), expanded=False):
    st.markdown(t("material_balance_text"))

st.markdown("---")

# ============================================
# FLUJO DE TRABAJO SUGERIDO
# ============================================
st.header(t("workflow_header"))
st.markdown(t("workflow_text"))

st.caption(t("caption"))

st.header(t("config_header"))

# Contenedor para selección de componentes
with st.container(border=True):
    st.subheader(t("sep_components_header"))
    col1, col2 = st.columns(2)
    with col1:
        opciones = st.session_state.df_completo['Componente'].tolist()
        seleccionado = st.selectbox(t("sep_select_component"), opciones, index=None, placeholder=t("sep_components_placeholder"))

        if st.button(t("sep_select_button")):
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
            seleccion_eliminar = st.selectbox(t("sep_select_row_delete"), opciones_eliminar)
            if st.button(t("sep_delete_button")):
                indice = int(seleccion_eliminar.split(" - ")[0])
                st.session_state.tabla = st.session_state.tabla.drop(indice).reset_index(drop=True)
                st.rerun()
        else:
            st.info(t("sep_no_components"))

    with col2:
        st.write(t("sep_selected_components"))
        tabla_editada = st.data_editor(
            st.session_state.tabla,
            num_rows="fixed",
            column_order=["Componente", "Composición"],
            column_config={
                "Componente": st.column_config.TextColumn(t("sep_component_col"), disabled=True),
                "Composición": st.column_config.NumberColumn(t("sep_fraction_col"), format="%.4f", min_value=0.00, max_value=1.00),
            },
            key="editor_tabla"
        )
        st.session_state.tabla = tabla_editada

# Introducción de condiciones de operación (Presión de operación, Temperatura de operación)
with st.container(border=True):
    st.write(t("sep_operating_conditions"))
    col3, col4 = st.columns(2)
    with col3:
        presion = st.number_input(t("sep_pressure"), value=1.0, min_value=0.0, step=0.1)
        temperatura = st.number_input(t("sep_temperature"), value=25.0, min_value=-273.15, step=0.1)
    with col4:
        modelo = st.selectbox(
            t("sep_select_model"),
            ("REDLICH-KWONG", "SOAVE-REDLICH-KWONG", "PENG-ROBINSON"),
            index=None,
            placeholder=t("sep_models_placeholder"),
        )
        if modelo == 'REDLICH-KWONG':
            st.write(t("sep_rk_selected"))
        elif modelo == 'SOAVE-REDLICH-KWONG':
            st.write(t("sep_srk_selected"))
        elif modelo == 'PENG-ROBINSON':
            st.write(t("sep_pr_selected"))
        else:
            st.info(t("sep_no_model_selected"))

# Selección de componentes clave para la separación
with st.container(border=True):
    st.write(t("sep_keys_header"))
    col7, col8 = st.columns(2)
    with col7:
        if not st.session_state.tabla.empty:
            nombre = st.session_state.tabla['Componente'].tolist()
            lk_idx = st.selectbox(t("sep_light_key"), options=range(len(nombre)), format_func=lambda i: nombre[i])
            hk_idx = st.selectbox(t("sep_heavy_key"), options=range(len(nombre)), format_func=lambda i: nombre[i])
            if lk_idx == hk_idx:
                st.error(t("sep_keys_must_differ"))
        else:
            st.warning(t("sep_add_component_warning"))
            lk_idx = hk_idx = None

    with col8:
        rec_LK = st.number_input(t("sep_rec_lk"), min_value=0.0, max_value=1.0, value=0.99, step=0.01)
        rec_HK = st.number_input(t("sep_rec_hk"), min_value=0.0, max_value=1.0, value=0.99, step=0.01)
        R_factor = st.number_input(t("sep_reflux_factor"), value=1.5, min_value=1.0, step=0.1)

        if st.button(t("sep_run_button")):
            # Validaciones previas
            errores = []
            if st.session_state.tabla.empty:
                errores.append(t("sep_error_no_components"))
            if modelo is None:
                errores.append(t("sep_error_no_model"))
            if presion <= 0:
                errores.append(t("sep_error_pressure"))
            if temperatura <= -273.15:
                errores.append(t("sep_error_temperature"))
            if lk_idx is None or hk_idx is None:
                errores.append(t("sep_error_select_keys"))
            if lk_idx == hk_idx:
                errores.append(t("sep_error_keys_differ"))

            if errores:
                for err in errores:
                    st.error(err)
            else:
                # Preparar datos (unidades: bar)
                y = st.session_state.tabla['Composición'].values
                Tc = st.session_state.tabla['Tc'].values
                Pc = st.session_state.tabla['Pc'].values * 1.01325   # convertir a bar (si el csv está en atm)
                omega = st.session_state.tabla['Omega'].values
                nombre = st.session_state.tabla['Componente'].tolist()
                T = temperatura + 273.15
                P = presion   # bar

                # Calcular flash y constantes K con el modelo seleccionado
                try:
                    beta, x_liquido, y_vapor, K, it = flash(T, P, y, Tc, Pc, omega, modelo=modelo, kij=None)
                    alpha = relative_volatility(K)
                except Exception as e:
                    st.error(t("sep_error_flash").format(e))
                    st.stop()

                # Verificar que alpha tenga valores positivos
                if any(a <= 0 for a in alpha):
                    st.error(t("sep_error_alpha"))
                else:
                    # Llamar a design_column
                    try:
                        res = design_column(
                            componentes=nombre,
                            alpha=alpha,
                            zF=y,
                            q=1.0,  # líquido saturado por defecto
                            LK_index=lk_idx,
                            HK_index=hk_idx,
                            rec_LK=rec_LK,
                            rec_HK=rec_HK,
                            R_factor=R_factor,
                            F_total=1.0
                        )
                        # Mostrar resultados
                        st.write(t("sep_design_results"))
                        tabla1 = pd.DataFrame({
                            t("sep_col_n_min"): [res['N_min']],
                            t("sep_col_n_actual"): [res['N_actual']],
                            t("sep_col_r_min"): [res['R_min']],
                            t("sep_col_r_actual"): [res['R_actual']],
                            t("sep_col_theta"): [res['theta']],
                            t("sep_col_n_r"): [res['N_R']],
                            t("sep_col_n_s"): [res['N_S']],
                        })
                        tabla2 = pd.DataFrame({
                            t("sep_col_component"): nombre,
                            t("sep_col_d"): res['d'],
                            t("sep_col_b"): res['b'],
                            t("sep_col_d_lower"): res['d'],
                            t("sep_col_b_lower"): res['b'],
                            t("sep_col_xd"): res['xD'],
                            t("sep_col_xb"): res['xB'],
                        })
                        st.session_state.tabla1 = tabla1
                        st.session_state.tabla2 = tabla2
                    except Exception as e:
                        st.error(t("sep_error_design").format(e))

# Mostrar tablas de resultados si existen
if 'tabla1' in st.session_state:
    st.data_editor(st.session_state.tabla1)
if 'tabla2' in st.session_state:
    st.data_editor(st.session_state.tabla2)