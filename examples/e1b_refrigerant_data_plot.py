import numpy as np
import matplotlib.pyplot as plt
import pandas as pd  # Import für den Excel-Export
from vclibpy.media import RefProp


def analyze_co2_properties():
    """
    Berechnet und visualisiert verschiedene Stoffeigenschaften von CO2
    über einen Temperaturbereich bei verschiedenen Drücken und speichert sie in Excel.
    """
    try:
        ref_prop = RefProp(fluid_name="CO2")
    except Exception as e:
        print(f"Fehler bei der Initialisierung von RefProp: {e}")
        print("Stelle sicher, dass REFPROP korrekt installiert und konfiguriert ist.")
        return

    # --- Konfiguration ---
    # Druckniveaus in bar
    pressures_bar = [75, 80, 85, 90, 95, 100, 150, 200, 250]

    # Temperaturbereich in Celsius mit 1000 Datenpunkten
    temperatures_C = np.linspace(25, 100, 400)

    all_data = {p: {} for p in pressures_bar}

    # --- Datenberechnung ---
    print("Starte die Berechnung der Stoffdaten für 1000 Punkte pro Druckniveau...")
    for p_bar in pressures_bar:
        results = {
            'temps_C': [],
            'density_kg_m3': [],
            'dyn_vis_Pas': [],
            'therm_cond_W_mK': []
        }

        p_Pa = p_bar * 1e5

        for T_C in temperatures_C:
            T_K = T_C + 273.15
            try:
                state = ref_prop.calc_state("PT", p_Pa, T_K)
                transport_props = ref_prop.calc_transport_properties(state=state)

                results['temps_C'].append(T_C)
                results['density_kg_m3'].append(state.d)
                results['dyn_vis_Pas'].append(transport_props.dyn_vis)
                # Korrekter Attributname für Wärmeleitfähigkeit ist lambda_val
                results['therm_cond_W_mK'].append(transport_props.lam)
            except Exception as e:
                print(f"Warnung: Berechnung bei P={p_bar} bar, T={T_C}°C fehlgeschlagen. Fehler: {e}")

        all_data[p_bar] = results

    print("Berechnung abgeschlossen.")

    # --- Daten als Excel-Datei speichern ---
    print("Konvertiere Daten und speichere sie in Excel...")
    pressure_col, temp_col, density_col, viscosity_col, conductivity_col = [], [], [], [], []

    for p_bar, res in all_data.items():
        num_points = len(res['temps_C'])
        pressure_col.extend([p_bar] * num_points)
        temp_col.extend(res['temps_C'])
        density_col.extend(res['density_kg_m3'])
        viscosity_col.extend(res['dyn_vis_Pas'])
        conductivity_col.extend(res['therm_cond_W_mK'])

    df = pd.DataFrame({
        'Druck [bar]': pressure_col,
        'Temperatur [°C]': temp_col,
        'Dichte [kg/m³]': density_col,
        'Dyn. Viskosität [Pa·s]': viscosity_col,
        'Wärmeleitfähigkeit [W/m·K]': conductivity_col
    })

    excel_filename = 'co2_stoffdaten.xlsx'
    try:
        df.to_excel(excel_filename, index=False, engine='openpyxl')
        print(f"Daten erfolgreich in '{excel_filename}' gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern der Excel-Datei: {e}")
        print("Stelle sicher, dass 'pandas' und 'openpyxl' installiert sind: pip install pandas openpyxl")

    # --- Plotting ---
    print("Erstelle die Plots...")

    # Plot 1: Dichte (rho)
    plot_property(
        data=all_data,
        key='density_kg_m3',
        title='Dichte ($\\rho$) von CO$_2$',
        ylabel='Dichte $\\rho$ [kg/m³]'
    )

    # Plot 2: Dynamische Viskosität (eta)
    plot_property(
        data=all_data,
        key='dyn_vis_Pas',
        title='Dynamische Viskosität ($\\eta$) von CO$_2$',
        ylabel='Dynamische Viskosität $\\eta$ [Pa·s]'
    )

    # Plot 3: Wärmeleitfähigkeit (lambda)
    plot_property(
        data=all_data,
        key='therm_cond_W_mK',
        title='Wärmeleitfähigkeit ($\\lambda$) von CO$_2$',
        ylabel='Wärmeleitfähigkeit $\\lambda$ [W/m·K]'
    )
    # Zeige alle erstellten Plots am Ende an
    plt.show()


def plot_property(data, key, title, ylabel):
    """
    Eine Helferfunktion, um ein beliebiges Stoffdatum zu plotten.
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 7))

    for p_bar, results in data.items():
        # Stelle sicher, dass Daten für x und y existieren und die gleiche Länge haben
        if results and len(results['temps_C']) == len(results[key]):
            ax.plot(results['temps_C'], results[key], label=f'{p_bar} bar')

    ax.set_xlabel('Temperatur [°C]')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(title='Druck')

    if data:
        # Setzt die Grenzen der x-Achse auf den berechneten Bereich
        temp_list = next(iter(data.values()))['temps_C']
        if temp_list:
            ax.set_xlim(min(temp_list), max(temp_list))

    plt.tight_layout()
    # plt.show() wird nun am Ende des Hauptskripts aufgerufen


if __name__ == '__main__':
    analyze_co2_properties()