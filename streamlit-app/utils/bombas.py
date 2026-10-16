"""
Módulo de cálculo de bombas centrífugas
Basado en las ecuaciones y procedimiento de las imágenes proporcionadas.
"""

import numpy as np
from scipy.interpolate import interp1d
from typing import List, Tuple, Optional


class PumpCalculator:
    """
    Calculadora de bombas que implementa:
    - Cálculo de presión de succión y descarga
    - Cálculo de NPSHA
    - Cálculo de cabeza diferencial y requerida
    - Curva de la bomba y punto de operación
    """

    def __init__(self, sp_gr: float, atm_pressure: float = 14.7):
        """
        Inicializa la calculadora.

        Args:
            sp_gr: Gravedad específica del fluido (adimensional)
            atm_pressure: Presión atmosférica en psia (default 14.7)
        """
        self.sp_gr = sp_gr
        self.atm_pressure = atm_pressure  # psia
        self.conversion_factor = 2.31  # psi → ft de cabeza

    # ==================== CONVERSIONES ====================

    def psi_to_head(self, psi: float) -> float:
        """Convierte psi a pies de cabeza."""
        return psi * self.conversion_factor / self.sp_gr

    def head_to_psi(self, head: float) -> float:
        """Convierte pies de cabeza a psi."""
        return head * self.sp_gr / self.conversion_factor

    def psia_to_psig(self, psia: float) -> float:
        """Convierte psia a psig (manométrica)."""
        return psia - self.atm_pressure

    def psig_to_psia(self, psig: float) -> float:
        """Convierte psig a psia (absoluta)."""
        return psig + self.atm_pressure

    # ==================== CÁLCULOS PRINCIPALES ====================

    def calculate_suction_pressure(
        self,
        vessel_pressure_psia: float,
        elevation_ft: float,
        friction_psi: float
    ) -> float:
        """
        Calcula la presión absoluta en la succión de la bomba.

        P_succ = P_vessel + P_elevation - P_friction

        Args:
            vessel_pressure_psia: Presión del recipiente de succión (psia)
            elevation_ft: Elevación del nivel de líquido sobre la bomba (ft)
            friction_psi: Pérdidas por fricción en la línea de succión (psi)

        Returns:
            Presión absoluta en la succión (psia)
        """
        elevation_psi = self.head_to_psi(elevation_ft)
        return vessel_pressure_psia + elevation_psi - friction_psi

    def calculate_discharge_pressure(
        self,
        vessel_pressure_psia: float,
        elevation_ft: float,
        friction_psi: float
    ) -> float:
        """
        Calcula la presión absoluta en la descarga de la bomba.

        P_desc = P_vessel + P_elevation + P_friction

        Args:
            vessel_pressure_psia: Presión del recipiente de descarga (psia)
            elevation_ft: Elevación del nivel de líquido sobre la bomba (ft)
            friction_psi: Pérdidas por fricción en la línea de descarga (psi)

        Returns:
            Presión absoluta en la descarga (psia)
        """
        elevation_psi = self.head_to_psi(elevation_ft)
        return vessel_pressure_psia + elevation_psi + friction_psi

    def calculate_differential_head(
        self,
        suction_pressure_psia: float,
        discharge_pressure_psia: float
    ) -> float:
        """
        Calcula la cabeza diferencial (altura total de la bomba).

        H = (P_desc - P_succ) * 2.31 / sp_gr

        Args:
            suction_pressure_psia: Presión en la succión (psia)
            discharge_pressure_psia: Presión en la descarga (psia)

        Returns:
            Cabeza diferencial (ft)
        """
        diff_pressure = discharge_pressure_psia - suction_pressure_psia
        return self.psi_to_head(diff_pressure)

    def calculate_required_head(
        self,
        differential_head: float,
        safety_factor: float = 0.10
    ) -> float:
        """
        Calcula la cabeza requerida con factor de seguridad.

        H_req = H * (1 + safety_factor)

        Args:
            differential_head: Cabeza diferencial calculada (ft)
            safety_factor: Factor de seguridad (ej. 0.10 = 10%)

        Returns:
            Cabeza requerida con factor de seguridad (ft)
        """
        return differential_head * (1 + safety_factor)

    def calculate_npsha(
        self,
        suction_vessel_pressure_psia: float,
        elevation_ft: float,
        friction_psi: float,
        vapor_pressure_psia: float
    ) -> float:
        """
        Calcula el NPSH disponible (NPSHA).

        NPSHA = [2.31 * (P_sv + Z_sv - h_fsv - P_vp)] / sp_gr

        Args:
            suction_vessel_pressure_psia: Presión del recipiente de succión (psia)
            elevation_ft: Elevación del nivel de líquido sobre la bomba (ft)
            friction_psi: Pérdidas por fricción en la succión (psi)
            vapor_pressure_psia: Presión de vapor del fluido (psia)

        Returns:
            NPSHA en pies (ft)
        """
        elevation_psi = self.head_to_psi(elevation_ft)
        npsh_psi = suction_vessel_pressure_psia + elevation_psi - friction_psi - vapor_pressure_psia
        return self.psi_to_head(npsh_psi)

    # ==================== CURVA DE LA BOMBA ====================

    def interpolate_pump_curve(
        self,
        flow_data: List[float],
        head_data: List[float],
        target_flow: float,
        kind: str = 'linear'
    ) -> Optional[float]:
        """
        Interpola la curva de la bomba para obtener la cabeza a un caudal dado.

        Args:
            flow_data: Lista de caudales (gpm)
            head_data: Lista de cabezas (ft)
            target_flow: Caudal objetivo (gpm)
            kind: Tipo de interpolación ('linear', 'cubic', etc.)

        Returns:
            Cabeza interpolada (ft) o None si no se puede interpolar
        """
        if len(flow_data) < 2:
            return None

        # Ordenar por caudal
        pairs = sorted(zip(flow_data, head_data))
        flow_sorted, head_sorted = zip(*pairs)

        # Verificar si el target está dentro del rango
        if target_flow < min(flow_sorted) or target_flow > max(flow_sorted):
            # Extrapolación - usar el valor más cercano
            if target_flow < min(flow_sorted):
                return head_sorted[0]
            else:
                return head_sorted[-1]

        # Interpolación
        interp_func = interp1d(flow_sorted, head_sorted, kind=kind, fill_value='extrapolate')
        return float(interp_func(target_flow))

    def get_system_curve(
        self,
        flow_rates: np.ndarray,
        static_head_ft: float,
        friction_head_at_design: float,
        design_flow: float
    ) -> np.ndarray:
        """
        Calcula la curva del sistema: H = H_static + K * Q²

        Args:
            flow_rates: Array de caudales (gpm)
            static_head_ft: Cabeza estática (ft) - diferencia de elevación
            friction_head_at_design: Cabeza de fricción en el caudal de diseño (ft)
            design_flow: Caudal de diseño (gpm)

        Returns:
            Array de cabezas del sistema (ft)
        """
        if design_flow > 0:
            K = friction_head_at_design / (design_flow ** 2)
        else:
            K = 0
        return static_head_ft + K * np.array(flow_rates) ** 2

    def find_operating_point(
        self,
        pump_flow: List[float],
        pump_head: List[float],
        system_flow: np.ndarray,
        system_head: np.ndarray,
        flow_range: Optional[Tuple[float, float]] = None
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Encuentra el punto de operación (intersección de curva de bomba y sistema).

        Args:
            pump_flow: Caudales de la curva de la bomba (gpm)
            pump_head: Cabezas de la curva de la bomba (ft)
            system_flow: Caudales de la curva del sistema (gpm)
            system_head: Cabezas de la curva del sistema (ft)
            flow_range: Rango de caudales a considerar (min, max)

        Returns:
            Tupla (caudal_operacion, cabeza_operacion) o (None, None)
        """
        if len(pump_flow) < 2:
            return None, None

        # Ordenar datos de la bomba
        pairs = sorted(zip(pump_flow, pump_head))
        pump_flow_sorted, pump_head_sorted = zip(*pairs)

        # Crear función de interpolación para la bomba
        try:
            pump_interp = interp1d(
                pump_flow_sorted, pump_head_sorted,
                kind='linear', fill_value='extrapolate'
            )
        except Exception:
            return None, None

        # Determinar rango de búsqueda
        if flow_range is None:
            min_flow = max(0, min(pump_flow_sorted))
            max_flow = max(pump_flow_sorted)
        else:
            min_flow, max_flow = flow_range

        # Crear grid fino
        flow_grid = np.linspace(min_flow, max_flow, 2000)

        # Evaluar curvas
        pump_h = pump_interp(flow_grid)
        system_h = np.interp(flow_grid, system_flow, system_head)

        # Buscar intersección (cambio de signo)
        diff = pump_h - system_h

        for i in range(len(diff) - 1):
            if diff[i] * diff[i + 1] < 0:
                # Interpolación lineal para el cruce por cero
                t = -diff[i] / (diff[i + 1] - diff[i])
                op_flow = flow_grid[i] + t * (flow_grid[i + 1] - flow_grid[i])
                op_head = pump_interp(op_flow)
                return float(op_flow), float(op_head)

        # Si no hay intersección, encontrar el punto más cercano
        idx = np.argmin(np.abs(diff))
        return float(flow_grid[idx]), float(pump_interp(flow_grid[idx]))

    # ==================== MÉTODO COMPLETO PARA EL EJEMPLO ====================

    def run_example(self) -> dict:
        """
        Ejecuta el cálculo completo usando los datos del ejemplo de las imágenes.

        Returns:
            Diccionario con todos los resultados del ejemplo
        """
        # Datos del ejemplo (de las imágenes)
        sp_gr = 0.485
        atm = 14.7

        # Succión
        suction_vessel_pressure = 200.0  # psia
        suction_elevation = 20.0  # ft
        suction_friction_piping = 0.5  # psi
        suction_friction_valves = 0.2  # psi

        # Descarga
        discharge_vessel_pressure = 220.0  # psia
        discharge_elevation = 74.0  # ft
        discharge_friction_piping = 3.0  # psi
        discharge_friction_valves = 2.0  # psi
        discharge_friction_orifice = 1.2  # psi
        discharge_friction_filter = 13.0  # psi
        discharge_friction_check_valve = 1.0  # psi
        discharge_friction_control_valve = 9.0  # psi

        # Vapor
        vapor_pressure = 200.0  # psia

        # Factor de seguridad
        safety_factor = 0.10  # 10%

        # Inicializar calculadora
        calc = PumpCalculator(sp_gr, atm)

        # Calcular fricción total
        suction_friction_total = suction_friction_piping + suction_friction_valves
        discharge_friction_total = (
            discharge_friction_piping + discharge_friction_valves +
            discharge_friction_orifice + discharge_friction_filter +
            discharge_friction_check_valve + discharge_friction_control_valve
        )

        # Presiones
        suction_pressure = calc.calculate_suction_pressure(
            suction_vessel_pressure, suction_elevation, suction_friction_total
        )
        discharge_pressure = calc.calculate_discharge_pressure(
            discharge_vessel_pressure, discharge_elevation, discharge_friction_total
        )

        # Cabeza diferencial
        differential_head = calc.calculate_differential_head(
            suction_pressure, discharge_pressure
        )

        # Cabeza requerida
        required_head = calc.calculate_required_head(differential_head, safety_factor)

        # NPSHA
        npsha = calc.calculate_npsha(
            suction_vessel_pressure, suction_elevation,
            suction_friction_total, vapor_pressure
        )

        # Resultados
        return {
            'sp_gr': sp_gr,
            'atm_pressure': atm,
            'suction_vessel_pressure_psia': suction_vessel_pressure,
            'suction_elevation_ft': suction_elevation,
            'suction_friction_psi': suction_friction_total,
            'suction_pressure_psia': suction_pressure,
            'suction_pressure_psig': calc.psia_to_psig(suction_pressure),
            'discharge_vessel_pressure_psia': discharge_vessel_pressure,
            'discharge_elevation_ft': discharge_elevation,
            'discharge_friction_psi': discharge_friction_total,
            'discharge_pressure_psia': discharge_pressure,
            'discharge_pressure_psig': calc.psia_to_psig(discharge_pressure),
            'differential_pressure_psi': discharge_pressure - suction_pressure,
            'differential_head_ft': differential_head,
            'safety_factor': safety_factor,
            'required_head_ft': required_head,
            'npsha_ft': npsha,
            'vapor_pressure_psia': vapor_pressure,
            'elevation_difference_ft': discharge_elevation - suction_elevation,
            'static_head_ft': discharge_elevation - suction_elevation,
            'suction_friction_breakdown': {
                'piping': suction_friction_piping,
                'valves': suction_friction_valves,
            },
            'discharge_friction_breakdown': {
                'piping': discharge_friction_piping,
                'valves': discharge_friction_valves,
                'orifice': discharge_friction_orifice,
                'filter': discharge_friction_filter,
                'check_valve': discharge_friction_check_valve,
                'control_valve': discharge_friction_control_valve,
            }
        }


# ==================== FUNCIÓN DE PRUEBA ====================

def test_calculator():
    """Prueba rápida del módulo con el ejemplo."""
    calc = PumpCalculator(sp_gr=0.485)
    results = calc.run_example()

    print("=" * 60)
    print("RESULTADOS DEL EJEMPLO (de las imágenes)")
    print("=" * 60)
    print(f"\n📍 SUCCIÓN:")
    print(f"  Presión recipiente:   {results['suction_vessel_pressure_psia']:.1f} psia")
    print(f"  Elevación:            {results['suction_elevation_ft']:.1f} ft  →  "
          f"{calc.head_to_psi(results['suction_elevation_ft']):.1f} psi")
    print(f"  Fricción:             {results['suction_friction_psi']:.1f} psi")
    print(f"  Presión de succión:   {results['suction_pressure_psia']:.1f} psia  =  "
          f"{results['suction_pressure_psig']:.1f} psig")

    print(f"\n📍 DESCARGA:")
    print(f"  Presión recipiente:   {results['discharge_vessel_pressure_psia']:.1f} psia")
    print(f"  Elevación:            {results['discharge_elevation_ft']:.1f} ft  →  "
          f"{calc.head_to_psi(results['discharge_elevation_ft']):.1f} psi")
    print(f"  Fricción:             {results['discharge_friction_psi']:.1f} psi")
    print(f"  Presión de descarga:  {results['discharge_pressure_psia']:.1f} psia  =  "
          f"{results['discharge_pressure_psig']:.1f} psig")

    print(f"\n📊 DIFERENCIAL:")
    print(f"  ΔP = {results['differential_pressure_psi']:.1f} psi")
    print(f"  H = {results['differential_head_ft']:.1f} ft")

    print(f"\n🔒 CON FACTOR DE SEGURIDAD ({results['safety_factor']*100:.0f}%):")
    print(f"  H_req = {results['required_head_ft']:.1f} ft")

    print(f"\n💧 NPSHA:")
    print(f"  NPSHA = {results['npsha_ft']:.1f} ft")
    print("=" * 60)


if __name__ == "__main__":
    test_calculator()