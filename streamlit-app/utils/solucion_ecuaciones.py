# solucion_ecuaciones.py
import numpy as np
from sympy import sympify, SympifyError, symbols, lambdify, diff, Matrix
import pandas as pd

# ============================================================
# 1. MÉTODOS UNIVARIABLES
# ============================================================

def biseccion(f, a, b, tol=1e-6, max_iter=100):
    """
    Método de bisección para encontrar raíz en [a, b].
    
    Parámetros:
    - f: función f(x)
    - a, b: intervalo [a, b]
    - tol: tolerancia
    - max_iter: número máximo de iteraciones
    
    Retorna:
    - raiz: valor de la raíz
    - iteraciones: lista de iteraciones
    - converg: True si convergió
    """
    if f(a) * f(b) >= 0:
        return None, None, False
    
    iteraciones = []
    for i in range(max_iter):
        c = (a + b) / 2
        iteraciones.append((i+1, a, b, c, f(c)))
        if abs(f(c)) < tol or (b - a)/2 < tol:
            return c, iteraciones, True
        if f(a) * f(c) < 0:
            b = c
        else:
            a = c
    return (a + b) / 2, iteraciones, False


def newton_raphson_1d(f, df, x0, tol=1e-6, max_iter=100):
    """
    Método de Newton-Raphson para 1D.
    
    Parámetros:
    - f: función f(x)
    - df: derivada de f(x)
    - x0: valor inicial
    - tol: tolerancia
    - max_iter: número máximo de iteraciones
    
    Retorna:
    - raiz: valor de la raíz
    - iteraciones: lista de iteraciones
    - converg: True si convergió
    """
    x = x0
    iteraciones = []
    for i in range(max_iter):
        fx = f(x)
        dfx = df(x)
        if abs(dfx) < 1e-12:
            return None, None, False
        x_new = x - fx / dfx
        iteraciones.append((i+1, x, fx, x_new))
        if abs(x_new - x) < tol:
            return x_new, iteraciones, True
        x = x_new
    return x, iteraciones, False


def secante(f, x0, x1, tol=1e-6, max_iter=100):
    """
    Método de la secante para encontrar raíz.
    
    Parámetros:
    - f: función f(x)
    - x0, x1: valores iniciales
    - tol: tolerancia
    - max_iter: número máximo de iteraciones
    
    Retorna:
    - raiz: valor de la raíz
    - iteraciones: lista de iteraciones
    - converg: True si convergió
    """
    iteraciones = []
    for i in range(max_iter):
        fx0 = f(x0)
        fx1 = f(x1)
        if abs(fx1 - fx0) < 1e-12:
            return None, None, False
        x_new = x1 - fx1 * (x1 - x0) / (fx1 - fx0)
        iteraciones.append((i+1, x0, x1, x_new, f(x_new)))
        if abs(x_new - x1) < tol:
            return x_new, iteraciones, True
        x0, x1 = x1, x_new
    return x1, iteraciones, False


# ============================================================
# 2. MÉTODOS MULTIVARIABLES
# ============================================================

def newton_raphson_multivariable(F, J, x0, tol=1e-6, max_iter=100):
    """
    Newton-Raphson para sistemas F(x) = 0.
    
    Parámetros:
    - F: lista de funciones numéricas F_i(x1, x2, ..., xn)
    - J: matriz jacobiana (función que devuelve matriz n×n)
    - x0: array inicial
    - tol: tolerancia
    - max_iter: número máximo de iteraciones
    
    Retorna:
    - sol: solución del sistema
    - iteraciones: lista de iteraciones
    - converg: True si convergió
    """
    x = np.array(x0, dtype=float)
    n = len(x)
    iteraciones = []
    for i in range(max_iter):
        Fx = np.array([f(*x) for f in F])
        Jx = np.array(J(*x))
        try:
            dx = np.linalg.solve(Jx, -Fx)
        except np.linalg.LinAlgError:
            return None, None, False
        x_new = x + dx
        iteraciones.append((i+1, x.copy(), Fx.copy(), dx))
        if np.linalg.norm(dx) < tol:
            return x_new, iteraciones, True
        x = x_new
    return x, iteraciones, False


def punto_fijo_multivariable(G, x0, tol=1e-6, max_iter=100):
    """
    Método de punto fijo para sistemas x = G(x).
    
    Parámetros:
    - G: lista de funciones numéricas G_i(x1, x2, ..., xn)
    - x0: array inicial
    - tol: tolerancia
    - max_iter: número máximo de iteraciones
    
    Retorna:
    - sol: solución del sistema
    - iteraciones: lista de iteraciones
    - converg: True si convergió
    """
    x = np.array(x0, dtype=float)
    n = len(x)
    iteraciones = []
    for i in range(max_iter):
        x_new = np.array([g(*x) for g in G])
        iteraciones.append((i+1, x.copy(), x_new))
        if np.linalg.norm(x_new - x) < tol:
            return x_new, iteraciones, True
        x = x_new
    return x, iteraciones, False


