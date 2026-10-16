# edp_1d.py
import numpy as np
from scipy.linalg import solve_banded
from sympy import sympify, SympifyError, symbols, lambdify

def resolver_calor_explicito(alpha, L, T, Nx, Nt, u0_func, f_func,
                             bc_left_type, bc_left_val,
                             bc_right_type, bc_right_val):
    """
    Esquema FTCS explícito para ecuación del calor con condiciones mixtas.
    
    Parámetros:
    - alpha: coeficiente de difusión
    - L: longitud del dominio
    - T: tiempo final
    - Nx: número de puntos en x
    - Nt: número de puntos en t
    - u0_func: función condición inicial u(x,0)
    - f_func: función fuente f(x,t)
    - bc_left_type: 'Dirichlet' o 'Neumann' en x=0
    - bc_left_val: valor de la condición de frontera izquierda
    - bc_right_type: 'Dirichlet' o 'Neumann' en x=L
    - bc_right_val: valor de la condición de frontera derecha
    
    Retorna:
    - x: array de coordenadas espaciales
    - t: array de tiempos
    - u: matriz de solución u(x,t)
    - r: parámetro de estabilidad r = α*dt/dx²
    """
    dx = L / (Nx - 1)
    dt = T / (Nt - 1)
    r = alpha * dt / (dx ** 2)

    x = np.linspace(0, L, Nx)
    t = np.linspace(0, T, Nt)
    u = np.zeros((Nx, Nt))
    u[:, 0] = u0_func(x)

    # Aplicar condiciones de frontera en t=0 (si son Dirichlet)
    if bc_left_type == 'Dirichlet':
        u[0, 0] = bc_left_val
    if bc_right_type == 'Dirichlet':
        u[-1, 0] = bc_right_val

    # Bucle temporal
    for j in range(Nt - 1):
        # Calcular fuente en el tiempo actual
        f_vals = f_func(x[1:-1], t[j])

        # Esquema FTCS para el interior
        u[1:-1, j+1] = (r * u[:-2, j] +
                        (1 - 2*r) * u[1:-1, j] +
                        r * u[2:, j] +
                        dt * f_vals)

        # Aplicar condiciones de frontera
        # Extremo izquierdo
        if bc_left_type == 'Dirichlet':
            u[0, j+1] = bc_left_val
        else:  # Neumann: ∂u/∂x(0, t) = bc_left_val
            u[0, j+1] = u[1, j+1] - dx * bc_left_val

        # Extremo derecho
        if bc_right_type == 'Dirichlet':
            u[-1, j+1] = bc_right_val
        else:  # Neumann: ∂u/∂x(L, t) = bc_right_val
            u[-1, j+1] = u[-2, j+1] + dx * bc_right_val

    return x, t, u, r


def resolver_calor_implicito(alpha, L, T, Nx, Nt, u0_func, f_func,
                             bc_left_type, bc_left_val,
                             bc_right_type, bc_right_val):
    """
    Esquema Crank-Nicolson (implícito) para ecuación del calor.
    
    Parámetros:
    - alpha: coeficiente de difusión
    - L: longitud del dominio
    - T: tiempo final
    - Nx: número de puntos en x
    - Nt: número de puntos en t
    - u0_func: función condición inicial u(x,0)
    - f_func: función fuente f(x,t)
    - bc_left_type: 'Dirichlet' o 'Neumann' en x=0
    - bc_left_val: valor de la condición de frontera izquierda
    - bc_right_type: 'Dirichlet' o 'Neumann' en x=L
    - bc_right_val: valor de la condición de frontera derecha
    
    Retorna:
    - x: array de coordenadas espaciales
    - t: array de tiempos
    - u: matriz de solución u(x,t)
    - r: parámetro r = α*dt/dx²
    """
    dx = L / (Nx - 1)
    dt = T / (Nt - 1)
    r = alpha * dt / (dx ** 2)

    x = np.linspace(0, L, Nx)
    t = np.linspace(0, T, Nt)
    u = np.zeros((Nx, Nt))
    u[:, 0] = u0_func(x)

    # Aplicar condiciones de frontera en t=0
    if bc_left_type == 'Dirichlet':
        u[0, 0] = bc_left_val
    if bc_right_type == 'Dirichlet':
        u[-1, 0] = bc_right_val

    # Construir la matriz tridiagonal
    N = Nx
    ab = np.zeros((3, N))
    ab[0, 1:] = -r/2              # superior
    ab[1, :] = 1 + r              # principal
    ab[2, :-1] = -r/2             # inferior

    def build_b(u_prev, j):
        b = np.zeros(N)
        # Interior
        b[1:-1] = (r/2) * (u_prev[:-2] + u_prev[2:]) + (1 - r) * u_prev[1:-1] + \
                  (dt/2) * (f_func(x[1:-1], t[j]) + f_func(x[1:-1], t[j+1]))
        # Extremo izquierdo
        if bc_left_type == 'Dirichlet':
            b[0] = bc_left_val
            ab[0, 0] = 0
            ab[1, 0] = 1
            ab[2, 0] = 0
        else:
            b[0] = u_prev[0]
        # Extremo derecho
        if bc_right_type == 'Dirichlet':
            b[-1] = bc_right_val
            ab[0, -1] = 0
            ab[1, -1] = 1
            ab[2, -1] = 0
        else:
            b[-1] = u_prev[-1]
        return b

    for j in range(Nt - 1):
        b = build_b(u[:, j], j)
        u[:, j+1] = solve_banded((1, 1), ab, b)

        # Corregir fronteras Neumann
        if bc_left_type == 'Neumann':
            u[0, j+1] = u[1, j+1] - dx * bc_left_val
        if bc_right_type == 'Neumann':
            u[-1, j+1] = u[-2, j+1] + dx * bc_right_val

        # Asegurar Dirichlet
        if bc_left_type == 'Dirichlet':
            u[0, j+1] = bc_left_val
        if bc_right_type == 'Dirichlet':
            u[-1, j+1] = bc_right_val

    return x, t, u, r


