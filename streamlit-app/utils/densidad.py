import math

# Constante de los gases (J/mol·K)
R = 8.31446261815324

def peso_molecular_promedio(fracciones_molares, pesos_moleculares_gmol):
    """
    Calcula el peso molecular promedio de una mezcla gaseosa.

    Parámetros:
    - fracciones_molares : lista de fracciones molares (suma = 1.0)
    - pesos_moleculares_gmol : lista de pesos moleculares (g/mol) en el mismo orden

    Retorna:
    - MW_prom_kg : peso molecular promedio en kg/mol
    """
    if len(fracciones_molares) != len(pesos_moleculares_gmol):
        raise ValueError("Las listas deben tener la misma longitud")

    # Suma ponderada (resultado en g/mol)
    MW_prom_g = sum(y * MW for y, MW in zip(fracciones_molares, pesos_moleculares_gmol))
    # Convertir a kg/mol (necesario para usar con R en J/mol·K)
    MW_prom_kg = MW_prom_g / 1000.0
    return MW_prom_kg


def densidad_mezcla_gas(P_Pa, T_K, Z, MW_prom_kg):
    """
    Calcula la densidad de una mezcla gaseosa real.

    Parámetros:
    - P_Pa : presión en Pascales
    - T_K  : temperatura en Kelvin
    - Z    : factor de compresibilidad (adimensional)
    - MW_prom_kg : peso molecular promedio en kg/mol

    Retorna:
    - rho : densidad en kg/m³
    """
    if Z <= 0:
        raise ValueError("El factor de compresibilidad debe ser mayor que cero")
    rho = ((P_Pa * 100000) * MW_prom_kg) / (Z * R * T_K)
    return rho


# =============================================================================
# EJEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    # Composición molar (metano, etano, propano, butano)
    fracciones = [0.30, 0.30, 0.20, 0.20]
    nombres = ['Metano', 'Etano', 'Propano', 'Butano']
    pesos_moleculares = [16.04, 30.07, 44.10, 58.12]  # g/mol

    # 1) Calcular peso molecular promedio
    MW_kg = peso_molecular_promedio(fracciones, pesos_moleculares)
    print(f"Peso molecular promedio: {MW_kg*1000:.2f} g/mol = {MW_kg:.6f} kg/mol")

    # 2) Condiciones de operación (ejemplo)
    P_atm = 10.0                # presión en atmósferas
    T = 300.0                   # temperatura en K
    Z = 0.92                    # factor de compresibilidad (supuesto)

    # Convertir presión a Pa (1 atm = 101325 Pa)
    P_Pa = P_atm * 101325.0

    # 3) Calcular densidad
    rho = densidad_mezcla_gas(P_Pa, T, Z, MW_kg)

    # Mostrar resultados
    print(f"Presión: {P_atm} atm = {P_Pa:.1f} Pa")
    print(f"Temperatura: {T} K")
    print(f"Factor de compresibilidad Z: {Z}")
    print(f"Densidad de la mezcla: {rho:.4f} kg/m³")
    print(f"Densidad en g/L: {rho:.4f} g/L")  # 1 kg/m³ = 1 g/L