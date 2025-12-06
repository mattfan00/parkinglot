from enum import Enum
from typing import Iterable


class VehicleType(Enum):
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"
    VAN = "VAN"


class SpotType(Enum):
    COMPACT = "COMPACT"
    REGULAR = "REGULAR"


class ParkingRequirement():
    """
    Specifies the requirements a vehicle needs to park. A vehicle can have
    multiple parking requirements.
    """

    def __init__(self, spot_type: SpotType, spots_required: int):
        self.spot_type = spot_type
        self.spots_required = spots_required


class Vehicle():
    def __init__(
            self,
            plate: str,
            type: VehicleType,
            pr: list[ParkingRequirement]):
        self.plate: str = plate
        self.type: VehicleType = type
        self.parking_requirements: list[ParkingRequirement] = pr


class Motorcycle(Vehicle):
    def __init__(self, plate: str):
        parking_requirements: list[ParkingRequirement] = [
            ParkingRequirement(SpotType.COMPACT, 1),
            ParkingRequirement(SpotType.REGULAR, 1),
        ]

        Vehicle.__init__(
            self,
            plate,
            VehicleType.MOTORCYCLE,
            parking_requirements,
        )


class Car(Vehicle):
    def __init__(self, plate: str):
        parking_requirements: list[ParkingRequirement] = [
            ParkingRequirement(SpotType.REGULAR, 1),
        ]

        Vehicle.__init__(
            self,
            plate,
            VehicleType.CAR,
            parking_requirements,
        )


class Van(Vehicle):
    def __init__(self, plate: str):
        parking_requirements: list[ParkingRequirement] = [
            ParkingRequirement(SpotType.REGULAR, 2),
        ]

        Vehicle.__init__(
            self,
            plate,
            VehicleType.VAN,
            parking_requirements,
        )


def create_vehicle(plate: str, vehicle_type: VehicleType) -> Vehicle:
    """Construct the appropriate vehicle based on the type"""
    match vehicle_type:
        case VehicleType.MOTORCYCLE:
            return Motorcycle(plate)
        case VehicleType.CAR:
            return Car(plate)
        case VehicleType.VAN:
            return Van(plate)


class Spot:
    def __init__(self, row: int, col: int, type: SpotType):
        self.row: int = row
        self.col: int = col
        self.type: SpotType = type
        self.parked_vehicle: Vehicle = None

    def id(self) -> str:
        return f"{self.row}-{self.col}"

    def is_free(self) -> bool:
        return self.parked_vehicle is None

    def meets_requirement(self, req: ParkingRequirement):
        return self.is_free() and self.type == req.spot_type

    def park_vehicle(self, vehicle: Vehicle):
        self.parked_vehicle = vehicle

    def remove_vehicle(self):
        self.parked_vehicle = None

    def __str__(self) -> str:
        vehicle_str = "NONE" if self.is_free() else self.parked_vehicle.plate
        return f"{self.id()},{self.type.value},{vehicle_str}"


class VehicleParking():
    """
    Represents what spots a vehicle is parked in. This is a one-to-many
    relationship, one vehicle can be marked in many spots.
    """

    def __init__(self, vehicle: Vehicle, spots: list[Spot]):
        self.vehicle: Vehicle = vehicle
        self.spots: list[Spot] = spots


