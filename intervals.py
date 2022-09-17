interval_1 = [0, 2]
interval_2 = [1, 3]

intervals = [ interval_2, interval_1 ]
new_intervals = []
intervals.sort( key= lambda i: i[0] )
if intervals[1][1] < intervals[0][1]:
    if intervals[1][0] == intervals[0][0]:
        new_intervals.append( [intervals[1][1], intervals[0][1] ] )
    else:
        new_intervals.append( [intervals[0][0], intervals[1][0] ] )
        new_intervals.append( [intervals[1][1], intervals[0][1] ] )
