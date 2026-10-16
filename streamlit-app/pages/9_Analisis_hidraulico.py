import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go
from utils.analisis_hidraulico import calcular_analisis_hidraulico, convertir_presion
from utils.i18n import language_selector
from languages.hidraulico_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()

st.set_page_config(layout="wide")
# st.title('Análisis Hidráulicos')

# ============================================================
# 1. Carga de datos (rutas absolutas, ajústalas según tu entorno)
# ============================================================
@st.cache_data
def diametro_nominal(diametro, cedula):
    df1 = pd.read_excel('dababase\diametro.xlsx')
    df1.columns = df1.columns.str.strip()
    try:
        valor = df1.loc[df1['DIAMETRO'] == diametro, cedula].values[0]
        return valor
    except IndexError:
        return f"Diámetro {diametro} no encontrado"
    except KeyError:
        return f"Accesorio '{cedula}' no válido. Columnas disponibles: {list(df1.columns)}"

@st.cache_data
def longitud_equivalente(diametro, accesorio):
    df = pd.read_csv('dababase\equiv.csv')
    df.columns = df.columns.str.strip()
    try:
        valor = df.loc[df['DIAMETRO'] == diametro, accesorio].values[0]
        return valor
    except IndexError:
        return f"Diámetro {diametro} no encontrado"
    except KeyError:
        return f"Accesorio '{accesorio}' no válido. Columnas disponibles: {list(df.columns)}"

@st.cache_data
def columnas():
    df = pd.read_excel(r'C:\Users\varia\OneDrive\Documentos\Accesorios\columnas.xlsx')
    df.dropna(inplace=True, how='all')
    df.columns = df.columns.str.strip()
    return df

