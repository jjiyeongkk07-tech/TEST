import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. 페이지 설정 (라이트 테마 기반)
st.set_page_config(page_title="글로벌 SCM 분석", page_icon="🌍", layout="wide")

# [세션 상태 초기화] 지도 뷰 상태 관리
if "map_view" not in st.session_state:
    st.session_state.map_view = "all"

def reset_map_view():
    st.session_state.map_view = "all"

# 2. 눈에 확 띄는 깔끔한 프리미엄 라이트(Light) CSS 주입
css = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
html, body, [class*='css'] { font-family: 'Pretendard', sans-serif !important; }

/* 배경 및 기본 레이아웃 - 눈에 띄는 밝은 톤 (연한 그레이) */
.stApp { 
    background-color: #f4f6f9; 
}
.block-container { 
    background-color: #ffffff;
    padding: 3rem 4rem !important; 
    margin-top: 2rem;
    margin-bottom: 3rem;
    border-radius: 16px;
    max-width: 1400px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}
header { visibility: hidden; } footer { visibility: hidden; }

/* 메인 타이틀 배너 - 다크 네이비 + 골드 포인트 유지 (가장 눈에 잘 띔) */
.dashboard-header { 
    background: #111827; 
    padding: 35px 40px; 
    border-radius: 12px; 
    margin-bottom: 40px; 
    box-shadow: 0 10px 20px -5px rgba(0,0,0,0.2); 
    border-bottom: 4px solid #bba14f; 
}
.dashboard-header h1 { 
    margin: 0; font-size: 34px; font-weight: 800; color: #ffffff !important; 
    letter-spacing: -1px; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
}

