from vclibpy.datamodels import Inputs, FlowsheetState
from vclibpy.flowsheets import BaseCycleTC, StandardCycleTC, StandardCycle
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

def save_state_to_excel(fs_state: FlowsheetState, inputs: Inputs, save_path: Path):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    t_eva_in_c = int(inputs.T_eva_in - 273.15)
    t_con_in_c = int(inputs.T_con_in - 273.15)

    file_name = f"{t_eva_in_c}_{t_con_in_c}_{timestamp}.xlsx"
    full_path = save_path / file_name

    data_list = []
    for key, state_var in fs_state.items():
        data_list.append({
            "Parameter": key,
            "Value": state_var.value,
            "Unit": state_var.unit,
            "Description": state_var.description
        })

    df = pd.DataFrame(data_list)


    save_path.mkdir(parents=True, exist_ok=True)

    print(f"DEBUG: Attempting to save to path: {repr(str(full_path))}")

    df.to_excel(full_path, index=False, engine='openpyxl')

    print(f"✅ Results successfully saved to: {full_path}")

def save_plot_data_to_csv(flowsheet: StandardCycle, fs_state: FlowsheetState, save_path: Path):

    """

    Sammelt und speichert alle relevanten Datenpunkte für T-h- und log(p)-h-Diagramme in einer CSV-Datei.

    """

    print("\n--- Erstelle Plot-Daten für CSV-Export ---")

    try:

        all_plot_points = []

        # Teil 1 & 2: Kreislaufpunkte und Sättigungslinien (unverändert)

        cycle_states = flowsheet.get_states_in_order_for_plotting()

        for i, s in enumerate(cycle_states):
            all_plot_points.append(
                {'label': f'cycle_point_{i + 1}', 'h_kJ_kg': s.h / 1000, 'T_C': s.T - 273.15, 'p_bar': s.p / 1e5})

        h_sat = flowsheet.med_prop.get_two_phase_limits('h')
        T_sat = flowsheet.med_prop.get_two_phase_limits('T')
        p_sat = flowsheet.med_prop.get_two_phase_limits('p')

        split_idx = len(h_sat) // 2
        for i in range(split_idx):
            all_plot_points.append({'label': 'sat_liquid', 'h_kJ_kg': h_sat[i] / 1000, 'T_C': T_sat[i] - 273.15, 'p_bar': p_sat[i] / 1e5})

        for i in range(split_idx, len(h_sat)):
            all_plot_points.append({'label': 'sat_vapor', 'h_kJ_kg': h_sat[i] / 1000, 'T_C': T_sat[i] - 273.15, 'p_bar': p_sat[i] / 1e5})



        # Teil 3: KORREKTUR - Zugriff auf das fs_state Objekt

        # Gaskühler/Kondensator Sekundärseite
        all_plot_points.append({
        'label': 'sec_condenser_in',
        'h_kJ_kg': flowsheet.condenser.state_outlet.h / 1000,
        'T_C': fs_state.get('SEC_T_con_in').value, # KORREKTUR: Wert aus fs_state (bereits in °C)
        'p_bar': None
        })

        all_plot_points.append({
        'label': 'sec_condenser_out',
        'h_kJ_kg': flowsheet.condenser.state_inlet.h / 1000,
        'T_C': fs_state.get('SEC_T_con_out').value, # KORREKTUR: Wert aus fs_state (bereits in °C)
        'p_bar': None
        })

        # Verdampfer Sekundärseite
        all_plot_points.append({
        'label': 'sec_evaporator_in',
        'h_kJ_kg': flowsheet.evaporator.state_outlet.h / 1000,
        'T_C': fs_state.get('SEC_T_eva_in').value, # KORREKTUR: Wert aus fs_state (bereits in °C)
        'p_bar': None
        })

        all_plot_points.append({
        'label': 'sec_evaporator_out',
        'h_kJ_kg': flowsheet.evaporator.state_inlet.h / 1000,
        'T_C': fs_state.get('SEC_T_eva_out').value, # KORREKTUR: Wert aus fs_state (bereits in °C)
        'p_bar': None
        })

        # Teil 4: Speichern (unverändert)
        df_plot = pd.DataFrame(all_plot_points)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"plot_data_{timestamp}.csv"
        csv_path = save_path / file_name
        df_plot.to_csv(csv_path, sep=';', decimal='.', index=False)
        print(f"✅ Plot-Daten erfolgreich gespeichert in: {csv_path}")

        return csv_path



    except Exception as e:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"\n--- 🚨 FEHLER: Plot-Daten konnten nicht gespeichert werden. Grund: {e} (in Zeile {exc_tb.tb_lineno}) ---")
        return None

