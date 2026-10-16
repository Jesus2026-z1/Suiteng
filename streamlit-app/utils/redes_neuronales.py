# redes_neuronales.py
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, callbacks
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report
import joblib
import io

def build_model(input_dim, num_layers, neurons_per_layer, activation, output_units, output_activation, optimizer, learning_rate):
    """
    Construye el modelo Keras según la configuración.
    
    Parámetros:
    - input_dim: número de características de entrada
    - num_layers: número de capas ocultas
    - neurons_per_layer: lista con el número de neuronas por capa
    - activation: función de activación para capas ocultas
    - output_units: número de neuronas de salida
    - output_activation: función de activación de salida
    - optimizer: optimizador (instancia de optimizador Keras)
    - learning_rate: tasa de aprendizaje
    
    Retorna:
    - model: modelo Keras compilado
    """
    model = models.Sequential()
    model.add(layers.Input(shape=(input_dim,)))
    for i in range(num_layers):
        model.add(layers.Dense(neurons_per_layer[i], activation=activation))
    model.add(layers.Dense(output_units, activation=output_activation))
    
    # Determinar pérdida y métricas según el tipo de problema
    if output_units > 1 and output_activation == 'softmax':
        loss = 'categorical_crossentropy'
        metrics = ['accuracy']
    elif output_units == 1 and output_activation == 'sigmoid':
        loss = 'binary_crossentropy'
        metrics = ['accuracy']
    else:
        loss = 'mse'
        metrics = ['mae']
    
    model.compile(
        optimizer=optimizer(learning_rate=learning_rate),
        loss=loss,
        metrics=metrics
    )
    return model

def preprocesar_datos(df, target_col, feature_cols, problem_type, test_size, random_state=42):
    """
    Preprocesa los datos para el entrenamiento.
    
    Parámetros:
    - df: DataFrame con los datos
    - target_col: nombre de la columna objetivo
    - feature_cols: lista de columnas características
    - problem_type: 'Clasificación' o 'Regresión'
    - test_size: proporción para prueba
    - random_state: semilla aleatoria
    
    Retorna:
    - dict con: X_train, X_test, y_train, y_test, scaler, label_encoder, 
                output_units, output_activation, n_classes, classes
    """
    X = df[feature_cols].values
    y = df[target_col].values
    
    # Preprocesar según tipo de problema
    if problem_type == "Clasificación":
        # Codificar etiquetas si son texto
        if y.dtype == object:
            le = LabelEncoder()
            y = le.fit_transform(y)
            classes = le.classes_
        else:
            le = None
            classes = np.unique(y)
        
        n_classes = len(classes)
        
        # Si es multiclase (>2), usamos one-hot encoding
        if n_classes > 2:
            y = keras.utils.to_categorical(y, num_classes=n_classes)
            output_units = n_classes
            output_activation = 'softmax'
        else:
            output_units = 1
            output_activation = 'sigmoid'
    else:
        # Regresión
        le = None
        classes = None
        n_classes = None
        output_units = 1
        output_activation = 'linear'
    
    # Escalar características
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=test_size, random_state=random_state
    )
    
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'scaler': scaler,
        'label_encoder': le,
        'output_units': output_units,
        'output_activation': output_activation,
        'n_classes': n_classes,
        'classes': classes,
        'feature_names': feature_cols,
        'target_name': target_col
    }

