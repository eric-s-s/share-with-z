"""for all things dicey."""
from __future__ import absolute_import

from dicetables.baseevents import AdditiveEvents, IntegerEvents


class ProtoDie(IntegerEvents):
    """
    base object for any kind of die.


    :all Die objects need: get_size(), get_weight(), weight_info(), multiply_str(), all_events
    :all_events: must be sorted and have no zero occurrences.

    """
    def __init__(self):
        super(ProtoDie, self).__init__()

    def get_size(self):
        raise NotImplementedError

    def get_weight(self):
        raise NotImplementedError

    @property
    def all_events(self):
        raise NotImplementedError

    def weight_info(self):
        """return detailed info of how the die is weighted"""
        raise NotImplementedError

    def multiply_str(self, number):
        """return a string that is the die string multiplied by a number. i.e.,
        D6+1 times 3 is '3D6+3' """
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __hash__(self):
        return hash('hash of {!r}, {}, {}, {}'.format(self,
                                                      self.get_size(),
                                                      self.get_weight(),
                                                      self.all_events))

    def __lt__(self, other):
        return (
            (self.get_size(), self.get_weight(), self.all_events, repr(self)) <
            (other.get_size(), other.get_weight(), other.all_events, repr(other))
        )

    def __eq__(self, other):
        return (
            (self.get_size(), self.get_weight(), self.all_events, repr(self)) ==
            (other.get_size(), other.get_weight(), other.all_events, repr(other))
        )

    def __ne__(self, other):
        return not self == other

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return self == other or self > other


class Die(ProtoDie):
    """
    stores and returns info for a basic Die.
    Die(4) rolls 1, 2, 3, 4 with equal weight
    """
    def __init__(self, die_size):
        """

        :param die_size: int > 0
        """
        self._die_size = die_size
        self._weight = 0
        super(Die, self).__init__()

    def get_size(self):
        return self._die_size

    def get_weight(self):
        return self._weight

    @property
    def all_events(self):
        return [(value, 1) for value in range(1, self._die_size + 1)]

    def weight_info(self):
        return str(self) + '\n    No weights'

    def multiply_str(self, number):
        return '{}{}'.format(number, self)

    def __str__(self):
        return 'D{}'.format(self._die_size)

    def __repr__(self):
        return 'Die({})'.format(self.get_size())


class ModDie(Die):
    """
    stores and returns info for a Die with a modifier
    that changes the values of the rolls.
    ModDie(4, -1) rolls 0, 1, 2, 3 with equal weight
    """
    def __init__(self, die_size, modifier):
        """

        :param die_size: int >0
        :param modifier: int
        """
        self._mod = modifier
        super(ModDie, self).__init__(die_size)

    def get_modifier(self):
        return self._mod

    @property
    def all_events(self):
        return [(value + self._mod, 1)
                for value in range(1, self._die_size + 1)]

    def multiply_str(self, number):
        return '{}D{}{:+}'.format(number, self._die_size, number * self._mod)

    def __str__(self):
        return 'D{0}{1:+}'.format(self._die_size, self._mod)

    def __repr__(self):
        return 'ModDie({}, {})'.format(self.get_size(), self.get_modifier())


class WeightedDie(ProtoDie):
    def __init__(self, dictionary_input):
        """
        stores and returns info for die with different chances for different rolls.
        WeightedDie(1:1, 2:5} rolls 1 once for every five times that 2 is rolled.

        :param dictionary_input: {roll: weight} roll: int, weight: int>=0\n
            the sum of all weights >0
        """
        self._dic = dictionary_input.copy()

        self._die_size = max(self._dic.keys())
        self._weight = sum(self._dic.values())
        super(WeightedDie, self).__init__()

    def get_size(self):
        return self._die_size

    def get_weight(self):
        return self._weight

    @property
    def all_events(self):
        return sorted([pair for pair in self._dic.items() if pair[1]])

    def weight_info(self):
        num_len = len(str(self.get_size()))
        out = str(self) + '\n'
        for roll in range(1, self._die_size + 1):
            out += ('    a roll of {:>{}} has a weight of {}\n'
                    .format(roll, num_len, self._dic.get(roll, 0)))
        return out.rstrip('\n')

    def multiply_str(self, number):
        return '{}{}'.format(number, self)

    def __str__(self):
        return 'D{}  W:{}'.format(self._die_size, self._weight)

    def __repr__(self):
        new_dic = {}
        for roll in range(1, self.get_size() + 1):
            new_dic[roll] = self._dic.get(roll, 0)
        return 'WeightedDie({})'.format(new_dic)


