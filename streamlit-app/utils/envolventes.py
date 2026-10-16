# envolventes.py
import numpy as np
from CoolProp.CoolProp import PropsSI, FluidsList

def get_fluid_list():
    """Obtiene la lista de fluidos disponibles en CoolProp."""
    return sorted(FluidsList())

def get_saturation_curve(fluid, T_min=None, T_max=None, n_points=300):
    """Calcula la curva de saturación (líquido y vapor)."""
    try:
        T_crit = PropsSI('Tcrit', fluid)
        T_triple = PropsSI('Ttriple', fluid)

        if T_min is None:
            T_min = T_triple + 0.1
        if T_max is None:
            T_max = T_crit - 0.1

        T_vals = np.linspace(T_min, T_max, n_points)
        T_vals = np.clip(T_vals, T_triple + 0.1, T_crit - 0.1)

        P_liquid = np.zeros_like(T_vals)
        P_vapor = np.zeros_like(T_vals)
        s_liquid = np.zeros_like(T_vals)
        s_vapor = np.zeros_like(T_vals)
        h_liquid = np.zeros_like(T_vals)
        h_vapor = np.zeros_like(T_vals)

        for i, T in enumerate(T_vals):
            try:
                P = PropsSI('P', 'T', T, 'Q', 0, fluid)
                P_liquid[i] = P
                P_vapor[i] = P
                s_liquid[i] = PropsSI('S', 'T', T, 'Q', 0, fluid)
                s_vapor[i] = PropsSI('S', 'T', T, 'Q', 1, fluid)
                h_liquid[i] = PropsSI('H', 'T', T, 'Q', 0, fluid)
                h_vapor[i] = PropsSI('H', 'T', T, 'Q', 1, fluid)
            except:
                P_liquid[i] = np.nan
                P_vapor[i] = np.nan
                s_liquid[i] = np.nan
                s_vapor[i] = np.nan
                h_liquid[i] = np.nan
                h_vapor[i] = np.nan

        mask = ~np.isnan(P_liquid)
        return {
            'T': T_vals[mask],
            'P_liquid': P_liquid[mask],
            'P_vapor': P_vapor[mask],
            's_liquid': s_liquid[mask],
            's_vapor': s_vapor[mask],
            'h_liquid': h_liquid[mask],
            'h_vapor': h_vapor[mask],
        }
    except Exception as e:
        raise Exception(f"Error al calcular curva de saturación: {e}")

def get_fluid_properties(fluid, T, P):
    """Obtiene propiedades en un punto (T, P)."""
    try:
        return {
            'T': T,
            'P': P,
            'D': PropsSI('D', 'T', T, 'P', P, fluid),
            'H': PropsSI('H', 'T', T, 'P', P, fluid),
            'S': PropsSI('S', 'T', T, 'P', P, fluid),
            'U': PropsSI('U', 'T', T, 'P', P, fluid),
            'Cp': PropsSI('C', 'T', T, 'P', P, fluid),
            'Cv': PropsSI('Cvmass', 'T', T, 'P', P, fluid),
            'Visc': PropsSI('V', 'T', T, 'P', P, fluid),
            'Cond': PropsSI('L', 'T', T, 'P', P, fluid),
            'Z': PropsSI('Z', 'T', T, 'P', P, fluid),
            'Q': PropsSI('Q', 'T', T, 'P', P, fluid),
        }
    except:
        return None

def generate_isobar_points(fluid, P, T_min, T_max, n_points=100):
    """Genera puntos para una isobara en el diagrama T-s (T vs s) a presión constante."""
    try:
        T_vals = np.linspace(T_min, T_max, n_points)
        s_vals = np.zeros_like(T_vals)
        valid = np.ones(len(T_vals), dtype=bool)
        for i, T in enumerate(T_vals):
            try:
                s_vals[i] = PropsSI('S', 'T', T, 'P', P, fluid)
            except:
                valid[i] = False
        return T_vals[valid], s_vals[valid]
    except:
        return np.array([]), np.array([])

def generate_isotherm_points(fluid, T, P_min, P_max, n_points=100):
    """Genera puntos para una isoterma en el diagrama P-h (P vs h) a temperatura constante."""
    try:
        P_vals = np.linspace(P_min, P_max, n_points)
        h_vals = np.zeros_like(P_vals)
        valid = np.ones(len(P_vals), dtype=bool)
        for i, P in enumerate(P_vals):
            try:
                h_vals[i] = PropsSI('H', 'T', T, 'P', P, fluid)
            except:
                valid[i] = False
        return P_vals[valid], h_vals[valid]
    except:
        return np.array([]), np.array([])

def generate_quality_lines(fluid, quality, T_min, T_max, n_points=100):
    """Genera puntos para una línea de calidad constante en el diagrama T-s."""
    try:
        T_vals = np.linspace(T_min, T_max, n_points)
        s_vals = np.zeros_like(T_vals)
        valid = np.ones(len(T_vals), dtype=bool)
        for i, T in enumerate(T_vals):
            try:
                s_vals[i] = PropsSI('S', 'T', T, 'Q', quality, fluid)
            except:
                valid[i] = False
        return T_vals[valid], s_vals[valid]
    except:
        return np.array([]), np.array([])

