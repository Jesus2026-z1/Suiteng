import streamlit as st 
import pandas as pd
from utils.eqstate import *
from utils.densidad import *
from utils.viscosidad import *
from utils.cpvapor import *
from utils.i18n import language_selector
from languages.prop_mezclas_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar() 

# ---------- 1. Carga de datos ----------
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv(r'C:\Users\varia\OneDrive\Documentos\Database\data.csv')        
        df_filtrado = df.iloc[4:,[1,2,5,6,9,2,13,14,15,16,17,18,19,20]]
        df_filtrado.columns = ['Componente', 'Composición_inicial', 'Extra1', 'Extra2', 'Extra3', 'Extra4','HA', 'HB', 'HC', 'HD', 'VB', 'VC', 'DELHG', 'DELGF']
        # Convertir columnas numéricas a float (manejar errores con coerce)
        for col in ['Composición_inicial', 'Extra1', 'Extra2', 'Extra3', 'Extra4', 'HA', 'HB', 'HC', 'HD', 'VB', 'VC', 'DELHG', 'DELGF']:
            df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0.0)
        return df_filtrado
    except FileNotFoundError:
        return pd.DataFrame({
            'Componente': ['A', 'B', 'C', 'D'],
            'Composición_inicial': [0.0, 0.0, 0.0, 0.0],
            'Extra1': [10, 20, 30, 40],
            'Extra2': [100, 200, 300, 400],
            'Extra3': [1, 2, 3, 4],
            'HA': [1, 2, 3, 4],
            'HB': [1, 2, 3, 4],
            'HC': [1, 2, 3, 4],
            'HD': [1, 2, 3, 4],
            'VB': [1, 2, 3, 4],
            'VC': [1, 2, 3, 4],
            'DELHG': [1, 2, 3, 4],
            'DELGF': [1, 2, 3, 4],
        })

# ---------- 2. Inicialización del estado ----------
if 'tabla' not in st.session_state:
    st.session_state.tabla = pd.DataFrame(columns=['Componente', 'Composición', 'Extra1', 'Extra2', 'Extra3', 'Extra4', 'HA', 'HB', 'HC', 'HD', 'VB', 'VC', 'DELHG', 'DELGF'])

if 'df_completo' not in st.session_state:
    st.session_state.df_completo = cargar_datos()

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
    page_icon="🔬",
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

with st.expander(t("molecular_expander_title"), expanded=False):
    st.markdown(t("molecular_text"))

with st.expander(t("transport_expander_title"), expanded=False):
    st.markdown(t("transport_text"))

with st.expander(t("thermal_expander_title"), expanded=False):
    st.markdown(t("thermal_text"))

with st.expander(t("thermochemical_expander_title"), expanded=False):
    st.markdown(t("thermochemical_text"))

st.markdown("---")

# ============================================
# ALCANCE Y APLICABILIDAD
# ============================================
st.header(t("scope_header"))
st.markdown(t("scope_text"))

st.caption(t("caption"))

st.header(t("config_header"))

# Contenedor para selección de componentes
with st.container(border=True):
    st.subheader(t("mix_components_header"))
    col1, col2 = st.columns(2)
    with col1:
        opciones = st.session_state.df_completo['Componente'].tolist()
        seleccionado = st.selectbox(t("mix_select_component"), opciones, index=None, placeholder=t("mix_components_placeholder"))

        if st.button(t("mix_select_button")):
                fila = st.session_state.df_completo[st.session_state.df_completo['Componente'] == seleccionado]
                if not fila.empty:
                    # Ya no usamos 'Composición_inicial'
                    extra1 = fila['Extra1'].values[0]
                    extra2 = fila['Extra2'].values[0]
                    extra3 = fila['Extra3'].values[0]
                    extra4 = fila['Extra4'].values[0]
                    ha = fila['HA'].values[0]
                    hb = fila['HB'].values[0]
                    hc = fila['HC'].values[0]
                    hd = fila['HD'].values[0]
                    vb = fila['VB'].values[0]
                    vc = fila['VC'].values[0]
                    delhg = fila['DELHG'].values[0]
                    delgf = fila['DELGF'].values[0]
                    nueva_fila = pd.DataFrame({
                        'Componente': [seleccionado],
                        'Composición': [0.0],           # <--- SIEMPRE 0.0
                        'Extra1': [extra1],
                        'Extra2': [extra2],
                        'Extra3': [extra3],
                        'Extra4': [extra4],
                        'HA': [ha],
                        'HB': [hb],
                        'HC': [hc],
                        'HD': [hd],
                        'VB': [vb],
                        'VC': [vc],
                        'DELHG': [delhg],
                        'DELGF': [delgf],
                    })
                    st.session_state.tabla = pd.concat([st.session_state.tabla, nueva_fila], ignore_index=True)

        if not st.session_state.tabla.empty:
                    opciones_eliminar = [f"{i} - {row['Componente']}" for i, row in st.session_state.tabla.iterrows()]
                    seleccion_eliminar = st.selectbox(t("mix_select_row_delete"), opciones_eliminar)
                    if st.button(t("mix_delete_button")):
                        indice = int(seleccion_eliminar.split(" - ")[0])
                        st.session_state.tabla = st.session_state.tabla.drop(indice).reset_index(drop=True)
                        st.rerun()
        else:
            st.info(t("mix_no_components"))
    
    with col2:
        st.write(t("mix_selected_components"))
        tabla_editada = st.data_editor(
            st.session_state.tabla,
            num_rows="fixed",                     # <--- SOLO ESTE CAMBIO
            column_order=["Componente", "Composición"],
            column_config={
                "Componente": st.column_config.TextColumn(t("mix_component_col"), disabled=True),
                "Composición": st.column_config.NumberColumn(t("mix_fraction_col"), format="%.2f", min_value=0.00, max_value=1.00),
            },
            key="editor_tabla"
        )
        st.session_state.tabla = tabla_editada

        # Cálculos usando columnas extras
        if not st.session_state.tabla.empty:
            suma_x = st.session_state.tabla['Composición'].sum()
            if 0 <= suma_x <= 1:
                st.write(t("mix_total_sum").format(suma_x))
                # Asegurar que 'Extra1' sea numérica (ya debería serlo)
                suma_extra = st.session_state.tabla['Extra4'].sum()
                # Si por algún motivo es string, conviértela:
                # suma_extra = pd.to_numeric(st.session_state.tabla['Extra1'], errors='coerce').sum()
                # st.write(f"Suma de Extra1: {suma_extra:.2f}")   # <--- AQUÍ FALLA SI ES STRING
                ponderado = (st.session_state.tabla['Composición'] * st.session_state.tabla['Extra4']).sum()
                st.write(t("mix_molecular_weight").format(ponderado))
            else:
                st.write(t("mix_sum_must_be_one"))


