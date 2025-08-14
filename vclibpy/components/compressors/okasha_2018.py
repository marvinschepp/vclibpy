from vclibpy.components.compressors.compressor import Compressor
from vclibpy.datamodels import Inputs
from vclibpy import media


class Okasha_CO2_Rec(Compressor):
    """
    Compressor model based on the paper of Okasha et al. (2018).


    Parameters:

        N_max (float): Maximal rotations per second of the compressor.
        V_h (float): Volume of the compressor in m^3.

    Methods:
        get_lambda_h(inputs: Inputs) -> float:
            Returns the volumetric efficiency based on the regressions of Okasha et al. (2018).

        get_eta_isentropic(p_outlet: float, inputs: Inputs) -> float:
            Returns the isentropic efficiency based on the regressions of Okasha et al. (2018).

        get_eta_mech(inputs: Inputs) -> float:
            Returns the mechanical efficiency based on the regressions of Okasha et al. (2018).

    """
    def __init__(self, N_max: float, V_h: float, eta_mech: float = 0.85):

        super().__init__(N_max=N_max, V_h=V_h)
        # Store all parameters as instance variables
        self.eta_mech_const = eta_mech

        self._coeffs = {
            # Coefficients for T_eva = -8°C
            -8: {"lambda_a0": 1.0904, "lambda_a1": -0.1929, "lambda_a2": 0.0189, "lambda_a3": -0.0003,
                 "eta_is_b0": 0.7532, "eta_is_b1": -0.1378, "eta_is_b2": 0.0351, "eta_is_b3": -0.0029},
            # Coefficients for T_eva = 0°C
            0: {"lambda_a0": 1.0829, "lambda_a1": -0.1965, "lambda_a2": 0.0202, "lambda_a3": -0.0001,
                "eta_is_b0": 0.7191, "eta_is_b1": -0.1358, "eta_is_b2": 0.0455, "eta_is_b3": -0.0048},
            # Coefficients for T_eva = 15°C
            15: {"lambda_a0": 1.0380, "lambda_a1": -0.2044, "lambda_a2": 0.0249, "lambda_a3": 0.0002,
                 "eta_is_b0": 0.0561, "eta_is_b1": 0.5536, "eta_is_b2": -0.1961, "eta_is_b3": 0.0240}
        }

    def _get_coeffs_for_t_eva(self) -> dict:
        """
        Selects the appropriate set of coefficients based on the evaporation temperature.
        The evaporation temperature is derived from the compressor's inlet state pressure.
        """
        t_eva_c = self.med_prop.calc_state("PQ", self.state_inlet.p, 1).T - 273.15

        if t_eva_c > 7.5:
            return self._coeffs[15]
        elif t_eva_c > -4:
            return self._coeffs[0]
        else:
            return self._coeffs[-8]

    def get_lambda_h(self, inputs: Inputs) -> float:
        """
        Returns the volumetric efficiency based on the semi-empirical model of Ortiz et al. (2003).

        Args:
            inputs (Inputs): Not directly used, but necessary for method signature.

        Returns:
            float: volumetric efficiency.
        """
        coeffs = self._get_coeffs_for_t_eva()
        r_p = self.get_p_outlet() / self.state_inlet.p
        lambda_h = (
                coeffs["lambda_a0"] +
                coeffs["lambda_a1"] * r_p +
                coeffs["lambda_a2"] * r_p ** 2 +
                coeffs["lambda_a3"] * r_p ** 3
        )
        return lambda_h

    def get_eta_isentropic(self, p_outlet: float, inputs: Inputs) -> float:
        """
        Returns the isentropic efficiency based on the semi-empirical model of Ortiz et al. (2003).

        Args:
            p_outlet (float): Outlet pressure.
            inputs (Inputs): Not directly used, but necessary for method signature.

        Returns:
            float: Isentropic efficiency.
        """
        coeffs = self._get_coeffs_for_t_eva()
        r_p = p_outlet / self.state_inlet.p

        eta_is = (
                coeffs["eta_is_b0"] +
                coeffs["eta_is_b1"] * r_p +
                coeffs["eta_is_b2"] * r_p ** 2 +
                coeffs["eta_is_b3"] * r_p ** 3
        )

        # Plausibility check
        if eta_is <= 0 <= 1:
            raise ValueError(f"Calculated isentropic efficiency ({eta_is:.3f}) is outside the plausible range (0.1-1.0) for pi={pi:.2f}.")
        return eta_is

    def get_eta_mech(self, inputs: Inputs) -> float:
        """
        Returns the mechanical efficiency of the compressor.
        """
        # Returns the constant value defined during initialization
        return self.eta_mech_const
