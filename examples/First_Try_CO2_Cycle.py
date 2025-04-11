from vclibpy.components.heat_exchangers import MovingBoundaryNTUEvaporator
#help(MovingBoundaryNTUEvaporator)
from vclibpy.components.heat_exchangers.heat_transfer.constant import (
    ConstantHeatTransfer, ConstantTwoPhaseHeatTransfer
)
from vclibpy.components.heat_exchangers.heat_transfer.wall import WallTransfer
evaporator = MovingBoundaryNTUEvaporator(
    A=15,
    secondary_medium="air",
    flow_type="counter",
    ratio_outer_to_inner_area=10,
    two_phase_heat_transfer=ConstantTwoPhaseHeatTransfer(alpha=1000),
    gas_heat_transfer=ConstantHeatTransfer(alpha=1000),
    wall_heat_transfer=WallTransfer(lambda_=236, thickness=2e-3),
    liquid_heat_transfer=ConstantHeatTransfer(alpha=5000),
    secondary_heat_transfer=ConstantHeatTransfer(alpha=25)
)
