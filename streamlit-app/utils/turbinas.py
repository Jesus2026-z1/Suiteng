import numpy as np

class TurbineCalculator:
    def __init__(self, R, MW, Z_avg, k, eta, T1, P1, P2, Q_vol, comp_type='isentropic'):
        """
        Inicializa la calculadora de turbina.
        :param R: Constante universal de los gases (kJ/kmol·K)
        :param MW: Peso molecular (kg/kmol)
        :param Z_avg: Factor de compresibilidad promedio
        :param k: Relación de calores específicos (cp/cv)
        :param eta: Eficiencia (isentrópica o politrópica) en fracción (0-1)
        :param T1: Temperatura de entrada (K)
        :param P1: Presión de entrada (kPa abs)
        :param P2: Presión de salida (kPa abs)
        :param Q_vol: Caudal volumétrico en condiciones de entrada (m³/h)
        :param comp_type: 'isentropic' o 'polytropic'
        """
        self.R = R
        self.MW = MW
        self.Z_avg = Z_avg
        self.k = k
        self.eta = eta
        self.T1 = T1
        self.P1 = P1
        self.P2 = P2
        self.Q_vol = Q_vol
        self.comp_type = comp_type

        self.R_specific = R / MW  # kJ/kg·K
        self.cp = self.R_specific * k / (k - 1)  # kJ/kg·K
        self.cv = self.cp / k

        # Relación de expansión (P1/P2)
        self.rp = P1 / P2  # > 1

        # Calcular exponente politrópico si aplica
        self.n = None
        if comp_type == 'polytropic':
            # Relación para turbina: eta_p = (n-1)/n * k/(k-1)
            # => n = 1 / (1 - eta * (k-1)/k)
            denom = 1 - eta * (k - 1) / k
            if denom <= 0:
                raise ValueError("La eficiencia politrópica es demasiado baja, denom <= 0")
            self.n = 1 / denom

    def head(self):
        """Calcula el trabajo específico real (J/kg) generado por la turbina."""
        # Temperatura ideal de salida (isentrópica)
        T2s = self.T1 * (self.P2 / self.P1) ** ((self.k - 1) / self.k)
        head_ideal = self.cp * (self.T1 - T2s)  # kJ/kg

        if self.comp_type == 'isentropic':
            head_real = self.eta * head_ideal  # kJ/kg
        else:  # polytropic
            # Usar exponente n para calcular T2 real
            T2 = self.T1 * (self.P2 / self.P1) ** ((self.n - 1) / self.n)
            head_real = self.cp * (self.T1 - T2)  # kJ/kg

        # Convertir a J/kg
        return head_real * 1000

    def discharge_temperature(self):
        """Calcula la temperatura real de descarga (K)."""
        if self.comp_type == 'isentropic':
            T2s = self.T1 * (self.P2 / self.P1) ** ((self.k - 1) / self.k)
            # head_real = eta * cp*(T1 - T2s)
            head_real = self.eta * self.cp * (self.T1 - T2s)  # kJ/kg
            T2 = self.T1 - head_real / self.cp
        else:  # polytropic
            T2 = self.T1 * (self.P2 / self.P1) ** ((self.n - 1) / self.n)
        return T2

    def discharge_temperature_ideal(self):
        """Temperatura ideal de descarga (isentrópica) en K."""
        if self.comp_type == 'isentropic':
            return self.T1 * (self.P2 / self.P1) ** ((self.k - 1) / self.k)
        else:
            # Para politrópico, la temperatura ideal no se define, devolvemos None
            return None

    def mass_flow(self, Q_vol, P, T):
        """
        Calcula el flujo másico (kg/s) a partir del caudal volumétrico (m³/h),
        presión (kPa) y temperatura (K).
        """
        Q = Q_vol / 3600.0  # m³/s
        # Densidad = P / (Z * R_specific * T)  (R_specific en kJ/kg·K, P en kPa)
        # R_specific en kJ/kg·K, P en kPa -> densidad en kg/m³
        rho = P / (self.R_specific * T)  # kg/m³ (sin Z)
        rho = rho / self.Z_avg
        m_dot = rho * Q  # kg/s
        return m_dot

    def power(self):
        """Calcula la potencia generada (kW)."""
        m_dot = self.mass_flow(self.Q_vol, self.P1, self.T1)
        head_Jkg = self.head()  # J/kg
        power_kW = m_dot * head_Jkg / 1000.0  # kW
        return power_kW

    @staticmethod
    def interpolate_curve(x_data, y_data, x_val):
        """Interpola linealmente un valor en una curva."""
        if len(x_data) != len(y_data) or len(x_data) < 2:
            return None
        pairs = sorted(zip(x_data, y_data))
        x_sorted, y_sorted = zip(*pairs)
        if x_val <= x_sorted[0]:
            return y_sorted[0]
        if x_val >= x_sorted[-1]:
            return y_sorted[-1]
        for i in range(len(x_sorted)-1):
            if x_sorted[i] <= x_val <= x_sorted[i+1]:
                slope = (y_sorted[i+1] - y_sorted[i]) / (x_sorted[i+1] - x_sorted[i])
                return y_sorted[i] + slope * (x_val - x_sorted[i])
        return None

    def find_operating_point(self, Q_comp, H_comp, Q_sys, H_sys):
        """
        Encuentra el punto de operación como intersección de la curva de la turbina
        y la curva del sistema.
        Q_comp, H_comp: datos de la curva de la máquina
        Q_sys, H_sys: arrays de la curva del sistema (generados con np.linspace)
        Retorna (Q_op, H_op) o (None, None) si no hay intersección.
        """
        H_comp_interp = []
        for q in Q_sys:
            h = self.interpolate_curve(Q_comp, H_comp, q)
            if h is None:
                h = np.nan
            H_comp_interp.append(h)
        diff = np.array(H_comp_interp) - np.array(H_sys)
        for i in range(len(diff)-1):
            if diff[i] * diff[i+1] < 0:
                Q_op = Q_sys[i] - diff[i] * (Q_sys[i+1] - Q_sys[i]) / (diff[i+1] - diff[i])
                H_op = np.interp(Q_op, Q_sys, H_sys)
                return Q_op, H_op
        idx = np.argmin(np.abs(diff))
        if not np.isnan(diff[idx]):
            return Q_sys[idx], H_sys[idx]
        return None, None