# Introducción de condiciones de operación (Presión de operación, Temperatura de operación)

with st.container(border=True):
     st.write(t("mix_operating_conditions"))
     col3, col4 = st.columns(2)
     with col3: 
                presion = st.number_input(t("mix_pressure"))
                P = presion
                temperatura = st.number_input(t("mix_temperature"))
                T = temperatura + 273.15
                y = st.session_state.tabla['Composición']
                Tc = st.session_state.tabla['Extra1']
                Pc = st.session_state.tabla['Extra2'] * 1.01325
                omega = st.session_state.tabla['Extra3']
                cpa = st.session_state.tabla['HA']
                cpb = st.session_state.tabla['HB']
                cpc = st.session_state.tabla['HC']
                cpd = st.session_state.tabla['HD']
                facbvisc = st.session_state.tabla['VB']
                faccvisc = st.session_state.tabla['VC']
                entalStd = st.session_state.tabla['DELHG']
                gibsStd = st.session_state.tabla['DELGF']                
                
     with col4:
                modelo = st.selectbox(t("mix_select_model"), ("REDLICH-KWONG", "SOAVE-REDLICH-KWONG", "PENG-ROBINSON"), index=None, placeholder=t("mix_models_placeholder"),) # st.multiselect('Selecciona un modelo', ['REDLICH-KWONG', 'SOAVE-REDLICH-KWONG', 'PENG-ROBINSON'], default=['REDLICH-KWONG'],)                
                col5, col6 = st.columns(2)
                with col5:                    
                        if modelo == 'REDLICH-KWONG':
                            st.write(t("mix_rk_selected"))
                        elif modelo == 'SOAVE-REDLICH-KWONG':
                            st.write(t("mix_srk_selected"))
                        elif modelo == 'PENG-ROBINSON':
                            st.write(t("mix_pr_selected"))
                        else:
                            st.info(t("mix_no_model_selected"))
                with col6:
                    if st.button(t("mix_calculate_button")):
                        if modelo == 'REDLICH-KWONG':
                            compresibilidad = Z_RK_mezcla(T,P,y,Tc,Pc,k_ij=None,fase='líquido')                            
                        elif modelo == 'SOAVE-REDLICH-KWONG':
                            compresibilidad = Z_SRK_mezcla(T,P,y,Tc,Pc,omega,k_ij=None,fase='vapor')
                        elif modelo == 'PENG-ROBINSON':
                            compresibilidad = Z_PR_mezcla(T,P,y,Tc,Pc,omega,k_ij=None,fase='vapor')                            
                        else:
                            st.info(t("mix_select_model_info"))
                        
                        densidad = densidad_mezcla_gas(P, T, compresibilidad, ponderado) / 1000
                        viscosidad = (viscosidad_pura(facbvisc, faccvisc, T) * y).sum()
                        capacidadcal = (cp_vapor_puro(cpa, cpb, cpc, cpd, T) * y).sum()
                        capCal = capacidadcal * (4.1868 / ponderado)
                        entalpiastd = ((entalStd * y).sum()) * (4.1868 / ponderado)
                        ennergiastd = ((gibsStd * y).sum()) * (4.1868 / ponderado)

                        resultados = pd.DataFrame(
                                                    [
                                                        {t("mix_property_col"): t("mix_prop_mw"), t("mix_value_col"): ponderado},
                                                        {t("mix_property_col"): t("mix_prop_z"), t("mix_value_col"): compresibilidad},
                                                        {t("mix_property_col"): t("mix_prop_density"), t("mix_value_col"): densidad},
                                                        {t("mix_property_col"): t("mix_prop_viscosity"), t("mix_value_col"): viscosidad},
                                                        {t("mix_property_col"): t("mix_prop_cp_vapor"), t("mix_value_col"): capCal},
                                                        {t("mix_property_col"): t("mix_prop_std_enthalpy"), t("mix_value_col"): entalpiastd},
                                                        {t("mix_property_col"): t("mix_prop_std_energy"), t("mix_value_col"): ennergiastd},
                                                    ]
                                                )


st.write(t("mix_thermo_properties"))
try:
     edited_df = st.data_editor(resultados)
except NameError:     
     st.info(t("mix_no_results"))