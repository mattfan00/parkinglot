from parkinglot import ParkingLot, SpotType, VehicleType, create_vehicle

# we cant assume that the parking lot is a perfect rectangle
# it can also have blocked spaces


def main():
    parking_lot = ParkingLot()
    parking_lot.add_row([SpotType.REGULAR, SpotType.COMPACT])
    parking_lot.add_row([SpotType.COMPACT])
    parking_lot.add_row([SpotType.REGULAR, SpotType.REGULAR, SpotType.REGULAR])
    print(parking_lot)

    motorcycle1 = create_vehicle("motorcycle1", VehicleType.MOTORCYCLE)
    parking_lot.park_vehicle(motorcycle1)

    car1 = create_vehicle("car1", VehicleType.CAR)
    parking_lot.park_vehicle(car1)

    van1 = create_vehicle("van1", VehicleType.VAN)
    parking_lot.park_vehicle(van1)

    parking_lot.remove_vehicle(motorcycle1.id)

    car2 = create_vehicle("car2", VehicleType.CAR)
    parking_lot.park_vehicle(car2)
    print(parking_lot)

    parking_lot.print_metrics()


if __name__ == "__main__":
    main()
