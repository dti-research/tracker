# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

import click
import functools
import re


class Args(object):

    def __init__(self, **kw):
        for name in kw:
            setattr(self, name, kw[name])
        self.__names = list(kw)

    def __repr__(self):
        return "<tracker.utils.click.Args %s>" % self.as_kw()

    def as_kw(self):
        return {name: getattr(self, name) for name in self.__names}


class Group(click.Group):

    def get_command(self, ctx, cmd_name):
        for cmd in self.commands.values():
            names = re.split(", ?", cmd.name)
            if cmd_name in names:
                cmd_name = cmd.name
                break
        return super(Group, self).get_command(ctx, cmd_name)


def use_args(fn0):
    def fn(*args, **kw):
        return fn0(*(args + (Args(**kw),)))
    return functools.update_wrapper(fn, fn0)


def append_params(fn, params):
    fn.__click_params__ = getattr(fn, "__click_params__", [])
    for param in reversed(params):
        if callable(param):
            param(fn)
        else:
            fn.__click_params__.append(param)


def verbose_option(fn):
    """ Verbose
    """
    append_params(fn, [
        click.Option(("-v", "--verbose",), is_flag=True,
                     help="Show more status information.")
    ])
    return fn


def no_prompt_option(fn):
    """ No prompt
    """
    append_params(fn, [
        click.Option(
            ("-y", "--yes"),
            help="Do not prompt before running operation.",
            is_flag=True),
    ])
    return fn
