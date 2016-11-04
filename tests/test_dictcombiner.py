import unittest

from dicetables.tools.dictcombiner import flatten_events_tuples, get_best_key, get_indexed_values_min, DictCombiner


class TestDictCombiner(unittest.TestCase):
    def setUp(self):
        self.identity_combiner = DictCombiner({0: 1})

    def tearDown(self):
        del self.identity_combiner

    """
    the next several tests show how DictCombiner.get_fastest_method works.  The edge cases to choose between
    methods were determined empirically.  To see how they were derived see time_trials/flattenedlist_timetrials.py
    and time_trials/indexedvalues_timetrials.py.  Those modules require numpy and matplotlib where the actual
    project does not.  Before running either one, under "if __name__ == '__main__':" make sure to comment in
    the UI you wish to use.  The full data set for determining whether to use indexed_values is this:
        choices = {'flattened_list': {
        2: {10: 200,  20: 100,  100: 50,  500: 1},
        4: {2: 100, 5: 50, 10: 10, 20: 1},
        6: {1: 100, 4: 50, 10: 1},
        8: {1: 100, 3: 50, 5: 10, 10: 1},
        20: {1: 50, 3: 10, 4: 1},
        50: {1: 50, 3: 1},
        100: {1: 100, 2: 1}
        },
        'dictionary': {
        2: {10: 100, 50: 50, 100: 1},
        4: {2: 100, 10: 50, 50: 1},
        6: {2: 50, 10: 10, 20: 1},
        8: {1: 100, 3: 50, 10: 1},
        10: {1: 100, 3: 50, 5: 1},
        20: {1: 50, 3: 10, 4: 1},
        50: {1: 50, 2: 10, 3: 1},
        100: {1: 100, 2: 1}
        }
    }
    {'first method': {size of input dict: {combine times: size of Dictcombiner.get_dict(), ...}, ...}, ... }
    """
    def test_DictCombiner_get_fastest_method_one_current_events_and_one_times_never_picks_indexed_values(self):
        accepted_choices = ('dictionary', 'flattened_list')
        for power_of_two in range(10):
            """
            events are:
            len(events) = 2**power_of_two (start =1, end = about 10**3)
            single = 1 occurrence
            some = 1, 2, 3 occurrences
            high = 1 + 2 ** event value
            """
            single_occurrence, some_occurrence, high_occurrence = next(events_generator())
            self.assertIn(self.identity_combiner.get_fastest_combine_method(1, single_occurrence), accepted_choices)
            self.assertIn(self.identity_combiner.get_fastest_combine_method(1, some_occurrence), accepted_choices)
            self.assertIn(self.identity_combiner.get_fastest_combine_method(1, high_occurrence), accepted_choices)

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_total_occurrences_min(self):
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, {1: 1}), 'flattened_list')

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_total_occurrences_mid(self):
        other_dict = dict.fromkeys(range(100), 1)
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, other_dict), 'flattened_list')

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_total_occurrences_edge(self):
        other_dict = dict.fromkeys(range(9999), 1)
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, other_dict), 'flattened_list')

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_total_occurrences_over_edge(self):
        """
        this cutoff is not for speed but for safety.  as the next test will demonstrate
        """
        other_dict = dict.fromkeys(range(10000), 1)
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, other_dict), 'dictionary')

    def test_DictCombiner_demonstrate_why_there_is_cutoff_for_flattened_list(self):
        ok_events = {1: 10 ** 4}
        self.assertEqual(flatten_events_tuples(ok_events), [1] * 10 ** 4)
        bad_events = {1: 10 ** 20}
        self.assertRaises((OverflowError, MemoryError), flatten_events_tuples, bad_events)

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_ratio_under(self):
        other_dict = {1: 1, 2: 1, 3: 2, 4: 1}
        ratio = sum(other_dict.values()) / float(len(list(other_dict.keys())))
        self.assertEqual(ratio, 1.25)
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, other_dict), 'flattened_list')

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_ratio_edge(self):
        other_dict = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 10: 4}
        ratio = sum(other_dict.values()) / float(len(list(other_dict.keys())))
        self.assertEqual(ratio, 1.3)
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, other_dict), 'flattened_list')

    def test_DictCombiner_get_fastest_method_tuple_vs_flattened_by_ratio_over_edge(self):
        other_dict = dict.fromkeys(range(99), 1)
        other_dict[100] = 32
        ratio = sum(other_dict.values()) / float(len(list(other_dict.keys())))
        self.assertEqual(ratio, 1.31)
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, other_dict), 'dictionary')

    def test_DictCombiner_get_fastest_method_part_get_best_key_below_min(self):
        test_dict = {1: 1, 3: 1, 5: 1}
        self.assertEqual(get_best_key(-1, test_dict), 1)

    def test_DictCombiner_get_fastest_method_part_get_best_key_above_max(self):
        test_dict = {1: 1, 3: 1, 5: 1}
        self.assertEqual(get_best_key(1001, test_dict), 5)

    def test_DictCombiner_get_fastest_method_part_get_best_key_at_value(self):
        test_dict = {1: 1, 3: 1, 5: 1}
        self.assertEqual(get_best_key(3, test_dict), 3)

    def test_DictCombiner_get_fastest_method_part_get_best_key_between_values(self):
        test_dict = {1: 1, 3: 1, 5: 1}
        self.assertEqual(get_best_key(4, test_dict), 3)

    def test_DictCombiner_get_fastest_method_part_get_indexed_values_min_method_variable(self):
        """
        'flattened_list' - 4: {2: 100, 5: 50, 10: 10, 20: 1}
        'dictionary' - 4: {2: 100, 10: 50, 50: 1}
        """
        self.assertEqual(get_indexed_values_min('flattened_list', 4, 10), 10)
        self.assertEqual(get_indexed_values_min('dictionary', 4, 10), 50)

    def test_DictCombiner_get_fastest_method_part_get_indexed_values_min_uses_get_best_key(self):
        """
        'dictionary' - {2: {10: 100, 50: 50, 100: 1},
                        4: {2: 100, 10: 50, 50: 1}. ...
        """
        self.assertEqual(get_indexed_values_min('dictionary', 4, 10), 50)
        self.assertEqual(get_indexed_values_min('dictionary', 4, 49), 50)
        self.assertEqual(get_indexed_values_min('dictionary', 5, 10), 50)
        self.assertEqual(get_indexed_values_min('dictionary', 1, 1), 100)
        self.assertEqual(get_indexed_values_min('dictionary', 100000, 10000), 1)

    def test_white_box_test_get_indexed_values_min_hardcoded_without_error_because_i_am_a_dumb_ass(self):
        range_of_input_dictionary = [1, 2, 4, 6, 8, 10, 20, 50, 100, 200]
        range_of_combine_times = [1, 2, 3, 4, 5, 10, 20, 50, 100, 200, 500, 600]
        for size in range_of_input_dictionary:
            for times in range_of_combine_times:
                self.assertIsInstance(get_indexed_values_min('dictionary', size, times), int)
                self.assertIsInstance(get_indexed_values_min('flattened_list', size, times), int)

    def test_DictCombiner_get_fastest_method_uses_size_cutoff_to_choose_size_indexed_combiner_size_one(self):
        """'flattened_list' - 4: {2: 100, 5: 50, 10: 10, 20: 1}"""
        sized_twenty = dict.fromkeys(range(20), 1)
        sized_one_combiner = DictCombiner({1: 1})
        self.assertEqual(get_indexed_values_min('flattened_list', 4, 20), 1)
        self.assertEqual(sized_one_combiner.get_fastest_combine_method(4, sized_twenty),
                         'indexed_values')

    def test_DictCombiner_get_fastest_method_uses_size_cutoff_to_choose_other_combiner_size_one(self):
        """'dictionary' - 4: {2: 100, 10: 50, 50: 1}"""
        sized_four = dict.fromkeys(range(4), 2)
        sized_one_combiner = DictCombiner({1: 1})
        self.assertEqual(get_indexed_values_min('dictionary', 4, 20), 50)
        self.assertEqual(sized_one_combiner.get_fastest_combine_method(4, sized_four), 'dictionary')

    def test_DictCombiner_get_fastest_method_uses_size_cutoff_to_choose_below_cutoff(self):
        """'dictionary' - 4: {2: 100, 10: 50, 50: 1}"""
        sized_four = dict.fromkeys(range(4), 2)
        sized_five_combiner = DictCombiner(dict.fromkeys(range(5), 1))
        self.assertEqual(get_indexed_values_min('dictionary', 4, 10), 50)
        self.assertEqual(sized_five_combiner.get_fastest_combine_method(20, sized_four),
                         'dictionary')

    def test_DictCombiner_get_fastest_method_uses_size_cutoff_to_choose_at_cutoff(self):
        """'dictionary' - 4: {2: 100, 10: 50, 50: 1}"""
        sized_four = dict.fromkeys(range(4), 2)
        sized_fifty_combiner = DictCombiner(dict.fromkeys(range(50), 1))
        self.assertEqual(get_indexed_values_min('dictionary', 4, 10), 50)
        self.assertEqual(sized_fifty_combiner.get_fastest_combine_method(20, sized_four),
                         'indexed_values')

    def test_DictCombiner_get_fastest_method_uses_size_cutoff_to_choose_above_cutoff(self):
        """'dictionary' - 4: {2: 100, 10: 50, 50: 1}"""
        sized_four = dict.fromkeys(range(4), 2)
        sized_fifty_one_combiner = DictCombiner(dict.fromkeys(range(51), 1))
        self.assertEqual(get_indexed_values_min('dictionary', 4, 10), 50)
        self.assertEqual(sized_fifty_one_combiner.get_fastest_combine_method(20, sized_four),
                         'indexed_values')

    def test_DictCombiner_combine_by_dictionary_identity(self):
        to_combine = {1: 1, 2: 2}
        new_combiner = DictCombiner({0: 1}).combine_by_dictionary(1, to_combine)
        self.assertEqual(new_combiner.get_dict(), to_combine)

    def test_DictCombiner_combine_by_dictionary_complex(self):
        to_combine = {1: 1, 2: 2}
        new_combiner = DictCombiner({0: 1}).combine_by_dictionary(3, to_combine)
        """
        {1: 1, 2: 2}
    
        {2: 1, 3: 2} + {3: 2, 4: 4} = {2: 1, 3: 4, 4: 4}
    
        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        self.assertEqual(new_combiner.get_dict(), {3: 1, 4: 6, 5: 12, 6: 8})

    def test_DictCombiner_combine_by_dictionary_complex_DictCombiner(self):
        to_combine = {1: 1, 2: 2}
        complex_events = DictCombiner({2: 1, 3: 4, 4: 4})
        new_combiner = complex_events.combine_by_dictionary(1, to_combine)
        """
        {2: 1, 3: 4, 4: 4}
    
        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3: 1, 4: 6, 5: 12, 6: 8}
        """
        self.assertEqual(new_combiner.get_dict(), {3: 1, 4: 6, 5: 12, 6: 8})

    def test_DictCombiner_combine_by_flattened_list_identity(self):
        to_combine = {1: 1, 2: 2}
        new_combiner = DictCombiner({0: 1}).combine_by_flattened_list(1, to_combine)
        self.assertEqual(new_combiner.get_dict(), to_combine)
    
    def test_DictCombiner_combine_by_flattened_list_complex(self):
        to_combine = {1: 1, 2: 2}
        new_combiner = DictCombiner({0: 1}).combine_by_flattened_list(3, to_combine)
        """
        {1: 1, 2: 2}
    
        {2: 1, 3: 2} + {3: 2, 4: 4} = {2:1, 3: 4, 4: 4}
    
        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        self.assertEqual(new_combiner.get_dict(), {3: 1, 4: 6, 5: 12, 6: 8})
    
    def test_DictCombiner_combine_by_flattened_list_complex_DictCombiner(self):
        to_combine = {1: 1, 2: 2}
        complex_events = DictCombiner({2: 1, 3: 4, 4: 4})
        new_combiner = complex_events.combine_by_flattened_list(1, to_combine)
        """
        {2: 1, 3: 4, 4: 4}
    
        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        self.assertEqual(new_combiner.get_dict(), {3: 1, 4: 6, 5: 12, 6: 8})
    
    def test_DictCombiner_combine_by_indexed_values_identity(self):
        to_combine = {1: 1, 2: 2}
        new_combiner = DictCombiner({0: 1}).combine_by_indexed_values(1, to_combine)
        self.assertEqual(new_combiner.get_dict(), to_combine)
    
    def test_DictCombiner_combine_by_indexed_values_complex(self):
        to_combine = {1: 1, 2: 2}
        new_combiner = DictCombiner({0: 1}).combine_by_indexed_values(3, to_combine)
        """
        {1: 1, 2: 2}
    
        {2: 1, 3: 2} + {3: 2, 4: 4} = {2:1, 3: 4, 4: 4}
    
        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        self.assertEqual(new_combiner.get_dict(), {3: 1, 4: 6, 5: 12, 6: 8})
    
    def test_DictCombiner_combine_by_indexed_values_complex_DictCombiner(self):
        to_combine = {1: 1, 2: 2}
        complex_events = DictCombiner({2: 1, 3: 4, 4: 4})
        new_combiner = complex_events.combine_by_indexed_values(1, to_combine)
        """
        {2: 1, 3: 4, 4: 4}
    
        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        self.assertEqual(new_combiner.get_dict(), {3: 1, 4: 6, 5: 12, 6: 8})

    def test_DictCombiner_combine_by_fastest_works_with_flattened_list(self):
        to_add = {1: 1, 2: 1}
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, to_add), 'flattened_list')
        self.assertEqual(self.identity_combiner.combine_by_fastest(1, to_add).get_dict(), to_add)

    def test_DictCombiner_combine_by_fastest_works_with_dictionary(self):
        to_add = {1: 10, 2: 10}
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(1, to_add), 'dictionary')
        self.assertEqual(self.identity_combiner.combine_by_fastest(1, to_add).get_dict(), to_add)

    def test_DictCombiner_combine_by_fastest_works_with_indexed_values(self):
        to_add = dict.fromkeys(range(100), 1)
        answer = self.identity_combiner.combine_by_flattened_list(2, to_add).get_dict()
        self.assertEqual(self.identity_combiner.get_fastest_combine_method(2, to_add), 'indexed_values')
        self.assertEqual(self.identity_combiner.combine_by_fastest(2, to_add).get_dict(), answer)

    def test_DictCombiner_remove_by_tuple_list(self):
        """
        {1: 1, 2: 2}

        {2: 1, 3: 2} + {3: 2, 4: 4} = {2: 1, 3: 4, 4: 4}

        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        start = DictCombiner({3: 1, 4: 6, 5: 12, 6: 8})
        new = start.remove_by_tuple_list(1, {1: 1, 2: 2})
        self.assertEqual(new.get_dict(), {2: 1, 3: 4, 4: 4})

    def test_DictCombiner_remove_by_tuple_list_many(self):
        """
        {1: 1, 2: 2}

        {2: 1, 3: 2} + {3: 2, 4: 4} = {2: 1, 3: 4, 4: 4}

        {3: 1, 4: 4, 5: 4} + {4: 2, 5: 8, 6:8} = {3:1, 4: 6, 5: 12, 6: 8}
        """
        start = DictCombiner({3: 1, 4: 6, 5: 12, 6: 8})
        new = start.remove_by_tuple_list(3, {1: 1, 2: 2})
        self.assertEqual(new.get_dict(), {0: 1})

    def test_DictCombiner_remove_by_tuple_list_dict_has_spaces(self):
        """
        {10: 1, 20: 2}

        {20: 1, 30: 2} + {30: 2, 40: 4} = {20: 1, 30: 4, 40: 4}

        {30: 1, 40: 4, 50: 4} + {40: 2, 50: 8, 60:8} = {30: 1, 40: 6, 50: 12, 60: 8}
        """
        start = DictCombiner({30: 1, 40: 6, 50: 12, 60: 8})
        new = start.remove_by_tuple_list(2, {10: 1, 20: 2})
        self.assertEqual(new.get_dict(), {10: 1, 20: 2})


def events_generator():
    step_by_power_of_two = 1
    while True:
        single_occurrence = dict([(event, 1) for event in range(step_by_power_of_two)])
        middle_occurrences = dict([(event, 1 + event % 3) for event in range(step_by_power_of_two)])
        high_occurrences = dict([(event, 1 + 2 * event) for event in range(step_by_power_of_two)])
        step_by_power_of_two *= 2
        yield (single_occurrence,
               middle_occurrences,
               high_occurrences)
