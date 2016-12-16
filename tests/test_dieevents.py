# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
from __future__ import absolute_import

import unittest
from dicetables.dieevents import Die, ModDie, WeightedDie, ModWeightedDie, StrongDie, ProtoDie
from dicetables.baseevents import InvalidEventsError


class DummyDie(ProtoDie):
    def __init__(self, size, weight, dictionary, repr_str):
        self.size = size
        self.weight = weight
        self.dictionary = dictionary
        self.repr_str = repr_str
        super(DummyDie, self).__init__()

    def get_dict(self):
        return self.dictionary

    def get_size(self):
        return self.size

    def get_weight(self):
        return self.weight

    def __repr__(self):
        return self.repr_str

    def __str__(self):
        return 'hi'

    def multiply_str(self, number):
        return str(number)

    def weight_info(self):
        return "OyVei! you're too thin. Es, bubelah."


class TestDieEvents(unittest.TestCase):

    # rich comparison testing
    def test_ProtoDie_equality_true(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(2, 3, {2: 2}, 'b')
        self.assertTrue(first == second)

    def test_ProtoDie_equality_true_if_different_types_eval_the_same(self):
        class NewDummyDie(DummyDie):
            def __init__(self, size, weight, dictionary, repr_str):
                super(NewDummyDie, self).__init__(size, weight, dictionary, repr_str)

        first = DummyDie(2, 3, {2: 2}, 'b')
        second = NewDummyDie(2, 3, {2: 2}, 'b')
        self.assertTrue(first == second)

    def test_ProtoDie_equality_false_by_size(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(100, 3, {2: 2}, 'b')
        self.assertFalse(first == second)

    def test_ProtoDie_equality_false_by_weight(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(2, 100, {2: 2}, 'b')
        self.assertFalse(first == second)

    def test_ProtoDie_equality_false_by_get_dict(self):
        first = DummyDie(2, 3, {200: 200}, 'b')
        second = DummyDie(2, 3, {2: 2}, 'b')
        self.assertFalse(first == second)

    def test_ProtoDie_equality_false_by_get_repr(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(2, 3, {2: 2}, 'different repr')
        self.assertFalse(first == second)

    def test_ProtoDie_equality_false_by_not_a_proto_die(self):
        self.assertFalse(DummyDie(2, 3, {2: 2}, 'b') == 2)

    def test_lt_false_if_equal(self):
        first = DummyDie(2, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertFalse(first < second)
        self.assertFalse(second < first)

    def test_ProtoDie_lt_by_size(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(20, 3, {2: 2}, 'b')
        self.assertTrue(first < second)

    def test_ProtoDie_lt_by_weight(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(2, 30, {2: 2}, 'b')
        self.assertTrue(first < second)

    def test_ProtoDie_lt_by_sorted_get_dict(self):
        first = DummyDie(2, 3, {2: 200, 20: 200}, 'b')
        second = DummyDie(2, 3, {20: 2}, 'b')
        third = DummyDie(2, 3, {20: 20}, 'b')
        self.assertTrue(first < second)
        self.assertTrue(first < third)
        self.assertTrue(second < third)

    def test_ProtoDie_lt_by_repr(self):
        first = DummyDie(2, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'b')
        self.assertTrue(first < second)

    def test_ProtoDie_lt_by_size_is_most_important(self):
        first = DummyDie(2, 30, {20: 20}, 'b')
        second = DummyDie(20, 3, {2: 2}, 'a')
        self.assertTrue(first < second)

    def test_ProtoDie_lt_by_weight_is_second_most_important(self):
        first = DummyDie(2, 3, {20: 20}, 'b')
        second = DummyDie(2, 30, {2: 2}, 'a')
        self.assertTrue(first < second)

    def test_ProtoDie_lt_by_sorted_get_dict_is_third_most_important_and_so_repr_is_last(self):
        first = DummyDie(2, 3, {2: 2}, 'b')
        second = DummyDie(2, 3, {20: 20}, 'a')
        self.assertTrue(first < second)

    def test_ProtoDie_not_equal_true(self):
        first = DummyDie(20, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertTrue(first != second)
        self.assertFalse(first == second)

    def test_ProtoDie_not_equal_false(self):
        first = DummyDie(2, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertTrue(first == second)
        self.assertFalse(first != second)

    def test_ProtoDie_gt_true(self):
        first = DummyDie(20, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertTrue(first > second)

    def test_ProtoDie_gt_false(self):
        first = DummyDie(20, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertFalse(second > first)
        self.assertFalse(first > first)

    def test_ProtoDie_le_true(self):
        first = DummyDie(2, 3, {2: 2}, 'a')
        second = DummyDie(20, 3, {2: 2}, 'a')
        self.assertTrue(first <= second)
        self.assertTrue(first <= first)

    def test_ProtoDie_le_false(self):
        first = DummyDie(2, 3, {2: 2}, 'a')
        second = DummyDie(20, 3, {2: 2}, 'a')
        self.assertFalse(second <= first)

    def test_ProtoDie_ge_true(self):
        first = DummyDie(20, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertTrue(first >= second)
        self.assertTrue(first >= first)

    def test_ProtoDie_ge_false(self):
        first = DummyDie(20, 3, {2: 2}, 'a')
        second = DummyDie(2, 3, {2: 2}, 'a')
        self.assertFalse(second >= first)

    def test_ProtoDie_lt_all_die_types_can_sort_with_each_other(self):
        dice = [StrongDie(Die(2), 1),
                ModWeightedDie({1: 1, 2: 1}, 0),
                WeightedDie({1: 1, 2: 1}),
                ModDie(2, 0),
                Die(2),
                Die(3)]
        self.assertIsNone(dice.sort())

    def test_ProtoDie_lt_all_die_types_sort_as_expected(self):
        dice = [StrongDie(Die(2), 1),
                StrongDie(WeightedDie({1: 2, 2: 0}), 1),
                ModWeightedDie({1: 1, 2: 1}, 0),
                WeightedDie({1: 2, 2: 0}),
                ModDie(2, 0),
                Die(2),
                Die(3)]
        sorted_dice = [Die(2),
                       ModDie(2, 0),
                       StrongDie(Die(2), 1),
                       ModWeightedDie({1: 1, 2: 1}, 0),
                       StrongDie(WeightedDie({1: 2, 2: 0}), 1),
                       WeightedDie({1: 2, 2: 0}),
                       Die(3)]
        self.assertEqual(sorted(dice), sorted_dice)

    def test_ProtoDie_hash(self):
        hash_str = 'hash of REPR, 2, 3, {4: 5}'
        self.assertEqual(hash(DummyDie(2, 3, {4: 5}, 'REPR')), hash(hash_str))

    def test_ProtoDie_hash_with_Die(self):
        one_a = Die(1)
        one_b = Die(1)
        self.assertEqual(hash(one_a), hash(one_b))
        self.assertNotEqual(hash(one_a), hash(Die(2)))

    def test_ProtoDie_hash_with_Die_and_ModDie(self):
        one_a = ModDie(1, 0)
        one_b = ModDie(1, 0)
        not_same_a = Die(1)
        not_same_b = ModDie(2, 0)
        not_same_c = ModDie(1, 1)
        self.assertEqual(hash(one_a), hash(one_b))
        self.assertNotEqual(hash(one_a), hash(not_same_a))
        self.assertNotEqual(hash(one_a), hash(not_same_b))
        self.assertNotEqual(hash(one_a), hash(not_same_c))

    def test_Die_init_raises_InvalidEventsError_for_illegal_size(self):
        self.assertRaises(InvalidEventsError, Die, 0)
        self.assertRaises(InvalidEventsError, Die, -2)

    def test_Die_get_size(self):
        self.assertEqual(Die(6).get_size(), 6)

    def test_Die_get_weight(self):
        self.assertEqual(Die(10).get_weight(), 0)

    def test_Die_get_dict(self):
        self.assertEqual(Die(3).get_dict(), {1: 1, 2: 1, 3: 1})

    def test_Die_weight_info(self):
        self.assertEqual(Die(10000).weight_info(), 'D10000\n    No weights')

    def test_Die_str(self):
        self.assertEqual(str(Die(1234)), 'D1234')

    def test_Die_repr(self):
        self.assertEqual(repr(Die(123)), 'Die(123)')

    def test_Die_multiply_str(self):
        self.assertEqual(Die(5).multiply_str(101), '101D5')

    def test_ModDie_get_modifier(self):
        self.assertEqual(ModDie(7, 33).get_modifier(), 33)

    def test_ModDie_get_dict(self):
        self.assertEqual(ModDie(2, 5).get_dict(), {6: 1, 7: 1})

    def test_ModDie_string(self):
        self.assertEqual(str(ModDie(10, 0)), 'D10+0')

    def test_ModDie_repr(self):
        self.assertEqual(repr(ModDie(5, -1)), 'ModDie(5, -1)')

    def test_ModDie_multiply_str_pos_mod(self):
        self.assertEqual(ModDie(5, 3).multiply_str(2), '2D5+6')

    def test_ModDie_multiply_str_neg_mod(self):
        self.assertEqual(ModDie(5, -3).multiply_str(2), '2D5-6')

    def test_WeightedDie_init_raises_ValueError_on_zero_key(self):
        self.assertRaises(ValueError, WeightedDie, {0: 1, 2: 1})

    def test_WeightedDie_init_raises_ValueError_on_negative_key(self):
        self.assertRaises(ValueError, WeightedDie, {-5: 1, 2: 1})

    def test_WeightedDie_init_raises_InvalidEvents_error_on_bad_dict(self):
        self.assertRaises(InvalidEventsError, WeightedDie, {1: -1})
        self.assertRaises(InvalidEventsError, WeightedDie, {1: 0})

    def test_WeightedDie_init_does_not_raise_error_if_zero_values_in_dict(self):
        self.assertIsNotNone(WeightedDie({1: 1, 2: 0, 3: 0}))

    def test_WeightedDie_get_size(self):
        self.assertEqual(WeightedDie({5: 2, 2: 5}).get_size(), 5)

    def test_WeightedDie_get_size_edge_case(self):
        self.assertEqual(WeightedDie({1: 1, 3: 0}).get_size(), 3)

    def test_WeightedDie_get_weight(self):
        self.assertEqual(WeightedDie({1: 2, 3: 5}).get_weight(), 2+5)

    def test_WeightedDie_get_dict(self):
        self.assertEqual(WeightedDie({1: 2, 3: 4}).get_dict(), {1: 2, 3: 4})

    def test_WeightedDie_get_dict_doesnt_return_zero_frequencies(self):
        self.assertEqual(WeightedDie({1: 2, 3: 0}).get_dict(), {1: 2})

    def test_WeightedDie_weight_info(self):
        dic = dict((x, x + 1) for x in range(1, 6, 2))
        weights_str = ('D5  W:12\n' +
                       '    a roll of 1 has a weight of 2\n' +
                       '    a roll of 2 has a weight of 0\n' +
                       '    a roll of 3 has a weight of 4\n' +
                       '    a roll of 4 has a weight of 0\n' +
                       '    a roll of 5 has a weight of 6')
        self.assertEqual(WeightedDie(dic).weight_info(), weights_str)

    def test_WeightedDie_weight_info_formatting_large_num(self):
        dic = dict((x, x + 1) for x in range(1, 12, 2))
        weights_str = ('D11  W:42\n' +
                       '    a roll of  1 has a weight of 2\n' +
                       '    a roll of  2 has a weight of 0\n' +
                       '    a roll of  3 has a weight of 4\n' +
                       '    a roll of  4 has a weight of 0\n' +
                       '    a roll of  5 has a weight of 6\n' +
                       '    a roll of  6 has a weight of 0\n' +
                       '    a roll of  7 has a weight of 8\n' +
                       '    a roll of  8 has a weight of 0\n' +
                       '    a roll of  9 has a weight of 10\n' +
                       '    a roll of 10 has a weight of 0\n' +
                       '    a roll of 11 has a weight of 12')
        self.assertEqual(WeightedDie(dic).weight_info(), weights_str)

    def test_WeightedDie_str(self):
        self.assertEqual(str(WeightedDie({1: 1, 5: 3})), 'D5  W:4')

    def test_WeightedDie_repr(self):
        self.assertEqual(repr(WeightedDie({1: 1, 2: 3})),
                         'WeightedDie({1: 1, 2: 3})')

    def test_WeightedDie_repr_edge_case(self):
        die1 = WeightedDie({1: 1, 3: 0})
        die2 = WeightedDie({1: 1, 2: 0, 3: 0})
        the_repr = 'WeightedDie({1: 1, 2: 0, 3: 0})'
        self.assertEqual(repr(die1), the_repr)
        self.assertEqual(repr(die2), the_repr)
        self.assertEqual(die1, die2)

    def test_WeightedDie_multiply_str(self):
        self.assertEqual(WeightedDie({1: 1, 5: 3}).multiply_str(2), '2D5  W:4')

    def test_WeightedDie_get_raw_dict(self):
        self.assertEqual(WeightedDie({1: 2, 2: 4}).get_raw_dict(), {1: 2, 2: 4})

    def test_WeightedDie_get_raw_dict_includes_zeroes(self):
        self.assertEqual(WeightedDie({2: 1, 4: 1, 5: 0}).get_raw_dict(), {1: 0, 2: 1, 3: 0, 4: 1, 5: 0})

    def test_ModWeightedDie_get_mod(self):
        self.assertEqual(ModWeightedDie({1: 2}, 3).get_modifier(), 3)

    def test_ModWeightedDie_get_dict(self):
        self.assertEqual(ModWeightedDie({1: 2, 3: 4}, -2).get_dict(),
                         {1 - 2: 2, 3 - 2: 4})

    def test_ModWeightedDie_string_for_positive_mod(self):
        self.assertEqual(str(ModWeightedDie({1: 2}, 3)), 'D1+3  W:2')

    def test_ModWeightedDie_string_for_negative_mod(self):
        self.assertEqual(str(ModWeightedDie({1: 2}, -3)), 'D1-3  W:2')

    def test_ModWeightedDie_repr(self):
        self.assertEqual(repr(ModWeightedDie({1: 2}, -3)),
                         'ModWeightedDie({1: 2}, -3)')

    def test_ModWeightedDie_multiply_str_for_positive_mod(self):
        self.assertEqual(ModWeightedDie({1: 2}, 3).multiply_str(5), '5D1+15  W:2')

    def test_ModWeightedDie_multiply_str_for_negative_mod(self):
        self.assertEqual(ModWeightedDie({1: 2}, -3).multiply_str(5), '5D1-15  W:2')

    def test_StrongDie_get_size(self):
        orig = ModWeightedDie({1: 2}, -3)
        self.assertEqual(StrongDie(orig, 100).get_size(), orig.get_size())

    def test_StrongDie_get_weight(self):
        orig = ModWeightedDie({1: 2}, -3)
        self.assertEqual(StrongDie(orig, 100).get_weight(), orig.get_weight())

    def test_StrongDie_get_multiplier(self):
        self.assertEqual(StrongDie(Die(3), 5).get_multiplier(), 5)

    def test_StrongDie_get_input_die(self):
        self.assertEqual(StrongDie(Die(3), 5).get_input_die(), Die(3))

    def test_StrongDie_get_dict(self):
        orig = ModWeightedDie({1: 2, 2: 1}, 1)
        self.assertEqual(StrongDie(orig, 100).get_dict(), {200: 2, 300: 1})

    def test_StrongDie_zero_multiplier(self):
        die = StrongDie(WeightedDie({1: 2, 3: 4}), 0)
        self.assertEqual(die.get_dict(), {0: 4})

    def test_StrongDie_negative_multiplier(self):
        die = StrongDie(WeightedDie({1: 2, 3: 4}), -2)
        self.assertEqual(die.get_dict(), {-2: 2, -6: 4})

    def test_StrongDie_weight_info(self):
        dic = dict((x, x + 1) for x in range(1, 6, 2))
        weights_str = ('(D5  W:12)X(10)\n' +
                       '    a roll of 1 has a weight of 2\n' +
                       '    a roll of 2 has a weight of 0\n' +
                       '    a roll of 3 has a weight of 4\n' +
                       '    a roll of 4 has a weight of 0\n' +
                       '    a roll of 5 has a weight of 6')
        self.assertEqual(StrongDie(WeightedDie(dic), 10).weight_info(),
                         weights_str)

    def test_StrongDie_multiply_str(self):
        orig = ModWeightedDie({1: 2}, -3)
        expected = '(5D1-15  W:2)X(100)'
        self.assertEqual(StrongDie(orig, 100).multiply_str(5), expected)

    def test_StrongDie_str(self):
        self.assertEqual(str(StrongDie(Die(7), 5)), '(D7)X(5)')

    def test_StrongDie_repr(self):
        self.assertEqual(repr(StrongDie(Die(7), 5)), 'StrongDie(Die(7), 5)')

    def test_StrongDie_edge_StrongDie_of_StrongDie_size(self):
        die = StrongDie(Die(5), 2)
        self.assertEqual(StrongDie(die, 3).get_size(), 5)

    def test_StrongDie_edge_StrongDie_of_StrongDie_weight(self):
        die = StrongDie(WeightedDie({1: 5}), 2)
        self.assertEqual(StrongDie(die, 3).get_weight(), 5)

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_get_dict(self):
        die = StrongDie(ModDie(3, 1), 2)
        expected_tuple = dict((roll * 6, 1) for roll in [2, 3, 4])
        self.assertEqual(StrongDie(die, 3).get_dict(), expected_tuple)

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_get_multiplier(self):
        die = StrongDie(ModDie(3, 1), 2)
        self.assertEqual(StrongDie(die, 3).get_multiplier(), 3)

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_get_original(self):
        die = StrongDie(ModDie(3, 1), 2)
        self.assertEqual(StrongDie(die, 3).get_input_die(), die)

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_str(self):
        die = StrongDie(ModDie(3, 1), 2)
        self.assertEqual(StrongDie(die, 3).__str__(), '((D3+1)X(2))X(3)')

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_repr(self):
        die = StrongDie(ModDie(3, 1), 2)
        self.assertEqual(StrongDie(die, 3).__repr__(), 'StrongDie(StrongDie(ModDie(3, 1), 2), 3)')

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_multiply_str(self):
        die = StrongDie(ModDie(3, 1), 2)
        self.assertEqual(StrongDie(die, 3).multiply_str(5), '((5D3+5)X(2))X(3)')

    def test_StrongDie_edge_case_StrongDie_of_StrongDie_weight_info(self):
        die = StrongDie(ModWeightedDie({1: 4}, 1), 2)
        self.assertEqual(StrongDie(die, 3).weight_info(), '((D1+1  W:4)X(2))X(3)\n    a roll of 1 has a weight of 4')

if __name__ == '__main__':
    unittest.main()
