#class Animal:
#    def __init__(self,name,species,age):
#        self.name = name.capitalize()
#        self.species = species.capitalize()
#        self.age = age
#    def __str__(self):
#       return f"Name = {self.name}\n Species = {self.species}\n Age = {self.age}" 
#    def birthday(self):
#        self.age += 1
#dog = Animal("doug","dog",4)
#bunny = Animal("Judy","rabbit",20)
#print(dog)
#print(bunny)
#dog.birthday()
#print(dog)

class ClassPeriod:
    def __init__(self,subject,teacher = "Ms.Larose ",room = None):
        self.subject = subject.capitalize()
        self.teacher = teacher
        self.room = room

def __str__(self):
    return f"Subject:{self.subject}\n Teacher:{self.teacher} Room:{self.room}"

first = ClassPeriod("Computer Programming 2","Ms.Larose",room=200)
second = ClassPeriod("Biology","Ms.Krueger",room=210)
third = ClassPeriod("Geography","Mr.Macinanti",room=220)
fourth = ClassPeriod("Lunch"," is up your butt",room ="Cafeteria")

print(first)
print(second)
print(third)
print(fourth)