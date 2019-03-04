from typing import NewType, Tuple, Iterator

Claim = NewType(
  'Claim',
  Iterator[
    Tuple[int, int]
  ]
)
