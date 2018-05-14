import functools
import time

class Uncertainty:
    def __init__(self, center: float, absolute: float, relative: float):
        self.center: float = center
        self.absolute: float = absolute
        self.relative: float = relative

    def addition(self, other = None):
        if other is None:
            return self

        result_center = self.center + other.center
        result_absolute = self.absolute + other.absolute
        result = AbsoluteUncertainty(result_center, result_absolute)

        return result

    def subtraction(self, other = None):
        if other is None:
            return self

        result_center = self.center - other.center
        result_absolute = self.absolute + other.absolute
        result = AbsoluteUncertainty(result_center, result_absolute)

        return result

    def multiplication(self, other = None):
        if other is None:
            return self

        result_center = self.center * other.center
        result_relative = self.relative + other.relative
        result = RelativeUncertainty(result_center, result_relative)

        return result

    def division(self, other = None):
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
        return ('HIGH' if self.is_unbounded() else str(self.value)) + (')' if self.is_open else ']')

class Interval:
    def __init__(self, left: LeftEndpoint, right: RightEndpoint):
        self.left:  LeftEndpoint  = left
        self.right: RightEndpoint = right

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
        return self.left.is_open != self.right.is_open and self.left.is_closed != self.right.is_closed

    def is_half_bounded(self) -> bool:
        return self.left.is_bounded() != self.right.is_bounded()

    def is_not_bounded(self) -> bool:
        return not self.is_bounded()

    def is_proper(self) -> bool:
        return self.is_not_bounded() or self.left.value < self.right.value

    def is_empty(self) -> bool:
        return not self.is_degenerated() and not self.is_proper()

    def is_not_empty(self) -> bool:
        return not self.is_empty()

    def touches(self, other) -> bool:
        possible_contacts = [Interval(self.left, other.right), Interval(other.left, self.right)]
        return any(value.is_half_open() and value.left.value == value.right.value for value in possible_contacts)

    def intersects(self, other) -> bool:
        possible_contacts = [Interval(self.left, other.right), Interval(other.left, self.right)]
        return all(value.is_not_empty() for value in possible_contacts)

    @classmethod
    def empty(cls):
        interval_left  = LeftEndpoint(0, True, False)
        interval_right = RightEndpoint(0, True, False)
        return cls(interval_left, interval_right)

    @classmethod
    def domain(cls):
        interval_left  = LeftEndpoint(0, True, True)
        interval_right = RightEndpoint(0, True, True)
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
            return '()'
        elif self.is_degenerated():
            return '{' + str(self.left.value) + '}'
        else:
            return str(self.left) + ('..') + str(self.right)

