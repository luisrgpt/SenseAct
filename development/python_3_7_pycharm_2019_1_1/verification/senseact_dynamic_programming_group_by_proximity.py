import unittest

from senseact.dynamic_programming import group_by_proximity

class GroupByProximity(unittest.TestCase):

  def test_something_1(self):
    result = group_by_proximity(
      extrapolation={
        (0.0, 0.0): (
          (0.0, 0.0),
        ),
        (0.0, 0.5): (
          (0.0, 0.5),
        ),
        (0.0, 1.0): (
          (0.0, 1.0),
        ),
        (0.0, 1.5): (
          (0.0, 1.5),
        ),
        (0.5, 0.5): (
          (0.5, 0.5),
        ),
        (0.5, 1.0): (
          (0.5, 1.0),
        ),
        (0.5, 1.5): (
          (0.5, 1.5),
        ),
        (1.0, 1.0): (
          (1.0, 1.0),
        ),
        (1.0, 1.5): (
          (1.0, 1.5),
        ),
        (1.5, 1.5): (
          (1.5, 1.5),
        ),
      },
    )
    self.assertEqual(
      sorted(
        (
          ((0.0, 0.0), (0.0, 0.5), (0.0, 1.0), (0.0, 1.5)),
          ((0.5, 0.5), (0.5, 1.0), (0.5, 1.5)),
          ((1.0, 1.0), (1.0, 1.5)),
          ((1.5, 1.5),)
        )
      ),
      sorted(result),
    )

  def test_something_2(self):
    result = group_by_proximity(
      extrapolation={
        (0.0, 1.0): (
          (0.0, 1.0),
          (0.0, 1.5),
        ),
        (0.0, 1.5): (
          (0.0, 1.5),
        ),
      },
    )
    self.assertEqual(
      sorted(
        (
          ((0.0, 1.0), (0.0, 1.5)),
        ),
      ),
      sorted(result),
    )

if __name__ == '__main__':
  unittest.main()
