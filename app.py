import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pyproj import Transformer

# ------------------------------------------------------
# Streamlit 설정
# ------------------------------------------------------

st.set_page_config(
    page_title="서울 응급실 이용 현황",
    layout="wide"
)

st.title("서울 행정동 응급실 이용 현황")

# ------------------------------------------------------
# GeoJSON 읽기
# ------------------------------------------------------

with open("dong_emergency_count.geojson", encoding="utf-8") as f:
    geojson = json.load(f)

df = pd.DataFrame(
    [feature["properties"] for feature in geojson["features"]]
)

# ------------------------------------------------------
# 소방서 데이터
# ------------------------------------------------------

fire = pd.read_excel(
    "서울시 소방서,안전센터,구조대 위치정보.xlsx"
)

# 5186 -> 4326

transformer = Transformer.from_crs(
    "EPSG:5186",
    "EPSG:4326",
    always_xy=True
)

fire["lon"], fire["lat"] = transformer.transform(
    fire["X좌표"],
    fire["Y좌표"]
)

# ------------------------------------------------------
# Toggle
# ------------------------------------------------------

only_mok = st.toggle("목1~5동만 보기")

if only_mok:

    df = df[df["ADM_NM"].str.match(r"^목\d동$", na=False)]

    selected = set(df["ADM_CD"])

    geojson = {
        "type": "FeatureCollection",
        "features": [
            f for f in geojson["features"]
            if f["properties"]["ADM_CD"] in selected
        ]
    }

# ------------------------------------------------------
# Choropleth
# ------------------------------------------------------

fig = px.choropleth_mapbox(
    df,
    geojson=geojson,
    locations="ADM_CD",
    featureidkey="properties.ADM_CD",
    color="emergency_count",
    color_continuous_scale="YlOrRd",
    opacity=0.7,
    center=dict(
        lat=37.5662952,
        lon=126.9779451
    ),
    zoom=10,
    mapbox_style="carto-positron",
    hover_name="ADM_NM",
    hover_data={
        "ADM_CD": True,
        "emergency_count": True
    }
)

# Hover

fig.update_traces(
    hovertemplate=
    "<b>%{customdata[1]}</b><br>"
    "행정동 코드 : %{location}<br>"
    "응급실 이용건수 : %{z:,}<extra></extra>"
)

# ------------------------------------------------------
# 소방서 추가
# ------------------------------------------------------

fig.add_trace(

    go.Scattermapbox(

        lat=fire["lat"],
        lon=fire["lon"],

        mode="markers",

        marker=dict(
            size=10,
            color="royalblue"
        ),

        text=fire["기관명"],

        hovertemplate=
        "<b>%{text}</b><extra></extra>",

        name="소방기관"
    )
)

# ------------------------------------------------------
# Layout
# ------------------------------------------------------

fig.update_layout(

    margin=dict(
        l=0,
        r=0,
        t=0,
        b=0
    ),

    legend=dict(
        y=0.99,
        x=0.01
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)
