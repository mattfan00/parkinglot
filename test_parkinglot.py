from parkinglot import ParkingLot, SpotType, VehicleType, create_vehicle

import pytest


def test_add_row():
    pl = ParkingLot()
    pl.add_row([SpotType.COMPACT])
    pl.add_row([SpotType.COMPACT, SpotType.REGULAR])

    assert len(pl.lot) == 2
    assert len(pl.lot[0]) == 1
    assert len(pl.lot[1]) == 2
    assert pl.lot[0][0].type == SpotType.COMPACT
    assert pl.lot[1][0].type == SpotType.COMPACT
    assert pl.lot[1][1].type == SpotType.REGULAR


def test_park_vehicle_no_spots_in_lot():
    pl = ParkingLot()

    car1 = create_vehicle("car1", VehicleType.CAR)
    result = pl.park_vehicle(car1)

    assert result is False
    assert len(pl.lot) == 0
    assert len(pl.vehicle_parkings) == 0


@pytest.fixture()
def parking_lot():
    pl = ParkingLot()
    pl.add_row([SpotType.REGULAR, SpotType.REGULAR, SpotType.COMPACT])
    pl.add_row([SpotType.REGULAR])

    yield pl


def test_num_spots(parking_lot: ParkingLot):
    assert parking_lot.num_spots() == 4

    counts = parking_lot.num_spots_by_type()
    assert counts[SpotType.REGULAR] == 3
    assert counts[SpotType.COMPACT] == 1


def test_park_vehicle_first_eligible(parking_lot: ParkingLot):
    """
    If there are multiple spots that a vehicle can park, choose the first one
    that can be parked at.
    """

    car = create_vehicle("car", VehicleType.CAR)
    result = parking_lot.park_vehicle(car)

    assert result is True
    assert parking_lot.lot[0][0].is_free() is False


def test_park_vehicle_first_requirement(parking_lot: ParkingLot):
    """
    If a vehicle has multiple parking requirements, a parking spot will be
    found for its first requirement, even if its second requirement is
    technically "closer".
    """

    motorcycle = create_vehicle("motorcycle", VehicleType.MOTORCYCLE)
    result = parking_lot.park_vehicle(motorcycle)

    assert result is True
    assert parking_lot.lot[0][0].is_free() is True
    assert parking_lot.lot[0][2].is_free() is False


def test_park_vehicle_second_requirement(parking_lot: ParkingLot):
    """
    After the first requirement spots are all gone, the vehicle will
    be parked in the second requirement
    """

    motorcycle1 = create_vehicle("motorcycle1", VehicleType.MOTORCYCLE)
    motorcycle1_result = parking_lot.park_vehicle(motorcycle1)

    motorcycle2 = create_vehicle("motorcycle2", VehicleType.MOTORCYCLE)
    motorcycle2_result = parking_lot.park_vehicle(motorcycle2)

    assert motorcycle1_result is True
    assert motorcycle2_result is True
    assert parking_lot.lot[0][2].is_free() is False
    assert parking_lot.lot[0][1].is_free() is True


def test_park_vehicle_multiple_of_same(parking_lot: ParkingLot):
    """
    Multiple of the same types of cars should park in different spots.
    """

    car1 = create_vehicle("car1", VehicleType.CAR)
    car1_result = parking_lot.park_vehicle(car1)

    car2 = create_vehicle("car2", VehicleType.CAR)
    car2_result = parking_lot.park_vehicle(car2)

    assert car1_result is True
    assert car2_result is True
    assert parking_lot.lot[0][0].parked_vehicle.plate == "car1"
    assert parking_lot.lot[0][1].parked_vehicle.plate == "car2"


def test_park_vehicle_multiple_spots_success(parking_lot: ParkingLot):
    """
    Should park a vehicle that spans multiple spots
    """

    van = create_vehicle("van", VehicleType.VAN)
    result = parking_lot.park_vehicle(van)

    assert result is True
    assert parking_lot.lot[0][0].is_free() is False
    assert parking_lot.lot[0][1].is_free() is False
    assert len(parking_lot.vehicle_parkings["van"].spots) == 2


def test_park_vehicle_multiple_spots_fail(parking_lot: ParkingLot):
    """
    Should not park a vehicle that spans multiple spots into a parking lot
    that does not have the necessary contiguous spots.
    """

    car = create_vehicle("car", VehicleType.CAR)
    car_result = parking_lot.park_vehicle(car)

    van = create_vehicle("van", VehicleType.VAN)
    van_result = parking_lot.park_vehicle(van)

    assert car_result is True
    assert van_result is False


def test_park_vehicle_already_parked(parking_lot: ParkingLot):
    """
    Should not park a vehicle if it is already parked.
    """

    car1 = create_vehicle("car1", VehicleType.CAR)
    car1_result = parking_lot.park_vehicle(car1)

    car2 = create_vehicle("car1", VehicleType.CAR)
    car2_result = parking_lot.park_vehicle(car2)

    assert car1_result is True
    assert car2_result is False


def test_park_vehicle_full_lot(parking_lot: ParkingLot):
    """
    Should not park a vehicle if the lot is full.
    """

    van = create_vehicle("van", VehicleType.VAN)
    van_result = parking_lot.park_vehicle(van)

    motorcycle = create_vehicle("motorcycle", VehicleType.MOTORCYCLE)
    motorcycle_result = parking_lot.park_vehicle(motorcycle)

    car1 = create_vehicle("car1", VehicleType.CAR)
    car1_result = parking_lot.park_vehicle(car1)

    assert parking_lot.is_full() is True

    car2 = create_vehicle("car2", VehicleType.CAR)
    car2_result = parking_lot.park_vehicle(car2)

    assert van_result is True
    assert motorcycle_result is True
    assert car1_result is True
    assert car2_result is False


def test_remove_vehicle(parking_lot: ParkingLot):
    """
    Should remove vehicle if it is parked.
    """

    car = create_vehicle("car", VehicleType.CAR)
    parking_lot.park_vehicle(car)

    assert parking_lot.lot[0][0].is_free() is False

    result = parking_lot.remove_vehicle("car")

    assert result is True
    assert parking_lot.lot[0][0].is_free() is True
    assert car.plate not in parking_lot.vehicle_parkings
    assert parking_lot.is_empty() is True


def test_remove_vehicle_not_parked(parking_lot: ParkingLot):
    """
    Should not remove vehicle if it is not parked.
    """

    result = parking_lot.remove_vehicle("car")

    assert result is False
    assert parking_lot.is_empty() is True


def test_queries_by_type(parking_lot: ParkingLot):
    parking_lot.park_vehicle(create_vehicle("motorcycle", VehicleType.MOTORCYCLE))
    parking_lot.park_vehicle(create_vehicle("van", VehicleType.VAN))

    remaining_spots = parking_lot.num_remaining_spots_by_type()
    assert remaining_spots[SpotType.REGULAR] == 1
    assert remaining_spots[SpotType.COMPACT] == 0

    assert parking_lot.is_full_by_type(SpotType.REGULAR) is False
    assert parking_lot.is_full_by_type(SpotType.COMPACT) is True

    assert parking_lot.num_occupied_spots_by_vehicle_type(VehicleType.MOTORCYCLE) == 1
    assert parking_lot.num_occupied_spots_by_vehicle_type(VehicleType.CAR) == 0
    assert parking_lot.num_occupied_spots_by_vehicle_type(VehicleType.VAN) == 2
