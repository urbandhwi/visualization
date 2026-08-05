import json
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide")
st.title("서울시 행정동별 출동건수 지도 시각화")


# 1. 데이터 불러오기 (캐싱)
@st.cache_data
def load_geojson():
    # 저장소에 있는 geojson 파일 경로
    with open("seoul_dong.geojson", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_csv():
    # 저장소에 있는 출동건수 csv 파일 경로
    # csv에는 'ADM_CD'(또나 'ADM_NM')와 'COUNT'(출동건수) 컬럼이 필요합니다.
    return pd.read_csv("data.csv")


try:
    geojson_data = load_geojson()
    df = load_csv()

    # GeoJSON 구조 내부의 키 확인 (기본적으로 'ADM_NM', 'ADM_CD'가 쓰임)
    # GeoJSON properties 예시: {"ADM_NM": "목1동", "ADM_CD": "1115051000"}

    # 2. 사이드바 - 목X동 전용 토글 버튼
    st.sidebar.header("필터 설정")
    show_mokdong_only = st.sidebar.toggle("목1~5동만 보기", value=False)

    # 3. 데이터 필터링 logic
    # ADM_NM 컬럼이 없을 경우를 대비해 변환
    if "ADM_NM" not in df.columns:
        # 동 이름으로 추정되는 첫번째 문자열 컬럼 사용
        str_cols = df.select_dtypes(include=["object"]).columns
        if len(str_cols) > 0:
            df["ADM_NM"] = df[str_cols[0]]

    # 토글 켜짐 여부에 따라 데이터 필터링
    if show_mokdong_only:
        # 목동, 목1동~목5동 매칭 정규식
        mok_pattern = r"목[1-5]?동|목동"
        filtered_df = df[
            df["ADM_NM"].astype(str).str.contains(mok_pattern, regex=True, na=False)
        ]
    else:
        filtered_df = df.copy()

    # 4. Plotly Choropleth 지도 생성
    # 출동건수가 적으면 하얀색(white), 많으면 빨간색(red)
    fig = px.choropleth_mapbox(
        filtered_df,
        geojson=geojson_data,
        locations="ADM_CD",  # CSV의 행정동 코드 컬럼명
        featureidkey="properties.ADM_CD",  # GeoJSON 내부의 행정동 코드 키 위치
        color="COUNT",  # 출동건수 컬럼명 (숫자 데이터)
        color_continuous_scale=["#FFFFFF", "#FF0000"],  # 하얀색 -> 빨간색
        range_color=(df["COUNT"].min(), df["COUNT"].max()),  # 전체 기준 색상 범위
        mapbox_style="carto-positron",  # 지도 배경 스타일
        # 처음 진입 시 서울시청 중심 시점 세팅
        center={"lat": 37.5665, "lon": 126.9780},
        zoom=10.5 if not show_mokdong_only else 12.5,  # 목동 모드일 땐 살짝 확대
        opacity=0.7,
        # 마우스 올렸을 때 나타나는 툴팁 정보 설정 (행정동 이름, 코드)
        hover_name="ADM_NM",
        hover_data={"ADM_CD": True, "COUNT": True},
        labels={
            "COUNT": "출동건수",
            "ADM_CD": "행정동 코드",
            "ADM_NM": "행정동명",
        },
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=750,
    )

    # 지도 출력
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"데이터를 로드하거나 시각화하는 도중 에러가 발생했습니다: {e}")
    st.info(
        "CSV 및 GeoJSON의 컬럼명/키값이 'ADM_CD', 'ADM_NM', 'COUNT' 로 매핑되어 있는지 확인해주세요."
    )
