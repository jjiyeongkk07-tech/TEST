import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. 페이지 설정
st.set_page_config(page_title="글로벌 SCM 분석", page_icon="🌍", layout="wide")

# 2. 다크/라이트 모드 모두 호환되는 프리미엄 & 묵직한 CSS 주입
css = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
html, body, [class*='css'] { font-family: 'Pretendard', sans-serif !important; }

/* 배경 및 기본 레이아웃 - Streamlit 테마에 자동 적응 */
.stApp { background-color: transparent; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }
header { visibility: hidden; } footer { visibility: hidden; }

/* 메인 타이틀 배너 - 항상 다크 네이비 톤 + 골드 포인트 유지 (글자색 강제 지정) */
.dashboard-header { 
    background: #111827; 
    padding: 35px 40px; 
    border-radius: 8px; 
    margin-bottom: 40px; 
    box-shadow: 0 15px 25px -5px rgba(0,0,0,0.4); 
    border-bottom: 4px solid #bba14f; 
    position: relative; 
}
.dashboard-header h1 { 
    margin: 0; font-size: 32px; font-weight: 800; color: #ffffff !important; 
    letter-spacing: -1px; text-transform: uppercase;
}

/* 정보 카드 - 다크/라이트 모드 테마 변수 적용 */
.info-card { 
    background-color: var(--secondary-background-color); 
    border: 1px solid var(--faded-text-color); 
    border-radius: 8px; 
    padding: 30px 25px; height: 100%; 
    box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
    transition: all 0.3s ease; 
}
.info-card:hover { box-shadow: 0 10px 20px rgba(0,0,0,0.2); border-color: #bba14f; }
.info-card-title { font-size: 14px; color: var(--faded-text-color); font-weight: 700; margin-bottom: 12px; letter-spacing: 1px; }
.info-card-value { font-size: 19px; color: var(--text-color); font-weight: 800; line-height: 1.5; letter-spacing: -0.5px; }

/* 제품 및 인증서 카드 */
.product-card { 
    background: var(--secondary-background-color); 
    border: 1px solid var(--faded-text-color); 
    border-radius: 8px; padding: 40px 15px; text-align: center; height: 100%; 
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); transition: all 0.2s;
}
.product-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.2); border-color: #bba14f; }
.product-emoji { font-size: 56px; line-height: 1; margin-bottom: 20px; filter: drop-shadow(0px 5px 5px rgba(0,0,0,0.2)); }
.product-title { font-size: 17px; font-weight: 800; color: var(--text-color); letter-spacing: -0.5px; word-break: keep-all; }

/* 섹션 타이틀 - 묵직한 밑줄 포인트 */
.section-title { 
    font-size: 22px; font-weight: 900; color: var(--text-color); margin-top: 50px; margin-bottom: 25px; 
    display: inline-block; padding-bottom: 8px; border-bottom: 3px solid var(--text-color);
    letter-spacing: -0.5px;
}

