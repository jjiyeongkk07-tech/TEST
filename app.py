import streamlit as st
import pandas as pd
import pydeck as pdk

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(page_title="글로벌 SCM 분석 대시보드", page_icon="🏢", layout="wide")

# ==========================================
# 2. 고급 CSS 주입 (Corporate & Clean Style)
# ==========================================
css = """
<style>
/* 폰트: Pretendard 적용 */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
html, body, [class*='css'], [class*='st-'] { 
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif !important; 
}

/* 기본 배경 및 레이아웃 */
.stApp { background-color: #F8FAFC; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1440px; }
header, footer { visibility: hidden; }

/* 메인 타이틀 바 */
.main-header {
    background: #0F172A;
    padding: 24px 32px;
    border-radius: 8px;
    margin-bottom: 32px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.main-header h1 { 
    margin: 0; color: #FFFFFF; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;
}
.main-header .badge {
    background: #3B82F6; color: white; padding: 6px 12px; border-radius: 4px; font-size: 14px; font-weight: 600;
}

/* 기업 개요 헤더 영역 */
.company-header {
    display: flex; align-items: baseline; gap: 16px; margin-bottom: 16px;
}
.company-name {
    font-size: 36px; font-weight: 800; color: #111827; margin: 0; letter-spacing: -1px;
}
.company-industry {
    background-color: #EFF6FF; color: #1D4ED8; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 15px; border: 1px solid #BFDBFE;
}

/* 기업 설명 박스 */
.desc-box {
    background-color: #FFFFFF; border-left: 4px solid #3B82F6; border-radius: 0 8px 8px 0; 
    padding: 20px 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-size: 16px; 
    color: #4B5563; line-height: 1.6; font-weight: 500; margin-bottom: 32px;
}

/* 섹션 타이틀 */
.section-title { 
    font-size: 20px; font-weight: 700; color: #111827; margin: 40px 0 20px 0; 
    padding-bottom: 10px; border-bottom: 2px solid #E2E8F0;
}

/* SCM Flow 스테퍼 (Stepper) */
.stepper-container {
    background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 40px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 20px;
}
.stepper {
    display: flex; justify-content: space-between; position: relative; max-width: 1000px; margin: 0 auto;
}
.stepper::before {
    content: ''; position: absolute; top: 24px; left: 10%; right: 10%; height: 2px; background: #CBD5E1; z-index: 1;
}
.step {
    position: relative; z-index: 2; text-align: center; flex: 1; padding: 0 10px;
}
.step-icon {
    width: 48px; height: 48px; border-radius: 50%; background: #3B82F6; color: white;
    display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold;
    margin: 0 auto 16px auto; border: 4px solid #FFFFFF; box-shadow: 0 0 0 1px #E2E8F0;
}
.step-stage { font-size: 14px; font-weight: 700; color: #111827; margin-bottom: 4px; }
.step-loc { font-size: 13px; font-weight: 600; color: #64748b; margin-bottom: 8px; }
.step-desc { font-size: 12px; color: #475569; line-height: 1.4; word-break: keep-all; }

/* 데이터 카드 (인프라 현황) */
.data-card { 
    background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; 
    padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); 
}
.data-card-header { 
    display: flex; align-items: center; gap: 8px; font-size: 14px; color: #64748b; font-weight: 700; margin-bottom: 8px; text-transform: uppercase; 
}
.data-card-value { font-size: 16px; color: #0F172A; font-weight: 600; line-height: 1.5; }

/* 제품 태그 */
.product-tag-container { display: flex; flex-wrap: wrap; gap: 12px; }
.product-tag {
    background: #F8FAFC; border: 1px solid #CBD5E1; padding: 12px 20px; border-radius: 8px;
    display: flex; align-items: center; gap: 10px; font-size: 15px; font-weight: 600; color: #334155;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

/* 사이드바 스타일링 */
[data-testid='stSidebar'] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
.stSelectbox label, .stTextInput label, .stRadio label { font-weight: 600 !important; color: #334155 !important; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ==========================================
# 3. 데이터 소스 (기존 데이터 유지)
# ==========================================
suppliers = [
    {
        "name": "A업체", "industry": "PCB", 
        "hq": "서울 서초구", "kr": "천안 공장, 구미 R&D센터", "gl": "베트남 하노이 공장, 미국 산호세 영업소",
        "desc": "국내 천안 및 구미에서 핵심 R&D 및 초기 양산을 진행하며, 대량 생산은 베트남 하노이 공장에서 담당하고 있습니다. 북미 주요 고객사 대응을 위해 미국 산호세에 직영 영업소를 운영 중입니다.",
        "chain": [
            {"stage": "원자재 소싱", "loc": "🇨🇳 중국 칭다오", "desc": "구리/수지 등 기초원료 조달"},
            {"stage": "R&D/초기양산", "loc": "🇰🇷 한국 천안·구미", "desc": "핵심 기술 설계 및 파일럿 양산"},
            {"stage": "대량 양산(조립)", "loc": "🇻🇳 베트남 하노이", "desc": "인건비 절감형 대규모 조립 라인"},
            {"stage": "최종 납품", "loc": "🇺🇸 미국 산호세", "desc": "북미 주요 IT 고객사 직납"}
        ],
        "products": [{"name": "PCB", "img": "🖲️"}, {"name": "원재료", "img": "🪨"}],
        "locations": [
            {"name": "본사 (서울)", "lat": 37.4836, "lon": 127.0326, "type": "hq", "color": [15, 23, 42, 200]}, # Slate
            {"name": "천안 공장", "lat": 36.8151, "lon": 127.1138, "type": "kr", "color": [37, 99, 235, 200]}, # Blue
            {"name": "구미 R&D", "lat": 36.1194, "lon": 128.3444, "type": "kr", "color": [37, 99, 235, 200]},
            {"name": "하노이 공장", "lat": 21.0285, "lon": 105.8542, "type": "gl", "color": [16, 185, 129, 200]}, # Green
            {"name": "산호세 영업소", "lat": 37.3382, "lon": -121.8863, "type": "gl", "color": [16, 185, 129, 200]}
        ]
    },
    {
        "name": "B업체", "industry": "가공(일반)",
        "hq": "부산 사하구", "kr": "창원 공장", "gl": "중국 칭다오 공장, 미국 텍사스 법인",
        "desc": "부산 본사를 중심으로 창원과 중국 칭다오에서 주요 장비 부품을 가공하고 있습니다. 최근 북미 IRA 법안 대응 및 직납 체계 구축을 위해 미국 텍사스에 조립 법인을 신설하였습니다.",
        "chain": [
            {"stage": "소재/기초가공", "loc": "🇰🇷 한국 부산·창원", "desc": "고정밀 기초 부품 가공"},
            {"stage": "서브 부품가공", "loc": "🇨🇳 중국 칭다오", "desc": "범용 부품 위탁 생산"},
            {"stage": "최종 조립", "loc": "🇺🇸 미국 텍사스", "desc": "IRA 대응 현지 조립 라인 가동"},
            {"stage": "고객 납품", "loc": "🌎 북미 전역", "desc": "장비사 1차 벤더 납품"}
        ],
        "products": [{"name": "SHAFT", "img": "⚙️"}, {"name": "Bearing", "img": "🔄"}, {"name": "GEAR", "img": "🛞"}],
        "locations": [
            {"name": "본사 (부산)", "lat": 35.1044, "lon": 128.9748, "type": "hq", "color": [15, 23, 42, 200]},
            {"name": "창원 공장", "lat": 35.2279, "lon": 128.6811, "type": "kr", "color": [37, 99, 235, 200]},
            {"name": "칭다오 공장", "lat": 36.0671, "lon": 120.3826, "type": "gl", "color": [16, 185, 129, 200]},
            {"name": "텍사스 법인", "lat": 31.9685, "lon": -99.9018, "type": "gl", "color": [16, 185, 129, 200]}
        ]
    },
    {
        "name": "C업체", "industry": "에폭시",
        "hq": "인천 남동구", "kr": "울산 공장, 여수 공장", "gl": "해당 없음",
        "desc": "해외 지사는 없으나, 국내 핵심 화학 단지인 울산과 여수에 대규모 생산 플랜트를 운영하여 매우 안정적인 내수 공급망을 확보하고 있는 건실한 기업입니다.",
        "chain": [
            {"stage": "원유/원료 수입", "loc": "🛢️ 중동 / 호주", "desc": "원유 및 기초 화합물 수입"},
            {"stage": "정제 및 합성", "loc": "🇰🇷 한국 울산·여수", "desc": "대규모 석유화학 플랜트 가동"},
            {"stage": "품질 검수", "loc": "🇰🇷 인천 본사", "desc": "최종 패키징 및 R&D 검수"},
            {"stage": "내수 납품", "loc": "🚚 국내 전역", "desc": "국내 주요 대기업 납품"}
        ],
        "products": [{"name": "RUBBER", "img": "🧤"}],
        "locations": [
            {"name": "본사 (인천)", "lat": 37.4473, "lon": 126.7315, "type": "hq", "color": [15, 23, 42, 200]},
            {"name": "울산 공장", "lat": 35.5383, "lon": 129.3113, "type": "kr", "color": [37, 99, 235, 200]},
            {"name": "여수 공장", "lat": 34.7603, "lon": 127.6622, "type": "kr", "color": [37, 99, 235, 200]}
        ]
    },
    {
        "name": "D업체", "industry": "원재료(철판)",
        "hq": "경북 포항시", "kr": "포항 1, 2공장", "gl": "폴란드 브로츠와프 법인, 미국 미시간 법인",
        "desc": "글로벌 전기차 배터리 수요 증가에 대응하기 위해 포항에 대규모 양극재 라인을 증설하였으며, 유럽(폴란드)과 북미(미시간)에 핵심 생산 거점을 구축해 현지 조달 역량을 극대화했습니다.",
        "chain": [
            {"stage": "핵심 광물 소싱", "loc": "🇦🇺 남미 / 호주", "desc": "리튬, 니켈 원광석 직계약"},
            {"stage": "전구체/양극재 생산", "loc": "🇰🇷 한국 포항", "desc": "글로벌 최대 규모 양극재 양산"},
            {"stage": "현지 조달", "loc": "🇵🇱 폴란드 / 🇺🇸 미국", "desc": "유럽/북미 권역별 물류기지"},
            {"stage": "고객사 직납", "loc": "🔋 글로벌 셀메이커", "desc": "완성차 및 배터리 3사 납품"}
        ],
        "products": [{"name": "원재료", "img": "🪨"}],
        "locations": [
            {"name": "본사 및 공장 (포항)", "lat": 36.0190, "lon": 129.3435, "type": "hq", "color": [15, 23, 42, 200]},
            {"name": "폴란드 법인", "lat": 51.1079, "lon": 17.0385, "type": "gl", "color": [16, 185, 129, 200]},
            {"name": "미국 미시간 법인", "lat": 43.3266, "lon": -84.5361, "type": "gl", "color": [16, 185, 129, 200]}
        ]
    },
    {
        "name": "E업체", "industry": "임가공(조립)",
        "hq": "경기 화성시", "kr": "동탄 R&D센터, 평택 공장", "gl": "대만 신주 연락사무소, 미국 실리콘밸리 지사",
        "desc": "국내 주요 반도체 제조사와의 끈끈한 협력을 바탕으로 화성과 평택에 차세대 장비 R&D 센터를 운영 중입니다. TSMC 및 인텔과의 기술 교류를 위해 대만과 미국 지사를 최근 오픈했습니다.",
        "chain": [
            {"stage": "부품 소싱/설계", "loc": "🇰🇷 화성 동탄", "desc": "코어 부품 설계 및 글로벌 소싱"},
            {"stage": "장비 제조/셋업", "loc": "🇰🇷 평택 공장", "desc": "클린룸 내 장비 셋업 및 테스트"},
            {"stage": "해외 CS 지원", "loc": "🇹🇼 대만 / 🇺🇸 미국", "desc": "고객사 인접 현지 기술 지원"},
            {"stage": "고객 인도", "loc": "💻 글로벌 파운드리", "desc": "TSMC, Intel 등 메인 팹 반입"}
        ],
        "products": [{"name": "TERMINAL", "img": "🔌"}, {"name": "MAGNET WIRE", "img": "🧵"}],
        "locations": [
            {"name": "본사 (화성)", "lat": 37.1995, "lon": 126.8315, "type": "hq", "color": [15, 23, 42, 200]},
            {"name": "평택 R&D", "lat": 36.9921, "lon": 127.1129, "type": "kr", "color": [37, 99, 235, 200]},
            {"name": "대만 신주 사무소", "lat": 24.8138, "lon": 120.9675, "type": "gl", "color": [16, 185, 129, 200]},
            {"name": "실리콘밸리 지사", "lat": 37.3875, "lon": -122.0575, "type": "gl", "color": [16, 185, 129, 200]}
        ]
    },
    {
        "name": "F업체", "industry": "사출",
        "hq": "경기 파주시", "kr": "파주 LCD/OLED 라인", "gl": "베트남 하이퐁 조립공장",
        "desc": "파주 본사에서 고부가가치 하이엔드 OLED 패널 부품을 생산하고, 노동 집약적인 후공정 및 모듈 조립은 베트남 하이퐁 공장으로 이관하여 원가 경쟁력을 크게 확보하고 있습니다.",
        "chain": [
            {"stage": "기초소재 수입", "loc": "🇯🇵 일본 / 🇹🇼 대만", "desc": "유리 기판 및 코팅 소재 수입"},
            {"stage": "하이엔드 가공", "loc": "🇰🇷 한국 파주", "desc": "고도화된 OLED 패널 코어 가공"},
            {"stage": "모듈 조립(후공정)", "loc": "🇻🇳 베트남 하이퐁", "desc": "원가 절감형 노동집약 후공정"},
            {"stage": "최종 납품", "loc": "📱 스마트폰 제조사", "desc": "글로벌 모바일 제조 공장 납품"}
        ],
        "products": [{"name": "MAGNET", "img": "🧲"}, {"name": "CORE", "img": "🔩"}],
        "locations": [
            {"name": "본사 (파주)", "lat": 37.7600, "lon": 126.7800, "type": "hq", "color": [15, 23, 42, 200]},
            {"name": "하이퐁 공장", "lat": 20.8449, "lon": 106.6881, "type": "gl", "color": [16, 185, 129, 200]}
        ]
    },
    {
        "name": "G업체", "industry": "PRESS(CASE)",
        "hq": "경기 수원시", "kr": "화성 주행시험장", "gl": "멕시코 몬테레이 공장, 헝가리 부다페스트 공장",
        "desc": "수원 본사 및 화성 주행시험장에서 자율주행 모듈을 개발합니다. 북미 3대 완성차 업체 납품을 위해 멕시코에, 유럽 자동차 메이커 대응을 위해 헝가리에 각각 대형 공장을 가동하고 있습니다.",
        "chain": [
            {"stage": "알고리즘 R&D", "loc": "🇰🇷 한국 수원", "desc": "자율주행 코어 소프트웨어 개발"},
            {"stage": "글로벌 소싱", "loc": "🌐 글로벌 전역", "desc": "렌즈, 칩셋 등 최적 단가 소싱"},
            {"stage": "권역별 현지 조립", "loc": "🇲🇽 멕시코 / 🇭🇺 헝가리", "desc": "미주/유럽 타겟 현지 공장 가동"},
            {"stage": "완성차 납품", "loc": "🚗 주요 자동차 메이커", "desc": "글로벌 Top 5 완성차 라인 납품"}
        ],
        "products": [{"name": "CASE", "img": "📦"}, {"name": "BRUSH", "img": "🖌️"}],
        "locations": [
            {"name": "본사 (수원)", "lat": 37.2636, "lon": 127.0286, "type": "hq", "color": [15, 23, 42, 200]},
            {"name": "화성 시험장", "lat": 37.2100, "lon": 126.8100, "type": "kr", "color": [37, 99, 235, 200]},
            {"name": "멕시코 몬테레이", "lat": 25.6866, "lon": -100.3161, "type": "gl", "color": [16, 185, 129, 200]},
            {"name": "헝가리 부다페스트", "lat": 47.4979, "lon": 19.0402, "type": "gl", "color": [16, 185, 129, 200]}
        ]
    }
]

# ==========================================
# 4. 헤더 렌더링
# ==========================================
st.markdown("""
<div class='main-header'>
    <h1>Global SCM Intelligence</h1>
    <span class='badge'>Supply Chain Analytics</span>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 사이드바 (필터)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#0F172A; font-weight:700; margin-bottom: 20px;'>🔍 검색 및 필터</h3>", unsafe_allow_html=True)
    
    # 5-1. 업종 필터 
    all_industries = [
        "PCB", "PRESS(CASE)", "PRESS(CORE)", "PRESS(TERMINAL)", "RUBBER",
        "가공(COMM;Y)", "가공(DIECASTING)", "가공(MAGNET WIRE)", "가공(SHAFT)", "가공(일반)",
        "단조", "라벨", "베어링", "사출", "소결(BRUSH)", "소결(GEAR)", "소결(MAGNET)", 
        "에폭시", "원재료(SHAFT)", "원재료(사출)", "원재료(철판)", "원재료(황동)", 
        "일반구매", "임가공(조립)", "포장재"
    ]
    
    selected_industry = st.selectbox("업종 선택", ["전체"] + all_industries)
    
    # 5-2. 지역 필터
    selected_region = st.selectbox("주요 권역", ["전체", "국내", "중국", "인도", "유럽", "베트남", "미국"])
    
    st.divider()

    # 5-3. 검색어 입력
    search_term = st.text_input("기업명 직접 검색", placeholder="예: A업체").strip()

    # 필터 적용 로직
    filtered = suppliers
    if selected_industry != "전체":
        filtered = [s for s in filtered if s["industry"] == selected_industry]
        
    if selected_region == "국내":
        filtered = [s for s in filtered if s["gl"] == "해당 없음"]
    elif selected_region == "유럽":
        filtered = [s for s in filtered if any(x in s["gl"] for x in ["유럽", "폴란드", "헝가리"])]
    elif selected_region != "전체":
        filtered = [s for s in filtered if selected_region in s["gl"]]

    if search_term:
        filtered = [s for s in filtered if search_term.lower() in s["name"].lower()]

    st.divider()

    # 결과 리스트 라디오 버튼
    if not filtered:
        st.warning("조건에 맞는 파트너사가 없습니다.")
        selected = None
    else:
        st.markdown("<p style='font-size:14px; font-weight:600; color:#64748b; margin-bottom:10px;'>📋 검색 결과 ({}건)</p>".format(len(filtered)), unsafe_allow_html=True)
        selected_name = st.radio("상세 분석할 기업을 선택하세요", [s["name"] for s in filtered], label_visibility="collapsed")
        selected = next((s for s in filtered if s["name"] == selected_name), None)

