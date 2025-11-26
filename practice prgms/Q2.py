from abc import ABC, abstractmethod

class Person(ABC):
    #Abstract base class representing a person.
    @abstractmethod
    def get_gender(self):
        #Return/print the gender of the person.
        pass

class Male(Person):
    def get_gender(self):
        return "Male"

class Female(Person):
    def get_gender(self):
        return "Female"

if __name__ == "__main__":
    m = Male()
    f = Female()
    print(m.get_gender())   
    print(f.get_gender())   

  
    try:
        p = Person()
    except TypeError as e:
        print("Cannot instantiate Person():", e)
