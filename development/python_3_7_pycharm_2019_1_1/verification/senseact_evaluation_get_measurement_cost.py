import unittest

from senseact.evaluation import get_measurement_cost

class GetMeasurementCost(unittest.TestCase):

  def test_something_1(self):
    result = get_measurement_cost(
      chromosome=[True, False, False, False, False],
      amount=5,
      settings={
        'probe': {
          'types': {
            1.0: 5
          },
        },
      },
    )
    self.assertEqual(5, result)

  def test_something_2(self):
    result = get_measurement_cost(
      chromosome=[True, False, False, False, False],
      amount=5,
      settings={
        'probe': {
          'types': {
            1.0: 10
          },
        },
      },
    )
    self.assertEqual(10, result)

  def test_something_3(self):
    result = get_measurement_cost(
      chromosome=[True, False, True, False, False],
      amount=5,
      settings={
        'probe': {
          'types': {
            1.0: 0.75
          },
        },
      },
    )
    self.assertEqual(1.5, result)

  def test_something_4(self):
    result = get_measurement_cost(
      chromosome=[True, False, True, False, False],
      amount=5,
      settings={
        'probe': {
          'types': {
            0.5: 2
          },
        },
      },
    )
    self.assertEqual(4, result)


if __name__ == '__main__':
  unittest.main()
