import folium
import streamlit as st
from streamlit_folium import folium_static

import functions as func


st.title("International Football Map")

statistic_choice = st.sidebar.selectbox("Select statistic: ", ("Number of wins","Number of looses", "Number of draws"))

# Create folium map
map = folium.Map()

# Add folium map into streamlit using streamlit_folium library
map_result, column_to_check, legend_text = func.select_statistic(statistic_choice)
func.map_display(map,map_result, column_to_check, legend_text)
st.write(folium_static(map))


