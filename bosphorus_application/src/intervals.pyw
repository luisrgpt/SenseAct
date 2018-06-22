# coding=utf-8
"""Intervals

"""
import functools
import time

class Uncertainty:
    """Uncertainty

    """
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
    """Absolute uncertainty

    """
    def __init__(self, center: float, absolute: float):
        relative = (absolute / center * 100) if center != 0 else 0
        super().__init__(center, absolute, relative)
    def __repr__(self):
        return str(self.center) + ' +- ' + str(self.absolute)
class RelativeUncertainty(Uncertainty):
    """Relative uncertainty

    """
    def __init__(self, center: float, relative: float):
        absolute = relative * center / 100
        super().__init__(center, absolute, relative)
    def __repr__(self):
        return str(self.center) + ' +- ' + str(self.relative) + '%'

class Endpoint:
    """Endpoint

    """
    def __init__(self, value: float, is_open: bool, is_closed: bool):
        self.value: float = float(value)
        self.is_open: bool = is_open
        self.is_closed: bool = is_closed
        self.is_unbounded: bool = is_open == is_closed
        self.is_bounded: bool = is_open != is_closed

    def __eq__(self, other):
        return (self.value == other.value and self.is_open == other.is_open) or (
                    self.is_unbounded and other.is_unbounded)
    def __ne__(self, other):
        return not self.__eq__(other)

    def __iadd__(self, other: float):
        self.value += other
        return self
    def __isub__(self, other: float):
        self.value -= other
        return self
class LeftEndpoint(Endpoint):
    """Left endpoint

    """
    def __init__(self, value: float, is_open: bool, is_closed: bool):
        super().__init__(value, is_open, is_closed)
    def __deepcopy__(self, memodict={}):
        return LeftEndpoint(self.value, self.is_open, self.is_closed)

    def __eq__(self, other):
        return super().__eq__(other)
    def __ne__(self, other):
        return super().__ne__(other)
    def __ge__(self, other):
        return other.is_unbounded \
               or self.is_bounded \
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
        result = self.__deepcopy__()
        result += other
        return result
    def __sub__(self, other: float):
        result = self.__deepcopy__()
        result -= other
        return result

    def __repr__(self):
        return ('(' if self.is_open else '[') + ('LOW' if self.is_unbounded else str(self.value))
class RightEndpoint(Endpoint):
    """Right endpoint

    """
    def __init__(self, value: float, is_open: bool, is_closed: bool):
        super().__init__(value, is_open, is_closed)
    def __deepcopy__(self, memodict={}):
        return RightEndpoint(self.value, self.is_open, self.is_closed)

    def __eq__(self, other):
        return super().__eq__(other)
    def __ne__(self, other):
        return super().__ne__(other)
    def __le__(self, other):
        return other.is_unbounded \
               or self.is_bounded \
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
        result = self.__deepcopy__()
        result += other
        return result
    def __sub__(self, other: float):
        result = self.__deepcopy__()
        result -= other
        return result

    def __repr__(self):
        return ('HIGH' if self.is_unbounded else str(self.value)) + (')' if self.is_open else ']')