class IntervalExpression:
    def __init__(self, intervals: list):
        self.intervals = sorted(list(filter(lambda value: value.is_not_empty(), intervals)))

    def __eq__(self, other):
        if len(self.intervals) == 0:
            return len(other.intervals) == 0
        elif len(other.intervals) == 0:
            return False
        else:
            return all(value[0] == value[1] for value in zip(self.union().intervals, other.union().intervals))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return functools.reduce(lambda acc, value: str(acc) + (' or ' if acc != '' else '') + str(value), self.intervals, '') \
            if self != IntervalExpression.empty() else '()'

    @classmethod
    def empty(cls):
        return cls([])

    @classmethod
    def domain(cls):
        return cls([Interval.domain()])

    def union(self, other = None):
        if other is None:
            other = self.empty()
        elif isinstance(other, Interval):
            other = IntervalExpression([other])

        intervals = self.intervals + other.intervals

        number_of_intervals = len(intervals)
        if number_of_intervals == 0:
            return IntervalExpression.empty()
        elif number_of_intervals == 1:
            return IntervalExpression(intervals)

        head, *tail = sorted(intervals)
        acc = [head]
        for snd in tail:
            acc, fst = acc[:-1], acc[-1]

            # reduction condition
            if fst.touches(snd) or fst.intersects(snd):
                left  = min(fst.left,  snd.left)
                right = max(fst.right, snd.right)
                acc += [Interval(left, right)]

            else:
                acc += [fst, snd]

        return IntervalExpression(acc)

    def negation(self):
        if self == IntervalExpression.empty():
            return IntervalExpression.domain()

        acc = []
        stack = None
        for value in self.union().intervals:
            if value.left.is_bounded():
                if stack is not None:
                    left = LeftEndpoint(stack.value, stack.is_closed, stack.is_open)
                else:
                    left = LeftEndpoint(None, True, True)
                right = RightEndpoint(value.left.value, value.left.is_closed, value.left.is_open)
                acc += [Interval(left, right)]
                stack = None
            if value.right.is_bounded():
                stack = value.right
        if stack is not None:
            left = LeftEndpoint(stack.value, stack.is_closed, stack.is_open)
            right = RightEndpoint(None, True, True)
            acc += [Interval(left, right)]

        return IntervalExpression(acc)

    def intersection(self, other = None):
        if other is None:
            other = self.domain()
        elif isinstance(other, Interval):
            other = IntervalExpression([other])

        # Applying De Morgan's Laws
        not_self  = self.negation()
        not_other = other.negation()

        not_result = not_self.union(not_other)
        result = not_result.negation()

        #print('')
        #print('Intersection:')
        #print('(' + str(self) + ') and (' + str(other) + ')')
        #print('not ' + str(self) + ' = ' + str(not_self))
        #print('not ' + str(other) + ' = ' + str(not_other))
        #print(str(not_self) + ' u ' + str(not_other) + ' = ' + str(not_result))
        #print('not ' + str(not_result) + ' = ' + str(result))
        #if result.intervals[-1].right.is_unbounded():
        #    print('')
        #else:
        #    print('')
        #print('')
        #print('')
        return result

    def contains(self, other):
        if self == IntervalExpression.empty() or other == IntervalExpression.empty():
            return False

        and_interval_expression = self.intersection(other)
        
        if and_interval_expression == IntervalExpression.empty():
            return False
        else:
            return all(value[0] == value[1] for value in zip(other.intervals, and_interval_expression.intervals))

    def addition(self, other: Uncertainty = None):
        if other is None:
            return self

        result_intervals = []
        for self_interval in self.intervals:
            self_left = self_interval.left
            self_right = self_interval.right

            self_absolute = (self_right.value - self_left.value) / 2
            self_center = self_left.value + self_absolute
            self_uncertainty = AbsoluteUncertainty(self_center, self_absolute)

            result_uncertainty = self_uncertainty.addition(other)
            result_absolute = result_uncertainty.absolute
            result_center = result_uncertainty.center

            result_left = LeftEndpoint(result_center - result_absolute, self_left.is_open, self_left.is_closed)
            result_right = RightEndpoint(result_center + result_absolute, self_right.is_open, self_right.is_closed)
            result_interval = Interval(result_left, result_right)
            
            result_intervals += [result_interval]

        result = IntervalExpression(result_intervals).union()

        return result

    def subtraction(self, other: Uncertainty = None):
        if other is None:
            return self

        result_intervals = []
        for self_interval in self.intervals:
            self_left = self_interval.left
            self_right = self_interval.right
            
            self_absolute_ = (self_left.value - self_right.value) / 2
            self_center = self_left.value + self_absolute
            self_uncertainty = AbsoluteUncertainty(self_center, self_absolute)

            result_uncertainty = self_uncertainty.subtraction(other)
            result_absolute = result_uncertainty.absolute
            result_center = result_uncertainty.center

            result_left = LeftEndpoint(result_center - result_absolute, self_left.is_open, self_left.is_closed)
            result_right = RightEndpoint(result_center + result_absolute, self_right.is_open, self_right.is_closed)

            result_interval = Interval(result_left, result_right)

            result_intervals += [result_interval]

        result = IntervalExpression(result_intervals)

        return result

