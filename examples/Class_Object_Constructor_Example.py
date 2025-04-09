"""
Zuerst einmal eine Klassische Herangehensweise, die natürlich deutlich aufwöndiger ist
 und nachher dann mit Konstruktor
"""
"""
class Smartphone:
    def name_device(self):
        print("Es handelt sich um ein " + self.geraet + " mit " + str(self.storage)
              + " GB und in der Farbe " + self.color + " .")

s1 = Smartphone()
s1.geraet = "Samsung Galaxy S25"
s1.storage = 512
s1.color = "Blau"

s2 = Smartphone()
s2.geraet = "Pixel 7 Pro"
s2.storage = 128
s2.color = "Midnight Black"

s1.name_device()
s2.name_device()
"""
# Und nun in eleganter

class Smartphone():
    def __init__(self, geraet, storage, color):
        self.geraet = geraet
        self.storage = storage
        self.color = color
    def name_device(self):
        print("Es handelt sich um ein " + self.geraet + " mit " + str(self.storage)
              + " GB und in der Farbe " + self.color + " .")

s1 = Smartphone("Samsung Galaxy S25 Ultra", 512, "Blau")
s2 = Smartphone("Pixel 7 Pro", 128, "Midnight Black")

s1.name_device()
s2.name_device()