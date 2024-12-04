"""Generate a graph from an SRAM export."""

import json
from pathlib import Path
from typing import Any, Union

import networkx as nx


def read_json(fpath: Union[str, Path]) -> dict:
    """Read sram json export."""
    with open(fpath, "r", encoding="utf-8") as f:
        sram_export = json.load(f)
    return sram_export


def get_nodes_from_dict(sram_org_dict: dict) -> list:
    """Extract node names and types from dictionary on sram organisation level.

    Parameters
    ----------
    sram_org_dict: dict
        A python dictionary generated from an SRAM export.
        Root node must be an Organistation.

    Returns
    -------
    List of nodes per type:
        [{node_name: org_name, label: org_short_name},
         [unit1, unit2, ...],
         [{coll1}, {coll2, ...}],
         {user1: {}, user2: {}}
        ]
        Where coll is a dictionary:
         {node_name: str, label: str, units: list, services: list, users: list[str]}
        Where user is a dictionary:
         {"label": str, "created_by": str, "role": str, "create": list[str], "admin_of": list}

    """
    nodes: list[Any] = []
    org = {"node_name": sram_org_dict["name"]}
    org["label"] = sram_org_dict["short_name"]
    nodes.append(org)
    units = sram_org_dict["units"]
    nodes.append(units)

    colls: list[dict[str, Any]] = []
    users: dict[dict[str, Any]] = {}
    for entry in sram_org_dict["collaborations"]:
        if entry["created_by"] not in users:
            users[entry["created_by"]] = {"admin_of": [], "create": []}
        users[entry["created_by"]]["create"].append(entry["name"])

        coll = {"node_name": entry["name"]}
        coll["label"] = entry["short_name"]
        coll["edges_from"] = entry["units"]
        coll["services"] = []
        for service in entry["services"]:
            coll["services"].append(service["name"])
        coll["groups"] = []
        for group in entry["groups"]:
            coll["groups"].append(group["name"])
        coll["users"] = []
        for u_entry in entry["collaboration_memberships"]:
            coll["users"].append(u_entry["user"]["uid"])
            if u_entry["user"]["uid"] not in users:
                users[u_entry["user"]["uid"]] = {"admin_of": [], "create": []}
            if "label" not in users[u_entry["user"]["uid"]]:
                users[u_entry["user"]["uid"]]["label"] = u_entry["user"]["username"]
            if "created_by" not in users[u_entry["user"]["uid"]]:
                users[u_entry["user"]["uid"]]["created_by"] = u_entry["created_by"]
            if u_entry["role"] == "admin":
                users[u_entry["user"]["uid"]]["admin_of"].append(entry["name"])
        colls.append(coll)

    nodes.append(colls)
    nodes.append(users)
    return nodes


def nodes_to_graph(nodes_sets: list) -> nx.MultiGraph:
    """Add nodes and their adges to the graph.

    Also sets node attributes color_group, node_type and label, which are used
    to create the hierarchical graph and add the coloring.

    Parameters
    ----------
    nodes_sets: list
        List of nodes per type:
        [{node_name: org_name, label: org_short_name},
         [unit1, unit2, ...],
         [{coll1}, {coll2, ...}],
         [{user1}, {user2}, ...],
        ]
        Where coll is a dictionary:
         {node_name: str, label: str, units: list, services: list}
        Where user is a dictionary:
         {node_name: str, label: str, created_by: str, role: [admin, member], coll: str}

    Returns
    -------
    graph: MultiDiGraph

    """
    graph = nx.MultiDiGraph()
    graph.add_node(
        nodes_sets[0]["node_name"],
        label=nodes_sets[0]["label"],
        color_group="entity",
        node_type="ORGANISATION",
    )
    add_units(graph, nodes_sets[1], nodes_sets[0]["node_name"])
    add_collaborations(graph, nodes_sets[2], nodes_sets[0]["node_name"])
    add_users(graph, nodes_sets[3])
    return graph


def add_units(graph: nx.MultiGraph, units: list, org: str):
    """Add units from nodes_set.

    Also sets the correct color_group and node_type attributes.
    """
    for unit in units:
        graph.add_node(unit, color_group="entity", node_type="UNIT")
        graph.add_edge(org, unit, color="black")


def add_collaborations(graph: nx.MultiGraph, collabs: dict, org: str):
    """Add collaborations from nodes_set.

    Also sets the correct label, color_group and node_type attributes.
    """
    for coll in collabs:
        graph.add_node(
            coll["node_name"],
            label=coll["label"],
            color_group="entity",
            node_type="COLLABORATION",
        )
        edges_from = coll.get("edges_from", [])
        if len(edges_from) > 0:
            for from_node in edges_from:
                graph.add_edge(from_node, coll["node_name"], color="black")
        else:
            graph.add_edge(org, coll["node_name"])
        for service in coll["services"]:
            graph.add_node(service, color_group="service", node_type="APPLICATION")
            graph.add_edge(coll["node_name"], service, color="black")
        for group in coll["groups"]:
            graph.add_node(
                f'{coll["node_name"]}_{group}',
                label=group,
                color_group="group",
                node_type="CO_GROUP",
            )
            graph.add_edge(coll["node_name"], f'{coll["node_name"]}_{group}', color="black")
        for user in coll["users"]:
            graph.add_edge(user, coll["node_name"], label="member_of", etype="MEMBER")


def add_users(graph: nx.MultiGraph, users: dict):
    """Add users from node_set."""
    # add al user nodes
    for user, u_dict in users.items():
        graph.add_node(
            user,
            color_group="role" if len(u_dict["admin_of"]) > 0 else "user",
            label=u_dict["label"],
            node_type="COLL_ADMIN" if len(u_dict["admin_of"]) > 0 else "CO_MEMBER",
        )

    # add action edges between users (admin, member) and collaborations
    for user, u_dict in users.items():
        if u_dict["created_by"] in graph:
            graph.add_edge(u_dict["created_by"], user, label="invite", etype="ACTION")
        for item in u_dict["admin_of"]:
            graph.add_edge(user, item, color="black")
        for item in u_dict["create"]:
            graph.add_edge(user, item, label="create", etype="ACTION")