def test():
    l0 = LeftEndpoint(-1, True, True)  # (LOW
    l1 = LeftEndpoint(0, True, True)   # (LOW
    l2 = LeftEndpoint(0, False, True)  # [0
    l3 = LeftEndpoint(0, True, False)  # (0
    l4 = LeftEndpoint(1, True, True)   # (LOW
    l5 = LeftEndpoint(1, False, True)  # [1
    l6 = LeftEndpoint(1, True, False)  # (1

    r0 = RightEndpoint(-1, True, True) # HIGH)
    r1 = RightEndpoint(1, True, True)  # HIGH)
    r2 = RightEndpoint(1, False, True) # 1]
    r3 = RightEndpoint(1, True, False) # 1)
    r4 = RightEndpoint(0, True, True)  # HIGH)
    r5 = RightEndpoint(0, False, True) # 0]
    r6 = RightEndpoint(0, True, False) # 0)
    r7 = RightEndpoint(5, False, True) # 5]

    i0 = Interval(l1, r1) # (LOW..HIGH)
    i1 = Interval(l1, r2) # (LOW..1]
    i2 = Interval(l1, r3) # (LOW..1)
    i3 = Interval(l2, r1) # [0..HIGH)
    i4 = Interval(l2, r2) # [0..1]
    i5 = Interval(l2, r3) # [0..1)
    i6 = Interval(l3, r1) # (0..HIGH)
    i7 = Interval(l3, r2) # (0..1]
    i8 = Interval(l3, r3) # (0..1)
    i9 = Interval(l5, r5) # [1..0] -> ()
    i10 = Interval(l1, r6) # (LOW..0)
    i11 = Interval(l6, r1) # (1..HIGH)
    i12 = Interval(l2, r7) # [0..5]

    e0 = IntervalExpression.empty() # ()
    e1 = IntervalExpression.domain() # (LOW..HIGH)

    print(str(e0.union(i10).union(i11)) + ' n ' + str(i12) + ' = ' + str(e0.union(i10).union(i11).intersection(i12)))
   #print('-----------------------')
   #print('left_endpoint:')
   #print('')
   #print('id')
   #print('l0 = ' + str(l0))
   #print('l1 = ' + str(l1))
   #print('l2 = ' + str(l2))
   #print('l3 = ' + str(l3))
   #print('l4 = ' + str(l4))
   #print('l5 = ' + str(l5))
   #print('l6 = ' + str(l6))
   #print('')
   #print('less')
   #print('l0 < l1 = ' + str(l0 < l1))
   #print('l1 < l2 = ' + str(l1 < l2))
   #print('l2 < l3 = ' + str(l2 < l3))
   #print('l3 < l4 = ' + str(l3 < l4))
   #print('l4 < l5 = ' + str(l4 < l5))
   #print('l5 < l6 = ' + str(l5 < l6))
   #print('')
   #print('less equal')
   #print('l0 <= l1 = ' + str(l0 <= l1))
   #print('l1 <= l2 = ' + str(l1 <= l2))
   #print('l2 <= l3 = ' + str(l2 <= l3))
   #print('l3 <= l4 = ' + str(l3 <= l4))
   #print('l4 <= l5 = ' + str(l4 <= l5))
   #print('l5 <= l6 = ' + str(l5 <= l6))
   #print('')
   #print('equal')
   #print('l0 == l1 = ' + str(l0 == l1))
   #print('l1 == l2 = ' + str(l1 == l2))
   #print('l2 == l3 = ' + str(l2 == l3))
   #print('l3 == l4 = ' + str(l3 == l4))
   #print('l4 == l5 = ' + str(l4 == l5))
   #print('l5 == l6 = ' + str(l5 == l6))
   #print('')
   #print('greater equal')
   #print('l0 >= l1 = ' + str(l0 >= l1))
   #print('l1 >= l2 = ' + str(l1 >= l2))
   #print('l2 >= l3 = ' + str(l2 >= l3))
   #print('l3 >= l4 = ' + str(l3 >= l4))
   #print('l4 >= l5 = ' + str(l4 >= l5))
   #print('l5 >= l6 = ' + str(l5 >= l6))
   #print('')
   #print('greater')
   #print('l0 > l1 = ' + str(l0 > l1))
   #print('l1 > l2 = ' + str(l1 > l2))
   #print('l2 > l3 = ' + str(l2 > l3))
   #print('l3 > l4 = ' + str(l3 > l4))
   #print('l4 > l5 = ' + str(l4 > l5))
   #print('l5 > l6 = ' + str(l5 > l6))
   #print('')
   #print('-----------------------')
   #print('right_endpoint:')
   #print('')
   #print('id')
   #print('r0 = ' + str(r0))
   #print('r1 = ' + str(r1))
   #print('r2 = ' + str(r2))
   #print('r3 = ' + str(r3))
   #print('r4 = ' + str(r4))
   #print('r5 = ' + str(r5))
   #print('r6 = ' + str(r6))
   #print('')
   #print('less')
   #print('r0 < r1 = ' + str(r0 < r1))
   #print('r1 < r2 = ' + str(r1 < r2))
   #print('r2 < r3 = ' + str(r2 < r3))
   #print('r3 < r4 = ' + str(r3 < r4))
   #print('r4 < r5 = ' + str(r4 < r5))
   #print('r5 < r6 = ' + str(r5 < r6))
   #print('')
   #print('less equal')
   #print('r0 <= r1 = ' + str(r0 <= r1))
   #print('r1 <= r2 = ' + str(r1 <= r2))
   #print('r2 <= r3 = ' + str(r2 <= r3))
   #print('r3 <= r4 = ' + str(r3 <= r4))
   #print('r4 <= r5 = ' + str(r4 <= r5))
   #print('r5 <= r6 = ' + str(r5 <= r6))
   #print('')
   #print('equal')
   #print('r0 == r1 = ' + str(r0 == r1))
   #print('r1 == r2 = ' + str(r1 == r2))
   #print('r2 == r3 = ' + str(r2 == r3))
   #print('r3 == r4 = ' + str(r3 == r4))
   #print('r4 == r5 = ' + str(r4 == r5))
   #print('r5 == r6 = ' + str(r5 == r6))
   #print('')
   #print('greater equal')
   #print('r0 >= r1 = ' + str(r0 >= r1))
   #print('r1 >= r2 = ' + str(r1 >= r2))
   #print('r2 >= r3 = ' + str(r2 >= r3))
   #print('r3 >= r4 = ' + str(r3 >= r4))
   #print('r4 >= r5 = ' + str(r4 >= r5))
   #print('r5 >= r6 = ' + str(r5 >= r6))
   #print('')
   #print('greater')
   #print('r0 > r1 = ' + str(r0 > r1))
   #print('r1 > r2 = ' + str(r1 > r2))
   #print('r2 > r3 = ' + str(r2 > r3))
   #print('r3 > r4 = ' + str(r3 > r4))
   #print('r4 > r5 = ' + str(r4 > r5))
   #print('r5 > r6 = ' + str(r5 > r6))
   #print('')
   #print('-----------------------')
   #print('interval:')
   #print('')
   #print('id')
   #print('i0 = ' + str(i0))
   #print('i1 = ' + str(i1))
   #print('i2 = ' + str(i2))
   #print('i3 = ' + str(i3))
   #print('i4 = ' + str(i4))
   #print('i5 = ' + str(i5))
   #print('i6 = ' + str(i6))
   #print('i7 = ' + str(i7))
   #print('i8 = ' + str(i8))
   #print('i9 = ' + str(i9))
   #print('-----------------------')
   #print('interval_expression:')
   #print('')
   #print(str(e0) + ' u ' + str(i1) + ' = ' + str(e0.union(i1)))
   #print(str(e0) + ' / ' + str(i1) + ' = ' + str(e0.union(i1).negation()))
   #print(str(e0) + ' n ' + str(i1) + ' = ' + str(e0.intersection(i1)))
   #print(str(e0) + ' u ' + str(i2) + ' = ' + str(e0.union(i2)))
   #print(str(e0) + ' / ' + str(i2) + ' = ' + str(e0.union(i2).negation()))
   #print(str(e0) + ' n ' + str(i2) + ' = ' + str(e0.intersection(i2)))
   #print(str(i1) + ' u ' + str(i2) + ' = ' + str(e0.union(i1).union(i2)))
   #print(str(i2) + ' u ' + str(i1) + ' = ' + str(e0.union(i2).union(i1)))
   #print(str(i1) + ' n ' + str(i2) + ' = ' + str(e0.union(i1).intersection(i2)))
   #print(str(i2) + ' n ' + str(i1) + ' = ' + str(e0.union(i2).intersection(i1)))
   #print(str(e0) + ' / ' + str(i7) + ' = ' + str(e0.union(i7).negation()))
   #print(str(e1) + ' n ' + str(i7) + ' = ' + str(e1.intersection(i7)))

    while(True):
        time.sleep(1000)