import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import confusion_matrix
from utils.redes_neuronales import (
    preprocesar_datos, entrenar_modelo, guardar_modelo_completo,
    predecir, obtener_clases
)
from utils.i18n import language_selector
from languages.redes_translate import init_lang, t, tw
from utils.sidebar import render_sidebar

init_lang()

render_sidebar()

# =============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =============================================================================
st.set_page_config(page_title="Entrenador de Redes Neuronales (TensorFlow)", layout="wide")
# st.title("🧠 Entrenador de Redes Neuronales con TensorFlow")
# st.markdown("Carga tus datos, define la arquitectura de la red y entrena un modelo.")
st.markdown("---")

# =============================================================================
# 2. INICIALIZACIÓN DEL ESTADO
# =============================================================================
if 'model_trained' not in st.session_state:
    st.session_state.model_trained = False
if 'history' not in st.session_state:
    st.session_state.history = None
if 'model' not in st.session_state:
    st.session_state.model = None
if 'data_prep' not in st.session_state:
    st.session_state.data_prep = None
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'feature_cols' not in st.session_state:
    st.session_state.feature_cols = []
if 'target_col' not in st.session_state:
    st.session_state.target_col = None
if 'problem_type' not in st.session_state:
    st.session_state.problem_type = "Clasificación"
if 'test_size' not in st.session_state:
    st.session_state.test_size = 0.2
if 'num_layers' not in st.session_state:
    st.session_state.num_layers = 2
if 'neurons_per_layer' not in st.session_state:
    st.session_state.neurons_per_layer = [64, 64]
if 'activation' not in st.session_state:
    st.session_state.activation = 'relu'
if 'optimizer_name' not in st.session_state:
    st.session_state.optimizer_name = 'adam'
if 'learning_rate' not in st.session_state:
    st.session_state.learning_rate = 0.001
if 'epochs' not in st.session_state:
    st.session_state.epochs = 50
if 'batch_size' not in st.session_state:
    st.session_state.batch_size = 32
if 'validation_split' not in st.session_state:
    st.session_state.validation_split = 0.2
if 'use_early_stopping' not in st.session_state:
    st.session_state.use_early_stopping = False
if 'early_stopping_patience' not in st.session_state:
    st.session_state.early_stopping_patience = 10
if 'use_reduce_lr' not in st.session_state:
    st.session_state.use_reduce_lr = False
if 'reduce_factor' not in st.session_state:
    st.session_state.reduce_factor = 0.5
if 'reduce_patience' not in st.session_state:
    st.session_state.reduce_patience = 5
if 'data_source' not in st.session_state:
    st.session_state.data_source = "Archivo"

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
    page_icon="🧠",
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
# CAPACIDADES DEL MÓDULO
# ============================================
st.header(t("capabilities_header"))
st.markdown(t("capabilities_text"))

st.markdown("---")

# ============================================
# VARIABLES DE ENTRADA
# ============================================
st.header(t("inputs_header"))

st.subheader(t("inputs_subheader_A"))
st.markdown(t("inputs_text_A"))

st.subheader(t("inputs_subheader_B"))
st.markdown(t("inputs_text_B"))

st.subheader(t("inputs_subheader_C"))
st.markdown(t("inputs_text_C"))

st.subheader(t("inputs_subheader_D"))
st.markdown(t("inputs_text_D"))

st.markdown("---")

# ============================================
# RESULTADOS OBTENIDOS
# ============================================
st.header(t("results_header"))

with st.expander(t("training_expander_title"), expanded=False):
    st.markdown(t("training_expander_text"))

with st.expander(t("evaluation_expander_title"), expanded=False):
    st.markdown(t("evaluation_expander_text"))

with st.expander(t("predictions_expander_title"), expanded=False):
    st.markdown(t("predictions_expander_text"))

with st.expander(t("summary_expander_title"), expanded=False):
    st.markdown(t("summary_expander_text"))

st.markdown("---")

# ============================================
# ALCANCE Y APLICABILIDAD
# ============================================
st.header(t("applications_header"))
st.markdown(t("applications_text"))

st.caption(t("caption"))

# =============================================================================
# 3. FUNCIONES DE VISUALIZACIÓN
# =============================================================================

