import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. 페이지 설정
st.set_page_config(page_title="글로벌 SCM 분석", page_icon="🌍", layout="wide")

# [세션 상태 초기화] 지도 뷰 상태 관리
if "map_view" not in st.session_state:
    st.session_state.map_view = "전체 뷰"

def set_view(view):
    st.session_state.map_view = view

def reset_map_view():
    st.session_state.map_view = "전체 뷰"

# 2. 임원 보고용 프리미엄 엔터프라이즈 테마 (Silver Gray & Deep Navy & Gold)
css = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
html, body, [class*='css'] { font-family: 'Pretendard', sans-serif !important; }

/* 🌟 배경 - 단순 화이트가 아닌 고급스러운 실버/슬레이트 그레이 그라데이션 */
.stApp { 
    background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); 
}

/* 메인 대시보드 컨테이너 - 깔끔한 화이트 패널과 부드러운 그림자 */
.block-container { 
    background-color: #ffffff;
    padding: 3rem 4rem !important; 
    margin-top: 2rem;
    margin-bottom: 3rem;
    border-radius: 16px;
    max-width: 1400px; 
    border: 1px solid #cbd5e1;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05);
}

header { visibility: hidden; } footer { visibility: hidden; }

/* 사이드바 스타일 - 배경과 어우러지는 톤 */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #cbd5e1 !important;
}

/* 🚀 텍스트 컬러 최적화 - 완전 검은색이 아닌 세련된 진회색/네이비톤 */
h1, h2, h3, h4, p, span, label, li { color: #1e293b !important; }
[data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 900 !important; }
[data-testid="stMetricLabel"] { color: #64748b !important; font-weight: 700 !important; }

/* 섹션 타이틀 - 딥 네이비 컬러와 골드 밑줄 */
.section-title { 
    font-size: 22px; font-weight: 900; color: #0f172a !important; margin-top: 40px; margin-bottom: 25px; 
    display: inline-block; padding-bottom: 8px; border-bottom: 3px solid #bba14f;
}

/* 제품/인증서 카드 - 임원 보고용의 깔끔한 카드 스타일 */
.product-card { 
    background-color: #ffffff !important; 
    border: 1px solid #e2e8f0 !important; 
    border-radius: 12px !important; 
    padding: 25px 15px !important; 
    text-align: center !important; 
    height: 100% !important; 
    transition: all 0.2s !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
}
.product-card:hover { 
    transform: translateY(-4px) !important; 
    border-color: #bba14f !important; 
    box-shadow: 0 10px 15px rgba(0,0,0,0.08) !important;
}
.product-emoji { 
    font-size: 42px !important; 
    margin-bottom: 12px !important; 
    filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.1)) !important;
}
.product-title { 
    font-size: 16px !important; 
    font-weight: 800 !important; 
    color: #1e293b !important; 
}

/* 좌우 구분선 (Streamlit 컬럼 내 적용) */
.vertical-divider {
    border-right: 2px dashed #cbd5e1;
    padding-right: 30px;
    height: 100%;
}
.right-padding {
    padding-left: 10px;
    height: 100%;
}

