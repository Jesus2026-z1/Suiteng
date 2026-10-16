# analisis_hidraulico.py
import math
import pandas as pd

def haaland_friction_factor(Re, e_D):
    """Calcula el factor de fricción usando la ecuación de Haaland"""
    if Re == 0:
        return 0.02
    term1 = (e_D / 3.7) ** 1.11
    term2 = 6.9 / Re
    f = (1 / (-1.8 * math.log10(term1 + term2))) ** 2
    return f

def convertir_presion(valor, unidad_origen, unidad_destino):
    """
    Convierte presión entre diferentes unidades
    Unidades soportadas: psi, Pa, kPa, kg/cm2, bar
    """
    # Primero convertir a Pa (SI base)
    if unidad_origen == "psi":
        valor_pa = valor * 6894.76  # 1 psi = 6894.76 Pa
    elif unidad_origen == "kPa":
        valor_pa = valor * 1000  # 1 kPa = 1000 Pa
    elif unidad_origen == "Pa":
        valor_pa = valor
    elif unidad_origen == "kg/cm2":
        valor_pa = valor * 98066.5  # 1 kg/cm2 = 98066.5 Pa
    elif unidad_origen == "bar":
        valor_pa = valor * 100000  # 1 bar = 100000 Pa
    else:
        valor_pa = valor

    # Luego convertir de Pa a la unidad destino
    if unidad_destino == "psi":
        return valor_pa / 6894.76
    elif unidad_destino == "kPa":
        return valor_pa / 1000
    elif unidad_destino == "Pa":
        return valor_pa
    elif unidad_destino == "kg/cm2":
        return valor_pa / 98066.5
    elif unidad_destino == "bar":
        return valor_pa / 100000
    else:
        return valor_pa

