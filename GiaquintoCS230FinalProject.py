"""
Name: John Giaquinto
CS230: Section 3
Data: NCAA Stadiums
URL: https://share.streamlit.io/jgia/streamlit/main/GiaquintoCS230FinalProject.py

Description: This program uses Streamlit to display 5 maps/charts/graphs. The first is an interactive map of each NCAA stadium and their respective capacities
using pydeck. The next is a bar chart of the average stadium capacity by NCAA conference. The user can use checkboxes to select which NCAA conferences to include
in the barchart. Next, a scatter plot shows the relationship between stadium date built and stadium capacity. The user can use a double ended slider to select
the range of years for the scatter plot x-axis. The barchart and scatter plot are both created using the matplotlib library, but the next two charts use plotly
to show the number of NCAA stadiums per state and average capacity of NCAA stadiums by state. When states are shaded with darker colors, they have more stadiums
or a higher average stadium capacity. Plotly takes state abbreviations instead of state names to create these charts, so I used the us library to convert each
state name to its abbreviation.
"""

import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import us
#The user has the option to select red, green, or blue using radio buttons. This selection will determine the color of each graph/chart/map
colors = ['Red','Green','Blue']
sb_color = st.sidebar.radio("Select a color theme for the charts, plots, and maps: ",colors)

#This function creates a Matplotlib barchart which shows the average stadium capacity by NCAA conference
def barchart(x, y):
    global sb_color
    plt.clf() #The figure is cleared before anything else is done. For some reason the barchart interfered with the scatterplot, but plt.clf() fixed the issue
    plt.bar(x, y, color=sb_color) #The color is selected by the user using radio buttons. See line 24.
    plt.xticks(rotation='vertical') #Conference names are vertical instead of horizontal
    plt.ylabel("Average Stadium Capacity (# of People)")
    plt.xlabel("NCAA Conference Names")
    plt.title("Average Stadium Capacity By NCAA Conference")
    return plt

#This function creates a scatter plot. It is almost identical to the function that creates the barchart. However, the labels are horizontal and it has a grid.
def scatterplot(x, y):
    global sb_color
    plt.clf()
    plt.scatter(x, y, color=sb_color)
    plt.ylabel("Capacity")
    plt.xlabel("Date Built")
    plt.title("Relationship Between Date Built and Capacity")
    plt.grid(True)
    return plt

#This function creates a shaded US map using Plotly. By default the map is for NCAA stadiums per state, but this can be changed.
#This function is adapted from https://plotly.com/python/choropleth-maps/. See the section titled "United States Choropleth Map".
def us_choropleth_map(loc, z, cbt="Number of Stadiums", tt="NCAA Stadiums per State"):
    global sb_color
    fig = go.Figure(data=go.Choropleth(
        locations=loc, #Spatial coordinates
        z = z, #Data to be color-coded
        locationmode = 'USA-states', #set of locations match entries in `locations`
        colorscale = sb_color + 's', #The color scale does not recognize red, green, or blue. It does recognize reds, greens, blues
        colorbar_title = cbt,
    ))

    fig.update_layout(
        title_text = tt,
        geo_scope='usa', #limit map scope to USA
    )
    st.plotly_chart(fig, use_container_width=True)

#Pydeck uses RGB color codes instead of names, so this function helps change the color of the stadiums on the Pydeck map
def color_to_rgb(sb_color):
    if sb_color == 'Red':
        return [255,0,0]
    if sb_color == 'Green':
        return[0,128,0] #0,255,0 is lime green, not green
    if sb_color == 'Blue':
        return [0,0,255]

df = pd.read_csv("stadiums.csv") #The dataframe is created from a CSV file of the data
df = df.sort_values(by='capacity', ascending=True)  #This sorts the dataframe by capacity. It has no effect on the streamlit output; I included it to meet the Pandas requirements

#Some of the state names in the CSV are full names instead of abbreviations. The Ployly United States Choropleth Map can ony be created using state abbreviations.
#I used the us library to convert state names to their abbreviations, as it was much faster than creating a dictionary.
#https://pypi.org/project/us/
states = [us.states.lookup(row['state']).abbr if "D.C." not in row['state'] else 'DC' for index, row in df.iterrows()] #The us library doesn't recognize D.C.
df.state=states

#Here I create a second dataframe based of a groupby of the original df that shows the number of stadiums per state
df2 = pd.DataFrame(df.groupby(['state']).size())
df2.reset_index(inplace=True)
df2 = df2.rename(columns = {'index':'state', 0:'count'})
average_capacities = pd.Series(df.groupby('state')['capacity'].mean())
df2['average_capacity'] = average_capacities.values #The average capacity of stadiums by state is added as a third column
#This 2nd dataframe is useful for the 2 Plotly choropleth maps

#The text created with st.write didn't look great everywhere, so I used st.markdown to create different text types using CSS
#https://docs.streamlit.io/library/api-reference/text/st.markdown
st.markdown('<style>p{font-family:Sans-Serif; font-size: 22px; text-align: center;}.sidebar-font{font-family:"Source Sans Pro"; font-size: 15px;text-align: left}.explanation-font{font-family:"Source Sans Pro"; font-size: 18px;text-align: left}</style>', unsafe_allow_html=True)

