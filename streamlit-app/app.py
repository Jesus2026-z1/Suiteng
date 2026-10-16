import streamlit as st
from utils.i18n import init_lang, t, tw
from utils.sidebar import render_sidebar

# ============================================
# Inicializar idioma ANTES de set_page_config
# ============================================
init_lang()

# ============================================
# Formato CSS (SIN CAMBIOS)
# ============================================
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
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# Selector de idioma (sidebar)
# ============================================

render_sidebar() 

st.title(t("title_main"))
st.markdown("---")

# ============================================
# DESCRIPCIÓN GENERAL (visible siempre)
# ============================================
st.header(t("header_proposito"))
st.markdown(t("intro_text"))
st.markdown("---")

# ============================================
# ORGANIZACIÓN POR CATEGORÍAS
# ============================================
st.header(t("header_modulos"))
st.subheader(t("subcat1"))
st.markdown(t("cat1_desc"))
st.subheader(t("subcat2"))
st.markdown(t("cat2_desc"))
st.subheader(t("subcat3"))
st.markdown(t("cat3_desc"))
st.subheader(t("subcat4"))
st.markdown(t("cat4_desc"))
st.markdown("---")

# ============================================
# PIE DE PÁGINA Y CRÉDITOS
# ============================================
st.caption(t("footer_caption"))