def resolver_onda(c, L, T, Nx, Nt, u0_func, v0_func, f_func,
                  bc_left_type, bc_left_val, bc_right_type, bc_right_val):
    """
    Esquema explícito centrado para onda con condiciones mixtas.
    
    Parámetros:
    - c: velocidad de onda
    - L: longitud del dominio
    - T: tiempo final
    - Nx: número de puntos en x
    - Nt: número de puntos en t
    - u0_func: función condición inicial u(x,0)
    - v0_func: función condición inicial du/dt(x,0)
    - f_func: función fuente f(x,t)
    - bc_left_type: 'Dirichlet' o 'Neumann' en x=0
    - bc_left_val: valor de la condición de frontera izquierda
    - bc_right_type: 'Dirichlet' o 'Neumann' en x=L
    - bc_right_val: valor de la condición de frontera derecha
    
    Retorna:
    - x: array de coordenadas espaciales
    - t: array de tiempos
    - u: matriz de solución u(x,t)
    - cfl: número de Courant-Friedrichs-Lewy
    """
    dx = L / (Nx - 1)
    dt = T / (Nt - 1)
    r = (c * dt / dx) ** 2
    cfl = np.sqrt(r)

    x = np.linspace(0, L, Nx)
    t = np.linspace(0, T, Nt)
    u = np.zeros((Nx, Nt))
    u[:, 0] = u0_func(x)

    # Fronteras en t=0
    if bc_left_type == 'Dirichlet':
        u[0, 0] = bc_left_val
    if bc_right_type == 'Dirichlet':
        u[-1, 0] = bc_right_val

    # Paso 1 (t=dt)
    u[1:-1, 1] = (u[1:-1, 0] + dt * v0_func(x[1:-1]) +
                  0.5 * r * (u[:-2, 0] - 2*u[1:-1, 0] + u[2:, 0]) +
                  0.5 * dt**2 * f_func(x[1:-1], t[0]))
    
    # Fronteras en t=dt
    if bc_left_type == 'Dirichlet':
        u[0, 1] = bc_left_val
    else:
        u[0, 1] = u[1, 1] - dx * bc_left_val

    if bc_right_type == 'Dirichlet':
        u[-1, 1] = bc_right_val
    else:
        u[-1, 1] = u[-2, 1] + dx * bc_right_val

    # Bucle temporal
    for j in range(1, Nt - 1):
        f_vals = f_func(x[1:-1], t[j])
        u[1:-1, j+1] = (2*(1 - r)*u[1:-1, j] - u[1:-1, j-1] +
                        r*(u[:-2, j] + u[2:, j]) +
                        dt**2 * f_vals)
        # Fronteras
        if bc_left_type == 'Dirichlet':
            u[0, j+1] = bc_left_val
        else:
            u[0, j+1] = u[1, j+1] - dx * bc_left_val

        if bc_right_type == 'Dirichlet':
            u[-1, j+1] = bc_right_val
        else:
            u[-1, j+1] = u[-2, j+1] + dx * bc_right_val

    return x, t, u, cfl


