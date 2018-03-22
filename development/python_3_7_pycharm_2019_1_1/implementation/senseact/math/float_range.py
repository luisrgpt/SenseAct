def float_range(
    minimum,
    maximum,
    scale,
):

  while minimum <= maximum:

    yield minimum
    minimum = round(minimum + scale, 12)
