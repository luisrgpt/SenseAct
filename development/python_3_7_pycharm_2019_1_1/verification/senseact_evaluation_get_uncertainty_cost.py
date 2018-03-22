import unittest

from senseact.evaluation import get_uncertainty_cost

class GetUncertaintyCost(unittest.TestCase):

  def test_something_1(self):
    result = get_uncertainty_cost(
      uncertainty=(((0.0, 1.0), 0.25),),
      cost_table={
        (-2.0, 3.0): { (): 100 },
      },
      settings = {
        'alert': {
          'types': [
            (
              (0.5, 1.5),
              200,
            ),
            (
              (0.0, 0.5),
              0,
            ),
            (
              (1.5, 5.5),
              0,
            ),
          ]
        },
        'target': {
          'speed': 2,
        },
      },
    )
    self.assertEqual(75, result)

  def test_something_2(self):
    result = get_uncertainty_cost(
      uncertainty=(((-2.0, -1.0), 0.25),),
      cost_table={
        (-4.0, 1.0): { (): 200 },
      },
      settings={
        'alert': {
          'types': [
            (
              (0.5, 1.5),
              300,
            ),
            (
              (-2.0, 0.5),
              0,
            ),
            (
              (1.5, 5.5),
              0,
            ),
          ]
        },
        'target': {
          'speed': 2,
        },
      },
    )
    self.assertEqual(50, result)

  def test_something_3(self):
    result = get_uncertainty_cost(
      uncertainty=(((-2.0, -1.0), 0.25), ((-1.0, 1.0), 0.5)),
      cost_table={
        (-3.5, 0.5): { (): 100 },
        (-2.5, 2.5): { (): 100 },
      },
      settings={
        'alert': {
          'types': [
            (
              (0.5, 1.5),
              200,
            ),
            (
              (-2.0, 0.5),
              0,
            ),
            (
              (1.5, 5.5),
              0,
            ),
          ]
        },
        'target': {
          'speed': 1.5,
        },
      },
    )
    self.assertEqual(225, result)

  def test_something_4(self):
    result = get_uncertainty_cost(
      uncertainty=(((-2.0, -1.5), 0.125), ((-0.5, 0.5), 0.25)),
      cost_table={
        (-2.75, -0.75): { (): 100 },
        (-1.25, 1.25): { (): 100 },
      },
      settings={
        'alert': {
          'types': [
            (
              (0.0, 1.5),
              200,
            ),
            (
              (-2.0, 0.0),
              0,
            ),
            (
              (1.5, 5.5),
              0,
            ),
          ],
        },
        'target': {
          'speed': 0.75,
        },
      },
    )
    self.assertEqual(112.5, result)

if __name__ == '__main__':
  unittest.main()
