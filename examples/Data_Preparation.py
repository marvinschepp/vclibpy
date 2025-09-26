# Benötigte Bibliotheken importieren
import pandas as pd
from pathlib import Path
import re

# =============================================================================
# HIER MUSST DU DEINE PFADE ANPASSEN
# =============================================================================

# 1. Der absolute Pfad zum Hauptordner, in dem deine TP-Ordner liegen.
#    WICHTIG: Benutze ein r"..." für den Pfad unter Windows.
QUELLE_ORDNER = r"G:\Meine Ablage\Masterarbeit\R290"

# 2. Der Name des Zielordners, in dem alle CSVs gesammelt werden.
#    Dieser Ordner wird automatisch erstellt, falls er nicht existiert.
#    Idealerweise ist das der "Rohdaten"-Ordner für unser erstes Skript.
ZIEL_ORDNER = r"G:\Meine Ablage\Masterarbeit\R290\Rohdaten"


# =============================================================================
# AB HIER LÄUFT DIE AUTOMATISCHE VERARBEITUNG
# =============================================================================

def dateien_vorbereiten():
    """
    Durchsucht den Quellen-Ordner, konvertiert gefundene .xlsx-Dateien
    und benennt sie anhand der Ordnerstruktur um.
    """
    quelle = Path(QUELLE_ORDNER)
    ziel = Path(ZIEL_ORDNER)

    # Erstelle den Ziel-Ordner, falls er noch nicht existiert
    ziel.mkdir(exist_ok=True)

    print(f"🔎 Durchsuche den Ordner '{quelle}' nach .xlsx-Dateien...")

    # Finde ALLE .xlsx-Dateien in allen Unterordnern
    xlsx_dateien = list(quelle.glob("**/*.xlsx"))

    if not xlsx_dateien:
        print("❌ Keine .xlsx-Dateien gefunden. Bitte den QUELLE_ORDNER überprüfen.")
        return

    print(f"✅ {len(xlsx_dateien)} Dateien gefunden. Starte Konvertierung...")

    # Gehe jede gefundene Excel-Datei durch
    for excel_pfad in xlsx_dateien:
        try:
            # Extrahiere die benötigten Teile aus dem Pfad
            pfad_teile = excel_pfad.parts

            # Finde die relevanten Informationen im Pfad
            testpunkt_teil = next((teil for teil in pfad_teile if teil.startswith("TP_")), None)
            auslegungspunkt_teil = next((teil for teil in pfad_teile if teil.startswith("AP")), None)
            modell_teil = next((teil for teil in pfad_teile if teil in ["Const", "Guth"]), None)

            if not all([testpunkt_teil, auslegungspunkt_teil, modell_teil]):
                print(f"⚠️ Konnte nicht alle Informationen extrahieren für: {excel_pfad}. Überspringe.")
                continue

            # Bereinige die extrahierten Teile
            testpunkt = testpunkt_teil.split('_')[1]
            auslegungspunkt = re.findall(r'\d+', auslegungspunkt_teil)[0]
            modell = modell_teil

            # Baue den neuen Dateinamen
            neuer_dateiname = f"TP{testpunkt}_AP{auslegungspunkt}_{modell}.csv"
            ziel_pfad = ziel / neuer_dateiname

            # Lese die Excel-Datei und speichere sie als CSV
            excel_df = pd.read_excel(excel_pfad)
            excel_df.to_csv(ziel_pfad, sep=';', index=False)

            print(f"-> '{neuer_dateiname}' erfolgreich erstellt.")

        except Exception as e:
            print(f"❌ Fehler bei der Verarbeitung von {excel_pfad}: {e}")

    print("\n✨ Vorbereitung abgeschlossen! Alle Dateien wurden konvertiert.")


# Führe die Hauptfunktion aus
if __name__ == "__main__":
    dateien_vorbereiten()