def plot_training_history(history):
    """Dibuja gráficas de pérdida y métrica durante el entrenamiento."""
    epochs = range(1, len(history.history['loss']) + 1)
    fig = make_subplots(rows=1, cols=2, subplot_titles=(t("nn_plot_loss"), t("nn_plot_metric")))

    # Pérdida
    fig.add_trace(go.Scatter(x=epochs, y=history.history['loss'], mode='lines+markers', name=t("nn_plot_training")), row=1, col=1)
    if 'val_loss' in history.history:
        fig.add_trace(go.Scatter(x=epochs, y=history.history['val_loss'], mode='lines+markers', name=t("nn_plot_validation")), row=1, col=1)
    fig.update_xaxes(title_text=t("nn_plot_epoch"), row=1, col=1)
    fig.update_yaxes(title_text=t("nn_plot_loss_y"), row=1, col=1)

    # Métrica
    metric_key = None
    for key in history.history.keys():
        if key not in ['loss', 'val_loss'] and not key.startswith('val_'):
            metric_key = key
            break
    if metric_key:
        fig.add_trace(go.Scatter(x=epochs, y=history.history[metric_key], mode='lines+markers', name=t("nn_plot_training")), row=1, col=2)
        if f'val_{metric_key}' in history.history:
            fig.add_trace(go.Scatter(x=epochs, y=history.history[f'val_{metric_key}'], mode='lines+markers', name=t("nn_plot_validation")), row=1, col=2)
        fig.update_xaxes(title_text=t("nn_plot_epoch"), row=1, col=2)
        fig.update_yaxes(title_text=metric_key.capitalize(), row=1, col=2)

    fig.update_layout(height=400, template='plotly_white')
    return fig

def plot_confusion_matrix(y_true, y_pred, classes):
    """Dibuja la matriz de confusión con Plotly."""
    cm = confusion_matrix(y_true, y_pred)
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=classes,
        y=classes,
        colorscale='Blues',
        text=cm,
        texttemplate='%{text}',
        textfont={"size": 16}
    ))
    fig.update_layout(
        title=t("nn_plot_confusion_title"),
        xaxis_title=t("nn_plot_confusion_pred"),
        yaxis_title=t("nn_plot_confusion_real"),
        height=500,
        width=500,
        template='plotly_white'
    )
    return fig

# =============================================================================
# 4. INTERFAZ DE USUARIO
# =============================================================================

# =============================================================================
# 4.1 SELECCIÓN DE FUENTE DE DATOS
# =============================================================================
st.subheader(t("nn_data_header"))

data_source = st.radio(
    t("nn_data_source"),
    [t("nn_source_excel"), t("nn_source_manual")],
    horizontal=True,
    key="data_source_radio"
)
st.session_state.data_source = data_source

