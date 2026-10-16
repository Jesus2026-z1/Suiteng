import math
from ECES import *  # Se carga el primer archivo (aunque no se use directamente)

# ------------------------------------------------------------
# 1. FENSKE: Número mínimo de etapas y distribución de no clave
# ------------------------------------------------------------

def fenske_Nmin(alpha_ij, d_i, d_j, b_i, b_j):
    """
    Ecuación de Fenske para número mínimo de etapas.
    Parámetros:
        alpha_ij: volatilidad relativa del componente ligero i respecto al pesado j
        d_i, d_j: flujos molares de i y j en destilado
        b_i, b_j: flujos molares de i y j en fondos
    Retorna:
        N_min: número mínimo de etapas de equilibrio
    """
    numerador = (d_i / d_j) * (b_j / b_i)
    N_min = math.log(numerador) / math.log(alpha_ij)
    return N_min

def fenske_distribution(alpha_nr, N_min, d_r, b_r, f_n):
    """
    Distribución de un componente no clave utilizando Fenske.
    Parámetros:
        alpha_nr: volatilidad relativa del componente n respecto al de referencia r (clave pesado)
        N_min: número mínimo de etapas
        d_r, b_r: flujos del componente de referencia en destilado y fondos
        f_n: flujo de alimentación del componente n
    Retorna:
        d_n, b_n: flujos del componente n en destilado y fondos
    """
    ratio = (d_r / b_r) * (alpha_nr ** N_min)
    b_n = f_n / (1.0 + ratio)
    d_n = f_n - b_n
    return d_n, b_n

# ------------------------------------------------------------
# 2. UNDERWOOD: Reflujo mínimo
# ------------------------------------------------------------

def underwood_theta(alpha, zF, q, theta_guess_low, theta_guess_high, tol=1e-6):
    """
    Encuentra la raíz theta de la ecuación:
        sum_i (alpha_i * zF_i) / (alpha_i - theta) = 1 - q
    para una zona de pinzamiento (generalmente entre alpha_HK y alpha_LK).
    Parámetros:
        alpha: lista de volatilidades relativas (respecto a un componente de referencia)
        zF: lista de fracciones molares en la alimentación
        q: condición térmica de la alimentación (1 = líquido saturado, 0 = vapor saturado)
        theta_guess_low, theta_guess_high: intervalo que contiene la raíz
        tol: tolerancia
    Retorna:
        theta: valor de theta que satisface la ecuación
    """
    def f(theta):
        s = 0.0
        for a, z in zip(alpha, zF):
            denom = a - theta
            if abs(denom) < 1e-12:
                return 1e12 if theta > a else -1e12
            s += a * z / denom
        return s - (1.0 - q)
    
    # Búsqueda por bisección
    if f(theta_guess_low) * f(theta_guess_high) > 0:
        raise ValueError("El intervalo no contiene la raíz. Ajuste los límites.")
    
    while (theta_guess_high - theta_guess_low) > tol:
        theta_mid = (theta_guess_low + theta_guess_high) / 2.0
        if f(theta_mid) == 0.0:
            return theta_mid
        elif f(theta_guess_low) * f(theta_mid) < 0:
            theta_guess_high = theta_mid
        else:
            theta_guess_low = theta_mid
    return (theta_guess_low + theta_guess_high) / 2.0

def underwood_Rmin(alpha, xD, theta):
    """
    Calcula el reflujo mínimo R_min a partir del theta encontrado.
    Parámetros:
        alpha: lista de volatilidades relativas
        xD: lista de fracciones molares en el destilado
        theta: valor de theta (raíz de la ecuación anterior)
    Retorna:
        R_min: relación de reflujo mínima
    """
    suma = 0.0
    for a, x in zip(alpha, xD):
        denom = a - theta
        if abs(denom) < 1e-12:
            continue
        suma += a * x / denom
    return suma - 1.0

# ------------------------------------------------------------
# 3. GILLILAND: Número real de etapas
# ------------------------------------------------------------

def gilliland_N(R, R_min, N_min):
    """
    Correlación de Gilliland para estimar el número real de etapas.
    Parámetros:
        R: relación de reflujo real
        R_min: relación de reflujo mínima
        N_min: número mínimo de etapas (Fenske)
    Retorna:
        N: número real de etapas de equilibrio
    """
    X = (R - R_min) / (R + 1.0)
    if X <= 0:
        return N_min
    # Correlación común: Y = 0.75 * (1 - X^0.5668)
    Y = 0.75 * (1.0 - X ** 0.5668)
    # Y = (N - N_min) / (N + 1)  -> despejar N
    # Y*(N+1) = N - N_min -> Y*N + Y = N - N_min -> Y + N_min = N - Y*N -> N = (Y+N_min)/(1-Y)
    N = (Y + N_min) / (1.0 - Y)
    return max(N, N_min)

# ------------------------------------------------------------
# 4. KIRKBRIDE: Ubicación del plato de alimentación
# ------------------------------------------------------------

