import unittest

from senseact.dynamic_programming import store_well_known_costs

class StoreWellKnownCosts(unittest.TestCase):

  def test_something_1(self):
    result = store_well_known_costs(
      cost_table={
        (-1.5, 2.5): { (): 100 },
        (-1.5, 3.0): { (): 150 },
        (-1.5, 3.5): { (): 100 },
        (-1.0, 3.0): { (): 100 },
        (-1.0, 3.5): { (): 100 },
        (-0.5, 3.5): { (): 100 },
        (-2.0, 2.0): { (): 100 },
        (-2.0, 2.5): { (): 101 },
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
            )
          )
        },
        'boundaries': (0.0, 1.5),
        'scale': 0.5,
        'target': {
          'speed': 2,
        },
      },
    )
    self.assertEqual(
      sorted({
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
      }.items()),
      sorted(result.items()),
    )

if __name__ == '__main__':
  unittest.main()
