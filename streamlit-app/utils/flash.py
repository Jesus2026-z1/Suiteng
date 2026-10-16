import numpy as np
from scipy.optimize import bisect
from utils.eqstate import (                    # <--- Cambia a 'eqstate' si renombraste el archivo
    a_RK_puro, b_RK_puro,
    a_SRK_puro, b_SRK_puro,
    a_PR_puro, b_PR_puro,
    A_star, B_star
)

R = 0.08314  # L·bar/(mol·K)

# ------------------------------------------------------------
# 1. Parámetros puros y de mezcla según modelo
# ------------------------------------------------------------
def get_pure_params(T, Tc, Pc, omega, modelo):
    if modelo == 'REDLICH-KWONG':
        a = a_RK_puro(T, Tc, Pc)
        b = b_RK_puro(Tc, Pc)
    elif modelo == 'SOAVE-REDLICH-KWONG':
        a = a_SRK_puro(T, Tc, Pc, omega)
        b = b_SRK_puro(Tc, Pc)
    elif modelo == 'PENG-ROBINSON':
        a = a_PR_puro(T, Tc, Pc, omega)
        b = b_PR_puro(Tc, Pc)
    else:
        raise ValueError(f"Modelo desconocido: {modelo}")
    return a, b

def mixture_parameters(T, P, z, Tcs, Pcs, omegas, modelo, kij=None):
    nc = len(z)
    a = np.zeros(nc)
    b = np.zeros(nc)
    for i in range(nc):
        a[i], b[i] = get_pure_params(T, Tcs[i], Pcs[i], omegas[i], modelo)

    if kij is None:
        kij = np.zeros((nc, nc))

    a_mix = 0.0
    b_mix = 0.0
    for i in range(nc):
        b_mix += z[i] * b[i]
        for j in range(nc):
            a_mix += z[i] * z[j] * np.sqrt(a[i]*a[j]) * (1 - kij[i, j])

    A = a_mix * P / (R**2 * T**2)
    B = b_mix * P / (R * T)
    return a, b, a_mix, b_mix, A, B

def cubic_roots(A, B, modelo):
    if modelo in ('REDLICH-KWONG', 'SOAVE-REDLICH-KWONG'):
        coef = [1, -1, A - B - B**2, -A*B]
    elif modelo == 'PENG-ROBINSON':
        coef = [1, -(1 - B), A - 2*B - 3*B**2, -(A*B - B**2 - B**3)]
    else:
        raise ValueError(f"Modelo desconocido: {modelo}")
    roots = np.roots(coef)
    real_roots = [r.real for r in roots if np.isclose(r.imag, 0, atol=1e-8)]
    return real_roots

# ------------------------------------------------------------
# 2. Coeficientes de fugacidad (versión unificada)
# ------------------------------------------------------------
def fugacity_coeff(T, P, z, Tcs, Pcs, omegas, modelo, kij=None):
    """
    Calcula coeficientes de fugacidad para las fases vapor y líquido.
    Retorna: phi_v, Z_v, phi_l, Z_l
    """
    nc = len(z)
    a, b, a_mix, b_mix, A, B = mixture_parameters(T, P, z, Tcs, Pcs, omegas, modelo, kij)
    roots = cubic_roots(A, B, modelo)
    if not roots:
        raise ValueError("No hay raíces reales para la cúbica.")
    Z_v = max(roots)
    # Raíz positiva más pequeña (si no, se toma la menor)
    positives = [r for r in roots if r > 0]
    Z_l = min(positives) if positives else min(roots)

    def calc_phi(Z):
        lnphi = np.zeros(nc)
        for i in range(nc):
            # Suma sobre j para el término de mezcla
            sum_aj = 0.0
            for j in range(nc):
                kij_ij = 0.0 if kij is None else kij[i, j]
                sum_aj += z[j] * np.sqrt(a[i]*a[j]) * (1 - kij_ij)

            term1 = (b[i] / b_mix) * (Z - 1)
            term2 = - np.log(Z - B)

            if modelo == 'PENG-ROBINSON':
                # Fórmula de PR
                term3 = (A / (2 * np.sqrt(2) * B)) * ( (2 * sum_aj) / a_mix - (b[i] / b_mix) )
                term4 = np.log( (Z + (1 + np.sqrt(2)) * B) / (Z + (1 - np.sqrt(2)) * B) )
                lnphi[i] = term1 + term2 - term3 * term4
            else:  # RK y SRK usan la misma forma
                term3 = (A / B) * ( (2 * sum_aj) / a_mix - (b[i] / b_mix) )
                term4 = np.log(1 + B / Z)
                lnphi[i] = term1 + term2 - term3 * term4

        return np.exp(lnphi)

    phi_v = calc_phi(Z_v)
    phi_l = calc_phi(Z_l)
    return phi_v, Z_v, phi_l, Z_l

# ------------------------------------------------------------
# 3. Rachford‑Rice y flash
# ------------------------------------------------------------
def rachford_rice(beta, z, K):
    return np.sum(z * (K - 1) / (1 + beta * (K - 1)))

def flash(T, P, z, Tcs, Pcs, omegas, modelo, kij=None, tol=1e-6, max_iter=100):
    """
    Flash isotérmico.
    T [K], P [bar], z composición global.
    Retorna: beta, x_líquido, y_vapor, K, iteraciones
    """
    nc = len(z)
    if kij is None:
        kij = np.zeros((nc, nc))

    # Estimación inicial de K (Wilson)
    K = np.array([(Pcs[i] / P) * np.exp(5.37 * (1 + omegas[i]) * (1 - Tcs[i] / T)) for i in range(nc)])
    K = np.maximum(K, 1e-6)

    for it in range(max_iter):
        f0 = rachford_rice(0, z, K)
        f1 = rachford_rice(1, z, K)

        if f0 * f1 > 0:
            if np.sum(z * K) < 1:
                beta = 0.0
                x = z.copy()
                y = None
            else:
                beta = 1.0
                y = z.copy()
                x = None
            return beta, x, y, K, it+1

        beta = bisect(lambda b: rachford_rice(b, z, K), 0, 1, xtol=1e-8)
        denom = 1 + beta * (K - 1)
        x = z / denom
        y = K * x

        # Coeficientes de fugacidad para vapor y líquido
        phi_v, _, phi_l, _ = fugacity_coeff(T, P, y, Tcs, Pcs, omegas, modelo, kij)
        phi_l_old, _, _, _ = fugacity_coeff(T, P, x, Tcs, Pcs, omegas, modelo, kij)

        K_new = phi_l_old / phi_v
        error = np.max(np.abs(K_new - K) / K)
        if error < tol:
            K = K_new
            x = z / (1 + beta * (K - 1))
            y = K * x
            return beta, x, y, K, it+1

        K = K_new

    raise RuntimeError(f"No convergió en {max_iter} iteraciones.")

# ------------------------------------------------------------
# 4. Volatilidad relativa
# ------------------------------------------------------------
def relative_volatility(K, ref_index=-1):
    K = np.asarray(K)
    K_ref = K[ref_index]
    return K / K_ref