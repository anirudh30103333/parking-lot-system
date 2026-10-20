# Parking Lot System

A command-line parking lot management program written in Python 3 using only the standard library.

## Requirements

- Python 3.9 or newer recommended
- No external packages

## Run the program

Save the source as `parking_lot.py`. Put the commands and grid in `input.txt`, then run:

```bash
python parking_lot.py input.txt
```

## Run unit tests

```bash
python parking_lot.py --test
```

## Supported commands

- `create_parking_lot <rows> <cols>` followed by exactly `<rows>` map lines
- `park <registration_number> <colour>`
- `leave <row> <col>`
- `status`
- `registration_numbers_for_cars_with_colour <colour>`
- `slot_numbers_for_cars_with_colour <colour>`
- `slot_number_for_registration_number <registration_number>`

## Algorithm

- BFS from the entrance calculates shortest road distances.
- Only parking slots adjacent to reachable road/entrance cells are usable.
- A min-heap orders free slots by distance, row, then column.
- Dictionaries track cars by slot and registration number; colour lookups sort matching occupied slots in row/column order.

## Notes

The map is assumed valid as stated in the assignment. Invalid commands and invalid state changes are handled without terminating the program. The exact wording of invalid-input messages is not prescribed by the assignment.
