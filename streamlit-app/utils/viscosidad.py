import math

def viscosidad_pura(B, C, T):
    """
    Calcula la viscosidad de un líquido puro según:
    log10(μ) = B * (1/T - 1/C)
    donde μ está en las mismas unidades que se definan (ej. cP).
    T en Kelvin.
    Retorna μ.
    """
    if T <= 0:
        raise ValueError("La temperatura debe ser mayor que 0 K.")
    # Calcular log10(μ)
    log10_mu = B * (1.0 / T - 1.0 / C)
    mu = 10.0 ** log10_mu
    return mu