/* 기업 개요 박스 - 묵직한 골드 바(Bar) 포인트 */
.desc-box {
    background-color: var(--secondary-background-color); 
    border: 1px solid var(--faded-text-color); 
    border-radius: 8px; padding: 30px;
    border-left: 6px solid #bba14f;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
    font-size: 17px; color: var(--text-color); line-height: 1.8; font-weight: 500;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. 헤더
st.markdown("<div class='dashboard-header'><h1>🌍 글로벌 SCM 및 파트너사 인프라 분석</h1></div>", unsafe_allow_html=True)

# 4. 데이터 
base_certs = [
    {"name": "IATF 16949", "img": "📜"},
    {"name": "SQ 인증", "img": "🎖️"},
    {"name": "ISO 9001 / 14001", "img": "🏅"},
    {"name": "ESG 경영 우수", "img": "🌱"}
]

suppliers = [
    {
        "name": "A업체", "industry": "PCB", 
        "hq": "서울 서초구", "kr": "천안 공장, 구미 R&D센터", "gl": "베트남 하노이 공장, 미국 산호세 영업소",
        "desc": "국내 천안 및 구미에서 핵심 R&D 및 초기 양산을 진행하며, 대량 생산은 베트남 하노이 공장에서 담당하고 있습니다. 북미 주요 고객사 대응을 위해 미국 산호세에 직영 영업소를 운영 중입니다.",
        "products": [{"name": "PCB", "img": "🖲️"}, {"name": "원재료", "img": "🪨"}],
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
        "name": "B업체", "industry": "가공(일반)",
        "hq": "부산 사하구", "kr": "창원 공장", "gl": "중국 칭다오 공장, 미국 텍사스 법인",
        "desc": "부산 본사를 중심으로 창원과 중국 칭다오에서 주요 장비 부품을 가공하고 있습니다. 최근 북미 IRA 법안 대응 및 직납 체계 구축을 위해 미국 텍사스에 조립 법인을 신설하였습니다.",
        "products": [{"name": "SHAFT", "img": "⚙️"}, {"name": "Bearing", "img": "🔄"}, {"name": "GEAR", "img": "🛞"}],
        "certs": base_certs,
        "locations": [
            {"name": "본사 (부산)", "lat": 35.1044, "lon": 128.9748, "type": "hq"},
            {"name": "창원 공장", "lat": 35.2279, "lon": 128.6811, "type": "kr"},
            {"name": "칭다오 공장", "lat": 36.0671, "lon": 120.3826, "type": "gl"},
            {"name": "텍사스 법인", "lat": 31.9685, "lon": -99.9018, "type": "gl"}
        ]
    },
    {
        "name": "C업체", "industry": "에폭시",
        "hq": "인천 남동구", "kr": "울산 공장, 여수 공장", "gl": "해당 없음",
        "desc": "해외 지사는 없으나, 국내 핵심 화학 단지인 울산과 여수에 대규모 생산 플랜트를 운영하여 매우 안정적인 내수 공급망을 확보하고 있는 건실한 기업입니다.",
        "products": [{"name": "RUBBER", "img": "🧤"}],
        "certs": base_certs,
        "locations": [
            {"name": "본사 (인천)", "lat": 37.4473, "lon": 126.7315, "type": "hq"},
            {"name": "울산 공장", "lat": 35.5383, "lon": 129.3113, "type": "kr"},
            {"name": "여수 공장", "lat": 34.7603, "lon": 127.6622, "type": "kr"}
        ]
    },
    {
        "name": "D업체", "industry": "원재료(철판)",
        "hq": "경북 포항시", "kr": "포항 1, 2공장", "gl": "폴란드 브로츠와프 법인, 미국 미시간 법인",
        "desc": "글로벌 전기차 배터리 수요 증가에 대응하기 위해 포항에 대규모 양극재 라인을 증설하였으며, 유럽(폴란드)과 북미(미시간)에 핵심 생산 거점을 구축해 현지 조달 역량을 극대화했습니다.",
        "products": [{"name": "원재료", "img": "🪨"}],
        "certs": base_certs,
        "locations": [
            {"name": "본사 및 공장 (포항)", "lat": 36.0190, "lon": 129.3435, "type": "hq"},
            {"name": "폴란드 법인", "lat": 51.1079, "lon": 17.0385, "type": "gl"},
            {"name": "미국 미시간 법인", "lat": 43.3266, "lon": -84.5361, "type": "gl"}
        ]
    },
    {
        "name": "E업체", "industry": "임가공(조립)",
        "hq": "경기 화성시", "kr": "동탄 R&D센터, 평택 공장", "gl": "대만 신주 연락사무소, 미국 실리콘밸리 지사",
        "desc": "국내 주요 반도체 제조사와의 끈끈한 협력을 바탕으로 화성과 평택에 차세대 장비 R&D 센터를 운영 중입니다. TSMC 및 인텔과의 기술 교류를 위해 대만과 미국 지사를 최근 오픈했습니다.",
        "products": [{"name": "TERMINAL", "img": "🔌"}, {"name": "MAGNET WIRE", "img": "🧵"}],
        "certs": base_certs,
        "locations": [
            {"name": "본사 (화성)", "lat": 37.1995, "lon": 126.8315, "type": "hq"},
            {"name": "평택 R&D", "lat": 36.9921, "lon": 127.1129, "type": "kr"},
            {"name": "대만 신주 사무소", "lat": 24.8138, "lon": 120.9675, "type": "gl"},
            {"name": "실리콘밸리 지사", "lat": 37.3875, "lon": -122.0575, "type": "gl"}
        ]
    },
    {
        "name": "F업체", "industry": "사출",
        "hq": "경기 파주시", "kr": "파주 LCD/OLED 라인", "gl": "베트남 하이퐁 조립공장",
        "desc": "파주 본사에서 고부가가치 하이엔드 OLED 패널 부품을 생산하고, 노동 집약적인 후공정 및 모듈 조립은 베트남 하이퐁 공장으로 이관하여 원가 경쟁력을 크게 확보하고 있습니다.",
        "products": [{"name": "MAGNET", "img": "🧲"}, {"name": "CORE", "img": "🔩"}],
        "certs": base_certs,
        "locations": [
            {"name": "본사 (파주)", "lat": 37.7600, "lon": 126.7800, "type": "hq"},
            {"name": "하이퐁 공장", "lat": 20.8449, "lon": 106.6881, "type": "gl"}
        ]
    },
    {
        "name": "G업체", "industry": "PRESS(CASE)",
        "hq": "경기 수원시", "kr": "화성 주행시험장", "gl": "멕시코 몬테레이 공장, 헝가리 부다페스트 공장",
        "desc": "수원 본사 및 화성 주행시험장에서 자율주행 모듈을 개발합니다. 북미 3대 완성차 업체 납품을 위해 멕시코에, 유럽 자동차 메이커 대응을 위해 헝가리에 각각 대형 공장을 가동하고 있습니다.",
        "products": [{"name": "CASE", "img": "📦"}, {"name": "BRUSH", "img": "🖌️"}],
        "certs": base_certs,
        "locations": [
            {"name": "본사 (수원)", "lat": 37.2636, "lon": 127.0286, "type": "hq"},
            {"name": "화성 시험장", "lat": 37.2100, "lon": 126.8100, "type": "kr"},
            {"name": "멕시코 몬테레이", "lat": 25.6866, "lon": -100.3161, "type": "gl"},
            {"name": "헝가리 부다페스트", "lat": 47.4979, "lon": 19.0402, "type": "gl"}
        ]
    }
]

# 5. 사이드바 
with st.sidebar:
    st.markdown("<h3 style='color:var(--text-color); margin-bottom:20px; font-weight:900;'>🏢 파트너사 상세 검색</h3>", unsafe_allow_html=True)
    
    all_industries = [
        "PCB", "PRESS(CASE)", "PRESS(CORE)", "PRESS(TERMINAL)", "RUBBER",
        "가공(COMM;Y)", "가공(DIECASTING)", "가공(MAGNET WIRE)", "가공(SHAFT)", "가공(일반)",
        "단조", "라벨", "베어링", "사출", "소결(BRUSH)", "소결(GEAR)", "소결(MAGNET)", 
        "에폭시", "원재료(SHAFT)", "원재료(사출)", "원재료(철판)", "원재료(황동)", 
        "일반구매", "임가공(조립)", "포장재"
    ]
    
    industry_list = ["전체"] + all_industries
    selected_industry = st.selectbox("🏷️ 업종 필터", industry_list)
    
    filtered = suppliers
    if selected_industry != "전체":
        filtered = [s for s in filtered if s["industry"] == selected_industry]
    
    product_set = set()
    for s in filtered:
        for p in s["products"]:
            product_set.add(p["name"])
    
    product_list = ["전체"] + sorted(list(product_set))
    selected_product = st.selectbox("📦 세부 품목 필터", product_list)
    
    if selected_product != "전체":
        filtered = [s for s in filtered if any(p["name"] == selected_product for p in s["products"])]
        
    region_list = ["전체", "국내", "중국", "인도", "유럽", "베트남"]
    selected_region = st.selectbox("🌍 지역 필터", region_list)
    
    if selected_region == "국내":
        filtered = [s for s in filtered if s["gl"] == "해당 없음"]
    elif selected_region == "유럽":
        filtered = [s for s in filtered if any(x in s["gl"] for x in ["유럽", "폴란드", "헝가리"])]
    elif selected_region != "전체":
        filtered = [s for s in filtered if selected_region in s["gl"]]

    search_term = st.text_input("🔍 업체명 검색", placeholder="예: A업체").strip()
    
    if search_term:
        filtered = [s for s in filtered if search_term.lower() in s["name"].lower()]

    if not filtered:
        st.warning("조건에 맞는 업체가 없습니다.")
        selected = None
    else:
        st.markdown("<hr style='border-color: var(--faded-text-color); margin: 20px 0;'>", unsafe_allow_html=True)
        selected_name = st.radio("📊 상세 분석할 업체 선택", [s["name"] for s in filtered])
        selected = next((s for s in filtered if s["name"] == selected_name), None)

# 6. 메인 화면 출력 (순서 재배치)
if selected:
    # [순서 1] 타이틀 및 기업 개요
    st.markdown(
        f"<div style='margin-bottom:25px; display:flex; align-items:baseline; gap: 15px;'>"
        f"<h2 style='margin:0; color:var(--text-color); font-weight:900; font-size:42px; letter-spacing: -1px;'>{selected['name']}</h2>"
        f"<span style='background:#111827; color:#bba14f; padding: 4px 12px; font-size: 15px; font-weight: 800; border-radius: 4px;'>{selected['industry']}</span></div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='section-title'>기업 개요</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='desc-box'>{selected['desc']}</div>", unsafe_allow_html=True)

    # [순서 2] 품질 인증 및 ESG 경영
    st.markdown("<div class='section-title'>품질 인증 및 ESG 경영</div>", unsafe_allow_html=True)
    cols_cert = st.columns(len(selected['certs']))
    for idx, c in enumerate(selected['certs']):
        cols_cert[idx].markdown(
            f"<div class='product-card'><div class='product-emoji'>{c['img']}</div><div class='product-title'>{c['name']}</div></div>",
            unsafe_allow_html=True
        )

    # [순서 3] 핵심 생산 품목
    st.markdown("<div class='section-title'>핵심 생산 품목</div>", unsafe_allow_html=True)
    cols_prod = st.columns(len(selected['products']))
    for idx, p in enumerate(selected['products']):
        cols_prod[idx].markdown(
            f"<div class='product-card'><div class='product-emoji'>{p['img']}</div><div class='product-title'>{p['name']}</div></div>",
            unsafe_allow_html=True
        )

    # [순서 4] 주요 거점 네트워크 (지도)
    st.markdown("<div class='section-title'>주요 거점 네트워크</div>", unsafe_allow_html=True)
    
    # 강조할 지역 옵션명 변경
    highlight_opt = st.radio(
        "📍 지도에서 강조할 지역을 선택하세요:", 
        ["전체 보기", "🏢 국내(본사)", "🇰🇷 국내(지사)", "🌐 해외"], 
        horizontal=True
    )
    
    map_col, text_col = st.columns([1.5, 1])

    with map_col:
        df_loc = pd.DataFrame(selected["locations"])
        
        def get_color(row):
            base_colors = {'hq': [31, 41, 55, 220], 'kr': [107, 114, 128, 220], 'gl': [187, 161, 79, 220]}
            hi_colors = {'hq': [220, 38, 38, 255], 'kr': [37, 99, 235, 255], 'gl': [16, 185, 129, 255]}
            dim_color = [156, 163, 175, 100]
            
            if highlight_opt == "전체 보기": return base_colors[row['type']]
            elif highlight_opt == "🏢 국내(본사)" and row['type'] == 'hq': return hi_colors['hq']
            elif highlight_opt == "🇰🇷 국내(지사)" and row['type'] == 'kr': return hi_colors['kr']
            elif highlight_opt == "🌐 해외" and row['type'] == 'gl': return hi_colors['gl']
            else: return dim_color

        def get_radius(row):
            if highlight_opt == "전체 보기": return 120000
            if highlight_opt == "🏢 국내(본사)" and row['type'] == 'hq': return 350000
            if highlight_opt == "🇰🇷 국내(지사)" and row['type'] == 'kr': return 350000
            if highlight_opt == "🌐 해외" and row['type'] == 'gl': return 350000
            return 40000 

        df_loc['color'] = df_loc.apply(get_color, axis=1)
        df_loc['radius'] = df_loc.apply(get_radius, axis=1)
        
        if highlight_opt == "전체 보기":
            center_lat, center_lon = df_loc['lat'].mean(), df_loc['lon'].mean()
            lon_range = df_loc['lon'].max() - df_loc['lon'].min()
            zoom_lvl = 1.0 if lon_range > 150 else (2.5 if lon_range > 50 else 5.5)
        else:
            target_type = 'hq' if "본사" in highlight_opt else ('kr' if "지사" in highlight_opt else 'gl')
            target_df = df_loc[df_loc['type'] == target_type]
            
            if not target_df.empty:
                center_lat, center_lon = target_df['lat'].mean(), target_df['lon'].mean()
                if len(target_df) == 1:
                    zoom_lvl = 5.5 
                else:
                    lon_range = target_df['lon'].max() - target_df['lon'].min()
                    zoom_lvl = 2.0 if lon_range > 100 else (3.5 if lon_range > 20 else 5.5)
            else:
                center_lat, center_lon = df_loc['lat'].mean(), df_loc['lon'].mean()
                zoom_lvl = 2.0

        view_state = pdk.ViewState(
            latitude=center_lat, 
            longitude=center_lon, 
            zoom=zoom_lvl, 
            pitch=0,
            transition_duration=1000 
        )
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_loc,
            get_position='[lon, lat]',
            get_fill_color='color',
            get_line_color=[255, 255, 255], 
            stroked=True,
            line_width_min_pixels=2,
            get_radius='radius',
            radius_min_pixels=6,  
            radius_max_pixels=30, 
            pickable=True,
        )
        
        with st.container(border=True):
            st.pydeck_chart(pdk.Deck(
                map_style="light", # 지도가 검게 나오는 현상 방지 (밝은 테마 고정)
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "{name}"} 
            ))

    with text_col:
        hq_border = "#dc2626" if "본사" in highlight_opt else "var(--faded-text-color)"
        kr_border = "#2563eb" if "지사" in highlight_opt else "var(--faded-text-color)"
        gl_border = "#10b981" if "해외" in highlight_opt else ("#bba14f" if selected['gl'] != "해당 없음" else "var(--faded-text-color)")
        
        hq_opacity = "1" if highlight_opt in ["전체 보기", "🏢 국내(본사)"] else "0.4"
        kr_opacity = "1" if highlight_opt in ["전체 보기", "🇰🇷 국내(지사)"] else "0.4"
        gl_opacity = "1" if highlight_opt in ["전체 보기", "🌐 해외"] else "0.4"

        st.markdown(f"<div class='info-card' style='border-left: 6px solid {hq_border}; opacity: {hq_opacity};'><div class='info-card-title'>🏢 국내(본사)</div><div class='info-card-value'>{selected['hq']}</div></div>", unsafe_allow_html=True)
        st.write("") 
        st.markdown(f"<div class='info-card' style='border-left: 6px solid {kr_border}; opacity: {kr_opacity};'><div class='info-card-title'>🇰🇷 국내(지사)</div><div class='info-card-value'>{selected['kr']}</div></div>", unsafe_allow_html=True)
        st.write("") 
        st.markdown(f"<div class='info-card' style='border-left: 6px solid {gl_border}; opacity: {gl_opacity};'><div class='info-card-title'>🌐 해외</div><div class='info-card-value'>{selected['gl']}</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
