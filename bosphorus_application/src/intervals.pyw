# coding=utf-8
from dataclasses import dataclass
from math import inf

@dataclass
class Uncertainty:
    center: float
    absolute: float
    relative: float
    def __add__(self, other=None):
        if other is None:
            return self

        result_center = self.center + other.center
        result_absolute = self.absolute + other.absolute
        result = AbsoluteUncertainty(result_center, result_absolute)

        return result
    def __sub__(self, other=None):
        if other is None:
            return self

        result_center = self.center - other.center
        result_absolute = self.absolute + other.absolute
        result = AbsoluteUncertainty(result_center, result_absolute)

        return result
    def __mul__(self, other=None):
        if other is None:
            return self

        result_center = self.center * other.center
        result_relative = self.relative + other.relative
        result = RelativeUncertainty(result_center, result_relative)

        return result
    def __truediv__(self, other=None):
        if other is None:
            return self

        result_center = self.center / other.center
        result_relative = self.relative + other.relative
        result = RelativeUncertainty(result_center, result_relative)

        return result
class AbsoluteUncertainty(Uncertainty):
    def __init__(self, center: float, absolute: float):
        relative = (absolute / center * 100) if center != 0 else 0
        super().__init__(float(center), float(absolute), float(relative))
    def __repr__(self):
        return str(self.center) + ' +- ' + str(self.absolute)
class RelativeUncertainty(Uncertainty):
    def __init__(self, center: float, relative: float):
        absolute = relative * center / 100
        super().__init__(float(center), float(absolute), float(relative))
    def __repr__(self):
        return str(self.center) + ' +- ' + str(self.relative) + '%'

