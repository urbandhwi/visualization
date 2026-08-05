import streamlit as st
import geopandas as gpd
import plotly.express as px

st.set_page_config(
    page_title="행정동 지도",
    layout="wide"
)

st.title("서울 행정동 지도")

########################################################
# GeoJSON 읽기
########################################################

gdf = gpd.read_file("dong_emergency_count.geojson")

# 좌표계 확인 후 WGS84 변환
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs(epsg=4326)

########################################################
# 컬럼명
########################################################
# 아래 이름만 실제 컬럼명에 맞게 수정하면 됩니다.

DONG_NAME = "ADM_NM"      # 행정동명
DONG_CODE = "ADM_CD"      # 행정동 코드
VALUE = "count"           # 색칠할 값

########################################################
# Toggle
########################################################

only_mok = st.toggle("목X동만 보기", value=False)

if only_mok:
    gdf = gdf[gdf[DONG_NAME].str.contains("목", na=False)]

########################################################
# Plotly
########################################################

fig = px.choropleth_mapbox(
    gdf,
    geojson=gdf.geometry,
    locations=gdf.index,
    color=VALUE,
    hover_name=DONG_NAME,
    hover_data={
        DONG_CODE: True,
        VALUE: True
    },
    opacity=0.65,
    mapbox_style="carto-positron",
    center={
        "lat": 37.5662952,
        "lon": 126.9779451
    },      # 서울시청
    zoom=10
)

fig.update_traces(
    marker_line_width=0.6,
    marker_line_color="white"
)

fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(
    fig,
    use_container_width=True
)
