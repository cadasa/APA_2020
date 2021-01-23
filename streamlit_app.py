import pandas as pd
import re
import time
import string
import datetime
import os
import streamlit as st
import altair as alt
import geopandas as gpd
from streamlit_folium import folium_static
from streamlit_vega_lite import vega_lite_component, altair_component
import folium
from folium.plugins import MiniMap

@st.cache(allow_output_mutation=True)
def read_fielddata():
    gdf_dsc = gpd.read_file("https://factpages.npd.no/downloads/shape/dscArea.zip")
    gdf_dsc = gdf_dsc.loc[gdf_dsc.loc[:,'geometry']!=None,:]
    gdf_pl = gpd.read_file("APA2020_offered.shp")
    gdf_pl = gdf_pl.loc[gdf_pl.loc[:,'geometry']!=None,:]
    gdf_pl['PL'] = gdf_pl['PL_nr']
    gdf_pl.loc[gdf_pl.loc[:,'OBJECTID']==32,'PL_nr'] = '1049B'
    df_pl = pd.read_excel('apa2020_partners.xlsx')

    gdf_pl2 = gpd.read_file("APA2019_offered.shp")
    gdf_pl2 = gdf_pl2.loc[gdf_pl2.loc[:,'geometry']!=None,:]
    gdf_pl2['PL'] = gdf_pl2['PL_nr']
    df_pl2 = pd.read_excel('apa-2019-partners.xlsx', skiprows=[0])
    df_pl2 = df_pl2.rename(columns={"Blocks": "Block(s)"})
    df_pl2['PL']=df_pl2['PL'].astype(str)
    return (gdf_dsc,gdf_pl,df_pl,gdf_pl2,df_pl2)

def main():
    st.sidebar.title("Navigation")
    col1, col2,col3 = st.sidebar.beta_columns([0.5,9.0,0.5])
    years = col2.select_slider("Slide to select:",options=['APA-2019', 'APA-2020'],value='APA-2020')
    if years == 'APA-2019':
        st.title("APA-2019: Awards in Predefined Areas 2019")
        col2.info(
                        '👉 Click on each company to see all of its APA-2019 PL.'
                        ' Individual PL can be viewed using the select-box below.')
        apa2020(years)
    else:
        st.title("APA-2020: Awards in Predefined Areas 2020")
        col2.info(
                        '👉 Click on each company to see all of its APA-2020 PL.'
                        ' Individual PL can be viewed using the select-box below.')
        apa2020(years)

    st.sidebar.markdown(
        "**Made with [NORDLYS](https://share.streamlit.io/cadasa/nordlys)**"
        )
    st.sidebar.markdown(
        "**Based on data from [NPD](https://www.npd.no/en/facts/production-licences/licensing-rounds/apa-2020/)**"
        )
    st.sidebar.markdown(
        "**Created by [KHANH NGUYEN](mailto:khanhduc@gmail.com)**")
    return None

def apa2020(years):
    col1, col2,col3 = st.sidebar.beta_columns([0.5,9.0,0.5])
    if years == 'APA-2019':
        gdf_dsc,gdf_pl1,df_pl1,gdf_pl2,df_pl2 = read_fielddata()
        gdf_pl = gdf_pl2
        df_pl = df_pl2
#        st.dataframe(df_pl)
#        st.dataframe(df_pl1)
#        st.stop
    else:
        gdf_dsc,gdf_pl1,df_pl1,gdf_pl2,df_pl2 = read_fielddata()
        gdf_pl = gdf_pl1
        df_pl = df_pl1

    df_pl = df_pl.loc[df_pl.loc[:,'O/P'].notnull(),:].reset_index(drop=True)
    df_pl['%']=df_pl['%'].astype(str)
    df_pl['Companies'] = df_pl.groupby('PL')['Partners'].transform(lambda x: ",\n".join(x))
    df_pl['Operatorships'] = df_pl.groupby('PL')['O/P'].transform(lambda x: ", ".join(x))
    df_pl['Percentages'] = df_pl.groupby('PL')['%'].transform(lambda x: "%, ".join(x))
#    st.dataframe(df_pl)
#    st.stop()
    plnames = df_pl.drop_duplicates(subset = ['PL'])['PL'].to_list()
