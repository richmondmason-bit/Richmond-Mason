class Vehicle:
    def __init__(self,model,brand):
        self.brand = brand  
        self.model = model

    def move(self):
        print("Move!")

class Car(Vehicle):
    pass

car = Car("Ford","Mustang")

print(car.brand)
print(car.brand)