/* 우측 인터랙티브 카드(버튼) 스타일 - 고급스러운 화이트 버튼 */
.stButton > button {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 20px 25px !important;
    width: 100% !important;
    text-align: left !important;
    display: flex !important;
    justify-content: flex-start !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    color: #1e293b !important; 
    white-space: pre-wrap !important;
    line-height: 1.6 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
}
.stButton > button:hover {
    background-color: #f8fafc !important;
    border-color: #bba14f !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 12px rgba(0,0,0,0.05) !important;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. 헤더 (타이틀 배너만 딥 네이비로 처리하여 강렬한 대비감 부여)
st.markdown("""
<div style="background: #0f172a; padding: 30px 40px; border-radius: 12px; margin-bottom: 40px; border-bottom: 4px solid #bba14f; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
    <h1 style="margin: 0; font-size: 34px; font-weight: 900; color: #ffffff !important;">🌍 글로벌 SCM 및 파트너사 인프라 분석</h1>
</div>
""", unsafe_allow_html=True)

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

    st.markdown("<hr style='border-color: #cbd5e1; margin: 20px 0;'>", unsafe_allow_html=True)
    
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
        st.pydeck_chart(pdk.Deck(map_style="light", initial_view_state=view_state, layers=[layer], tooltip={"text": "{name}"}))

else:
    # --- [상세 업체 화면] ---
    selected = next((s for s in filtered if s["name"] == selected_name), None)
    
    # 타이틀
    st.markdown(
        f"<div style='margin-bottom:25px; display:flex; align-items:baseline; gap: 15px;'>"
        f"<h2 style='margin:0; font-weight:900; font-size:42px; letter-spacing: -1px; color:#0f172a !important;'>{selected['name']}</h2>"
        f"<span style='background:#f8fafc; border: 1px solid #bba14f; color:#bba14f !important; padding: 4px 12px; font-size: 15px; font-weight: 800; border-radius: 4px;'>{selected['industry']}</span></div>",
        unsafe_allow_html=True
    )

    # 기업 개요
    st.markdown("<div class='section-title' style='margin-top:10px;'>기업 개요</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='background-color:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:30px; border-left:6px solid #bba14f; font-size:17px; color:#334155 !important; line-height:1.8;'>"
        f"{selected['desc']}</div>", 
        unsafe_allow_html=True
    )

    # 🚀 핵심 역량 및 품질 인증
    st.markdown("<div class='section-title'>핵심 역량 및 품질 인증</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 30px; margin-bottom: 20px;">
    """, unsafe_allow_html=True)

    col_prod, col_cert = st.columns([1, 1])

    with col_prod:
        st.markdown("<div class='vertical-divider'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #0f172a !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>📦 핵심 생산 품목</h4>", unsafe_allow_html=True)
        p_cols = st.columns(2)
        for idx, p in enumerate(selected['products']):
            p_cols[idx % 2].markdown(
                f"<div class='product-card'><div class='product-emoji'>{p['img']}</div><div class='product-title'>{p['name']}</div></div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cert:
        st.markdown("<div class='right-padding'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #0f172a !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>📜 품질 및 ESG 인증</h4>", unsafe_allow_html=True)
        c_cols = st.columns(2)
        for idx, c in enumerate(selected['certs']):
            c_cols[idx % 2].markdown(
                f"<div class='product-card' style='margin-bottom:15px;'><div class='product-emoji'>{c['img']}</div><div class='product-title'>{c['name']}</div></div>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


    # 🚀 거점 네트워크 
    st.markdown("<div class='section-title' style='margin-top: 50px;'>주요 거점 네트워크</div>", unsafe_allow_html=True)
    
    map_col, text_col = st.columns([1.8, 1])
    df_loc = pd.DataFrame(selected["locations"])

    # 우측 컨트롤러
    with text_col:
        st.markdown("<p style='color:#bba14f !important; font-weight:800; font-size:15px; margin-bottom:10px;'>🖱️ 거점을 클릭하면 지도가 이동합니다.</p>", unsafe_allow_html=True)
        
        st.button("🌍 전체 뷰", on_click=set_view, args=("전체 뷰",), use_container_width=True)
        st.write("")
        st.button(f"🏢 본사\n\n{selected['hq']}", on_click=set_view, args=("🏢 국내(본사)",), use_container_width=True)
        st.write("")
        st.button(f"🏭 지사\n\n{selected['kr']}", on_click=set_view, args=("🏭 국내(지사)",), use_container_width=True)
        
        if selected['gl'] != "해당 없음":
            st.write("")
            st.button(f"🌐 해외 지점\n\n{selected['gl']}", on_click=set_view, args=("🌐 해외",), use_container_width=True)

    # 지도 렌더링 영역 (라이트 테마 맵 적용)
    with map_col:
        current_view = st.session_state.map_view
        
        def get_color(row):
            hi_colors = {'hq': [220, 38, 38, 255], 'kr': [37, 99, 235, 255], 'gl': [16, 185, 129, 255]} 
            dim_color = [148, 163, 184, 100]
            
            if current_view == "전체 뷰": return [187, 161, 79, 220]
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
                map_style="light",
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "{name}"} 
            ))
