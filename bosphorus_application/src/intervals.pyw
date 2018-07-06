# coding=utf-8
import functools

class Uncertainty:
    def __init__(self, center: float, absolute: float, relative: float):
        self.center: float = float(center)
        self.absolute: float = float(absolute)
        self.relative: float = float(relative)
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
        super().__init__(center, absolute, relative)
    def __repr__(self):
        return str(self.center) + ' +- ' + str(self.absolute)
class RelativeUncertainty(Uncertainty):
    def __init__(self, center: float, relative: float):
        absolute = relative * center / 100
        super().__init__(center, absolute, relative)
    def __repr__(self):
        return str(self.center) + ' +- ' + str(self.relative) + '%'

class Endpoint:
    def __init__(self, value: float, is_open: bool, is_closed: bool):
        self.value: float = float(value) if is_open != is_closed else None
        self.is_open: bool = is_open
        self.is_closed: bool = is_closed

    def is_bounded(self):
        return self.is_open != self.is_closed
    def is_unbounded(self):
        return self.is_open == self.is_closed

    def __eq__(self, other):
        return (self.value == other.value and self.is_open == other.is_open) or (
                    self.is_unbounded() and other.is_unbounded())
    def __ne__(self, other):
        return not self.__eq__(other)

    def __iadd__(self, other: float):
        self.value += other
        return self
    def __isub__(self, other: float):
        self.value -= other
        return self
class LeftEndpoint(Endpoint):
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
               and (self.value != other.value
                    or self.is_open
                    or other.is_closed)
    def __gt__(self, other):
        return self.__ge__(other) and self.__ne__(other)
    def __le__(self, other):
        return not self.__gt__(other)
    def __lt__(self, other):
        return not self.__ge__(other)

    def __add__(self, other: float):
        result = LeftEndpoint(self.value, self.is_open, self.is_closed)
        result += other
        return result
    def __sub__(self, other: float):
        result = LeftEndpoint(self.value, self.is_open, self.is_closed)
        result -= other
        return result

    def __repr__(self):
        return ('(' if self.is_open else '[') + ('LOW' if self.is_unbounded() else str(self.value))
class RightEndpoint(Endpoint):
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
               and (self.value != other.value
                    or self.is_open
                    or other.is_closed)
    def __lt__(self, other):
        return self.__le__(other) and self.__ne__(other)
    def __ge__(self, other):
        return not self.__lt__(other)
    def __gt__(self, other):
        return not self.__le__(other)

    def __add__(self, other: float):
        result = RightEndpoint(self.value, self.is_open, self.is_closed)
        result += other
        return result
    def __sub__(self, other: float):
        result = RightEndpoint(self.value, self.is_open, self.is_closed)
        result -= other
        return result

    def __repr__(self):
        return ('HIGH' if self.is_unbounded() else str(self.value)) + (')' if self.is_open else ']')

