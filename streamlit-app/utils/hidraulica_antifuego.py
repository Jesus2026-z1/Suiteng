# hidraulica_antifuego.py
import math
import pandas as pd

def convertir_presion(valor, unidad_origen, unidad_destino):
    # (función sin cambios, igual que antes)
    if unidad_origen in ["psi", "PSI"]:
        valor_pa = valor * 6894.76
    elif unidad_origen in ["kPa", "KPa"]:
        valor_pa = valor * 1000
    elif unidad_origen in ["Pa", "pa"]:
        valor_pa = valor
    elif unidad_origen in ["kg/cm2", "kg/cm²"]:
        valor_pa = valor * 98066.5
    elif unidad_origen in ["bar", "Bar"]:
        valor_pa = valor * 100000
    else:
        valor_pa = valor

    if unidad_destino in ["psi", "PSI"]:
        return valor_pa / 6894.76
    elif unidad_destino in ["kPa", "KPa"]:
        return valor_pa / 1000
    elif unidad_destino in ["Pa", "pa"]:
        return valor_pa
    elif unidad_destino in ["kg/cm2", "kg/cm²"]:
        return valor_pa / 98066.5
    elif unidad_destino in ["bar", "Bar"]:
        return valor_pa / 100000
    else:
        return valor_pa

