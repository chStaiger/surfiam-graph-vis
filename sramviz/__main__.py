#!/usr/bin/env python3
"""Draw the plain sram graph."""

import argparse
import pprint
import sys
from pathlib import Path

import networkx as nx

from sramviz.graph_from_sram_json import get_nodes_from_dict, nodes_to_graph, read_json, stats_dict
from sramviz.utils import (
    add_graph_edges_from_config,
    color_nodes,
    read_graph_config,
    render_editable_network,
    set_node_levels_from_config,
    set_node_type,
)

try:  # Python < 3.10 (backport)
    from importlib_metadata import version  # type: ignore
except ImportError:
    from importlib.metadata import version  # type: ignore [assignment]

# Preconfiguration
colors = {
    "group": "darkorange",
    "service": "teal",
    "default": "lightblue",
    "user": "darkseagreen",
    "admin": "darkseagreen",
}

MAIN_HELP_MESSAGE = f"""
SRAM graph visualisation version {version("sramviz")}

Usage: sramviz [subcommand] [options]

Available subcommands:
    organisation
        Generate the graph representation of the export to json of an SRAM organisation.
    graph
        Generate the graph representation from a section in the configuration file.
    stats
        Retrieve statistics from the export to json of an SRAM organisation.

Example usage:

    sramviz graph -o html/test.html -c configs/graph_config.toml -g plain_graph -v
    sramviz organisation -i data/output.json -o html/test.html -c configs/graph_config.toml
    sramviz stats -i data/output.json
"""


def main() -> None:
    """CLI with different entrypoints."""
    subcommand = "--help" if len(sys.argv) < 2 else sys.argv.pop(1)

    if subcommand in ["-h", "--help"]:
        print(MAIN_HELP_MESSAGE)
    elif subcommand in ["-v", "--version"]:
        print(f"sramviz version {version('sramviz')}")

    # find the subcommand in this module and run it!
    elif subcommand == "organisation":
        render_graph_from_json()
    elif subcommand == "graph":
        render_graph_from_config()
    elif subcommand == "stats":
        get_stats_from_json()
    else:
        print(f"Invalid subcommand ({subcommand}). For help see sramviz --help")
        sys.exit(1)


def render_graph_from_json():
    """Render graph from the json export of an sram organisation."""
    parser = argparse.ArgumentParser(
        prog="sramviz organisation",
        description="Render the graph of an SRAM organisation froman json export file.",
    )
    parser.add_argument(
        "-i",
        "--input",
        help="The path to the json file from an export of an SRAM organisation.",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path and name to store the generated html file.",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Configuration file defining node and edge types.",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "-v", "--verbose", help="Verbose output.", action="store_true", default=False
    )
    args = parser.parse_args()

    graph_config = _parse_config(args)
    if args.verbose:
        pprint.pprint(graph_config)

    _parse_output(args)

    sram_dict = _parse_input(args)

    nodes = get_nodes_from_dict(sram_dict)
    graph = nodes_to_graph(nodes)
    set_node_levels_from_config(graph, graph_config)
    color_nodes(graph, graph_config, **colors)
    render_editable_network(graph, args.output.absolute(), args.verbose)


def render_graph_from_config():
    """Render a graph section from the configuration file."""
    parser = argparse.ArgumentParser(
        prog="sramviz graph", description="Render a graph section from the configuration file."
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Path and name to store the generated html file.",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Configuration file defining node, edge types and the graph(s).",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "-g",
        "--graph",
        help="the name of the section in the config file which defines the edges of the graph.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-v", "--verbose", help="Verbose output.", action="store_true", default=False
    )

    args = parser.parse_args()

    graph_config = _parse_config(args)
    if args.verbose:
        print("Configuration:")
        pprint.pprint(graph_config)

    if args.graph not in graph_config:
        print(f"Graph {args.graph} not defined in {args.config.absolute()}. Exit.")
        sys.exit(234)
    if args.verbose:
        print(f"Rendering {args.graph}")
        pprint.pprint(graph_config[args.graph])

    _parse_output(args)

    graph = nx.MultiDiGraph()
    add_graph_edges_from_config(graph, graph_config, args.graph)
    set_node_type(graph, graph_config)
    set_node_levels_from_config(graph, graph_config)
    color_nodes(graph, graph_config, **colors)

    render_editable_network(graph, args.output.absolute(), args.verbose)


def get_stats_from_json():
    """Get statistics of an SRAM organisation."""
    parser = argparse.ArgumentParser(
        prog="sramviz stats", description="Retrieve statistics from SRAM json file."
    )

    parser.add_argument(
        "-i",
        "--input",
        help="The path to the json file from an export of an SRAM organisation.",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    sram_dict = _parse_input(args)
    nodes = get_nodes_from_dict(sram_dict)
    pprint.pprint(stats_dict(nodes))


def _parse_config(args: argparse.Namespace) -> dict:
    if args.config.is_file():
        try:
            graph_config = read_graph_config(args.config.absolute())
            return graph_config
        except Exception as error:
            print(f"Cannot read in {args.config}: {repr(error)}.")
            sys.exit(234)
    else:
        print(f"Config {args.config.absolute()} is directory or does not exist. Exit.")
        sys.exit(234)


def _parse_output(args: argparse.Namespace):
    if args.output.is_dir():
        print(f"Output {args.output} is a directory, cannot export graph.")
        sys.exit(234)
    elif args.output.is_file():
        confirm = input(f"Overwrite {args.output.absolute()} [Yes(ENTER)/No(Any key)]?")
        if confirm != "":
            sys.exit(234)
    else:
        print(f"Saving graph as {args.output.absolute()}.")


def _parse_input(args: argparse.Namespace) -> dict:
    if args.input.is_file():
        try:
            sram_dict = read_json(args.input)
            return sram_dict
        except Exception as error:
            print(f"Cannot read in {args.input}: {repr(error)}.")
            sys.exit(234)
    else:
        print(f"Input {args.input} is not a file or does not exist. Exit.")
        sys.exit(234)
