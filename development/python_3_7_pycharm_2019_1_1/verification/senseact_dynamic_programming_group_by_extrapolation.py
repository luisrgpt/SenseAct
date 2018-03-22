import unittest

from senseact.dynamic_programming import group_by_extrapolation

class GroupByExtrapolation(unittest.TestCase):

  def test_something_1(self,):
    result = group_by_extrapolation(
      excluded={
        (-2.0, 0.0): { (): 100 },
        (-2.0, 0.5): { (): 101 },
        (-2.0, 2.5): { (): 101 },
        (-1.5, 1.0): { (): 350 },
        (-1.5, 1.5): { (): 300 },
        (-1.5, 3.0): { (): 350 },
        (-1.5, 3.5): { (): 300 },
        (-1.0, 1.5): { (): 300 },
        (-1.0, 3.5): { (): 300 },
        (0.0, 0.0): { (): 100 },
        (0.0, 0.5): { (): 101 },
        (0.0, 2.5): { (): 101 },
        (0.5, 0.5): { (): 100 },
        (0.5, 1.0): { (): 350 },
        (0.5, 1.5): { (): 300 },
        (0.5, 3.0): { (): 350 },
        (0.5, 3.5): { (): 300 },
        (1.0, 1.0): { (): 300 },
        (1.0, 1.5): { (): 300 },
        (1.0, 3.5): { (): 300 },
        (1.5, 1.5): { (): 300 },
        (1.5, 3.5): { (): 300 },
      },
      time=1,
      settings={
        'alert': {
          'types': (
            (
              (0.5, 1.5),
              200,
            ),
            (
              (0.0, 0.5),
              0,
            ),
          )
        },
        'scale': 0.5,
        'boundaries': (0.0, 1.5),
        'target': {
          'speed': 1,
        },
      },
    )
    self.assertEqual(
      sorted({
        (0.0, 1.0): (
          (0.0, 1.0),
          (0.0, 1.5),
        ),
        (0.0, 1.5): (
          (0.0, 1.5),
        ),
      }.items(),),
      sorted(
        result.items(),
      ),
    )

if __name__ == '__main__':
  unittest.main()