class Interval:
    def __init__(self, intervals: list):
        self.intervals = intervals
    def __iter__(self):
        return self.intervals.__iter__()
    def __getitem__(self, item):
        return self.intervals.__getitem__(item)
    def __setitem__(self, key, value):
        return self.intervals.__setitem__(key, value)
    def __delitem__(self, key):
        return self.intervals.__delitem__(key)
    def __len__(self):
        return self.intervals.__len__()
    def __eq__(self, other):
        return self.intervals.__eq__(other.intervals)
    def __ne__(self, other):
        return self.intervals.__ne__(other.intervals)

    def range(self):
        if -inf in self[0][0] or inf in self[-1][1]:
            return

        for x in self:
            lower, max_upper = x
            upper = (lower[0] + lower[1], not lower[1])
            while upper <= max_upper:
                yield Interval([(lower, upper)])
                if upper < max_upper:
                    upper = (upper[0] + upper[1], not upper[1])
                else:
                    lower = (lower[0] + lower[1], not lower[1])
                    upper = (lower[0] + lower[1], not lower[1])
    def size(self):
        return int(sum(x[1][0] - x[0][0] for x in self))

    def __contains__(self, other):
        return (
            any(
                ((x[0][1] and x[0][0] < other) or x[0][0] <= other)
                and
                ((x[1][1] and other <= x[1][0]) or other < x[1][0])
                for x in self
            )
            if isinstance(other, int)
            else
            all(
                any(
                    y[0] <= x[0] and x[1] <= y[1]
                    for y in self
                ) for x in other
            )
        )

    def __repr__(self):
        return ' or '.join(
            [
                (
                    ('{' + str(x[0][0]) + '}')
                    if not x[0][1] and x[1][1] and x[0][0] == x[1][0]
                    else
                    (
                        ('(' if x[0][1] or -inf in x[0] else '[') +
                        ('LOW' if -inf in x[0] else str(float(x[0][0]))) +
                        '..' +
                        ('HIGH' if inf in x[1] else str(float(x[1][0]))) +
                        (']' if x[1][1] else ')')
                    )
                )
                for x in self.intervals
            ]
        ) if len(self) > 0 else '()'

    def invert(self):
        if len(self) is 0:
            self.intervals = [
                ((-inf, None), (inf, None))
            ]
        elif self[0][0][0] != -inf:
            lower, upper = self[0]
            self[0] = (-inf, None), lower
            for x in range(1, len(self)):
                prev = upper
                lower, upper = self[x]
                self[x] = prev, lower
            if inf not in upper:
                self.intervals += [
                    (upper, (inf, None))
                ]
        else:
            lower, _ = self[-1]
            for x in range(len(self) - 2, -1, -1):
                post = lower
                lower, upper = self[x]
                self[x] = upper, post
            _, upper = self[-1]
            if inf in upper:
                del self[-1]
            else:
                self[-1] = upper, (inf, None)
    def __ior__(self, other):
        self.intervals += other[:]

        self.intervals.sort()
        n_self = len(self) - 1
        x = 0
        while x < n_self:
            y = x + 1
            lower = (self[x] if self[y][1] <= self[x][1] else self[y])[0]
            upper = (self[x] if self[x][0] <= self[y][0] else self[y])[1]

            if lower <= upper:
                self[x] = (min(self[x][0], self[y][0]), max(self[x][1], self[y][1]))
                del[self[y]]
                n_self -= 1
            x += 1
        return self
    def __iand__(self, other):
        intervals = self.intervals
        self.intervals = []
        for x in intervals:
            for y in other:
                lower = (x if y[1] <= x[1] else y)[0]
                upper = (x if x[0] <= y[0] else y)[1]

                if lower < upper:
                    self.intervals += [
                        (max(x[0], y[0]), min(x[1], y[1]))
                    ]

        self.intervals.sort()
        n_self = len(self) - 1
        x = 0
        while x < n_self:
            y = x + 1
            lower = (self[x] if self[y][1] <= self[x][1] else self[y])[0]
            upper = (self[x] if self[x][0] <= self[y][0] else self[y])[1]

            if lower <= upper:
                self[x] = (min(self[x][0], self[y][0]), max(self[x][1], self[y][1]))
                del[self[y]]
                n_self -= 1
            x += 1
        return self
    def __iadd__(self, other: Uncertainty):
        for x in range(len(self)):
            self_absolute = (self[x][1][0] - self[x][0][0]) / 2
            self_center = self[x][0][0] + self_absolute
            self_uncertainty = AbsoluteUncertainty(self_center, self_absolute)

            uncertainty = self_uncertainty + other
            center = uncertainty.center
            absolute = uncertainty.absolute

            self[x] = ((center - absolute, self[x][0][1]), (center + absolute, self[x][1][1]))

        #self.sort()
        return self
    def __isub__(self, other: Uncertainty):
        for x in range(len(self)):
            self_absolute = (self[x][1][0] - self[x][0][0]) / 2
            self_center = self[x][0][0] + self_absolute
            self_uncertainty = AbsoluteUncertainty(self_center, self_absolute)

            uncertainty = self_uncertainty - other
            center = uncertainty.center
            absolute = uncertainty.absolute

            self[x] = ((center - absolute, self[x][0][1]), (center + absolute, self[x][1][1]))

        #self.sort()
        return self
    def __invert__(self):
        result = Interval(self[:])
        result.invert()
        return result
    def __add__(self, other: Uncertainty):
        result = Interval(self[:])
        result += other
        return result
    def __sub__(self, other: Uncertainty):
        result = Interval(self[:])
        result -= other
        return result
    def __and__(self, other):
        result = Interval(self[:])
        result &= other
        return result
    def __or__(self, other):
        result = Interval(self[:])
        result |= other
        return result

