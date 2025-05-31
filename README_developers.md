# Some notes for developers

## Code structure

```
├── configs
│   └── sram_config.toml
├── data
│   └── sram_test_org.json
├── example_graphs
│   └── sram_examples.toml
├── gravis_html
│   └── app_graph.html
├── LICENSE
├── pyproject.toml
├── README_developers.md
├── README.md
├── surfiamviz
│   ├── __init__.py
│   ├── __main__.py
│   ├── graph_from_config.py
│   ├── graph_from_sram_json.py
│   ├── utils.py
│   ├── webtool.py
│   └── webutils
│       ├── all_nodes.html
│       ├── createtab.py
│       ├── exampletab.py
│       ├── exploretab.py
│       ├── utils.py
│       └── welcometab.py
└── tests
    ├── conftest.py
    ├── test_config.py
    ├── test_sram.py
    └── testdata
    	 ├── config.toml
    	 └── sram.json
```

The code implements a command line tool and a web applictaion (streamlit) which is started through the commandline interface.

## Input and output data

### Input data

- Example data for an SRAM organisation can be found in `data/sram_test_org.json`
- An example of a preconfigured network can be found in `example_graphs/sram_examples.toml`

To plot the networks one needs a configuration file which can be found in `configs/sram_config.toml`
 

### Output data

The command line interface allows users to define the output path. The web application stored rendered networks in the folder `gravis_html`. The html files in this folder will be overwritten by the web application and serves as storage to load rendered networks. 

## Code

- Commandline interface `surfiamviz/__main__py`
- The python files in `surfiamviz ` contain the main code to build and render the networks
	- Build and render a graph from an example toml: `graph_from_config.py`
	- Build and render a graph from an organisation json: `graph_from_sram_json.py`
	- The webtool draws on the functions above. The code to start the webapp can be found in `webtool.py`. It defines a streamlit app and several tabs.
- The web app's functionality and tabs can be found in the folder `webutils`. Each tab is defined by an own python script.

## Tests

The GitHub repository contains a workflow which checks the code with *ruff* and *pylint*. It also runs `pytest` on the data in `tests/testdata`.

