from vclibpy.components.compressors.compressor import Compressor
from vclibpy.datamodels import Inputs
from vclibpy import media
import numpy as np


class Guth_R290_Scroll(Compressor):
    """
    Compressor model based on the paper of Guth et al. (2022) for a
    variable speed scroll compressor with R-290.

    Source:
        Guth, T., & Atakan, B. (2022). Semi-empirical model of a variable
        speed scroll compressor for R-290 with the focus on compressor
        efficiencies and transferability. International Journal of Refrigeration.

    Parameters:
        N_max (float): Maximal rotations per second of the compressor.
        V_h (float): Swept volume of the compressor in m^3.

    Methods:
        get_lambda_h(inputs: Inputs) -> float:
            Returns the volumetric efficiency based on the regressions of Guth et al. (2022).

        get_eta_isentropic(p_outlet: float, inputs: Inputs) -> float:
            Returns the isentropic efficiency based on the regressions of Guth et al. (2022).

        get_eta_mech(inputs: Inputs) -> float:
            Return the mechanical efficiency of the compressor as fixed value.

    """
    def __init__(self, N_max: float, V_h: float, eta_mech: float = 0.85):

        super().__init__(N_max=N_max, V_h=V_h)
        # Store all parameters as instance variables
        self.eta_mech_const = eta_mech

        self._coeffs = {
            # Coefficients for volumetric efficiency from Table A.1
            "lambda_coeffs": [0.00683154, -0.06876312, 1.00797235],  # [a, b, c]

            # Coefficient matrices for isentropic efficiency from Table A.2
            "eta_is_A0": np.array([
                [9.88235991e-11, -8.83581762e-09, 1.95189394e-07],
                [-9.74390523e-07, 8.65545844e-05, -1.89450724e-03],
                [1.56129544e-03, -1.32067821e-01, 2.69683260e+00]
            ]),
            "eta_is_A1": np.array([
                [-4.06643637e-10, 3.62423302e-08, -7.95868728e-07],
                [4.37082719e-06, -3.87143895e-04, 8.42228834e-03],
                [-7.31600581e-03, 6.11368510e-01, -1.22011957e+01]
            ]),
            "eta_is_A2": np.array([
                [3.81902911e-10, -3.41674867e-08, 7.47429740e-07],
                [-4.73896035e-06, 4.22415809e-04, -9.21630940e-03],
                [8.55048075e-03, -7.20783031e-01, 1.51818016e+01]
            ]),

            # Coefficient matrices for overall compressor efficiency from Table A.3
            "eta_comp_A0": np.array([
                [-3.31242445e-09, 2.37737242e-05, -4.59804512e-02],
                [1.88339750e-08, 6.44687148e-04, 1.36903699e+01],
                [1.04857472e-08, -5.43870648e-04, 1.92659163e+00]
            ]),
            "eta_comp_A1": np.array([
                [-3.66418494e-10, -1.65831030e-05, 3.38019071e-02],
                [1.72087897e-09, 7.13478801e-05, -8.72990757e-02],
                [-1.14880656e-04, 4.76082956e-04, -9.85248276e-01]
            ]),
            "eta_comp_A2": np.array([
                [2.22336271e-09, -8.72990757e-02, -9.85248276e-01],
                [-1.14775474e-08, 4.76082956e-04, 1.92659163e+00],
                [-5.65025114e-08, -9.85248276e-01, -9.85248276e-01]
            ])
        }

    '''def _get_coeffs_for_t_eva(self) -> dict:
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
            return self._coeffs[-8]'''

    def get_lambda_h(self, inputs: Inputs) -> float:
        """
        Returns the volumetric efficiency based on the semi-empirical model of Guth et al. (2022).
        The model uses a 2nd order polynomial depending on the pressure ratio.
        """
        # Calculate pressure ratio
        pi = self.get_p_outlet() / self.state_inlet.p

        # Get coefficients
        a, b, c = self._coeffs["lambda_coeffs"]

        # Equation (20) from Guth et al. (2022)
        lambda_h = a * pi**2 + b * pi + c
        return lambda_h

    def get_eta_isentropic(self, p_outlet: float, inputs: Inputs) -> float:
        """
        Returns the isentropic efficiency based on the semi-empirical model of Guth et al. (2022).
        Depends on pressure ratio, compressor speed, and condensation temperature.
        """
        # --- Get needed input values ---
        pi = p_outlet / self.state_inlet.p
        # Get speed in min^-1
        n = self.N_max * 60
        # Get condensation temperature in °C from outlet pressure
        T_c = self.med_prop.calc_state("PQ", p_outlet, 0).T - 273.15

        # --- Get coefficient matrices ---
        A0 = self._coeffs["eta_is_A0"]
        A1 = self._coeffs["eta_is_A1"]
        A2 = self._coeffs["eta_is_A2"]

        # --- Create vectors for matrix multiplication ---
        n_vec = np.array([n**2, n, 1])
        Tc_vec = np.array([T_c**2, T_c, 1])

        # --- Calculate terms based on Equation (21) from Guth et al. (2022) ---
        # The equation is essentially: term0*pi^2 + term1*pi + term2
        term0 = n_vec @ A0 @ Tc_vec
        term1 = n_vec @ A1 @ Tc_vec
        term2 = n_vec @ A2 @ Tc_vec

        eta_is = term0 * pi**2 + term1 * pi + term2

        # Plausibility check
        if not (0.1 < eta_is < 1.0):
            # Using a warning instead of an error might be better for simulation stability
            print(f"Warning: Calculated isentropic efficiency ({eta_is:.3f}) is outside the plausible range (0.1-1.0).")
        return eta_is

    def get_eta_mech(self, inputs: Inputs) -> float:
        """
        Returns the mechanical efficiency of the compressor.
        """
        # Returns the constant value defined during initialization
        return self.eta_mech_const
