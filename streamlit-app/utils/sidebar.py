"""
Sidebar de navegación personalizado con soporte i18n.
Reemplaza el sidebar nativo de Streamlit.
"""
import streamlit as st
from utils.i18n import t, get_lang, set_lang


def render_sidebar():
    """Renderiza el sidebar personalizado con traducción."""
    
    with st.sidebar:
        # Título
        st.markdown("###  " + t("sidebar_title", default="Navegación"))
        st.markdown("---")
                
                # === SELECTOR DE IDIOMA ===
        st.markdown("### 🌐 " + t("language_label", default="Idioma"))
                
        lang_options = {
                    "es": t("lang_es", default="🇲 Español"),
                    "en": t("lang_en", default="🇺🇸 Inglés")
                }
                
        current_lang = get_lang()
        selected_lang = st.radio(
                    "",
                    options=["es", "en"],
                    format_func=lambda x: lang_options[x],
                    index=0 if current_lang == "es" else 1,
                    horizontal=True,
                    key="sidebar_lang_selector"
                )
                
        if selected_lang != current_lang:
                    set_lang(selected_lang)
                    st.rerun()
        
        st.markdown("---")
        
        # Función auxiliar para botones de navegación
        def nav_button(label, page_file=None, url_externa=None):
            """Crea un botón de navegación."""
            if st.button(label, use_container_width=True, key=f"nav_{label}"):
                if url_externa:
                    # Para páginas HTML externas
                    st.markdown(
                        f'<script>window.open("{url_externa}", "_blank");</script>',
                        unsafe_allow_html=True
                    )
                elif page_file:
                    st.switch_page(page_file)
        
        # === INICIO ===
        nav_button("🏠 " + t("nav_home", default="Iinicio"), "app.py")

        st.markdown("---")
        st.markdown("**🧠 " + t("nav_ai", default="Ai y Datos") + "**")
        # nav_button(t("nav_neural", default="Redes Neuronales"), "pages/17_Redes_neuronales.py")
        nav_button(t("nav_mc", default="Mínimos Cuadrados"), "pages/1_Minimos_Cuadrados.py")
        nav_button(t("nav_opt", default="Optimización"), "pages/2_Optimizacion.py")

        st.markdown("---")
        st.markdown("**💧 " + t("nav_hydraulics", default="Hidráulica") + "**")
        nav_button(t("nav_hydraulic", default="Análisis Hidráulico"), "pages/9_Analisis_hidraulico.py")
        nav_button(t("nav_pumps", default="Bombas"), "pages/18_Bombas.py")
        nav_button(t("nav_compressors", default="Compresores"), "pages/19_Compresores.py")
        nav_button(t("nav_firewater", default="Rociadores"), "pages/10_Hidraulica_antifuego.py")        
        nav_button(t("nav_turbines", default="Turbinas"), "pages/20_Turbinas.py")
                
        st.markdown("---")
        st.markdown("**📊 " + t("nav_numerical", default="Métodos Numéricos") + "**")
        nav_button(t("nav_ode", default="Ecuaciones Diferenciales"), "pages/11_Ecuaciones_diferenciales.py")
        nav_button(t("nav_integration", default="Integración Numérica"), "pages/12_Integracion_numerica.py")
        nav_button(t("nav_ode_system", default="Sistema EDOs"), "pages/13_Sistema_edos.py")
        # nav_button(t("nav_pde", default="EDPs 1D"), "pages/14_Ecuacionesdif_parciales1d.py")
        nav_button(t("nav_polynomials", default="Solución Polinomios"), "pages/15_Solucion_polinomios.py")
        
        st.markdown("---")
        st.markdown("** " + t("nav_thermo", default="Termodinámica") + "**")
        nav_button(t("nav_flash", default="Cálculo Flash"), "pages/6_Calculo_flash.py")
        nav_button(t("nav_envelope", default="Envolventes"), "pages/16_Envolventes.py")
        nav_button(t("nav_shortcut", default="Métodos Cortos"), "pages/7_Metodos_cortos.py")
        nav_button(t("nav_rigorous", default="Métodos Rigurosos"), "pages/8_Metodos_rigurosos.py")
        nav_button(t("nav_properties", default="Propiedades Mezclas"), "pages/5_Propiedades_mezclas.py")
                        
        #st.markdown("---")
        #st.markdown("**💳 " + t("nav_external", default="Donativos") + "**")
        # Pagos y Donativos como enlaces externos (HTML)
        # nav_button(t("nav_payments", default="Pagos"), url_externa="pagos.html")
        # nav_button(t("nav_donations", default="Donativos"), url_externa="donativos.html")
        #st.link_button("💳 " + t("nav_donations", default="Donativos"), "./donativos.html", use_container_width=True,)