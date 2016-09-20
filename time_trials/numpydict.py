"""a simulated Counter dict with numpy arrays"""
import numpy as np


def convert_tuple_list_to_array_and_start_value(sorted_tuple_list):
    start_val = sorted_tuple_list[0][0]
    end_val = sorted_tuple_list[-1][0]
    out_array = np.zeros(end_val - start_val + 1, dtype=object)
    for index, value in sorted_tuple_list:
        array_index = index - start_val
        out_array[array_index] = value
    return start_val, out_array


class NumpyCounter(object):
    def __init__(self, start_val=0, array=np.array([1], dtype=object)):
        self.start_val = start_val
        self.array = array

    def items(self):
        out = []
        for index, value in enumerate(self.array):
            if value:
                out.append((index + self.start_val, value))
        return out

    def add(self, other):
        val_diff = self.start_val - other.start_val
        if val_diff < 0:
            lower = self
            higher = other
        else:
            lower = other
            higher = self
        new_array = combine_arrays(lower.array, higher.array, abs(val_diff))
        return NumpyCounter(lower.start_val, new_array)


def equalize_size_lower(lower, total_size):
    zeros = np.zeros(total_size - lower.size, dtype=object)
    return np.append(lower, zeros)


def equalize_size_higher(higher, total_size, val_diff):
    left = np.zeros(val_diff, dtype=object)
    right = np.zeros(total_size - val_diff - higher.size, dtype=object)
    higher = np.append(left, higher)
    higher = np.append(higher, right)
    return higher


def combine_arrays(lower, higher, val_diff):
    total_size = max(lower.size, higher.size + val_diff)
    lower = equalize_size_lower(lower, total_size)
    higher = equalize_size_higher(higher, total_size, val_diff)
    return lower + higher






