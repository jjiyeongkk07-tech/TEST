import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. 페이지 설정
st.set_page_config(page_title="글로벌 SCM 분석", page_icon="🌍", layout="wide")

# 2. 고급 CSS 주입
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
html, body, [class*='css'] { font-family: 'Noto Sans KR', sans-serif !important; }

/* 배경 및 기본 레이아웃 */
.stApp { background-color: #f1f5f9; }
.block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }
header { visibility: hidden; } footer { visibility: hidden; }

/* 메인 타이틀 배너 */
.dashboard-header { 
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); 
    padding: 30px 40px; border-radius: 16px; margin-bottom: 30px; 
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15); color: white;
    position: relative; overflow: hidden;
}
.dashboard-header::after {
    content: ''; position: absolute; top: -50%; right: -10%;
    width: 300px; height: 300px; background: radial-gradient(circle, rgba(99,102,241,0.2) 0%, transparent 70%);
    border-radius: 50%;
}
.dashboard-header h1 { margin: 0; font-size: 32px; font-weight: 900; color: #ffffff; letter-spacing: -0.5px; position: relative; z-index: 1;}

/* 정보 카드 */
.info-card { 
    background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; 
    padding: 24px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); 
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); border-top: 4px solid #3b82f6;
}
.info-card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
.info-card-title { font-size: 14px; color: #64748b; font-weight: 800; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
.info-card-value { font-size: 18px; color: #1e293b; font-weight: 700; line-height: 1.5; }

/* 제품 카드 */
.product-card { 
    background: linear-gradient(to bottom, #ffffff, #f8fafc); border: 1px solid #e2e8f0; 
    border-radius: 16px; padding: 30px 20px; text-align: center; height: 100%; 
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); transition: all 0.3s;
}
.product-card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #cbd5e1; }
.product-emoji { font-size: 64px; line-height: 1; margin-bottom: 15px; filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.1)); }
.product-title { font-size: 18px; font-weight: 800; color: #0f172a; }

/* 섹션 타이틀 */
.section-title { 
    font-size: 20px; font-weight: 900; color: #0f172a; margin-top: 45px; margin-bottom: 20px; 
    display: flex; align-items: center; gap: 10px;
}
.section-title::before { content: ''; display: block; width: 6px; height: 24px; background-color: #3b82f6; border-radius: 3px; }

/* 기업 개요 박스 */
.desc-box {
    background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 25px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-size: 17px; color: #334155; line-height: 1.8; font-weight: 500;
}

/* 사이드바 스타일링 */
[data-testid='stSidebar'] { background-color: #ffffff; border-right: 1px solid #e2e8f0; box-shadow: 2px 0 10px rgba(0,0,0,0.02); }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. 헤더 (요청하신 최상단 제목 반영)
st.markdown("<div class='dashboard-header'><h1>🌍 글로벌 SCM 및 파트너사 인프라 분석</h1></div>", unsafe_allow_html=True)

# 4. 데이터 (A~G 업체)
suppliers = [
    {
        "name": "A업체", "industry": "PCB 제조",
        "hq": "서울 서초구", "kr": "천안 공장, 구미 R&D센터", "gl": "베트남 하노이 공장, 미국 산호세 영업소",
        "desc": "국내 천안 및 구미에서 핵심 R&D 및 초기 양산을 진행하며, 대량 생산은 베트남 하노이 공장에서 담당하고 있습니다. 북미 주요 고객사 대응을 위해 미국 산호세에 직영 영업소를 운영 중입니다.",
        "products": [{"name": "서버용 PCB", "img": "🖲️"}, {"name": "통신 컨트롤러", "img": "🔌"}, {"name": "고성능 칩셋", "img": "💾"}],
        "locations": [
            {"name": "본사 (서울)", "lat": 37.4836, "lon": 127.0326, "type": "hq", "color": [220, 38, 38, 220]}, # Red
            {"name": "천안 공장", "lat": 36.8151, "lon": 127.1138, "type": "kr", "color": [37, 99, 235, 220]},   # Blue
            {"name": "구미 R&D", "lat": 36.1194, "lon": 128.3444, "type": "kr", "color": [37, 99, 235, 220]},
            {"name": "하노이 공장", "lat": 21.0285, "lon": 105.8542, "type": "gl", "color": [16, 185, 129, 220]}, # Green
            {"name": "산호세 영업소", "lat": 37.3382, "lon": -121.8863, "type": "gl", "color": [16, 185, 129, 220]}
        ]
    },
    {
        "name": "B업체", "industry": "정밀 가공",
        "hq": "부산 사하구", "kr": "창원 공장", "gl": "중국 칭다오 공장, 미국 텍사스 법인",
        "desc": "부산 본사를 중심으로 창원과 중국 칭다오에서 주요 장비 부품을 가공하고 있습니다. 최근 북미 IRA 법안 대응 및 직납 체계 구축을 위해 미국 텍사스에 조립 법인을 신설하였습니다.",
        "products": [{"name": "정밀 모터", "img": "⚙️"}, {"name": "로봇 암", "img": "🤖"}],
        "locations": [
            {"name": "본사 (부산)", "lat": 35.1044, "lon": 128.9748, "type": "hq", "color": [220, 38, 38, 220]},
            {"name": "창원 공장", "lat": 35.2279, "lon": 128.6811, "type": "kr", "color": [37, 99, 235, 220]},
            {"name": "칭다오 공장", "lat": 36.0671, "lon": 120.3826, "type": "gl", "color": [16, 185, 129, 220]},
            {"name": "텍사스 법인", "lat": 31.9685, "lon": -99.9018, "type": "gl", "color": [16, 185, 129, 220]}
        ]
    },
    {
        "name": "C업체", "industry": "화학/소재",
        "hq": "인천 남동구", "kr": "울산 공장, 여수 공장", "gl": "해당 없음",
        "desc": "해외 지사는 없으나, 국내 핵심 화학 단지인 울산과 여수에 대규모 생산 플랜트를 운영하여 매우 안정적인 내수 공급망을 확보하고 있는 건실한 기업입니다.",
        "products": [{"name": "합성수지", "img": "🧪"}, {"name": "특수 코팅액", "img": "💧"}, {"name": "산업용 접착제", "img": "🍯"}],
        "locations": [
            {"name": "본사 (인천)", "lat": 37.4473, "lon": 126.7315, "type": "hq", "color": [220, 38, 38, 220]},
            {"name": "울산 공장", "lat": 35.5383, "lon": 129.3113, "type": "kr", "color": [37, 99, 235, 220]},
            {"name": "여수 공장", "lat": 34.7603, "lon": 127.6622, "type": "kr", "color": [37, 99, 235, 220]}
        ]
    },
    {
        "name": "D업체", "industry": "2차전지 소재",
        "hq": "경북 포항시", "kr": "포항 1, 2공장", "gl": "폴란드 브로츠와프 법인, 미국 미시간 법인",
        "desc": "글로벌 전기차 배터리 수요 증가에 대응하기 위해 포항에 대규모 양극재 라인을 증설하였으며, 유럽(폴란드)과 북미(미시간)에 핵심 생산 거점을 구축해 현지 조달 역량을 극대화했습니다.",
        "products": [{"name": "하이니켈 양극재", "img": "🔋"}, {"name": "실리콘 음극재", "img": "⚡"}, {"name": "전해액 첨가제", "img": "🧪"}],
        "locations": [
            {"name": "본사 및 공장 (포항)", "lat": 36.0190, "lon": 129.3435, "type": "hq", "color": [220, 38, 38, 220]},
            {"name": "폴란드 법인", "lat": 51.1079, "lon": 17.0385, "type": "gl", "color": [16, 185, 129, 220]},
            {"name": "미국 미시간 법인", "lat": 43.3266, "lon": -84.5361, "type": "gl", "color": [16, 185, 129, 220]}
        ]
    },
    {
        "name": "E업체", "industry": "반도체 장비",
        "hq": "경기 화성시", "kr": "동탄 R&D센터, 평택 R&D센터", "gl": "대만 신주 연락사무소, 미국 실리콘밸리 지사",
        "desc": "국내 주요 반도체 제조사와의 끈끈한 협력을 바탕으로 화성과 평택에 차세대 장비 R&D 센터를 운영 중입니다. TSMC 및 인텔과의 기술 교류를 위해 대만과 미국 지사를 최근 오픈했습니다.",
        "products": [{"name": "CVD 증착장비", "img": "🏭"}, {"name": "웨이퍼 세정기", "img": "🧽"}],
        "locations": [
            {"name": "본사 (화성)", "lat": 37.1995, "lon": 126.8315, "type": "hq", "color": [220, 38, 38, 220]},
            {"name": "평택 R&D", "lat": 36.9921, "lon": 127.1129, "type": "kr", "color": [37, 99, 235, 220]},
            {"name": "대만 신주 사무소", "lat": 24.8138, "lon": 120.9675, "type": "gl", "color": [16, 185, 129, 220]},
            {"name": "실리콘밸리 지사", "lat": 37.3875, "lon": -122.0575, "type": "gl", "color": [16, 185, 129, 220]}
        ]
    },
    {
        "name": "F업체", "industry": "디스플레이 부품",
        "hq": "경기 파주시", "kr": "파주 LCD/OLED 라인", "gl": "베트남 하이퐁 조립공장",
        "desc": "파주 본사에서 고부가가치 하이엔드 OLED 패널 부품을 생산하고, 노동 집약적인 후공정 및 모듈 조립은 베트남 하이퐁 공장으로 이관하여 원가 경쟁력을 크게 확보하고 있습니다.",
        "products": [{"name": "초박형 글라스", "img": "📱"}, {"name": "터치 IC 센서", "img": "👆"}],
        "locations": [
            {"name": "본사 (파주)", "lat": 37.7600, "lon": 126.7800, "type": "hq", "color": [220, 38, 38, 220]},
            {"name": "하이퐁 공장", "lat": 20.8449, "lon": 106.6881, "type": "gl", "color": [16, 185, 129, 220]}
        ]
    },
    {
        "name": "G업체", "industry": "전장 부품",
        "hq": "경기 수원시", "kr": "화성 주행시험장", "gl": "멕시코 몬테레이 공장, 헝가리 부다페스트 공장",
        "desc": "수원 본사 및 화성 주행시험장에서 자율주행 모듈을 개발합니다. 북미 3대 완성차 업체 납품을 위해 멕시코에, 유럽 자동차 메이커 대응을 위해 헝가리에 각각 대형 공장을 가동하고 있습니다.",
        "products": [{"name": "자율주행 라이다", "img": "📡"}, {"name": "차량용 카메라", "img": "📷"}, {"name": "인포테인먼트", "img": "🖥️"}],
        "locations": [
            {"name": "본사 (수원)", "lat": 37.2636, "lon": 127.0286, "type": "hq", "color": [220, 38, 38, 220]},
            {"name": "화성 시험장", "lat": 37.2100, "lon": 126.8100, "type": "kr", "color": [37, 99, 235, 220]},
            {"name": "멕시코 몬테레이", "lat": 25.6866, "lon": -100.3161, "type": "gl", "color": [16, 185, 129, 220]},
            {"name": "헝가리 부다페스트", "lat": 47.4979, "lon": 19.0402, "type": "gl", "color": [16, 185, 129, 220]}
        ]
    }
]

# 5. 사이드바 (업종 필터 및 검색)
with st.sidebar:
    st.markdown("<h3 style='color:#0f172a; margin-bottom:20px; font-weight:900;'>🏢 파트너사 검색</h3>", unsafe_allow_html=True)
    
    industry_list = ["전체"] + sorted(list(set(s["industry"] for s in suppliers)))
    selected_industry = st.selectbox("🏷️ 업종 필터", industry_list)
    search_term = st.text_input("🔍 업체명 검색", placeholder="예: A업체").strip()

    filtered = suppliers
    if selected_industry != "전체":
        filtered = [s for s in filtered if s["industry"] == selected_industry]
    
    if search_term:
        filtered = [s for s in filtered if search_term.lower() in s["name"].lower()]

    if not filtered:
        st.warning("조건에 맞는 업체가 없습니다.")
        filtered = suppliers

    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
    selected_name = st.radio("📊 상세 분석할 업체 선택", [s["name"] for s in filtered])

selected = next((s for s in filtered if s["name"] == selected_name), None)

# 6. 메인 화면 출력
if selected:
    st.markdown(
        f"<div style='margin-bottom:20px;'><h2 style='margin:0; color:#0f172a; font-weight:900; font-size:40px;'>{selected['name']}</h2>"
        f"<p style='margin:8px 0 0 0; color:#475569; font-size:18px; font-weight:500;'>업종 : <span style='color:#3b82f6; font-weight:800;'>{selected['industry']}</span></p></div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='section-title'>기업 개요</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='desc-box'>{selected['desc']}</div>", unsafe_allow_html=True)

    # --- 🗺️ 글로벌 거점 인프라 (지도 개선: 명확한 2D 마커 적용) ---
    st.markdown("<div class='section-title'>주요 거점 네트워크</div>", unsafe_allow_html=True)
    
    map_col, text_col = st.columns([1.5, 1])

    with map_col:
        df_loc = pd.DataFrame(selected["locations"])
        
        # 좌표 분포도에 따른 동적 줌 레벨 최적화
        lon_range = df_loc['lon'].max() - df_loc['lon'].min()
        if lon_range > 150:    # 글로벌 (미국, 유럽 포함)
            zoom_lvl = 1.0
        elif lon_range > 50:   # 아시아 리전 (동남아 포함)
            zoom_lvl = 2.5
        else:                  # 국내 전용
            zoom_lvl = 6.0
            
        view_state = pdk.ViewState(
            latitude=df_loc['lat'].mean(), 
            longitude=df_loc['lon'].mean(), 
            zoom=zoom_lvl, 
            pitch=0  # 평면(2D) 뷰로 설정하여 위치 왜곡 방지 및 명확성 극대화
        )
        
        # 3D 기둥(ColumnLayer)을 제거하고, 세련된 원형 점(ScatterplotLayer)으로 교체
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_loc,
            get_position='[lon, lat]',
            get_fill_color='color',
            get_line_color=[255, 255, 255], # 모든 마커에 흰색 테두리를 줘서 구분을 명확하게 함
            stroked=True,
            line_width_min_pixels=2,
            radius_scale=1,
            radius_min_pixels=8,  # 지도를 아무리 축소해도 최소 크기 유지 (잘 보임)
            radius_max_pixels=20, # 지도를 아무리 확대해도 거대해지지 않음
            pickable=True,
        )
        
        with st.container(border=True):
            st.pydeck_chart(pdk.Deck(
                map_style="light",
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "{name}"} 
            ))

    with text_col:
        st.markdown(f"<div class='info-card' style='border-top-color:#dc2626;'><div class='info-card-title'>🏢 Headquarter (본사)</div><div class='info-card-value'>{selected['hq']}</div></div>", unsafe_allow_html=True)
        st.write("") 
        st.markdown(f"<div class='info-card' style='border-top-color:#2563eb;'><div class='info-card-title'>🇰🇷 Domestic (국내 공장/지사)</div><div class='info-card-value'>{selected['kr']}</div></div>", unsafe_allow_html=True)
        st.write("") 
        
        gl_color = "#10b981" if selected['gl'] != "해당 없음" else "#94a3b8"
        st.markdown(f"<div class='info-card' style='border-top-color:{gl_color};'><div class='info-card-title'>🌐 Global (해외 법인/지사)</div><div class='info-card-value'>{selected['gl']}</div></div>", unsafe_allow_html=True)

    # --- 📦 생산 품목 ---
    st.markdown("<div class='section-title'>핵심 생산 품목</div>", unsafe_allow_html=True)
    cols = st.columns(len(selected['products']))
    for idx, p in enumerate(selected['products']):
        cols[idx].markdown(
            f"<div class='product-card'><div class='product-emoji'>{p['img']}</div><div class='product-title'>{p['name']}</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
