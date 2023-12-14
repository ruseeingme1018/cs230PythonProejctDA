"""
Class: CS230--Section 1
Name: Rishaan Uttamchandani
Description: Final DA Project
I pledge that I have completed the programming assignment
independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
Sources I used
https://stackoverflow.com/questions/26716616/convert-a-pandas-dataframe-to-a-dictionary
https://deckgl.readthedocs.io/en/latest/deck.html
https://copyprogramming.com/howto/python-zip-used-in-python-stack-overflow
https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.idxmin.html
https://folium.streamlit.app/

"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import folium

from streamlit_folium import st_folium



def homePage():
    #home page
    st.title("BlueBikes in Boston!")
    st.header("Welcome to my CS 230 Project")
    image = open('bike_dock.jpg', 'rb').read()
    st.image(image)
    st.write("Project by Rishaan Uttamchandani")
    st.write("Trip Data from Q1 2015")

    return

def getData():
    #reading in csv
    mapdf = pd.read_csv("current_stations.csv")
    tripdf = pd.read_csv("tripdata.csv", header=0, names=["Trip Duration","Start time","Stop time","Start Station Id","Start Station Name","Start Station Latitude","Start Station Longitude","End Station Id","End Station Name","End Station Latitude","End Station Longitude","Bike Id","User Type","Birth Year","Gender"])
    return mapdf, tripdf

def byDockLocation(mapdf):
    #Creating a map that maps out all dock locations of blue bikes with hover feature
    st.title("A Map of all the Blue Bike docks in the Greater Boston Area!")
    locationInput = st.multiselect('Choose a District (or multiple)', mapdf['District'].dropna().drop_duplicates())
    dfByDistrict = mapdf[mapdf['District'].isin(locationInput)]

    #pydeck map
    view_state = pdk.ViewState(
        latitude=dfByDistrict['Latitude'].mean(),
        longitude=dfByDistrict['Longitude'].mean(),
        zoom=11,
        pitch=50,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=dfByDistrict,
        get_position=['Longitude', 'Latitude'],
        get_radius=80,
        get_fill_color=[0,0,255],
        pickable=True,
        auto_highlight=True,
    )

    #tooltip to display dock count
    tooltipHtml = "<b>Docks:</b> {Total docks}"
    tooltip = {"html": tooltipHtml}

    plots = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/streets-v11",
        tooltip=tooltip
    )
    st.pydeck_chart(plots)

    #Also looks at the average docks and filters to do a map again or dictionary
    averageDocks = mapdf['Total docks'].mean()

    #Filter docks below average and create a dictionary from the DF to show that I cam use both
    belowAverageDocks = mapdf[mapdf['Total docks'] > averageDocks]
    belowAverageDocksDict = dict(
        zip(
            belowAverageDocks['Name'],
            zip(belowAverageDocks['Latitude'], belowAverageDocks['Longitude'], belowAverageDocks['Total docks']),
        )
    )

    st.subheader(f"Average number of docks (all stations): {averageDocks:.2f}")
    st.write("Docks above average:")
    toggleMap = st.toggle("Show Map?")
    toggleDict = st.toggle("Show Dictionary?")
    if toggleDict:
        st.write(belowAverageDocksDict)

    if toggleMap:
        #pydeck map
        layer = pdk.Layer(
            "ScatterplotLayer",
            belowAverageDocks,
            get_position="[Longitude, Latitude]",
            get_radius=80,
            get_fill_color=[0, 0, 255],
            pickable=True,
        )
        view_state = pdk.ViewState(
            latitude=belowAverageDocks['Latitude'].mean(),
            longitude=belowAverageDocks['Longitude'].mean(),
            zoom=11,
            pitch=0,
        )

        tooltipHtml2 = "<b>Docks:</b> {Total docks}"
        tooltip2 = {"html": tooltipHtml2}

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/streets-v11",
            tooltip=tooltip2
        )
        st.pydeck_chart(deck)
        return

def tripStats(tripdf):
    #Average trip duration, Longest Trip, Shortest Trip
    #making start time a uniform format
    tripdf["Start time"] = pd.to_datetime(tripdf["Start time"])

    st.title("Trip Duration Analysis")
    st.header("Average Trip time, Longest Trip and Shortest Trip")

    #calcs
    averageDurationSeconds = tripdf["Trip Duration"].mean()
    longestTrip = tripdf.loc[tripdf["Trip Duration"].idxmax()]
    shortestTrip = tripdf.loc[tripdf["Trip Duration"].idxmin()]
    longestTripSeconds = tripdf.loc[tripdf["Trip Duration"].idxmax()]["Trip Duration"]
    shortestTripSeconds = tripdf.loc[tripdf["Trip Duration"].idxmin()]["Trip Duration"]
    averageDurationMinutes = averageDurationSeconds / 60
    longestTripMinutes = longestTripSeconds / 60
    shortestTripMinutes = shortestTripSeconds / 60

    #displaying
    st.subheader("Trip Duration Statistics")
    st.write(f"Average Duration: {averageDurationMinutes:.2f} minutes")

    st.subheader("Longest Trip:")
    st.write(f"Duration: {longestTripMinutes:.2f} minutes")
    st.write(longestTrip[["Start time", "Stop time", "Start Station Name", "End Station Name", "Bike Id", "User Type", "Birth Year"]])

    stationButton = st.toggle("See map")

    # using a folium route map
    points = []
    points.append([longestTrip["Start Station Latitude"], longestTrip["Start Station Longitude"]])
    points.append([longestTrip["End Station Latitude"], longestTrip["End Station Longitude"]])

    m = folium.Map(location=[longestTrip["Start Station Latitude"], longestTrip["Start Station Longitude"]],
                   zoom_start=15)

    folium.Marker(
        location=[longestTrip["Start Station Latitude"], longestTrip["Start Station Longitude"]],
        popup=f'Starting Point',
        icon=folium.Icon(color='lightblue', icon='bicycle', prefix='fa')
    ).add_to(m)

    folium.Marker(
        location=[longestTrip["End Station Latitude"], longestTrip["End Station Longitude"]],
        popup=f'Ending Point',
        icon=folium.Icon(color='lightblue', icon='bicycle', prefix='fa')
    ).add_to(m)

    folium.PolyLine(points, color='blue', dash_array='5', opacity='.85', tooltip='BlueBike').add_to(m)

    if stationButton:
        st_folium(m, height=500, width=550)

    st.subheader("Shortest Trip:")
    st.write(f"Duration: {shortestTripMinutes:.2f} minutes")
    st.write(shortestTrip[["Start time", "Stop time", "Start Station Name", "End Station Name", "Bike Id", "User Type", "Birth Year"]])

    return

def usagePatternsAnalysis(tripdf):
    #Analyzing the usage patterns, narrowed down by day inputted by the user
    st.title("BlueBike Usage Patterns")
    st.header("Average Rides per day of Q1 2015")

    #narrowing down days and times to be used in plots
    tripdf["Start time"] = pd.to_datetime(tripdf["Start time"])
    tripdf["Day_of_Week"] = tripdf["Start time"].dt.day_name()
    tripdf["Hour_of_Day"] = tripdf["Start time"].dt.hour
    selectedDays = st.multiselect("Select Days to Display Data", tripdf["Day_of_Week"].unique())
    filteredData = tripdf[tripdf["Day_of_Week"].isin(selectedDays)]

    totalRidesPerDay = filteredData["Day_of_Week"].value_counts()
    avgRidesPerDay = totalRidesPerDay / len(tripdf["Day_of_Week"].unique())

    #Plotting data using matplotlib
    #Bar chart to display average rides per day based on selected days
    figBar, axBar = plt.subplots()
    bars = axBar.bar(avgRidesPerDay.index, avgRidesPerDay.values)

    axBar.bar(avgRidesPerDay.index, avgRidesPerDay.values, color='blue')
    axBar.set_xlabel("Day of Week")
    axBar.set_ylabel("Average Number of Rides")
    axBar.set_title("Day-of-Week Analysis")

    #for loop to display numbers
    for bar in bars:
        yval = bar.get_height()
        axBar.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), ha='center', va='bottom')

    st.pyplot(figBar)

    #line chart to display peak usage hours throughout a 24 hour day
    st.header("Peak Usage Hours")
    peakUsageHours = filteredData["Hour_of_Day"].value_counts().sort_index()

    figLine, axLine = plt.subplots(figsize=(10, 6))
    axLine.plot(peakUsageHours.index, peakUsageHours.values)
    axLine.set_xlabel("Hour of Day")
    axLine.set_ylabel("Number of Rides")
    axLine.set_title("Peak Usage Hours")
    st.pyplot(figLine)

    #peak hours display and calc
    st.write("Peak Usage Hours:")
    peakHour = peakUsageHours[peakUsageHours == peakUsageHours.max()].index

    if not peakHour.empty:
        peakHour = peakHour[0]
        peakHour12 = (peakHour % 12) or 12
        if peakHour < 12:
            ampm = 'AM'
        else:
            ampm = 'PM'
        st.write(f"Peak usage hour is: {peakHour12} {ampm}")
    else:
        st.write("No peak usage hour found.")

def mostPopularStations(tripdf):
    #Displaying most popular OR least popular stations based on user input and decisions. Slider selects numer and radio selects > or <
    st.sidebar.title("Display BlueBike Stations based on Number of Trips")
    numTrips = st.sidebar.select_slider("Select Number of Trips", options=range(1, 700), value=310)
    greaterThanOrLessThan = st.sidebar.radio(f"Do you want to view stations with less than or greater than {numTrips} trips?", ['Greater Than', 'Less Than'])
    stationCounts = tripdf.groupby(
        ['Start Station Name']).size().reset_index(name='count')

    #input conditions
    if greaterThanOrLessThan == 'Greater Than':
        dfBasedOnSlider = stationCounts.query('count >= @numTrips')
    elif greaterThanOrLessThan == 'Less Than':
        dfBasedOnSlider = stationCounts.query('count <= @numTrips')

    st.write(f"Stations with {greaterThanOrLessThan} {numTrips} trips:")
    st.write(dfBasedOnSlider)

    #bar chart to show stations
    fig, ax = plt.subplots()
    ax.bar(dfBasedOnSlider['Start Station Name'], dfBasedOnSlider['count'])
    ax.set_xlabel('Start Station Name')
    ax.set_ylabel('Number of Trips')
    ax.set_title(f"Stations with {greaterThanOrLessThan} {numTrips} trips")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

    return

def ageCompare(tripdf):
    #Input your year of birth and see avg trip time of those your age. Button to display df to prove it!
    userBirthYear = st.text_input("Enter your birth year:")

    if userBirthYear:
        sameBirthYearDf = tripdf[tripdf['Birth Year'] == userBirthYear]
        if not sameBirthYearDf.empty:
            avgTripTime = (sameBirthYearDf['Trip Duration'].mean()) / 60
            st.write(
                f"The average trip time for customers with the birth year {userBirthYear} is: {avgTripTime:.2f} minutes")
            proof = st.button("Prove it!")
            if proof:
                st.write(sameBirthYearDf[["Trip Duration","Start time","Stop time","Start Station Name","End Station Name","Bike Id","User Type","Birth Year","Gender"]])
        else:
            st.write(f"No data found for the birth year {userBirthYear}.")

    return


def nav():
    sessionState = st.session_state

    if 'page' not in sessionState:
        sessionState['page'] = 'home'

    #navigation Menu
    menu = ['Home', 'Docks Around the City', 'Trip Stats', 'Usage Pattern', 'Most Popular Stations', 'About you!']
    navigation = st.sidebar.selectbox('Select a page', menu)

    #Update session state page based on nav selection
    if navigation == 'Home':
        sessionState['page'] = 'Home'
    elif navigation == 'Docks Around the City':
        sessionState['page'] = 'Docks Around the City'
    elif navigation == 'Trip Stats':
        sessionState['page'] = 'Trip Stats'
    elif navigation == 'Usage Pattern':
        sessionState['page'] = 'Usage Pattern'
    elif navigation == 'Most Popular Stations':
        sessionState['page'] = 'Most Popular Stations'
    elif navigation == 'About you!':
        sessionState['page'] = 'About you!'
    return sessionState, menu

def main():
    sessionState, menu = nav()
    mapdf, tripdf = getData()

    if sessionState['page'] == 'Home' or sessionState['page'] not in menu:
        homePage()
    elif sessionState['page'] == 'Docks Around the City':
        byDockLocation(mapdf)
    elif sessionState['page'] == 'Trip Stats':
        tripStats(tripdf)
    elif sessionState['page'] == 'Usage Pattern':
        usagePatternsAnalysis(tripdf)
    elif sessionState['page'] == 'Most Popular Stations':
        mostPopularStations(tripdf)
    elif sessionState['page'] == 'About you!':
        ageCompare(tripdf)
    return

main()