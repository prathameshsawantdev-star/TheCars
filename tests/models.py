from models import Car, updateCar, CarCollection 

audi = Car(
    brand="audi",
    make="a4",
    year=2020,
    cm3=2000,
    km=50000,
    price=2000
)

lamborghini = Car(
    brand="lamborghini",
    make="huracan",
    year=2021,
    cm3=5000,
    km=10000,
    price=25000
)

cars = CarCollection(cars=[audi, lamborghini])
print(cars.model_dump())

