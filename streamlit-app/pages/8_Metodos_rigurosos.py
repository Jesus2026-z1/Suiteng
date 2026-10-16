import streamlit as st
import pandas as pd
import numpy as np
from utils.metodos_rigurosos import columna_multicomponente
from utils.i18n import language_selector
from languages.met_rigurosos_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()

# ... (carga de datos y selección de componentes igual) ...
# ---------- 1. Carga de datos ----------
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv(r'C:\Users\varia\OneDrive\Documentos\Database\data.csv')
        df_filtrado = df.iloc[4:,[1,2,5,6,9,2,21,22,23]]
        df_filtrado.columns = ['Componente', 'Composición_inicial', 'Tc', 'Pc', 'Omega', 'PM', 'A', 'B', 'C']
        for col in ['Composición_inicial', 'Tc', 'Pc', 'Omega', 'PM', 'A', 'B', 'C']:
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

import streamlit as st

st.set_page_config(
    page_title=t("page_title"),
    page_icon="🏭",
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

with st.expander(t("convergence_expander_title"), expanded=False):
    st.markdown(t("convergence_expander_text"))

with st.expander(t("composition_expander_title"), expanded=False):
    st.markdown(t("composition_expander_text"))

with st.expander(t("download_expander_title"), expanded=False):
    st.markdown(t("download_expander_text"))

st.markdown("---")

# ============================================
# FLUJO DE TRABAJO SUGERIDO
# ============================================
st.header(t("workflow_header"))
st.markdown(t("workflow_text"))

st.caption(t("caption"))

st.header(t("config_header"))

# ---------- Inicialización del estado ----------
if 'tabla' not in st.session_state:
    st.session_state.tabla = pd.DataFrame(columns=['Componente', 'Composición', 'Tc', 'Pc', 'Omega', 'PM', 'A', 'B', 'C'])

if 'df_completo' not in st.session_state:
    st.session_state.df_completo = cargar_datos()

# ---------- Selección de componentes ----------
with st.container(border=True):
    st.subheader(t("col_components_header"))
    col1, col2 = st.columns(2)
    with col1:
        opciones = st.session_state.df_completo['Componente'].tolist()
        seleccionado = st.selectbox(t("col_select_component"), opciones, index=None, placeholder=t("col_components_placeholder"))
        if st.button(t("col_select_button")):
            fila = st.session_state.df_completo[st.session_state.df_completo['Componente'] == seleccionado]
            if not fila.empty:
                nueva_fila = pd.DataFrame({
                    'Componente': [seleccionado],
                    'Composición': [0.0],
                    'Tc': [fila['Tc'].values[0]],
                    'Pc': [fila['Pc'].values[0]],
                    'Omega': [fila['Omega'].values[0]],
                    'PM': [fila['PM'].values[0]],
                    'A': [fila['A'].values[0]],
                    'B': [fila['B'].values[0]],
                    'C': [fila['C'].values[0]],
                })
                st.session_state.tabla = pd.concat([st.session_state.tabla, nueva_fila], ignore_index=True)

        if not st.session_state.tabla.empty:
            opciones_eliminar = [f"{i} - {row['Componente']}" for i, row in st.session_state.tabla.iterrows()]
            seleccion_eliminar = st.selectbox(t("col_select_row_delete"), opciones_eliminar)
            if st.button(t("col_delete_button")):
                indice = int(seleccion_eliminar.split(" - ")[0])
                st.session_state.tabla = st.session_state.tabla.drop(indice).reset_index(drop=True)
                st.rerun()
        else:
            st.info(t("col_no_components"))

    with col2:
        st.write(t("col_selected_components"))
        tabla_editada = st.data_editor(
            st.session_state.tabla,
            num_rows="fixed",
            column_order=["Componente", "Composición"],
            column_config={
                "Componente": st.column_config.TextColumn(t("col_component_col"), disabled=True),
                "Composición": st.column_config.NumberColumn(t("col_fraction_col"), format="%.4f", min_value=0.00, max_value=1.00),
            },
            key="editor_tabla"
        )
        st.session_state.tabla = tabla_editada

# ---------- Condiciones de operación y modelo ----------
with st.container(border=True):
    st.write(t("col_operating_conditions"))
    col3, col4 = st.columns(2)
    with col3:
        presion = st.number_input(t("col_pressure"), value=1.0, step=0.1)
        P_bar = presion
        P_mmHg = presion * 750.1875
        P_atm = presion / 1.01325
        temperatura = st.number_input(t("col_temperature"), value=25.0)
        T_K = temperatura + 273.15

    with col4:
        modelo = st.selectbox(t("col_select_model"),
                              ("Antoine"), # , "RK", "SRK", "PR"
                              index=0)
        st.write(t("col_model_selected").format(modelo))

# ---------- Parámetros de la columna ----------
with st.container(border=True):
    st.write(t("col_column_params_header"))
    col7, col8 = st.columns(2)
    with col7:
        numEtapas = st.number_input(t("col_num_stages"), value=10, step=1, min_value=2)
        etapaAlimentacion = st.number_input(t("col_feed_stage"), value=5, step=1, min_value=1, max_value=numEtapas-1)
        flujoMol = st.number_input(t("col_feed_molar_flow"), value=100.0)

    with col8:
        flujoDestilado = st.number_input(t("col_distillate"), value=35.0)
        refExterno = st.number_input(t("col_external_reflux"), value=70.0)

        if st.button(t("col_run_simulation_button"), type="primary"):
            if st.session_state.tabla.empty:
                st.error(t("col_error_no_components"))
            else:
                comp_names = st.session_state.tabla['Componente'].tolist()
                z = st.session_state.tabla['Composición'].tolist()
                if abs(sum(z) - 1.0) > 1e-4:
                    z = np.array(z) / np.sum(z)
                    st.session_state.tabla['Composición'] = z
                    st.warning(t("col_warning_normalized"))
                z = z.tolist() if isinstance(z, np.ndarray) else z

                A_list = st.session_state.tabla['A'].tolist()
                B_list = st.session_state.tabla['B'].tolist()
                C_list = st.session_state.tabla['C'].tolist()
                Tc_list = st.session_state.tabla['Tc'].tolist()
                Pc_list = st.session_state.tabla['Pc'].tolist()  # bar
                omega_list = st.session_state.tabla['Omega'].tolist()

                # Seleccionar presión según modelo
                if modelo == "Antoine":
                    P_uso = P_mmHg
                else:
                    P_uso = P_bar  # EOS usan bar

                progress_bar = st.progress(0, text=t("col_progress_starting"))
                status_text = st.empty()

                def actualizar(progreso, mensaje):
                    progress_bar.progress(progreso, text=mensaje)
                    status_text.text(mensaje)

                with st.spinner(t("col_spinner_calculating")):
                    resultado = columna_multicomponente(
                        int(numEtapas),
                        int(etapaAlimentacion),
                        flujoMol,
                        z,
                        flujoDestilado,
                        refExterno,
                        P_uso,
                        A_list,
                        B_list,
                        C_list,
                        comp_names,
                        modelo=modelo,
                        Tc_list=Tc_list,
                        Pc_list=Pc_list,
                        omega_list=omega_list,
                        tol=1e-3,
                        max_iter=100,
                        progress_callback=actualizar
                    )

                progress_bar.empty()
                status_text.empty()

                try:
                    st.success(t("col_success_simulation").format(resultado['iteraciones'], resultado['error_final']))

                    df_perfiles = pd.DataFrame({
                        t("col_stage_col"): list(range(1, numEtapas+1)),
                        'T (K)': resultado['perfil_T'],
                    })
                    for j, comp in enumerate(comp_names):
                        df_perfiles[f'x_{comp}'] = resultado['perfil_x'][:, j]
                        df_perfiles[f'y_{comp}'] = resultado['perfil_y'][:, j]
                    df_perfiles['L (kmol/h)'] = resultado['perfil_L']
                    df_perfiles['V (kmol/h)'] = resultado['perfil_V']

                    st.data_editor(df_perfiles, use_container_width=True)

                    csv = df_perfiles.to_csv(index=False)
                    st.download_button(t("col_download_csv"), csv, "perfiles_columna.csv", "text/csv")
                except Exception as e:
                    st.error(t("col_error_display_results").format(e))