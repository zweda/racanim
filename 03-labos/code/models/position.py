import math

class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def mult(self, d):
        self.x *= d
        self.y *= d

    def normalize(self):
        l = math.sqrt(self.x ** 2 + self.y ** 2)
        self.x /= l
        self.y /= l

    def add(self, p):
        self.x += p.x
        self.y += p.y

    def sub(self, p):
        self.x -= p.x
        self.y -= p.y


def distance(p1: Position, p2: Position):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
