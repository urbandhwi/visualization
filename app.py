import json

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="서울 행정동 응급실 이용 현황",
    layout="wide",
)

st.title("서울 행정동 응급실 이용 현황")

# ----------------------------------------------------
# GeoJSON 읽기
# ----------------------------------------------------
with open("dong_emergency_count.geojson", encoding="utf-8") as f:
    geojson = json.load(f)

# properties -> DataFrame
rows = [feature["properties"] for feature in geojson["features"]]
df = pd.DataFrame(rows)

# ----------------------------------------------------
# Toggle : 목동만 보기
# ----------------------------------------------------
only_mok = st.toggle("목동만 보기", value=False)

if only_mok:
    df = df[df["ADM_NM"].str.startswith("목", na=False)]

# 선택된 행정동만 GeoJSON에도 반영
selected_codes = set(df["ADM_CD"])

filtered_geojson = {
    "type": "FeatureCollection",
    "features": [
        feature
        for feature in geojson["features"]
        if feature["properties"]["ADM_CD"] in selected_codes
    ],
}

# ----------------------------------------------------
# Choropleth Map
# ----------------------------------------------------
fig = px.choropleth_mapbox(
    df,
    geojson=filtered_geojson,
    featureidkey="properties.ADM_CD",
    locations="ADM_CD",
    color="emergency_count",
    color_continuous_scale="YlOrRd",
    hover_name="ADM_NM",
    hover_data={
        "ADM_CD": True,
        "emergency_count": True,
    },
    center={
        "lat": 37.5662952,
        "lon": 126.9779451,  # 서울시청
    },
    zoom=10,
    opacity=0.75,
    mapbox_style="carto-positron",
)

fig.update_traces(
    marker_line_width=0.5,
    marker_line_color="white",
    hovertemplate=(
        "<b>%{customdata[1]}</b><br>"
        "행정동 코드 : %{location}<br>"
        "응급실 이용건수 : %{z:,}<extra></extra>"
    ),
)

fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(title="건수"),
)

st.plotly_chart(fig, use_container_width=True)
