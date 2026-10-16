import numpy as np

# ------------------------------------------------------------
# 1. CONSTANTES Y FUNCIONES AUXILIARES COMUNES
# ------------------------------------------------------------
R = 0.08314  # L·bar/(mol·K)  (unidades típicas para presiones en bar y volúmenes en L)

def A_star(a, P, T):
    """A* = a P / (R² T²)"""
    return a * P / (R**2 * T**2)

def B_star(b, P, T):
    """B* = b P / (R T)"""
    return b * P / (R * T)

def raiz_apropiada(coef, fase):
    """
    Dados los coeficientes de la cúbica en Z (de la forma [1, c2, c1, c0]),
    devuelve la raíz real adecuada según la fase.
    """
    raices = np.roots(coef)
    raices_reales = [r.real for r in raices if abs(r.imag) < 1e-8]
    if len(raices_reales) == 0:
        raise ValueError("No se encontraron raíces reales")
    if fase == 'vapor':
        return max(raices_reales)
    elif fase == 'líquido':
        positivos = [r for r in raices_reales if r > 0]
        if positivos:
            return min(positivos)      # raíz positiva más pequeña
        else:
            return min(raices_reales)  # podría ser negativa (no físico, pero se devuelve)
    else:
        raise ValueError("fase debe ser 'vapor' o 'líquido'")

# ------------------------------------------------------------
# 2. MODELO REDLICH-KWONG (RK) ORIGINAL
# ------------------------------------------------------------
def a_RK_puro(T, Tc, Pc):
    """Parámetro a para RK (independiente de T, salvo la raíz de T en la ec. original,
       pero aquí se devuelve el valor constante a_i)."""
    return 0.42748 * (R**2) * (Tc**2.5) / Pc

def b_RK_puro(Tc, Pc):
    return 0.08664 * R * Tc / Pc

def polinomio_RK(A, B):
    """
    Coeficientes de la cúbica de RK: Z^3 - Z^2 + (A - B - B^2) Z - A B = 0
    Devuelve lista [1, -1, A-B-B**2, -A*B]
    """
    return [1, -1, A - B - B**2, -A*B]

def Z_RK_mezcla(T, P, y, Tc_list, Pc_list, k_ij=None, fase='vapor'):
    """
    Calcula Z con RK para una mezcla multicomponente.
    """
    N = len(y)
    # Parámetros puros
    a_puros = np.array([a_RK_puro(T, Tc_list[i], Pc_list[i]) for i in range(N)])
    b_puros = np.array([b_RK_puro(Tc_list[i], Pc_list[i]) for i in range(N)])
    
    # Reglas de mezclado
    b_m = np.dot(y, b_puros)
    if k_ij is None:
        k_ij = np.zeros((N, N))
    a_m = 0.0
    for i in range(N):
        for j in range(N):
            a_m += y[i] * y[j] * np.sqrt(a_puros[i] * a_puros[j]) * (1 - k_ij[i, j])
    
    A = A_star(a_m, P, T)
    B = B_star(b_m, P, T)
    coef = polinomio_RK(A, B)
    return raiz_apropiada(coef, fase)

# ------------------------------------------------------------
# 3. MODELO SOAVE-REDLICH-KWONG (SRK)
# ------------------------------------------------------------
def alpha_SRK(T, Tc, omega):
    """Función α(T) para SRK: α = [1 + m (1 - sqrt(T/Tc))]^2"""
    Tr = T / Tc
    m = 0.480 + 1.574 * omega - 0.176 * omega**2
    return (1 + m * (1 - np.sqrt(Tr)))**2

def a_SRK_puro(T, Tc, Pc, omega):
    """Parámetro a(T) para SRK (dependiente de T)"""
    a0 = 0.42748 * (R**2) * (Tc**2) / Pc   # valor a la temperatura crítica
    return a0 * alpha_SRK(T, Tc, omega)

def b_SRK_puro(Tc, Pc):
    """Parámetro b para SRK (igual que RK)"""
    return 0.08664 * R * Tc / Pc

def polinomio_SRK(A, B):
    """Coeficientes de la cúbica de SRK: igual que RK"""
    return [1, -1, A - B - B**2, -A*B]

def Z_SRK_mezcla(T, P, y, Tc_list, Pc_list, omega_list, k_ij=None, fase='vapor'):
    """
    Calcula Z con SRK para una mezcla multicomponente.
    """
    N = len(y)
    a_puros = np.array([a_SRK_puro(T, Tc_list[i], Pc_list[i], omega_list[i]) for i in range(N)])
    b_puros = np.array([b_SRK_puro(Tc_list[i], Pc_list[i]) for i in range(N)])
    
    b_m = np.dot(y, b_puros)
    if k_ij is None:
        k_ij = np.zeros((N, N))
    a_m = 0.0
    for i in range(N):
        for j in range(N):
            a_m += y[i] * y[j] * np.sqrt(a_puros[i] * a_puros[j]) * (1 - k_ij[i, j])
    
    A = A_star(a_m, P, T)
    B = B_star(b_m, P, T)
    coef = polinomio_SRK(A, B)
    return raiz_apropiada(coef, fase)

