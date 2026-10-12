import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. 페이지 설정
st.set_page_config(page_title="글로벌 SCM 분석", page_icon="🌍", layout="wide")

# [세션 상태 초기화] 지도 뷰 상태 및 선택 초기화
if "map_view" not in st.session_state:
    st.session_state.map_view = "all"

def reset_map_view():
    st.session_state.map_view = "all"

# 2. 프리미엄 다크 테마 & 세계지도 배경 CSS 주입
css = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
html, body, [class*='css'] { font-family: 'Pretendard', sans-serif !important; }

/* 배경화면 - 무겁고 깔끔한 글로벌 맵 / 우주 느낌 + 다크 오버레이 */
.stApp { 
    background-image: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.95)), 
                      url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* 메인 컨텐츠 영역 글래스모피즘 (유리 질감) 적용 */
.block-container { 
    background: rgba(17, 24, 39, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 3rem 4rem !important; 
    margin-top: 3rem;
    margin-bottom: 3rem;
    max-width: 1400px; 
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}
header { visibility: hidden; } footer { visibility: hidden; }

/* 텍스트 컬러 강제 지정 (배경이 어두우므로 라이트/다크모드 상관없이 밝은 텍스트 유지) */
h1, h2, h3, h4, h5, h6, p, li, span { color: #f8fafc !important; }

/* 메인 타이틀 배너 */
.dashboard-header { 
    background: rgba(0, 0, 0, 0.4);
    padding: 35px 40px; 
    border-radius: 12px; 
    margin-bottom: 40px; 
    border-bottom: 4px solid #bba14f; 
}
.dashboard-header h1 { margin: 0; font-size: 34px; font-weight: 800; letter-spacing: -1px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }

/* 제품 및 인증서 카드 */
.product-card { 
    background: rgba(255, 255, 255, 0.05); 
    border: 1px solid rgba(255, 255, 255, 0.1); 
    border-radius: 12px; padding: 30px 15px; text-align: center; height: 100%; 
    transition: all 0.3s ease;
}
.product-card:hover { transform: translateY(-5px); border-color: #bba14f; background: rgba(255, 255, 255, 0.1); }
.product-emoji { font-size: 48px; margin-bottom: 15px; filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.4)); }
.product-title { font-size: 16px; font-weight: 700; color: #e2e8f0; }

/* 섹션 타이틀 */
.section-title { 
    font-size: 24px; font-weight: 800; margin-top: 50px; margin-bottom: 25px; 
    display: inline-block; padding-bottom: 8px; border-bottom: 3px solid #bba14f;
}

/* 기업 개요 박스 */
.desc-box {
    background: rgba(0, 0, 0, 0.3); 
    border: 1px solid rgba(255, 255, 255, 0.1); 
    border-radius: 12px; padding: 30px;
    border-left: 6px solid #bba14f;
    font-size: 17px; line-height: 1.8; font-weight: 400; color: #cbd5e1 !important;
}

/* 🚀 오른쪽 인터랙티브 버튼 커스텀 (카드를 버튼화) */
.stButton > button {
    background: rgba(30, 41, 59, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 12px !important;
    padding: 20px 25px !important;
    text-align: left !important;
    display: flex !important;
    justify-content: flex-start !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #f8fafc !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
}
.stButton > button:hover {
    background: rgba(30, 41, 59, 1) !important;
    border-color: #bba14f !important;
    transform: translateX(-5px);
}
.stButton > button:active { transform: scale(0.98); }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. 헤더
st.markdown("<div class='dashboard-header'><h1>🌍 글로벌 SCM 및 파트너사 인프라 모니터링</h1></div>", unsafe_allow_html=True)

# 4. 데이터 (이전과 동일)
base_certs = [{"name": "IATF 16949", "img": "📜"}, {"name": "SQ 인증", "img": "🎖️"}, {"name": "ISO 9001/14001", "img": "🏅"}, {"name": "ESG 경영 우수", "img": "🌱"}]
suppliers = [
    {
        "name": "한성전장부산공장", "industry": "PCB", 
        "hq": "서울 서초구", "kr": "천안 공장, 구미 R&D센터", "gl": "베트남 하노이 공장, 미국 산호세 영업소",
        "desc": "국내 천안 및 구미에서 핵심 R&D 및 초기 양산을 진행하며, 대량 생산은 베트남 하노이 공장에서 담당하고 있습니다. 북미 주요 고객사 대응을 위해 미국 산호세에 직영 영업소를 운영 중입니다.",
        "products": [{"name": "PCB", "img": "🖲️"}, {"name": "임가공(조립)", "img": "⚙️"}],
        "certs": base_certs,
        "locations": [
            {"name": "본사 (서울)", "lat": 37.4836, "lon": 127.0326, "type": "hq"},
            {"name": "천안 공장", "lat": 36.8151, "lon": 127.1138, "type": "kr"},
            {"name": "구미 R&D", "lat": 36.1194, "lon": 128.3444, "type": "kr"},
            {"name": "하노이 공장", "lat": 21.0285, "lon": 105.8542, "type": "gl"},
            {"name": "산호세 영업소", "lat": 37.3382, "lon": -121.8863, "type": "gl"}
        ]
    },
    {
        "name": "효성정밀", "industry": "사출",
        "hq": "부산 사하구", "kr": "창원 공장", "gl": "중국 칭다오 공장, 미국 텍사스 법인",
        "desc": "부산 본사를 중심으로 창원과 중국 칭다오에서 주요 장비 부품을 가공하고 있습니다. 최근 북미 IRA 법안 대응 및 직납 체계 구축을 위해 미국 텍사스에 조립 법인을 신설하였습니다.",
        "products": [{"name": "WHEEL", "img": "🛞"}, {"name": "FLANGE", "img": "💿"}, {"name": "FLANGE COVER", "img": "🛡️"}],
        "certs": base_certs,
        "locations": [
            {"name": "본사 (부산)", "lat": 35.1044, "lon": 128.9748, "type": "hq"},
            {"name": "창원 공장", "lat": 35.2279, "lon": 128.6811, "type": "kr"},
            {"name": "칭다오 공장", "lat": 36.0671, "lon": 120.3826, "type": "gl"},
            {"name": "텍사스 법인", "lat": 31.9685, "lon": -99.9018, "type": "gl"}
        ]
    },
    {
        "name": "(주)성우", "industry": "PRESS(CASE)",
        "hq": "인천 남동구", "kr": "울산 공장, 여수 공장", "gl": "해당 없음",
        "desc": "해외 지사는 없으나, 국내 핵심 화학 단지인 울산과 여수에 대규모 생산 플랜트를 운영하여 매우 안정적인 내수 공급망을 확보하고 있는 건실한 기업입니다.",
        "products": [{"name": "ROTORCASE", "img": "🛢️"}, {"name": "CASE ASM", "img": "📦"}],
        "certs": base_certs,
        "locations": [
            {"name": "본사 (인천)", "lat": 37.4473, "lon": 126.7315, "type": "hq"},
            {"name": "울산 공장", "lat": 35.5383, "lon": 129.3113, "type": "kr"},
            {"name": "여수 공장", "lat": 34.7603, "lon": 127.6622, "type": "kr"}
        ]
    },
    {
        "name": "ZEB", "industry": "PRESS(CORE)",
        "hq": "경북 포항시", "kr": "포항 1, 2공장", "gl": "폴란드 브로츠와프 법인, 미국 미시간 법인",
        "desc": "글로벌 전기차 배터리 수요 증가에 대응하기 위해 포항에 대규모 양극재 라인을 증설하였으며, 유럽(폴란드)과 북미(미시간)에 핵심 생산 거점을 구축해 현지 조달 역량을 극대화했습니다.",
        "products": [{"name": "CORE", "img": "🔩"}, {"name": "ROTORCASE", "img": "🛢️"}],
        "certs": base_certs,
        "locations": [
            {"name": "본사 및 공장 (포항)", "lat": 36.0190, "lon": 129.3435, "type": "hq"},
            {"name": "폴란드 법인", "lat": 51.1079, "lon": 17.0385, "type": "gl"},
            {"name": "미국 미시간 법인", "lat": 43.3266, "lon": -84.5361, "type": "gl"}
        ]
    }
]

# 5. 사이드바 구성
with st.sidebar:
    st.markdown("<h3 style='color:#bba14f; font-weight:900;'>🏢 필터 및 업체 검색</h3>", unsafe_allow_html=True)
    
    industry_list = ["전체", "PCB", "PRESS(CASE)", "PRESS(CORE)", "사출", "임가공(조립)"]
    selected_industry = st.selectbox("🏷️ 업종 필터", industry_list, on_change=reset_map_view)
    
    filtered = suppliers
    if selected_industry != "전체":
        filtered = [s for s in filtered if s["industry"] == selected_industry]
        
    search_term = st.text_input("🔍 업체명 검색", placeholder="예: 한성전장").strip()
    if search_term:
        filtered = [s for s in filtered if search_term.lower() in s["name"].lower()]

    st.markdown("<hr style='border-color: rgba(255,255,255,0.2); margin: 20px 0;'>", unsafe_allow_html=True)
    
    # 🌟 메인 화면 선택지 추가
    options = ["🏠 종합 메인 화면"] + [s["name"] for s in filtered]
    selected_name = st.radio("📊 상세 분석할 업체 선택", options, on_change=reset_map_view)

# 6. 화면 출력 로직 분기
if selected_name == "🏠 종합 메인 화면":
    # --- [메인 화면 대시보드] ---
    st.markdown("<div class='section-title' style='margin-top:0;'>글로벌 SCM 통합 현황</div>", unsafe_allow_html=True)
    
    # 통계 메트릭 계산
    total_companies = len(filtered)
    all_locations = [loc for s in filtered for loc in s["locations"]]
    total_locs = len(all_locations)
    global_locs = len([l for l in all_locations if l["type"] == "gl"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📌 검색된 파트너사", f"{total_companies} 개사")
    col2.metric("🏭 총 운영 거점", f"{total_locs} 곳")
    col3.metric("🌐 해외 진출 거점", f"{global_locs} 곳")
    
    st.markdown("<div class='section-title'>전 세계 거점 분포도</div>", unsafe_allow_html=True)
    if all_locations:
        df_all = pd.DataFrame(all_locations)
        # 맵 스타일 다크로 고정
        view_state = pdk.ViewState(latitude=35.0, longitude=127.0, zoom=1.5, pitch=0)
        layer = pdk.Layer(
            "ScatterplotLayer", data=df_all, get_position='[lon, lat]',
            get_fill_color=[187, 161, 79, 200], get_line_color=[255, 255, 255], 
            stroked=True, line_width_min_pixels=1, get_radius=100000, 
            radius_min_pixels=5, radius_max_pixels=15, pickable=True,
        )
        st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/dark-v10", initial_view_state=view_state, layers=[layer], tooltip={"text": "{name}"}))
    else:
        st.info("해당 조건의 거점 데이터가 없습니다.")

else:
    # --- [상세 업체 화면] ---
    selected = next((s for s in filtered if s["name"] == selected_name), None)
    
    st.markdown(
        f"<div style='margin-bottom:25px; display:flex; align-items:baseline; gap: 15px;'>"
        f"<h2 style='margin:0; font-weight:900; font-size:42px; letter-spacing: -1px;'>{selected['name']}</h2>"
        f"<span style='background:rgba(255,255,255,0.1); border: 1px solid #bba14f; color:#bba14f; padding: 4px 12px; font-size: 15px; font-weight: 800; border-radius: 4px;'>{selected['industry']}</span></div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='section-title' style='margin-top:10px;'>기업 개요</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='desc-box'>{selected['desc']}</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>핵심 생산 품목 및 인증</div>", unsafe_allow_html=True)
    cols = st.columns(max(len(selected['products']), len(selected['certs'])))
    
    for idx, p in enumerate(selected['products']):
        cols[idx].markdown(f"<div class='product-card'><div class='product-emoji'>{p['img']}</div><div class='product-title'>{p['name']}</div></div>", unsafe_allow_html=True)
    for idx, c in enumerate(selected['certs']):
        if idx < len(cols): 
            cols[idx].markdown(f"<div class='product-card' style='margin-top:20px;'><div class='product-emoji'>{c['img']}</div><div class='product-title'>{c['name']}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>주요 거점 네트워크</div>", unsafe_allow_html=True)
    
    map_col, text_col = st.columns([1.8, 1])

    # 데이터 프레임 준비
    df_loc = pd.DataFrame(selected["locations"])

    # 🚀 오른쪽 인터랙티브 버튼 (누르면 Session State 변경)
    with text_col:
        st.markdown("<p style='color:#bba14f; font-weight:700; font-size:15px; margin-bottom:10px;'>🖱️ 아래 카드를 클릭하면 지도가 이동합니다.</p>", unsafe_allow_html=True)
        
        if st.button(f"🌍 전체 뷰 복귀", use_container_width=True):
            st.session_state.map_view = "all"
        st.write("")
        if st.button(f"🏢 본사 : {selected['hq']}", use_container_width=True):
            st.session_state.map_view = "hq"
        st.write("")
        if st.button(f"🏭 지사 : {selected['kr']}", use_container_width=True):
            st.session_state.map_view = "kr"
        st.write("")
        if selected['gl'] != "해당 없음":
            if st.button(f"🌐 해외 : {selected['gl']}", use_container_width=True):
                st.session_state.map_view = "gl"

    # 🚀 지도 렌더링 영역
    with map_col:
        current_view = st.session_state.map_view
        
        # 선택된 뷰에 따라 하이라이트 컬러 및 카메라 줌 조절
        def get_color(row):
            hi_colors = {'hq': [220, 38, 38, 255], 'kr': [37, 99, 235, 255], 'gl': [16, 185, 129, 255]}
            if current_view == "all": return [187, 161, 79, 200]
            elif current_view == row['type']: return hi_colors[row['type']]
            else: return [100, 100, 100, 80] # 선택 안된 곳은 흐리게

        df_loc['color'] = df_loc.apply(get_color, axis=1)
        
        # 줌 레벨 및 중심점 자동 계산 로직
        if current_view == "all":
            center_lat, center_lon = df_loc['lat'].mean(), df_loc['lon'].mean()
            zoom_lvl = 1.2 if (df_loc['lon'].max() - df_loc['lon'].min()) > 100 else 5.0
        else:
            target_df = df_loc[df_loc['type'] == current_view]
            if not target_df.empty:
                center_lat, center_lon = target_df['lat'].mean(), target_df['lon'].mean()
                # 거점이 여러 개면 살짝 넓게, 1개면 줌인
                zoom_lvl = 4.5 if len(target_df) > 1 else 10.0 
            else:
                center_lat, center_lon = df_loc['lat'].mean(), df_loc['lon'].mean()
                zoom_lvl = 1.5

        view_state = pdk.ViewState(
            latitude=center_lat, longitude=center_lon, 
            zoom=zoom_lvl, pitch=0, transition_duration=1200 # 부드러운 카메라 이동
        )
        
        layer = pdk.Layer(
            "ScatterplotLayer", data=df_loc,
            get_position='[lon, lat]', get_fill_color='color', get_line_color=[255, 255, 255], 
            stroked=True, line_width_min_pixels=2, get_radius=100000, 
            radius_min_pixels=8, radius_max_pixels=25, pickable=True,
        )
        
        with st.container():
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10", # 다크 맵 스타일
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "{name}"} 
            ))
