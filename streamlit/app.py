#package imports
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
#Dashboard title
st.title("Misdrijven in Amsterdam in de periode van 2016 t/m 2021")

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

df_politie['year'] = pd.to_numeric(df_politie['year'], errors="coerce")

#Total kolom en incomplete jaren droppen uit dataframe voor beter overzicht in plots
df_politie = df_politie.loc[(df_politie['Title'] != "Totaal misdrijven") & (~df_politie['year'].isin([2015, 2014, 2013]))]

#Filters opstellen voor het dashboard
col3, col4 = st.columns(2)

with col3:
    #Algemeen filter opstellen voor het dashboard
    wijkFilter = st.multiselect(
    'Selecteer hier de gewenste wijken:',
    ['Driemond', 'Gein', 'Apollobuurt', 'Holendrecht/Reigersbos',
       'Amstel III/Bullewijk', 'Nellestein', 'Bijlmer Centrum (D,F,H)',
       'Bijlmer Oost (E,G,K)', 'Overtoomse Veld', 'Buitenveldert-Oost',
       'Slotervaart Zuid', 'Buitenveldert-West', 'Sloter-/Riekerpolder',
       'Westlandgracht', 'Elzenhagen', 'Oude Pijp', 'Slotervaart Noord',
       'De Punt', 'Middelveldsche Akerpolder', 'Lutkemeer/Ookmeer',
       'Osdorp-Midden', 'Osdorp-Oost', 'Slotermeer-Zuidwest', 'Eendracht',
       'Geuzenveld', 'Chassébuurt', 'Slotermeer-Noordoost',
       'Noordelijke IJ-oevers Oost', 'Tuindorp Nieuwendam', 'Waterland',
       'Noordelijke IJ-oevers West', 'Waterlandpleinbuurt',
       'Buikslotermeer', 'Banne Buiksloot', 'Betondorp', 'Kadoelen',
       'Tuindorp Oostzaan', 'Oostzanerwerf', 'Indische Buurt Oost',
       'Tuindorp Buiksloot', 'Nieuwendammerdijk/Buiksloterdijk',
       'Frankendael', 'Volewijck', 'IJplein/Vogelbuurt',
       'Prinses Irenebuurt e.o.', 'Omval/Overamstel', 'Middenmeer',
       'Rijnbuurt', 'Scheldebuurt', 'IJburg Zuid', 'IJselbuurt',
       'IJburg Oost', 'Museumkwartier', 'Stadionbuurt', 'Willemspark',
       'Westindische Buurt', 'Hoofddorppleinbuurt', 'Schinkelbuurt',
       'Landlust', 'Van Galenbuurt', 'Hoofdweg e.o.', 'Geuzenbuurt',
       'Erasmuspark', 'De Kolenkit', 'IJburg West', 'Sloterdijk',
       'Zeeburgereiland/Nieuwe Diep', 'Transvaalbuurt', 'Centrale Markt',
       'Oostelijk Havengebied', 'Indische Buurt West', 'Dapperbuurt',
       'Weesperzijde', 'Oosterparkbuurt', 'Zuid Pijp', 'Nieuwe Pijp',
       'Zuidas', 'Houthavens', 'Overtoomse Sluis', 'Vondelbuurt',
       'Kinkerbuurt', 'Helmersbuurt', 'Van Lennepbuurt', 'Da Costabuurt',
       'Frederik Hendrikbuurt', 'Spaarndammer- en Zeeheldenbuurt',
       'Staatsliedenbuurt', 'Grachtengordel-Zuid',
       'Westelijk Havengebied', 'Bedrijventerrein Sloterdijk',
       'Oostelijke Eilanden/Kadijken', 'Jordaan', 'Weesperbuurt/Plantage',
       'De Weteringschans', 'Haarlemmerbuurt', 'Nieuwmarkt/Lastage',
       'Grachtengordel-West', 'Burgwallen-Oude Zijde',
       'Burgwallen-Nieuwe Zijde'],
        [])

with col4:
#rangeslider voor de jaren opstellen
    yearFilter = st.slider(
        'Selecteer de gewenste jaren',
        int(df_politie['year'].min()), int(df_politie['year'].max()), ())

yearFilter = [*range(yearFilter[0], yearFilter[1]+1, 1)]

#If statement om het dashboard te laten reageren op het de filters
if wijkFilter:
    df_politie = df_politie.loc[df_politie['WK_NAAM'].isin(wijkFilter)]
    
if yearFilter:
    df_politie = df_politie.loc[df_politie['year'].isin(yearFilter)]

#df_wijken_info inladen
df_wijken_info = pd.read_csv('wijken_info.csv')    

