# Copyright (c) 2019, Danish Technological Institute.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -*- coding: utf-8 -*-

""" Function to manipulate assign nodes in abstract syntax trees (ASTs)

    Description:
        The main function maybe_change_parameters(...) accepts an AST tree
        and a list of parameters stored as dicts with "key", "value". The
        custom transformer class then visits all AST.Assign nodes and checks
        if the value intended for the target is a number. If so, it proceeds
        to check if it can find the parameter (specified by the target's id,
        i.e. its name!), if no direct match is found, then a search for
        similar parameters is done by the builtin SequenceMatcher.
        If no node is found, the user is warned. Otherwise if a (similar) node
        is found the value in the AST node and the value in the parameter list
        is compared and if they differ then prompts the user to decide which
        value to use.

    Possible to expand nodes visited by adding functions prepended `visit_`
    See:
    - https://docs.python.org/3/library/ast.html
    - https://greentreesnakes.readthedocs.io/en/latest/nodes.html

    AST Trees decoded:
    - https://python-ast-explorer.com/

    Example usage as standalone:

    ```
    filename = "src/train.py"
    src = open(filename, "r").read()
    tree = ast.parse(src, filename)

    parameters = [{
            "key": "batch_size",
            "value": 33
        },{
            "key": "epochs",
            "value": 20
        },{
            "key": "drop_out",
            "value": 0.5
        }
    ]

    _maybe_change_parameters(tree, parameters)
    code = compile(tree, filename, mode="exec")

    exec(code)
    ```

"""

import ast
import logging
from difflib import SequenceMatcher

from tracker.utils import cli

log = logging.getLogger(__name__)


def get_parameters_from_source(filename):
    assigns = []
    src = open(filename, "r").read()
    tree = ast.parse(src, filename)
    _get_assigns(tree, assigns)
    return assigns


def _get_assigns(root, assigns):
    class Transformer(ast.NodeTransformer):
        def visit_Assign(self, node):
            if not isinstance(node.value, ast.Num):
                # log.debug("Assign value is not a number. Skipping node {}"
                #           .format(node.targets[0].__dict__))
                return node

            assigns.append(
                {"key": node.targets[0].__dict__["id"],
                 "value": node.value.__dict__["n"]}
            )

            return node

    return Transformer().visit(root)


def _maybe_change_parameters(root, parameters, yes):
    """Change parameter in AST

    Arguments:
        root {AST.node} -- root of the AST tree
        parameters {list} -- list of dicts with parameter.key/value
        yes {bool} -- To or not to prompt user

    Returns:
        <AST.node> -- Potentially changed root of AST tree
    """
    # If we don't want to make inline changes do a deep copy
    # import copy
    # root = copy.deepcopy(root)

    def _get_parameter_by_id(parameters, name):
        return next((p for p in parameters if p["key"] == name), None)

    def _find_close_match(parameters, name):
        parameter = None
        match = None
        prob = 0
        for param in parameters:
            p = SequenceMatcher(None, param["key"], name).ratio()
            # 0.8 simply chosen to be confident enough prior to prompt
            if p > 0.8 and p > prob:
                prob = p
                parameter = param
                match = name
        return parameter, match

    class Transformer(ast.NodeTransformer):
        def visit_Assign(self, node):
            if not isinstance(node.value, ast.Num):
                # log.debug(
                #     "Assign value is not a number. Skipping node {}"
                #     .format(node.targets[0].__dict__))
                return node

            target = node.targets[0].__dict__["id"]
            parameter = _get_parameter_by_id(parameters, target)

            if not parameter:
                parameter, match = _find_close_match(parameters, target)

                # If parameter is found
                if parameter:
                    # Let user confirm parameter
                    if yes \
                       or _confirm_parameter_name(parameter["key"], match):
                        parameter["key"] = match
                    else:
                        for i in range(len(parameters)):
                            if parameters[i].get("key") == parameter["key"]:
                                del parameters[i]
                                break  # We break as we assume unique matches

            if parameter:
                if parameter["key"] in target:
                    # if parameter["value"] != node.value.__dict__["n"]:
                    #     if yes \
                    #         or _confirm_parameter_value(target,
                    #            parameter["value"],
                    #            node.value.__dict__["n"]):
                    #         node.value.__dict__["n"] = parameter["value"]
                    node.value.__dict__["n"] = parameter["value"]
            else:
                log.debug(
                    "No value found for '{}', in the experiment "
                    "configuration.\n"
                    "   Using default value from the source code: {}"
                    .format(node.targets[0].__dict__["id"],
                            node.value.__dict__["n"]))
            return node

    return Transformer().visit(root)


def _confirm_parameter_name(name, match):
    prompt = (
        "The parameter '{}' was not found!\n"
        "   Did you mean '{}'?"
        .format(name, match)
    )
    return cli.confirm(prompt, default=True)


def _confirm_parameter_value(target, config, source):
    prompt = (
        "Value assigned to '{}' in the source ('{}')\n"
        "differs from the one specified in the experiment\n"
        "configuration ('{}').\n"
        "Do you want to overwrite the source specified value?"
        .format(
            target,
            source,
            config
        )
    )
    return cli.confirm(prompt, default=True)


def check_parameters(filename, parameters, yes):
    src = open(filename, "r").read()
    tree = ast.parse(src, filename)
    _maybe_change_parameters(tree, parameters, yes)
    return tree
