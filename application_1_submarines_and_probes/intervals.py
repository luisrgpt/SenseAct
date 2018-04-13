#!/usr/bin/python3

import functools
import time

class endpoint:
    def __init__(self, value: float, is_open: bool, is_closed: bool):
        self.value: float = value
        self.is_open: bool = is_open
        self.is_closed: bool = is_closed

    def is_bounded(self):
        return self.is_open != self.is_closed

    def is_unbounded(self):
        return self.is_open == self.is_closed

    def __eq__(self, other):
        return (self.value == other.value and self.is_open == other.is_open) or (self.is_unbounded() and other.is_unbounded())

    def __ne__(self, other):
        return not self.__eq__(other)

class left_endpoint(endpoint):
    def __init__(self, value: float, is_open: bool, is_closed: bool):
        super().__init__(value, is_open, is_closed)

    def __eq__(self, other):
        return super().__eq__(other)

    def __ne__(self, other):
        return super().__ne__(other)

    def __ge__(self, other):
        return other.is_unbounded() \
            or self.is_bounded() \
            and self.value >= other.value \
            and (  self.value != other.value \
                or self.is_open \
                or other.is_closed )

    def __gt__(self, other):
        return self.__ge__(other) and self.__ne__(other)

    def __le__(self, other):
        return not self.__gt__(other)

    def __lt__(self, other):
        return not self.__ge__(other)

    def __repr__(self):
        return ("(" if self.is_open else "[") + ("LOW" if self.is_unbounded() else str(self.value))

class right_endpoint(endpoint):
    def __init__(self, value: float, is_open: bool, is_closed: bool):
        super().__init__(value, is_open, is_closed)

    def __eq__(self, other):
        return super().__eq__(other)

    def __ne__(self, other):
        return super().__ne__(other)

    def __le__(self, other):
        return other.is_unbounded() \
            or self.is_bounded() \
            and self.value <= other.value \
            and (  self.value != other.value \
                or self.is_open \
                or other.is_closed )

    def __lt__(self, other):
        return self.__le__(other) and self.__ne__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __repr__(self):
        return ("HIGH" if self.is_unbounded() else str(self.value)) + (")" if self.is_open else "]")

class interval:
    def __init__(self, left: left_endpoint, right: right_endpoint):
        self.left:  left_endpoint  = left
        self.right: right_endpoint = right

    def endpoints(self):
        return [self.left, self.right]

    def is_unbounded(self) -> bool:
        return all(value.is_unbounded() for value in self.endpoints())

    def is_bounded(self) -> bool:
        return all(value.is_bounded() for value in self.endpoints())

    def is_closed(self) -> bool:
        return all(value.is_closed for value in self.endpoints())

    def is_not_closed(self) -> bool:
        return not self.is_closed()

    def is_open(self) -> bool:
        return all(value.is_open for value in self.endpoints())

    def is_degenerated(self) -> bool:
        return self.is_bounded() and self.is_closed() and self.left.value == self.right.value

    def is_half_open(self) -> bool:
        return self.left.is_open != self.right.is_open and self.left.is_close != self.right.is_close

    def is_half_bounded(self) -> bool:
        return self.left.is_bounded() != self.right.is_bounded()

    def is_proper(self) -> bool:
        return self.is_unbounded() or self.is_half_bounded() or self.left.value < self.right.value

    def is_empty(self) -> bool:
        return not self.is_degenerated() and not self.is_proper()

    def is_not_empty(self) -> bool:
        return not self.is_empty()

    @classmethod
    def empty(cls):
        interval_left  = left_endpoint(0, True, False)
        interval_right = right_endpoint(0, True, False)
        return cls(interval_left, interval_right)

    @classmethod
    def domain(cls):
        interval_left  = left_endpoint(0, True, True)
        interval_right = right_endpoint(0, True, True)
        return cls(interval_left, interval_right)

    def __lt__(self, other):
        return self.left < other.left

    def __gt__(self, other):
        return other.right > self.right

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right or self.is_empty() and other.is_empty()

    def __le__(self, other):
        return self.left <= other.left or self.__eq__(other)

    def __ge__(self, other):
        return other.right >= self.right or self.__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        if self.is_empty():
            return "()"
        elif self.is_degenerated():
            return "{" + str(self.left.value) + "}"
        else:
            return str(self.left) + ("..") + str(self.right)

