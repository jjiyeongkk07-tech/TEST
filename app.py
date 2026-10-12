import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. 페이지 설정
st.set_page_config(page_title="글로벌 SCM 분석", page_icon="🌍", layout="wide")

# [세션 상태 초기화] 지도 뷰 동기화 관리
if "radio_view" not in st.session_state:
    st.session_state.radio_view = "전체 뷰"
if "map_view" not in st.session_state:
    st.session_state.map_view = "전체 뷰"

# 라디오 버튼 변경 시 맵 뷰 업데이트
def update_radio():
    st.session_state.map_view = st.session_state.radio_view

# 우측 카드(버튼) 클릭 시 라디오와 맵 뷰 동시 업데이트
def set_view(view):
    st.session_state.map_view = view
    st.session_state.radio_view = view

def reset_map_view():
    st.session_state.map_view = "전체 뷰"
    st.session_state.radio_view = "전체 뷰"

# 2. 고급스러운 딥 슬레이트 네이비 테마 (Black 제외)
css = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
html, body, [class*='css'] { font-family: 'Pretendard', sans-serif !important; }

/* 🌟 배경 - 블랙 대신 가장 묵직하고 고급스러운 딥 네이비(Slate 900) */
.stApp { 
    background-color: #0f172a; 
}

/* 메인 대시보드 컨테이너 (Slate 800) */
.block-container { 
    background-color: #1e293b;
    padding: 3rem 4rem !important; 
    margin-top: 2rem;
    margin-bottom: 3rem;
    border-radius: 16px;
    max-width: 1400px; 
    border: 1px solid #334155;
    box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.7);
}
header { visibility: hidden; } footer { visibility: hidden; }

/* 사이드바 스타일 강제 적용 */
[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    border-right: 1px solid #1e293b !important;
}

