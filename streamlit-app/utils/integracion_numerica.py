# integracion_numerica.py
import numpy as np
from sympy import sympify, SympifyError, symbols, lambdify, integrate as sym_integrate

def simpson_compuesta(f, a, b, n):
    """
    Calcula la integral definida de f(x) desde a hasta b usando la regla de Simpson compuesta.
    
    Parámetros:
    - f: función numérica (de numpy) que evalúa f(x)
    - a, b: límites inferior y superior
    - n: número de subintervalos (debe ser par)
    
    Retorna:
    - integral (float), x_vals (np.array), y_vals (np.array)
    """
    # Asegurar que n sea par
    if n % 2 == 1:
        n += 1
    
    h = (b - a) / n
    x_vals = np.linspace(a, b, n + 1)
    y_vals = f(x_vals)
    
    # Regla de Simpson compuesta:
    # I = h/3 * [f(x0) + f(xn) + 4*sum(f(impares)) + 2*sum(f(pares))]
    integral = y_vals[0] + y_vals[-1]
    integral += 4 * np.sum(y_vals[1:-1:2])
    integral += 2 * np.sum(y_vals[2:-2:2])
    integral *= h / 3
    
    return integral, x_vals, y_vals

def trapecio_compuesta(f, a, b, n):
    """
    Calcula la integral definida de f(x) desde a hasta b usando la regla del trapecio compuesta.
    
    Parámetros:
    - f: función numérica (de numpy) que evalúa f(x)
    - a, b: límites inferior y superior
    - n: número de subintervalos
    
    Retorna:
    - integral (float), x_vals (np.array), y_vals (np.array)
    """
    h = (b - a) / n
    x_vals = np.linspace(a, b, n + 1)
    y_vals = f(x_vals)
    
    # Regla del trapecio compuesta:
    # I = h * [f(x0)/2 + f(x1) + f(x2) + ... + f(xn-1) + f(xn)/2]
    integral = y_vals[0] / 2 + y_vals[-1] / 2 + np.sum(y_vals[1:-1])
    integral *= h
    
    return integral, x_vals, y_vals

def simpson_38_compuesta(f, a, b, n):
    """
    Calcula la integral definida de f(x) desde a hasta b usando la regla de Simpson 3/8 compuesta.
    
    Parámetros:
    - f: función numérica (de numpy) que evalúa f(x)
    - a, b: límites inferior y superior
    - n: número de subintervalos (debe ser múltiplo de 3)
    
    Retorna:
    - integral (float), x_vals (np.array), y_vals (np.array)
    """
    # Asegurar que n sea múltiplo de 3
    if n % 3 != 0:
        n = n + (3 - n % 3)
    
    h = (b - a) / n
    x_vals = np.linspace(a, b, n + 1)
    y_vals = f(x_vals)
    
    # Regla de Simpson 3/8 compuesta:
    # I = 3h/8 * [f(x0) + f(xn) + 3*sum(f(1 mod 3)) + 3*sum(f(2 mod 3)) + 2*sum(f(0 mod 3))]
    integral = y_vals[0] + y_vals[-1]
    
    # Para Simpson 3/8, los puntos se agrupan en ternas
    for i in range(1, n):
        if i % 3 == 0:
            integral += 2 * y_vals[i]
        else:
            integral += 3 * y_vals[i]
    
    integral *= 3 * h / 8
    
    return integral, x_vals, y_vals

