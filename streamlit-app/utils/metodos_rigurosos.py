import pandas as pd
import numpy as np
import math
from utils.eqstate import (
    a_RK_puro, b_RK_puro,
    a_SRK_puro, b_SRK_puro,
    a_PR_puro, b_PR_puro,
    R as R_eos
)

# ---------- Funciones de K para EOS ----------
def K_PR(T, P, Tc_list, Pc_list, omega_list, x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    Tc = np.asarray(Tc_list, dtype=float)
    Pc = np.asarray(Pc_list, dtype=float)
    omega = np.asarray(omega_list, dtype=float)
    nc = len(x)

    ai = np.array([a_PR_puro(T, Tc[i], Pc[i], omega[i]) for i in range(nc)])
    bi = np.array([b_PR_puro(Tc[i], Pc[i]) for i in range(nc)])
    sqrt_ai = np.sqrt(ai)

    # Líquido
    a_mix_L = np.sum(np.outer(x, x) * np.outer(sqrt_ai, sqrt_ai))
    b_mix_L = np.sum(x * bi)
    A_L = a_mix_L * P / (R_eos**2 * T**2)
    B_L = b_mix_L * P / (R_eos * T)

    # Vapor
    a_mix_V = np.sum(np.outer(y, y) * np.outer(sqrt_ai, sqrt_ai))
    b_mix_V = np.sum(y * bi)
    A_V = a_mix_V * P / (R_eos**2 * T**2)
    B_V = b_mix_V * P / (R_eos * T)

    def calc_phi(z, A, B, a_mix, b_mix, is_liquid=True):
        z = np.asarray(z, dtype=float)
        coef = [1, -(1 - B), A - 3*B**2 - 2*B, -(A*B - B**2 - B**3)]
        roots = np.roots(coef)
        real_roots = [r.real for r in roots if np.isclose(r.imag, 0, atol=1e-8)]
        if not real_roots:
            Z = 1.0
        else:
            if is_liquid:
                positives = [r for r in real_roots if r > 0]
                Z = min(positives) if positives else min(real_roots)
            else:
                Z = max(real_roots)
        
        lnphi = np.zeros(nc)
        for i in range(nc):
            sum_aj = np.sum(z * sqrt_ai[i])
            term1 = (bi[i] / b_mix) * (Z - 1)
            term2 = -np.log(Z - B)
            term3 = (A / (2 * np.sqrt(2) * B)) * ((2 * sum_aj) / a_mix - (bi[i] / b_mix))
            term4 = np.log((Z + (1 + np.sqrt(2)) * B) / (Z + (1 - np.sqrt(2)) * B))
            lnphi[i] = term1 + term2 - term3 * term4
        lnphi = np.nan_to_num(lnphi, nan=0.0, posinf=1e10, neginf=-1e10)
        return np.exp(lnphi)

    phi_L = calc_phi(x, A_L, B_L, a_mix_L, b_mix_L, is_liquid=True)
    phi_V = calc_phi(y, A_V, B_V, a_mix_V, b_mix_V, is_liquid=False)
    phi_V = np.where(np.abs(phi_V) < 1e-12, 1e-12, phi_V)
    return np.maximum(phi_L / phi_V, 1e-12)

def K_RK(T, P, Tc_list, Pc_list, x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    Tc = np.asarray(Tc_list, dtype=float)
    Pc = np.asarray(Pc_list, dtype=float)
    nc = len(x)

    ai = np.array([a_RK_puro(T, Tc[i], Pc[i]) for i in range(nc)])
    bi = np.array([b_RK_puro(Tc[i], Pc[i]) for i in range(nc)])
    sqrt_ai = np.sqrt(ai)

    a_mix_L = np.sum(np.outer(x, x) * np.outer(sqrt_ai, sqrt_ai))
    b_mix_L = np.sum(x * bi)
    A_L = a_mix_L * P / (R_eos**2 * T**2)
    B_L = b_mix_L * P / (R_eos * T)

    a_mix_V = np.sum(np.outer(y, y) * np.outer(sqrt_ai, sqrt_ai))
    b_mix_V = np.sum(y * bi)
    A_V = a_mix_V * P / (R_eos**2 * T**2)
    B_V = b_mix_V * P / (R_eos * T)

    def calc_phi(z, A, B, a_mix, b_mix, is_liquid=True):
        z = np.asarray(z, dtype=float)
        coef = [1, -1, A - B - B**2, -A*B]
        roots = np.roots(coef)
        real_roots = [r.real for r in roots if np.isclose(r.imag, 0, atol=1e-8)]
        if not real_roots:
            Z = 1.0
        else:
            if is_liquid:
                positives = [r for r in real_roots if r > 0]
                Z = min(positives) if positives else min(real_roots)
            else:
                Z = max(real_roots)
        
        lnphi = np.zeros(nc)
        for i in range(nc):
            sum_aj = np.sum(z * sqrt_ai[i])
            term1 = (bi[i] / b_mix) * (Z - 1)
            term2 = -np.log(Z - B)
            term3 = (A / B) * ((2 * sum_aj) / a_mix - (bi[i] / b_mix))
            term4 = np.log(1 + B / Z)
            lnphi[i] = term1 + term2 - term3 * term4
        lnphi = np.nan_to_num(lnphi, nan=0.0, posinf=1e10, neginf=-1e10)
        return np.exp(lnphi)

    phi_L = calc_phi(x, A_L, B_L, a_mix_L, b_mix_L, is_liquid=True)
    phi_V = calc_phi(y, A_V, B_V, a_mix_V, b_mix_V, is_liquid=False)
    phi_V = np.where(np.abs(phi_V) < 1e-12, 1e-12, phi_V)
    return np.maximum(phi_L / phi_V, 1e-12)

def K_SRK(T, P, Tc_list, Pc_list, omega_list, x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    Tc = np.asarray(Tc_list, dtype=float)
    Pc = np.asarray(Pc_list, dtype=float)
    omega = np.asarray(omega_list, dtype=float)
    nc = len(x)

    ai = np.array([a_SRK_puro(T, Tc[i], Pc[i], omega[i]) for i in range(nc)])
    bi = np.array([b_SRK_puro(Tc[i], Pc[i]) for i in range(nc)])
    sqrt_ai = np.sqrt(ai)

    a_mix_L = np.sum(np.outer(x, x) * np.outer(sqrt_ai, sqrt_ai))
    b_mix_L = np.sum(x * bi)
    A_L = a_mix_L * P / (R_eos**2 * T**2)
    B_L = b_mix_L * P / (R_eos * T)

    a_mix_V = np.sum(np.outer(y, y) * np.outer(sqrt_ai, sqrt_ai))
    b_mix_V = np.sum(y * bi)
    A_V = a_mix_V * P / (R_eos**2 * T**2)
    B_V = b_mix_V * P / (R_eos * T)

    def calc_phi(z, A, B, a_mix, b_mix, is_liquid=True):
        z = np.asarray(z, dtype=float)
        coef = [1, -1, A - B - B**2, -A*B]
        roots = np.roots(coef)
        real_roots = [r.real for r in roots if np.isclose(r.imag, 0, atol=1e-8)]
        if not real_roots:
            Z = 1.0
        else:
            if is_liquid:
                positives = [r for r in real_roots if r > 0]
                Z = min(positives) if positives else min(real_roots)
            else:
                Z = max(real_roots)
        
        lnphi = np.zeros(nc)
        for i in range(nc):
            sum_aj = np.sum(z * sqrt_ai[i])
            term1 = (bi[i] / b_mix) * (Z - 1)
            term2 = -np.log(Z - B)
            term3 = (A / B) * ((2 * sum_aj) / a_mix - (bi[i] / b_mix))
            term4 = np.log(1 + B / Z)
            lnphi[i] = term1 + term2 - term3 * term4
        lnphi = np.nan_to_num(lnphi, nan=0.0, posinf=1e10, neginf=-1e10)
        return np.exp(lnphi)

    phi_L = calc_phi(x, A_L, B_L, a_mix_L, b_mix_L, is_liquid=True)
    phi_V = calc_phi(y, A_V, B_V, a_mix_V, b_mix_V, is_liquid=False)
    phi_V = np.where(np.abs(phi_V) < 1e-12, 1e-12, phi_V)
    return np.maximum(phi_L / phi_V, 1e-12)

def K_general(T, P, Tc_list, Pc_list, omega_list, x, y, modelo):
    if modelo == "PR":
        return K_PR(T, P, Tc_list, Pc_list, omega_list, x, y)
    elif modelo == "RK":
        return K_RK(T, P, Tc_list, Pc_list, x, y)
    elif modelo == "SRK":
        return K_SRK(T, P, Tc_list, Pc_list, omega_list, x, y)
    else:
        raise ValueError(f"Modelo EOS no soportado: {modelo}")

# ---------- Antoine ----------
def K_antoine(T, P, A_list, B_list, C_list):
    T_C = T - 273.15
    A = np.asarray(A_list, dtype=float)
    B = np.asarray(B_list, dtype=float)
    C = np.asarray(C_list, dtype=float)
    P_vap = np.exp(A - B / (T_C + C))
    return P_vap / P

# ---------- Bubble point ----------
def bubble_temp_general(x, P, A_list, B_list, C_list,
                        modelo="Antoine", Tc_list=None, Pc_list=None, omega_list=None,
                        T_guess=300.0, tol=1e-4, max_iter=30):
    x = np.asarray(x, dtype=float)
    nc = len(x)
    y = x.copy()

    if modelo == "Antoine":
        T_low = 180.0
        T_high = 650.0
        for _ in range(10):
            f_low = np.sum(K_antoine(T_low, P, A_list, B_list, C_list) * x) - 1.0
            f_high = np.sum(K_antoine(T_high, P, A_list, B_list, C_list) * x) - 1.0
            if f_low * f_high > 0:
                T_low *= 0.9
                T_high *= 1.1
            else:
                break
        for _ in range(50):
            T_mid = (T_low + T_high) / 2.0
            f_mid = np.sum(K_antoine(T_mid, P, A_list, B_list, C_list) * x) - 1.0
            if abs(f_mid) < tol:
                return T_mid
            if f_mid < 0:
                T_low = T_mid
            else:
                T_high = T_mid
        return (T_low + T_high) / 2.0
    else:
        T = T_guess
        for it in range(max_iter):
            K = K_general(T, P, Tc_list, Pc_list, omega_list, x, y, modelo)
            sumKx = np.sum(K * x)
            if sumKx <= 0:
                sumKx = 1e-12
            y_new = K * x / sumKx
            
            T_low = 180.0
            T_high = 650.0
            for _ in range(40):
                T_mid = (T_low + T_high) / 2.0
                K_mid = K_general(T_mid, P, Tc_list, Pc_list, omega_list, x, y_new, modelo)
                f_mid = np.sum(K_mid * x) - 1.0
                if abs(f_mid) < tol:
                    T = T_mid
                    break
                if f_mid < 0:
                    T_low = T_mid
                else:
                    T_high = T_mid
            else:
                T = (T_low + T_high) / 2.0
            
            if np.max(np.abs(y_new - y)) < tol:
                break
            y = y_new
        return T

# ---------- Thomas ----------
def thomas_tdma(a, b, c, d):
    n = len(d)
    cp = np.zeros(n)
    dp = np.zeros(n)
    x = np.zeros(n)
    cp[0] = c[0] / b[0]
    dp[0] = d[0] / b[0]
    for i in range(1, n):
        denom = b[i] - a[i] * cp[i-1]
        cp[i] = c[i] / denom
        dp[i] = (d[i] - a[i] * dp[i-1]) / denom
    x[-1] = dp[-1]
    for i in range(n-2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i+1]
    return x

# ---------- Simulación de columna (CON ACTUALIZACIÓN DE FLUJOS) ----------
def columna_multicomponente(N, feed_stage, F, z, D, L_D, P,
                            A_list, B_list, C_list, comp_names,
                            modelo="Antoine",
                            Tc_list=None, Pc_list=None, omega_list=None,
                            tol=1e-3, max_iter=100,
                            progress_callback=None):
    if not isinstance(N, int) or N < 2:
        raise ValueError("N debe ser un entero >= 2")
    if feed_stage < 1 or feed_stage > N:
        raise ValueError("feed_stage debe estar entre 1 y N")
    nc = len(comp_names)
    z = np.asarray(z, dtype=float)

    # --- Inicialización ---
    # Temperaturas iniciales
    T_feed_guess = 350.0
    T_cond = bubble_temp_general(z, P, A_list, B_list, C_list, modelo, Tc_list, Pc_list, omega_list, T_guess=T_feed_guess)
    T_herv = bubble_temp_general(z, P, A_list, B_list, C_list, modelo, Tc_list, Pc_list, omega_list, T_guess=T_feed_guess + 30)
    T_stage = np.linspace(T_cond, T_herv, N)

    # Flujos iniciales (estimación)
    B = F - D
    L_rect = L_D
    V_rect = L_rect + D
    L_strip = L_rect + F
    V_strip = V_rect

    L = np.zeros(N+1)
    V = np.zeros(N+1)
    for stage in range(1, N+1):
        if stage <= feed_stage:
            L[stage] = L_rect
            V[stage] = V_rect
        else:
            L[stage] = L_strip
            V[stage] = V_strip

    # Composición inicial (líquido = alimentación en todas las etapas)
    x = np.tile(z, (N, 1))
    y = np.zeros_like(x)
    for stage in range(N):
        if modelo == "Antoine":
            K = K_antoine(T_stage[stage], P, A_list, B_list, C_list)
        else:
            K = K_general(T_stage[stage], P, Tc_list, Pc_list, omega_list, x[stage], x[stage], modelo)
        y[stage, :] = K * x[stage] / np.sum(K * x[stage])

    iter_count = 0
    error = 1e10
    relax = 0.5

    if progress_callback:
        progress_callback(0, "Iniciando simulación...")

    while error > tol and iter_count < max_iter:
        x_old = x.copy()
        T_old = T_stage.copy()
        L_old = L.copy()
        V_old = V.copy()

        # --- 1. Calcular K para cada etapa ---
        K_mat = np.zeros((N, nc))
        for stage in range(N):
            if modelo == "Antoine":
                K_mat[stage, :] = K_antoine(T_stage[stage], P, A_list, B_list, C_list)
            else:
                K_mat[stage, :] = K_general(T_stage[stage], P, Tc_list, Pc_list, omega_list,
                                            x[stage], y[stage], modelo)

        # --- 2. Resolver sistema de ecuaciones para cada componente (TDMA) ---
        for j in range(nc):
            a = np.zeros(N)
            b = np.zeros(N)
            c = np.zeros(N)
            d = np.zeros(N)

            # Etapa 0 (condensador)
            a[0] = 0.0
            b[0] = L[1] + D
            c[0] = -V[2] * K_mat[1, j] if N > 1 else 0.0
            d[0] = 0.0

            # Etapas intermedias
            for i in range(1, N-1):
                a[i] = L[i]
                b[i] = -(L[i+1] + V[i+1])
                c[i] = V[i+2] * K_mat[i+1, j] if (i+1) < N else 0.0
                d[i] = 0.0
                if (i+1) == feed_stage:
                    d[i] = -F * z[j]

            # Última etapa (calderín)
            a[N-1] = L[N-1]
            b[N-1] = -(L[N] + B) + V[N] * K_mat[N-1, j]
            c[N-1] = 0.0
            d[N-1] = 0.0

            x_new = thomas_tdma(a, b, c, d)
            x[:, j] = relax * np.maximum(x_new, 1e-12) + (1 - relax) * x[:, j]

        # --- 3. Normalizar composiciones ---
        for stage in range(N):
            sum_x = np.sum(x[stage, :])
            if sum_x > 0:
                x[stage, :] /= sum_x
            K_stage = K_mat[stage, :]
            y_stage = K_stage * x[stage, :]
            sum_y = np.sum(y_stage)
            if sum_y > 0:
                y[stage, :] = y_stage / sum_y
            else:
                y[stage, :] = x[stage, :]

        # --- 4. Actualizar temperaturas (bubble point) ---
        for stage in range(N):
            T_new = bubble_temp_general(x[stage, :], P, A_list, B_list, C_list,
                                        modelo, Tc_list, Pc_list, omega_list,
                                        T_guess=T_stage[stage])
            T_stage[stage] = relax * T_new + (1 - relax) * T_stage[stage]

        # --- 5. Actualizar flujos L y V (balance de materia) ---
        # Sumar flujos de líquido y vapor en cada etapa
        L_new = np.zeros(N+1)
        V_new = np.zeros(N+1)
        
        # Condensador (etapa 1)
        L_new[1] = L_D
        V_new[1] = L_D + D
        
        # Etapas intermedias (balance total)
        for stage in range(2, N+1):
            if stage <= feed_stage:
                # Sección de rectificación
                V_new[stage] = V_new[stage-1]
                L_new[stage] = L_new[stage-1] + V_new[stage] - V_new[stage-1]
            else:
                # Sección de agotamiento (incluye alimentación)
                if stage == feed_stage + 1:
                    L_new[stage] = L_new[stage-1] + F
                    V_new[stage] = V_new[stage-1]
                else:
                    L_new[stage] = L_new[stage-1]
                    V_new[stage] = V_new[stage-1]
        
        # Calderín (etapa N)
        V_new[N] = L_new[N] + B
        
        # Aplicar relajación a los flujos
        L = relax * L_new + (1 - relax) * L_old
        V = relax * V_new + (1 - relax) * V_old
        
        # Asegurar que los flujos sean positivos
        L = np.maximum(L, 1e-6)
        V = np.maximum(V, 1e-6)

        # --- 6. Calcular error ---
        error_x = np.max(np.abs(x - x_old))
        error_T = np.max(np.abs(T_stage - T_old))
        error_L = np.max(np.abs(L - L_old) / (L_old + 1e-10))
        error_V = np.max(np.abs(V - V_old) / (V_old + 1e-10))
        error = max(error_x, error_T, error_L, error_V)
        
        iter_count += 1

        if progress_callback:
            progress_callback(min(iter_count / max_iter, 1.0),
                              f"Iter {iter_count}/{max_iter} - error {error:.2e}")

    if iter_count >= max_iter:
        print("Advertencia: no convergió en el máximo de iteraciones.")

    return {
        "etapas": N,
        "perfil_T": T_stage,
        "perfil_x": x,
        "perfil_y": y,
        "perfil_L": L[1:],
        "perfil_V": V[1:],
        "componentes": comp_names,
        "iteraciones": iter_count,
        "error_final": error
    }