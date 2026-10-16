import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go
from utils.hidraulica_antifuego import calcular_analisis_antifuego, convertir_presion
from utils.i18n import language_selector
from languages.rociadores_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()

st.set_page_config(layout="wide")

# ============================================================
# Carga de datos (rutas absolutas, ajústalas según tu entorno)
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
def longitud_equivalente(diametro, accesorios_str):
    """
    accesorios_str: string con nombres separados por coma (ej. "Codo 90°, Codo 90°, Tee")
    Devuelve la suma de las longitudes equivalentes de todos los accesorios.
    """
    df = pd.read_csv('dababase\equiv.csv')
    df.columns = df.columns.str.strip()
    if not accesorios_str or pd.isna(accesorios_str):
        return 0.0
    accesorios_list = [a.strip() for a in accesorios_str.split(',') if a.strip()]
    total = 0.0
    for acc in accesorios_list:
        try:
            valor = df.loc[df['DIAMETRO'] == diametro, acc].values[0]
            total += valor
        except (IndexError, KeyError):
            return f"Error: accesorio '{acc}' no encontrado para diámetro {diametro}"
    return total

@st.cache_data
def columnas():
    df = pd.read_excel(r'C:\Users\varia\OneDrive\Documentos\Accesorios\columnas.xlsx')
    df.dropna(inplace=True, how='all')
    df.columns = df.columns.str.strip()
    return df

