def cp_vapor_puro(A, B, C, D, T):
    """
    Calcula la capacidad calorífica del vapor de un componente puro según:
    Cp = A + B*T + C*T^2 + D*T^3
    T en Kelvin, Cp en cal/(g-mol·K).
    """
    if T < 0:
        raise ValueError("La temperatura debe ser >= 0 K.")
    return A + B*T + C*(T**2) + D*(T**3)

def cp_mezcla(componentes, T):
    """
    Calcula la capacidad calorífica de una mezcla de vapores (ideal) como
    promedio ponderado por fracción molar de los Cp de los componentes puros.
    componentes: lista de diccionarios con 'A','B','C','D' y 'fraccion'.
    T en Kelvin.
    Retorna Cp_mix en cal/(g-mol·K).
    """
    # Verificar que las fracciones sumen 1
    total_frac = sum(c['fraccion'] for c in componentes)
    if not abs(total_frac - 1.0) < 1e-9:
        raise ValueError(f"Las fracciones molares deben sumar 1. Suma = {total_frac}")

    Cp_mix = 0.0
    for c in componentes:
        Cp_i = cp_vapor_puro(c['A'], c['B'], c['C'], c['D'], T)
        Cp_mix += c['fraccion'] * Cp_i
    return Cp_mix

# ========== EJEMPLO DE USO ==========
if __name__ == "__main__":
    # Datos ficticios para dos componentes (coeficientes típicos en cal/(g-mol·K))
    componentes = [
        {'A': 6.713, 'B': 0.0015, 'C': -0.0000008, 'D': 0.0000000002, 'fraccion': 0.7},
        {'A': 7.200, 'B': 0.0020, 'C': -0.0000010, 'D': 0.0000000003, 'fraccion': 0.3}
    ]

    T = 500.0  # Kelvin

    print("Cp de componentes puros a T =", T, "K:")
    for i, c in enumerate(componentes):
        Cp_i = cp_vapor_puro(c['A'], c['B'], c['C'], c['D'], T)
        print(f"  Componente {i+1}: {Cp_i:.4f} cal/(g-mol·K)")

    Cp_mix = cp_mezcla(componentes, T)
    print(f"\nCp de la mezcla (promedio molar): {Cp_mix:.4f} cal/(g-mol·K)")