import numpy as np
from vclibpy.media import RefProp

def main():

    ref_prop = RefProp(fluid_name="CO2")

    help(ref_prop.calc_transport_properties)
    state_in = ref_prop.calc_state("PT", 84.533e5, 77.27 + 273.15)
    state_out = ref_prop.calc_state("PT", 84.533e5, 31.39 + 273.15)
    transport_properties_in = ref_prop.calc_transport_properties(state=state_in)
    transport_properties_out = ref_prop.calc_transport_properties(state=state_out)
    rho_mean = (state_in.d + state_out.d) / 2
    eta_mean = (transport_properties_in.dyn_vis + transport_properties_out.dyn_vis) / 2

    d_i = 8.740 * 10**-3 # [m]
    l_tube = 0.950 # [m]
    num_tubes_total = 220
    num_passes = 54
    tubes_per_pass = num_tubes_total / num_passes
    m_flow = 0.0848643062000998
    m_flow_per_tube = m_flow / tubes_per_pass
    l_total_flow_path = l_tube * num_passes

    v_flow_per_tube = m_flow_per_tube / rho_mean
    A_pipe = np.pi / 4 * d_i**2
    velocity = v_flow_per_tube / A_pipe
    print(f"v = {velocity} m/s")

    Re = rho_mean * velocity * d_i / eta_mean
    print(Re)


    if 3000 < Re < 100000:
        print(f"Turbulent flow with Re={Re:.0f}")
        zeta = 0.3164 * Re**-0.25
        print(f"Zeta = {zeta}")
        delta_p = zeta * l_total_flow_path / d_i * rho_mean * velocity**2 / 2
        print(f"delta_p = {delta_p / 10e5} bar")
    elif Re < 3000:
        print(f"Laminar flow with Re={Re:.0f}")
        zeta = 64 / Re
        print(f"Zeta = {zeta}")
        delta_p = zeta * l_tube / d_i * rho_mean * velocity**2 / 2
        print(f"delta_p = {delta_p / 10e5} bar")

def conservative_pressure_loss():
    ref_prop = RefProp(fluid_name="CO2")

    # help(ref_prop.calc_state)
    state_in = ref_prop.calc_state("PT", 75e5, 75.15 + 273.15)
    state_out = ref_prop.calc_state("PT", 75e5, 31.95 + 273.15)
    transport_properties_in = ref_prop.calc_transport_properties(state=state_in)
    transport_properties_out = ref_prop.calc_transport_properties(state=state_out)
    rho_mean = (state_in.d + state_out.d) / 2
    eta_mean = (transport_properties_in.dyn_vis + transport_properties_out.dyn_vis) / 2

    d_i = 8.740 * 10 ** -3  # [m]
    l_tube = 0.950  # [m]
    num_tubes_total = 220
    num_passes = 54
    #tubes_per_pass = num_tubes_total / num_passes
    m_flow = 0.041269133996131344
    m_flow_per_tube = m_flow / num_tubes_total
    l_total_flow_path = l_tube * num_passes

    v_flow_per_tube = m_flow_per_tube / rho_mean
    A_pipe = np.pi / 4 * d_i ** 2
    velocity = v_flow_per_tube / A_pipe
    print(f"v = {velocity} m/s")

    Re = rho_mean * velocity * d_i / eta_mean
    print(Re)

    if 3000 < Re < 100000:
        print(f"Turbulent flow with Re={Re:.0f}")
        zeta = 0.3164 * Re ** -0.25
        print(f"Zeta = {zeta}")
        delta_p = zeta * l_total_flow_path / d_i * rho_mean * velocity ** 2 / 2
        print(f"delta_p = {delta_p / 10e5} bar")
    elif Re < 3000:
        print(f"Laminar flow with Re={Re:.0f}")
        zeta = 64 / Re
        print(f"Zeta = {zeta}")
        delta_p = zeta * l_tube / d_i * rho_mean * velocity ** 2 / 2
        print(f"delta_p = {delta_p / 10e5} bar")

if __name__ == "__main__":
    main()
    #conservative_pressure_loss()