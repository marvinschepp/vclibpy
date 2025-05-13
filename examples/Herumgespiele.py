'''
# Hier folgt ein bisschen Herumgespiele, damit ich Sachen wie classes und super etc. verstehe

class Shape:                                        #Hier eine Parent-Class, weil alle Shapes die EIgenschaften Color und isfilled aufweisen
    def __init__(self, color, is_filled):
        self.color = color
        self.is_filled = is_filled

    def describe(self):
        print(f"It is {self.color} and {'filled' if self.is_filled else 'not filled'}")

class Circle(Shape):
    def __init__(self, color, is_filled, radius):
        super().__init__(color, is_filled)
        self.radius = radius

    def describe(self):
        print(f"It is a circle with an area of {3.14 * self.radius * self.radius} cm^2.")
        super().describe()

class Square(Shape):
    def __init__(self, color, is_filled, width):
        super().__init__(color, is_filled)
        self.width = width

class Triangle(Shape):
    def __init__(self, color, is_filled, width, height):
        super().__init__(color, is_filled)
        self.width = width
        self.height = height


circle = Circle("Red", True, 5)
square = Square("Blue", False, 2)
triangle = Triangle("Yellow", is_filled=True, width=7, height=8)


print(f"The color of the circle is {circle.color}.")
print(circle.is_filled)
print(f"{circle.radius} cm")

print(square.color)
print(square.is_filled)
print(f"{square.width} cm")

print(triangle.color)
print(triangle.is_filled)
print(f"{triangle.width} cm")
print(f"{triangle.height} cm")


circle.describe()           #Wenn nur describe von child class aufgerufen wird, dann überschreibt die das von der parent class
'''

# Jetzt folgt was bezüglich return funktion

class Item:
    def __init__(self, name):
        self.name = name

class Box:
    def __init__(self, items=None):
        if items is None:
            self.items = []
        else:
            self.items = items

    def add_item(self, item):
        self.items.append(item)

    def get_all_items(self):
        "Gibt eine Liste aller Items aus der Box zurück."
        return self.items
# Erstellen einer Box und einiger Items
meine_leere_Box = Box()
print(meine_leere_Box.items)
item1 = Item("Buch")
item2 = Item("Stift")
meine_box = Box([item1])
meine_box.add_item(item2)

# Aufrufen der Methode get_all_items
alle_items = meine_box.get_all_items()
#print(alle_items)  # Ausgabe: [<__main__.Item object at 0x...>, <__main__.Item object at 0x...>]

# Wir können uns die Namen der Items in der Liste anschauen
for item in alle_items:
    print(meine_box.items)