class Interval:
    """Interval

    """
    def __init__(self, left: LeftEndpoint, right: RightEndpoint):
        self.left: LeftEndpoint = left
        self.right: RightEndpoint = right
        self.is_bounded = left.is_bounded and right.is_bounded
        self.is_unbounded = left.is_unbounded and right.is_unbounded
        self.is_closed = left.is_closed and right.is_closed
        self.is_degenerated = self.is_bounded and self.is_closed and left.value == right.value
        self.is_proper = not self.is_bounded or left.value < right.value
        self.is_empty = not self.is_degenerated and not self.is_proper
    def __deepcopy__(self, memodict={}):
        return Interval(
            left=self.left.__deepcopy__(),
            right=self.right.__deepcopy__()
        )
    def __iter__(self):
        return self.range()
    def __len__(self):
        return int(self.right.value - self.left.value) if self.is_bounded else None

    @classmethod
    def empty(cls):
        """

        :return:
        """
        interval_left = LeftEndpoint(0, True, False)
        interval_right = RightEndpoint(0, True, False)
        return cls(interval_left, interval_right)
    @classmethod
    def domain(cls):
        """

        :return:
        """
        interval_left = LeftEndpoint(0, True, True)
        interval_right = RightEndpoint(0, True, True)
        return cls(interval_left, interval_right)
    def is_not_closed(self) -> bool:
        """

        :return:
        """
        return not self.is_closed
    def is_open(self) -> bool:
        """

        :return:
        """
        return self.left.is_open and self.right.is_open
    def is_half_open(self) -> bool:
        """

        :return:
        """
        return self.left.is_open != self.right.is_open and self.left.is_closed != self.right.is_closed
    def is_half_bounded(self) -> bool:
        """

        :return:
        """
        return self.left.is_bounded != self.right.is_bounded
    def is_not_bounded(self) -> bool:
        """

        :return:
        """
        return not self.is_bounded
    def is_not_empty(self) -> bool:
        """

        :return:
        """
        return not self.is_empty
    def is_infinitesimal(self) -> bool:
        """

        :return:
        """
        return self.is_half_open() and self.left.value == self.right.value
    def is_not_infinitesimal(self) -> bool:
        """

        :return:
        """
        return not self.is_infinitesimal()

    def range(self):
        if self.is_empty or self.is_unbounded:
            raise StopIteration()

        left = self.left.__deepcopy__()
        right = (
            RightEndpoint(self.left.value, False, True)
            if self.left.is_closed
            else
            RightEndpoint(self.left.value + 1, True, False)
        )
        current = Interval(left, right)
        while current.right <= self.right:
            current = Interval(left, right)
            yield current
            if current.right < self.right:
                if current.right.is_open:
                    current.right.is_open = False
                    current.right.is_closed = True
                else:
                    current.right += 1
                    current.right.is_open = True
                    current.right.is_closed = False
            else:
                if current.left.is_closed:
                    current.left.is_open = True
                    current.left.is_closed = False
                    current.right.value = current.left.value + 1
                    current.right.is_open = True
                    current.right.is_closed = False
                else:
                    current.left += 1
                    current.left.is_open = False
                    current.left.is_closed = True
                    current.right.value = current.left.value
                    current.right.is_open = False
                    current.right.is_closed = True
        raise StopIteration()

    def __repr__(self):
        if self.is_empty:
            return '()'
        elif self.is_degenerated:
            return '{' + str(self.left.value) + '}'
        else:
            return str(self.left) + '..' + str(self.right)
    def __contains__(self, other):
        # print(str(other) + " in " + str(self) + "?")
        # noinspection PyChainedComparisons
        return self.is_not_empty() and other.is_not_empty() and self <= other and self >= other

    def __lt__(self, other):
        return self.left < other.left
    def __gt__(self, other):
        return other.right < self.right
    def __eq__(self, other):
        return self.left == other.left and self.right == other.right or self.is_empty and other.is_empty
    def __le__(self, other):
        return self.left <= other.left or self.__eq__(other)
    def __ge__(self, other):
        return other.right <= self.right or self.__eq__(other)
    def __ne__(self, other):
        return not self.__eq__(other)

    def __ior__(self, other):
        gap = Interval(
            left=max(self, other).left,
            right=min(self, other).right
        )

        # empty and not infinitesimal
        if gap.is_empty and gap.is_not_infinitesimal():
            return self, other
        # proper or degenerated or infinitesimal
        self.left = min(self.left, other.left)
        self.right = max(self.right, other.right)

        self.is_bounded = self.left.is_bounded and self.right.is_bounded
        self.is_unbounded = self.left.is_unbounded and self.right.is_unbounded
        self.is_closed = self.left.is_closed and self.right.is_closed
        self.is_degenerated = self.is_bounded and self.is_closed and self.left.value == self.right.value
        self.is_proper = not self.is_bounded or self.left.value < self.right.value
        self.is_empty = not self.is_degenerated and not self.is_proper

        return self
    def __iand__(self, other):
        gap = Interval(
            left=max(self, other).left,
            right=min(self, other).right
        )

        return (
            # if empty
            Interval.empty()
            if gap.is_empty
            else
            # if proper or degenerated
            Interval(
                left=max(self.left, other.left),
                right=min(self.right, other.right)
            )
        )
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
        result = self.__deepcopy__()
        result += other
        return result
    def __sub__(self, other: Uncertainty):
        result = self.__deepcopy__()
        result -= other
        return result
    def __and__(self, other):
        result = self.__deepcopy__()
        result &= other
        return result
    def __or__(self, other):
        result = self.__deepcopy__()
        result |= other
        return result