# ------------------------------------------------------------
# 4. MODELO PENG-ROBINSON (PR)
# ------------------------------------------------------------
def alpha_PR(T, Tc, omega):
    """Función α(T) para PR: α = [1 + m (1 - sqrt(T/Tc))]^2"""
    Tr = T / Tc
    m = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
    return (1 + m * (1 - np.sqrt(Tr)))**2

def a_PR_puro(T, Tc, Pc, omega):
    """Parámetro a(T) para PR"""
    a0 = 0.45724 * (R**2) * (Tc**2) / Pc
    return a0 * alpha_PR(T, Tc, omega)

def b_PR_puro(Tc, Pc):
    """Parámetro b para PR"""
    return 0.07780 * R * Tc / Pc

def polinomio_PR(A, B):
    """
    Coeficientes de la cúbica de PR:
    Z^3 - (1 - B) Z^2 + (A - 2B - 3B^2) Z - (AB - B^2 - B^3) = 0
    """
    return [1, -(1 - B), A - 2*B - 3*B**2, -(A*B - B**2 - B**3)]

def Z_PR_mezcla(T, P, y, Tc_list, Pc_list, omega_list, k_ij=None, fase='vapor'):
    """
    Calcula Z con PR para una mezcla multicomponente.
    """
    N = len(y)
    a_puros = np.array([a_PR_puro(T, Tc_list[i], Pc_list[i], omega_list[i]) for i in range(N)])
    b_puros = np.array([b_PR_puro(Tc_list[i], Pc_list[i]) for i in range(N)])
    
    b_m = np.dot(y, b_puros)
    if k_ij is None:
        k_ij = np.zeros((N, N))
    a_m = 0.0
    for i in range(N):
        for j in range(N):
            a_m += y[i] * y[j] * np.sqrt(a_puros[i] * a_puros[j]) * (1 - k_ij[i, j])
    
    A = A_star(a_m, P, T)
    B = B_star(b_m, P, T)
    coef = polinomio_PR(A, B)
    return raiz_apropiada(coef, fase)

# ------------------------------------------------------------
# 5. EJEMPLO DE USO (mezcla binaria metano + etano)
# ------------------------------------------------------------
if __name__ == "__main__":
    # Datos de los componentes: Metano (1), Etano (2)
    Tc = [190.6, 305.3]      # K
    Pc = [46.0, 48.7]        # bar
    omega = [0.008, 0.098]   # factor acéntrico
    
    # Composición de la mezcla (fracciones molares)
    y = np.array([0.5, 0.5])
    
    # Condiciones
    T = 300   # K
    P = 50    # bar
    
    # Matriz k_ij (todas cero, mezcla sin interacción)
    k_ij = np.array([[0.0, 0.0],
                     [0.0, 0.0]])
    
    print(f"Mezcla equimolar metano(1) + etano(2) a T = {T} K, P = {P} bar")
    print("-" * 60)
    
    # Calcular Z con cada modelo (fase vapor)
    Z_RK = Z_RK_mezcla(T, P, y, Tc, Pc, k_ij, fase='vapor')
    Z_SRK = Z_SRK_mezcla(T, P, y, Tc, Pc, omega, k_ij, fase='vapor')
    Z_PR = Z_PR_mezcla(T, P, y, Tc, Pc, omega, k_ij, fase='vapor')
    
    print(f"RK  : Z = {Z_RK:.5f}")
    print(f"SRK : Z = {Z_SRK:.5f}")
    print(f"PR  : Z = {Z_PR:.5f}")
    
    # Opcional: comparar con la raíz de fase líquida (si existiera)
    Z_RK_liq = Z_RK_mezcla(T, P, y, Tc, Pc, k_ij, fase='líquido')
    Z_SRK_liq = Z_SRK_mezcla(T, P, y, Tc, Pc, omega, k_ij, fase='líquido')
    Z_PR_liq = Z_PR_mezcla(T, P, y, Tc, Pc, omega, k_ij, fase='líquido')
    
    print("\nRaíces correspondientes a fase líquida (menor positiva):")
    print(f"RK  : Z_líq = {Z_RK_liq:.5f}")
    print(f"SRK : Z_líq = {Z_SRK_liq:.5f}")
    print(f"PR  : Z_líq = {Z_PR_liq:.5f}")