"""Webtool to explore and interact with surf iam graphs."""


import streamlit as st

from surfiamviz.webutils.createtab import create
from surfiamviz.webutils.exampletab import examples
from surfiamviz.webutils.exploretab import explore
from surfiamviz.webutils.welcometab import welcome

pg = st.navigation([welcome, examples, explore, create])
pg.run()
