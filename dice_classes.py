'''for all things dicey.  this contains DiceInfo and DiceTable and add_dice.'''
from longinttable import LongIntTable

class DiceInfo(object):
    '''dice info is an object that stores and returns info on a set of dice.
    it has the number, kind, weight info for a weighted die'''
    def __init__(self, num, size):
        '''num is a positive int. size can be an int, as in, six makes a D6.
        for a weighted die, input a list of values, or a dictionary or a list
        of tuples.  [1,1,1,2,3], {1:3, 2:1, 3:1} and [(1,3), (2,1), (3,1)] all
        create a D3 that rolls a one 3 times more than a two or a three.'''
        if isinstance(size, int):
            self._dic = dict((val, 1) for val in range(1,size+1))
            self._size = size
            self._num = num
        else:
            self._dic = self._make_dic(size)
            temp_size = self._dic.keys()
            temp_size.sort()
            self._size = temp_size[-1]
            self._num = num
        weight = sum(self._dic.values()) 
        if len(self._dic.keys()) == weight:
            self._weight = None
        else:
            self._weight = weight 
            
    def _make_dic(self, lst):
        '''turns any appropriate die representation into a dictionary'''
        if isinstance(lst, dict):
            return lst
        if isinstance(lst[0], int):
            out = {}
            for val in lst:
                out[val] = out.get(val, 0) + 1
            return out
        else:
            return dict((val, freq) for val, freq in lst)
    def get_num(self):
        '''returns the number of dice recorded'''
        return self._num
    def get_size(self):
        '''returns the size of the die'''
        return self._size
    def get_dic(self):
        '''returns the dictionary that is the dice values'''
        return self._dic        
    def get_weight(self):
        '''returns the weight of the die'''
        return self._weight
    def weight_info(self):
        '''prints out detailed weight info'''
        print self
        if self._weight == None:
            print '    No weights\n'
        else:
            for val, freq in self._dic.items():
                print ('    a roll of %s has a weight of %s' % (val, freq))
            
    def add_num(self, num):
        '''increases the number of dice recorded'''
        self._num += num
    def __lt__(self, other):
        if self.get_size() != other.get_size():
            if self.get_size() < other.get_size():
                return True
            else:
                return False
        else:
            if self.get_weight() < other.get_weight():
                return True
            else:
                return False
    def __eq__(self, other):
        if self.get_dic() == other.get_dic():
            return True
        else:
            return False
    def __str__(self):
        out = '%sD%s' % (self._num, self._size)
        if self._weight == None:
            return out
        else:
            return out + ' W: %s' % (self._weight)
            
class DiceTable(LongIntTable):
    '''this is a LongIntTable with a list that holds information about the dice
    added to it.'''
    def __init__(self, dic = {0:1}, dice_list = []):
        LongIntTable.__init__(self, dic)
        self._dice_list = dice_list
        self._dice_list.sort()
        self._last_die = None
        
    def update_list(self, new_dice_info):
        '''adds new dice info to the list. if the new dice is the same as an
        old one, just adds the number instead. makes this die's dict. the 
        last die added.'''
        done = False
        for dice_info in self._dice_list:
            if new_dice_info == dice_info:
                dice_info.add_num(new_dice_info.get_num())
                done = True
                break
        if not done:
            self._dice_list.append(new_dice_info)
        self._dice_list.sort()
        self._last_die = new_dice_info.get_dic()
    def get_list(self):
        '''return the dice list'''
        return self._dice_list
    def get_last(self):
        '''return the dict of the last die added'''
        return self._last_die
    def weights_info(self):
        '''prints detailed info of dice in the list'''
        for dice_info in self._dice_list:
            dice_info.weight_info()
    def __str__(self):
        out_str = ''
        for dice_info in self._dice_list:
            out_str = out_str + str(dice_info) + '\n'
        return out_str.rstrip('\n')

def add_dice(table, num = 1, size = 'last'):
    '''uses num and size to make a DiceInfo.  updates the table's list and uses
    the DiceInfo dict to call LongIntTable.add() on the table'''
    if size == 'last':
        size = table.get_last()
    dice_to_add = DiceInfo(num, size)
    table.update_list(dice_to_add)
    table.add(num, dice_to_add.get_dic())