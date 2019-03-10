import csv

def save_cost_table(cost_table):
  with open('../share/cost_table_' + name + '.csv', 'w') as file:
    writer = csv.writer(
      file,
      escapechar='\\',
      lineterminator='\n',
      delimiter=';',
      quoting=csv.QUOTE_NONE
    )
    for c, row_value in sorted(cost_table.items(), key=lambda x: x[0]):
      writer.writerow([c, row_value])