#Groupby aanmaken voor plots
groupbyWijk = df_politie.groupby(by=['WK_NAAM'])['GeregistreerdeMisdrijven_1'].sum().to_frame().reset_index()
groupbyWijk = groupbyWijk.sort_values(by="GeregistreerdeMisdrijven_1", ascending = False).iloc[0:20]
groupbyTitle = df_politie.groupby(by=['Title'])['GeregistreerdeMisdrijven_1'].sum().to_frame().reset_index()
groupbyTitle = groupbyTitle.loc[groupbyTitle['Title'] != "Totaal misdrijven"].sort_values(by="GeregistreerdeMisdrijven_1", ascending = False).iloc[0:20]
groupbyYearTitle = df_politie.groupby(by=['year', 'Title'])['GeregistreerdeMisdrijven_1'].sum().to_frame().reset_index()
groupbyYearTitle = groupbyYearTitle.loc[groupbyYearTitle['Title'] != "Totaal misdrijven"]
df_politie_grouped = df_politie.groupby(['WK_NAAM', 'WijkenEnBuurten', 'year'])['GeregistreerdeMisdrijven_1'].sum().to_frame().reset_index()
df_politie_grouped = df_politie_grouped.merge(df_wijken_info, left_on=['WijkenEnBuurten','year'], right_on = ["gwb_code", "year"], how="left")
groupbyYear = df_politie.groupby(by=['year'])['GeregistreerdeMisdrijven_1'].sum().to_frame().reset_index()
groupbyYear = groupbyYear.loc[groupbyTitle['Title'] != "Totaal misdrijven"].sort_values(by="GeregistreerdeMisdrijven_1", ascending = False).iloc[0:20]

                             
#Plotly chart van totaal aantal misdrijven per regio
fig1 = px.bar(groupbyWijk,x='WK_NAAM',y='GeregistreerdeMisdrijven_1',labels={
                     "GeregistreerdeMisdrijven_1": "Totaal aantal misdrijven",
                     "WK_NAAM": "Wijken"},
                title="Aantal misdrijven van de top 20 wijken")
                             
#Plotly chart van totaal aantal misdrijven per type misdrijf
fig2 = px.bar(groupbyTitle,x='Title',y='GeregistreerdeMisdrijven_1',labels={
                     "GeregistreerdeMisdrijven_1": "Totaal aantal misdrijven",
                     "Title": "Type misdrijven"},
                title="Aantallen van de top 20 misdrijven")

#Plotly scatter van type misdrijven per jaar
fig3 = px.box(df_politie_grouped, x='year',y='GeregistreerdeMisdrijven_1', labels={
                     "GeregistreerdeMisdrijven_1": "Totaal aantal misdrijven",
                     "year": "Jaar"},
                title="Aantal misdrijven per jaar per wijk")

#Pie chart van de verdeling van de misdrijven per type misdrijf
fig5 = px.pie(groupbyTitle, values='GeregistreerdeMisdrijven_1', names='Title', title='Aantal misdrijven per type misdrijf',
              labels={'Title':'Misdrijf','GeregistreerdeMisdrijven_1' : 'Aantal misdrijven'})

#Line chart van misdrijven per jaar
fig6 = px.line(groupbyYear, x='year',y='GeregistreerdeMisdrijven_1', title='Aantal misdrijven per jaar',
               labels={'year':'Jaar','GeregistreerdeMisdrijven_1' : 'Aantal misdrijven'})

               
#data mergen en groupby'en voor de folium map
df_politie_wijken = df_politie.loc[df_politie['Title'] != "Totaal misdrijven"].groupby('WK_NAAM')['GeregistreerdeMisdrijven_1'].sum().to_frame().reset_index()
df_politie_wijken_merged = df_politie_wijken.merge(politie_wijken_geo,on="WK_NAAM", how="left")
df_politie_wijken_merged = df_politie_wijken_merged.sort_values(by="GeregistreerdeMisdrijven_1", ascending=False, ignore_index=True)

# removed outliers by excluding 'GeregistreerdeMisdrijven_1' <= 150
test = df_politie.loc[(df_politie["Title"] == "1.1.1 Diefstal/inbraak woning") & (df_politie["GeregistreerdeMisdrijven_1"] <= 150)].groupby(['WK_NAAM', 'WijkenEnBuurten', 'year'])['GeregistreerdeMisdrijven_1'].sum().to_frame().reset_index()
test = test.merge(df_wijken_info, left_on=['WijkenEnBuurten','year'], right_on = ["gwb_code", "year"], how="left")