def calcular_analisis_antifuego(df, sistema, desidad, viscosidad, presion_diseno,
                                diametro_nominal_func, longitud_equivalente_func,
                                unidad_presion_salida="psi", C_factor=120):
    """
    Realiza el análisis hidráulico para sistemas de rociadores según NFPA 15.
    Usa Hazen-Williams para pérdidas por fricción y considera presión de velocidad.
    Retorna: df_resultados, P_inicial, P_final, long_acum, presion_nodos, elevacion_nodos
    """
    # Configuración de unidades
    if sistema == "Imperial":
        rho = desidad          # lb/ft³
        P_ultimo = presion_diseno  # psi
        psi_to_lbft2 = 144.0
        unidad_presion_base = "psi"
        flow_to_gpm = 448.831      # ft³/s a gpm
    else:
        rho = desidad          # kg/m³
        P_ultimo = presion_diseno * 1000.0  # kPa a Pa
        unidad_presion_base = "Pa"
        flow_to_Lmin = 60000.0     # m³/s a L/min
        pres_to_bar = 100000.0     # Pa a bar
        long_to_ft = 0.3048        # m a ft

    # Verificar que los números de línea sean únicos y estén en orden (fuente -> último rociador)
    # Asegurar que el orden sea ascendente
    df = df.sort_values(by='Número de Línea').reset_index(drop=True)

    # Invertir para el cálculo desde el último rociador hacia la fuente
    # df_calc = df.iloc[::-1].reset_index(drop=True)

    df_calc = df.copy()   # No invertir, procesar en el orden ingresado
    df_resultados = df.copy()

    # Variables de cálculo
    P_nodo = P_ultimo
    flujo_acumulado = 0.0       # en unidades base (ft³/s o m³/s)
    Z_nodo = df_calc.iloc[0]['Elevación'] if not df_calc.empty else 0.0

    lista_resultados = []  # para construir la tabla final

    # Recorrer desde el último tramo hasta el primero
    for idx, row in df_calc.iterrows():
        # 1. Obtener K y determinar si es el último rociador (idx == 0)
        K = row['K (rociador)']
        es_ultimo = (idx == 0)

        # 2. Calcular flujo del rociador
        if sistema == "Imperial":
            if es_ultimo:
                Q_rociador_gpm = K * math.sqrt(max(P_nodo, 0.0))
            else:
                # Iteración para presión normal
                Q_rociador_gpm = K * math.sqrt(max(P_nodo, 0.0))
                for _ in range(5):
                    Q_total_gpm = Q_rociador_gpm + flujo_acumulado * flow_to_gpm + row['Flujo adicional']
                    D_in = diametro_nominal_func(row['Diámetro'], row['Cédula'])
                    if isinstance(D_in, str):
                        return f"Error en línea {row['Número de Línea']}: {D_in}", None, None, None, None, None
                    Pv_psi = 0.001123 * (Q_total_gpm ** 2) / (D_in ** 4)
                    Pn_psi = P_nodo - Pv_psi
                    if Pn_psi < 0:
                        Pn_psi = 0.0
                    Q_nuevo_gpm = K * math.sqrt(Pn_psi)
                    if abs(Q_nuevo_gpm - Q_rociador_gpm) < 1e-6:
                        Q_rociador_gpm = Q_nuevo_gpm
                        break
                    Q_rociador_gpm = Q_nuevo_gpm
                P_efectiva = Pn_psi if 'Pn_psi' in locals() else P_nodo
            Q_rociador = Q_rociador_gpm / flow_to_gpm
            if es_ultimo:
                P_efectiva = P_nodo
        else:  # SI
            P_bar = P_nodo / pres_to_bar
            if es_ultimo:
                Q_rociador_Lmin = K * math.sqrt(max(P_bar, 0.0))
            else:
                Q_rociador_Lmin = K * math.sqrt(max(P_bar, 0.0))
                for _ in range(5):
                    Q_total_Lmin = Q_rociador_Lmin + flujo_acumulado * flow_to_Lmin + row['Flujo adicional']
                    D_in = diametro_nominal_func(row['Diámetro'], row['Cédula'])
                    if isinstance(D_in, str):
                        return f"Error en línea {row['Número de Línea']}: {D_in}", None, None, None, None, None
                    D_mm = D_in * 25.4
                    Pv_bar = 2.249 * (Q_total_Lmin ** 2) / (D_mm ** 4)
                    Pn_bar = P_bar - Pv_bar
                    if Pn_bar < 0:
                        Pn_bar = 0.0
                    Q_nuevo_Lmin = K * math.sqrt(Pn_bar)
                    if abs(Q_nuevo_Lmin - Q_rociador_Lmin) < 1e-6:
                        Q_rociador_Lmin = Q_nuevo_Lmin
                        break
                    Q_rociador_Lmin = Q_nuevo_Lmin
                P_efectiva = Pn_bar * pres_to_bar if 'Pn_bar' in locals() else P_nodo
            Q_rociador = Q_rociador_Lmin / flow_to_Lmin
            if es_ultimo:
                P_efectiva = P_nodo

        # 3. Flujo total que circula por este tramo (acumulado + rociador + adicional)
        flujo_total = flujo_acumulado + Q_rociador + row['Flujo adicional']

        # 4. Diámetro interno (en pulgadas)
        D_in = diametro_nominal_func(row['Diámetro'], row['Cédula'])
        if isinstance(D_in, str):
            return f"Error en línea {row['Número de Línea']}: {D_in}", None, None, None, None, None

        # 5. Longitud equivalente (la función devuelve la suma total en pies)
        Le_pies = longitud_equivalente_func(row['Diámetro'], row['Accesorio'])
        if isinstance(Le_pies, str):
            return f"Error en línea {row['Número de Línea']}: {Le_pies}", None, None, None, None, None

        # 6. Longitud total
        if sistema == "Imperial":
            L_total_ft = row['Longitud'] + Le_pies
        else:
            L_total_m = row['Longitud'] + Le_pies * long_to_ft

        # 7. Pérdida por fricción con Hazen-Williams
        if sistema == "Imperial":
            Q_gpm = flujo_total * flow_to_gpm
            p_fric_psi_per_ft = (4.52 * (Q_gpm ** 1.85)) / (C_factor ** 1.85 * (D_in ** 4.87))
            dP_fric = p_fric_psi_per_ft * L_total_ft
        else:
            Q_Lmin = flujo_total * flow_to_Lmin
            D_mm = D_in * 25.4
            p_fric_bar_per_m = 6.05 * (Q_Lmin ** 1.85) / (C_factor ** 1.85 * (D_mm ** 4.87)) * 1e5
            dP_fric_bar = p_fric_bar_per_m * L_total_m
            dP_fric = dP_fric_bar * 100000

        # 8. Pérdida por elevación
        if idx < len(df_calc) - 1:
            Z_anterior = df_calc.iloc[idx + 1]['Elevación']
            if sistema == "Imperial":
                dP_elev = rho * (Z_anterior - Z_nodo) / psi_to_lbft2
            else:
                dP_elev = rho * 9.81 * (Z_anterior - Z_nodo)
        else:
            dP_elev = 0.0

        # 9. Presión aguas arriba
        P_aguas_arriba = P_nodo + dP_fric + dP_elev

        # 10. Guardar resultados para este tramo (en unidades de visualización)
        if sistema == "Imperial":
            flujo_acum_mostrar = flujo_total * flow_to_gpm
            flujo_rociador_mostrar = Q_rociador * flow_to_gpm
            P_rociador = P_nodo
            P_arriba = P_aguas_arriba
            D_mostrar = D_in
            V = flujo_total / (math.pi * (D_in/12)**2 / 4) if D_in > 0 else 0
            Le_mostrar = Le_pies
            Ltot_mostrar = L_total_ft
            dPf_mostrar = dP_fric
            dPe_mostrar = dP_elev
            if not es_ultimo:
                Pv_mostrar = Pv_psi if 'Pv_psi' in locals() else 0.0
                Pn_mostrar = P_efectiva
            else:
                Pv_mostrar = 0.0
                Pn_mostrar = P_nodo
        else:
            flujo_acum_mostrar = flujo_total * flow_to_Lmin
            flujo_rociador_mostrar = Q_rociador * flow_to_Lmin
            P_rociador = P_nodo / 1000.0
            P_arriba = P_aguas_arriba / 1000.0
            D_mostrar = D_in * 25.4
            V = flujo_total / (math.pi * (D_in*0.0254)**2 / 4) if D_in > 0 else 0
            Le_mostrar = Le_pies * 0.3048
            Ltot_mostrar = L_total_m
            dPf_mostrar = dP_fric / 1000.0
            dPe_mostrar = dP_elev / 1000.0
            if not es_ultimo:
                Pv_mostrar = Pv_bar * 1000 if 'Pv_bar' in locals() else 0.0
                Pn_mostrar = P_efectiva / 1000.0
            else:
                Pv_mostrar = 0.0
                Pn_mostrar = P_nodo / 1000.0

        # Almacenar en la lista (en orden inverso, porque recorremos desde el último)
        # Usaremos el número de línea como identificador
        lista_resultados.append({
            'Número de Línea': row['Número de Línea'],
            'Flujo acumulado': round(flujo_acum_mostrar, 2),
            'Flujo rociador': round(flujo_rociador_mostrar, 2),
            'Presión en rociador': round(P_rociador, 4),
            'Presión aguas arriba': round(P_arriba, 4),
            'Diámetro interno': round(D_mostrar, 4),
            'Velocidad': round(V, 2),
            'Re': float('nan'),
            'f': float('nan'),
            'Longitud equivalente': round(Le_mostrar, 2),
            'Longitud total': round(Ltot_mostrar, 2),
            'dP_fricción': round(dPf_mostrar, 4),
            'dP_elevación': round(dPe_mostrar, 4),
            'Pv (velocidad)': round(Pv_mostrar, 4),
            'Pn (normal)': round(Pn_mostrar, 4)
        })

        # Actualizar para el siguiente tramo (más cerca de la fuente)
        P_nodo = P_aguas_arriba
        flujo_acumulado = flujo_total
        Z_nodo = row['Elevación']

    # Reordenar los resultados para que estén en el orden original (fuente -> último rociador)
    # lista_resultados está en orden inverso (último a primero), lo invertimos
    # df_resultados = pd.DataFrame(lista_resultados[::-1])

    # Por esta:
    df_resultados = pd.DataFrame(lista_resultados)   # No invertir resultados

    # Convertir presiones a la unidad de salida
    P_inicial_convertida = convertir_presion(P_ultimo, unidad_presion_base, unidad_presion_salida)
    P_final_convertida = convertir_presion(P_nodo, unidad_presion_base, unidad_presion_salida)

    # Replace the section that builds the graph arrays (near the end of the function)
