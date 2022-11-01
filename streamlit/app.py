import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib as plt
import folium
import streamlit as st

df_politie = pd.read_csv('politie.csv')

df_politie['WijkenEnBuurten'] = df_politie['WijkenEnBuurten'].str.replace(' ', '')
df_politie['Gemeentenaam_2'] = df_politie['Gemeentenaam_2'].str.replace(' ', '')
df_politie['SoortRegio_3'] = df_politie['SoortRegio_3'].str.replace(' ', '')

df_politie = df_politie.loc[df_politie['WijkenEnBuurten'].str.contains('WK')]
df_politie = df_politie.sort_values(by=["SoortMisdrijf"], ascending = False)

df_meta = pd.read_csv('cbs_meta.csv', sep = ';', index_col = 0)
df_politie = df_politie.merge(df_meta, left_on="SoortMisdrijf", right_index = True, how="left")

st.dataframe(df_politie)
