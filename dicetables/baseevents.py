""" this module contains the class LongIntTable and longintmath that the table
needs to deal with it's BFN"""
from decimal import Decimal
from math import log10
from sys import version_info

from tools.dictcombiner import DictCombiner

CONVERSIONS = {'LongIntTable.add()': 'AdditiveEvents.combine()',
               'LongIntTable.frequency()': 'AdditiveEvents.get_event()',
               'LongIntTable.frequency_all()': 'AdditiveEvents.all_events',
               'LongIntTable.frequency_highest()': 'AdditiveEvents.biggest_event',
               'LongIntTable.frequency_range()': 'AdditiveEvents.get_range_of_events()',
               'LongIntTable.mean()': 'AdditiveEvents.mean()',
               'LongIntTable.merge()': 'GONE',
               'LongIntTable.remove()': 'AdditiveEvents.remove()',
               'LongIntTable.stddev()': 'AdditiveEvents.stddev()',
               'LongIntTable.total_frequency()': 'AdditiveEvents.total_occurrences',
               'LongIntTable.update_frequency()': 'GONE',
               'LongIntTable.update_value_add()': 'GONE',
               'LongIntTable.update_value_ow()': 'GONE',
               'LongIntTable.values()': 'AdditiveEvents.event_keys',
               'LongIntTable.values_max()': 'AdditiveEvents.event_range[0]',
               'LongIntTable.values_min()': 'AdditiveEvents.event_range[1]',
               'LongIntTable.values_range()': 'AdditiveEvents.event_range',
               'scinote()': ('format_number()', 'NumberFormatter.format()'),
               }


def _convert_decimal_to_float_or_int(num):
    answer_as_float = float(num)
    if answer_as_float == float('inf') or answer_as_float == float('-inf'):
        return int(num)
    else:
        return answer_as_float


def safe_true_div(numerator, denominator):
    """floating point division for any sized number"""
    ans = Decimal(numerator) / Decimal(denominator)
    return _convert_decimal_to_float_or_int(ans)


class InvalidEventsError(ValueError):
    def __init__(self, message='', *args, **kwargs):
        super(InvalidEventsError, self).__init__(message, *args, **kwargs)
        

class InputVerifier(object):
    def __init__(self):
        self._int_tuple = (int,)
        self._type_str = 'ints'
        if version_info[0] < 3:
            self._int_tuple += (long, )
            self._type_str += ' or longs'

    def verify_all_events(self, all_events):
        """

        :param all_events: IntegerEvents.all_events
        :raises: InvalidEventsError
        """
        if not all_events:
            raise InvalidEventsError('events may not be empty. a good alternative is the identity - [(0, 1)].')
        if not self.is_all_ints(all_events.keys()) or not self.is_all_ints(all_events.values()):
            raise InvalidEventsError('all values must be {}'.format(self._type_str))
        if any(occurrence <= 0 for occurrence in all_events.values()):
            raise InvalidEventsError('no negative or zero occurrences in Events.all_events')

    def is_int(self, number):
        return isinstance(number, self._int_tuple)

    def is_all_ints(self, iterable):
        return all(self.is_int(value) for value in iterable)

    @staticmethod
    def is_sorted(iterable):
        return list(iterable) == sorted(iterable)


class IntegerEvents(object):
    def __init__(self):
        InputVerifier().verify_all_events(self.get_dict())

    def get_dict(self):
        """

        :return: sorted([(event, occurrence) .. ] if occurrence != 0)
        """
        message = ('all_events must return a SORTED tuple list of\n' +
                   '[(event, occurrences),  ...] event=int, occurrence=int>0.')
        raise NotImplementedError(message)


def scrub_zeroes(dictionary):
    return dict([item for item in dictionary.items() if item[1]])


class AdditiveEvents(IntegerEvents):
    def __init__(self, events_dictionary):
        """

        :param events_dictionary: {event: occurrences}\n
            event=int. occurrences=int >=0
            total occurrences > 0
        """
        self._table = scrub_zeroes(events_dictionary)
        super(AdditiveEvents, self).__init__()

    @property
    def event_keys(self):
        return sorted(self._table.keys())

    @property
    def event_range(self):
        all_keys = self.event_keys
        return all_keys[0], all_keys[-1]

    @property
    def all_events(self):
        return sorted(self._table.items())
        # return [pair for pair in self._table.items() if pair[1]]

    @property
    def biggest_event(self):
        """

        :return: (event, occurrences) for first event with highest occurrences
        """
        highest_occurrences = max(self._table.values())
        for event in sorted(self._table.keys()):
            if self._table[event] == highest_occurrences:
                return event, highest_occurrences

    @property
    def total_occurrences(self):
        all_occurrences = self._table.values()
        return sum(all_occurrences)

    def get_event(self, event):
        return event, self._table.get(event, 0)

    def get_range_of_events(self, start, stop_before):
        return [self.get_event(event) for event in range(start, stop_before)]

    def __str__(self):
        return 'table from {} to {}'.format(*self.event_range)

    def mean(self):
        numerator = sum([value * freq for value, freq in self._table.items()])
        denominator = self.total_occurrences
        return safe_true_div(numerator, denominator)

    def stddev(self, decimal_place=4):
        avg = self.mean()
        extra_digits = 5
        largest_exponent = int(log10(self.biggest_event[1]))
        required_exp_for_accuracy = 2 * (extra_digits + decimal_place)
        if largest_exponent < required_exp_for_accuracy:
            factor_to_truncate_digits = 1
        else:
            factor_to_truncate_digits = 10 ** (largest_exponent - required_exp_for_accuracy)
        truncated_deviations = 0
        total_occurrences = self.total_occurrences
        for event_value, occurrences in self._table.items():
            truncated_deviations += (occurrences // factor_to_truncate_digits) * (avg - event_value) ** 2.
        truncated_total_occurrences = total_occurrences // factor_to_truncate_digits
        return round((truncated_deviations / truncated_total_occurrences) ** 0.5, decimal_place)

    def get_dict(self):
        return self._table.copy()

    def combine(self, times, events):
        combiner = DictCombiner(self.get_dict())
        dictionary = combiner.combine_by_fastest(times, events.get_dict()).get_dict()
        self._table = dictionary

    def combine_by_flattened_list(self, times, events):
        """

        :WARNING - UNSAFE METHOD: len(flattened_list) = total occurrences of events.
            if this list is too big, it will raise MemoryError or OverflowError
        """
        combiner = DictCombiner(self.get_dict())
        dictionary = combiner.combine_by_flattened_list(times, events.get_dict()).get_dict()
        self._table = dictionary

    def combine_by_dictionary(self, times, events):
        combiner = DictCombiner(self.get_dict())
        dictionary = combiner.combine_by_dictionary(times, events.get_dict()).get_dict()
        self._table = dictionary

    def combine_by_indexed_values(self, times, events):
        combiner = DictCombiner(self.get_dict())
        dictionary = combiner.combine_by_indexed_values(times, events.get_dict()).get_dict()
        self._table = dictionary

    def remove(self, times, events):
        """

        :WARNING - UNSAFE METHOD: There is no record of what you added to an AdditiveEvents.
            If you remove what you haven't added, no error will be raised, but you will have bugs.
        """
        combiner = DictCombiner(self.get_dict())
        dictionary = combiner.remove_by_tuple_list(times, events.get_dict()).get_dict()
        self._table = dictionary