class IntervalExpression:
    """Interval expression

    """
    def __init__(self, intervals: list):
        self.intervals = [x for x in intervals if x.is_not_empty()]
        self.intervals.sort()
    def __iter__(self):
        return self.intervals.__iter__()
    def __getitem__(self, item):
        return self.intervals.__getitem__(item)
    def __len__(self):
        return self.intervals.__len__()
    def __deepcopy__(self, memodict={}):
        return IntervalExpression(
            intervals=[x.__deepcopy__() for x in self]
        )

    @classmethod
    def empty(cls):
        """

        :return:
        """
        return cls([])
    @classmethod
    def domain(cls):
        """

        :return:
        """
        return cls([Interval.domain()])
    def sort(self):
        """Sort

        """
        self.intervals.sort()
        for fst, snd in zip(self.intervals[1:], self.intervals[:-1]):
            fst |= snd
            if isinstance(fst, Interval):
                self.intervals.remove(snd)
            else:
                fst, _ = fst

    def __eq__(self, other):
        if len(self.intervals) == 0:
            return len(other.intervals) == 0
        elif len(other.intervals) == 0:
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
            if self != IntervalExpression.empty()
            else
            '()'
        )

    def __invert__(self):
        if len(self) == 0:
            return IntervalExpression.domain()

        acc = []
        stack = None
        self.sort()
        for x in self:
            if x.left.is_bounded:
                if stack is not None:
                    left = LeftEndpoint(stack.value, stack.is_closed, stack.is_open)
                else:
                    left = LeftEndpoint(0, True, True)
                right = RightEndpoint(x.left.value, x.left.is_closed, x.left.is_open)
                acc += [Interval(left, right)]
                stack = None
            if x.right.is_bounded:
                stack = x.right
        if stack is not None:
            left = LeftEndpoint(stack.value, stack.is_closed, stack.is_open)
            right = RightEndpoint(0, True, True)
            acc += [Interval(left, right)]

        return IntervalExpression(acc)
    def __ior__(self, other):
        self.intervals += [x.__deepcopy__() for x in other]
        self.sort()

        return self
    def __iand__(self, other):
        # print('')
        # print('Intersection:')
        # print('(' + str(self) + ') and (' + str(other) + ')')
        # print('not ' + str(self) + ' = ' + str(not_self))
        # print('not ' + str(other) + ' = ' + str(not_other))
        # print(str(not_self) + ' or ' + str(not_other) + ' = ' + str(not_result))
        # print('not ' + str(not_result) + ' = ' + str(result))
        # if result.intervals[-1].right.is_unbounded():
        #    print('')
        # else:
        #    print('')
        # print('')
        # print('')

        # Applying De Morgan's Laws
        self.intervals = (~self).intervals
        self |= ~other
        self.intervals = (~self).intervals
        return self
    def __iadd__(self, other: Uncertainty):
        for interval in self:
            interval += other
        self.sort()
        return self
    def __isub__(self, other: Uncertainty):
        for interval in self:
            interval -= other
        self.sort()
        return self
    def __add__(self, other: Uncertainty):
        result = self.__deepcopy__()
        result += other
        return result
    def __sub__(self, other: Uncertainty):
        result = self.__deepcopy__()
        result -= other
        return result
    def __and__(self, other):
        result = self.__deepcopy__()
        result &= other
        return result
    def __or__(self, other):
        result = self.__deepcopy__()
        result |= other
        return result

def test():
    """Test

    """
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

    e0 = IntervalExpression.empty()  # ()
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
    print(i2)
    print(str(i2) + ' or ' + str(i1) + ' = ' + str(i2 | i1))
    print(i2)
    print(str(i1) + ' and ' + str(i2) + ' = ' + str(i1 & i2))
    print(str(i2) + ' and ' + str(i1) + ' = ' + str(i2 & i1))
    print('not ' + str(i7) + ' = ' + str(~i7))
    print(str(e1) + ' and ' + str(i7) + ' = ' + str(e1 & i7))
    print(str(e1) + ' in ' + str(i7) + ' = ' + str(e1 in i7))
    print(str(i7) + ' in ' + str(e1) + ' = ' + str(i7 in e1))

    while True:
        time.sleep(1000)
