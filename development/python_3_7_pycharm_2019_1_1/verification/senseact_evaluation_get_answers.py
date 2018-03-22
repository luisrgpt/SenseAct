import unittest

from senseact.evaluation import get_answers

class GetAnswers(unittest.TestCase):

  def test_something_1(self):
    result = get_answers(
      claims={0.0: 1, 1.0: -1},
      boundaries=(0, 4),
    )
    self.assertEqual(([((0.0, 1.0), 0.25)], [((1.0, 4.0), 0.75)]), result)

  def test_something_2(self):
    result = get_answers(
      claims={-2.0: 1, -1.0: -1},
      boundaries=(-2, 2),
    )
    self.assertEqual(([((-2.0, -1.0), 0.25)], [((-1.0, 2.0), 0.75)]), result)

  def test_something_3(self):
    result = get_answers(
      claims={-2.0: 1, -1.0: 0, 1.0: -1},
      boundaries=(-2, 2),
    )
    self.assertEqual(([((-2.0, -1.0), 0.25), ((-1.0, 1.0), 0.5)], [((1.0, 2.0), 0.25)]), result)

  def test_something_4(self):
    result = get_answers(
      claims={-2.0: 1, -1.5: -1, -0.5: 1, 0.5: -1},
      boundaries=(-2, 2),
    )
    self.assertEqual(([((-2.0, -1.5), 0.125), ((-0.5, 0.5), 0.25)], [((-1.5, -0.5), 0.25), ((0.5, 2.0), 0.375)]), result)

  def test_something_5(self):
    result = get_answers(
      claims={40.0: 1, 41.0: -1},
      boundaries=(0.0, 41.0),
    )
    self.assertEqual(([((40.0, 41.0), 0.024390243902439025)], [((0.0, 40.0), 0.975609756097561)]), result)

  def test_something_6(self):
    result = get_answers(
      claims={-1.0: 1, -0.5: -1, 1.0: 1, 2.0: -1},
      boundaries=(-2, 2),
    )
    self.assertEqual(([((-1.0, -0.5), 0.125), ((1.0, 2.0), 0.25)], [((-2.0, -1.0), 0.25), ((-0.5, 1.0), 0.375)]), result)

if __name__ == '__main__':
  unittest.main()