/* 텍스트 컬러 강제 지정 해제 - 사이드바 및 메인 텍스트가 자연스럽게 검은색으로 보이도록 설정 */
p, span, label, li { color: #1e293b !important; }

/* 섹션 타이틀 - 묵직한 검은색 밑줄 포인트 */
.section-title { 
    font-size: 22px; font-weight: 900; color: #0f172a !important; margin-top: 50px; margin-bottom: 25px; 
    display: inline-block; padding-bottom: 8px; border-bottom: 3px solid #0f172a;
    letter-spacing: -0.5px;
}

/* 기업 개요 박스 - 원본 느낌 복구 */
.desc-box {
    background-color: #f8fafc; 
    border: 1px solid #e2e8f0; 
    border-radius: 8px; padding: 30px;
    border-left: 6px solid #bba14f;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02); 
    font-size: 17px; color: #334155 !important; line-height: 1.8; font-weight: 500;
}

/* 제품 및 인증서 카드 - 원본 복구 */
.product-card { 
    background: #ffffff; 
    border: 1px solid #e2e8f0; 
    border-radius: 8px; padding: 30px 15px; text-align: center; height: 100%; 
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); transition: all 0.2s;
}
.product-card:hover { transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #bba14f; }
.product-emoji { font-size: 50px; line-height: 1; margin-bottom: 15px; filter: drop-shadow(0px 3px 3px rgba(0,0,0,0.15)); }
.product-title { font-size: 16px; font-weight: 800; color: #1e293b !important; letter-spacing: -0.5px; }

/* 🚀 [가장 중요한 부분] 오른쪽 정보 카드를 클릭 가능한 '버튼'으로 변환하면서 카드 스타일 유지 */
.stButton > button {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    padding: 20px 25px !important;
    width: 100% !important;
    text-align: left !important;
    display: flex !important;
    justify-content: flex-start !important;
    font-size: 17px !important;
    font-weight: 800 !important;
    color: #0f172a !important; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    white-space: pre-wrap !important; /* 글씨 줄바꿈 허용 */
    line-height: 1.6 !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background-color: #f8fafc !important;
    border-color: #bba14f !important;
    box-shadow: 0 10px 15px rgba(0,0,0,0.1) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active { transform: scale(0.98) !important; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. 헤더
st.markdown("<div class='dashboard-header'><h1>🌍 글로벌 SCM 및 파트너사 인프라 분석</h1></div>", unsafe_allow_html=True)

# 4. 데이터
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

# 5. 사이드바 (기본 테마 적용으로 글씨가 완벽하게 보입니다)
with st.sidebar:
    st.markdown("<h3 style='color:#1e293b; font-weight:900;'>🏢 필터 및 업체 검색</h3>", unsafe_allow_html=True)
    
    industry_list = ["전체", "PCB", "PRESS(CASE)", "PRESS(CORE)", "사출", "임가공(조립)"]
    selected_industry = st.selectbox("🏷️ 업종 필터", industry_list, on_change=reset_map_view)
    
    filtered = suppliers
    if selected_industry != "전체":
        filtered = [s for s in filtered if s["industry"] == selected_industry]
        
    search_term = st.text_input("🔍 업체명 검색", placeholder="예: 한성전장").strip()
    if search_term:
        filtered = [s for s in filtered if search_term.lower() in s["name"].lower()]

    st.markdown("<hr style='border-color: #cbd5e1; margin: 20px 0;'>", unsafe_allow_html=True)
    
    options = ["🏠 종합 메인 화면"] + [s["name"] for s in filtered]
    selected_name = st.radio("📊 상세 분석할 업체 선택", options, on_change=reset_map_view)

# 6. 메인 화면 출력 로직
if selected_name == "🏠 종합 메인 화면":
    st.markdown("<div class='section-title' style='margin-top:0;'>글로벌 SCM 통합 현황</div>", unsafe_allow_html=True)
    
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
        view_state = pdk.ViewState(latitude=35.0, longitude=127.0, zoom=1.5, pitch=0)
        layer = pdk.Layer(
            "ScatterplotLayer", data=df_all, get_position='[lon, lat]',
            get_fill_color=[187, 161, 79, 200], get_line_color=[255, 255, 255], 
            stroked=True, line_width_min_pixels=1, get_radius=100000, 
            radius_min_pixels=6, radius_max_pixels=15, pickable=True,
        )
        # 맵 스타일을 가장 깔끔한 'light' 모드로 적용
        st.pydeck_chart(pdk.Deck(map_style="light", initial_view_state=view_state, layers=[layer], tooltip={"text": "{name}"}))
    else:
        st.info("해당 조건의 거점 데이터가 없습니다.")

else:
    # --- [상세 업체 화면] ---
    selected = next((s for s in filtered if s["name"] == selected_name), None)
    
    st.markdown(
        f"<div style='margin-bottom:25px; display:flex; align-items:baseline; gap: 15px;'>"
        f"<h2 style='margin:0; font-weight:900; font-size:42px; letter-spacing: -1px; color:#0f172a;'>{selected['name']}</h2>"
        f"<span style='background:#f1f5f9; border: 1px solid #bba14f; color:#bba14f !important; padding: 4px 12px; font-size: 15px; font-weight: 800; border-radius: 4px;'>{selected['industry']}</span></div>",
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
    df_loc = pd.DataFrame(selected["locations"])

    # 🚀 우측 정보 카드 (버튼으로 동작하여 지도를 움직임)
    with text_col:
        st.markdown("<p style='color:#bba14f !important; font-weight:800; font-size:15px; margin-bottom:10px;'>🖱️ 아래 카드를 클릭하면 지도가 이동합니다.</p>", unsafe_allow_html=True)
        
        # 버튼 텍스트에 줄바꿈(\n\n)을 넣어서 원본 카드의 Title/Value 느낌을 그대로 재현
        if st.button(f"🌍 전체 뷰 복귀\n\n모든 거점을 한눈에 확인합니다.", use_container_width=True):
            st.session_state.map_view = "all"
        st.write("")
        if st.button(f"🏢 국내(본사)\n\n{selected['hq']}", use_container_width=True):
            st.session_state.map_view = "hq"
        st.write("")
        if st.button(f"🏭 국내(지사)\n\n{selected['kr']}", use_container_width=True):
            st.session_state.map_view = "kr"
        st.write("")
        if selected['gl'] != "해당 없음":
            if st.button(f"🌐 해외 지사\n\n{selected['gl']}", use_container_width=True):
                st.session_state.map_view = "gl"

    # 🚀 지도 랜더링 (원본 디자인 컬러 + 클릭 연동)
    with map_col:
        current_view = st.session_state.map_view
        
        # 원본에서 썼던 강조 색상 로직 복구
        def get_color(row):
            base_colors = {'hq': [31, 41, 55, 220], 'kr': [107, 114, 128, 220], 'gl': [187, 161, 79, 220]}
            hi_colors = {'hq': [220, 38, 38, 255], 'kr': [37, 99, 235, 255], 'gl': [16, 185, 129, 255]}
            dim_color = [156, 163, 175, 100]
            
            if current_view == "all": return base_colors[row['type']]
            elif current_view == row['type']: return hi_colors[row['type']]
            else: return dim_color

        # 원본에서 썼던 점 크기(반경) 확대 로직 복구
        def get_radius(row):
            if current_view == "all": return 120000
            if current_view == row['type']: return 350000
            return 40000 

        df_loc['color'] = df_loc.apply(get_color, axis=1)
        df_loc['radius'] = df_loc.apply(get_radius, axis=1)
        
        # 카메라 자동 이동 로직
        if current_view == "all":
            center_lat, center_lon = df_loc['lat'].mean(), df_loc['lon'].mean()
            zoom_lvl = 1.2 if (df_loc['lon'].max() - df_loc['lon'].min()) > 100 else 5.0
        else:
            target_df = df_loc[df_loc['type'] == current_view]
            if not target_df.empty:
                center_lat, center_lon = target_df['lat'].mean(), target_df['lon'].mean()
                zoom_lvl = 4.5 if len(target_df) > 1 else 10.0 
            else:
                center_lat, center_lon = df_loc['lat'].mean(), df_loc['lon'].mean()
                zoom_lvl = 1.5

        view_state = pdk.ViewState(
            latitude=center_lat, longitude=center_lon, 
            zoom=zoom_lvl, pitch=0, transition_duration=1200
        )
        
        layer = pdk.Layer(
            "ScatterplotLayer", data=df_loc,
            get_position='[lon, lat]', get_fill_color='color', get_line_color=[255, 255, 255], 
            stroked=True, line_width_min_pixels=2, get_radius='radius', 
            radius_min_pixels=6, radius_max_pixels=30, pickable=True,
        )
        
        with st.container(border=True):
            # 원본 요청대로 밝고 깔끔한 light 맵 적용
            st.pydeck_chart(pdk.Deck(
                map_style="light", 
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "{name}"} 
            ))
