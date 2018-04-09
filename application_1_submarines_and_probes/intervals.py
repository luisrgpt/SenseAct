#!/usr/bin/python3

import enum
import functools
import itertools
import time

class limit(enum.Enum):
    open = 1
    closed = 2
    unbounded = 3

class interval:
    def __init__(self, min: float, max: float, left: limit, right: limit):
        self.min:   float = min
        self.max:   float = max
        self.left:  limit = left
        self.right: limit = right

    def __lt__(self, other):
        return (self.left == limit.unbounded) \
            or (self.min  <  other.min) \
            or (self.min  == other.min and self.left == limit.closed and other.left == limit.open)

    def __gt__(self, other):
        return (self.left != limit.unbounded) \
           and (  (other.min <  self.min) \
               or (other.min == self.min and other.left == limit.closed and self.left == limit.open))

    def __eq__(self, other):
        return (other      != None) \
           and (self.min   == other.min) \
           and (self.max   == other.max) \
           and (self.left  == other.left) \
           and (self.right == other.right)

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return ("(" if self.left == limit.open else "[") \
             + ("LOW" if self.left == limit.unbounded else str(self.min)) \
             + (",") \
             + ("HIGH" if self.right == limit.unbounded else str(self.max)) \
             + (")" if self.right == limit.open else "]")

    def is_empty(self) -> bool:
        return (self.left  != limit.unbounded) \
           and (self.right != limit.unbounded) \
           and (  (self.max <  self.min) \
               or (self.max == self.min and (self.right == limit.open or self.left == limit.open)))

    def empty():
        return None

    def intersection(self, other):
        # empty or separated interval conditions
        if  (self.left   != limit.unbounded) \
        and (self.right  != limit.unbounded) \
        and (other.left  != limit.unbounded) \
        and (other.right != limit.unbounded) \
        and (  (self.is_empty()) \
            or (other.is_empty()) \
            or (self.max  <  other.min) \
            or (other.max <  self.min) \
            or (self.max  == other.min and (self.right  == limit.open or other.left == limit.open)) \
            or (other.max == self.min  and (other.right == limit.open or self.left  == limit.open))):
            return interval.empty()

        if (other.left == limit.unbounded) \
        or (other.min  <  self.min) \
        or (other.min  == self.min and other.left == limit.closed and self.left == limit.open):
            min  = self.min
            left = self.left
        else:
            min  = other.min
            left = other.left

        if (other.right == limit.unbounded) \
        or (self.max    <  other.max) \
        or (self.max    == other.max and self.right == limit.open and other.right == limit.closed):
            max   = self.max
            right = self.right
        else:
            max   = other.max
            right = other.right

        return interval(min, max, left, right)

    def contains(self, other):
        and_interval = self.intersection(other)

        return and_interval == other


class interval_expression:
    def __init__(self, intervals: list):
        self.intervals: list = list(filter(lambda value: value != None, intervals))

    def __repr__(self):
        return functools.reduce(lambda acc, value: str(acc) + (" or " if acc != "" else "") + str(value), self.intervals, "")

    def is_empty(self) -> bool:
        return self.intervals == []

    def empty():
        return interval_expression([])

    def union(self, other: interval):
        # empty or only one interval condition
        if self.is_empty():
            if other.is_empty():
                return interval_expression.empty()
            else:
                return interval_expression([other])
        if other.is_empty():
            return self

        init = self.intervals[:-1]
        last: interval = self.intervals[-1]

        # no reduction condition
        if  (last.left   != limit.unbounded) \
        and (last.right  != limit.unbounded) \
        and (other.left  != limit.unbounded) \
        and (other.right != limit.unbounded) \
        and (  (last.max  < other.min) \
            or (last.max == other.min  and last.right == limit.open and other.left  == limit.open)):
            return interval_expression(self.intervals + [other])

        if (last.left == limit.unbounded) \
        or (last.min  <  other.min) \
        or (last.min  == other.min and last.left == limit.closed and other.left == limit.open):
            min  = last.min
            left = last.left
        else:
            min  = other.min
            left = other.left

        if (last.right == limit.unbounded) \
        or (other.max  <  last.max) \
        or (other.max  == last.max and other.right == limit.open and last.right == limit.closed):
            max   = last.max
            right = last.right
        else:
            max   = other.max
            right = other.right

        return interval_expression(init + [interval(min, max, left, right)])

    def reduce(self):
        self.intervals = sorted(self.intervals)

        return functools.reduce(lambda acc, value: acc.union(value), self.intervals, interval_expression.empty())

    def intersection(self, other):
        return interval_expression(sorted(list(map(lambda value: value[0].intersection(value[1]), itertools.product(self.intervals, other.intervals)))))

    def negation(self):
        not_intervals = []

        for value in self.intervals:
            if(value.left != limit.unbounded):
                not_max = value.min
                not_right = limit.open if value.left == limit.closed else limit.closed
                not_intervals.append(interval(0, not_max, limit.unbounded, not_right))

            if(value.right != limit.unbounded):
                not_min = value.max
                not_left = limit.open if value.right == limit.closed else limit.closed
                not_intervals.append(interval(not_min, 0, not_left, limit.unbounded))

        return interval_expression(sorted(not_intervals))

    def contains(self, other):
        sorted_intervals = sorted(other.intervals)
        and_intervals = self.intersection(other).intervals
        
        return all(value[0] == value[1] for value in zip(sorted_intervals, and_intervals))
        

def test():
    i1 = interval(1,2,limit.closed, limit.unbounded)
    i2 = interval(1,2,limit.closed, limit.closed)
    i3 = interval(1,2,limit.closed, limit.open)
    i4 = interval(0,2,limit.closed, limit.unbounded)
    i5 = interval(1,2,limit.open, limit.unbounded)

    o1 = interval_expression([i1, i2, None, i4])
    o2 = o1.reduce()
    o3 = o2.negation()
    o4 = o1.intersection(o3)

    print(i1.intersection(i2))
    print(i2.intersection(i3))
    print(min(i1, i4))
    print(min(i1, i5))
    print(max(i1, i5))
    print(o1)
    print(o2)
    print(o3)
    print(o4)

    while(True):
        time.sleep(1000)