def entrenar_modelo(data_preprocesado, num_layers, neurons_per_layer, activation,
                    optimizer_name, learning_rate, epochs, batch_size, 
                    validation_split, use_early_stopping=False, early_stopping_patience=10,
                    use_reduce_lr=False, reduce_factor=0.5, reduce_patience=5):
    """
    Entrena un modelo de red neuronal.
    
    Parámetros:
    - data_preprocesado: dict con datos preprocesados
    - num_layers: número de capas ocultas
    - neurons_per_layer: lista con neuronas por capa
    - activation: función de activación
    - optimizer_name: nombre del optimizador ('adam', 'sgd', 'rmsprop')
    - learning_rate: tasa de aprendizaje
    - epochs: número de épocas
    - batch_size: tamaño de lote
    - validation_split: proporción para validación
    - use_early_stopping: usar early stopping
    - early_stopping_patience: paciencia para early stopping
    - use_reduce_lr: usar reducción de learning rate
    - reduce_factor: factor de reducción
    - reduce_patience: paciencia para reducción
    
    Retorna:
    - model: modelo entrenado
    - history: historial de entrenamiento
    - test_metrics: métricas en prueba
    - model_summary: resumen del modelo
    """
    X_train = data_preprocesado['X_train']
    X_test = data_preprocesado['X_test']
    y_train = data_preprocesado['y_train']
    y_test = data_preprocesado['y_test']
    output_units = data_preprocesado['output_units']
    output_activation = data_preprocesado['output_activation']
    
    # Obtener el optimizador
    optimizer_class = getattr(optimizers, optimizer_name.capitalize())
    
    # Construir modelo
    model = build_model(
        input_dim=X_train.shape[1],
        num_layers=num_layers,
        neurons_per_layer=neurons_per_layer,
        activation=activation,
        output_units=output_units,
        output_activation=output_activation,
        optimizer=optimizer_class,
        learning_rate=learning_rate
    )
    
    # Callbacks
    callbacks_list = []
    if use_early_stopping:
        callbacks_list.append(
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=early_stopping_patience,
                restore_best_weights=True
            )
        )
    if use_reduce_lr:
        callbacks_list.append(
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=reduce_factor,
                patience=reduce_patience,
                min_lr=1e-7
            )
        )
    
    # Entrenar
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=validation_split,
        verbose=0,
        callbacks=callbacks_list
    )
    
    # Evaluar en prueba
    test_loss = model.evaluate(X_test, y_test, verbose=0)
    metrics_names = model.metrics_names
    test_metrics = dict(zip(metrics_names, test_loss))
    
    # Resumen del modelo
    stream = io.StringIO()
    model.summary(print_fn=lambda x: stream.write(x + '\n'))
    model_summary = stream.getvalue()
    
    return {
        'model': model,
        'history': history,
        'test_metrics': test_metrics,
        'model_summary': model_summary
    }

def guardar_modelo_completo(model, scaler, label_encoder, filepath):
    """
    Guarda el modelo y los preprocesadores en archivos separados.
    
    Parámetros:
    - model: modelo Keras
    - scaler: StandardScaler entrenado
    - label_encoder: LabelEncoder entrenado (puede ser None)
    - filepath: ruta base para guardar los archivos
    
    Retorna:
    - tuple: (model_bytes, preproc_bytes)
    """
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, 'modelo')
        model_path = base_path + '.h5'
        preproc_path = base_path + '_preprocessors.pkl'
        
        # Guardar
        model.save(model_path)
        joblib.dump({
            'scaler': scaler,
            'label_encoder': label_encoder
        }, preproc_path)
        
        # Leer archivos
        with open(model_path, 'rb') as f:
            model_bytes = f.read()
        with open(preproc_path, 'rb') as f:
            preproc_bytes = f.read()
    
    return model_bytes, preproc_bytes

def predecir(model, scaler, X_data):
    """
    Realiza predicciones con el modelo entrenado.
    
    Parámetros:
    - model: modelo Keras entrenado
    - scaler: StandardScaler entrenado
    - X_data: datos a predecir (array o DataFrame)
    
    Retorna:
    - predicciones: array con las predicciones
    """
    if isinstance(X_data, pd.DataFrame):
        X_data = X_data.values
    
    X_scaled = scaler.transform(X_data)
    predictions = model.predict(X_scaled, verbose=0)
    
    # Si es clasificación con softmax, devolver clase
    if predictions.shape[-1] > 1:
        return np.argmax(predictions, axis=1)
    elif predictions.shape[-1] == 1 and len(predictions.shape) == 2:
        # Binaria con sigmoid
        return (predictions > 0.5).astype(int).flatten()
    else:
        return predictions

def obtener_clases(label_encoder, classes):
    """Obtiene los nombres de las clases para clasificación."""
    if label_encoder is not None:
        return label_encoder.classes_
    elif classes is not None:
        return [str(c) for c in classes]
    else:
        return None