#    a = set(gdf_pl['PL_nr'].unique())
#    b = set(df_pl['PL'])
#    fieldnames = list(a.difference(b))
#    st.write(plnames)
#    st.write(len(plnames))
#    st.stop()
    all = ['OVERVIEW']
    plnames = all + plnames
    fields = col2.selectbox('Select Production Licences:',plnames)
    if fields == 'OVERVIEW':
        st.subheader(f"""**Ownership interests of {"".join(str(len(df_pl['PL'].unique())))} production licences have been offered to {"".join(str(len(df_pl['Partners'].unique())))} companies**""")
        @st.cache
        def altair_bar():
            pts = alt.selection_single(encodings=["y"], name="pts")
            return(
                alt.Chart(df_pl).mark_bar(size=12).encode(
                    x = alt.X('count(PL):Q',title='Numbers of Production Licence'),
                    y = alt.Y('Partners:N', title=None,sort='-x'),
                    tooltip=[alt.Tooltip('Partners:N',title='Company:'),
                            alt.Tooltip('O/P:N',title='Ownership:'),
                            alt.Tooltip('count():Q',title='Numbers of licences:')],
                    color=alt.Color('O/P',legend=alt.Legend(strokeColor='black',padding=5,fillColor='white',title='Ownership',columns=2,offset=5,orient='bottom-right')),
                    opacity=alt.condition(pts, alt.value(1.0), alt.value(0.2)),
        #            size=alt.Size('Remaining_OE:Q', legend=alt.Legend(title='Remaining Reserves in MSM³OE',orient='bottom'),
        #                            scale=alt.Scale(range=[10, 1000]))
                ).properties(title = 'PL Ownership per Companies',
                    width=210,
                    height=465
                ).add_selection(
                    pts
                )
            )
        col1, col2 = st.beta_columns([5,5])
        with col2.beta_container():
            event_dict = altair_component(altair_chart=altair_bar())
        r = event_dict.get("Partners")
        PL_names = df_pl.drop_duplicates(subset = ['PL'])['PL'].to_list()
#        pl_map = df_pl.loc[(df_pl.loc[:,'O/P']=='O'),:].reset_index(drop=True)
        field_info = df_pl.loc[(df_pl.loc[:,'O/P']=='O'),:].reset_index(drop=True)
        field_info['O/P'] = field_info['Operatorship_list']
        if r:
            field_info = df_pl.loc[(df_pl.loc[:,'Partners']==r[0]),:].reset_index(drop=True)
            PL_names = field_info['PL'].to_list()
#            pl_map = df_pl.loc[df_pl.loc[:,'PL'].isin(PL_names),:].reset_index(drop=True)
        with st.beta_expander("EXPAND TO SEE DATA TABLE"):
            st.subheader(f"""**Data table showing all ownership**""")
            field_info.index = field_info.index + 1
            st.table(field_info[['PL','Block(s)','Companies','Operatorships','Percentages']])

        with col1.beta_container():
#            dsc_map = gdf_dsc.loc[(gdf_dsc.loc[:,'fieldName']==fields)&((gdf_dsc.loc[:,'curActStat']=='Producing')|(gdf_dsc.loc[:,'curActStat']=='Shut down')),:]
#            gdf_dsc2 = gdf_dsc
#            gdf_dsc = gdf_dsc.loc[gdf_dsc.loc[:,'geometry']!=None,:]
            st.write('')
            gdf_dsc['Disc./Field'] = gdf_dsc.apply(lambda row: row.fieldName if row.fieldName else row.discName, axis=1)
            dsc_map = gdf_pl.loc[gdf_pl.loc[:,'PL'].isin(PL_names),:].reset_index(drop=True)
            dsc_map = dsc_map.merge(field_info,"left",left_on='PL',right_on='PL',
                        indicator=False, validate='many_to_many')
#            dsc_map2 = dsc_map.iloc[0:1]
#            st.table(dsc_map)
#            if len(dsc_map2)!=0 :
#            dsc_map2['center_point'] = dsc_map2['geometry'].centroid
#            lon = dsc_map2.center_point.map(lambda p: p.x)
#            lat = dsc_map2.center_point.map(lambda p: p.y)

    # center on the middle of the field
            m = folium.Map(width=400,height=500,location=[65.562, 17.704], tiles='cartodbpositron', zoom_start=4)

            style_function = lambda x: {'fillColor': "gray", "weight": 0.1, 'color': "gray"}
            highlight_function = lambda x: {'fillColor': "black", "weight": 0.1, 'color': "black"}