class Interval:
    def __init__(self, left: LeftEndpoint, right: RightEndpoint):
        self.left: LeftEndpoint = left
        self.right: RightEndpoint = right

    @classmethod
    def empty(cls):
        interval_left = LeftEndpoint(0, True, False)
        interval_right = RightEndpoint(0, True, False)
        return cls(interval_left, interval_right)
    @classmethod
    def domain(cls):
        interval_left = LeftEndpoint(0, True, True)
        interval_right = RightEndpoint(0, True, True)
        return cls(interval_left, interval_right)

    def is_unbounded(self):
        return self.left.is_unbounded() and self.right.is_unbounded()
    def is_bounded(self):
        return self.left.is_bounded() and self.right.is_bounded()
    def is_closed(self):
        return self.left.is_closed and self.right.is_closed
    def is_open(self):
        return self.left.is_open and self.right.is_open
    def is_degenerated(self):
        return self.is_bounded() and self.is_closed() and self.left.value == self.right.value
    def is_half_open(self):
        return self.left.is_open != self.right.is_open and self.left.is_closed != self.right.is_closed
    def is_proper(self):
        return not self.is_bounded() or self.left.value < self.right.value
    def is_empty(self):
        return not self.is_degenerated() and not self.is_proper()
    def is_infinitesimal(self):
        return self.is_half_open() and self.left.value == self.right.value

    def range(self):
        if self.is_empty() or self.is_unbounded():
            raise StopIteration()

        left = LeftEndpoint(self.left.value, self.left.is_open, self.left.is_closed)
        right = (
            RightEndpoint(self.left.value, False, True)
            if self.left.is_closed
            else
            RightEndpoint(self.left.value + 1, True, False)
        )
        while right <= self.right:
            yield Interval(left, right)
            if right < self.right:
                if right.is_open:
                    right = RightEndpoint(right.value, False, True)
                else:
                    right = RightEndpoint(right.value + 1, True, False)
            else:
                if left.is_closed:
                    left = LeftEndpoint(left.value, True, False)
                    right = RightEndpoint(left.value + 1, True, False)
                else:
                    left = LeftEndpoint(left.value + 1, False, True)
                    right = RightEndpoint(left.value, False, True)
        raise StopIteration()

    def __iter__(self):
        return self.range()
    def __len__(self):
        return int(self.right.value - self.left.value) if self.is_bounded() else None
    def __repr__(self):
        if self.is_empty():
            return '()'
        elif self.is_degenerated():
            return '{' + str(self.left.value) + '}'
        else:
            return str(self.left) + '..' + str(self.right)
    def __contains__(self, other):
        # print(str(other) + " in " + str(self) + "?")
        # noinspection PyChainedComparisons
        if isinstance(other, int):
            return (
                not self.is_empty()
                and (
                    (self.left.is_closed and self.left.value <= other)
                    or (self.left.is_open and self.left.value < other)
                )
                and (
                    (self.right.is_closed and other <= self.right.value)
                    or (self.right.is_open and other < self.right.value)
                )
            )
        else:
            return not self.is_empty() and not other.is_empty() and self <= other and self >= other

    def __lt__(self, other):
        return self.left < other.left
    def __gt__(self, other):
        return other.right < self.right
    def __eq__(self, other):
        return self.left == other.left and self.right == other.right or self.is_empty() and other.is_empty()
    def __le__(self, other):
        return self.left <= other.left or self.__eq__(other)
    def __ge__(self, other):
        return other.right <= self.right or self.__eq__(other)
    def __ne__(self, other):
        return not self.__eq__(other)

    def __ior__(self, other):
        # empty and not infinitesimal
        left = max(self, other).left
        right = min(self, other).right

        if (
            left.is_unbounded() or right.is_unbounded() or (
                left.value <= right.value and (
                    left.value != right.value or left.is_closed or right.is_closed
                )
            )
        ):
            # proper or degenerated or infinitesimal
            if other.left < self.left:
                self.left.value = other.left.value
                self.left.is_open = other.left.is_open
                self.left.is_closed = other.left.is_closed
            if other.right > self.right:
                self.right.value = other.right.value
                self.right.is_open = other.right.is_open
                self.right.is_closed = other.right.is_closed

        return self
    def __iand__(self, other):
        left = max(self, other).left
        right = min(self, other).right

        if left.is_unbounded() or right.is_unbounded() or (
            left.value <= right.value and (
                left.value != right.value or left.is_closed == right.is_closed
            )
        ):
            if other.left > self.left:
                self.left.value = other.left.value
                self.left.is_open = other.left.is_open
                self.left.is_closed = other.left.is_closed
            if other.right < self.right:
                self.right.value = other.right.value
                self.right.is_open = other.right.is_open
                self.right.is_closed = other.right.is_closed

        return self
    def __iadd__(self, other: Uncertainty):
        self_absolute = (self.right.value - self.left.value) / 2
        self_center = self.left.value + self_absolute
        self_uncertainty = AbsoluteUncertainty(self_center, self_absolute)

        uncertainty = self_uncertainty + other
        center = uncertainty.center
        absolute = uncertainty.absolute

        self.left.value = center - absolute
        self.right.value = center + absolute

        return self
    def __isub__(self, other: Uncertainty):
        self_absolute = (self.right.value - self.left.value) / 2
        self_center = self.left.value + self_absolute
        self_uncertainty = AbsoluteUncertainty(self_center, self_absolute)

        uncertainty = self_uncertainty - other
        center = uncertainty.center
        absolute = uncertainty.absolute

        self.left.value = center - absolute
        self.right.value = center + absolute

        return self
    def __add__(self, other: Uncertainty):
        result = Interval(
            left=LeftEndpoint(self.left.value, self.left.is_open, self.left.is_closed),
            right=RightEndpoint(self.right.value, self.right.is_open, self.right.is_closed)
        )
        result += other
        return result
    def __sub__(self, other: Uncertainty):
        result = Interval(
            left=LeftEndpoint(self.left.value, self.left.is_open, self.left.is_closed),
            right=RightEndpoint(self.right.value, self.right.is_open, self.right.is_closed)
        )
        result -= other
        return result
    def __and__(self, other):
        result = Interval(
            left=LeftEndpoint(self.left.value, self.left.is_open, self.left.is_closed),
            right=RightEndpoint(self.right.value, self.right.is_open, self.right.is_closed)
        )
        result &= other
        return result
    def __or__(self, other):
        result = Interval(
            left=LeftEndpoint(self.left.value, self.left.is_open, self.left.is_closed),
            right=RightEndpoint(self.right.value, self.right.is_open, self.right.is_closed)
        )
        result |= other
        return result
