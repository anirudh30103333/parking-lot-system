#!/usr/bin/env python3
"""
Parking Lot System

Run:
    python parking_lot.py input.txt

Run unit tests:
    python parking_lot.py --test

Only Python's standard library is required.
"""

from __future__ import annotations

import heapq
import sys
import unittest
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


Slot = Tuple[int, int]  # Internal coordinates are zero-based.


@dataclass
class Car:
    registration: str
    colour: str


class ParkingLot:
    def __init__(self, rows: int, cols: int, grid: List[str]):
        if rows <= 0 or cols <= 0:
            raise ValueError("Rows and columns must be positive")
        if len(grid) != rows or any(len(line) != cols for line in grid):
            raise ValueError("Grid dimensions do not match rows and columns")
        if any(ch not in "E.#P" for line in grid for ch in line):
            raise ValueError("Grid contains an invalid symbol")
        if sum(line.count("E") for line in grid) != 1:
            raise ValueError("Grid must contain exactly one entrance")

        self.rows = rows
        self.cols = cols
        self.grid = grid
        self.cars_by_slot: Dict[Slot, Car] = {}
        self.slot_by_registration: Dict[str, Slot] = {}

        self._slots_sorted: List[Slot] = []
        self._slot_distance: Dict[Slot, int] = {}
        self._available_heap: List[Tuple[int, int, int]] = []
        self._available_set: set[Slot] = set()

        self._calculate_reachable_slots()

    @staticmethod
    def _neighbours(r: int, c: int):
        # The order does not determine ties; ties are explicitly sorted.
        yield r - 1, c
        yield r + 1, c
        yield r, c - 1
        yield r, c + 1

    def _calculate_reachable_slots(self) -> None:
        entrance = None
        for r, line in enumerate(self.grid):
            c = line.find("E")
            if c != -1:
                entrance = (r, c)
                break

        assert entrance is not None
        distances = [[-1] * self.cols for _ in range(self.rows)]
        q = deque([entrance])
        distances[entrance[0]][entrance[1]] = 0

        # BFS traverses roads and the entrance, but never walls or parking cells.
        while q:
            r, c = q.popleft()
            for nr, nc in self._neighbours(r, c):
                if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                    continue
                if distances[nr][nc] != -1:
                    continue
                if self.grid[nr][nc] not in ".E":
                    continue
                distances[nr][nc] = distances[r][c] + 1
                q.append((nr, nc))

        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != "P":
                    continue
                adjacent_road_distances = [
                    distances[nr][nc]
                    for nr, nc in self._neighbours(r, c)
                    if 0 <= nr < self.rows
                    and 0 <= nc < self.cols
                    and distances[nr][nc] >= 0
                ]
                if adjacent_road_distances:
                    slot = (r, c)
                    # A slot directly adjacent to more than one reachable road
                    # uses the shortest way to reach that slot.
                    distance = min(adjacent_road_distances) + 1
                    self._slot_distance[slot] = distance
                    self._slots_sorted.append(slot)

        self._slots_sorted.sort(key=lambda s: (self._slot_distance[s], s[0], s[1]))
        self._available_set = set(self._slots_sorted)
        self._available_heap = [
            (self._slot_distance[r_c], r_c[0], r_c[1])
            for r_c in self._slots_sorted
        ]
        heapq.heapify(self._available_heap)

    @property
    def usable_slots(self) -> int:
        return len(self._slots_sorted)

    def park(self, registration: str, colour: str) -> str:
        registration = registration.strip()
        colour = colour.strip()
        if not registration or not colour:
            return "Invalid input"
        if registration in self.slot_by_registration:
            return "Invalid input: registration number is already parked"
        if not self._available_set:
            return "Sorry, parking lot is full"

        # Lazy deletion: entries for occupied slots are skipped.
        while self._available_heap:
            distance, r, c = heapq.heappop(self._available_heap)
            slot = (r, c)
            if slot in self._available_set:
                self._available_set.remove(slot)
                self.cars_by_slot[slot] = Car(registration, colour)
                self.slot_by_registration[registration] = slot
                return f"Allocated slot: ({r + 1}, {c + 1})"

        # Defensive fallback; the set and heap should remain consistent.
        return "Sorry, parking lot is full"

    def leave(self, row: int, col: int) -> str:
        # Public command coordinates are one-based.
        if not (1 <= row <= self.rows and 1 <= col <= self.cols):
            return "Invalid input"
        slot = (row - 1, col - 1)
        if slot not in self.cars_by_slot:
            return "Invalid input: slot is not occupied"

        car = self.cars_by_slot.pop(slot)
        self.slot_by_registration.pop(car.registration, None)
        self._available_set.add(slot)
        heapq.heappush(
            self._available_heap,
            (self._slot_distance[slot], slot[0], slot[1]),
        )
        return f"Slot ({row}, {col}) is free"

    def status(self) -> str:
        if not self.cars_by_slot:
            return "Parking lot is empty"

        lines = [
            f"{'Slot':<10}{'Registration No':<19}Colour"
        ]
        for (r, c), car in sorted(self.cars_by_slot.items()):
            lines.append(
                f"({r + 1}, {c + 1})".ljust(10)
                + car.registration.ljust(19)
                + car.colour
            )
        return "\n".join(lines)

    def registration_numbers_for_cars_with_colour(self, colour: str) -> str:
        target = colour.casefold()
        matches = [
            (slot, car.registration)
            for slot, car in self.cars_by_slot.items()
            if car.colour.casefold() == target
        ]
        matches.sort(key=lambda item: item[0])
        if not matches:
            return "Not found"
        return ", ".join(registration for _, registration in matches)

    def slot_numbers_for_cars_with_colour(self, colour: str) -> str:
        target = colour.casefold()
        slots = sorted(
            slot for slot, car in self.cars_by_slot.items()
            if car.colour.casefold() == target
        )
        if not slots:
            return "Not found"
        return ", ".join(f"({r + 1}, {c + 1})" for r, c in slots)

    def slot_number_for_registration_number(self, registration: str) -> str:
        slot = self.slot_by_registration.get(registration)
        if slot is None:
            return "Not found"
        return f"({slot[0] + 1}, {slot[1] + 1})"


