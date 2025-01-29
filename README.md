# surfiam-graph-vis
Python code to visualise preconfigured SRAM graphs, SRAM json exports of an organisation and getting statistics from such a json.

# Dependencies
- networkx
- pyvis

# Installation

## Install a git branch as python package

```
pip install git+https://github.com/chStaiger/surfiam-graph-vis.git@<branch>
```

## Checkout code and install python package

```
# HTTP
git clone https://github.com/chStaiger/surfiam-graph-vis.git
# SSH
git clone git@github.com:chStaiger/surfiam-graph-vis.git

cd surfiam-graph-vis
pip install -e .
```


# Usage

To run the main script simply type in the terminal:
```
surfiamviz
```

# Configuration
Standard graphs, node colours and edge colours can be submitted to the tool through a config file. We provide an [example config file](configs/sram_config.toml) to illustrate how node and edge type determine the colour and to show two standard example graphs for an SRAM collaboration.

## Configured SRAM graphs
### Adding a new graph section

To define an SRAM graph start with a new section in the configuration toml-file:

```
[my_graph]
```

The name `my_graph` will be used in the commandline tool to determine which graph will be plotted:

```
surfiamviz graph -g my_graph
```

### Adding new edge sets
In the new section you can set new edges and give the edges a type:

```
entities.edges = [["ORGANISATION", "COLLABORATION"],
                  ["COLLABORATION", "APP_GROUP"],
                  ["COLLABORATION_1", "CO_GROUP"]
                 ]
             
entities.type = "BACKBONE"
```
Of course you can define several edge sets of different types.

The edge type, here "BACKBONE" is used in the section `[edge_colors]` to give all edges of the same type a color.

### Nodes 
Edges are defined between two nodes. In the section `node_types` you will find a list of all defined nodes for SRAM. Each node has a name and a level e.g. `ORG_ADMIN.name = "admin"` and `ORG_ADMIN.level`.

The name again groups nodes and gives them a common color as defined in the section `[node_colors]`. E.g. all nodes with the name `admin` will be plotted in green.

The node level determines on which level in the graph hierarchy the nodes of the respective type will be plotted. For SRAM the `ORGANISATION` is the top level indicated by the smallest number and appears in the graphs always on left side of the plot.

### Colours

The names for colours are taken from the [matplotlib colour scheme](https://matplotlib.org/stable/gallery/color/named_colors.html).

## Plotting exported SRAM graphs

To visualise the actual situation of your SRAM organisation you will need an export to a json from the SRAM API:

```
curl -X GET "https://acc.sram.surf.nl/api/organisations/v1" -H  "accept: application/json" -H  "Authorization: Bearer <YOUR TOKEN>" | jq > sram_output.json
```

The file `sram_output.json` is used in the visualisation together with the configuration file to draw the graph:

```
surfiamviz organisation -i sram_output.json -o test.html -c configs/sram_config.toml
```

We provide an example json file in `data/sram_test_org.json`.

The software will set the node types and the edge types. You can steer the colouring of nodes and edges in the [configuration file](configs/sram_config.toml) in the section `[node_colors]` and `[edge_colors]`.