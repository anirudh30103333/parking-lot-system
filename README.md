# Parking Lot System

A command-line parking lot management system implemented in Python 3.
The application manages parking slots on a 2D grid, allocates the nearest
available slot, tracks parked vehicles, and supports vehicle lookups.

## Features

- Creates a parking lot from a grid-based map.
- Uses Breadth-First Search (BFS) to calculate reachable parking slots.
- Allocates the nearest available parking slot.
- Resolves equal-distance ties using row and column order.
- Supports parking and leaving vehicles.
- Displays the current parking status.
- Searches vehicles by registration number and colour.
- Performs case-insensitive colour matching.
- Handles invalid commands without crashing.

## Prerequisites

- Python 3.9 or newer recommended.
- No external packages required.

## Project Structure

```text
parking_lot_system/
├── parking_lot.py
├── input.txt
└── README.md
```

## How to Run

1. Open a terminal in the project directory.
2. Run the following command:

```bash
python parking_lot.py input.txt
```

The program reads commands from `input.txt` and prints the result of each
command to the terminal.

## Running Tests

Run the built-in unit tests using:

```bash
python parking_lot.py --test
```

The tests cover parking allocation, leaving and reusing slots, colour
matching, unknown registrations, duplicate registrations, and empty
parking status.

## Supported Commands

| Command | Description |
|---|---|
| `create_parking_lot <rows> <cols>` | Creates a parking lot using the specified dimensions, followed by the map lines. |
| `park <registration_number> <colour>` | Parks a vehicle in the nearest available slot. |
| `leave <row> <col>` | Frees an occupied parking slot. |
| `status` | Displays all occupied slots and vehicle details. |
| `registration_numbers_for_cars_with_colour <colour>` | Lists registration numbers matching a colour. |
| `slot_numbers_for_cars_with_colour <colour>` | Lists slots occupied by vehicles of a given colour. |
| `slot_number_for_registration_number <registration_number>` | Finds the slot occupied by a vehicle. |

## Algorithm

- BFS calculates the shortest road distances from the entrance.
- Only parking slots adjacent to reachable road or entrance cells are usable.
- A min-heap selects the nearest available slot using distance, row, and
  column as the priority.
- Dictionaries maintain mappings between parking slots and registration
  numbers.
- A set tracks available parking slots.
- Colour lookup results are sorted by row and column.


## Notes

The parking lot map is assumed to be valid, as specified in the assignment.
The program also includes handling for invalid commands and invalid state
changes.

The exact wording of invalid-input messages is not specified by the
assignment.