st.title("NCAA Stadiums Data Visualization")
st.markdown("Created by John Giaquinto", unsafe_allow_html=True)
original_data_link = """ <a href="https://github.com/gboeing/data-visualization/blob/main/ncaa-football-stadiums/data/stadiums-geocoded.csv" target="_blank">Download Original Data</a> """
st.markdown(original_data_link, unsafe_allow_html=True)

st.markdown('<p class="explanation-font"><br /><br />The following map is created with Pydeck. It shows the location and capacity of each NCAA stadium.'
            ' To move the map, right click and drag. Use your scroll wheel to zoom in and out. Left click and drag to change the viewing angle.</p>', unsafe_allow_html=True)
st.write("Map of Every NCAA Stadium")
#This map is adapted from the in-class example streamlit_map.py
#https://deckgl.readthedocs.io/en/latest/index.html
#ViewState represents where the state of a viewport, essentially where the screen is focused
#zoom is between 0 (whole world) and 24 (individual building)
#pitch is the up/down angle relative to the map’s plane, with 0 being looking directly at the map
view_state = pdk.ViewState(
    latitude=df["latitude"].mean(),
    longitude=df["longitude"].mean(),
    zoom = 6,
    pitch = 5)

#a scatter plot layer
layer1 = pdk.Layer('ScatterplotLayer',
                  data = df[['stadium', 'capacity', 'latitude', 'longitude']],
                  get_position = '[longitude, latitude]',
                  get_radius = 1000,
                  get_color = color_to_rgb(sb_color), #get_color requires an RGB code
                  pickable = True)

tool_tip = {"html": "Stadium Name:<br/> <b>{stadium}</b><br/> Capacity:<br/> <b>{capacity}</b>",
            "style": { "backgroundColor": sb_color,
                        "color": "white"}}

#https://deckgl.readthedocs.io/en/latest/deck.html
#mapbox://styles/mapbox/light-v9
map = pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=view_state,
    layers=[layer1],
    tooltip= tool_tip
)

st.pydeck_chart(map) #Displays the map

st.sidebar.markdown('<p class="sidebar-font">Select the conferences to include in the barchart:</p>', unsafe_allow_html=True) #the sidebar-font class has the same font size at the color radio buttons
#When checkboxes have the value "True", the corresponding conferences are shown in the bar chart
bigten = st.sidebar.checkbox("Big Ten", True)
sec = st.sidebar.checkbox("SEC", True)
big12 = st.sidebar.checkbox("Big 12", True)
pac12 = st.sidebar.checkbox("Pac-12", True)
acc = st.sidebar.checkbox("ACC", True)
independent = st.sidebar.checkbox("Independent", True)
mountainwest = st.sidebar.checkbox("Mountain West", True)
american = st.sidebar.checkbox("American", True)
cusa = st.sidebar.checkbox("C-USA", True)
sunbelt = st.sidebar.checkbox("Sun Belt", True)
mac = st.sidebar.checkbox("MAC", True)
ohiovalley = st.sidebar.checkbox("Ohio Valley", True)
ivy = st.sidebar.checkbox("Ivy", True)
swac = st.sidebar.checkbox("SWAC", True)
meac = st.sidebar.checkbox("MEAC", True)
bigsky = st.sidebar.checkbox("Big Sky", True)
caa = st.sidebar.checkbox("CAA", True)
patriot = st.sidebar.checkbox("Patriot", True)
southern = st.sidebar.checkbox("Southern", True)
missourivalley = st.sidebar.checkbox("Missouri Valley", True)
bigsouth = st.sidebar.checkbox("Big South", True)
southland = st.sidebar.checkbox("Southland", True)
pioneer = st.sidebar.checkbox("Pioneer", True)
northeast = st.sidebar.checkbox("Northeast", True)

#The following loop creates a dictionary of all conference names and how many stadiums are there are for each conference
conference_name_dict = {}
for index, row in df.iterrows(): #Each row in the df contains information about a stadium
    if row['conference'] not in conference_name_dict.keys():
        conference_name_dict[row['conference']] = 1 #If a conference is not already a dictionary key but exists in the df then there is at least 1 stadium with the conference
    else:
        conference_name_dict[row['conference']] = conference_name_dict.get(row['conference'], 0) + 1 #If a conference already exists in the dictionary the number of stadiums for that confernece is incremented by +1

#The follwing loops create a dictionary where the keys are the conference names and the values are the average stadium size (capacity) for each conference
conference_stadium_size_dictionary = {}
#Initially each conference name is set as a dictionary key. The values are initially all set to 0.
for conference_name in conference_name_dict.keys():
    conference_stadium_size_dictionary[conference_name] = 0
#The total capacity of each stadium for each conference is then added
for index, row in df.iterrows():
    conference_stadium_size_dictionary[row['conference']] = conference_stadium_size_dictionary.get(row['conference'], 0) + int(row['capacity'])