# =============================================================================
# 4.2 CARGA DE ARCHIVO
# =============================================================================
if data_source == t("nn_source_excel"):
    uploaded_file = st.file_uploader(t("nn_upload_label"), type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.session_state.df = df
        st.success(t("nn_upload_success").format(df.shape[0], df.shape[1]))
        
        with st.expander(t("nn_preview_expander")):
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(t("nn_preview_caption").format(df.shape[0], df.shape[1]))
        
        # Selección de columnas
        columns = df.columns.tolist()
        col1, col2 = st.columns(2)
        with col1:
            target_col = st.selectbox(
                t("nn_target_col_label"),
                columns,
                index=len(columns)-1,
                key="target_select_file"
            )
            st.session_state.target_col = target_col
        with col2:
            feature_cols = st.multiselect(
                t("nn_feature_cols_label"),
                [c for c in columns if c != target_col],
                default=[c for c in columns if c != target_col],
                key="feature_select_file"
            )
            st.session_state.feature_cols = feature_cols

# =============================================================================
# 4.3 INGRESO MANUAL
# =============================================================================
else:
    st.info(t("nn_manual_info"))
    
    # Número de filas y columnas
    col_rows, col_cols = st.columns(2)
    with col_rows:
        num_rows = st.number_input(t("nn_num_rows"), min_value=2, max_value=100, value=5, step=1, key="num_rows")
    with col_cols:
        num_cols = st.number_input(t("nn_num_cols"), min_value=2, max_value=10, value=3, step=1, key="num_cols")
    
    # Nombres de columnas
    st.caption(t("nn_col_names_caption"))
    col_names = []
    cols_names = st.columns(min(num_cols, 4))
    for i in range(num_cols):
        col_idx = i % len(cols_names)
        with cols_names[col_idx]:
            default_name = t("nn_col_default_name").format(i+1) if i < num_cols - 1 else t("nn_col_default_target")
            name = st.text_input(t("nn_col_name_label").format(i+1), value=default_name, key=f"col_name_{i}")
            col_names.append(name)
    
    # Ingreso de datos
    st.caption(t("nn_data_caption"))
    
    data_rows = []
    for i in range(num_rows):
        cols_row = st.columns(num_cols)
        row_data = []
        for j in range(num_cols):
            with cols_row[j]:
                val = st.number_input(
                    t("nn_cell_label").format(i+1, col_names[j]),
                    value=0.0,
                    step=0.1,
                    format="%.2f",
                    key=f"cell_{i}_{j}"
                )
                row_data.append(val)
        data_rows.append(row_data)
    
    # Botón para crear DataFrame
    if st.button(t("nn_create_df_button"), key="create_df_btn"):
        try:
            df = pd.DataFrame(data_rows, columns=col_names)
            st.session_state.df = df
            st.success(t("nn_data_created").format(df.shape[0], df.shape[1]))
            
            with st.expander(t("nn_preview_expander")):
                st.dataframe(df, use_container_width=True)
            
            # Selección de columnas
            columns = df.columns.tolist()
            col1, col2 = st.columns(2)
            with col1:
                target_col = st.selectbox(
                    t("nn_target_col_label"),
                    columns,
                    index=len(columns)-1,
                    key="target_select_manual"
                )
                st.session_state.target_col = target_col
            with col2:
                feature_cols = st.multiselect(
                    t("nn_feature_cols_label"),
                    [c for c in columns if c != target_col],
                    default=[c for c in columns if c != target_col],
                    key="feature_select_manual"
                )
                st.session_state.feature_cols = feature_cols
        except Exception as e:
            st.error(t("nn_error_create_df").format(e))

# =============================================================================
# 4.4 CONFIGURACIÓN DEL MODELO (común para ambas fuentes)
# =============================================================================
if st.session_state.df is not None and st.session_state.feature_cols:
    df = st.session_state.df
    target_col = st.session_state.target_col
    feature_cols = st.session_state.feature_cols
    
    # Tipo de problema
    unique_y = df[target_col].unique()
    n_unique = len(unique_y)
    
    if n_unique <= 10:
        try:
            if all(isinstance(val, (int, float)) and float(val).is_integer() for val in unique_y):
                default_problem = t("nn_problem_classification")
            elif any(isinstance(val, str) for val in unique_y):
                default_problem = t("nn_problem_classification")
            else:
                default_problem = t("nn_problem_regression")
        except:
            default_problem = t("nn_problem_regression")
    else:
        default_problem = t("nn_problem_regression")
    
    problem_type = st.radio(
        t("nn_problem_type"),
        [t("nn_problem_classification"), t("nn_problem_regression")],
        index=0 if default_problem == t("nn_problem_classification") else 1,
        horizontal=True
    )
    st.session_state.problem_type = problem_type
    
    test_size = st.slider(
        t("nn_test_size"),
        min_value=10,
        max_value=40,
        value=20,
        step=5
    ) / 100
    st.session_state.test_size = test_size
    
    # =========================================================================
    # 4.5 ARQUITECTURA DE LA RED
    # =========================================================================
    st.subheader(t("nn_architecture_header"))
    
    col3, col4 = st.columns(2)
    with col3:
        num_layers = st.number_input(
            t("nn_num_layers"),
            min_value=1,
            max_value=5,
            value=st.session_state.num_layers,
            step=1,
            key="num_layers_input"
        )
        st.session_state.num_layers = num_layers
    
    # Capas ocultas
    neurons_per_layer = []
    cols_layers = st.columns(min(num_layers, 4))
    for i in range(num_layers):
        col_idx = i % len(cols_layers)
        with cols_layers[col_idx]:
            default_neurons = st.session_state.neurons_per_layer[i] if i < len(st.session_state.neurons_per_layer) else 64
            neurons = st.number_input(
                t("nn_neurons_layer").format(i+1),
                min_value=4,
                max_value=512,
                value=default_neurons,
                step=8,
                key=f"neurons_{i}"
            )
            neurons_per_layer.append(neurons)
    st.session_state.neurons_per_layer = neurons_per_layer
    
    col5, col6, col7 = st.columns(3)
    with col5:
        activation = st.selectbox(
            t("nn_activation"),
            ['relu', 'sigmoid', 'tanh', 'elu', 'selu'],
            index=0,
            key="activation_select"
        )
        st.session_state.activation = activation
    with col6:
        optimizer_name = st.selectbox(
            t("nn_optimizer"),
            ['adam', 'sgd', 'rmsprop'],
            index=0,
            key="optimizer_select"
        )
        st.session_state.optimizer_name = optimizer_name
    with col7:
        learning_rate = st.number_input(
            t("nn_learning_rate"),
            min_value=0.0001,
            max_value=0.1,
            value=st.session_state.learning_rate,
            format="%.4f",
            key="lr_input"
        )
        st.session_state.learning_rate = learning_rate
    
    # =========================================================================
    # 4.6 PARÁMETROS DE ENTRENAMIENTO
    # =========================================================================
    st.subheader(t("nn_training_header"))
    
    col8, col9, col10 = st.columns(3)
    with col8:
        epochs = st.number_input(
            t("nn_epochs"),
            min_value=1,
            max_value=1000,
            value=st.session_state.epochs,
            step=10,
            key="epochs_input"
        )
        st.session_state.epochs = epochs
    with col9:
        batch_size = st.number_input(
            t("nn_batch_size"),
            min_value=8,
            max_value=512,
            value=st.session_state.batch_size,
            step=8,
            key="batch_size_input"
        )
        st.session_state.batch_size = batch_size
    with col10:
        validation_split = st.slider(
            t("nn_validation_split"),
            min_value=0,
            max_value=30,
            value=int(st.session_state.validation_split * 100),
            step=5,
            key="val_split_slider"
        ) / 100
        st.session_state.validation_split = validation_split
    
    # =========================================================================
    # 4.7 CALLBACKS
    # =========================================================================
    st.subheader(t("nn_callbacks_header"))
    
    col11, col12 = st.columns(2)
    with col11:
        use_early_stopping = st.checkbox(
            t("nn_use_early_stopping"),
            value=st.session_state.use_early_stopping,
            key="early_stop_check"
        )
        st.session_state.use_early_stopping = use_early_stopping
        if use_early_stopping:
            early_stopping_patience = st.number_input(
                t("nn_early_stopping_patience"),
                min_value=2,
                value=st.session_state.early_stopping_patience,
                step=2,
                key="early_stop_patience"
            )
            st.session_state.early_stopping_patience = early_stopping_patience
    with col12:
        use_reduce_lr = st.checkbox(
            t("nn_use_reduce_lr"),
            value=st.session_state.use_reduce_lr,
            key="reduce_lr_check"
        )
        st.session_state.use_reduce_lr = use_reduce_lr
        if use_reduce_lr:
            col13, col14 = st.columns(2)
            with col13:
                reduce_factor = st.number_input(
                    t("nn_reduce_factor"),
                    min_value=0.1,
                    max_value=0.9,
                    value=st.session_state.reduce_factor,
                    step=0.1,
                    key="reduce_factor"
                )
                st.session_state.reduce_factor = reduce_factor
            with col14:
                reduce_patience = st.number_input(
                    t("nn_reduce_patience"),
                    min_value=2,
                    value=st.session_state.reduce_patience,
                    step=1,
                    key="reduce_patience"
                )
                st.session_state.reduce_patience = reduce_patience
    
    # =========================================================================
    # 4.8 BOTÓN DE ENTRENAMIENTO
    # =========================================================================
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        entrenar = st.button(t("nn_train_button"), type="primary", use_container_width=True)
    
    # =========================================================================
    # 4.9 LÓGICA DE ENTRENAMIENTO
    # =========================================================================
    if entrenar:
        try:
            with st.spinner(t("nn_spinner_training")):
                data_prep = preprocesar_datos(
                    df=df,
                    target_col=target_col,
                    feature_cols=feature_cols,
                    problem_type=problem_type,
                    test_size=test_size
                )
                st.session_state.data_prep = data_prep
                
                resultados = entrenar_modelo(
                    data_preprocesado=data_prep,
                    num_layers=num_layers,
                    neurons_per_layer=neurons_per_layer,
                    activation=activation,
                    optimizer_name=optimizer_name,
                    learning_rate=learning_rate,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_split=validation_split,
                    use_early_stopping=use_early_stopping,
                    early_stopping_patience=early_stopping_patience if use_early_stopping else 10,
                    use_reduce_lr=use_reduce_lr,
                    reduce_factor=reduce_factor if use_reduce_lr else 0.5,
                    reduce_patience=reduce_patience if use_reduce_lr else 5
                )
                st.session_state.resultados = resultados
                st.session_state.model_trained = True
                st.success(t("nn_success_training"))
        except Exception as e:
            st.error(t("nn_error_training").format(e))
            st.session_state.model_trained = False

# =============================================================================
# 5. MOSTRAR RESULTADOS
# =============================================================================
if st.session_state.model_trained and st.session_state.resultados is not None:
    resultados = st.session_state.resultados
    data_prep = st.session_state.data_prep
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader(t("nn_training_progress_header"))
        fig = plot_training_history(resultados['history'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader(t("nn_test_metrics_header"))
        for name, value in resultados['test_metrics'].items():
            st.metric(name.capitalize(), f"{value:.4f}")

        if data_prep['n_classes'] is not None and data_prep['n_classes'] > 0:
            st.subheader(t("nn_confusion_matrix_header"))
            y_pred = resultados['model'].predict(data_prep['X_test'], verbose=0)
            if y_pred.shape[-1] > 1:
                y_pred_classes = np.argmax(y_pred, axis=1)
                y_true = np.argmax(data_prep['y_test'], axis=1)
            else:
                y_pred_classes = (y_pred > 0.5).astype(int).flatten()
                y_true = data_prep['y_test'].flatten()
            classes = obtener_clases(data_prep['label_encoder'], data_prep['classes'])
            fig_cm = plot_confusion_matrix(y_true, y_pred_classes, classes)
            st.plotly_chart(fig_cm, use_container_width=True)

    with st.expander(t("nn_model_summary_expander")):
        st.text(resultados['model_summary'])

    # =========================================================================
    # 5.1 PREDICCIONES
    # =========================================================================
    st.subheader(t("nn_predictions_header"))
    cols_pred = st.columns(min(len(data_prep['feature_names']), 3))
    input_values = []
    for i, feature in enumerate(data_prep['feature_names']):
        col_idx = i % len(cols_pred)
        with cols_pred[col_idx]:
            default_val = float(st.session_state.df[feature].mean())
            val = st.number_input(
                f"{feature}",
                value=default_val,
                step=0.1,
                format="%.4f",
                key=f"pred_{feature}"
            )
            input_values.append(val)
    
    if st.button(t("nn_predict_button"), key="predict_button"):
        try:
            X_input = np.array(input_values).reshape(1, -1)
            model = resultados['model']
            scaler = data_prep['scaler']
            X_scaled = scaler.transform(X_input)
            pred = model.predict(X_scaled, verbose=0)
            
            if data_prep['n_classes'] is not None and data_prep['n_classes'] > 0:
                if pred.shape[-1] > 1:
                    pred_class = np.argmax(pred, axis=1)[0]
                    confidence = np.max(pred, axis=1)[0]
                    classes = obtener_clases(data_prep['label_encoder'], data_prep['classes'])
                    st.success(t("nn_predicted_class").format(classes[pred_class]))
                    st.info(t("nn_confidence").format(confidence*100))
                    prob_df = pd.DataFrame({t("nn_prob_df_class"): classes, t("nn_prob_df_probability"): pred[0]})
                    st.bar_chart(prob_df.set_index(t("nn_prob_df_class")))
                else:
                    pred_class = int(pred[0][0] > 0.5)
                    confidence = pred[0][0] if pred_class == 1 else 1 - pred[0][0]
                    classes = obtener_clases(data_prep['label_encoder'], data_prep['classes'])
                    st.success(t("nn_predicted_class").format(classes[pred_class]))
                    st.info(t("nn_confidence").format(confidence*100))
            else:
                st.success(t("nn_predicted_value").format(pred[0][0]))
        except Exception as e:
            st.error(t("nn_error_prediction").format(e))

    # =========================================================================
    # 5.2 GUARDAR MODELO
    # =========================================================================
    with st.expander(t("nn_save_model_expander")):
        try:
            model_bytes, preproc_bytes = guardar_modelo_completo(
                model=resultados['model'],
                scaler=data_prep['scaler'],
                label_encoder=data_prep['label_encoder'],
                filepath='modelo'
            )
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label=t("nn_download_model"),
                    data=model_bytes,
                    file_name='modelo_entrenado.h5',
                    mime='application/octet-stream',
                    use_container_width=True
                )
            with col_dl2:
                st.download_button(
                    label=t("nn_download_preproc"),
                    data=preproc_bytes,
                    file_name='preprocesadores.pkl',
                    mime='application/octet-stream',
                    use_container_width=True
                )
        except Exception as e:
            st.error(t("nn_error_save").format(e))

else:
    if st.session_state.df is None:
        if data_source == t("nn_source_excel"):
            st.info(t("nn_info_upload_excel"))
        else:
            st.info(t("nn_info_manual_data"))
    elif not st.session_state.feature_cols:
        st.info(t("nn_info_select_features"))

# =============================================================================
# 6. FOOTER CON AYUDA RÁPIDA
# =============================================================================
st.markdown("---")
st.caption(t("nn_footer_file_format"))
st.caption(t("nn_footer_classification"))
st.caption(t("nn_footer_regression"))