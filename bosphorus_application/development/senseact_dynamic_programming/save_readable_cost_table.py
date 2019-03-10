import csv

def save_readable_cost_table(cost_table, time):
  with open('../share/' + name + '_readable_cost_table_t_minus_' + str(
      time) + '_minutes.csv', 'w') as file:
    writer = csv.writer(
      file,
      escapechar='\\',
      lineterminator='\n',
      quoting=csv.QUOTE_NONE
    )
    writer.writerow(
      ['time till done', 'interval', 'probes', 'cost', 'probes', 'cost',
       'probes', 'cost',
       'probes',
       'cost', 'probes', 'cost'])
    for x, row_value in sorted(cost_table.items(), key=lambda x: x[0]):
      t, ((x_lower, x_open), (x_upper, x_closed)) = x
      i = (
        ('{' + str(x_lower) + '}')
        if not x_open and x_closed and x_lower == x_upper
        else
        (
            ('(' if x_open else '[') +
            str(float(x_lower)) + '..' + str(float(x_upper)) +
            (']' if x_closed else ')')
        )
      )
      writer.writerow([t] + [i] + [
        x
        for probes, cost in row_value
        for x in [' '.join([
          str(u) + '(' + ' '.join([str(pos) for pos in comb]) + ')'
          for u, comb in probes
        ]), cost]
      ])