#Finally, each value in the dictionary (currently the sum of the capacity of every stadium for each conference) is divided by the number stadiums for each conference
#The final values are the mean stadium capacity for the stadiums in each conference
for conference in conference_stadium_size_dictionary:
    conference_stadium_size_dictionary[conference] = conference_stadium_size_dictionary.get(conference, 0) / conference_name_dict[conference]

#If the user has selected a conference to appear in the bar chart, the name of the conference is appended to the conferencenames list and the average stadium size is appended to the capacities list
capacities = []
conferencenames = []

if bigten:
    capacities.append(conference_stadium_size_dictionary['Big Ten'])
    conferencenames.append('Big Ten')
if sec:
    capacities.append(conference_stadium_size_dictionary['SEC'])
    conferencenames.append('SEC')
if big12:
    capacities.append(conference_stadium_size_dictionary['Big 12'])
    conferencenames.append('Big 12')
if pac12:
    capacities.append(conference_stadium_size_dictionary['Pac-12'])
    conferencenames.append('Pac-12')
if acc:
    capacities.append(conference_stadium_size_dictionary['ACC'])
    conferencenames.append('ACC')
if independent:
    capacities.append(conference_stadium_size_dictionary['Independent'])
    conferencenames.append('Independent')
if mountainwest:
    capacities.append(conference_stadium_size_dictionary['Mountain West'])
    conferencenames.append('Mountain West')
if american:
    capacities.append(conference_stadium_size_dictionary['American'])
    conferencenames.append('American')
if cusa:
    capacities.append(conference_stadium_size_dictionary['C-USA'])
    conferencenames.append('C-USA')
if sunbelt:
    capacities.append(conference_stadium_size_dictionary['Sun Belt'])
    conferencenames.append('Sun Belt')
if mac:
    capacities.append(conference_stadium_size_dictionary['MAC'])
    conferencenames.append('MAC')
if ohiovalley:
    capacities.append(conference_stadium_size_dictionary['Ohio Valley'])
    conferencenames.append('Ohio Valley')
if ivy:
    capacities.append(conference_stadium_size_dictionary['Ivy'])
    conferencenames.append('Ivy')
if swac:
    capacities.append(conference_stadium_size_dictionary['SWAC'])
    conferencenames.append('SWAC')
if meac:
    capacities.append(conference_stadium_size_dictionary['MEAC'])
    conferencenames.append('MEAC')
if bigsky:
    capacities.append(conference_stadium_size_dictionary['Big Sky'])
    conferencenames.append('Big Sky')
if caa:
    capacities.append(conference_stadium_size_dictionary['CAA'])
    conferencenames.append('CAA')
if patriot:
    capacities.append(conference_stadium_size_dictionary['Patriot'])
    conferencenames.append('Patriot')
if southern:
    capacities.append(conference_stadium_size_dictionary['Southern'])
    conferencenames.append('Southern')
if missourivalley:
    capacities.append(conference_stadium_size_dictionary['Missouri Valley'])
    conferencenames.append('Missouri Valley')
if bigsouth:
    capacities.append(conference_stadium_size_dictionary['Big South'])
    conferencenames.append('Big South')
if southland:
    capacities.append(conference_stadium_size_dictionary['Southland'])
    conferencenames.append('Southland')
if pioneer:
    capacities.append(conference_stadium_size_dictionary['Pioneer'])
    conferencenames.append('Pioneer')
if northeast:
    capacities.append(conference_stadium_size_dictionary['Northeast'])
    conferencenames.append('Northeast')

st.markdown('<p class="explanation-font"><br />The following two charts are created using Matplotlib. The barchart shows the average NCAA stadium capacity by conference, '
            'and the scatter plot shows the relationship (or lack thereof) between stadium capacity and stadium construction date. To remove conferences from the'
            ' bar chart, use the checkboxes in the sidebar. To adjust the date range on the scatter plot, use the slider.</p>', unsafe_allow_html=True)
#the conference names list is the x-axis of the bar chart and the capacities list is the y-axis
st.pyplot(barchart(conferencenames,capacities))

#The following 3 lines creates a double ended slider where the user can select a range of dates from the year the first NCAA stadium was built to the year the last NCAA stadium was built
min_built = int(df['built'].min())
max_built = int(df['built'].max())
date_range = st.slider('Select a date range for the scatter plot:', min_built, max_built, (min_built, max_built))

#The slider restricts the x-axis of the scatter plot which shows the relationship between stadium date built and capacity
df_subset = df.loc[(df['built'] >= date_range[0]) & (df['built'] <= date_range[1])]
st.pyplot(scatterplot(df_subset['built'],df_subset['capacity']))

#The choropleth maps use the 2nd data frame
st.markdown('<p class="explanation-font">These final choropleth maps are created with Plotly. They show the NCAA stadiums per state and average NCAA stadium '
            'capacity by state. Mouse over each state to see their individual values. </p>', unsafe_allow_html=True)
us_choropleth_map(df2['state'], df2['count'].astype(int)) #The count of each stadium per state is an interger
us_choropleth_map(df2['state'], df2['average_capacity'].astype(float),"Capacity","Average NCAA Stadium Capacity by State") #The average capacity is a float
