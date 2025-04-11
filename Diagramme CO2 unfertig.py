def main():

    from vclibpy.media import CoolProp, ThermodynamicState, TransportProperties
    import matplotlib.pyplot as plt
    import numpy as np
    #help(cool_prop.calc_state)



    #Zuerst das Arbeitsmittel festlegen
    cool_prop = CoolProp(fluid_name="R744")

    #Hier werden der Startdruck, der Kritische Punkt und der Maximaldruck berechnet
    p_min = cool_prop.calc_state("TQ", 273.15 - 40, 0).p  # Pa
    T_crit, p_crit, d_crit = cool_prop.get_critical_point()
    p_max = p_crit

    #Hier kommt nun die Schrittweite der for Schleife
    p_step = 5000  # Pa
    q0 = []
    q1 = []
    for p in range(int(p_min), int(p_max), p_step):
        q0.append(cool_prop.calc_state("PQ", p, 0))
        q1.append(cool_prop.calc_state("PQ", p, 1))
    # Now, we can plot these states, for example in a T-h Diagram.
    # Note: [::-1] reverts the list, letting it start from the critical point.
    # [state.T for state in q0] is a list comprehension, quite useful in Python.
    p = [state.p for state in q0 + q1[::-1]]
    h = [state.h for state in q0 + q1[::-1]]
    T = [state.T for state in q0 + q1[::-1]]

    # Plot vorbereiten
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # === p-h Diagramm mit Isothermen ===
    ax1.plot(h, p, color="black", label="Sättigungslinie")
    ax1.set_xlabel("$h$ in J/kg")
    ax1.set_ylabel("$p$ in Pa")
    ax1.set_yscale("log")
    ax1.grid(True)
    ax1.set_title("p-h Diagramm mit Isothermen")

    # Isothermen einzeichnen
    T_iso = np.linspace(250, T_crit - 1, 8)
    for T_iso_val in T_iso:
        p_vals = np.geomspace(p_min * 1.1, p_crit * 0.95, 300)
        h_vals = []
        valid_p_vals = []
        for p_val in p_vals:
            try:
                state = cool_prop.calc_state("TP", T_iso_val, p_val)
                h_vals.append(state.h)
                valid_p_vals.append(p_val)
            except:
                continue  # Ungültiger Zustand, einfach überspringen
        if len(valid_p_vals) > 0:
            ax1.plot(h_vals, valid_p_vals, '--', label=f"{int(T_iso_val)} K")
    ax1.legend(fontsize="small")

    # === T-h Diagramm mit Isobaren ===
    ax2.plot(h, T, color="black", label="Sättigungslinie")
    ax2.set_xlabel("$h$ in J/kg")
    ax2.set_ylabel("$T$ in K")
    ax2.grid(True)
    ax2.set_title("T-h Diagramm mit Isobaren")

    # Isobaren einzeichnen
    p_iso = np.geomspace(p_min * 1.1, p_crit * 0.95, 8)
    for p_iso_val in p_iso:
        h_vals = np.linspace(min(h), max(h), 300)
        T_vals = []
        for h_val in h_vals:
            try:
                state = cool_prop.calc_state("PH", p_iso_val, h_val)
                T_vals.append(state.T)
            except:
                T_vals.append(np.nan)
        ax2.plot(h_vals, T_vals, '--', label=f"{int(p_iso_val / 1e5)} bar")
    ax2.legend(fontsize="small")

    plt.tight_layout()
    plt.show()



if __name__ == '__main__':
    main()