#            tooltip = folium.GeoJsonTooltip(fields=['PL'])
#            style_function1 = lambda x: {'fillColor': "None", "weight": 0.5, 'color': "blue"}
#            highlight_function1 = lambda x: {'fillColor': "None", "weight": 1.0, 'color': "darkblue"}
            tooltip1 = folium.GeoJsonTooltip(fields=['Disc./Field'])
#            folium.GeoJson(data=gdf_pl,style_function=style_function1,highlight_function =highlight_function1, tooltip=tooltip).add_to(m)
            folium.GeoJson(data=gdf_dsc,style_function=style_function,highlight_function =highlight_function, tooltip=tooltip1).add_to(m)
#                style_function2 = lambda x: {'fillColor': "green" if x['properties']['Dctype']=='OIL' else ( "red" if x['properties']['Dctype']=='GAS' else ("orange" if x['properties']['Dctype']=='OIL/GAS' else "blue")),
#                                            "weight": 1,
#                                            'color': "green" if x['properties']['Dctype']=='OIL' else ( "red" if x['properties']['Dctype']=='GAS' else ("orange" if x['properties']['Dctype']=='OIL/GAS' else "blue"))}
#                highlight_function2 = lambda x: {'fillColor': "darkgreen" if x['properties']['Dctype']=='OIL' else ( "darkred" if x['properties']['Dctype']=='GAS' else ("darkorange" if x['properties']['Dctype']=='OIL/GAS' else "darkblue")),
#                                            "weight": 2,
#                                            'color': "darkgreen" if x['properties']['Dctype']=='OIL' else ( "darkred" if x['properties']['Dctype']=='GAS' else ("darkorange" if x['properties']['Dctype']=='OIL/GAS' else "darkblue"))}

#            folium_static(m)
#            st.stop()
            tooltip2 = folium.GeoJsonTooltip(fields=['PL', 'Companies','Ownerships','Percentages'],
                                              labels=True,
                                              sticky=False,
                                              toLocaleString=False)
            style_function2 = lambda x: {'fillColor': "steelblue" if x['properties']['O/P']=='O' else ("orange" if x['properties']['O/P']=='P' else "blue"),
                                            "weight": 1,
                                         'color': "steelblue" if x['properties']['O/P']=='O' else ("orange" if x['properties']['O/P']=='P' else "blue")}
            highlight_function2 = lambda x: {'fillColor': "steelblue" if x['properties']['O/P']=='O' else ("darkorange" if x['properties']['O/P']=='P' else "darkblue"),
                                            "weight": 2,
                                         'color': "steelblue" if x['properties']['O/P']=='O' else ("darkorange" if x['properties']['O/P']=='P' else "darkblue")}
            folium.GeoJson(data=dsc_map,style_function=style_function2,highlight_function =highlight_function2, tooltip=tooltip2).add_to(m)

        # call to render Folium map in Streamlit
            minimap = MiniMap(toggle_display=True,position="topright",tile_layer="cartodbpositron",zoom_level_offset=-3,width=120, height=150)
            minimap.add_to(m)
            folium_static(m)
#        st.dataframe(df_apa)
#        st.dataframe(df_pl)
#        df_plp = df_pl.loc[df_pl.loc[:,'O/P']=='P',:][['PL','Partners','%']]
#        df_plp.pivot(index='PL', columns='Partners', values='%').reset_index()
#        st.dataframe(df_plp)
#        st.stop()

    else:
        col1, col2 = st.beta_columns([5,5])

        col2.subheader(f"""**Production License {"" .join(str(fields))}'s info:**""")
#        with col2.beta_expander("GENERAL", expanded = True):
        field_info = df_pl.loc[(df_pl.loc[:,'PL']==fields),:].reset_index(drop=True)
        field_info.index = field_info.index + 1
#        field_info = field_info.T
#        col2.write(" ")
        col2.markdown(f"""**BLOCK(S):  {"".join(str(field_info['Block(s)'].to_list()[0]))}**""")
        with col2.beta_expander("Operator & Partners:",expanded=True):
            st.table(field_info[['Partners', 'O/P', '%']])
