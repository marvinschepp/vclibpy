def main():
    from vclibpy.media import CoolProp
    cool_prop = CoolProp(fluid_name = "CO2")
    help(cool_prop.calc_state)
    state = cool_prop.calc_state("PT", 75e5, 400)
    print(type(state))
    print(state.get_pretty_print())

    sat = cool_prop.calc_state("TQ", 400, 1)
    print("Sättigungsdruck bei 400 K:", sat.p / 1e5, "bar")

if __name__ == '__main__':
    main()