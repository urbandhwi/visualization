import json
import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 레이아웃 설정
st.set_page_config(page_title="행정동별 출동건수 지도", layout="wide")

st.title("🚨 서울시 행정동별 출동건수 시각화")

# GeoJSON 데이터 로드 (파일 경로 또는 dict 형태)
# 외부 파일 사용 시: with open("data.geojson", "r", encoding="utf-8") as f: geojson_data = json.load(f)
geojson_data = {
    "type": "FeatureCollection",
    "name": "dong_emergency_count",
    "crs": {
        "type": "name",
        "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
    },
    "features": [
        # 사용자의 GeoJSON features 데이터 들어가는 위치
    ],
}

# 1. Properties 데이터를 데이터프레임으로 변환
features = geojson_data.get("features", [])
df = pd.DataFrame([f["properties"] for f in features])

# 2. 상단 토글 버튼 구현 (목X동만 필터링)
show_mok_only = st.toggle("목X동만 보기", value=False)

if show_mok_only:
    # 행정동 이름(ADM_NM)에 '목'이 포함된 데이터만 필터링
    df = df[df["ADM_NM"].str.contains("목", na=False)]
    filtered_ids = set(df["ADM_CD"])
    filtered_geojson = {
        "type": "FeatureCollection",
        "features": [
            f
            for f in geojson_data["features"]
            if f["properties"]["ADM_CD"] in filtered_ids
        ],
    }
else:
    filtered_geojson = geojson_data

# 3. Plotly Choropleth Mapbox 생성
if not df.empty:
    fig = px.choropleth_mapbox(
        df,
        geojson=filtered_geojson,
        locations="ADM_CD",
        featureidkey="properties.ADM_CD",
        color="emergency_count",
        color_continuous_scale=["#FFFFFF", "#FF0000"],  # 하얀색 -> 빨간색
        range_color=(df["emergency_count"].min(), df["emergency_count"].max()),
        mapbox_style="carto-positron",  # 지도 배경 스타일
        center={"lat": 37.5665, "lon": 126.9780},  # 서울시청 중심 좌표
        zoom=10.5,
        hover_name="ADM_NM",  # 마우스 호버 시 행정동 이름
        hover_data={
            "ADM_CD": True,  # 행정동 코드 표시
            "emergency_count": True,  # 출동건수 표시
        },
        labels={
            "ADM_NM": "행정동명",
            "ADM_CD": "행정동코드",
            "emergency_count": "출동건수",
        },
        opacity=0.7,
    )

    fig.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="출동건수"),
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("조건에 맞는 데이터가 없습니다.")