# ============================================================
# 3. FUNCIONES DE PARSEO Y RESOLUCIÓN
# ============================================================

def parsear_funcion_univariable(func_str):
    """
    Parsea una función univariable f(x)
    
    Retorna:
    - f: función numérica
    - df: derivada numérica (None si no se puede calcular)
    - mensaje_error: mensaje de error (None si no hay error)
    """
    x_sym = symbols('x')
    try:
        expr = sympify(func_str)
        f = lambdify(x_sym, expr, modules=['numpy'])
        # Verificar que funciona
        f(np.array([0.0]))
        # Calcular derivada
        try:
            df_expr = diff(expr, x_sym)
            df = lambdify(x_sym, df_expr, modules=['numpy'])
        except:
            df = None
        return f, df, None
    except SympifyError:
        return None, None, f"Error de sintaxis en la función: '{func_str}'. Usa la variable 'x'."
    except Exception as e:
        return None, None, f"Error al interpretar la función: {e}"


def parsear_sistema(func_strs, n):
    """
    Parsea un sistema de ecuaciones F(x1, x2, ..., xn) = 0
    
    Retorna:
    - F: lista de funciones numéricas
    - vars_sym: lista de símbolos
    - F_expr: lista de expresiones simbólicas
    - mensaje_error: mensaje de error (None si no hay error)
    """
    vars_sym = symbols([f'x{i}' for i in range(1, n+1)])
    F_expr = []
    F = []
    try:
        for f_str in func_strs:
            expr = sympify(f_str)
            F_expr.append(expr)
            F.append(lambdify(vars_sym, expr, modules=['numpy']))
        return F, vars_sym, F_expr, None
    except SympifyError:
        return None, None, None, f"Error de sintaxis en una de las funciones. Usa x1, x2, ..."
    except Exception as e:
        return None, None, None, f"Error al interpretar las funciones: {e}"


def resolver_univariable(func_str, metodo, a=None, b=None, x0=None, tol=1e-6, max_iter=100):
    """
    Resuelve una ecuación univariable f(x) = 0
    
    Retorna:
    - raiz: valor de la raíz
    - iteraciones: lista de iteraciones
    - converg: True si convergió
    - mensaje_error: mensaje de error (None si no hay error)
    """
    f, df, error = parsear_funcion_univariable(func_str)
    if error:
        return None, None, None, error
    
    if metodo == "Bisección":
        if a is None or b is None:
            return None, None, None, "Se requiere intervalo [a, b] para bisección"
        raiz, iteraciones, converg = biseccion(f, a, b, tol, max_iter)
    elif metodo == "Newton-Raphson":
        if x0 is None:
            return None, None, None, "Se requiere valor inicial x0 para Newton-Raphson"
        if df is None:
            return None, None, None, "No se pudo calcular la derivada automáticamente"
        raiz, iteraciones, converg = newton_raphson_1d(f, df, x0, tol, max_iter)
    elif metodo == "Secante":
        if x0 is None or b is None:
            return None, None, None, "Se requieren dos valores iniciales para secante"
        raiz, iteraciones, converg = secante(f, x0, b, tol, max_iter)
    else:
        return None, None, None, f"Método '{metodo}' no reconocido"
    
    return raiz, iteraciones, converg, None


def resolver_multivariable(func_strs, n, metodo, x0_vals, tol=1e-6, max_iter=100):
    """
    Resuelve un sistema de ecuaciones F(x) = 0
    
    Retorna:
    - sol: solución del sistema
    - iteraciones: lista de iteraciones
    - converg: True si convergió
    - mensaje_error: mensaje de error (None si no hay error)
    """
    F, vars_sym, F_expr, error = parsear_sistema(func_strs, n)
    if error:
        return None, None, None, error
    
    if metodo == "Newton-Raphson (Jacobiano)":
        # Calcular Jacobiano simbólico
        J_expr = Matrix([[diff(expr, var) for var in vars_sym] for expr in F_expr])
        J_func = lambdify(vars_sym, J_expr, modules=['numpy'])
        sol, iteraciones, converg = newton_raphson_multivariable(F, J_func, x0_vals, tol, max_iter)
    elif metodo == "Punto fijo":
        # Definir G(x) = x - F(x)
        G_expr = [vars_sym[i] - F_expr[i] for i in range(n)]
        G = [lambdify(vars_sym, expr, modules=['numpy']) for expr in G_expr]
        sol, iteraciones, converg = punto_fijo_multivariable(G, x0_vals, tol, max_iter)
    else:
        return None, None, None, f"Método '{metodo}' no reconocido"
    
    return sol, iteraciones, converg, None


def metodos_univariables_disponibles():
    """Retorna los métodos disponibles para ecuaciones univariables"""
    return ["Bisección", "Newton-Raphson", "Secante"]


def metodos_multivariables_disponibles():
    """Retorna los métodos disponibles para sistemas multivariables"""
    return ["Newton-Raphson (Jacobiano)", "Punto fijo"]