def test():
    for x in Interval([
        ((0, False), (10, True))
    ]).range():
        print(x)

    l0 = (-inf, None)  # (LOW
    l1 = (-inf, None)  # (LOW
    l2 = (0, False)  # [0
    l3 = (0, True)  # (0
    l4 = (-inf, None)  # (LOW
    l5 = (1, False)  # [1
    l6 = (1, True)  # (1

    r0 = (inf, None)  # HIGH)
    r1 = (inf, None)  # HIGH)
    r2 = (1, True)  # 1]
    r3 = (1, False)  # 1)
    r4 = (inf, None)  # HIGH)
    r5 = (0, True)  # 0]
    r6 = (0, False)  # 0)
    r7 = (5, True)  # 5]

    i0 = Interval([(l1, r1)])  # (LOW..HIGH)
    i1 = Interval([(l1, r2)])  # (LOW..1]
    i2 = Interval([(l1, r3)])  # (LOW..1)
    i3 = Interval([(l2, r1)])  # [0..HIGH)
    i4 = Interval([(l2, r2)])  # [0..1]
    i5 = Interval([(l2, r3)])  # [0..1)
    i6 = Interval([(l3, r1)])  # (0..HIGH)
    i7 = Interval([(l3, r2)])  # (0..1]
    i8 = Interval([(l3, r3)])  # (0..1)
    i9 = Interval([])  # [1..0] -> ()
    i10 = Interval([(l1, r6)])  # (LOW..0)
    i11 = Interval([(l6, r1)])  # (1..HIGH)
    i12 = Interval([(l2, r7)])  # [0..5]

    e0 = Interval([])  # ()
    e1 = Interval([((-inf, None),(inf, None))])  # (LOW..HIGH)

    print('-----------------------')
    print('lower_endpoint:')
    print('')
    print('id')
    print('l0 = ' + str(l0))
    print('l1 = ' + str(l1))
    print('l2 = ' + str(l2))
    print('l3 = ' + str(l3))
    print('l4 = ' + str(l4))
    print('l5 = ' + str(l5))
    print('l6 = ' + str(l6))
    print('')
    print('less')
    print('l0 < l1 = ' + str(l0 < l1))
    print('l1 < l2 = ' + str(l1 < l2))
    print('l2 < l3 = ' + str(l2 < l3))
    print('l3 < l4 = ' + str(l3 < l4))
    print('l4 < l5 = ' + str(l4 < l5))
    print('l5 < l6 = ' + str(l5 < l6))
    print('')
    print('less equal')
    print('l0 <= l1 = ' + str(l0 <= l1))
    print('l1 <= l2 = ' + str(l1 <= l2))
    print('l2 <= l3 = ' + str(l2 <= l3))
    print('l3 <= l4 = ' + str(l3 <= l4))
    print('l4 <= l5 = ' + str(l4 <= l5))
    print('l5 <= l6 = ' + str(l5 <= l6))
    print('')
    print('equal')
    print('l0 == l1 = ' + str(l0 == l1))
    print('l1 == l2 = ' + str(l1 == l2))
    print('l2 == l3 = ' + str(l2 == l3))
    print('l3 == l4 = ' + str(l3 == l4))
    print('l4 == l5 = ' + str(l4 == l5))
    print('l5 == l6 = ' + str(l5 == l6))
    print('')
    print('greater equal')
    print('l0 >= l1 = ' + str(l0 >= l1))
    print('l1 >= l2 = ' + str(l1 >= l2))
    print('l2 >= l3 = ' + str(l2 >= l3))
    print('l3 >= l4 = ' + str(l3 >= l4))
    print('l4 >= l5 = ' + str(l4 >= l5))
    print('l5 >= l6 = ' + str(l5 >= l6))
    print('')
    print('greater')
    print('l0 > l1 = ' + str(l0 > l1))
    print('l1 > l2 = ' + str(l1 > l2))
    print('l2 > l3 = ' + str(l2 > l3))
    print('l3 > l4 = ' + str(l3 > l4))
    print('l4 > l5 = ' + str(l4 > l5))
    print('l5 > l6 = ' + str(l5 > l6))
    print('')
    print('-----------------------')
    print('upper_endpoint:')
    print('')
    print('id')
    print('r0 = ' + str(r0))
    print('r1 = ' + str(r1))
    print('r2 = ' + str(r2))
    print('r3 = ' + str(r3))
    print('r4 = ' + str(r4))
    print('r5 = ' + str(r5))
    print('r6 = ' + str(r6))
    print('')
    print('less')
    print('r0 < r1 = ' + str(r0 < r1))
    print('r1 < r2 = ' + str(r1 < r2))
    print('r2 < r3 = ' + str(r2 < r3))
    print('r3 < r4 = ' + str(r3 < r4))
    print('r4 < r5 = ' + str(r4 < r5))
    print('r5 < r6 = ' + str(r5 < r6))
    print('')
    print('less equal')
    print('r0 <= r1 = ' + str(r0 <= r1))
    print('r1 <= r2 = ' + str(r1 <= r2))
    print('r2 <= r3 = ' + str(r2 <= r3))
    print('r3 <= r4 = ' + str(r3 <= r4))
    print('r4 <= r5 = ' + str(r4 <= r5))
    print('r5 <= r6 = ' + str(r5 <= r6))
    print('')
    print('equal')
    print('r0 == r1 = ' + str(r0 == r1))
    print('r1 == r2 = ' + str(r1 == r2))
    print('r2 == r3 = ' + str(r2 == r3))
    print('r3 == r4 = ' + str(r3 == r4))
    print('r4 == r5 = ' + str(r4 == r5))
    print('r5 == r6 = ' + str(r5 == r6))
    print('')
    print('greater equal')
    print('r0 >= r1 = ' + str(r0 >= r1))
    print('r1 >= r2 = ' + str(r1 >= r2))
    print('r2 >= r3 = ' + str(r2 >= r3))
    print('r3 >= r4 = ' + str(r3 >= r4))
    print('r4 >= r5 = ' + str(r4 >= r5))
    print('r5 >= r6 = ' + str(r5 >= r6))
    print('')
    print('greater')
    print('r0 > r1 = ' + str(r0 > r1))
    print('r1 > r2 = ' + str(r1 > r2))
    print('r2 > r3 = ' + str(r2 > r3))
    print('r3 > r4 = ' + str(r3 > r4))
    print('r4 > r5 = ' + str(r4 > r5))
    print('r5 > r6 = ' + str(r5 > r6))
    print('')
    print('-----------------------')
    print('interval:')
    print('')
    print('id')
    print('i0 = ' + str(i0))
    print('i1 = ' + str(i1))
    print('i2 = ' + str(i2))
    print('i3 = ' + str(i3))
    print('i4 = ' + str(i4))
    print('i5 = ' + str(i5))
    print('i6 = ' + str(i6))
    print('i7 = ' + str(i7))
    print('i8 = ' + str(i8))
    print('i9 = ' + str(i9))
    print('-----------------------')
    print('')
    print(str(e0) + ' or ' + str(i1) + ' = ' + str(e0 | i1))
    print('not ' + str(i1) + ' = ' + str(~i1))
    print(str(e0) + ' and ' + str(i1) + ' = ' + str(e0 & i1))
    print(str(e0) + ' or ' + str(i2) + ' = ' + str(e0 | i2))
    print('not ' + str(i2) + ' = ' + str(~i2))
    print(str(e0) + ' and ' + str(i2) + ' = ' + str(e0 & i2))
    print(str(i1) + ' or ' + str(i2) + ' = ' + str(i1 | i2))
    print(str(i2) + ' or ' + str(i1) + ' = ' + str(i2 | i1))
    print(str(i1) + ' and ' + str(i2) + ' = ' + str(i1 & i2))
    print(str(i2) + ' and ' + str(i1) + ' = ' + str(i2 & i1))
    print('not ' + str(i7) + ' = ' + str(~i7))
    print(str(e1) + ' and ' + str(i7) + ' = ' + str(e1 & i7))
    print(str(e1) + ' in ' + str(i7) + ' = ' + str(e1 in i7))
    print(str(i7) + ' in ' + str(e1) + ' = ' + str(i7 in e1))
    print(str(i7 | i11))
    print(str(e0 | i10 | i11) + ' and ' + str(i12) + ' = ' + str((e0 | i10 | i11) & i12))
