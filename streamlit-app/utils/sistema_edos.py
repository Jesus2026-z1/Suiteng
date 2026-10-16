# sistema_edos.py
import numpy as np
from sympy import sympify, SympifyError, symbols, lambdify

def rk4_sistema(f_list, t0, y0, t_end, h):
    """
    Resuelve un sistema de EDOs de primer orden con RK4.
    
    Parámetros:
    - f_list: lista de funciones numéricas f_i(t, y1, y2, ..., yn)
    - t0: tiempo inicial
    - y0: lista de condiciones iniciales [y1(t0), y2(t0), ...]
    - t_end: tiempo final
    - h: tamaño del paso
    
    Retorna:
    - t_vals: array con los valores de t
    - y_vals: array con los valores de las variables
    """
    y0 = np.array(y0, dtype=float)
    n = len(y0)
    n_steps = int(np.ceil((t_end - t0) / h))
    t_vals = np.zeros(n_steps + 1)
    y_vals = np.zeros((n_steps + 1, n))
    t_vals[0] = t0
    y_vals[0] = y0

    t = t0
    y = y0.copy()

    for i in range(n_steps):
        k1 = np.array([f(t, *y) for f in f_list])
        k2 = np.array([f(t + h/2, *(y + h/2 * k1)) for f in f_list])
        k3 = np.array([f(t + h/2, *(y + h/2 * k2)) for f in f_list])
        k4 = np.array([f(t + h, *(y + h * k3)) for f in f_list])

        y = y + (h/6) * (k1 + 2*k2 + 2*k3 + k4)
        t = t + h

        t_vals[i+1] = t
        y_vals[i+1] = y

        if t >= t_end:
            break

    return t_vals[:i+2], y_vals[:i+2]

def rk2_sistema(f_list, t0, y0, t_end, h):
    """
    Resuelve un sistema de EDOs de primer orden con RK2 (Heun).
    
    Parámetros:
    - f_list: lista de funciones numéricas f_i(t, y1, y2, ..., yn)
    - t0: tiempo inicial
    - y0: lista de condiciones iniciales [y1(t0), y2(t0), ...]
    - t_end: tiempo final
    - h: tamaño del paso
    
    Retorna:
    - t_vals: array con los valores de t
    - y_vals: array con los valores de las variables
    """
    y0 = np.array(y0, dtype=float)
    n = len(y0)
    n_steps = int(np.ceil((t_end - t0) / h))
    t_vals = np.zeros(n_steps + 1)
    y_vals = np.zeros((n_steps + 1, n))
    t_vals[0] = t0
    y_vals[0] = y0

    t = t0
    y = y0.copy()

    for i in range(n_steps):
        k1 = np.array([f(t, *y) for f in f_list])
        k2 = np.array([f(t + h, *(y + h * k1)) for f in f_list])

        y = y + (h/2) * (k1 + k2)
        t = t + h

        t_vals[i+1] = t
        y_vals[i+1] = y

        if t >= t_end:
            break

    return t_vals[:i+2], y_vals[:i+2]

def rk1_sistema(f_list, t0, y0, t_end, h):
    """
    Resuelve un sistema de EDOs de primer orden con Euler (RK1).
    
    Parámetros:
    - f_list: lista de funciones numéricas f_i(t, y1, y2, ..., yn)
    - t0: tiempo inicial
    - y0: lista de condiciones iniciales [y1(t0), y2(t0), ...]
    - t_end: tiempo final
    - h: tamaño del paso
    
    Retorna:
    - t_vals: array con los valores de t
    - y_vals: array con los valores de las variables
    """
    y0 = np.array(y0, dtype=float)
    n = len(y0)
    n_steps = int(np.ceil((t_end - t0) / h))
    t_vals = np.zeros(n_steps + 1)
    y_vals = np.zeros((n_steps + 1, n))
    t_vals[0] = t0
    y_vals[0] = y0

    t = t0
    y = y0.copy()

    for i in range(n_steps):
        k1 = np.array([f(t, *y) for f in f_list])
        y = y + h * k1
        t = t + h

        t_vals[i+1] = t
        y_vals[i+1] = y

        if t >= t_end:
            break

    return t_vals[:i+2], y_vals[:i+2]

def parsear_sistema(func_strs, num_eqs, t0, y0_vals):
    """
    Parsea las funciones del sistema usando SymPy
    
    Parámetros:
    - func_strs: lista de strings con las funciones
    - num_eqs: número de ecuaciones
    - t0: tiempo inicial (para verificación)
    - y0_vals: condiciones iniciales (para verificación)
    
    Retorna:
    - f_numeric: lista de funciones numéricas
    - syms: lista de símbolos
    - error: mensaje de error (None si no hay error)
    """
    # Símbolos: t, y1, y2, ...
    sym_order = ['t'] + [f'y{i}' for i in range(1, num_eqs + 1)]
    syms = symbols(sym_order)
    
    f_numeric = []
    for i, f_str in enumerate(func_strs, start=1):
        try:
            expr = sympify(f_str)
            f_num = lambdify(syms, expr, modules=['numpy'])
            # Verificar evaluación en condiciones iniciales
            test_args = [t0] + y0_vals
            f_num(*test_args)
            f_numeric.append(f_num)
        except SympifyError:
            return None, None, f"Error de sintaxis en f{i}: '{f_str}'. Usa t, y1, y2, ..."
        except Exception as e:
            return None, None, f"Error en f{i}: {e}"
    
    return f_numeric, syms, None

def resolver_sistema(func_strs, num_eqs, t0, y0_vals, t_final, h, metodo='rk4'):
    """
    Función principal para resolver sistemas de EDOs
    
    Parámetros:
    - func_strs: lista de strings con las funciones
    - num_eqs: número de ecuaciones
    - t0: tiempo inicial
    - y0_vals: condiciones iniciales
    - t_final: tiempo final
    - h: tamaño del paso
    - metodo: 'rk1', 'rk2' o 'rk4'
    
    Retorna:
    - t_vals: array con los valores de t
    - y_vals: array con los valores de las variables
    - mensaje_error: string con mensaje de error (None si no hay error)
    """
    # Parsear las funciones
    f_numeric, syms, error = parsear_sistema(func_strs, num_eqs, t0, y0_vals)
    if error:
        return None, None, error
    
    # Resolver el sistema
    try:
        if metodo == 'rk4':
            t_vals, y_vals = rk4_sistema(f_numeric, t0, y0_vals, t_final, h)
        elif metodo == 'rk2':
            t_vals, y_vals = rk2_sistema(f_numeric, t0, y0_vals, t_final, h)
        else:  # rk1
            t_vals, y_vals = rk1_sistema(f_numeric, t0, y0_vals, t_final, h)
        
        if len(t_vals) == 0:
            return None, None, "No se generaron puntos. Revisa el intervalo y el paso."
        
        return t_vals, y_vals, None
        
    except OverflowError:
        return None, None, "Desbordamiento numérico. Reduce el paso 'h'."
    except Exception as e:
        return None, None, f"Error en la integración: {e}"

def get_metodos_disponibles():
    """Retorna los métodos de integración disponibles"""
    return {
        'rk4': 'Runge-Kutta 4to orden',
        'rk2': 'Runge-Kutta 2do orden (Heun)',
        'rk1': 'Euler (RK1)'
    }