# Find this section and replace it:

    # Arrays para gráficas (desde el rociador más lejano hasta la fuente)
    long_acum = [0.0]
    presion_nodos = [P_inicial_convertida]  # Empezar con presión del rociador más lejano
    elevacion_nodos = [df_calc.iloc[0]['Elevación'] if not df_calc.empty else 0.0]

    # Recorrer en orden de cálculo (del rociador más lejano hacia la fuente)
    for i, idx in enumerate(df_calc.index):
        row = df_calc.loc[idx]
        long_acum.append(long_acum[-1] + row['Longitud'])
        
        # Obtener la presión en rociador para este tramo
        res_fila = df_resultados[df_resultados['Número de Línea'] == row['Número de Línea']]
        if not res_fila.empty:
            # Usar "Presión aguas arriba" que es la presión después de este tramo
            pres_aguas_arriba = res_fila['Presión aguas arriba'].values[0]
            if sistema == "Imperial":
                pres_conv = convertir_presion(pres_aguas_arriba, "psi", unidad_presion_salida)
            else:
                pres_conv = convertir_presion(pres_aguas_arriba * 1000, "Pa", unidad_presion_salida)
            presion_nodos.append(pres_conv)
        else:
            presion_nodos.append(None)
        
        elevacion_nodos.append(row['Elevación'])

    return df_resultados, P_inicial_convertida, P_final_convertida, long_acum, presion_nodos, elevacion_nodos