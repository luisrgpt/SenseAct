import csv

def save_groupings(proximity_groups, extrapolation_groups, time):
  with open('../share/' + name + '_bla' + str(time) + '.csv', 'w') as file:
    writer = csv.writer(
      file,
      escapechar='\\',
      lineterminator='\n',
      quoting=csv.QUOTE_NONE
    )
    for ((x_lower, x_open), (x_upper, x_closed)), x in sorted(
        extrapolation_groups.items(), key=lambda x: x[0]):
      a = (
        ('{' + str(x_lower) + '}')
        if not x_open and x_closed and x_lower == x_upper
        else
        ('(' if x_open else '[') +
        str(float(x_lower)) + '..' + str(float(x_upper)) +
        (']' if x_closed else ')')
      )
      # print(a + ' -> ' + str(x))
      x = [
        (
          ('{' + str(x_lower) + '}')
          if not x_open and x_closed and x_lower == x_upper
          else
          ('(' if x_open else '[') +
          str(float(x_lower)) + '..' + str(float(x_upper)) +
          (']' if x_closed else ')')
        )
        for ((x_lower, x_open), (x_upper, x_closed)) in x
      ]
      writer.writerow([a] + x)
  with open('../share/' + name + '_ble' + str(time) + '.csv', 'w') as file:
    writer = csv.writer(
      file,
      escapechar='\\',
      lineterminator='\n',
      quoting=csv.QUOTE_NONE
    )
    for x in proximity_groups:
      x = [
        (
          ('{' + str(x_lower) + '}')
          if not x_open and x_closed and x_lower == x_upper
          else
          ('(' if x_open else '[') +
          str(float(x_lower)) + '..' + str(float(x_upper)) +
          (']' if x_closed else ')')
        )
        for ((x_lower, x_open), (x_upper, x_closed)) in x
      ]
      writer.writerow(x)
