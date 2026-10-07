import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. 페이지 설정
st.set_page_config(page_title="협력사 글로벌 현황", page_icon="🌍", layout="wide")

# 2. 고급 CSS 주입 (Noto Sans 폰트, 그림자, 그라데이션, 애니메이션 추가)
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
html, body, [class*='css'] { font-family: 'Noto Sans KR', sans-serif !important; }

/* 배경 및 기본 레이아웃 */
.stApp { background-color: #f1f5f9; }
.block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }
header { visibility: hidden; } footer { visibility: hidden; }

/* 메인 타이틀 배너 (고급스러운 다크 블루 & 퍼플 그라데이션) */
.dashboard-header { 
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); 
    padding: 30px 40px; border-radius: 16px; margin-bottom: 30px; 
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15); color: white;
    position: relative; overflow: hidden;
}
/* 타이틀 배경 장식 요소 */
.dashboard-header::after {
    content: ''; position: absolute; top: -50%; right: -10%;
    width: 300px; height: 300px; background: radial-gradient(circle, rgba(99,102,241,0.2) 0%, transparent 70%);
    border-radius: 50%;
}
.dashboard-header h1 { margin: 0; font-size: 32px; font-weight: 900; color: #ffffff; letter-spacing: -0.5px; position: relative; z-index: 1;}

/* 정보 카드 (거점 텍스트) */
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

/* 섹션 타이틀 (디자인 강화) */
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

# 3. 헤더 (요청하신 문구 2개 삭제)
st.markdown(
    "<div class='dashboard-header'><h1>🌍 협력사별 글로벌 현황</h1></div>", 
    unsafe_allow_html=True
)

# 4. 데이터 (지도에 표시하기 위해 위경도 데이터 추가)
# 실제 보고용이므로, 각 본사/지사의 대략적인 좌표(lat, lon)와 타입(본사, 공장 등)을 정의합니다.
suppliers = [
    {
        "name": "A업체", "industry": "PCB 제조",
        "hq": "서울 서초구", "kr": "천안 공장, 구미 R&D센터", "gl": "베트남 하노이 공장, 미국 산호세 영업소",
        "desc": "국내 천안 및 구미에서 핵심 R&D 및 초기 양산을 진행하며, 대량 생산은 베트남 하노이 공장에서 담당하고 있습니다. 북미 주요 고객사 대응을 위해 미국 산호세에 직영 영업소를 운영 중입니다.",
        "products": [{"name": "서버용 PCB", "img": "🖲️"}, {"name": "통신 컨트롤러", "img": "🔌"}, {"name": "고성능 칩셋", "img": "💾"}],
        "locations": [
            {"name": "본사 (서울)", "lat": 37.4836, "lon": 127.0326, "type": "hq", "color": [220, 38, 38, 200]}, # Red
            {"name": "천안 공장", "lat": 36.8151, "lon": 127.1138, "type": "kr", "color": [37, 99, 235, 200]},   # Blue
            {"name": "구미 R&D", "lat": 36.1194, "lon": 128.3444, "type": "kr", "color": [37, 99, 235, 200]},
            {"name": "하노이 공장", "lat": 21.0285, "lon": 105.8542, "type": "gl", "color": [16, 185, 129, 200]}, # Green
            {"name": "산호세 영업소", "lat": 37.3382, "lon": -121.8863, "type": "gl", "color": [16, 185, 129, 200]}
        ]
    },
    {
        "name": "B업체", "industry": "정밀 가공",
        "hq": "부산 사하구", "kr": "창원 공장", "gl": "중국 칭다오 공장, 미국 텍사스 법인",
        "desc": "부산 본사를 중심으로 창원과 중국 칭다오에서 주요 장비 부품을 가공하고 있습니다. 최근 북미 IRA 법안 대응 및 직납 체계 구축을 위해 미국 텍사스에 조립 법인을 신설하였습니다.",
        "products": [{"name": "정밀 모터", "img": "⚙️"}, {"name": "로봇 암", "img": "🤖"}],
        "locations": [
            {"name": "본사 (부산)", "lat": 35.1044, "lon": 128.9748, "type": "hq", "color": [220, 38, 38, 200]},
            {"name": "창원 공장", "lat": 35.2279, "lon": 128.6811, "type": "kr", "color": [37, 99, 235, 200]},
            {"name": "칭다오 공장", "lat": 36.0671, "lon": 120.3826, "type": "gl", "color": [16, 185, 129, 200]},
            {"name": "텍사스 법인", "lat": 31.9685, "lon": -99.9018, "type": "gl", "color": [16, 185, 129, 200]}
        ]
    },
    {
        "name": "C업체", "industry": "원재료 (사출/화학)",
        "hq": "인천 남동구", "kr": "울산 공장, 여수 공장", "gl": "해당 없음 (국내 집중)",
        "desc": "해외 지사는 없으나, 국내 핵심 화학 단지인 울산과 여수에 대규모 생산 플랜트를 운영하여 매우 안정적인 내수 공급망을 확보하고 있는 건실한 기업입니다.",
        "products": [{"name": "합성수지", "img": "🧪"}, {"name": "특수 코팅액", "img": "💧"}, {"name": "산업용 접착제", "img": "🍯"}],
        "locations": [
            {"name": "본사 (인천)", "lat": 37.4473, "lon": 126.7315, "type": "hq", "color": [220, 38, 38, 200]},
            {"name": "울산 공장", "lat": 35.5383, "lon": 129.3113, "type": "kr", "color": [37, 99, 235, 200]},
            {"name": "여수 공장", "lat": 34.7603, "lon": 127.6622, "type": "kr", "color": [37, 99, 235, 200]}
        ]
    }
]

# 5. 사이드바
with st.sidebar:
    st.markdown("<h3 style='color:#0f172a; margin-bottom:20px; font-weight:900;'>🏢 파트너사 목록</h3>", unsafe_allow_html=True)
    search_term = st.text_input("🔍 업체명 / 업종 검색", "").strip()

    filtered = [s for s in suppliers if search_term.lower() in s["name"].lower() or search_term.lower() in s["industry"].lower()]
    if not filtered: filtered = suppliers

    selected_name = st.radio("상세 분석할 업체 선택", [s["name"] for s in filtered])

selected = next(s for s in filtered if s["name"] == selected_name)

# 6. 메인 화면 출력
if selected:
    # --- 타이틀 및 개요 ---
    st.markdown(
        f"<div style='margin-bottom:20px;'><h2 style='margin:0; color:#0f172a; font-weight:900; font-size:40px;'>{selected['name']}</h2>"
        f"<p style='margin:8px 0 0 0; color:#475569; font-size:18px; font-weight:500;'>업종 : <span style='color:#3b82f6; font-weight:800;'>{selected['industry']}</span></p></div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='section-title'>기업 개요</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='desc-box'>{selected['desc']}</div>", unsafe_allow_html=True)

    # --- 🗺️ 글로벌 거점 인프라 (지도 + 텍스트 카드) ---
    st.markdown("<div class='section-title'>주요 거점 네트워크</div>", unsafe_allow_html=True)
    
    # 2단 레이아웃 (왼쪽: 지도, 오른쪽: 상세 텍스트)
    map_col, text_col = st.columns([1.5, 1])

    with map_col:
        # 지도 데이터 프레임 생성
        df_loc = pd.DataFrame(selected["locations"])
        
        # PyDeck 3D 지도 렌더링
        view_state = pdk.ViewState(
            latitude=df_loc['lat'].mean(), 
            longitude=df_loc['lon'].mean(), 
            zoom=2 if len(df_loc) > 3 else 5, # 글로벌 지사가 있으면 넓게, 국내만 있으면 좁게
            pitch=45 # 3D 기울기
        )
        
        layer = pdk.Layer(
            "ColumnLayer", # 기둥 형태의 마커
            data=df_loc,
            get_position='[lon, lat]',
            get_elevation=100000, # 기둥 높이
            elevation_scale=5,
            radius=50000, # 기둥 굵기
            get_fill_color='color', # 정의된 색상 (본사:빨강, 국내:파랑, 해외:초록)
            pickable=True,
            auto_highlight=True,
        )
        
        # 지도 그리기 (지도 컨테이너에 둥근 모서리 적용을 위해 컨테이너 사용)
        with st.container(border=True):
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9", # 깔끔한 밝은 지도 테마
                initial_view_state=view_state,
                layers=[layer],
                tooltip={"text": "{name}"} # 마우스 오버 시 이름 표시
            ))

    with text_col:
        # 우측에 거점 텍스트 카드 세로로 배치
        st.markdown(f"<div class='info-card' style='border-top-color:#dc2626;'><div class='info-card-title'>🏢 Headquarter (본사)</div><div class='info-card-value'>{selected['hq']}</div></div>", unsafe_allow_html=True)
        st.write("") # 간격
        st.markdown(f"<div class='info-card' style='border-top-color:#2563eb;'><div class='info-card-title'>🇰🇷 Domestic (국내 공장/지사)</div><div class='info-card-value'>{selected['kr']}</div></div>", unsafe_allow_html=True)
        st.write("") # 간격
        
        gl_color = "#10b981" if selected['branchesGL'] != "해당 없음 (국내 집중)" else "#94a3b8"
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
