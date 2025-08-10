# # Example for a heat pump with a standard cycle
from vclibpy.datamodels import Inputs, FlowsheetState
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

def main():
    from vclibpy.flowsheets import BaseCycle, StandardCycleTC
    from vclibpy.components.heat_exchangers import moving_boundary_ntu, mvb_new
    from vclibpy.components.heat_exchangers import heat_transfer
    condenser = mvb_new.GasCooler(
        A=0.8088,#62.929,
        secondary_medium="air",
        flow_type="counter",
        ratio_outer_to_inner_area=1,#14.569,
        model_approach="ntu",
        two_phase_heat_transfer=heat_transfer.constant.ConstantTwoPhaseHeatTransfer(alpha=2400),
        gas_heat_transfer=heat_transfer.constant.ConstantHeatTransfer(alpha=1200),
        wall_heat_transfer=heat_transfer.wall.WallTransfer(lambda_=np.inf, thickness=1),
        liquid_heat_transfer=heat_transfer.constant.ConstantHeatTransfer(alpha=1500),
        secondary_heat_transfer=heat_transfer.constant.ConstantHeatTransfer(alpha=np.inf),#2000),#54.99),
        n_elemente=50
    )

    evaporator = mvb_new.MVB_Evaporator(
        A=0.2186,
        secondary_medium="air",
        flow_type="counter",
        ratio_outer_to_inner_area=1,
        model_approach="ntu",
        two_phase_heat_transfer=heat_transfer.constant.ConstantTwoPhaseHeatTransfer(alpha=2400),
        gas_heat_transfer=heat_transfer.constant.ConstantHeatTransfer(alpha=1200),
        wall_heat_transfer=heat_transfer.wall.WallTransfer(lambda_=np.inf, thickness=1),
        liquid_heat_transfer=heat_transfer.constant.ConstantHeatTransfer(alpha=1500),#5000),
        secondary_heat_transfer=heat_transfer.constant.ConstantHeatTransfer(alpha=np.inf)#500)
    )
    from vclibpy.components.expansion_valves import Bernoulli
    expansion_valve = Bernoulli(A=0.1)

    from vclibpy.components.compressors import ConstantEffectivenessCompressor
    compressor = ConstantEffectivenessCompressor(
        N_max=100,
        V_h=8.34e-6,
        eta_mech=1,
        eta_isentropic=0.7,
        lambda_h=0.9
    )

    # Now, we can plug everything into the flowsheet:
    heat_pump = StandardCycleTC(
        evaporator=evaporator,
        condenser=condenser,
        fluid="CO2",
        compressor=compressor,
        expansion_valve=expansion_valve,
    )
    inputs = Inputs(
        T_eva_in=0 + 273.15,
        T_con_in=25 + 273.15,
        dT_eva_superheating=10,
        dT_con_subcooling=0,
        m_flow_eva=1,
        m_flow_con=1,
        n=1
    )

    #inputs.set(name="q4", value=0.3, description="Quality of refrigerant at exp_valve outlet")


    fs_state = heat_pump.calc_steady_state(inputs=inputs)
    #print(fs_state)
    results_path = Path("results")
    save_state_to_excel(fs_state=fs_state, inputs=inputs, save_path=results_path)



if __name__ == "__main__":
    main()