class interval_expression:
    def __init__(self, intervals: list):
        self.intervals = sorted(list(filter(lambda value: value.is_not_empty(), intervals)))

    def is_empty(self) -> bool:
        return len(self.intervals) == 0

    def is_not_empty(self) -> bool:
        return not self.is_empty()

    def __repr__(self):
        return functools.reduce(lambda acc, value: str(acc) + (" or " if acc != "" else "") + str(value), self.intervals, "") \
            if self.is_not_empty() else "()"

    @classmethod
    def empty(cls):
        return cls([])

    @classmethod
    def domain(cls):
        return cls([interval.domain()])

    def union(self, other = None):
        if other is None:
            other = self.empty()
        elif isinstance(other, interval):
            other = interval_expression([other])

        intervals = self.intervals + other.intervals

        number_of_intervals = len(intervals)
        if number_of_intervals == 0:
            return interval_expression.empty()
        elif number_of_intervals == 1:
            return interval_expression(intervals)

        head, *tail = sorted(intervals)
        acc = [head]
        for snd in tail:
            init, fst = acc[:-1], acc[-1]

            # no reduction condition
            if interval(fst.left, snd.right).is_empty() or interval(snd.left, fst.right).is_empty():
                last = [fst, snd]

            else:
                left  = min(fst.left,  snd.left)
                right = max(fst.right, snd.right)
                last = [interval(left, right)]

            acc = init + last

        return interval_expression(acc)

    def negation(self):
        if self.is_empty():
            return interval_expression.domain()

        acc = []
        for value in self.intervals:
            if value.left.is_bounded():
                not_left  = left_endpoint(None, True, True)
                not_right = right_endpoint(value.left.value, value.left.is_closed, value.left.is_open)
                acc += [interval(not_left, not_right)]

            if value.right.is_bounded():
                not_left  = left_endpoint(value.right.value, value.right.is_closed, value.right.is_open)
                not_right = right_endpoint(None, True, True)
                acc += [interval(not_left, not_right)]

        number_of_intervals = len(acc)
        if number_of_intervals == 0:
            return interval_expression.empty()
        elif number_of_intervals == 1:
            return interval_expression(acc)

        sorted_acc = sorted(acc)
        acc = []
        for fst, snd in zip(sorted_acc[:-1], sorted_acc[1:]):
            if fst.left.is_unbounded():
                if snd.right.is_unbounded():
                    not_value = interval(snd.left, fst.right)
                    if not_value.is_not_empty():
                        acc += [not_value]
                    else:
                        acc += [fst, snd]
                else:
                    acc += [fst]
            elif snd.right.is_unbounded():
                acc += [snd]
            else:
                acc += [interval(fst.left, snd.right)]

        return interval_expression(acc)

    def intersection(self, other = None):
        if other is None:
            other = self.domain()
        elif isinstance(other, interval):
            other = interval_expression([other])

        # Applying De Morgan's Laws
        not_self  = self.negation()
        not_other = other.negation()

        return not_self.union(not_other).negation()

    def contains(self, other):
        if self.is_empty() or other.is_empty():
            return False

        and_interval_expression = self.intersection(other)
        
        if and_interval_expression.is_empty():
            return False
        else:
            return all(value[0] == value[1] for value in zip(other.intervals, and_interval_expression.intervals))
        