def calcular_analisis_hidraulico(df, sistema, flujovolum, desidad, viscosidad, presion, 
                                 diametro_nominal_func, longitud_equivalente_func,
                                 unidad_presion_salida="psi", es_gas=True):
    """
    Realiza el análisis hidráulico completo para líquidos o gases
    
    Parámetros:
    - df: DataFrame con los datos de entrada
    - sistema: "Imperial" o "SI"
    - flujovolum: flujo volumétrico
    - desidad: densidad del fluido
    - viscosidad: viscosidad del fluido
    - presion: presión de entrada
    - diametro_nominal_func: función para obtener diámetro nominal
    - longitud_equivalente_func: función para obtener longitud equivalente
    - unidad_presion_salida: unidad para mostrar resultados (psi, kPa, Pa, kg/cm2, bar)
    - es_gas: True si el fluido es un gas (usa ecuaciones con factor de compresibilidad)
    
    Retorna:
    - df_resultados: DataFrame con resultados
    - P_out: presión de salida en la unidad especificada
    - long_acum: lista de longitudes acumuladas
    - presion_nodos: lista de presiones en nodos
    - elevacion_nodos: lista de elevaciones en nodos
    - P_in: presión de entrada en la unidad especificada
    """
    # --- Conversión de unidades según sistema ---
    if sistema == "Imperial":
        Q_inicial = flujovolum          # ft³/h
        rho = desidad                   # lb/ft³
        nu = viscosidad * 0.00107639    # Stokes a ft²/s
        P_in = presion                  # psi
        epsilon = 0.00015               # ft (acero comercial)
        factor_long = 1.0
        factor_elev = 1.0
        psi_to_lbft2 = 144.0
        unidad_presion_base = "psi"
        g = 32.174                      # ft/s²
    else:  # SI
        Q_inicial = flujovolum          # m³/h
        rho = desidad                   # kg/m³
        nu = viscosidad * 1e-6          # cSt a m²/s
        P_in = presion * 1000.0         # kPa a Pa
        epsilon = 0.00004572            # m
        factor_long = 1.0
        factor_elev = 1.0
        psi_to_lbft2 = 1.0
        unidad_presion_base = "Pa"
        g = 9.81                        # m/s²

    # --- Copiar DataFrame y agregar columnas de resultados ---
    df_resultados = df.copy()
    df_resultados['Flujo (unidades)'] = 0.0
    df_resultados['D_interno (m)' if sistema=='SI' else 'D_interno (ft)'] = 0.0
    df_resultados['Velocidad (m/s)' if sistema=='SI' else 'Velocidad (ft/s)'] = 0.0
    df_resultados['Re'] = 0
    df_resultados['f'] = 0.0
    df_resultados['Le (m)' if sistema=='SI' else 'Le (ft)'] = 0.0
    df_resultados['L_total (m)' if sistema=='SI' else 'L_total (ft)'] = 0.0
    df_resultados['dP_fricción (Pa)' if sistema=='SI' else 'dP_fricción (psi)'] = 0.0
    df_resultados['dP_elevación (Pa)' if sistema=='SI' else 'dP_elevación (psi)'] = 0.0
    df_resultados['P_salida (Pa)' if sistema=='SI' else 'P_salida (psi)'] = 0.0
    df_resultados['Factor_compresibilidad'] = 0.0

    P_actual = P_in
    Z_anterior = 0.0
    V_anterior = 0.0
    
    # Flujo actual que circula por la línea (en unidades base: m³/s o ft³/s)
    if sistema == "SI":
        Q_actual = Q_inicial / 3600.0   # m³/s
    else:
        Q_actual = Q_inicial / 3600.0   # ft³/s

    # Para gráficas: acumuladores de longitud y presión/elevación en nodos
    long_acum = [0.0]
    presion_nodos = [convertir_presion(P_in, unidad_presion_base, unidad_presion_salida)]
    elevacion_nodos = [df.iloc[0]['Elevación'] * factor_elev if not df.empty else 0.0]

    for idx, row in df.iterrows():
        # 1. Flujo que circula por esta línea
        Q_linea = Q_actual

        # 2. Diámetro interno
        D_in_pulg = diametro_nominal_func(row['Diámetro'], row['Cédula'])
        if isinstance(D_in_pulg, str):
            return f"Error en línea {idx+1}: {D_in_pulg}", None, None, None, None, None
        
        if sistema == "SI":
            D = D_in_pulg * 0.0254   # m
        else:
            D = D_in_pulg / 12.0     # ft

        # 3. Área y velocidad
        A = math.pi * (D ** 2) / 4.0
        V = Q_linea / A

        # 4. Reynolds
        Re = (V * D) / nu if nu > 0 else 1e6

        # 5. Factor de fricción
        e_D = epsilon / D
        f = haaland_friction_factor(Re, e_D)

        # 6. Longitud equivalente
        Le_pies = longitud_equivalente_func(row['Diámetro'], row['Accesorio'])
        if isinstance(Le_pies, str):
            return f"Error en línea {idx+1}: {Le_pies}", None, None, None, None, None
        
        if sistema == "SI":
            Le = Le_pies * 0.3048    # m
        else:
            Le = Le_pies             # ft

        # 7. Longitud total
        L_total = row['Longitud'] * factor_long + Le

        # 8. Factor de compresibilidad para gases
        if es_gas:
            # Z se calcula en función de la presión y temperatura
            # Para simplificar, asumimos Z basado en presión reducida
            # En una implementación más completa, se usaría una ecuación de estado
            P_critica = 37.2  # bar para aire (ejemplo)
            T_critica = 132.5  # K para aire (ejemplo)
            P_abs = P_actual / 14.5038  # convertir a bar
            # Aproximación de Z usando correlación simple
            Pr = P_abs / P_critica
            Tr = 1.2  # Asumir Tr = 1.2 para este ejemplo
            Z = 1.0 - Pr * 0.027
            Z = max(0.85, min(1.0, Z))  # Limitar Z
        else:
            Z = 1.0

        df_resultados.at[idx, 'Factor_compresibilidad'] = round(Z, 4)

        # 9. Caída por fricción (Darcy-Weisbach) - corregida para gases
        if sistema == "SI":
            # Para gases, usar la densidad a la presión actual
            rho_actual = rho * (P_actual / P_in) if es_gas else rho
            dP_fric = f * (L_total / D) * (rho_actual * V**2 / 2.0)  # Pa
        else:
            rho_actual = rho * (P_actual / P_in) if es_gas else rho
            dP_fric = f * (L_total / D) * (rho_actual * V**2 / 2.0) / psi_to_lbft2  # psi

        # 10. Caída por elevación (corregida para gases)
        Z_actual = row['Elevación'] * factor_elev
        if idx == 0:
            Z_anterior = Z_actual
        if sistema == "SI":
            # Para gases, usar la densidad promedio
            rho_promedio = (rho_actual + rho * (P_actual / P_in)) / 2.0 if es_gas else rho
            dP_elev = rho_promedio * g * (Z_actual - Z_anterior)  # Pa
        else:
            rho_promedio = (rho_actual + rho * (P_actual / P_in)) / 2.0 if es_gas else rho
            dP_elev = rho_promedio * (Z_actual - Z_anterior) / psi_to_lbft2  # psi

        # 11. Caída por cambio de velocidad
        if sistema == "SI":
            dP_vel = rho_actual * (V**2 - V_anterior**2) / 2.0  # Pa
        else:
            dP_vel = rho_actual * (V**2 - V_anterior**2) / (2.0 * psi_to_lbft2)  # psi
        if idx == 0:
            dP_vel = 0.0

        # 12. Presión de salida
        P_salida = P_actual - dP_fric - dP_elev - dP_vel

        # Guardar en DataFrame de resultados
        col_D = 'D_interno (m)' if sistema=='SI' else 'D_interno (ft)'
        col_V = 'Velocidad (m/s)' if sistema=='SI' else 'Velocidad (ft/s)'
        col_Le = 'Le (m)' if sistema=='SI' else 'Le (ft)'
        col_Ltot = 'L_total (m)' if sistema=='SI' else 'L_total (ft)'
        col_dPf = 'dP_fricción (Pa)' if sistema=='SI' else 'dP_fricción (psi)'
        col_dPe = 'dP_elevación (Pa)' if sistema=='SI' else 'dP_elevación (psi)'
        col_Ps = 'P_salida (Pa)' if sistema=='SI' else 'P_salida (psi)'

        # Flujo en unidades originales
        flujo_mostrar = Q_linea * 3600.0

        df_resultados.at[idx, 'Flujo (unidades)'] = round(flujo_mostrar, 4)
        df_resultados.at[idx, col_D] = round(D, 4)
        df_resultados.at[idx, col_V] = round(V, 2)
        df_resultados.at[idx, 'Re'] = round(Re, 0)
        df_resultados.at[idx, 'f'] = round(f, 5)
        df_resultados.at[idx, col_Le] = round(Le, 2)
        df_resultados.at[idx, col_Ltot] = round(L_total, 2)
        df_resultados.at[idx, col_dPf] = round(dP_fric, 4)
        df_resultados.at[idx, col_dPe] = round(dP_elev, 4)
        df_resultados.at[idx, col_Ps] = round(P_salida, 4)

        # Actualizar para siguiente iteración
        P_actual = P_salida
        Z_anterior = Z_actual
        V_anterior = V

        # Actualizar el flujo circulante con el flujo adicional
        Q_adicional = row.get('Flujo adicional', 0.0)
        if sistema == "SI":
            Q_adicional_base = Q_adicional / 3600.0  # m³/s
        else:
            Q_adicional_base = Q_adicional / 3600.0  # ft³/s
        Q_actual = Q_actual + Q_adicional_base

        # Acumular longitudes para gráficas
        long_acum.append(long_acum[-1] + row['Longitud'] * factor_long)
        presion_nodos.append(convertir_presion(P_salida, 
                                               "Pa" if sistema == "SI" else "psi", 
                                               unidad_presion_salida))
        elevacion_nodos.append(Z_actual)

    # Convertir P_in a la unidad de salida
    P_in_convertida = convertir_presion(P_in, unidad_presion_base, unidad_presion_salida)
    
    # Convertir P_salida a la unidad de salida
    P_salida_convertida = convertir_presion(P_actual, 
                                           "Pa" if sistema == "SI" else "psi", 
                                           unidad_presion_salida)

    return df_resultados, P_salida_convertida, long_acum, presion_nodos, elevacion_nodos, P_in_convertida

def calcular_caida_presion_gas(P1, P2, L, D, Q, rho, f, Z_avg=1.0):
    """
    Calcula la caída de presión para gases usando la ecuación generalizada
    
    Parámetros:
    - P1: Presión de entrada (Pa o psi)
    - P2: Presión de salida (Pa o psi)
    - L: Longitud de la tubería (m o ft)
    - D: Diámetro interno (m o ft)
    - Q: Caudal (m³/s o ft³/s)
    - rho: Densidad del gas (kg/m³ o lb/ft³)
    - f: Factor de fricción
    - Z_avg: Factor de compresibilidad promedio
    
    Retorna:
    - dP: Caída de presión
    """
    # Ecuación generalizada para flujo de gas:
    # P1² - P2² = (f * L * (Q²) * rho * Z_avg * R * T) / (D * A²)
    # Para simplificar, usamos la forma simplificada
    A = math.pi * (D ** 2) / 4.0
    V = Q / A
    dP = f * (L / D) * (rho * V**2 / 2.0) * Z_avg
    return dP