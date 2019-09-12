# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Utility code to print a list in multiple coloums
"""


def print_two_coloumn(l):
    if len(l) % 2 != 0:
        l.append(" ")

    split = int(len(l) / 2)
    l1 = l[0:split]
    l2 = l[split:]
    for key, value in zip(l1, l2):
        print("{0:<20s} {1}".format(key, value))