class IntervalExpression:
    def __init__(self, intervals: list):
        self.intervals = intervals#[x for x in intervals if not x.is_empty()]
        #self.intervals.sort()
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

    @classmethod
    def domain(cls):
        return cls([Interval.domain()])
    def sort(self):
        self.intervals.sort()
        for fst, snd in zip(self.intervals[1:], self.intervals[:-1]):
            fst |= snd
            if snd in fst:
                self.intervals.remove(snd)

    def __eq__(self, other):
        if len(self.intervals) is 0:
            return len(other.intervals) is 0
        elif len(other.intervals) is 0:
            return False
        else:
            return all(x[0] == x[1] for x in zip(self, other))
    def __ne__(self, other):
        return not self.__eq__(other)
    def __contains__(self, other):
        return all(any(small_interval in big_interval for big_interval in self) for small_interval in other)

    def __repr__(self):
        return (
            functools.reduce(
                lambda acc, value: str(acc) + (' or ' if acc != '' else '') + str(value),
                self.intervals,
                ''
            )
            if len(self) > 0
            else
            '()'
        )

    def invert(self):
        if len(self) is 0:
            self.intervals += [
                Interval(
                    left=LeftEndpoint(0, True, True),
                    right=RightEndpoint(0, True, True)
                )
            ]
        elif self[0].left.is_bounded():
            x = self[0]
            # Save right endpoint
            right_value = x.right.value
            right_is_open = x.right.is_open
            right_is_closed = x.right.is_closed
            # Change right endpoint using left endpoint
            x.right.value = x.left.value
            x.right.is_open = x.left.is_closed
            x.right.is_closed = x.left.is_open
            # Change left endpoint using low endpoint
            x.left.value = 0
            x.left.is_open = True
            x.left.is_closed = True
            for x in self[1:]:
                # Save left endpoint
                left_value = x.left.value
                left_is_open = x.left.is_open
                left_is_closed = x.left.is_closed
                # Change left endpoint using saved right endpoint
                x.left.value = right_value
                x.left.is_open = right_is_closed
                x.left.is_closed = right_is_open
                # Save right endpoint
                right_value = x.right.value
                right_is_open = x.right.is_open
                right_is_closed = x.right.is_closed
                # Change right endpoint using saved left endpoint
                x.right.value = left_value
                x.right.is_open = left_is_closed
                x.right.is_closed = left_is_open
            if right_is_open != right_is_closed:
                # Add new interval with high endpoint if it does not already exist
                self.intervals += [
                    Interval(
                        left=LeftEndpoint(
                            value=right_value,
                            is_open=right_is_closed,
                            is_closed=right_is_open
                        ),
                        right=RightEndpoint(
                            value=0,
                            is_open=True,
                            is_closed=True
                        )
                    )
                ]
        else:
            x = self[-1]
            if x.right.is_bounded():
                # Save left endpoint
                left_value = x.left.value
                left_is_open = x.left.is_open
                left_is_closed = x.left.is_closed
                # Save right endpoint
                x.left.value = x.right.value
                x.left.is_open = x.right.is_closed
                x.left.is_closed = x.right.is_open
                # Change right endpoint using high endpoint
                x.right.value = 0
                x.right.is_open = True
                x.right.is_closed = True
                for x in reversed(self[:-1]):
                    # Save right endpoint
                    right_value = x.right.value
                    right_is_open = x.right.is_open
                    right_is_closed = x.right.is_closed
                    # Change right endpoint using saved left endpoint
                    x.right.value = left_value
                    x.right.is_open = left_is_closed
                    x.right.is_closed = left_is_open
                    # Save left endpoint
                    left_value = x.left.value
                    left_is_open = x.left.is_open
                    left_is_closed = x.left.is_closed
                    # Change left endpoint using saved right endpoint
                    x.left.value = right_value
                    x.left.is_open = right_is_closed
                    x.left.is_closed = right_is_open
            else:
                # Save left endpoint
                left_value = x.left.value
                left_is_open = x.left.is_open
                left_is_closed = x.left.is_closed
                del self[-1]
                for x in reversed(self):
                    # Save right endpoint
                    right_value = x.right.value
                    right_is_open = x.right.is_open
                    right_is_closed = x.right.is_closed
                    # Change right endpoint using saved left endpoint
                    x.right.value = left_value
                    x.right.is_open = left_is_closed
                    x.right.is_closed = left_is_open
                    # Save left endpoint
                    left_value = x.left.value
                    left_is_open = x.left.is_open
                    left_is_closed = x.left.is_closed
                    # Change left endpoint using saved right endpoint
                    x.left.value = right_value
                    x.left.is_open = right_is_closed
                    x.left.is_closed = right_is_open
    def __ior__(self, other):
        self.intervals += [
            Interval(
                left=LeftEndpoint(x.left.value, x.left.is_open, x.left.is_closed),
                right=RightEndpoint(x.right.value, x.right.is_open, x.right.is_closed)
            ) for x in other
        ]
        self.sort()
        return self
    def __iand__(self, other):
        self.intervals = [x & y for x in self for y in other]
        self.intervals = [x for x in self if any(x in y for y in other)]
        self.sort()
        return self
    def __iadd__(self, other: Uncertainty):
        for interval in self:
            interval += other
        #self.sort()
        return self
    def __isub__(self, other: Uncertainty):
        for interval in self:
            interval -= other
        #self.sort()
        return self
    def __invert__(self):
        result = IntervalExpression(
            intervals=[
                Interval(
                    left=LeftEndpoint(x.left.value, x.left.is_open, x.left.is_closed),
                    right=RightEndpoint(x.right.value, x.right.is_open, x.right.is_closed)
                ) for x in self
            ]
        )
        result.invert()
        return result
    def __add__(self, other: Uncertainty):
        result = IntervalExpression(
            intervals=[
                Interval(
                    left=LeftEndpoint(x.left.value, x.left.is_open, x.left.is_closed),
                    right=RightEndpoint(x.right.value, x.right.is_open, x.right.is_closed)
                ) for x in self
            ]
        )
        result += other
        return result
    def __sub__(self, other: Uncertainty):
        result = IntervalExpression(
            intervals=[
                Interval(
                    left=LeftEndpoint(x.left.value, x.left.is_open, x.left.is_closed),
                    right=RightEndpoint(x.right.value, x.right.is_open, x.right.is_closed)
                ) for x in self
            ]
        )
        result -= other
        return result
    def __and__(self, other):
        result = IntervalExpression(
            intervals=[
                Interval(
                    left=LeftEndpoint(x.left.value, x.left.is_open, x.left.is_closed),
                    right=RightEndpoint(x.right.value, x.right.is_open, x.right.is_closed)
                ) for x in self
            ]
        )
        result &= other
        return result
    def __or__(self, other):
        result = IntervalExpression(
            intervals=[
                Interval(
                    left=LeftEndpoint(x.left.value, x.left.is_open, x.left.is_closed),
                    right=RightEndpoint(x.right.value, x.right.is_open, x.right.is_closed)
                ) for x in self
            ]
        )
        result |= other
        return result