def main():
    from vclibpy.flowsheets import BaseCycle, StandardCycleTC
    from vclibpy.components.heat_exchangers import mvb_new
    from vclibpy.components.heat_exchangers import heat_transfer

    A_con_oka_2 = 19.75262150362
    A_eva_oka_2 = 10.9940748710396
    V_h_oka_2 = 8.6614346007427E-06

    A_con_const_2 = 20.2628558750705
    A_eva_const_2 = 11.3432789455855
    V_h_const_2 = 7.903384455858833E-06

    A_con_oka_4 = 46.3228647344602
    A_eva_oka_4 = 30.7527707916683
    V_h_oka_4 = 1.91565645203768E-05

    A_con_oka_6 = 6.77961238570236
    A_eva_oka_6 = 7.57119235043258
    V_h_oka_6 = 8.99983781814193E-06

    A_con_const_4 = 48.0041947850241
    A_eva_const_4 = 32.1418700052833
    V_h_const_4 = 1.65572283091709E-05

    A_con_const_6 = 7.07323327063744
    A_eva_const_6 = 7.94778647340534
    V_h_const_6 = 7.35676811701068E-06

    m_con_oka = 0.981028521910861
    m_eva_oka = 0.846920801952098
    m_con_const = 0.981028521910861
    m_eva_const = 0.87944217829006

    condenser = mvb_new.MVB_Condenser(
        A=A_con_oka_6,
        secondary_medium="air",
        flow_type="counter",
        ratio_outer_to_inner_area=1,
        model_approach="ntu",
        two_phase_heat_transfer=heat_transfer.constant.ConstantTwoPhaseHeatTransfer(alpha=2400),
        gas_heat_transfer=heat_transfer.constant.ConstantHeatTransfer(alpha=1200),
        wall_heat_transfer=heat_transfer.wall.WallTransfer(lambda_=np.inf, thickness=1),
        liquid_heat_transfer=heat_transfer.constant.ConstantHeatTransfer(alpha=1500),
        secondary_heat_transfer=heat_transfer.constant.ConstantHeatTransfer(alpha=50),
    )

    evaporator = mvb_new.MVB_Evaporator(
        A=A_eva_oka_6,
        secondary_medium="air",
        flow_type="counter",
        ratio_outer_to_inner_area=1,
        model_approach="ntu",
        two_phase_heat_transfer=heat_transfer.constant.ConstantTwoPhaseHeatTransfer(alpha=3000),
        gas_heat_transfer=heat_transfer.constant.ConstantHeatTransfer(alpha=1200),
        wall_heat_transfer=heat_transfer.wall.WallTransfer(lambda_=np.inf, thickness=1),
        liquid_heat_transfer=heat_transfer.constant.ConstantHeatTransfer(alpha=1500),
        secondary_heat_transfer=heat_transfer.constant.ConstantHeatTransfer(alpha=50),
        use_pressure_loss=False,
    )
    from vclibpy.components.expansion_valves import Bernoulli
    expansion_valve = Bernoulli(A=0.1)

    from vclibpy.components.compressors import ConstantEffectivenessCompressor, Okasha_CO2_Rec
    compressor = Okasha_CO2_Rec(
        N_max=50,
        V_h=V_h_oka_6,
        eta_mech=1.0,
    )

    '''from vclibpy.components.compressors import ConstantEffectivenessCompressor
    compressor = ConstantEffectivenessCompressor(
        N_max=50,
        V_h=V_h_const_4,
        eta_isentropic=0.7,
        lambda_h=0.9,
        eta_mech=1.0,
    )'''

    # Now, we can plug everything into the flowsheet:
    flowsheet = StandardCycle(
        evaporator=evaporator,
        condenser=condenser,
        fluid="CO2",
        compressor=compressor,
        expansion_valve=expansion_valve,
    )

    inputs = Inputs(
        fix_speed=False,
        #fix_m_flow_con=False,
        #fix_m_flow_eva=False,
        T_eva_in=14.0322332 + 273.15,
        T_con_in=17.5941378 + 273.15,
        dT_eva_superheating=10,
        dT_con_subcooling=5,
        m_flow_eva=m_eva_oka,
        m_flow_con=m_con_oka,
        n=1,
        #T_eva_out=10 + 273.15 -5,
        #T_con_out=273.15+40,
        Q_con=2513.221,  # W
    )

    #inputs.set(name="q4", value=0.3, description="Quality of refrigerant at exp_valve outlet")

    results_path = Path(r"D:\11_Auslegung_CO2\TP_10\AP6\Oka_Sub")
    results_path.mkdir(parents=True, exist_ok=True)
    print(f"Saving results in '{results_path.absolute()}'.")

    fs_state = flowsheet.calc_steady_state(inputs=inputs, save_path_plots=results_path)
    #print(fs_state)

    save_state_to_excel(fs_state=fs_state, inputs=inputs, save_path=results_path)
    save_plot_data_to_csv(flowsheet, fs_state, save_path=results_path)


if __name__ == "__main__":
    main()
