import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정
st.set_page_config(page_title="서울시 미세먼지 시각화", page_icon="☁️", layout="wide")

# 2. 제목
st.title("☁️ 2025년 서울시 구별 (초)미세먼지 시각화 앱")
st.markdown("선택한 자치구의 미세먼지(PM10)와 초미세먼지(PM2.5) 시간별 추이를 확인하세요.")

# 3. 데이터 로드 함수 (캐싱을 통해 앱 속도 향상)
@st.cache_data
def load_data():
    # 파일명은 실제 업로드할 파일명과 동일해야 합니다.
    df = pd.read_csv("서울시 시간별 (초)미세먼지_2025년.csv")
    
    # '일시' 컬럼을 datetime 객체로 변환
    df['일시'] = pd.to_datetime(df['일시'])
    
    # 데이터 정렬 (과거 -> 최신)
    df = df.sort_values(by='일시')
    
    # 결측치(NaN) 처리: 시간의 흐름에 따라 이전 시간의 값으로 채움
    df = df.fillna(method='ffill') 
    return df

# 데이터 불러오기
df = load_data()

# 4. 사이드바 - 구별 필터링 기능 추가
st.sidebar.header("⚙️ 검색 설정")

# 자치구 목록 추출 ('평균' 포함)
gu_list = df['구분'].unique().tolist()
# '평균'을 기본값(가장 처음)으로 설정하기 위한 정렬 팁
if '평균' in gu_list:
    gu_list.remove('평균')
    gu_list = ['평균'] + sorted(gu_list)

selected_gu = st.sidebar.selectbox("🏢 자치구를 선택하세요:", gu_list)

# 날짜 범위 설정 (1년치 데이터가 한 번에 나오면 복잡하므로)
min_date = df['일시'].min().date()
max_date = df['일시'].max().date()

st.sidebar.write("📅 날짜 범위 선택:")
start_date, end_date = st.sidebar.date_input(
    "조회할 기간을 지정하세요.",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# 5. 선택된 조건에 맞게 데이터 필터링
filtered_df = df[(df['구분'] == selected_gu) & 
                 (df['일시'].dt.date >= start_date) & 
                 (df['일시'].dt.date <= end_date)]

# 6. 메인 화면 - 시각화 (Plotly 활용)
st.subheader(f"📍 [{selected_gu}] 미세먼지 및 초미세먼지 추이")

if not filtered_df.empty:
    # 탭으로 나누어 보여주기
    tab1, tab2, tab3 = st.tabs(["미세먼지 (PM10)", "초미세먼지 (PM2.5)", "데이터 원본 확인"])
    
    with tab1:
        fig_pm10 = px.line(filtered_df, x='일시', y='미세먼지(PM10)', 
                           title=f"{selected_gu} 시간별 미세먼지(PM10) 농도",
                           color_discrete_sequence=['#FF9999'])
        fig_pm10.update_layout(xaxis_title="날짜 및 시간", yaxis_title="농도 (㎍/㎥)")
        st.plotly_chart(fig_pm10, use_container_width=True)

    with tab2:
        fig_pm25 = px.line(filtered_df, x='일시', y='초미세먼지(PM25)', 
                           title=f"{selected_gu} 시간별 초미세먼지(PM25) 농도",
                           color_discrete_sequence=['#66B2FF'])
        fig_pm25.update_layout(xaxis_title="날짜 및 시간", yaxis_title="농도 (㎍/㎥)")
        st.plotly_chart(fig_pm25, use_container_width=True)
        
    with tab3:
        st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
        
else:
    st.warning("⚠️ 선택하신 조건에 해당하는 데이터가 없습니다. 날짜 범위를 다시 확인해주세요.")
