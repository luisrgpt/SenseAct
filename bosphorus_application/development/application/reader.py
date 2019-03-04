import time as timer
import csv
from ast import literal_eval

from uncertainty_use_cases.submarine import Parameters

start = timer.time()

with open('../share/cost_table_t_minus_' + str(
    Parameters.cost_table_quality) + '_minutes.csv', newline='') as csvfile:
  spamreader = csv.reader(
    csvfile,
    escapechar='\\',
    lineterminator='\n',
    delimiter=';',
    quoting=csv.QUOTE_NONE
  )
  cost_table = {}
  for row in spamreader:
    cost_table[literal_eval(row[0])] = literal_eval(row[1])

end = timer.time()
print(end - start)
