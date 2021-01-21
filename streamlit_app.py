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

    ctr=gpd.read_file("https://github.com/simonepri/geo-maps/releases/download/v0.6.0/countries-coastline-1km.geo.json")
    no=pd.DataFrame(ctr.loc[ctr.loc[:,'A3']=='NOR',:].reset_index(drop=True)['geometry'])
    poly=no.geometry[0]
    df_coasline_no = pd.DataFrame([])
    for x, y in poly[1].exterior.coords:
        row=pd.DataFrame([['poly_2',x,y]])
        df_coasline_no = df_coasline_no.append(row).reset_index(drop=True)

    df_apa = pd.DataFrame([])
    for i in gdf_pl.index:
        polygons=gdf_pl.geometry[i]
        PL_nr = gdf_pl.PL_nr[i]
        PL = gdf_pl.PL[i]
        for x, y in polygons.exterior.coords:
            row=pd.DataFrame([[PL_nr,x,y,PL]])
            df_apa = df_apa.append(row).reset_index(drop=True)
    df_apa = df_apa.rename(columns={0: "PL_nr",1: "x",2: "y",3: "PL"})
    df_plo = df_pl.loc[df_pl.loc[:,'O/P']=='O',:]
    df_apa = df_apa.merge(df_plo,"left",left_on='PL',right_on='PL',
                indicator=False, validate='many_to_one')

    return (gdf_pl,df_pl,df_coasline_no,gdf_dsc,df_apa)

def main():
    st.title("APA-2020: Awards in Predefined Areas 2020")
    st.sidebar.title("Navigation")
    apa2020()
    col1, col2,col3 = st.sidebar.beta_columns([0.5,9.0,0.5])
    col2.info(
                    '👉 Click on each company to see all its APA-2020 PL.'
                    ' Individual PL can be viewed using the selection box above.')
    st.sidebar.markdown(
        "**Made with [NORDLYS](https://share.streamlit.io/cadasa/nordlys)**"
        )
    st.sidebar.markdown(
        "**Based on data from [NPD](https://www.npd.no/en/facts/production-licences/licensing-rounds/apa-2020/)**"
        )
    st.sidebar.markdown(
        "**Created by [KHANH NGUYEN](mailto:khanhduc@gmail.com)**")
    return None

def apa2020():
    col1, col2,col3 = st.sidebar.beta_columns([0.5,9.0,0.5])
    gdf_pl,df_pl,df_coasline_no,gdf_dsc,df_apa = read_fielddata()
    df_pl = df_pl.loc[df_pl.loc[:,'O/P'].notnull(),:].reset_index(drop=True)
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
#        bin = col2.checkbox('Binned Heatmap?', False)
        st.subheader(f"""**Ownership interests of {"".join(str(len(df_pl['PL'].unique())))} production licences have been offered to {"".join(str(len(df_pl['Partners'].unique())))} companies**""")
#        st.dataframe(df_dsc_fld)
#        st.stop()
#        pts = alt.selection(type="multi", fields=['Partners'])
#        pts_y = alt.selection(type="multi", encodings=['y'])
#        brush = alt.selection_interval(encodings=['x'])

        # Top panel is scatter plot of temperature vs time
#        bas = alt.Chart(df_pl).mark_bar(size=12).encode(
#            x = alt.X('count(PL):Q',title='Numbers of Production Licence'),
#            y = alt.Y('Partners:N', title=None,sort='-x'),
#            tooltip=['O/P:N',
#                    alt.Tooltip('count():Q',title='Numbers of licences:')],
#            color=alt.Color('O/P'),
#            opacity=alt.condition(pts, alt.value(1.0), alt.value(0.2)),
#            size=alt.Size('Remaining_OE:Q', legend=alt.Legend(title='Remaining Reserves in MSM³OE',orient='bottom'),
#                            scale=alt.Scale(range=[10, 1000]))
#        ).properties(title = 'Ownership Interests per Companies',
#            width=230,
#            height=450
#        ).add_selection(
#            pts
#        )

#        map = alt.Chart(df_coasline_no).mark_area(
#            strokeWidth=0.5,color='red'
#        ).encode(
#            y=alt.Y('2:Q',scale=alt.Scale(domain=(55,72.5)), title=None, axis=None),
#            x=alt.X('1:Q',scale=alt.Scale(domain=(0,30)), title=None, axis=None),
#            order='0:O'
#            ).properties(title = 'Interactive PL Operatorship Map',
#                width=400,
#                height=478
#            ).interactive()