#scatterplot misdrijven per aantal inwoners
fig4 = px.scatter(test, x='a_inw',y='GeregistreerdeMisdrijven_1', color='year', trendline="ols",labels={
                     "GeregistreerdeMisdrijven_1": "Totaal # woninginbraken en -diefstallen",
                     "a_inw": "Totaal # inwoners"},
                title="Aantal woninginbraken en -diefstallen tegenover aantal inwoners")
                            
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
        tab2.write("Voor deze plot is gebruik gemaakt van 2 bronnen.") 
        tab2.write("Het aantal misdrijven per wijk en de top 20 misdrijven komt van de open politiedata van het CBS. Deze is hier te vinden: https://data.politie.nl/portal.html?_la=nl&_catalog=Politie&tableId=47022NED&_theme=107.")
        tab2.write("Gezien in bovenstaande dataset de wijknamen niet staan, hebben wij een ander dataset gevonden met de wijkcodes en bijbehorende wijknamen. Deze hebben wij gemerged om misdrijven per wijknaam te kunnen laten zien. Deze is hier terug te vinden: https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2021/")
        
with col2:
    tab3, tab4 = st.tabs(['Visualisatie','Bron'])
    with tab3:
        tab3.plotly_chart(fig2)
    with tab4:
        tab4.write("Voor deze plot is gebruik gemaakt van 1 bron.")
        tab4.write("Het aantal misdrijven per type misdrijf is te vinden in via de volgende link: https://data.politie.nl/portal.html?_la=nl&_catalog=Politie&tableId=47022NED&_theme=107.")
        
col5, col6 = st.columns(2)
with col5:
    tab5, tab6 = st.tabs(['Visualisatie','Bron'])
    with tab5:
        tab5.plotly_chart(fig3)
    with tab6:
        tab6.write("Voor deze plot is gebruik gemaakt van 2 bronnen.")
        tab6.write("De data over de misdrijven per jaar is gehaald uit de open politiedata bron van het CBS. Deze is via deze link terug te vinden: https://data.politie.nl/portal.html?_la=nl&_catalog=Politie&tableId=47022NED&_theme=107.")
        tab6.write("Om goed de outliers te laten zien hebben we gekozen om de misdrijven per wijk in de boxplot te plotten. De data over de wijken die wij hiervoor gebruikt hebben is hier terug te vinden: https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2021/.")
                             
with col6:
    tab7, tab8 = st.tabs(['Visualisatie','Bron'])
    with tab7:
        tab7.plotly_chart(fig4)
    with tab8:
        tab8.write("Voor deze scatterplot is gebruik gemaakt van 2 bronnen.")
        tab8.write("De data over het aantal inwoners komt voort uit de kerncijfers per wijk en buurt. Deze datasets zijn per jaar opgesteld en hier hebben wij 2016 t/m 2021 van gebruikt. Deze data is hier terug te vinden: https://www.cbs.nl/nl-nl/reeksen/kerncijfers-wijken-en-buurten.")
        tab8.write("Daarnaast zijn het aantal misdrijven in deze scatterplot te zien. Deze data komt voort uit de open politiedata van het CBS. Deze data is hier terug te vinden: https://data.politie.nl/portal.html?_la=nl&_catalog=Politie&tableId=47022NED&_theme=107.")

col7, col8 = st.columns(2)
with col7:
    tab9, tab10 = st.tabs(['Visualisatie','Bron'])
    with tab9:
        tab9.plotly_chart(fig6)
    with tab10:
        tab10.write("Voor deze visualisatie is gebruik gemaakt van 2 bronnen.")
        tab10.write("De data over het aantal inwoners komt voort uit de kerncijfers per wijk en buurt. Deze datasets zijn per jaar opgesteld en hier hebben wij 2016 t/m 2021 van gebruikt. Deze data is hier terug te vinden: https://www.cbs.nl/nl-nl/reeksen/kerncijfers-wijken-en-buurten.")
        tab10.write("Daarnaast zijn het aantal misdrijven in deze plot te zien. Deze data komt voort uit de open politiedata van het CBS. Deze data is hier terug te vinden: https://data.politie.nl/portal.html?_la=nl&_catalog=Politie&tableId=47022NED&_theme=107.")
        
with col8:
    tab11, tab12 = st.tabs(['Visualisatie','Bron'])
    with tab11:
        tab11.plotly_chart(fig5)
    with tab12:
        tab12.write("Voor deze pie chart is gebruik gemaakt van 1 bron.")
        tab12.write("Deze visualisatie is opgesteld uit data van de open politiedata van het CBS. Dit zijn het aantal misdrijven per type. Deze data is hier terug te vinden: https://data.politie.nl/portal.html?_la=nl&_catalog=Politie&tableId=47022NED&_theme=107.")
        
#Folium map weergeven                             
folium_static(m,width=1250)