def test():
    l0 = left_endpoint(-1, True, True)  # (LOW
    l1 = left_endpoint(0, True, True)   # (LOW
    l2 = left_endpoint(0, False, True)  # [0
    l3 = left_endpoint(0, True, False)  # (0
    l4 = left_endpoint(1, True, True)   # (LOW
    l5 = left_endpoint(1, False, True)  # [1
    l6 = left_endpoint(1, True, False)  # (1

    r0 = right_endpoint(-1, True, True) # HIGH)
    r1 = right_endpoint(1, True, True)  # HIGH)
    r2 = right_endpoint(1, False, True) # 1]
    r3 = right_endpoint(1, True, False) # 1)
    r4 = right_endpoint(0, True, True)  # HIGH)
    r5 = right_endpoint(0, False, True) # 0]
    r6 = right_endpoint(0, True, False) # 0)

    i0 = interval(l1, r1) # (LOW, HIGH)
    i1 = interval(l1, r2) # (LOW, 1]
    i2 = interval(l1, r3) # (LOW, 1)
    i3 = interval(l2, r1) # [0, HIGH)
    i4 = interval(l2, r2) # [0, 1]
    i5 = interval(l2, r3) # [0, 1)
    i6 = interval(l3, r1) # (0, HIGH)
    i7 = interval(l3, r2) # (0, 1]
    i8 = interval(l3, r3) # (0, 1)
    i9 = interval(l5, r5) # [1, 0] -> ()

    e0 = interval_expression.empty() # ()
    e1 = interval_expression.domain() # (LOW, HIGH)

    print("-----------------------")
    print("left_endpoint:")
    print("")
    print("id")
    print("l0 = " + str(l0))
    print("l1 = " + str(l1))
    print("l2 = " + str(l2))
    print("l3 = " + str(l3))
    print("l4 = " + str(l4))
    print("l5 = " + str(l5))
    print("l6 = " + str(l6))
    print("")
    print("less")
    print("l0 < l1 = " + str(l0 < l1))
    print("l1 < l2 = " + str(l1 < l2))
    print("l2 < l3 = " + str(l2 < l3))
    print("l3 < l4 = " + str(l3 < l4))
    print("l4 < l5 = " + str(l4 < l5))
    print("l5 < l6 = " + str(l5 < l6))
    print("")
    print("less equal")
    print("l0 <= l1 = " + str(l0 <= l1))
    print("l1 <= l2 = " + str(l1 <= l2))
    print("l2 <= l3 = " + str(l2 <= l3))
    print("l3 <= l4 = " + str(l3 <= l4))
    print("l4 <= l5 = " + str(l4 <= l5))
    print("l5 <= l6 = " + str(l5 <= l6))
    print("")
    print("equal")
    print("l0 == l1 = " + str(l0 == l1))
    print("l1 == l2 = " + str(l1 == l2))
    print("l2 == l3 = " + str(l2 == l3))
    print("l3 == l4 = " + str(l3 == l4))
    print("l4 == l5 = " + str(l4 == l5))
    print("l5 == l6 = " + str(l5 == l6))
    print("")
    print("greater equal")
    print("l0 >= l1 = " + str(l0 >= l1))
    print("l1 >= l2 = " + str(l1 >= l2))
    print("l2 >= l3 = " + str(l2 >= l3))
    print("l3 >= l4 = " + str(l3 >= l4))
    print("l4 >= l5 = " + str(l4 >= l5))
    print("l5 >= l6 = " + str(l5 >= l6))
    print("")
    print("greater")
    print("l0 > l1 = " + str(l0 > l1))
    print("l1 > l2 = " + str(l1 > l2))
    print("l2 > l3 = " + str(l2 > l3))
    print("l3 > l4 = " + str(l3 > l4))
    print("l4 > l5 = " + str(l4 > l5))
    print("l5 > l6 = " + str(l5 > l6))
    print("")
    print("-----------------------")
    print("right_endpoint:")
    print("")
    print("id")
    print("r0 = " + str(r0))
    print("r1 = " + str(r1))
    print("r2 = " + str(r2))
    print("r3 = " + str(r3))
    print("r4 = " + str(r4))
    print("r5 = " + str(r5))
    print("r6 = " + str(r6))
    print("")
    print("less")
    print("r0 < r1 = " + str(r0 < r1))
    print("r1 < r2 = " + str(r1 < r2))
    print("r2 < r3 = " + str(r2 < r3))
    print("r3 < r4 = " + str(r3 < r4))
    print("r4 < r5 = " + str(r4 < r5))
    print("r5 < r6 = " + str(r5 < r6))
    print("")
    print("less equal")
    print("r0 <= r1 = " + str(r0 <= r1))
    print("r1 <= r2 = " + str(r1 <= r2))
    print("r2 <= r3 = " + str(r2 <= r3))
    print("r3 <= r4 = " + str(r3 <= r4))
    print("r4 <= r5 = " + str(r4 <= r5))
    print("r5 <= r6 = " + str(r5 <= r6))
    print("")
    print("equal")
    print("r0 == r1 = " + str(r0 == r1))
    print("r1 == r2 = " + str(r1 == r2))
    print("r2 == r3 = " + str(r2 == r3))
    print("r3 == r4 = " + str(r3 == r4))
    print("r4 == r5 = " + str(r4 == r5))
    print("r5 == r6 = " + str(r5 == r6))
    print("")
    print("greater equal")
    print("r0 >= r1 = " + str(r0 >= r1))
    print("r1 >= r2 = " + str(r1 >= r2))
    print("r2 >= r3 = " + str(r2 >= r3))
    print("r3 >= r4 = " + str(r3 >= r4))
    print("r4 >= r5 = " + str(r4 >= r5))
    print("r5 >= r6 = " + str(r5 >= r6))
    print("")
    print("greater")
    print("r0 > r1 = " + str(r0 > r1))
    print("r1 > r2 = " + str(r1 > r2))
    print("r2 > r3 = " + str(r2 > r3))
    print("r3 > r4 = " + str(r3 > r4))
    print("r4 > r5 = " + str(r4 > r5))
    print("r5 > r6 = " + str(r5 > r6))
    print("")
    print("-----------------------")
    print("interval:")
    print("")
    print("id")
    print("i0 = " + str(i0))
    print("i1 = " + str(i1))
    print("i2 = " + str(i2))
    print("i3 = " + str(i3))
    print("i4 = " + str(i4))
    print("i5 = " + str(i5))
    print("i6 = " + str(i6))
    print("i7 = " + str(i7))
    print("i8 = " + str(i8))
    print("i9 = " + str(i9))
    print("-----------------------")
    print("interval_expression:")
    print("")
    print(str(e0) + " u " + str(i1) + " = " + str(e0.union(i1)))
    print(str(e0) + " / " + str(i1) + " = " + str(e0.union(i1).negation()))
    print(str(e0) + " n " + str(i1) + " = " + str(e0.intersection(i1)))
    print(str(e0) + " u " + str(i2) + " = " + str(e0.union(i2)))
    print(str(e0) + " / " + str(i2) + " = " + str(e0.union(i2).negation()))
    print(str(e0) + " n " + str(i2) + " = " + str(e0.intersection(i2)))
    print(str(i1) + " u " + str(i2) + " = " + str(e0.union(i1).union(i2)))
    print(str(i2) + " u " + str(i1) + " = " + str(e0.union(i2).union(i1)))
    print(str(i1) + " n " + str(i2) + " = " + str(e0.union(i1).intersection(i2)))
    print(str(i2) + " n " + str(i1) + " = " + str(e0.union(i2).intersection(i1)))
    print(str(e0) + " / " + str(i7) + " = " + str(e0.union(i7).negation()))
    print(str(e1) + " n " + str(i7) + " = " + str(e1.intersection(i7)))

    while(True):
        time.sleep(1000)