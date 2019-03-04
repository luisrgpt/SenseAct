from typing import NewType, Tuple, List

Problem = NewType(
  'Problem',
  Tuple[
    Tuple[
      Tuple[int, bool],
      Tuple[int, bool]
    ],
    List[float]
  ]
)
