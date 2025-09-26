# Benötigte Bibliotheken importieren
import pandas as pd
import re
from pathlib import Path

# =============================================================================
# HIER KANNST DU EINSTELLUNGEN VORNEHMEN
# =============================================================================

# 1. Gib den Namen des Ordners an, in dem deine CSV-Dateien liegen.
#    Das Skript erwartet diesen Ordner im selben Verzeichnis wie das Skript selbst.
ROHDATEN_ORDNER = r"G:\Meine Ablage\Masterarbeit\R290\Rohdaten"

# 2. Lege den Namen für die finale Excel-Datei fest.
OUTPUT_EXCEL_DATEI = r"G:\Meine Ablage\Masterarbeit\R290\Auswertung_Verdichter.xlsx"

# 3. Diese Zuordnung verbindet deine Wunschnamen (links) mit den Namen in der CSV (rechts).
#    Hier kannst du bei Bedarf Anpassungen vornehmen.
PARAMETER_MAPPING = {
    'COP': 'COP',
    'Q_con': 'Q_con',
    'Q_eva': 'Q_eva',
    'P_el': 'P_el',
    'Drehzahl': 'compressor_speed',
    'Eva_Error': 'ErrorEva',
    'Eva_Pinch': 'Eva_Pinch',
    'Con_Error': 'ErrorCon',
    'Con_Pinch': 'Con_Pinch',
    'Eta_is': 'eta_is',
    'Lambda': 'lambda_h',
    'p_con': 'REF_p_2',
    'p_eva': 'REF_p_1'
}


# =============================================================================
# AB HIER LÄUFT DIE AUTOMATISCHE VERARBEITUNG
# =============================================================================

def daten_verarbeiten():
    """
    Hauptfunktion, die alle CSV-Dateien verarbeitet und in einer Excel-Datei zusammenfasst.
    """
    # Definiere die Pfade basierend auf dem Skript-Verzeichnis
    script_pfad = Path(__file__).parent
    rohdaten_pfad = script_pfad / ROHDATEN_ORDNER
    output_pfad = script_pfad / OUTPUT_EXCEL_DATEI

    if not rohdaten_pfad.is_dir():
        print(f"❌ Fehler: Der Ordner '{ROHDATEN_ORDNER}' wurde nicht gefunden.")
        print("Bitte erstelle den Ordner und lege deine CSV-Dateien hinein.")
        return

    # Leeres Dictionary, um die Tabellen (DataFrames) zu sammeln
    daten_sammlung = {}

    # Regex-Muster, um Testpunkt, Auslegungspunkt und Modell aus dem Dateinamen zu lesen
    dateiname_muster = re.compile(r"TP(\d+)_AP(\d+)_(Guth|Const)\.CSV", re.IGNORECASE)

    print(f"🔎 Lese Dateien aus dem Ordner '{ROHDATEN_ORDNER}'...")

    # Gehe jede CSV-Datei im Ordner durch
    csv_dateien = list(rohdaten_pfad.glob("*.csv"))
    if not csv_dateien:
        print(f"❌ Keine CSV-Dateien in '{ROHDATEN_ORDNER}' gefunden.")
        return

    for dateipfad in csv_dateien:
        match = dateiname_muster.match(dateipfad.name)
        if not match:
            print(f"⚠️ Überspringe Datei mit ungültigem Namen: {dateipfad.name}")
            continue

        # Extrahiere Infos aus dem Dateinamen
        testpunkt, auslegungspunkt, modell = int(match.group(1)), int(match.group(2)), match.group(3)
        tabellen_name = f"AP{auslegungspunkt}_{modell}"

        try:
            # Lese die CSV-Datei ein.
            # NEU: Wir nutzen die erste Zeile als Header (header=0) und lesen
            # gezielt nur die Spalten 'Parameter' und 'Value' ein (usecols).
            csv_daten = pd.read_csv(
                dateipfad,
                sep=';',
                header=0,  # Erste Zeile als Spaltenüberschrift verwenden
                index_col='Parameter',  # Die Spalte 'Parameter' als Index nutzen
                usecols=['Parameter', 'Value']  # Nur diese beiden Spalten laden
            ).squeeze("columns")

            # Hole die gewünschten Werte anhand des Mappings
            ausgelesene_werte = {spalte: csv_daten.get(csv_param) for spalte, csv_param in PARAMETER_MAPPING.items()}

            # Wenn die Tabelle für diese Konfiguration (z.B. "AP2_Const") noch nicht existiert, erstelle sie
            if tabellen_name not in daten_sammlung:
                daten_sammlung[tabellen_name] = pd.DataFrame(columns=PARAMETER_MAPPING.keys())
                daten_sammlung[tabellen_name].index.name = "Testpunkt"

            # Füge die ausgelesenen Werte als neue Zeile hinzu (Index = Testpunkt)
            daten_sammlung[tabellen_name].loc[testpunkt] = ausgelesene_werte

        except Exception as e:
            print(f"❌ Fehler beim Verarbeiten der Datei {dateipfad.name}: {e}")

    # Schreibe die gesammelten Daten in eine Excel-Datei
    if not daten_sammlung:
        print("Keine Daten zum Speichern vorhanden.")
        return

    print(f"\n✅ Datenverarbeitung abgeschlossen. {len(daten_sammlung)} Tabellen werden erstellt.")
    print(f"💾 Speichere Ergebnisse in '{OUTPUT_EXCEL_DATEI}'...")

    with pd.ExcelWriter(output_pfad) as writer:
        # Sortiere die Tabellen alphabetisch nach Namen für eine saubere Reihenfolge der Arbeitsblätter
        for tabellen_name in sorted(daten_sammlung.keys()):
            df = daten_sammlung[tabellen_name].sort_index()  # Sortiere nach Testpunkt-Index
            df.to_excel(writer, sheet_name=tabellen_name)

    print("\n✨ Fertig! Die Excel-Datei wurde erfolgreich erstellt.")


# Führe die Hauptfunktion aus, wenn das Skript direkt gestartet wird
if __name__ == "__main__":
    daten_verarbeiten()