import unittest

from senseact.evaluation import evaluate

class Evaluate(unittest.TestCase):

  def test_something_1(self):
    result = evaluate(
      population={
        (True, False, False, False, False),
      },
      boundaries=(0.0, 4.0),
      extended_boundaries=(0.0, 4.0),
      amount=5,
      cost_table={
        (-2.0, 3.0): { (): 100 },
        (-1.0, 6.0): { (): 100 },
      },
      settings={
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
        'probe': {
          'types': {
            1.0: 5,
          },
        },
        'target': {
          'speed': 2,
        },
      },
    )
    self.assertEqual(
      {
        (True, False, False, False, False): 75 + (75 * 3) + 5,
      },
      result)

  def test_something_2(self):
    result = evaluate(
      population={
        (True, False, False, False, False),
      },
      boundaries=(-2.0, 2.0),
      extended_boundaries=(-2.0, 2.0),
      amount=5,
      cost_table={
        (-4.0, 1.0): { (): 200 },
        (-3.0, 4.0): { (): 200 },
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
          ],
        },
        'probe': {
          'types': {
            1.0: 10,
          },
        },
        'target': {
          'speed': 2,
        },
      },
    )
    self.assertEqual(
      {
        (True, False, False, False, False): 50 + (50 * 3 + 300 * 0.75) + 10,
      },
      result,
    )

  def test_something_3(self):
    result = evaluate(
      population={
        (True, False, True, False, False),
      },
      boundaries=(-2.0, 2.0),
      extended_boundaries=(-2.0, 2.0),
      amount=5,
      cost_table={
        (-3.5, 0.5): { (): 100 },
        (-2.5, 2.5): { (): 100 },
        (-0.5, 3.5): { (): 100 },
      },
      settings={
        'alert': {
          'types': (
            (
              (1.0, 1.5),
              200
            ),
            (
              (-2.0, 0.5),
              0
            ),
            (
              (1.5, 5.5),
              0
            ),
          ),
        },
        'probe': {
          'types': {
            1.0: 0.75
          },
        },
        'target': {
          'speed': 1.5
        },
      },
    )
    self.assertEqual(
      {
        (True, False, True, False, False): 175 + 75 + 1.5,
      },
      result,
    )

  def test_something_4(self):
    result = evaluate(
      population={
        (True, False, True, False, False),
      },
      boundaries=(-2.0, 2.0),
      extended_boundaries=(-2.0, 2.0),
      amount=5,
      cost_table={
        (-2.75, -0.75): { (): 100 },
        (-2.25, 0.25): { (): 100 },
        (-1.25, 1.25): { (): 100 },
        (-0.25, 2.75): { (): 100 },
      },
      settings={
        'alert': {
          'types': (
            (
              (0.5, 1.5),
              200
            ),
            (
              (-2.0, 0.5),
              0
            ),
            (
              (1.5, 5.5),
              0
            ),
          ),
        },
        'probe': {
          'types': {
            0.5: 2
          },
        },
        'target': {
          'speed': 0.75
        },
      },
    )
    self.assertEqual(
      {
        (True, False, True, False, False): 87.5 + 0.25 * (100 + 200) + 0.375 * (100 + 200) + 4,
      },
      result,
    )

  def test_something_5(self):
    result = evaluate(
      population={
        (False,) * 47 + (False,) * 45 + (True,) + (False,),
      },
      boundaries=(0.0, 41.0),
      extended_boundaries=(0.0, 46.0),
      amount=47,
      cost_table={
        (x, y): { (): 0 }
        for x in float_range(
          minimum=-1.0,
          maximum=101.0,
          scale=1,
        )
        for y in float_range(
          minimum=x,
          maximum=101.0,
          scale=1,
        )
      },
      settings={
        'alert': {
          'types': [
            (
              (40.0, 45.0),
              1000
            ),
            (
              (45.0, 70.0),
              50
            ),
            (
              (0.0, 40.0),
              0
            ),
            (
              (45.0, 45.0),
              0
            ),
            (
              (70.0, 100),
              0
            ),
          ]
        },
        'boundaries': (0.0, 100.0),
        'scale': 1,
        'probe': {
          'types': {
            3: 10,
            5: 1,
          },
        },
        'target': {
          'speed': 1,
        },
        'time': 1,
      },
    )
    self.assertEqual(
      {
        (False,) * 47 + (False,) * 45 + (True,) + (False,): 25.390243902439025,
      },
      result,
    )

  def test_something_6(self):
    population = [False,] * 48 * 2
    population[42 + 5 + 1 + 34] = True
    population[42 + 5 + 1 + 45] = True
    result = evaluate(
      population={
        tuple(population),
      },
      boundaries=(0.0, 42.0),
      extended_boundaries=(0.0, 47.0),
      amount=48,
      cost_table={
        (x, y): { (): 0 }
        for x in float_range(
          minimum=-1.0,
          maximum=101.0,
          scale=1,
        )
        for y in float_range(
          minimum=x,
          maximum=101.0,
          scale=1,
        )
      },
      settings={
        'alert': {
          'types': [
            (
              (40.0, 45.0),
              1000
            ),
            (
              (45.0, 70.0),
              50
            ),
            (
              (0.0, 40.0),
              0
            ),
            (
              (45.0, 45.0),
              0
            ),
            (
              (70.0, 100),
              0
            ),
          ]
        },
        'boundaries': (0.0, 100.0),
        'scale': 1,
        'probe': {
          'types': {
            3: 10,
            5: 1,
          },
        },
        'target': {
          'speed': 1,
        },
        'time': 1,
      },
    )
    self.assertEqual(
      {
        tuple(population): 49.61904761904761,
      },
      result,
    )

  def test_something_7(self):
    population = [False,] * 48 * 2
    population[42 + 5 + 1 + 38] = True
    population[42 + 5 + 1 + 43] = True
    result = evaluate(
      population={
        tuple(population),
      },
      boundaries=(0.0, 42.0),
      extended_boundaries=(0.0, 47.0),
      amount=48,
      cost_table={
        (x, y): { (): 0 }
        for x in float_range(
          minimum=-1.0,
          maximum=101.0,
          scale=1,
        )
        for y in float_range(
          minimum=x,
          maximum=101.0,
          scale=1,
        )
      },
      settings={
        'alert': {
          'types': [
            (
              (40.0, 45.0),
              1000
            ),
            (
              (45.0, 70.0),
              50
            ),
            (
              (0.0, 40.0),
              0
            ),
            (
              (45.0, 45.0),
              0
            ),
            (
              (70.0, 100),
              0
            ),
          ]
        },
        'boundaries': (0.0, 100.0),
        'scale': 1,
        'probe': {
          'types': {
            3: 10,
            5: 1,
          },
        },
        'target': {
          'speed': 1,
        },
        'time': 1,
      },
    )
    self.assertEqual(
      {
        tuple(population): 97.23809523809523,
      },
      result,
    )

if __name__ == '__main__':
  unittest.main()
