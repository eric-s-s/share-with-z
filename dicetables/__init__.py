'''All major classes for dicetables can be imported directly as dicetables.Class
or from original module as dicetables.module.Class.
DiceTable() is an AdditiveEvents with a list of dice added by method add_die()
  to see all methods, help(DiceTable) of note,
        stddev, mean, total_occurrences
4 dice, Die, ModDie, WeightedDie, ModWeightedDie.
functions for getting info from tables:
    full_table_string, graph_pts, graph_pts_overflow, stats, ascii_graph
'''
from __future__ import absolute_import


from dicetables import dicestats
from dicetables import longintmath
from dicetables import tableinfo
from dicetables.longintmath import safe_true_div, AdditiveEvents
from dicetables.dicestats import Die, ModDie, WeightedDie, ModWeightedDie, StrongDie, ProtoDie, DiceTable
from dicetables.tableinfo import full_table_string, graph_pts, graph_pts_overflow, stats, scinote, NumberFormatter
