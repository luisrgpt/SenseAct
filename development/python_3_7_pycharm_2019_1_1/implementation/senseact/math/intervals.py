from math import inf
############################################################


############################################################
class Interval:
  def __init__(self, intervals):
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

  def __lt__(self, other):
    return self.intervals.__lt__(other.intervals)

  def __le__(self, other):
    return self.intervals.__le__(other.intervals)
  ############################################################

  ############################################################
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
  ############################################################

  ############################################################
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
  ############################################################

  ############################################################
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
        del [self[y]]
        n_self -= 1
      x += 1
    return self
  ############################################################

  ############################################################
  def __iand__(self, other):
    intervals = self.intervals
    self.intervals = []

    for x in intervals:
      for y in other:
        # Left of the highest
        lower = (x if y[1] <= x[1] else y)[0]
        # Right of the lowest
        upper = (x if x[0] <= y[0] else y)[1]
        # Add interval if intersection exists
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
        del [self[y]]
        n_self -= 1
      x += 1
    return self
  ############################################################

  ############################################################
  def __iadd__(self, other: tuple):
    if other == (0, 0):
      return self

    (center, uncertainty) = other

    n_self = len(self)
    if n_self is 0:
      self.intervals += [
        ((center - uncertainty, True), (center + uncertainty, False))]
    else:
      for x in range(n_self):
        (s_lower, s_open), (s_upper, s_closed) = self[x]
        self[x] = ((s_lower + center - uncertainty, s_open),
                   (s_upper + center + uncertainty, s_closed))

      n_self -= 1
      x = 0
      while x < n_self:
        y = x + 1

        lower = (self[x] if self[y][1] <= self[x][1] else self[y])[0]
        upper = (self[x] if self[x][0] <= self[y][0] else self[y])[1]

        if lower <= upper:
          self[x] = (min(self[x][0], self[y][0]), max(self[x][1], self[y][1]))
          del [self[y]]
          n_self -= 1
        x += 1
    return self
  ############################################################

  ############################################################
  def remove(self, other: tuple):
    intervals = self.intervals
    self.intervals = []
    for x in intervals:
      lower = (x if other[1] <= x[1] else other)[0]
      upper = (x if x[0] <= other[0] else other)[1]

      if lower < upper:
        if x[0] < other[0]:
          self.intervals += [
            (x[0], other[0])
          ]
        if other[1] < x[1]:
          self.intervals += [
            (other[1], x[1])
          ]
      else:
        self.intervals += [x]
    return self
  ############################################################

  ############################################################
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

    removed = 0
    for x in range(len(self)):
      if self[x - removed][1] <= self[x - removed][0]:
        del self[x - removed]
        removed += 1
  ############################################################

  ############################################################
  def __invert__(self):
    result = Interval(self[:])
    result.invert()
    return result
  ############################################################

  ############################################################
  def __add__(self, other):
    result = Interval(self[:])
    result += other
    return result
  ############################################################

  ############################################################
  def __and__(self, other):
    result = Interval(self[:])
    result &= other
    return result
  ############################################################

  ############################################################
  def __or__(self, other):
    result = Interval(self[:])
    result |= other
    return result
