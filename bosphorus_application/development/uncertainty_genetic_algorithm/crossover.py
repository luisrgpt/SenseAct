from random import randint

def crossover(
    chromosome_1: list,
    chromosome_2: list
):
  # Check if both chromosomes are identical
  if chromosome_1 == chromosome_2:
    return

  # Identify first difference
  min_point = None
  for min_point, _ in enumerate(chromosome_1):
    if chromosome_1[min_point] != chromosome_2[min_point]:
      break

  # Identify last difference
  max_point = None
  for max_point in range(len(chromosome_1) - 1, -1, -1):
    if chromosome_1[max_point] != chromosome_2[max_point]:
      break

  # Check if both chromosomes differ at one and only one gene
  if min_point == max_point:
    return

  cx_point = randint(min_point, max_point)
  chromosome_1[cx_point:], chromosome_2[cx_point:] = chromosome_2[
                                                     cx_point:], chromosome_1[
                                                                 cx_point:]
