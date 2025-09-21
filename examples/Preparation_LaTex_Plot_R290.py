import pandas as pd
from pathlib import Path

# --- PFADE ANPASSEN ---
input_file = Path(r"D:\11_Auslegung_CO2\TP_1\R290.csv")
output_folder = Path(r"D:\11_Auslegung_CO2\TP_1\plotdaten_final")

try:
    output_folder.mkdir(parents=True, exist_ok=True)
    # Lese die komplette, originale CSV-Datei ein
    df = pd.read_csv(input_file, sep=';')
    print(f"✅ '{input_file.name}' erfolgreich eingelesen.")


    # Korrekte Reihenfolge für den thermodynamischen Kreisprozess 1->2->3->4
    df_cycle_corners = pd.DataFrame([
        df.iloc[2],  # ZP 1 (deine Zeile 4)
        df.iloc[4],  # ZP 2 (deine Zeile 5)
        df.iloc[9],  # ZP 3 (deine Zeile 54)
        df.iloc[0]  # ZP 4 (deine Zeile 55)
    ])

    # Die glatte Kurve nehmen wir weiterhin aus allen "cycle_point"-Einträgen
    df_cycle_full_curve = df[df['label'].str.contains('cycle_point')].copy()

    # --- 2. SÄTTIGUNGSLINIEN BEREINIGEN (Lücke & Artefakt entfernen) ---
    df_sat_liquid = df[df['label'] == 'sat_liquid'].sort_values(by='h_kJ_kg')
    df_sat_vapor = df[df['label'] == 'sat_vapor'].copy()
    # Artefakt rechts unten entfernen
    #df_sat_vapor = df_sat_vapor[df_sat_vapor['T_C'] > -50].copy()

    # Lücke schließen
    last_liquid_p = df_sat_liquid.iloc[-1]
    first_vapor_p = df_sat_vapor.iloc[0]
    critical_h = (last_liquid_p['h_kJ_kg'] + first_vapor_p['h_kJ_kg']) / 2
    critical_T = (last_liquid_p['T_C'] + first_vapor_p['T_C']) / 2
    critical_p = (last_liquid_p['p_bar'] + first_vapor_p['p_bar']) / 2
    critical_point = pd.DataFrame([{'h_kJ_kg': critical_h, 'T_C': critical_T, 'p_bar': critical_p}])
    df_sat_liquid = pd.concat([df_sat_liquid, critical_point], ignore_index=True)
    df_sat_vapor = pd.concat([critical_point, df_sat_vapor], ignore_index=True)

    # --- 3. SEKUNDÄRSEITEN (unverändert) ---
    df_condenser = df[df['label'].str.contains('sec_condenser')]
    df_evaporator = df[df['label'].str.contains('sec_evaporator')]

    # --- 4. ALLE DATEIEN SPEICHERN ---
    output_files = {
        'cycle_full_curve.csv': df_cycle_full_curve,
        'cycle_corner_points.csv': df_cycle_corners,
        'saturation_liquid.csv': df_sat_liquid,
        'saturation_vapor.csv': df_sat_vapor,
        'secondary_condenser.csv': df_condenser,
        'secondary_evaporator.csv': df_evaporator,
    }
    print(f"\nSpeichere Dateien in: '{output_folder.resolve()}'")
    for filename, dataframe in output_files.items():
        dataframe.to_csv(output_folder / filename, sep=';', decimal='.', index=False)

    # --- 5. LATEX-CODE FÜR KORREKTE ECKPUNKTE GENERIEREN ---
    print("\n\n" + "=" * 60)
    print("⬇️  Kopiere den folgenden Block in deine diagramm_standalone.tex ⬇️")
    print("=" * 60)
    positions = ['below right', 'left', 'above left', 'left']
    for i, (index, row) in enumerate(df_cycle_corners.iterrows()):
        h_coord = row['h_kJ_kg']

        # --- NEU: Spezialbehandlung für Punkt 2 ---
        if i + 1 == 2:
            h_coord = h_coord - 3.0  # Ziehe 3 von der h-Koordinate ab
        print(
            f"\\node at (axis cs: {h_coord:.2f}, {row['p_bar']:.2f})  [{positions[i]}, font=\\Large] {{{i + 1}}};")
    print("=" * 60)

except Exception as e:
    print(f"❌ EIN FEHLER IST AUFGETRETEN: {e}")