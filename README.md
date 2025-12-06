# Matt's Parking Lot

## How to run
1. Ensure `uv` is installed: https://docs.astral.sh/uv/getting-started/installation/
1. Run the tests:
```
uv run pytest --verbose
```
1. For a more interactive experience, you can modify `main.py` and create your own lot and vehicles (with more time I would have loved to make this a CLI!):
```
uv run main.py
```

## Structure:
```
parkinglot.py - main logic for `ParkingLot`, `Vehicle`, `Spot`, etc.
main.py - script for playing around with the logic
test_parkinglot.py - all tests
```

## Thought process

A lot of my thought process revolved around parking a vehicle so my approaches mostly address that.

### Initial approaches

My first approach for this design was to code explicitly for the REGULAR/COMPACT spot types and MOTORCYCLE/CAR/VAN vehicle types. This means `ParkingLot` will have some hardcoded logic to make sure if a MOTORCYCLE is passed then check both REGULAR and COMPACT, and if a VAN is passed then check for 2 contiguous REGULAR spots. However, this design is not extensible and it will be a pain to add new spot types and vehicle types.

My next approach was to assign each spot type a maximum size and each vehicle a size. So for example, the maximum size of COMPACT and REGULAR can be 1 and 2 respectively. If the size of a MOTORCYCLE is 1, then it can fit in both spots. If the size of a CAR is 2, it can only fit in REGULAR. If the size of a VAN is 4, then `ParkingLot` can loop through as many spots as it needs until all 4 units of the VAN are in a spot. This is really flexible, a VAN can fit in 2 COMPACTs and 1 REGULAR. This also means 2 MOTORCYCLEs can fit in 1 REGULAR. This design was a lot of fun to think up, but it felt like it would be more appropriate if the problem was more focused on cramming as many objects into a space as possible. Additionally, size is not the only factor for if a vehicle can park in a spot. You can also have "business" reasons, like handicap spots are reserved for specific cars.

### Final design

So my final approach tries to combine the more rigid, rule-like nature of real parking lots with some room for flexibility. Each vehicle comes with a list of `ParkingRequirement` which details what spot type it can park in and how many of those spots it requires. `ParkingLot` will not have any logic about specific vehicles, it only knows how to find an open spot(s) given a list of `ParkingRequirement`. So let's say we have a new RV vehicle and a new LARGE spot where an RV can fit in either 1 LARGE or 3 REGULARs. The new design will easily accommodate this with a `ParkingRequirement` for each. The only situation that this new design cannot handle is 2 MOTORCYCLEs fitting in 1 REGULAR, but in the context of a parking lot that doesn't make sense so I made the assumption that a spot can only have one vehicle in it.

An additional feature is prioritizing a `ParkingRequirement`. The logic in `ParkingLot` will first go through all the spots trying to meet the first `ParkingRequirement` in the list, essentially prioritizing it. If no spots meet it, then `ParkingLot` will start finding spots for the second `ParkingRequirement`. So if a COMPACT spot is the first requirement for a MOTORCYCLE, it will try to park there instead of a REGULAR spot even if it's "closer" (take a look at test case `test_park_vehicle_first_requirement`). This whole idea of prioritization can be expanded on even more, but this is a primitive implementation. 

Finally, all of this was implemented as an in-memory based solution. I structured the methods in `ParkingLot` so that if it needed to have a DB, the process wouldn't be too bad. Methods like `_is_vehicle_parked`, `_find_free_spots`, and `_park_vehicle_in_spots` can be implemented as SQL queries, so you could just interface `ParkingLot` and have multiple implementations.