def kirkbride_feed_location(z_HK_F, z_LK_F, x_LK_B, x_HK_D, B, D, N_total):
    """
    Ecuación de Kirkbride para estimar el número de etapas en las secciones
    de rectificación y agotamiento.
    Parámetros:
        z_HK_F, z_LK_F: fracciones molares del clave pesado y clave ligero en la alimentación
        x_LK_B: fracción del clave ligero en fondos
        x_HK_D: fracción del clave pesado en destilado
        B, D: flujos molares de fondos y destilado
        N_total: número total de etapas reales (incluyendo calderín? normalmente platos teóricos)
    Retorna:
        N_R: número de etapas en la sección de rectificación (sobre el plato de alimentación)
        N_S: número de etapas en la sección de agotamiento (incluyendo el plato de alimentación? cuidado)
    Nota: La ecuación original da la relación N_R/N_S. Se devuelven ambos números.
    """
    # Relación según la imagen: N_R/N_S = [ (z_HK_F / z_LK_F) * (x_LK_B / x_HK_D)^2 * (B/D) ]^{-0.206}
    term = (z_HK_F / z_LK_F) * (x_LK_B / x_HK_D) ** 2 * (B / D)
    ratio = term ** (-0.206)   # N_R / N_S
    N_S = N_total / (1.0 + ratio)
    N_R = N_total - N_S
    return N_R, N_S

def design_column(componentes, alpha, zF, q, LK_index, HK_index, rec_LK, rec_HK, R_factor=1.5, F_total=1.0):
    """
    Calcula el diseño de una columna de destilación multicomponente.
    
    Parámetros:
        componentes: lista de nombres (solo para referencia)
        alpha: lista de volatilidades relativas (respecto a un mismo referente)
        zF: lista de fracciones molares en alimentación (suma = 1)
        q: condición térmica
        LK_index: índice del clave ligero en las listas
        HK_index: índice del clave pesado
        rec_LK: fracción recuperada de LK en destilado (0-1)
        rec_HK: fracción recuperada de HK en fondos (0-1)
        R_factor: factor multiplicador de R_min para reflujo real
        F_total: flujo molar total de alimentación (por defecto 1.0)
    
    Retorna:
        dict con resultados: N_min, N_actual, R_min, R_actual, theta,
        D, B, composiciones, distribuciones, etc.
    """
    F = F_total
    # 1. Flujos de los clave
    d_LK = rec_LK * zF[LK_index] * F
    b_LK = zF[LK_index] * F - d_LK
    b_HK = rec_HK * zF[HK_index] * F
    d_HK = zF[HK_index] * F - b_HK

    # 2. Fenske Nmin
    alpha_LK_HK = alpha[LK_index] / alpha[HK_index]
    N_min = fenske_Nmin(alpha_LK_HK, d_LK, d_HK, b_LK, b_HK)

    # 3. Distribución de todos los componentes
    d = [0.0] * len(componentes)
    b = [0.0] * len(componentes)
    d[LK_index] = d_LK
    b[LK_index] = b_LK
    d[HK_index] = d_HK
    b[HK_index] = b_HK

    for i in range(len(componentes)):
        if i == LK_index or i == HK_index:
            continue
        alpha_i_ref = alpha[i] / alpha[HK_index]   # respecto al HK
        f_i = zF[i] * F
        d_i, b_i = fenske_distribution(alpha_i_ref, N_min, d_HK, b_HK, f_i)
        d[i] = d_i
        b[i] = b_i

    # 4. Totales y composiciones
    D = sum(d)
    B = sum(b)
    xD = [di / D for di in d]
    xB = [bi / B for bi in b]

    # 5. Underwood: encontrar theta entre alpha_HK y alpha_LK
    lower = alpha[HK_index] + 1e-6
    upper = alpha[LK_index] - 1e-6
    if lower >= upper:
        raise ValueError("alpha_LK debe ser mayor que alpha_HK")
    theta = underwood_theta(alpha, zF, q, lower, upper)
    R_min = underwood_Rmin(alpha, xD, theta)

    # 6. Gilliland
    R_actual = R_factor * R_min
    N_actual = gilliland_N(R_actual, R_min, N_min)

    # 7. Kirkbride
    z_HK_F = zF[HK_index]
    z_LK_F = zF[LK_index]
    x_LK_B = xB[LK_index]
    x_HK_D = xD[HK_index]
    N_R, N_S = kirkbride_feed_location(z_HK_F, z_LK_F, x_LK_B, x_HK_D, B, D, N_actual)
    
    # Resultados
    resultados = {
        'componentes': componentes,
        'N_min': N_min,
        'N_actual': N_actual,
        'R_min': R_min,
        'R_actual': R_actual,
        'theta': theta,
        'D': D,
        'B': B,
        'd': d,
        'b': b,
        'xD': xD,
        'xB': xB,
        'N_R': N_R,
        'N_S': N_S,
    }
    return resultados