import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib as plt
import folium
import streamlit as st
from streamlit_folium import folium_static

#Streamlit page config
st.set_page_config(
    layout="wide")

#politie df inladen
df_politie = pd.read_csv('politie.csv')

#politie df opschonen door whitespaces te vervangen in relevante kolommen
df_politie['WijkenEnBuurten'] = df_politie['WijkenEnBuurten'].str.replace(' ', '')
df_politie['Gemeentenaam_2'] = df_politie['Gemeentenaam_2'].str.replace(' ', '')
df_politie['SoortRegio_3'] = df_politie['SoortRegio_3'].str.replace(' ', '')

#politie df subsetten en sorten
df_politie = df_politie.loc[df_politie['WijkenEnBuurten'].str.contains('WK')]
df_politie = df_politie.sort_values(by=["SoortMisdrijf"], ascending = False)

#metadata inladen en mergen met bestaande politie df
df_meta = pd.read_csv('cbs_meta.csv', sep = ';', index_col = 0)
df_politie = df_politie.merge(df_meta, left_on="SoortMisdrijf", right_index = True, how="left")

#geodata inladen en mergen met bestaande politie df
politie_wijken_geo = gpd.read_file("politie_wijken_geo.shp")
df_politie = df_politie.merge(politie_wijken_geo, left_on="WijkenEnBuurten", right_on="WK_CODE", how="left")

#incomplete wijk en regio namen aanvullen
df_politie['Gemeentenaam_2'] = df_politie['Gemeentenaam_2'].apply(lambda x : x if x == "Amsterdam" else "Amsterdam")
df_politie['SoortRegio_3'] = df_politie['SoortRegio_3'].apply(lambda x : x if x == "Wijk" else "Wijk")

#object type vervangen voor float voor visualisaties
df_politie['GeregistreerdeMisdrijven_1'] = pd.to_numeric(df_politie['GeregistreerdeMisdrijven_1'], errors="coerce")

#duplicate kolom droppen
df_politie = df_politie.drop(columns="WK_CODE")
df_politie = df_politie.drop(columns="Title_y")
df_politie['Title'] = df_politie['Title_x']
df_politie = df_politie.drop(columns="Title_x")

#datum kolom splitten om het jaar te extracten en op te slaan in een eigen kolom
df_politie['year'] = df_politie['Perioden'].apply(lambda x: x.split('JJ')[0])

#Total kolom droppen uit dataframe voor beter overzicht in plots
df_politie = df_politie.loc[df_politie['Title'] != "Totaal misdrijven"]

#Groupby aanmaken voor plots
groupbyWijk = df_politie.groupby(by=['WK_NAAM'])['GeregistreerdeMisdrijven_1'].sum().to_frame().reset_index()
groupbyWijk = groupbyWijk.sort_values(by="GeregistreerdeMisdrijven_1", ascending = False).iloc[0:20]
groupbyTitle = df_politie.groupby(by=['Title'])['GeregistreerdeMisdrijven_1'].sum().to_frame().reset_index()
groupbyTitle = groupbyTitle.loc[groupbyTitle['Title'] != "Totaal misdrijven"].sort_values(by="GeregistreerdeMisdrijven_1", ascending = False).iloc[0:20]
groupbyYearTitle = df_politie.groupby(by=['year', 'Title'])['GeregistreerdeMisdrijven_1'].sum().to_frame().reset_index()
groupbyYearTitle = groupbyYearTitle.loc[groupbyYearTitle['Title'] != "Totaal misdrijven"]
                             
#Plotly chart van totaal aantal misdrijven per regio
fig1 = px.bar(groupbyWijk,x='WK_NAAM',y='GeregistreerdeMisdrijven_1')
                             
#Plotly chart van totaal aantal misdrijven per type misdrijf
fig2 = px.bar(groupbyTitle,x='Title',y='GeregistreerdeMisdrijven_1')

#Plotly scatter van type misdrijven per jaar
fig3 = px.scatter(groupbyYearTitle,x='year',y='GeregistreerdeMisdrijven_1',color='Title')
                             
#data mergen en groupby'en voor de folium map
df_politie_wijken = df_politie.loc[df_politie['Title'] != "Totaal misdrijven"].groupby('WK_NAAM')['GeregistreerdeMisdrijven_1'].sum().to_frame().reset_index()
df_politie_wijken_merged = df_politie_wijken.merge(politie_wijken_geo,on="WK_NAAM", how="left")
df_politie_wijken_merged = df_politie_wijken_merged.sort_values(by="GeregistreerdeMisdrijven_1", ascending=False, ignore_index=True)
                             
#Folium choropleth opstellen
geo_df = gpd.GeoDataFrame(data=df_politie_wijken_merged, geometry="geometry")

geo_df = geo_df.to_crs(epsg = 4326)

geo = gpd.GeoSeries(geo_df.set_index('WK_CODE')['geometry']).to_json()

m = folium.Map(location=[52.3568117, 4.9111453], zoom_start=11)
folium.Choropleth(
    geo_data = geo,
    name = 'Choropleth',
    data = geo_df,
    columns = ['WK_CODE','GeregistreerdeMisdrijven_1'],
    key_on = 'feature.id',
    fill_color = 'Reds',
    fill_opacity = 0.8,
    line_opacity = 1,
    legend_name = 'Geregistreerde misdrijven',
    smooth_factor=  0
).add_to(m)

#Bovenstaande plotly charts in columns op streamlit weergeven
col1, col2 = st.columns(2)
with col1:
    tab1, tab2 = st.tabs(['Visualisatie','Bron'])
    with tab1:
        tab1.plotly_chart(fig1)
    with tab2:
        tab2.subheader("Bron")
        tab2.write("Hier komt de bron")
                             
with col2:
    tab3, tab4 = st.tabs(['Visualisatie','Bron'])
    with tab3:
        tab3.plotly_chart(fig2)
    with tab4:
        tab4.subheader("Bron")
        tab4.write("Hier komt de bron")

                             
#Folium map weergeven                             
folium_static(m)