#        st.stop()

        col1.subheader(f"""**Production License {"" .join(str(fields))}'s location**""")
#        st.dataframe(df_dsc)
        with col1.beta_container():
#            dsc_map = gdf_dsc.loc[(gdf_dsc.loc[:,'fieldName']==fields)&((gdf_dsc.loc[:,'curActStat']=='Producing')|(gdf_dsc.loc[:,'curActStat']=='Shut down')),:]
#            gdf_dsc2 = gdf_dsc
#            gdf_dsc = gdf_dsc.loc[gdf_dsc.loc[:,'geometry']!=None,:]
            gdf_dsc['Disc./Field'] = gdf_dsc.apply(lambda row: row.fieldName if row.fieldName else row.discName, axis=1)
            dsc_map = gdf_pl.loc[gdf_pl.loc[:,'PL']==fields,:].reset_index(drop=True)
            dsc_map2 = dsc_map.iloc[0:1]
#            st.table(dsc_map)
#            if len(dsc_map2)!=0 :
            dsc_map2['center_point'] = dsc_map2['geometry'].centroid
            lon = dsc_map2.center_point.map(lambda p: p.x)
            lat = dsc_map2.center_point.map(lambda p: p.y)
    # center on the middle of the field
            m = folium.Map(width=400,height=500,location=[lat, lon], tiles='cartodbpositron', zoom_start=7)

            style_function = lambda x: {'fillColor': "gray", "weight": 0.1, 'color': "gray"}
            highlight_function = lambda x: {'fillColor': "black", "weight": 0.1, 'color': "black"}
            tooltip = folium.GeoJsonTooltip(fields=['PL'])
            style_function1 = lambda x: {'fillColor': "blue", "weight": 0.1, 'color': "blue"}
            highlight_function1 = lambda x: {'fillColor': "darkblue", "weight": 0.5, 'color': "darkblue"}
            tooltip1 = folium.GeoJsonTooltip(fields=['Disc./Field'])
            folium.GeoJson(data=gdf_pl,style_function=style_function1,highlight_function =highlight_function1, tooltip=tooltip).add_to(m)
            folium.GeoJson(data=gdf_dsc,style_function=style_function,highlight_function =highlight_function, tooltip=tooltip1).add_to(m)
#                style_function2 = lambda x: {'fillColor': "green" if x['properties']['Dctype']=='OIL' else ( "red" if x['properties']['Dctype']=='GAS' else ("orange" if x['properties']['Dctype']=='OIL/GAS' else "blue")),
#                                            "weight": 1,
#                                            'color': "green" if x['properties']['Dctype']=='OIL' else ( "red" if x['properties']['Dctype']=='GAS' else ("orange" if x['properties']['Dctype']=='OIL/GAS' else "blue"))}
#                highlight_function2 = lambda x: {'fillColor': "darkgreen" if x['properties']['Dctype']=='OIL' else ( "darkred" if x['properties']['Dctype']=='GAS' else ("darkorange" if x['properties']['Dctype']=='OIL/GAS' else "darkblue")),
#                                            "weight": 2,
#                                            'color': "darkgreen" if x['properties']['Dctype']=='OIL' else ( "darkred" if x['properties']['Dctype']=='GAS' else ("darkorange" if x['properties']['Dctype']=='OIL/GAS' else "darkblue"))}

#            folium_static(m)
#            st.stop()
            style_function2 = lambda x: {'fillColor': "red", "weight": 0.5, 'color': "red"}
            highlight_function2 = lambda x: {'fillColor': "darkred", "weight": 1, 'color': "darkred"}
            tooltip2 = folium.GeoJsonTooltip(fields=['PL'])
            folium.GeoJson(data=dsc_map,style_function=style_function2,highlight_function =highlight_function2, tooltip=tooltip2).add_to(m)

        # call to render Folium map in Streamlit
            minimap = MiniMap(toggle_display=True,position="topright",tile_layer="cartodbpositron",zoom_level_offset=-5,width=120, height=150)
            minimap.add_to(m)
            folium_static(m)

    return None

    # ----------------------
def _max_width_():
    max_width_str = f"max-width: 2000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )







if __name__ == "__main__":
    st.set_page_config(page_title="APA-2020", page_icon='logo.jpg', layout='wide', initial_sidebar_state='auto')
    _max_width_()

    main()
