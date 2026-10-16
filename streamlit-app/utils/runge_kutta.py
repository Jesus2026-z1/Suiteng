# runge_kutta.py
import numpy as np
from sympy import sympify, SympifyError, symbols, lambdify

def rk4(f, x0, y0, x_end, h):
    """
    Método Runge-Kutta de 4to orden para resolver EDOs de primer orden
    
    Parámetros:
    - f: función dy/dx = f(x, y)
    - x0: valor inicial de x
    - y0: valor inicial de y
    - x_end: valor final de x
    - h: tamaño del paso
    
    Retorna:
    - xs: array con los valores de x
    - ys: array con los valores de y
    """
    xs = [x0]
    ys = [y0]
    x = x0
    y = y0
    
    n_steps = int(np.ceil((x_end - x0) / h))
    for _ in range(n_steps):
        if x >= x_end:
            break
        
        k1 = f(x, y)
        k2 = f(x + h/2, y + h*k1/2)
        k3 = f(x + h/2, y + h*k2/2)
        k4 = f(x + h, y + h*k3)
        
        y = y + (h/6)*(k1 + 2*k2 + 2*k3 + k4)
        x = x + h
        
        xs.append(x)
        ys.append(y)
    
    return np.array(xs), np.array(ys)

def rk2(f, x0, y0, x_end, h):
    """
    Método Runge-Kutta de 2do orden (Heun)
    
    Parámetros:
    - f: función dy/dx = f(x, y)
    - x0: valor inicial de x
    - y0: valor inicial de y
    - x_end: valor final de x
    - h: tamaño del paso
    
    Retorna:
    - xs: array con los valores de x
    - ys: array con los valores de y
    """
    xs = [x0]
    ys = [y0]
    x = x0
    y = y0
    
    n_steps = int(np.ceil((x_end - x0) / h))
    for _ in range(n_steps):
        if x >= x_end:
            break
        
        k1 = f(x, y)
        k2 = f(x + h, y + h*k1)
        
        y = y + (h/2)*(k1 + k2)
        x = x + h
        
        xs.append(x)
        ys.append(y)
    
    return np.array(xs), np.array(ys)

def rk1(f, x0, y0, x_end, h):
    """
    Método de Euler (Runge-Kutta de 1er orden)
    
    Parámetros:
    - f: función dy/dx = f(x, y)
    - x0: valor inicial de x
    - y0: valor inicial de y
    - x_end: valor final de x
    - h: tamaño del paso
    
    Retorna:
    - xs: array con los valores de x
    - ys: array con los valores de y
    """
    xs = [x0]
    ys = [y0]
    x = x0
    y = y0
    
    n_steps = int(np.ceil((x_end - x0) / h))
    for _ in range(n_steps):
        if x >= x_end:
            break
        
        y = y + h * f(x, y)
        x = x + h
        
        xs.append(x)
        ys.append(y)
    
    return np.array(xs), np.array(ys)

def resolver_edo(func_str, x0, y0, x_end, h, metodo='rk4'):
    """
    Función principal para resolver EDOs
    
    Parámetros:
    - func_str: string con la función f(x, y)
    - x0: valor inicial de x
    - y0: valor inicial de y
    - x_end: valor final de x
    - h: tamaño del paso
    - metodo: 'rk1', 'rk2' o 'rk4'
    
    Retorna:
    - xs: array con los valores de x
    - ys: array con los valores de y
    - mensaje_error: string con mensaje de error (None si no hay error)
    """
    try:
        x_sym, y_sym = symbols('x y')
        expr = sympify(func_str)
        f_numerica = lambdify((x_sym, y_sym), expr, modules=['numpy'])
        
        # Verificación rápida
        f_numerica(0.0, 1.0)
        
    except SympifyError:
        return None, None, f"Error de sintaxis en la ecuación: '{func_str}'. Revisa que uses variables 'x' e 'y'."
    except Exception as e:
        return None, None, f"Error al interpretar la función: {e}"
    
    # Seleccionar el método
    try:
        if metodo == 'rk1':
            xs, ys = rk1(f_numerica, x0, y0, x_end, h)
        elif metodo == 'rk2':
            xs, ys = rk2(f_numerica, x0, y0, x_end, h)
        elif metodo == 'euler_implicito':
            xs, ys = euler_implicito(f_numerica, x0, y0, x_end, h)
        else:  # rk4 por defecto
            xs, ys = rk4(f_numerica, x0, y0, x_end, h)
        
        if len(xs) == 0:
            return None, None, "No se generaron puntos. Revisa el intervalo y el paso."
        
        return xs, ys, None
        
    except OverflowError:
        return None, None, "Desbordamiento numérico. La solución podría divergir. Prueba con un paso (h) más pequeño."
    except Exception as e:
        return None, None, f"Error durante la integración numérica: {e}"

def resolver_edo_con_funcion(f, x0, y0, x_end, h, metodo='rk4'):
    """
    Versión que acepta una función directamente (para compatibilidad)
    
    Parámetros:
    - f: función dy/dx = f(x, y)
    - x0: valor inicial de x
    - y0: valor inicial de y
    - x_end: valor final de x
    - h: tamaño del paso
    - metodo: 'rk1', 'rk2' o 'rk4'
    
    Retorna:
    - xs: array con los valores de x
    - ys: array con los valores de y
    """
    try:
        if metodo == 'rk1':
            return rk1(f, x0, y0, x_end, h)
        elif metodo == 'rk2':
            return rk2(f, x0, y0, x_end, h)
        else:  # rk4 por defecto
            return rk4(f, x0, y0, x_end, h)
    except OverflowError:
        return None, None
    except Exception:
        return None, None

def euler_implicito(f, x0, y0, x_end, h, tol=1e-8, max_iter=50):
    """
    Método de Euler implícito (hacia atrás) para EDOs de primer orden.
    Resuelve la ecuación y_{n+1} = y_n + h*f(x_{n+1}, y_{n+1})
    mediante el método de Newton con derivada numérica.
    """
    xs = [x0]
    ys = [y0]
    x = x0
    y = y0

    n_steps = int(np.ceil((x_end - x0) / h))
    for _ in range(n_steps):
        if x >= x_end:
            break

        x_next = x + h
        # Predictor: Euler explícito
        y_guess = y + h * f(x, y)

        # Newton para resolver g(y_new)= y_new - y - h*f(x_next, y_new) = 0
        for _ in range(max_iter):
            f_val = f(x_next, y_guess)
            # Derivada numérica de f respecto a y en (x_next, y_guess)
            eps = 1e-7
            f_plus = f(x_next, y_guess + eps)
            f_y = (f_plus - f_val) / eps

            g_val = y_guess - y - h * f_val
            g_prime = 1.0 - h * f_y
            if abs(g_prime) < 1e-12:
                break
            delta = g_val / g_prime
            y_guess = y_guess - delta
            if abs(delta) < tol:
                break

        y = y_guess
        x = x_next
        xs.append(x)
        ys.append(y)

    return np.array(xs), np.array(ys)