# Configuración de la página
st.set_page_config(
    page_title=t("page_title"),
    page_icon="🔧",
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

# Título principal
st.title(t("title"))
st.markdown("---")

# ============================================
# 1. PROPÓSITO Y FUNDAMENTOS
# ============================================
# with st.expander("📘 Propósito y Fundamentos Teóricos", expanded=True):
st.header(t("purpose_header"))
st.markdown(t("purpose_text"))    

# ============================================
# 2. VARIABLES DE ENTRADA
# ============================================
st.markdown("---")
st.header(t("inputs_header"))

st.subheader(t("inputs_subheader_A"))
st.markdown(t("inputs_text_A"))

st.subheader(t("inputs_subheader_B"))
st.markdown(t("inputs_text_B"))

# ============================================
# 3. RESULTADOS ESPERADOS
# ============================================
st.markdown("---")
st.header(t("results_header"))

with st.expander(t("summary_expander_title"), expanded=False):
    st.markdown(t("summary_expander_text"))

with st.expander(t("detail_expander_title"), expanded=False):
    st.markdown(t("detail_expander_text"))

with st.expander(t("graphics_expander_title"), expanded=False):
    st.markdown(t("graphics_expander_text"))

# ============================================
# 4. FLUJO DE TRABAJO SUGERIDO
# ============================================
st.markdown("---")
st.header(t("workflow_header"))
st.markdown(t("workflow_text"))

st.caption(t("caption"))

st.header(t("config_header"))

# ============================================================
# 2. Inicialización del estado
# ============================================================
if 'tabla_entrada' not in st.session_state:
    st.session_state.tabla_entrada = pd.DataFrame(columns=[
        'Número de Línea', 'Diámetro', 'Cédula', 'Longitud', 'Accesorio', 'Elevación', 'Flujo adicional'
    ])

if 'column' not in st.session_state:
    st.session_state.column = columnas()

if 'resultados' not in st.session_state:
    st.session_state.resultados = None

# Opciones para selects
opcion1 = st.session_state.column['DIAMETRO'].to_list()
opcion2 = st.session_state.column['ACCESORIO'].to_list()
opcion3 = st.session_state.column['CEDULA'].to_list()

# ============================================================
# 3. Selector de sistema de unidades
# ============================================================
sistema = st.radio(t("hyd_unit_system"), [t("hyd_unit_imperial"), t("hyd_unit_si")], horizontal=True, index=0)

# ============================================================
# 4. Condiciones de operación y propiedades del fluido
# ============================================================
with st.container(border=True):
    st.write(t("hyd_fluid_props_header"))
    colFlu, colOp = st.columns(2)
    with colFlu:
        if sistema == t("hyd_unit_imperial"):
            flujovolum = st.number_input(t("hyd_volumetric_flow_ft3h"), value=0.0, step=0.1)
            desidad = st.number_input(t("hyd_density_lbft3"), value=0.0, step=0.1)
            viscosidad = st.number_input(t("hyd_viscosity_stokes"), value=0.0, step=0.01)
        else:  # SI
            flujovolum = st.number_input(t("hyd_volumetric_flow_m3h"), value=0.0, step=0.1)
            desidad = st.number_input(t("hyd_density_kgm3"), value=0.0, step=0.1)
            viscosidad = st.number_input(t("hyd_viscosity_cst"), value=0.0, step=0.01)
    with colOp:
        if sistema == t("hyd_unit_imperial"):
            presion = st.number_input(t("hyd_pressure_psi"), value=0.0, step=0.1)
            temperatura = st.number_input(t("hyd_temperature_f"), value=0.0, step=0.1)
        else:
            presion = st.number_input(t("hyd_pressure_kpa"), value=0.0, step=0.1)
            temperatura = st.number_input(t("hyd_temperature_c"), value=0.0, step=0.1)

# ============================================================
# 5. Modelo: entrada de datos y tabla editable
# ============================================================
with st.container(border=True):
    st.write(t("hyd_build_model_header"))
    coltub, colacc = st.columns(2)
    with coltub:
        numlinea = st.number_input(t("hyd_line_number"))
        if sistema == t("hyd_unit_imperial"):
            longitudlinea = st.number_input(t("hyd_length_ft"), value=0.0, step=0.1, key='longitud')
            diametros = st.selectbox(t("hyd_diameter_in"), opcion1, placeholder=t("hyd_diameter_placeholder"), key='diam')
        else:
            longitudlinea = st.number_input(t("hyd_length_m"), value=0.0, step=0.1, key='longitud')
            diametros = st.selectbox(t("hyd_diameter_mm"), opcion1, placeholder=t("hyd_diameter_placeholder"), key='diam')
    with colacc:
        accesorios = st.selectbox(t("hyd_accessories"), opcion2, placeholder=t("hyd_accessories_placeholder"), key='acc')
        cedulas = st.selectbox(t("hyd_schedule"), opcion3, placeholder=t("hyd_schedule_placeholder"), key='ced')
        if sistema == t("hyd_unit_imperial"):
            elevacion = st.number_input(t("hyd_elevation_ft"), value=0.0, step=0.1, key='elev')
            flujo_adicional = st.number_input(t("hyd_additional_flow_ft3h"), value=0.0, step=0.1, key='flujo_adic')
        else:
            elevacion = st.number_input(t("hyd_elevation_m"), value=0.0, step=0.1, key='elev')
            flujo_adicional = st.number_input(t("hyd_additional_flow_m3h"), value=0.0, step=0.1, key='flujo_adic')

    # Botón agregar fila
    if st.button(t("hyd_add_row_button")):
        if not numlinea:
            st.warning(t("hyd_warn_line_number"))
        elif longitudlinea == 0.0:
            st.warning(t("hyd_warn_length"))
        elif not diametros or diametros == t("hyd_diameter_placeholder"):
            st.warning(t("hyd_warn_diameter"))
        elif not accesorios or accesorios == t("hyd_accessories"):
            st.warning(t("hyd_warn_accessory"))
        elif not cedulas or cedulas == t("hyd_schedule"):
            st.warning(t("hyd_warn_schedule"))
        else:
            nueva_fila = pd.DataFrame({
                'Número de Línea': [numlinea],
                'Diámetro': [diametros],
                'Cédula': [cedulas],
                'Longitud': [longitudlinea],
                'Accesorio': [accesorios],
                'Elevación': [elevacion],
                'Flujo adicional': [flujo_adicional]
            })
            st.session_state.tabla_entrada = pd.concat(
                [st.session_state.tabla_entrada, nueva_fila], ignore_index=True
            )
            st.success(t("hyd_success_row_added"))

# ============================================================
# 6. Mostrar tabla de entrada editable
# ============================================================
st.write(t("hyd_lines_table_header"))
if not st.session_state.tabla_entrada.empty:
    if 'Flujo adicional' not in st.session_state.tabla_entrada.columns:
        st.session_state.tabla_entrada['Flujo adicional'] = 0.0
    edited_df = st.data_editor(
        st.session_state.tabla_entrada,
        use_container_width=True,
        num_rows="dynamic",
        key='editor_entrada'
    )
    st.session_state.tabla_entrada = edited_df
else:
    st.info(t("hyd_info_add_lines"))

# ============================================================
# 7. Selector de unidad de presión para resultados
# ============================================================
unidades_presion = ["psi", "kPa", "Pa", "kg/cm²", "bar"]
unidad_presion_salida = st.selectbox(
    t("hyd_pressure_unit_selector"),
    unidades_presion,
    index=0,
    help=t("hyd_pressure_unit_help")
)

# ============================================================
# 8. Botón de cálculo
# ============================================================
if st.button(t("hyd_calc_button")):
    df = st.session_state.tabla_entrada.copy()
    if df.empty:
        st.warning(t("hyd_warn_no_lines"))
    else:
        # Llamar a la función de cálculo
        resultado = calcular_analisis_hidraulico(
            df=df,
            sistema=sistema,
            flujovolum=flujovolum,
            desidad=desidad,
            viscosidad=viscosidad,
            presion=presion,
            diametro_nominal_func=diametro_nominal,
            longitud_equivalente_func=longitud_equivalente,
            unidad_presion_salida=unidad_presion_salida
        )
        
        # Verificar si hubo error
        if isinstance(resultado[0], str):
            st.error(resultado[0])
        else:
            df_resultados, P_out, long_acum, presion_nodos, elevacion_nodos, P_in = resultado
            
            # Almacenar resultados en session_state
            st.session_state.resultados = df_resultados
            st.session_state.long_acum = long_acum
            st.session_state.presion_nodos = presion_nodos
            st.session_state.elevacion_nodos = elevacion_nodos
            st.session_state.P_in = P_in
            st.session_state.P_out = P_out
            st.session_state.unidad_presion = unidad_presion_salida
            st.session_state.sistema = sistema
            
            st.success(t("hyd_success_calc"))

# ============================================================
# 9. Mostrar resultados (si existen)
# ============================================================
if st.session_state.resultados is not None:
    st.write(t("hyd_results_header"))
    st.dataframe(st.session_state.resultados, use_container_width=True)

    # Métricas
    col1, col2, col3 = st.columns(3)
    unidad = st.session_state.unidad_presion
    with col1:
        st.metric(t("hyd_metric_inlet_pressure"), f"{st.session_state.P_in:.2f} {unidad}")
    with col2:
        st.metric(t("hyd_metric_outlet_pressure"), f"{st.session_state.P_out:.2f} {unidad}")
    with col3:
        st.metric(t("hyd_metric_total_drop"), f"{st.session_state.P_in - st.session_state.P_out:.2f} {unidad}")

    # ============================================================
    # 10. Gráficas (Plotly)
    # ============================================================
    st.write(t("hyd_profiles_header"))

    long = st.session_state.long_acum
    elev = st.session_state.elevacion_nodos
    pres = st.session_state.presion_nodos

    # Gráfica 1: Elevación vs Longitud
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=long, y=elev,
        mode='lines+markers',
        name=t("hyd_elevation_trace"),
        line=dict(color='green', width=2),
        marker=dict(size=8)
    ))
    fig1.update_layout(
        title=t("hyd_elevation_profile_title"),
        xaxis_title=t("hyd_axis_cumulative_length_m") if sistema == t("hyd_unit_si") else t("hyd_axis_cumulative_length_ft"),
        yaxis_title=t("hyd_axis_elevation_m") if sistema == t("hyd_unit_si") else t("hyd_axis_elevation_ft"),
        template='plotly_white'
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfica 2: Presión vs Longitud
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=long, y=pres,
        mode='lines+markers',
        name=t("hyd_pressure_trace"),
        line=dict(color='red', width=2),
        marker=dict(size=8)
    ))
    fig2.update_layout(
        title=t("hyd_pressure_profile_title"),
        xaxis_title=t("hyd_axis_cumulative_length_m") if sistema == t("hyd_unit_si") else t("hyd_axis_cumulative_length_ft"),
        yaxis_title=t("hyd_axis_pressure").format(unidad),
        template='plotly_white'
    )
    st.plotly_chart(fig2, use_container_width=True)