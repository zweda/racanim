import random

from models.position import Position
from models.tile import Tile
from typing import List

TILE_TRANSITION_SPEED = 8

def value_at(x, y, tiles):
    if x > 3 or x < 0 or y > 3 or y < 0:
        return -1

    for tile in tiles:
        if tile.position_to.x == x and tile.position_to.y == y:
            return tile.value
    return 0

def get_tile_at(x, y, tiles):
    for tile in tiles:
        if tile.position_to.x == x and tile.position_to.y == y:
            return tile
    return None


class Player:
    def __init__(self):
        self.score = 0
        self.dead = False
        self.tiles = []
        self.empty_slots: List[Position] = []

        self.move_direction = Position(0, 0)
        self.moving_tiles = False
        self.tile_moved = False

        self.starting_positions = []

        self.reset()
        self.add_tile()
        self.add_tile()

    def reset(self):
        for i in range(4):
            for j in range(4):
                self.empty_slots.append(Position(i, j))

    def add_tile(self):
        slot = self.empty_slots.pop(random.randint(0, len(self.empty_slots) - 1))
        self.tiles.append(Tile(slot.x, slot.y))

    def contains_tile(self, x, y):
        for tile in self.tiles:
            if tile.position_to.x == x and tile.position_to.y == y:
                return True
        return False

    def value_at(self, x, y):
        if x > 3 or x < 0 or y > 3 or y < 0:
            return -1

        for tile in self.tiles:
            if tile.position_to.x == x and tile.position_to.y == y:
                return tile.value
        return 0

    def get_tile_at(self, x, y):
        for tile in self.tiles:
            if tile.position_to.x == x and tile.position_to.y == y:
                return tile
        return None

    def refresh_empty_slots(self):
        self.empty_slots.clear()
        for i in range(4):
            for j in range(4):
                if not self.contains_tile(i, j):
                    self.empty_slots.append(Position(i, j))

    def draw(self, screen, font):
        for tile in self.tiles:
            if tile.death_on_impact:
                tile.draw(screen, font)

        for tile in self.tiles:
            if not tile.death_on_impact:
                tile.draw(screen, font)

    def move(self):
        if self.moving_tiles:
            for tile in self.tiles:
                tile.move(TILE_TRANSITION_SPEED)
            if self.done_moving():
                tiles_tmp = self.tiles.copy()
                for tile in self.tiles:
                    if tile.death_on_impact:
                        tiles_tmp.remove(tile)
                self.tiles = tiles_tmp

                self.moving_tiles = False
                self.refresh_empty_slots()
                self.add_tile()
        elif len(self.empty_slots) == 0 and not self.can_move():
            self.dead = True

    def move_tiles(self):
        self.tile_moved = False
        for tile in self.tiles:
            tile.value_increased = False

        slot_order: List[Position] = []
        first_to_move = None
        vertically = False
        if self.move_direction.x == 1:
            first_to_move = Position(3, 0)
            vertically = False
        elif self.move_direction.x == -1:
            first_to_move = Position(0, 0)
            vertically = False
        elif self.move_direction.y == 1:
            first_to_move = Position(0, 3)
            vertically = True
        elif self.move_direction.y == -1:
            first_to_move = Position(0, 0)
            vertically = True

        for i in range(4):
            for j in range(4):
                tmp_slot = Position(first_to_move.x, first_to_move.y)
                if vertically:
                    tmp_slot.x += j
                else:
                    tmp_slot.y += j
                slot_order.append(tmp_slot)
            first_to_move.sub(self.move_direction)

        for slot in slot_order:
            for tile in self.tiles:
                if tile.position.x == slot.x and tile.position.y == slot.y:
                    move_to = Position(tile.position.x + self.move_direction.x, tile.position.y + self.move_direction.y)
                    while self.value_at(move_to.x, move_to.y) == 0:
                        tile.move_to(move_to)
                        move_to = Position(tile.position_to.x + self.move_direction.x,
                                           tile.position_to.y + self.move_direction.y)
                        self.tile_moved = True

                    if self.value_at(move_to.x, move_to.y) == tile.value:
                        new_tile: Tile = self.get_tile_at(move_to.x, move_to.y)
                        if not new_tile.value_increased:
                            tile.move_to(move_to)
                            tile.death_on_impact = True

                            new_tile.value_increased = True
                            tile.value_increased = True

                            new_tile.value *= 2
                            self.score += new_tile.value
                            new_tile.set_colour()
                            self.tile_moved = True

        if self.tile_moved:
            self.moving_tiles = True

    def done_moving(self):
        for tile in self.tiles:
            if tile.moving:
                return False
        return True

    def can_move_in_the_direction(self, x, y):
        tiles = self.tiles.copy()
        direction = Position(x, y)
        moved = False
        for tile in tiles:
            tile.value_increased = False

        slot_order: List[Position] = []
        first_to_move = None
        vertically = False
        if x == 1:
            first_to_move = Position(3, 0)
            vertically = False
        elif x == -1:
            first_to_move = Position(0, 0)
            vertically = False
        elif y == 1:
            first_to_move = Position(0, 3)
            vertically = True
        elif y == -1:
            first_to_move = Position(0, 0)
            vertically = True

        for i in range(4):
            for j in range(4):
                tmp_slot = Position(first_to_move.x, first_to_move.y)
                if vertically:
                    tmp_slot.x += j
                else:
                    tmp_slot.y += j
                slot_order.append(tmp_slot)
            first_to_move.sub(direction)

        for slot in slot_order:
            for tile in tiles:
                if tile.position.x == slot.x and tile.position.y == slot.y:
                    move_to = Position(tile.position.x + direction.x, tile.position.y + direction.y)
                    while value_at(move_to.x, move_to.y, tiles) == 0:
                        tile.move_to(move_to)
                        move_to = Position(tile.position_to.x + direction.x,
                                           tile.position_to.y + direction.y)
                        moved = True

                    if value_at(move_to.x, move_to.y, tiles) == tile.value:
                        moved = True

        if moved:
            return True
        return False

    def can_move(self):
        if self.can_move_in_the_direction(1, 0) or self.can_move_in_the_direction(-1, 0) or self.can_move_in_the_direction(0, 1) or self.can_move_in_the_direction(0, -1):
            return True
        return False
