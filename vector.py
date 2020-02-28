# -*- coding: Utf-8 -*

from math import sqrt, pow, acos

class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @classmethod
    def from_two_points(cls, point_1: (tuple, list), point_2: (tuple, list)):
        return cls(point_2[0] - point_1[0], point_2[1] - point_1[1])

    def norm(self):
        return sqrt(pow(self.x, 2) + pow(self.y, 2))

    def cross_product(self, vector):
        return (self.x * vector.y) - (self.y * vector.x)

    def dot_product(self, vector):
        return (self.x * vector.x) + (self.y * vector.y)

    def angle_with_vector(self, vector):
        try:
            return acos(self.dot_product(vector) / (self.norm() * vector.norm()))
        except ZeroDivisionError:
            return 0