/* 모든 텍스트 화이트/라이트그레이로 강제 고정 (가독성 보장) */
h1, h2, h3, h4, h5, h6, p, span, div, label, li { color: #f8fafc !important; }

/* 타이틀 배너 - 확실하게 보이도록 조치 */
.dashboard-header { 
    background: #0f172a; 
    padding: 35px 40px; 
    border-radius: 12px; 
    margin-bottom: 40px; 
    border-bottom: 4px solid #bba14f; 
    border: 1px solid #334155;
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}
.dashboard-header h1 { 
    margin: 0 !important; font-size: 34px !important; font-weight: 900 !important; 
    color: #ffffff !important; letter-spacing: -1px !important;
}

/* 섹션 타이틀 */
.section-title { 
    font-size: 22px; font-weight: 900; color: #ffffff !important; margin-top: 50px; margin-bottom: 25px; 
    display: inline-block; padding-bottom: 8px; border-bottom: 3px solid #bba14f;
    letter-spacing: -0.5px;
}

/* 기업 개요 박스 */
.desc-box {
    background-color: #0f172a; 
    border: 1px solid #334155; 
    border-radius: 12px; padding: 30px;
    border-left: 6px solid #bba14f;
    font-size: 17px; color: #cbd5e1 !important; line-height: 1.8; font-weight: 400;
}

/* 제품/인증서 카드 */
.product-card { 
    background: #0f172a; 
    border: 1px solid #334155; 
    border-radius: 12px; padding: 25px 15px; text-align: center; height: 100%; 
    transition: all 0.2s;
}
.product-card:hover { transform: translateY(-4px); border-color: #bba14f; background: #1e293b; }
.product-emoji { font-size: 46px; margin-bottom: 15px; }
.product-title { font-size: 16px; font-weight: 700; color: #f8fafc !important; }

/* 입력창 및 셀렉트박스 다크모드 커스텀 */
.stTextInput input, .stSelectbox div[data-baseweb="select"] {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid #334155 !important;
}

/* 우측 인터랙티브 카드(버튼) 스타일 */
.stButton > button {
    background-color: #0f172a !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 20px 25px !important;
    width: 100% !important;
    text-align: left !important;
    display: flex !important;
    justify-content: flex-start !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #f8fafc !important; 
    white-space: pre-wrap !important;
    line-height: 1.6 !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background-color: #1e293b !important;
    border-color: #bba14f !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active { transform: scale(0.98) !important; }

/* 탭(Radio) 버튼 스타일 강제 적용 */
div[role="radiogroup"] { padding-bottom: 15px; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. 헤더
st.markdown("<div class='dashboard-header'><h1>🌍 글로벌 SCM 및 파트너사 인프라 분석</h1></div>", unsafe_allow_html=True)

# 4. 데이터 (이전과 동일)
base_certs = [{"name": "IATF 16949", "img": "📜"}, {"name": "SQ 인증", "img": "🎖️"}, {"name": "ISO 9001", "img": "🏅"}, {"name": "ESG 우수", "img": "🌱"}]
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
    }
]

# 5. 사이드바
with st.sidebar:
    st.markdown("<h3 style='color:#bba14f !important; font-weight:900;'>🏢 필터 및 업체 검색</h3>", unsafe_allow_html=True)
    
    industry_list = ["전체", "PCB", "사출"]
    selected_industry = st.selectbox("🏷️ 업종 필터", industry_list, on_change=reset_map_view)
    
    filtered = suppliers
    if selected_industry != "전체":
        filtered = [s for s in filtered if s["industry"] == selected_industry]
        
    search_term = st.text_input("🔍 업체명 검색", placeholder="예: 한성전장").strip()
    if search_term:
        filtered = [s for s in filtered if search_term.lower() in s["name"].lower()]

    st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
    
    options_sidebar = ["🏠 종합 메인 화면"] + [s["name"] for s in filtered]
    selected_name = st.radio("📊 상세 분석할 업체 선택", options_sidebar, on_change=reset_map_view)

# 6. 메인 화면 출력
if selected_name == "🏠 종합 메인 화면":
    st.markdown("<div class='section-title' style='margin-top:0;'>글로벌 SCM 통합 현황</div>", unsafe_allow_html=True)
    
    total_companies = len(filtered)
    all_locations = [loc for s in filtered for loc in s["locations"]]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📌 검색된 파트너사", f"{total_companies} 개사")
    col2.metric("🏭 총 운영 거점", f"{len(all_locations)} 곳")
    col3.metric("🌐 해외 진출 거점", f"{len([l for l in all_locations if l['type'] == 'gl'])} 곳")
    
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
        st.pydeck_chart(pdk.Deck(map_style="dark", initial_view_state=view_state, layers=[layer], tooltip={"text": "{name}"}))

else:
    # --- [상세 업체 화면] ---
    selected = next((s for s in filtered if s["name"] == selected_name), None)
    
    st.markdown(
        f"<div style='margin-bottom:25px; display:flex; align-items:baseline; gap: 15px;'>"
        f"<h2 style='margin:0; font-weight:900; font-size:42px; letter-spacing: -1px;'>{selected['name']}</h2>"
        f"<span style='background:#0f172a; border: 1px solid #bba14f; color:#bba14f !important; padding: 4px 12px; font-size: 15px; font-weight: 800; border-radius: 4px;'>{selected['industry']}</span></div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='section-title' style='margin-top:10px;'>기업 개요</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='desc-box'>{selected['desc']}</div>", unsafe_allow_html=True)

    # 🚀 핵심 생산 품목과 품질 인증 좌우 분리 및 구분선 추가
    st.markdown("<div class='section-title'>핵심 역량 및 품질 인증</div>", unsafe_allow_html=True)
    
    # 2개의 큰 컬럼을 생성하고, CSS를 이용해 첫번째 컬럼 우측에 구분선을 그립니다.
    col_prod, col_cert = st.columns(2)
    
    with col_prod:
        st.markdown("<div style='border-right: 2px dashed #475569; padding-right: 30px; height: 100%;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#cbd5e1 !important; text-align:center; margin-bottom: 20px;'>📦 생산 품목</h4>", unsafe_allow_html=True)
        # 품목 렌더링 (2개씩 배치되도록 내부 컬럼)
        inner_cols = st.columns(2)
        for idx, p in enumerate(selected['products']):
            inner_cols[idx % 2].markdown(f"<div class='product-card' style='margin-bottom:15px;'><div class='product-emoji'>{p['img']}</div><div class='product-title'>{p['name']}</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cert:
        st.markdown("<div style='padding-left: 10px; height: 100%;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#cbd5e1 !important; text-align:center; margin-bottom: 20px;'>📜 품질 및 ESG 인증</h4>", unsafe_allow_html=True)
        inner_cols = st.columns(2)
        for idx, c in enumerate(selected['certs']):
            inner_cols[idx % 2].markdown(f"<div class='product-card' style='margin-bottom:15px;'><div class='product-emoji'>{c['img']}</div><div class='product-title'>{c['name']}</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


    # 🚀 거점 네트워크 (상단 라디오 탭 + 우측 연동 버튼)
    st.markdown("<div class='section-title'>주요 거점 네트워크</div>", unsafe_allow_html=True)
    
    # 타이틀 바로 아래에 라디오 버튼 배치 (지도의 뷰를 결정)
    options_map = ["전체 뷰", "🏢 국내(본사)", "🏭 국내(지사)", "🌐 해외"]
    st.radio("지도 필터", options_map, horizontal=True, key="radio_view", on_change=update_radio, label_visibility="collapsed")
    st.write("") # 간격 띄우기

    map_col, text_col = st.columns([1.8, 1])
    df_loc = pd.DataFrame(selected["locations"])

    # 우측 카드(버튼) 영역 ('전체 뷰 복귀' 버튼 삭제)
    with text_col:
        st.markdown("<p style='color:#bba14f !important; font-weight:800; font-size:15px; margin-bottom:10px;'>🖱️ 거점을 클릭하면 지도가 이동합니다.</p>", unsafe_allow_html=True)
        
        st.button(f"🏢 본사\n\n{selected['hq']}", on_click=set_view, args=("🏢 국내(본사)",), use_container_width=True)
        st.write("")
        st.button(f"🏭 지사\n\n{selected['kr']}", on_click=set_view, args=("🏭 국내(지사)",), use_container_width=True)
        
        if selected['gl'] != "해당 없음":
            st.write("")
            st.button(f"🌐 해외 지점\n\n{selected['gl']}", on_click=set_view, args=("🌐 해외",), use_container_width=True)

    # 지도 렌더링 영역
    with map_col:
        current_view = st.session_state.map_view
        
        # 강조 컬러 지정 (네이비 배경에 잘 어울리는 컬러)
        def get_color(row):
            base_colors = {'hq': [71, 85, 105, 200], 'kr': [71, 85, 105, 200], 'gl': [71, 85, 105, 200]}
            hi_colors = {'hq': [248, 113, 113, 255], 'kr': [56, 189, 248, 255], 'gl': [52, 211, 153, 255]} # Red, Blue, Green
            dim_color = [51, 65, 85, 80]
            
            if current_view == "전체 뷰": return [187, 161, 79, 200] # 전체일땐 골드
            elif current_view == "🏢 국내(본사)" and row['type'] == 'hq': return hi_colors['hq']
            elif current_view == "🏭 국내(지사)" and row['type'] == 'kr': return hi_colors['kr']
            elif current_view == "🌐 해외" and row['type'] == 'gl': return hi_colors['gl']
            else: return dim_color

        def get_radius(row):
            if current_view == "전체 뷰": return 120000
            if current_view == "🏢 국내(본사)" and row['type'] == 'hq': return 350000
            if current_view == "🏭 국내(지사)" and row['type'] == 'kr': return 350000
            if current_view == "🌐 해외" and row['type'] == 'gl': return 350000
            return 40000 

        df_loc['color'] = df_loc.apply(get_color, axis=1)
        df_loc['radius'] = df_loc.apply(get_radius, axis=1)
        
        if current_view == "전체 뷰":
            center_lat, center_lon = df_loc['lat'].mean(), df_loc['lon'].mean()
            zoom_lvl = 1.2 if (df_loc['lon'].max() - df_loc['lon'].min()) > 100 else 5.0
        else:
            target_type = 'hq' if "본사" in current_view else ('kr' if "지사" in current_view else 'gl')
            target_df = df_loc[df_loc['type'] == target_type]
            
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
        
        with st.container():
            st.pydeck_chart(pdk.Deck(
                map_style="dark", # 다크 맵 (네이비 배경과 환상적 조화)
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "{name}"} 
            ))
