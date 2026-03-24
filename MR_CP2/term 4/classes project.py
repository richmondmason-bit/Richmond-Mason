import math
class Shape:
    def area(self):
        pass

    def perimeter(self):
        pass

    def display(self):
        print(f"Shape: {self.__class__.__name__}")
        print(f"Area: {self.area():.2f}")
        print(f"Perimeter: {self.perimeter():.2f}")

    def has_larger_area(self, other):
        return self.area() > other.area()

    def has_longer_perimeter(self, other):
        return self.perimeter() > other.perimeter()
class Circle(Shape):
    def __init__(self, radius):
        if radius <= 0:
            raise ValueError("Radius must be positive.")
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def perimeter(self):
        return 2 * math.pi * self.radius

    @staticmethod
    def formula():
        return "Area = πr², Perimeter = 2πr"
class Rectangle(Shape):
    def __init__(self, length, width):
        if length <= 0 or width <= 0:
            raise ValueError("Length and width must be positive.")
        self.length = length
        self.width = width

    def area(self):
        return self.length * self.width

    def perimeter(self):
        return 2 * (self.length + self.width)

    @staticmethod
    def formula():
        return "Area = length × width, Perimeter = 2(length + width)"
class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)

    @staticmethod
    def formula():
        return "Area = side², Perimeter = 4 × side"
class Triangle(Shape):
    def __init__(self, a, b, c):
        if a <= 0 or b <= 0 or c <= 0:
            raise ValueError("All sides must be positive.")
        if a + b <= c or a + c <= b or b + c <= a:
            raise ValueError("Invalid triangle sides.")
        self.a = a
        self.b = b
        self.c = c

    def perimeter(self):
        return self.a + self.b + self.c

    def area(self):
        s = self.perimeter() / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    @staticmethod
    def formula():
        return "Area = √(s(s-a)(s-b)(s-c)), Perimeter = a + b + c"
def get_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Value must be positive.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")


def create_shape():
    print("\nChoose shape:")
    print("1. Circle")
    print("2. Rectangle")
    print("3. Square")
    print("4. Triangle")

    choice = input("Enter choice: ")

    try:
        if choice == "1":
            r = get_positive_float("Enter radius: ")
            return Circle(r)

        elif choice == "2":
            l = get_positive_float("Enter length: ")
            w = get_positive_float("Enter width: ")
            return Rectangle(l, w)

        elif choice == "3":
            s = get_positive_float("Enter side: ")
            return Square(s)

        elif choice == "4":
            a = get_positive_float("Enter side a: ")
            b = get_positive_float("Enter side b: ")
            c = get_positive_float("Enter side c: ")
            return Triangle(a, b, c)

        else:
            print("Invalid choice.")
            return None

    except ValueError as e:
        print("Error:", e)
        return None
def main():
    shapes = []
    current_index = None

    while True:
        print("\n Geometry Calculator ")
        print("1. Create Shape")
        print("2. Select Shape")
        print("3. Display Current Shape")
        print("4. Compare Two Shapes")
        print("5. Sort Shapes")
        print("6. Show Formula")
        print("7. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            shape = create_shape()
            if shape:
                shapes.append(shape)
                print("Shape created successfully.")

        elif choice == "2":
            if not shapes:
                print("No shapes available.")
                continue

            for i, s in enumerate(shapes):
                print(f"{i}: {s.__class__.__name__}")

            try:
                idx = int(input("Select index: "))
                if 0 <= idx < len(shapes):
                    current_index = idx
                    print("Shape selected.")
                else:
                    print("Invalid index.")
            except ValueError:
                print("Invalid input.")

        elif choice == "3":
            if current_index is None:
                print("No shape selected.")
            else:
                shapes[current_index].display()

        elif choice == "4":
            if len(shapes) < 2:
                print("Need at least 2 shapes.")
                continue

            try:
                identity1 = int(input("First shape index: "))
                identity2 = int(input("Second shape index: "))

                shape1 = shapes[identity1]
                shape2 = shapes[identity2]

                print("Larger Area:", shape1.has_larger_area(shape2))
                print("Longer Perimeter:", shape1.has_longer_perimeter(shape2))

            except (ValueError, IndexError):
                print("Invalid indices.")

        elif choice == "5":
            print("Sort by:")
            print("1. Area")
            print("2. Perimeter")
            option = input("Choice: ")

            if option == "1":
                shapes.sort(key=lambda s: s.area())
            elif option == "2":
                shapes.sort(key=lambda s: s.perimeter())
            else:
                print("Invalid option.")
                continue

            print("Shapes sorted.")

        elif choice == "6":
            if current_index is None:
                print("No shape selected.")
            else:
                print(shapes[current_index].formula())

        elif choice == "7":
            print("Smell ya later")
            break

        else:
            print("Nope not an option ")

main()