# Estilos CSS (opcional)
st.markdown(
    """
    <style>
    .stApp { background-color: #080426 !important; color: #547FEB !important; }
    .stApp h1 { color: #2E8B57 !important; font-family: 'Arial', sans-serif; text-align: center; }
    .stApp h2, .stApp h3 { color: #2E8B57 !important; font-family: 'Arial', sans-serif; }
    .stMarkdown p { color: #90EE90 !important; font-size: 18px; text-align: justify; }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title=t("page_title"), page_icon="🧯", layout="wide")
st.title(t("title"))
st.markdown("---")

# ============================================
# Propósito y fundamentos (texto informativo)
# ============================================
st.header(t("purpose_header"))
st.markdown(t("purpose_text"))
st.header(t("fundamentals_header"))
st.markdown(t("fundamentals_text"))
st.markdown("---")

# ============================================================
# Inicialización del estado
# ============================================================
if 'tabla_entrada' not in st.session_state:
    st.session_state.tabla_entrada = pd.DataFrame(columns=[
        'Número de Línea', 'Diámetro', 'Cédula', 'Longitud', 'Accesorio', 'Elevación', 'K (rociador)', 'Flujo adicional'
    ])
if 'accesorios_temp' not in st.session_state:
    st.session_state.accesorios_temp = []  # lista de tuplas (accesorio, cantidad)
if 'column' not in st.session_state:
    st.session_state.column = columnas()
if 'resultados' not in st.session_state:
    st.session_state.resultados = None

opcion1 = st.session_state.column['DIAMETRO'].to_list()
opcion2 = st.session_state.column['ACCESORIO'].to_list()
opcion3 = st.session_state.column['CEDULA'].to_list()

# ============================================================
# Selector de sistema de unidades
# ============================================================
sistema = st.radio(t("fire_unit_system"), [t("fire_unit_imperial"), t("fire_unit_si")], horizontal=True, index=0)

# ============================================================
# Condiciones de operación y propiedades del fluido
# ============================================================
with st.container(border=True):
    st.write(t("fire_fluid_props_header"))
    colFlu, colOp = st.columns(2)
    with colFlu:
        if sistema == t("fire_unit_imperial"):
            desidad = st.number_input(t("fire_density_lbft3"), value=62.4, step=0.1)
            viscosidad = st.number_input(t("fire_viscosity_stokes"), value=1.0, step=0.01)
            presion_diseno = st.number_input(t("fire_design_pressure_psi"), value=7.0, step=0.1)
        else:
            desidad = st.number_input(t("fire_density_kgm3"), value=1000.0, step=0.1)
            viscosidad = st.number_input(t("fire_viscosity_cst"), value=1.0, step=0.01)
            presion_diseno = st.number_input(t("fire_design_pressure_kpa"), value=48.0, step=0.1)
    with colOp:
        if sistema == t("fire_unit_imperial"):
            temperatura = st.number_input(t("fire_temperature_f"), value=60.0, step=0.1)
        else:
            temperatura = st.number_input(t("fire_temperature_c"), value=15.0, step=0.1)

# ============================================================
# Modelo: entrada de datos (con validación de número de línea y accesorios múltiples)
# ============================================================
with st.container(border=True):
    # st.write('Ingrese los tramos de tubería en orden desde la fuente (bomba) hasta el rociador más lejano.')
    st.write(t("description_header"))

    st.info(t("description_text"))
    
    col1, col2 = st.columns(2)
    with col1:
        numlinea = st.number_input(t("fire_line_number"), step=1, min_value=1)
        if sistema == t("fire_unit_imperial"):
            longitudlinea = st.number_input(t("fire_length_ft"), value=0.0, step=0.1, key='longitud')
            diametros = st.selectbox(t("fire_diameter_in"), opcion1, placeholder=t("fire_diameter_placeholder"), key='diam')
        else:
            longitudlinea = st.number_input(t("fire_length_m"), value=0.0, step=0.1, key='longitud')
            diametros = st.selectbox(t("fire_diameter_mm"), opcion1, placeholder=t("fire_diameter_placeholder"), key='diam')
        cedulas = st.selectbox(t("fire_schedule"), opcion3, placeholder=t("fire_schedule_placeholder"), key='ced')
        if sistema == t("fire_unit_imperial"):
            elevacion = st.number_input(t("fire_elevation_ft"), value=0.0, step=0.1, key='elev')
        else:
            elevacion = st.number_input(t("fire_elevation_m"), value=0.0, step=0.1, key='elev')
        if sistema == t("fire_unit_imperial"):
            k_rociador = st.number_input(t("fire_k_factor_gpm"), value=5.6, step=0.1, key='k')
        else:
            k_rociador = st.number_input(t("fire_k_factor_lmin"), value=80.0, step=0.1, key='k')
        flujo_adicional = st.number_input(
            t("fire_additional_flow"),
            value=0.0,
            step=0.1,
            key='flujo_adic',
            help=t("fire_additional_flow_help")
        )
    
    with col2:
        st.subheader(t("fire_section_accessories_header"))
        acc_seleccionado = st.selectbox(t("fire_accessory"), opcion2, placeholder=t("fire_accessory_placeholder"), key='acc_sel')
        cantidad = st.number_input(t("fire_quantity"), min_value=1, value=1, step=1, key='cant_acc')
        
        if st.button(t("fire_add_accessory_button"), key='add_acc'):
            if acc_seleccionado and acc_seleccionado != t("fire_accessories_word"):
                st.session_state.accesorios_temp.append((acc_seleccionado, cantidad))
                st.success(t("fire_added_accessory").format(cantidad, acc_seleccionado))
            else:
                st.warning(t("fire_warn_valid_accessory"))
        
        if st.session_state.accesorios_temp:
            st.write(t("fire_selected_accessories"))
            for i, (acc, cant) in enumerate(st.session_state.accesorios_temp):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f'{cant}x {acc}')
                with col_b:
                    if st.button('🗑️', key=f'del_acc_{i}'):
                        st.session_state.accesorios_temp.pop(i)
                        st.rerun()
        else:
            st.info(t("fire_no_accessories_yet"))
        
        if st.button(t("fire_clear_accessories_button"), key='clear_acc'):
            st.session_state.accesorios_temp = []
            st.rerun()

    # Botón agregar tramo con validación de número de línea único
    if st.button(t("fire_add_section_button"), key='add_tramo'):
        if not numlinea:
            st.warning(t("fire_warn_line_number"))
        elif longitudlinea == 0.0:
            st.warning(t("fire_warn_length"))
        elif not diametros or diametros == t("fire_diameter_placeholder"):
            st.warning(t("fire_warn_diameter"))
        elif not st.session_state.accesorios_temp:
            st.warning(t("fire_warn_accessory"))
        elif not cedulas or cedulas == t("fire_schedule"):
            st.warning(t("fire_warn_schedule"))
        else:
            # Verificar que el número de línea no exista ya en la tabla
            if numlinea in st.session_state.tabla_entrada['Número de Línea'].values:
                st.error(t("fire_error_duplicate_line").format(numlinea))
            else:
                # Construir el string de accesorios: "Accesorio1, Accesorio2, ..." repetido según cantidad
                accesorios_str = ', '.join([f'{acc}' for acc, cant in st.session_state.accesorios_temp for _ in range(cant)])
                nueva_fila = pd.DataFrame({
                    'Número de Línea': [numlinea],
                    'Diámetro': [diametros],
                    'Cédula': [cedulas],
                    'Longitud': [longitudlinea],
                    'Accesorio': [accesorios_str],
                    'Elevación': [elevacion],
                    'K (rociador)': [k_rociador],
                    'Flujo adicional': [flujo_adicional]
                })
                st.session_state.tabla_entrada = pd.concat(
                    [st.session_state.tabla_entrada, nueva_fila], ignore_index=True
                )
                # Limpiar lista de accesorios temporal
                st.session_state.accesorios_temp = []
                st.success(t("fire_success_section_added"))

# ============================================================
# Mostrar tabla de entrada editable
# ============================================================
st.write(t("fire_sections_table_header"))
if not st.session_state.tabla_entrada.empty:
    edited_df = st.data_editor(
        st.session_state.tabla_entrada,
        use_container_width=True,
        num_rows="dynamic",
        key='editor_entrada'
    )
    st.session_state.tabla_entrada = edited_df
else:
    st.info(t("fire_info_add_sections"))

# ============================================================
# Selector de unidad de presión para resultados
# ============================================================
unidades_presion = ["psi", "kPa", "Pa", "kg/cm²", "bar"]
unidad_presion_salida = st.selectbox(
    t("fire_pressure_unit_selector"),
    unidades_presion,
    index=0,
    help=t("fire_pressure_unit_help")
)

# ============================================================
# Botón de cálculo
# ============================================================
if st.button(t("fire_calc_button")):
    df = st.session_state.tabla_entrada.copy()
    if df.empty:
        st.warning(t("fire_warn_no_sections"))
    else:
        resultado = calcular_analisis_antifuego(
            df=df,
            sistema=sistema,
            desidad=desidad,
            viscosidad=viscosidad,
            presion_diseno=presion_diseno,
            diametro_nominal_func=diametro_nominal,
            longitud_equivalente_func=longitud_equivalente,
            unidad_presion_salida=unidad_presion_salida,
            C_factor=120
        )
        if isinstance(resultado[0], str):
            st.error(resultado[0])
        else:
            df_resultados, P_inicial, P_final, long_acum, presion_nodos, elevacion_nodos = resultado
            st.session_state.resultados = df_resultados
            st.session_state.P_inicial = P_inicial
            st.session_state.P_final = P_final
            st.session_state.long_acum = long_acum
            st.session_state.presion_nodos = presion_nodos
            st.session_state.elevacion_nodos = elevacion_nodos
            st.session_state.unidad_presion = unidad_presion_salida
            st.session_state.sistema = sistema
            st.success(t("fire_success_calc"))

# ============================================================
# Mostrar resultados (si existen)
# ============================================================
if st.session_state.resultados is not None:
    st.write(t("fire_results_header"))
    st.caption(t("fire_results_caption"))
    df_res = st.session_state.resultados.rename(columns={t("fire_col_cumulative_flow"): t("fire_col_pipe_flow")})
    st.dataframe(df_res, use_container_width=True)

    # Métricas
    col1, col2, col3 = st.columns(3)
    unidad = st.session_state.unidad_presion
    with col1:
        st.metric(t("fire_metric_farthest_pressure"), f"{st.session_state.P_inicial:.2f} {unidad}")
    with col2:
        st.metric(t("fire_metric_source_pressure"), f"{st.session_state.P_final:.2f} {unidad}")
    with col3:
        st.metric(t("fire_metric_pressure_increase"), f"{st.session_state.P_final - st.session_state.P_inicial:.2f} {unidad}")

    # ============================================================
    # Gráficas
    # ============================================================
    st.write(t("fire_profiles_header"))

    long = st.session_state.long_acum
    elev = st.session_state.elevacion_nodos
    pres = st.session_state.presion_nodos

    # Gráfica 1: Elevación vs Longitud
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=long, y=elev,
        mode='lines+markers',
        name=t("fire_elevation_trace"),
        line=dict(color='green', width=2),
        marker=dict(size=8)
    ))
    fig1.update_layout(
        title=t("fire_elevation_profile_title"),
        xaxis_title=t("fire_axis_cumulative_length_m") if sistema == t("fire_unit_si") else t("fire_axis_cumulative_length_ft"),
        yaxis_title=t("fire_axis_elevation_m") if sistema == t("fire_unit_si") else t("fire_axis_elevation_ft"),
        template='plotly_white'
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfica 2: Presión vs Longitud (desde el rociador más lejano hasta la fuente)
    long = st.session_state.long_acum
    pres = st.session_state.presion_nodos

    # Los arrays ya están en el orden correcto (rociador más lejano -> fuente)
    # No es necesario invertir
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=long,
        y=pres,
        mode='lines+markers',
        name=t("fire_pressure_trace"),
        line=dict(color='red', width=2),
        marker=dict(size=8)
    ))
    fig2.update_layout(
        title=t("fire_pressure_profile_title"),
        xaxis_title=t("fire_axis_distance_m") if st.session_state.sistema == t("fire_unit_si") else t("fire_axis_distance_ft"),
        yaxis_title=t("fire_axis_pressure").format(st.session_state.unidad_presion),
        template='plotly_white'
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ============================================================
    # Gráfica de caídas de presión por tramo
    # ============================================================
    st.write(t("fire_drops_header"))
    if not st.session_state.resultados.empty:
        df_res = st.session_state.resultados
        tramos = df_res['Número de Línea'].astype(str).tolist()
        
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=tramos,
            y=df_res['dP_fricción'],
            name=t("fire_friction_loss"),
            marker_color='blue'
        ))
        fig3.add_trace(go.Bar(
            x=tramos,
            y=df_res['dP_elevación'],
            name=t("fire_elevation_loss"),
            marker_color='green'
        ))
        fig3.update_layout(
            title=t("fire_drops_title"),
            xaxis_title=t("fire_axis_section_number"),
            yaxis_title=t("fire_axis_pressure_drop").format(unidad),
            barmode='group',
            template='plotly_white'
        )
        st.plotly_chart(fig3, use_container_width=True)

        # Caída acumulada
        fig4 = go.Figure()
        caida_acumulada = []
        acum = 0
        for _, row in df_res.iterrows():
            acum += row['dP_fricción'] + row['dP_elevación']
            caida_acumulada.append(acum)
        
        fig4.add_trace(go.Scatter(
            x=tramos,
            y=caida_acumulada,
            mode='lines+markers',
            name=t("fire_cumulative_drop_trace"),
            line=dict(color='purple', width=2),
            marker=dict(size=8)
        ))
        fig4.update_layout(
            title=t("fire_cumulative_drop_title"),
            xaxis_title=t("fire_axis_section_number"),
            yaxis_title=t("fire_axis_cumulative_pressure_drop").format(unidad),
            template='plotly_white'
        )
        st.plotly_chart(fig4, use_container_width=True)