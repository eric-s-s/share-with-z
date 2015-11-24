'''printing and graphing functions for use with DiceTable class.
main functions are - grapher(), truncate_grapher(), fancy_grapher()
print_table() and stats()'''


import pylab

#helper function. used everywhere to make numbers look purty.
def scinote(num):
    '''checks a positive int or float.  outputs a string of the number.
    float(string) will give you the number.
    if number lower than scinonote_cutoff, no change.
    if number already in scientific notation, just prints first 4 digits
    else prints first four digits in scientific notation.'''
    scinote_cutoff = 10**6
    if num < scinote_cutoff:
        return str(num)
    elif 'e' in str(num):
        left, right = str(num).split('e')
        return left[0:5]+'e'+right
    else:
        string = str(int(num))
        power = str(len(string)-1)
        digits = string[0]+'.'+string[1:4]
        return digits+'e+'+power

#helper function for truncate_grapher() and stats()
def list_to_string(lst):
    '''outputs a list of intergers as a nice string.
    [1,2,3,7,9,10] becomes "1-3, 7, 9-10"
    [1,1,2,2,3] becomes "1-3"'''
    lst.sort()
    start_index = 0
    tuple_list = []
    for index in range(len(lst)-1):
        if lst[index+1]-lst[index] > 1:
            tuple_list.append((lst[start_index], lst[index]))
            start_index = index+1
    tuple_list.append((lst[start_index], lst[-1]))
    out_list = []
    for pair in tuple_list:
        if pair[0] == pair[1]:
            out_list.append(str(pair[0]))
        else:
            out_list.append(str(pair[0])+'-'+str(pair[1]))
    return ', '.join(out_list)

#helper function. currently used in print_table(), grapher()
#and truncate_grapher()
def justify_right(value, max_value):
    '''takes a roll, and the largest roll from a DiceTable.
    outputs a string of the roll with enough added spaces so that
    "roll:" and "max_roll:" will be the same number of characters.'''
    max_len = len(str(max_value))
    out_val = str(value)
    spaces = (max_len - len(out_val))*' '
    return spaces + out_val

#helper function that's really only useful for grapher and truncate_grapher
def graph_list(table):
    '''makes a list of tuples.  (roll-int, grapher output for roll-str).
    it's a helper function for grapher and truncate_grapher'''
    output_list = []

    max_frequency = table.frequency_highest()[1]
    max_value = table.values_max()
    max_graph_height = 80.0

    divisor = 1
    divstring = '1'
    #this sets the divisor so that max height of graph is MAX_GRAPH_HEIGHT x's
    if max_frequency > max_graph_height:
        divisor = max_frequency/table.int_or_float(max_graph_height)
        divstring = scinote(divisor)

    for value, frequency in table.frequency_all():
        num_of_xs = int(round(frequency/divisor))
        output_list.append((value,
                            justify_right(value, max_value) +':'+num_of_xs*'x'))

    output_list.append((None, 'each x represents '+divstring+' occurences'))
    return output_list

def print_table(table):
    '''input - DiceTable.  Prints all the rolls and their frequencies.'''
    max_value = table.values_max()
    for value, frequency in table.frequency_all():
        print justify_right(value, max_value) +':'+scinote(frequency)

def grapher(table, label = None):
    '''input = DiceTable. output = a graph of x's'''
    for output in graph_list(table):
        print output[1]
    print label

def truncate_grapher(table, label = None):
    '''input = DiceTable. output = a graph of x's
    but doesn't print zero-x rolls'''
    excluded = []
    for output in graph_list(table):
        if 'x' in output[1]:
            print output[1]
        else:
            excluded.append(output[0])
    if excluded != []:
        print 'not included: '+list_to_string(excluded).replace(',', ' and')
    print label

def fancy_grapher(table, figure=1, style='bo'):
    '''makes a pylab plot of a DiceTable.
    You can set other figures and styles'''
    x_axis = []
    y_axis = []
    factor = 1

    pylab.figure(figure)
    pylab.ylabel('number of occurences')
    #A work-around for the limitations of pylab.
    #It can't handle really fucking big ints and can't use my workarounds
    if isinstance(table.int_or_float(1), int):
        power = len(str(table.frequency_highest()[1])) - 5
        factor = 10**power
        pylab.ylabel('number of occurences times 10^'+str(power))

    for value, frequency in table.frequency_all():
        x_axis.append(value)
        y_axis.append(frequency/factor)

    pylab.xlabel('values')
    pylab.title('all the combinations for '+str(table))
    pylab.plot(x_axis, y_axis, style)
    pylab.draw()


def stats(table, values):
    '''returns the stats from a DiceTable for the rolls in the list, 'rolls'.'''
    all_combos = table.total_frequency()
    lst_frequency = 0
    for value in values:
        lst_frequency += table.roll_frequency(value)[1]

    if lst_frequency == 0:
        print 'no results'
        return None
    chance = table.divide(all_combos, lst_frequency, 4)
    pct = 100 * table.divide(lst_frequency, all_combos, 3)

    lst_frequency_str = scinote(lst_frequency)
    chance_str = scinote(chance)
    all_combos_str = scinote(all_combos)
    values_str = list_to_string(values)
    print
    print (values_str+' occurred '+lst_frequency_str+
           ' times out of a total of '+all_combos_str+
           ' possible combinations')
    #print 'if you roll '+str(table)+','
    print ('the chance of '+values_str+' is 1 in '+
           chance_str+' or '+str(pct)+' percent')
    print



#TODO delete.  for eval.
def stddevtst(table):
    avg = table.mean()
    sqs = 0
    count = 0
    for roll in table._table.keys():
        sqs += table._table[roll]*(((avg - roll)**2))
        count += table._table[roll]
    return round((sqs/count)**0.5, 4)

def stddeverr(table):
    accurate = stddevtst(table)
    approx = table.stddev()
    return 100*(accurate - approx)/accurate

def showit2(table):
    for count in range(100):
        table.add_a_die()
        print str(stddeverr(table))
def highest(table):
    return scinote(table.roll_frequency_highest()[1])
#TODO ends

