import unittest

from senseact.evaluation import get_claims

class GetClaims(unittest.TestCase):

  def test_something(self):
    result = get_claims(
      chromosome=(True, False, False, False, False),
      boundaries=(0.0, 4.0),
      extended_boundaries=(0.0, 4.0),
      amount=5,
      settings= {
        'probe': {
          'types': {
            1.0: None,
          }
        },
      },
    )
    self.assertEqual({0: 1, 1: -1}, result)

  def test_something_2(self):
    result = get_claims(
      chromosome=(True, False, False, False, False),
      boundaries=(-2.0, 2.0),
      extended_boundaries=(-2.0, 2.0),
      amount=5,
      settings= {
        'probe': {
          'types': {
            1.0: None,
          }
        },
      },
    )
    self.assertEqual({-2: 1, -1: -1}, result)

  def test_something_3(self):
    result = get_claims(
      chromosome=(True, False, True, False, False),
      boundaries=(-2.0, 2.0),
      extended_boundaries=(-2.0, 2.0),
      amount=5,
      settings= {
        'probe': {
          'types': {
            1.0: 1,
          }
        },
      },
    )
    self.assertEqual({-2: 1, -1.0: 0, 1.0: -1}, result)

  def test_something_4(self):
    result = get_claims(
      chromosome=(True, False, True, False, False),
      boundaries=(-2.0, 2.0),
      extended_boundaries=(-2.0, 2.0),
      amount=5,
      settings= {
        'probe': {
          'types': {
            0.5: None,
          }
        },
      },
    )
    self.assertEqual({-2: 1, -1.5: -1, -0.5: 1, 0.5: -1}, result)

  def test_something_5(self):
    result = get_claims(
      chromosome=(False,) * 47 + (False,) * 45 + (True,) + (False,),
      boundaries=(0.0, 41.0),
      extended_boundaries=(0.0, 46.0),
      amount=47,
      settings= {
        'probe': {
          'types': {
            3: None,
            5: None,
          }
        },
      },
    )
    self.assertEqual({40.0: 1, 41.0: -1}, result)

if __name__ == '__main__':
  unittest.main()
