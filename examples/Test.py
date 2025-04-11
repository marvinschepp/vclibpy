import matplotlib.pyplot as plt
from CoolProp.Plots import PropertyPlot
import CoolProp

def main():
    # Fluid festlegen
    fluid = 'R744'

    # p-h Diagramm erstellen
    ph_plot = PropertyPlot(fluid, 'PH', unit_system='EUR', tp_limits='ACHP')

    # Isothermen hinzufügen
    ph_plot.calc_isolines(CoolProp.iT, num=10)

    # Diagramm anzeigen
    ph_plot.show()

if __name__ == '__main__':
    main()
