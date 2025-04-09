def main():
    from vclibpy.media import CoolProp
    import numpy as np
    import matplotlib.pyplot as plt


    cool_prop = CoolProp(fluid_name = "R744")
    #help(cool_prop.calc_state)
    state = cool_prop.calc_state("PT", 75e5, 400)
    #print(type(state))
    #print(state.get_pretty_print())
    transport_properties = cool_prop.calc_transport_properties(state=state)
    #print(transport_properties.get_pretty_print())
    p_min = cool_prop.calc_state("TQ", 273.15 - 40, 0).p
    T_crit, p_crit, d_crit = cool_prop.get_critical_point()
    p_max = p_crit

    p_step  = 10000 # in Pa, um nur in 10000 Pa Schritten zu rechnen
    q0 = []
    q1 = []
    for p in range(int(p_min), int(p_max), p_step):
        q0.append(cool_prop.calc_state("PQ", p, 0))
        q1.append(cool_prop.calc_state("PQ", p, 1))
    T = [state.T for state in q0 + q1[::-1]]
    h = [state.h for state in q0 + q1[::-1]]
    import matplotlib.pyplot as plt
    plt.ylabel("$T$ in K")
    plt.xlabel("$h$ in J/kg")
    plt.plot(h, T, color="black")
    state_1 = cool_prop.calc_state("PT", 34.85e5, 273.15 + 5)
    state_2 = cool_prop.calc_state("PH", 80e5, 488870)
    state_3 = cool_prop.calc_state("PT", 80e5, 273.15 + 27)
    state_4 = cool_prop.calc_state("PH", 34.85e5, 270550)

    print(state_1)
    print(state_2)
    print(state_3)
    print(state_4)

    plot_lines_h = [state_1.h, state_2.h, state_3.h, state_4.h, state_1.h]
    plot_lines_t = [state_1.T, state_2.T, state_3.T, state_4.T, state_1.T]
    plt.plot(plot_lines_h, plot_lines_t, marker="s", color="red")
    # Zustände beschriften
    state_labels = ["1", "2", "3", "4"]
    states = [state_1, state_2, state_3, state_4]

    for i, state in enumerate(states):
        plt.annotate(f"State {state_labels[i]}",
                     (state.h, state.T),
                     textcoords="offset points",
                     xytext=(5, 5),
                     ha='left',
                     fontsize=9,
                     color='blue')

    plt.show()



if __name__ == '__main__':
    main()