class ModWeightedDie(WeightedDie):

    def __init__(self, dictionary_input, modifier):
        """
        stores and returns info for die with different chances for different rolls.
        The modifier changes the value of the rolls.
        ModWeightedDie({1:1, 2:5}, -1) rolls 0once for every five times that 1 is rolled.

        :param dictionary_input: {roll: weight} roll: int, weight: int>=0\n
            sum of all weights >0
        :param modifier: int
        """
        self._mod = modifier
        super(ModWeightedDie, self).__init__(dictionary_input)

    def get_modifier(self):
        """returns the modifier on the die"""
        return self._mod

    @property
    def all_events(self):
        return sorted([(roll + self._mod, weight) for roll, weight in self._dic.items() if weight])

    def multiply_str(self, number):
        return '{0}D{1}{2:+}  W:{3}'.format(number, self._die_size,
                                            number * self._mod, self._weight)

    def __str__(self):
        return 'D{0}{1:+}  W:{2}'.format(self._die_size, self._mod, self._weight)

    def __repr__(self):
        to_fix = super(ModWeightedDie, self).__repr__()[:-1]
        return 'Mod' + to_fix + ', {})'.format(self.get_modifier())


class StrongDie(ProtoDie):

    def __init__(self, input_die, multiplier):
        """
        StrongDie(ModDie(3, -1), 2) would make a
        D3-1 with twice the influence of a regular die.  so it would roll
        0, 2, 4.  die_size=input_die.get_size(), weight=input_die.get_weight().

        :param input_die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or subclass of ProtoDie
        :param multiplier: int >=1
        """
        self._original = input_die
        self._multiply = multiplier
        super(StrongDie, self).__init__()

    def get_size(self):
        return self.get_original().get_size()

    def get_weight(self):
        return self._original.get_weight()

    def get_multiplier(self):
        return self._multiply

    def get_original(self):
        """returns an instance of the original die"""
        return self._original

    @property
    def all_events(self):
        old = self._original.all_events
        return [(pair[0] * self.get_multiplier(), pair[1]) for pair in old]

    def weight_info(self):
        return (self._original.weight_info().replace(
            str(self._original), str(self)))

    def multiply_str(self, number):
        """return the str of die times a number. 5, (D6+3)X3 --> (5D6+15)X3"""
        return '({})X{}'.format(self.get_original().multiply_str(number),
                                self.get_multiplier())

    def __str__(self):
        return '({})X{}'.format(self.get_original(), self.get_multiplier())

    def __repr__(self):
        return 'StrongDie({!r}, {})'.format(self.get_original(),
                                            self.get_multiplier())


class DiceTable(AdditiveEvents):
    """this is an AdditiveEvents with a list that holds information about the dice
    added to it and removed from it."""

    def __init__(self):
        super(DiceTable, self).__init__({0: 1})
        self._dice_list = {}

    def update_list(self, add_number, new_die):
        """

        :param add_number: can be negative but should not reduce Die count below zero
        :type add_number: int
        :param new_die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        :type new_die: ProtoDie
        :return:
        """
        self._dice_list[new_die] = self._dice_list.get(new_die, 0) + add_number
        if self._dice_list[new_die] == 0:
            del self._dice_list[new_die]

    def get_list(self):
        """return copy of dice list. a list of tuples, (die, number of dice)"""
        return sorted(self._dice_list.items())

    def number_of_dice(self, query_die):
        """returns the number of that die in the dice list, or zero if not in
        the list"""
        return self._dice_list.get(query_die, 0)

    def weights_info(self):
        """return detailed info of dice in the list"""
        out_str = ''
        for die, number in self.get_list():
            adjusted = die.weight_info().replace(str(die),
                                                 die.multiply_str(number))
            out_str += adjusted + '\n\n'
        return out_str.rstrip('\n')

    def __str__(self):
        out_str = ''
        for die, number in self.get_list():
            out_str += '{}\n'.format(die.multiply_str(number))
        return out_str.rstrip('\n')

    def add_die(self, num, die):
        """

        :param num: >= 0
        :type num: int
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        :type die: ProtoDie
        :raises: dicetables.InvalidEventsError
        :return:
        """
        self.combine(num, die)
        self.update_list(num, die)

    def raise_error_for_too_many_removes(self, num, die):
        if self.number_of_dice(die) < num:
            raise ValueError('dice not in table, or removed too many dice')

    def remove_die(self, num, die):
        """

        :param num: >=0, must be at least that many dice of that kind in table
        :type num: int
        :param die: Die, ModDie, WeightedDie, ModWeightedDie, StrongDie or new ProtoDie subclass
        :type die: ProtoDie
        :raises: ValueError, dicetables.InvalidEventsError
        :return:
        """
        self.raise_error_for_too_many_removes(num, die)
        self.remove(num, die)
        self.update_list(-1 * num, die)