def gauss_legendre(f, a, b, n):
    """
    Calcula la integral definida de f(x) desde a hasta b usando cuadratura de Gauss-Legendre.
    
    Parámetros:
    - f: función numérica que evalúa f(x)
    - a, b: límites inferior y superior
    - n: número de puntos de Gauss (2-10)
    
    Retorna:
    - integral (float), x_vals (np.array), y_vals (np.array)
    """
    # Puntos y pesos de Gauss-Legendre para n hasta 10
    gauss_points = {
        2: ([-0.5773502691896257, 0.5773502691896257], [1.0, 1.0]),
        3: ([-0.7745966692414834, 0.0, 0.7745966692414834], 
            [0.5555555555555556, 0.8888888888888888, 0.5555555555555556]),
        4: ([-0.8611363115940526, -0.3399810435848563, 0.3399810435848563, 0.8611363115940526],
            [0.3478548451374538, 0.6521451548625461, 0.6521451548625461, 0.3478548451374538]),
        5: ([-0.9061798459386640, -0.5384693101056831, 0.0, 0.5384693101056831, 0.9061798459386640],
            [0.2369268850561891, 0.4786286704993665, 0.5688888888888889, 0.4786286704993665, 0.2369268850561891]),
        6: ([-0.9324695142031521, -0.6612093864662645, -0.2386191860831969,
             0.2386191860831969, 0.6612093864662645, 0.9324695142031521],
            [0.1713244923791704, 0.3607615730481386, 0.4679139345726910,
             0.4679139345726910, 0.3607615730481386, 0.1713244923791704]),
        7: ([-0.9491079123427585, -0.7415311855993945, -0.4058451513773972, 0.0,
             0.4058451513773972, 0.7415311855993945, 0.9491079123427585],
            [0.1294849661688697, 0.2797053914892766, 0.3818300505051189, 0.4179591836734694,
             0.3818300505051189, 0.2797053914892766, 0.1294849661688697]),
        8: ([-0.9602898564975363, -0.7966664774136267, -0.5255324099163290, -0.1834346424956498,
             0.1834346424956498, 0.5255324099163290, 0.7966664774136267, 0.9602898564975363],
            [0.1012285362903763, 0.2223810344533745, 0.3137066458778873, 0.3626837833783620,
             0.3626837833783620, 0.3137066458778873, 0.2223810344533745, 0.1012285362903763]),
        9: ([-0.9681602395076261, -0.8360311073266358, -0.6133714327005904, -0.3242534234038089,
             -0.0, 0.3242534234038089, 0.6133714327005904, 0.8360311073266358, 0.9681602395076261],
            [0.0812743883615744, 0.1806481606948574, 0.2606106964029354, 0.3123470770400029,
             0.3302393550012598, 0.3123470770400029, 0.2606106964029354, 0.1806481606948574,
             0.0812743883615744]),
        10: ([-0.9739065285171717, -0.8650633666889845, -0.6794095682990244, -0.4333953941292472,
             -0.1488743389816312, 0.1488743389816312, 0.4333953941292472, 0.6794095682990244,
             0.8650633666889845, 0.9739065285171717],
            [0.0666713443086881, 0.1494513491505806, 0.2190863625159821, 0.2692667193099964,
             0.2955242247147529, 0.2955242247147529, 0.2692667193099964, 0.2190863625159821,
             0.1494513491505806, 0.0666713443086881])
    }
    
    if n not in gauss_points:
        # Si n no está disponible, usar el más cercano
        n_available = min(gauss_points.keys(), key=lambda x: abs(x - n))
        n = n_available
    
    points, weights = gauss_points[n]
    
    # Transformar del intervalo [-1, 1] a [a, b]
    x_trans = 0.5 * (b - a) * np.array(points) + 0.5 * (a + b)
    y_vals = f(x_trans)
    integral = 0.5 * (b - a) * np.sum(weights * y_vals)
    
    # Para graficar, evaluamos la función en muchos puntos
    x_plot = np.linspace(a, b, 1000)
    y_plot = f(x_plot)
    
    return integral, x_plot, y_plot

def integrar(func_str, a, b, n, metodo='simpson'):
    """
    Función principal para integrar numéricamente
    
    Parámetros:
    - func_str: string con la función f(x)
    - a: límite inferior
    - b: límite superior
    - n: número de subintervalos/puntos
    - metodo: 'simpson', 'trapecio', 'simpson_38', 'gauss_2', 'gauss_3', etc.
    
    Retorna:
    - integral: valor aproximado de la integral
    - integral_exacta: valor exacto (si se puede calcular)
    - x_vals: puntos para graficar
    - y_vals: valores de la función
    - mensaje_error: string con mensaje de error (None si no hay error)
    - n_efectivo: número efectivo de subintervalos/puntos usados
    """
    try:
        x_sym = symbols('x')
        expr = sympify(func_str)
        f_numerica = lambdify(x_sym, expr, modules=['numpy'])
        
        # Verificación rápida
        f_numerica(np.array([a, b]))
        
    except SympifyError:
        return None, None, None, None, f"Error de sintaxis en la función: '{func_str}'. Revisa que uses la variable 'x'.", None
    except Exception as e:
        return None, None, None, None, f"Error al interpretar la función: {e}", None

    # Calcular integral exacta con SymPy
    try:
        integral_exacta = float(sym_integrate(expr, (x_sym, a, b)))
    except:
        integral_exacta = None

    # Aplicar el método seleccionado
    n_efectivo = n
    try:
        if metodo == 'simpson':
            if n % 2 == 1:
                n_efectivo = n + 1
            integral, x_vals, y_vals = simpson_compuesta(f_numerica, a, b, n_efectivo)
        elif metodo == 'trapecio':
            integral, x_vals, y_vals = trapecio_compuesta(f_numerica, a, b, n_efectivo)
        elif metodo == 'simpson_38':
            if n % 3 != 0:
                n_efectivo = n + (3 - n % 3)
            integral, x_vals, y_vals = simpson_38_compuesta(f_numerica, a, b, n_efectivo)
        elif metodo.startswith('gauss_'):
            try:
                n_gauss = int(metodo.split('_')[1])
                if n_gauss < 2 or n_gauss > 10:
                    n_gauss = 4
            except:
                n_gauss = 4
            n_efectivo = n_gauss
            integral, x_vals, y_vals = gauss_legendre(f_numerica, a, b, n_gauss)
        else:
            # Por defecto, Simpson
            integral, x_vals, y_vals = simpson_compuesta(f_numerica, a, b, n_efectivo)
            
        return integral, integral_exacta, x_vals, y_vals, None, n_efectivo
        
    except ZeroDivisionError:
        return None, None, None, None, "División por cero detectada en la función. Revisa si hay asíntotas en el intervalo.", None
    except OverflowError:
        return None, None, None, None, "Desbordamiento numérico. La función crece demasiado rápido en el intervalo.", None
    except Exception as e:
        return None, None, None, None, f"Error durante la integración: {e}", None