# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Command to compare experiments and their trials
"""

import click

from tracker.utils import click_utils


def compare_params(fn):
    click_utils.append_params(fn, [
        click.Option(
            ("-e", "--extra-cols",), is_flag=True,
            help="Show extra columns such as source code hash."),
        click.Option(
            ("-c", "--cols",), metavar="COLUMNS",
            help=(
                "Additional columns to compare. "
                "Cannot be used with --strict-columns.")),
        click.Option(
            ("--strict-cols",), metavar="COLUMNS",
            help="Columns to compare. Cannot be used with --columns."),
        click.Option(
            ("--skip-op-cols",), is_flag=True,
            help="Don't show operation columns."),
        click.Option(
            ("--skip-core",), is_flag=True,
            help="Don't show core columns."),
        click.Option(
            ("--top",), metavar="N", type=click.IntRange(min=1),
            help="Only show the top N runs."),
        click.Option(
            ("--min",), metavar="COLUMN",
            help="Show the lowest values for COLUMN first."),
        click.Option(
            ("--max",), metavar="COLUMN",
            help="Show the highest values for COLUMN first."),
        click.Option(
            ("-t", "--table",), is_flag=True,
            help="Show comparison data as a table."),
        click.Option(
            ("--csv",), metavar="PATH",
            help=(
                "Save comparison data to a CSV file. Use '-' for "
                "standard output.")),
    ])
    return fn


@click.command("compare")
@compare_params

@click.pass_context
@click_utils.use_args

def compare(ctx, args):
    """ Compare results of trials.

    Compare is a console based application that displays a
    spreadsheet of runs with their current accuracy and loss. The
    application will continue to run until you exit it by pressing
    ``q`` (for quit).

    Compare supports a number of commands. Commands are
    activated by pressing a letter. To view the list of commands,
    press ``?``.

    Compare does not automatically update to display the latest
    available data. If you want to update the list of runs and their
    status, press ``r`` (for refresh).

    You may alternative use the `--csv` option to write a CSV file
    containing the compare data. To print the CSV contents to standard
    output, use '-' for the file path.

    ### Compare Columns

    Compare shows columns for each run based on the columns
    defined for each run operation. Additional columns may be
    specified using the `--columns` option, which must be a comma
    separated list of column specs. See below for column spec details.

    If multiple columns have the same name, they are merged into a
    single column. Cell values are merged by taking the first non-null
    value in the list of cells with the common name from
    left-to-right.

    By default, columns always contain run ID, model, operation,
    started, time, label, status, and the set of columns defined for
    each displayed operation. You can skip the core columns by with
    `--skip-core` and skip the operation columns with
    `--skip-op-cols`.

    ### Column Specs

    Each column specified in `COLUMNS` must be a valid column spec. A
    column spec is the name of a run flag or scalar key. Flag names
    must be preceded by an equals sign ``=`` to differentiate them
    from scalar keys.

    For example, to include the flag ``epochs`` as a column, use
    ``--columns =epochs``.

    If a scalar is specified, it may be preceded by a qualifier of
    `min`, `max`, `first`, `last`, `avg`, `total`, or `count` to
    indicate the type of scalar value. For example, to include the
    highest logged value for `accuracy`, use ``--columns "max
    accuray"``.

    By default `last` is assumed, so that the last logged value for
    the specified scalar is used.

    A scalar spec may additionally contain the key word `step` to
    indicate that the step associated with the scalar is used. For
    example, to include the step of the last `accuracy` value, use
    ``--columns "accuracy step"``. Step may be used with scalar
    qualifiers. For example, to include the value and associated step
    of the lowest loss, use ``--columns "min loss, min loss step"``.

    Column specs may contain an alternative column heading using the
    keyword ``as`` in the format ``COL as HEADING``. Headings that
    contain spaces must be quoted.

    For example, to include the scalar ``val_loss`` with name
    ``validation loss``, use ``--columns val_loss as 'validation
    loss'``.

    You may include run attributes as column specs by preceding the
    run attribute name with a period ``.``. For example, to include
    the `stopped` attribute, use ``--columns .stopped``. This is
    useful when using `--skip-core`.

    ### Sort Runs

    Use `--min` and `--max` to sort results by a particular
    column. `--min` sorts in ascending order and `--max` sorts in
    descending order.

    When specifying `COLUMN`, use the column name as displayed in the
    table output. If the column name contains spaces, quote the value.

    By default, runs are sorted by start time in ascending order -
    i.e. the most recent runs are listed first.

    ### Limit Runs

    To limit the results to the top `N` runs, use `--top`.

    If a `RUN` argument is not specified, ``:`` is assumed (all runs
    are selected).

    """
    from . import compare_impl
    compare_impl.main(args)