def process_commands(lines: List[str]) -> List[str]:
    """Process commands in order and return one output per command."""
    outputs: List[str] = []
    lot: Optional[ParkingLot] = None
    i = 0

    while i < len(lines):
        raw = lines[i].strip()
        i += 1
        if not raw or raw.startswith("# "):
            continue

        parts = raw.split()
        command = parts[0]

        if command == "create_parking_lot":
            if len(parts) != 3:
                outputs.append("Invalid input")
                continue
            try:
                rows, cols = int(parts[1]), int(parts[2])
                if rows <= 0 or cols <= 0:
                    raise ValueError
                if i + rows > len(lines):
                    outputs.append("Invalid input")
                    break
                grid = [lines[i + j].rstrip("\r\n") for j in range(rows)]
                i += rows
                lot = ParkingLot(rows, cols, grid)
                outputs.append(
                    f"Created a parking lot with {lot.usable_slots} usable slots"
                )
            except (ValueError, IndexError):
                outputs.append("Invalid input")
            continue

        if lot is None:
            outputs.append("Invalid input: parking lot has not been created")
            continue

        try:
            if command == "park":
                if len(parts) != 3:
                    outputs.append("Invalid input")
                else:
                    outputs.append(lot.park(parts[1], parts[2]))

            elif command == "leave":
                if len(parts) != 3:
                    outputs.append("Invalid input")
                else:
                    row, col = int(parts[1]), int(parts[2])
                    outputs.append(lot.leave(row, col))

            elif command == "status":
                if len(parts) != 1:
                    outputs.append("Invalid input")
                else:
                    outputs.append(lot.status())

            elif command == "registration_numbers_for_cars_with_colour":
                if len(parts) != 2:
                    outputs.append("Invalid input")
                else:
                    outputs.append(
                        lot.registration_numbers_for_cars_with_colour(parts[1])
                    )

            elif command == "slot_numbers_for_cars_with_colour":
                if len(parts) != 2:
                    outputs.append("Invalid input")
                else:
                    outputs.append(lot.slot_numbers_for_cars_with_colour(parts[1]))

            elif command == "slot_number_for_registration_number":
                if len(parts) != 2:
                    outputs.append("Invalid input")
                else:
                    outputs.append(
                        lot.slot_number_for_registration_number(parts[1])
                    )
            else:
                outputs.append("Invalid input: unknown command")
        except (ValueError, IndexError):
            outputs.append("Invalid input")

    return outputs


class ParkingLotTests(unittest.TestCase):
    def make_lot(self):
        grid = [
            "E..P",
            ".#P.",
            "...P",
        ]
        return ParkingLot(3, 4, grid)

    def test_reachable_slots_and_nearest_allocation(self):
        lot = self.make_lot()
        self.assertEqual(lot.usable_slots, 3)
        self.assertEqual(lot.park("CAR-1", "White"), "Allocated slot: (1, 4)")
        self.assertEqual(lot.park("CAR-2", "Black"), "Allocated slot: (2, 3)")

    def test_leave_and_reuse(self):
        lot = self.make_lot()
        lot.park("CAR-1", "White")
        self.assertEqual(lot.leave(1, 4), "Slot (1, 4) is free")
        self.assertEqual(lot.park("CAR-2", "Blue"), "Allocated slot: (1, 4)")

    def test_colour_case_insensitive_and_sorted(self):
        lot = self.make_lot()
        lot.park("CAR-1", "White")
        lot.park("CAR-2", "white")
        self.assertEqual(
            lot.registration_numbers_for_cars_with_colour("WHITE"),
            "CAR-1, CAR-2",
        )
        self.assertEqual(
            lot.slot_numbers_for_cars_with_colour("wHiTe"),
            "(1, 4), (2, 3)",
        )

    def test_unknown_registration(self):
        lot = self.make_lot()
        self.assertEqual(
            lot.slot_number_for_registration_number("NOPE"), "Not found"
        )

    def test_duplicate_registration_rejected(self):
        lot = self.make_lot()
        lot.park("CAR-1", "White")
        self.assertIn("already parked", lot.park("CAR-1", "Black"))

    def test_empty_status(self):
        lot = self.make_lot()
        self.assertEqual(lot.status(), "Parking lot is empty")


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--test":
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ParkingLotTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1

    if len(sys.argv) != 2:
        print("Usage: python parking_lot.py input.txt")
        print("   or: python parking_lot.py --test")
        return 2

    try:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as exc:
        print(f"Could not read input file: {exc}", file=sys.stderr)
        return 1

    for output in process_commands(lines):
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
