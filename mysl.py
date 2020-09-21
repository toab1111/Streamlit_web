# -*- coding: utf-8 -*-
# Copyright 2018-2019 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An example of showing geographic data."""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

DATE_TIME = "timestart"
DATA_URL = (
    'https://raw.githubusercontent.com/Maplub/odsample/master/20190101.csv'
)

st.title("Origin-Destination extracted from iTIC data")
st.markdown(
"""
This is a demo of a Streamlit app that shows Origin-Destination extracted from iTIC data
geographical distribution in Thailand. Use the slider
to pick a specific hour and look at how the charts change.
[credit source code](https://github.com/streamlit/demo-uber-nyc-pickups/blob/master/app.py),
[data](https://github.com/Maplub/odsamples)
""")




option = st.selectbox(
    'datetime',
   ('2019-01-01', '2019-01-02', '2019-01-03', '2019-01-04', '2019-01-05'))
st.write('You selected:', option)

option2 = st.selectbox(
    'Origin-Destination',
   ('Origin', 'Destination','Origin-Destination'))
st.write('You selected:', option2)

if option == '2019-01-01':
    DATA_URL=('https://raw.githubusercontent.com/Maplub/odsample/master/20190101.csv')
elif option == '2019-01-02':
    DATA_URL=('https://raw.githubusercontent.com/Maplub/odsample/master/20190102.csv')
elif option == '2019-01-03':
    DATA_URL=('https://raw.githubusercontent.com/Maplub/odsample/master/20190103.csv')
elif option == '2019-01-04':
    DATA_URL=('https://raw.githubusercontent.com/Maplub/odsample/master/20190104.csv')
elif option == '2019-01-05':
    DATA_URL=('https://raw.githubusercontent.com/Maplub/odsample/master/20190105.csv')

@st.cache(persist=True)
def get_data():
    return pd.read_csv(DATA_URL)


if option2 == 'Origin':
    lat='latstartl'
    lon='lonstartl'
    DATE_TIME = "timestart"
    data = get_data()[[lon, lat,DATE_TIME]].dropna() # IMPORTANT TO DROP NA
elif option2 == 'Destination':
    lat='latstop'
    lon='lonstop'
    DATE_TIME = "timestop"
    data = get_data()[[lon, lat,DATE_TIME]].dropna() # IMPORTANT TO DROP NA
elif option2 == 'Origin-Destination':
    lat='lat'
    lon='lon'
    DATE_TIME ="time"
    data1 = get_data()[['latstartl','lonstartl',"timestart"]].dropna()
    data2 = get_data()[['latstop', 'lonstop',"timestop"]].dropna()
    data2 = data2.rename(columns={"latstop": "latstartl", "lonstop": "lonstartl", "timestop": "timestart"})
    frames = [data1,data2]
    data = pd.concat(frames)
    data = data.rename(columns={"latstartl":'lat',"lonstartl":'lon',"timestart":"time"})
data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])  


hour = st.slider("Hour to look at", 0, 23)

data = data[data[DATE_TIME].dt.hour == hour]

st.write(hour)  


st.subheader("Geo data between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data[lat]), np.average(data[lon]))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 9,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data,
            get_position=[lon, lat],
            radius=100,
            elevation_scale=10,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True, 
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))
]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ), use_container_width=True)

if st.checkbox("Show raw data", False):
    st.subheader("Raw data by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
    st.write(data)
st.subheader("Total data %i columns" % (data.count()[0]))