def test():
    for x in Interval(
        left=LeftEndpoint(0, False, True),
        right=RightEndpoint(10, False, True)
    ):
        print(IntervalExpression([x]))

    l0 = LeftEndpoint(-1, True, True)  # (LOW
    l1 = LeftEndpoint(0, True, True)  # (LOW
    l2 = LeftEndpoint(0, False, True)  # [0
    l3 = LeftEndpoint(0, True, False)  # (0
    l4 = LeftEndpoint(1, True, True)  # (LOW
    l5 = LeftEndpoint(1, False, True)  # [1
    l6 = LeftEndpoint(1, True, False)  # (1

    r0 = RightEndpoint(-1, True, True)  # HIGH)
    r1 = RightEndpoint(1, True, True)  # HIGH)
    r2 = RightEndpoint(1, False, True)  # 1]
    r3 = RightEndpoint(1, True, False)  # 1)
    r4 = RightEndpoint(0, True, True)  # HIGH)
    r5 = RightEndpoint(0, False, True)  # 0]
    r6 = RightEndpoint(0, True, False)  # 0)
    r7 = RightEndpoint(5, False, True)  # 5]

    i0 = IntervalExpression([Interval(l1, r1)])  # (LOW..HIGH)
    i1 = IntervalExpression([Interval(l1, r2)])  # (LOW..1]
    i2 = IntervalExpression([Interval(l1, r3)])  # (LOW..1)
    i3 = IntervalExpression([Interval(l2, r1)])  # [0..HIGH)
    i4 = IntervalExpression([Interval(l2, r2)])  # [0..1]
    i5 = IntervalExpression([Interval(l2, r3)])  # [0..1)
    i6 = IntervalExpression([Interval(l3, r1)])  # (0..HIGH)
    i7 = IntervalExpression([Interval(l3, r2)])  # (0..1]
    i8 = IntervalExpression([Interval(l3, r3)])  # (0..1)
    i9 = IntervalExpression([Interval(l5, r5)])  # [1..0] -> ()
    i10 = IntervalExpression([Interval(l1, r6)])  # (LOW..0)
    i11 = IntervalExpression([Interval(l6, r1)])  # (1..HIGH)
    i12 = IntervalExpression([Interval(l2, r7)])  # [0..5]

    e0 = IntervalExpression([])  # ()
    e1 = IntervalExpression.domain()  # (LOW..HIGH)

    print(str(i7 | i11))
    print(str(e0 | i10 | i11) + ' and ' + str(i12) + ' = ' + str((e0 | i10 | i11) & i12))
    print('-----------------------')
    print('left_endpoint:')
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
    print('right_endpoint:')
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
    print('interval_expression:')
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