class ParkingLot:
    """
    Manages the system of vehicles parking in spots, including parking and
    removing vehicles.

    Attributes:
        lot: Matrix of spots the parking lot contains.
        vehicle_parkings: Map of vehicle ID to the spots they are parked in.
    """

    def __init__(self):
        self.lot: list[list[Spot]] = []
        self.vehicle_parkings: dict[str, VehicleParking] = {}

    def add_row(self, row: list[SpotType]):
        """Adds a new row of spots to the `lot` matrix."""

        new_row: list[Spot] = []
        r = len(self.lot)
        for c, spot_type in enumerate(row):
            new_spot = Spot(r, c, spot_type)
            new_row.append(new_spot)

        self.lot.append(new_row)

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        """
        Park the vehicle in the first spot available based on its parking
        requirements.

        Returns:
            True if the vehicle was successfully parked in a spot.
            False if a spot couldn't be found.
        """

        print(f"Parking vehicle {vehicle.plate}")

        if self._is_vehicle_parked(vehicle.plate):
            print(f"Vehicle {vehicle.plate} has been parked already")
            return False

        for req in vehicle.parking_requirements:
            free_spots = self._find_free_spots(req)

            if free_spots is not None:
                self._park_vehicle_in_spots(vehicle, free_spots)
                return True

        return False

    def _is_vehicle_parked(self, plate: str) -> bool:
        """Checks if vehicle is already parked"""

        return plate in self.vehicle_parkings

    def _find_free_spots(self, req: ParkingRequirement) -> list[Spot]:
        """
        Finds free spot(s) based on a vehicle's parking requirements.

        Returns:
            List of free spots if they were found.
            None if there are no free spots.
        """

        for row in self.lot:
            for i in range(len(row) - req.spots_required + 1):
                window: list[Spot] = row[i:i + req.spots_required]
                meets_requirements = all(
                    spot.meets_requirement(req)
                    for spot in window
                )

                if meets_requirements:
                    return window

        return None

    def _park_vehicle_in_spots(self, vehicle: Vehicle, spots: list[Spot]):
        """
        Parks the vehicle given a list of spots.

        Does not perform validations on if the vehicle can park in those spots.
        """

        for spot in spots:
            spot.park_vehicle(vehicle)

        self.vehicle_parkings[vehicle.plate] = VehicleParking(vehicle, spots)

    def remove_vehicle(self, plate: str) -> bool:
        """
        Remove a vehicle from the parking lot.

        Returns:
            True if the vehicle was removed successfully.
            False if the vehicle was not removed for whatever reason.
        """

        print(f"Removing vehicle {plate}")

        if not self._is_vehicle_parked(plate):
            return False

        removed_vehicle_parking = self.vehicle_parkings.pop(plate)

        for spot in removed_vehicle_parking.spots:
            spot.remove_vehicle()

        return True

    def _iter_spots(self) -> Iterable[Spot]:
        """Iterate through all the spots in the parking lot"""
        for row in self.lot:
            for spot in row:
                yield spot

    def num_spots(self) -> int:
        """Total number of spots in the lot."""

        return sum(1 for s in self._iter_spots())

    def num_spots_by_type(self) -> dict[SpotType, int]:
        """Number of spots for each spot type."""

        counts: dict[SpotType, int] = {}

        for spot_type in SpotType:
            counts[spot_type] = 0

        for spot in self._iter_spots():
            counts[spot.type] += 1

        return counts

    def num_remaining_spots(self) -> int:
        """Total remaining number of spots in the lot."""

        return sum([1 if s.is_free() else 0 for s in self._iter_spots()])

    def num_remaining_spots_by_type(self) -> dict[SpotType, int]:
        """Number of remaining spots for each spot type."""

        counts: dict[SpotType, int] = {}

        for spot_type in SpotType:
            counts[spot_type] = 0

        for spot in self._iter_spots():
            if spot.is_free():
                counts[spot.type] += 1

        return counts

    def is_full(self) -> bool:
        """The parking lot is full if all spots are occupied."""

        return self.num_remaining_spots() == 0

    def is_empty(self) -> bool:
        """The parking lot is empty if no spots are occupied."""

        return len(self.vehicle_parkings) == 0

    def is_full_by_type(self, spot_type: SpotType) -> bool:
        """Given the type of spot, determine if all those spots are occupied"""
        counts = self.num_remaining_spots_by_type()
        return counts[spot_type] == 0

    def num_occupied_spots_by_vehicle_type(
            self,
            vehicle_type: VehicleType) -> int:
        """Returns the number of spots occupied by the given type of vehicle"""

        count = 0

        for vehicle_parking in self.vehicle_parkings.values():
            if vehicle_parking.vehicle.type == vehicle_type:
                count += len(vehicle_parking.spots)

        return count

    def print_metrics(self):
        """Used for debugging"""
        print(f"Total number of spots: {self.num_spots()}")
        print(f"Total number of remaining spots: {self.num_remaining_spots()}")
        print("")

        spots_by_type_counts = self.num_spots_by_type()
        remaining_spots_by_type_counts = self.num_remaining_spots_by_type()

        for t in SpotType:
            print(f"{t.value} spot:")
            print(f"Number of spots: {spots_by_type_counts[t]}")
            print(f"Number of remaining spots: {remaining_spots_by_type_counts[t]}")
            print(f"Is full: {self.is_full_by_type(t)}")
            print("")

        for t in VehicleType:
            print(f"Number of spots occupied by {t.value}: {self.num_occupied_spots_by_vehicle_type(t)}")

    def __str__(self) -> str:
        """Prints a semi-readable text representation of the lot. Used for debugging"""
        s = "-----\n"
        for row in self.lot:
            s += " | ".join([str(spot) for spot in row])
            s += "\n"
        s += "-----\n"

        return s
