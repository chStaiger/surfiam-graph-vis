"""welcome tab."""

import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

repo_root = Path(os.path.realpath(__file__)).parent.parent.parent


def welcome():
    """Welcome."""
    st.title("Welcome to SURF's Identity and Access management tools.")
    st.markdown("""
                This app aims to help you to understand SURF's IAM tools.
                We offer:

                - Example graphs which show the different roles and concepts SRAM implements.

                - To visually explore your own SRAM graph for your organisation.

            """)
    with open(repo_root / "surfiamviz/webutils/all_nodes.html", "r", encoding="utf-8") as htmlfile:
        components.html(htmlfile.read(), height=450)