def get_critical_point(fluid):
    """Obtiene las coordenadas del punto crítico."""
    try:
        T_crit = PropsSI('Tcrit', fluid)
        P_crit = PropsSI('Pcrit', fluid)
        s_crit = PropsSI('S', 'T', T_crit, 'P', P_crit, fluid)
        h_crit = PropsSI('H', 'T', T_crit, 'P', P_crit, fluid)
        return {
            'T': T_crit,
            'P': P_crit,
            'S': s_crit,
            'H': h_crit
        }
    except:
        return None

def calcular_envolvente(fluid, T_min, T_max, plot_type, 
                        show_isobars, num_isobars,
                        show_isotherms, num_isotherms,
                        show_quality, quality_vals,
                        op_point, show_op_point):
    """
    Función principal que calcula todos los datos necesarios para graficar la envolvente.
    
    Retorna:
    - sat_data: datos de saturación
    - op_props: propiedades del punto de operación
    - aux_lines: datos de líneas auxiliares
    - critical_point: punto crítico
    - error: mensaje de error (None si no hay error)
    """
    try:
        # Calcular curva de saturación
        sat_data = get_saturation_curve(fluid, T_min=T_min, T_max=T_max, n_points=300)
        if sat_data is None:
            return None, None, None, None, "No se pudo calcular la curva de saturación."
        
        # Punto crítico
        critical_point = get_critical_point(fluid)
        
        # Punto de operación
        op_props = None
        if show_op_point and op_point is not None:
            op_props = get_fluid_properties(fluid, op_point['T'], op_point['P'])
        
        # Líneas auxiliares
        aux_lines = {
            'isobars': [],
            'isotherms': [],
            'quality_lines': []
        }
        
        # Isobaras (solo en T-s)
        if show_isobars and plot_type == 'Ts':
            try:
                P_min = PropsSI('P', 'T', T_min, 'Q', 0, fluid)
                P_max = PropsSI('P', 'T', T_max, 'Q', 0, fluid)
                P_vals = np.linspace(P_min, P_max, num_isobars + 2)[1:-1]
                for P in P_vals:
                    T_iso, s_iso = generate_isobar_points(fluid, P, T_min, T_max, n_points=100)
                    if len(T_iso) > 0:
                        aux_lines['isobars'].append({'P': P, 'T': T_iso, 's': s_iso})
            except:
                pass
        
        # Isotermas (solo en P-h)
        if show_isotherms and plot_type == 'Ph':
            try:
                T_vals = np.linspace(T_min, T_max, num_isotherms + 2)[1:-1]
                for T in T_vals:
                    P_iso, h_iso = generate_isotherm_points(fluid, T, 1e3, 1e7, n_points=100)
                    if len(P_iso) > 0:
                        aux_lines['isotherms'].append({'T': T, 'P': P_iso, 'h': h_iso})
            except:
                pass
        
        # Líneas de calidad constante
        if show_quality and plot_type == 'Ts':
            for q in quality_vals:
                T_q, s_q = generate_quality_lines(fluid, q, T_min, T_max, n_points=100)
                if len(T_q) > 0:
                    aux_lines['quality_lines'].append({'q': q, 'T': T_q, 's': s_q})
        
        return sat_data, op_props, aux_lines, critical_point, None
        
    except Exception as e:
        return None, None, None, None, f"Error durante el cálculo: {e}"

def preparar_datos_grafica(sat_data, op_props, aux_lines, critical_point, fluid, plot_type):
    """
    Prepara los datos para graficar con Plotly.
    
    Retorna:
    - x_liquid: coordenadas x del líquido saturado
    - x_vapor: coordenadas x del vapor saturado
    - y_vals: coordenadas y
    - x_label: etiqueta del eje x
    - y_label: etiqueta del eje y
    - title: título de la gráfica
    - op_x: coordenada x del punto de operación
    - op_y: coordenada y del punto de operación
    - x_crit: coordenada x del punto crítico
    - y_crit: coordenada y del punto crítico
    """
    if plot_type == 'Ts':
        x_liquid = sat_data['s_liquid'] / 1000
        x_vapor = sat_data['s_vapor'] / 1000
        y_vals = sat_data['T']
        x_label = "Entropía, s [kJ/kg·K]"
        y_label = "Temperatura, T [K]"
        title = f"Diagrama T-s para {fluid}"
        
        if op_props:
            op_x = op_props['S'] / 1000
            op_y = op_props['T']
        else:
            op_x, op_y = None, None
        
        if critical_point:
            x_crit = critical_point['S'] / 1000
            y_crit = critical_point['T']
        else:
            x_crit, y_crit = None, None
            
    else:  # Ph
        x_liquid = sat_data['h_liquid'] / 1000
        x_vapor = sat_data['h_vapor'] / 1000
        y_vals = sat_data['P_vapor'] / 1e5
        x_label = "Entalpía, h [kJ/kg]"
        y_label = "Presión, P [bar]"
        title = f"Diagrama P-h para {fluid}"
        
        if op_props:
            op_x = op_props['H'] / 1000
            op_y = op_props['P'] / 1e5
        else:
            op_x, op_y = None, None
        
        if critical_point:
            x_crit = critical_point['H'] / 1000
            y_crit = critical_point['P'] / 1e5
        else:
            x_crit, y_crit = None, None
    
    return {
        'x_liquid': x_liquid,
        'x_vapor': x_vapor,
        'y_vals': y_vals,
        'x_label': x_label,
        'y_label': y_label,
        'title': title,
        'op_x': op_x,
        'op_y': op_y,
        'x_crit': x_crit,
        'y_crit': y_crit
    }