def parsear_funcion_u0(func_str, x_sym):
    """Parsea la función condición inicial u(x,0)"""
    try:
        expr = sympify(func_str)
        func = lambdify(x_sym, expr, modules=['numpy'])
        return func, None
    except SympifyError:
        return None, f"Error de sintaxis en u(x,0): '{func_str}'"
    except Exception as e:
        return None, f"Error en u(x,0): {e}"


def parsear_funcion_f(func_str, x_sym, t_sym):
    """Parsea la función fuente f(x,t)"""
    try:
        expr = sympify(func_str)
        func = lambdify((x_sym, t_sym), expr, modules=['numpy'])
        return func, None
    except SympifyError:
        return None, f"Error de sintaxis en f(x,t): '{func_str}'"
    except Exception as e:
        return None, f"Error en f(x,t): {e}"


def parsear_funcion_v0(func_str, x_sym):
    """Parsea la función condición inicial du/dt(x,0) para la ecuación de onda"""
    try:
        expr = sympify(func_str)
        func = lambdify(x_sym, expr, modules=['numpy'])
        return func, None
    except SympifyError:
        return None, f"Error de sintaxis en du/dt(x,0): '{func_str}'"
    except Exception as e:
        return None, f"Error en du/dt(x,0): {e}"


def resolver_edp(tipo_edp, alpha, c, L, T, Nx, Nt, u0_str, f_str, v0_str,
                 bc_left_type, bc_left_val, bc_right_type, bc_right_val,
                 metodo_heat="Explícito (FTCS)"):
    """
    Función principal para resolver EDPs 1D (Calor u Onda)
    
    Parámetros:
    - tipo_edp: "Calor" o "Onda"
    - alpha: coeficiente de difusión (para Calor)
    - c: velocidad de onda (para Onda)
    - L, T, Nx, Nt: parámetros de malla
    - u0_str, f_str, v0_str: strings de las funciones
    - bc_left_type, bc_left_val, bc_right_type, bc_right_val: condiciones de frontera
    - metodo_heat: "Explícito (FTCS)" o "Implícito (Crank-Nicolson)" (para Calor)
    
    Retorna:
    - x_vals, t_vals, u_vals, param, condicion, estable, nombre_metodo, mensaje_error
    """
    # Símbolos
    x_sym, t_sym = symbols('x t')
    
    # Parsear funciones
    u0_func, error = parsear_funcion_u0(u0_str, x_sym)
    if error:
        return None, None, None, None, None, None, None, error
    
    f_func, error = parsear_funcion_f(f_str, x_sym, t_sym)
    if error:
        return None, None, None, None, None, None, None, error
    
    if "Onda" in tipo_edp:
        v0_func, error = parsear_funcion_v0(v0_str, x_sym)
        if error:
            return None, None, None, None, None, None, None, error
    else:
        v0_func = None
    
    # Resolver
    try:
        if "Calor" in tipo_edp:
            if metodo_heat == "Explícito (FTCS)":
                x_vals, t_vals, u_vals, param = resolver_calor_explicito(
                    alpha, L, T, Nx, Nt, u0_func, f_func,
                    bc_left_type, bc_left_val, bc_right_type, bc_right_val
                )
                condicion = f"r = α·Δt/Δx² = {param:.4f} ≤ 0.5 (condición de estabilidad)"
                estable = param <= 0.5
                nombre_metodo = metodo_heat
            else:  # Implícito
                x_vals, t_vals, u_vals, param = resolver_calor_implicito(
                    alpha, L, T, Nx, Nt, u0_func, f_func,
                    bc_left_type, bc_left_val, bc_right_type, bc_right_val
                )
                condicion = "Crank-Nicolson: incondicionalmente estable"
                estable = True
                nombre_metodo = metodo_heat
        else:  # Onda
            x_vals, t_vals, u_vals, cfl = resolver_onda(
                c, L, T, Nx, Nt, u0_func, v0_func, f_func,
                bc_left_type, bc_left_val, bc_right_type, bc_right_val
            )
            condicion = f"CFL = c·Δt/Δx = {cfl:.4f} ≤ 1.0"
            estable = cfl <= 1.0
            nombre_metodo = "Explícito centrado"
            param = cfl
        
        return x_vals, t_vals, u_vals, param, condicion, estable, nombre_metodo, None
        
    except Exception as e:
        return None, None, None, None, None, None, None, f"Error durante la simulación: {e}"