# ==========================================
# 6. 메인 콘텐츠 영역
# ==========================================
if selected:
    # --- [섹션 1] 기업 개요 ---
    st.markdown(f"""
        <div class='company-header'>
            <h2 class='company-name'>{selected['name']}</h2>
            <span class='company-industry'>{selected['industry']}</span>
        </div>
        <div class='desc-box'>{selected['desc']}</div>
    """, unsafe_allow_html=True)

    # --- [섹션 2] 글로벌 밸류체인 Flow ---
    st.markdown("<div class='section-title'>Value Chain Process</div>", unsafe_allow_html=True)
    
    chain_html = "<div class='stepper-container'><div class='stepper'>"
    for i, step in enumerate(selected["chain"]):
        chain_html += f"""
        <div class='step'>
            <div class='step-icon'>{i+1}</div>
            <div class='step-stage'>{step['stage']}</div>
            <div class='step-loc'>{step['loc']}</div>
            <div class='step-desc'>{step['desc']}</div>
        </div>
        """
    chain_html += "</div></div>"
    st.markdown(chain_html, unsafe_allow_html=True)

    # --- [섹션 3] 인프라 및 생산품목 (2단 레이아웃) ---
    st.markdown("<div class='section-title'>Global Infrastructure & Assets</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.6, 1])

    # 왼쪽: 지도 데이터
    with col1:
        df_loc = pd.DataFrame(selected["locations"])
        lon_range = df_loc['lon'].max() - df_loc['lon'].min()
        zoom_lvl = 1.0 if lon_range > 150 else (2.5 if lon_range > 50 else 6.0)
            
        view_state = pdk.ViewState(
            latitude=df_loc['lat'].mean(), longitude=df_loc['lon'].mean(), zoom=zoom_lvl, pitch=0
        )
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_loc,
            get_position='[lon, lat]',
            get_fill_color='color',
            get_line_color=[255, 255, 255], 
            stroked=True,
            line_width_min_pixels=2,
            radius_scale=1,
            radius_min_pixels=8,  
            radius_max_pixels=20, 
            pickable=True,
        )
        
        with st.container(border=True):
            # 지도 스타일을 'road'로 변경하여 비즈니스용에 적합한 깔끔한 UI 제공
            st.pydeck_chart(pdk.Deck(
                map_style="road",
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "{name}"} 
            ))

    # 오른쪽: 거점 텍스트 데이터 & 핵심 품목
    with col2:
        # 거점 인프라 현황
        st.markdown(f"""
            <div class='data-card' style='border-left: 4px solid #0F172A;'>
                <div class='data-card-header'>🏢 Headquarter (본사)</div>
                <div class='data-card-value'>{selected['hq']}</div>
            </div>
            <div class='data-card' style='border-left: 4px solid #3B82F6;'>
                <div class='data-card-header'>🇰🇷 Domestic (국내 인프라)</div>
                <div class='data-card-value'>{selected['kr']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        gl_border = "#10B981" if selected['gl'] != "해당 없음" else "#CBD5E1"
        st.markdown(f"""
            <div class='data-card' style='border-left: 4px solid {gl_border}; margin-bottom:32px;'>
                <div class='data-card-header'>🌐 Global (해외 거점)</div>
                <div class='data-card-value'>{selected['gl']}</div>
            </div>
        """, unsafe_allow_html=True)

        # 핵심 생산 품목 태그형 UI
        st.markdown("<p style='font-size:16px; font-weight:700; color:#111827; margin-bottom:12px;'>핵심 생산 품목</p>", unsafe_allow_html=True)
        products_html = "<div class='product-tag-container'>"
        for p in selected['products']:
            products_html += f"<div class='product-tag'><span>{p['img']}</span> {p['name']}</div>"
        products_html += "</div>"
        st.markdown(products_html, unsafe_allow_html=True)

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