#        df_apa['Operator'] = df_apa.loc[:,'Partners']
#        pl = alt.Chart(df_apa).mark_area(
#            strokeWidth=0.5
#        ).encode(
#            y=alt.Y('y:Q',scale=alt.Scale(domain=(55,72.5))),
#            x=alt.X('x:Q',scale=alt.Scale(domain=(0,30))),
#            tooltip=['PL:N', 'Block(s):N',
#                    alt.Tooltip('Partners:T', title='Operator',condition=alt.condition(alt.datum.O/P=='O')),
#                    alt.Tooltip('%:Q', title='Percentage',condition=alt.condition(alt.datum.Partners == 'V'))
#                    ],
#            opacity=alt.condition(pts, alt.value(1.0), alt.value(0.2)),
#            order='PL_nr:N'
#            ).properties(
#                width=400,
#                height=478
#            ).add_selection(
#                pts
#            ).interactive()

#        st.markdown(
#            """
#            <style type='text/css'>
#                details {
#                    display: none;
#                }
#            </style>
#        """,
#            unsafe_allow_html=True,
#        )

#        st.altair_chart(
#                        map+pl|bas,use_container_width=True)
        @st.cache
        def altair_bar():
            pts = alt.selection_single(encodings=["y"], name="pts")
            return(
                alt.Chart(df_pl).mark_bar(size=12).encode(
                    x = alt.X('count(PL):Q',title='Numbers of Production Licence'),
                    y = alt.Y('Partners:N', title=None,sort='-x'),
                    tooltip=['O/P:N',
                            alt.Tooltip('count():Q',title='Numbers of licences:')],
                    color=alt.Color('O/P',legend=alt.Legend(title='Ownership',columns=2,offset=2,orient='bottom-right')),
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
        pl_map = df_pl.loc[(df_pl.loc[:,'O/P']=='O'),:].reset_index(drop=True)
        field_info = pl_map
        if r:
            field_info = df_pl.loc[(df_pl.loc[:,'Partners']==r[0]),:].reset_index(drop=True)
            PL_names = field_info['PL'].to_list()
            pl_map = df_pl.loc[df_pl.loc[:,'PL'].isin(PL_names),:].reset_index(drop=True)
            st.subheader(f"""**Data table showing all ownership interests of {"".join(r[0])}**""")
            pl_map.index = pl_map.index + 1
            st.table(pl_map)

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
            tooltip2 = folium.GeoJsonTooltip(fields=['PL', 'Partners','O/P','%'])
            style_function2 = lambda x: {'fillColor': "steelblue" if x['properties']['O/P']=='O' else "orange",
                                            "weight": 1,
                                         'color': "steelblue" if x['properties']['O/P']=='O' else "orange"}
            highlight_function2 = lambda x: {'fillColor': "steelblue" if x['properties']['O/P']=='O' else "darkorange",
                                            "weight": 2,
                                         'color': "steelblue" if x['properties']['O/P']=='O' else "darkorange"}
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
        col2.markdown(f"""***Blocks:  {"".join(str(field_info['Block(s)'].to_list()[0]))}***""")
        col2.markdown(f"""***Operator and Partners:***""")
        col2.table(field_info[['Partners', 'O/P', '%']])
#        st.stop()

        col1.subheader(f"""**Production License {"" .join(str(fields))}'s location**""")
#        st.dataframe(df_dsc)
        with col1.beta_container():
#            dsc_map = gdf_dsc.loc[(gdf_dsc.loc[:,'fieldName']==fields)&((gdf_dsc.loc[:,'curActStat']=='Producing')|(gdf_dsc.loc[:,'curActStat']=='Shut down')),:]
#            gdf_dsc2 = gdf_dsc
#            gdf_dsc = gdf_dsc.loc[gdf_dsc.loc[:,'geometry']!=None,:]
            gdf_dsc['Disc./Field'] = gdf_dsc.apply(lambda row: row.fieldName if row.fieldName else row.discName, axis=1)
            dsc_map = gdf_pl.loc[gdf_pl.loc[:,'PL_nr']==fields,:].reset_index(drop=True)
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
            tooltip = folium.GeoJsonTooltip(fields=['PL_nr'])
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
            folium.GeoJson(data=dsc_map,style_function=style_function2,highlight_function =highlight_function2,popup=fields, tooltip=fields).add_to(m)

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
