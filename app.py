import streamlit as st
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="협력사 글로벌 현황", page_icon="🌍", layout="wide")

# 2. 프리미엄 C-Level CSS 주입 (AI 관련 스타일 제거)
st.markdown("""
    <style>
        /* 기본 여백 최소화 및 불필요한 요소 숨김 */
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }
        header { visibility: hidden; }
        footer { visibility: hidden; }

        /* 글로벌 폰트 및 텍스트 설정 */
        * { font-family: 'Pretendard', 'Malgun Gothic', sans-serif; }

        /* 대시보드 헤더 배너 */
        .dashboard-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 24px 32px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .dashboard-header h1 { margin: 0; font-size: 28px; font-weight: 700; color: #ffffff; }
        .dashboard-header p { margin: 5px 0 0 0; color: #94a3b8; font-size: 15px; }

        /* 정보 카드 스타일 */
        .info-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            height: 100%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: box-shadow 0.2s;
        }
        .info-card:hover { box-shadow: 0 4px 10px rgba(0,0,0,0.08); }
        .info-card-title { font-size: 14px; color: #64748b; font-weight: 600; margin-bottom: 8px; text-transform: uppercase; }
        .info-card-value { font-size: 16px; color: #0f172a; font-weight: 500; line-height: 1.5; }
        
        /* 섹션 타이틀 */
        .section-title {
            font-size: 20px; font-weight: 700; color: #1e293b; 
            margin-top: 30px; margin-bottom: 15px;
            padding-bottom: 10px; border-bottom: 2px solid #e2e8f0;
        }
        
        /* 사이드바 스타일링 */
        [data-testid="stSidebar"] {
            background-color: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }
    </style>
""", unsafe_allow_html=True)

# 3. 메인 화면 헤더 (요청하신 제목으로 고정)
st.markdown("""
    <div class='dashboard-header'>
        <div>
            <h1>🌍 협력사별 글로벌 현황</h1>
            <p>글로벌 공급망 및 파트너사 인프라 보고</p>
        </div>
        <div style="text-align: right;">
            <span style="background: #3b82f6; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;">Confidential</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# 4. 가상 데이터 설정 (AI 데이터 삭제)
@st.cache_data
def load_data():
    return [
        {
            "id": 1, "name": "A업체", "industry": "PCB 제조",
            "hq": "서울 서초구", "branchesKR": "천안 공장, 구미 R&D센터", "branchesGL": "베트남 하노이 공장, 미국 산호세 영업소",
            "products": [
                {"name": "서버용 PCB", "emoji": "🖲️", "img_path": "pcb.png"},
                {"name": "통신 컨트롤러", "emoji": "🔌", "img_path": "controller.png"},
                {"name": "고성능 칩셋", "emoji": "💾", "img_path": "chip.png"}
            ],
            "desc": "국내 천안 및 구미에서 핵심 R&D 및 초기 양산을 진행하며, 대량 생산은 베트남 하노이 공장에서 담당하고 있습니다. 북미 주요 고객사 대응을 위해 미국 산호세에 직영 영업소를 운영 중입니다."
        },
        {
            "id": 2, "name": "B업체", "industry": "정밀 가공",
            "hq": "부산 사하구", "branchesKR": "창원 공장", "branchesGL": "중국 칭다오 공장, 미국 텍사스 법인",
            "products": [
                {"name": "정밀 모터", "emoji": "⚙️", "img_path": "motor.png"}, 
                {"name": "로봇 암", "emoji": "🤖", "img_path": "robot.png"}
            ],
            "desc": "부산 본사를 중심으로 창원과 중국 칭다오에서 주요 장비 부품을 가공하고 있습니다. 최근 북미 IRA 법안 대응 및 직납 체계 구축을 위해 미국 텍사스에 조립 법인을 신설하였습니다."
        },
        {
            "id": 3, "name": "C업체", "industry": "원재료 (사출/화학)",
            "hq": "인천 남동구", "branchesKR": "울산 공장, 여수 공장", "branchesGL": "해당 없음 (국내 집중)",
            "products": [
                {"name": "합성수지", "emoji": "🧪", "img_path": "resin.png"}, 
                {"name": "특수 코팅액", "emoji": "💧", "img_path": "coating.png"},
                {"name": "산업용 접착제", "emoji": "🍯", "img_path": "glue.png"}
            ],
            "desc": "해외 지사는 없으나, 국내 핵심 화학 단지인 울산과 여수에 대규모 생산 플랜트를 운영하여 매우 안정적인 내수 공급망을 확보하고 있는 건실한 기업입니다."
        }
    ]

suppliers = load_data()

# 5. 좌측 사이드바: 검색 및 리스트
with st.sidebar:
    st.markdown("<h3 style='color: #0f172a; margin-bottom: 20px;'>🏢 파트너사 목록</h3>", unsafe_allow_html=True)
    
    search_term = st.text_input("🔍 업체명 / 업종 검색", placeholder="예: PCB, A업체").strip()

    # 검색 필터링
    filtered_data = [s for s in suppliers if search_term.lower() in s["name"].lower() or search_term.lower() in s["industry"].lower()]

    if not filtered_data:
        st.warning("검색 결과가 없습니다.")
        filtered_data = suppliers

    supplier_names = [s["name"] for s in filtered_data]
    selected_name = st.radio("상세 분석할 업체를 선택하세요", supplier_names, label_visibility="collapsed")

selected = next((s for s in filtered_data if s["name"] == selected_name), None)

# 6. 우측 메인 상세 화면
if selected:
    # 6-1. 요약 메트릭
    col1, col2, col3 = st.columns([1.5, 1, 1])
    with col1:
        st.markdown(f"<h2 style='margin:0; color:#0f172a; font-weight:800; font-size:32px;'>{selected['name']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin:5px 0 0 0; color:#64748b; font-size:16px;'>{selected['industry']}</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 6-2. 기업 개요 및 설명
    st.markdown("<div class='section-title'>기업 개요</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 16px; color: #334155; line-height: 1.6;'>{selected['desc']}</p>", unsafe_allow_html=True)

    # 6-3. 글로벌 거점 카드 UI
    st.markdown("<div class='section-title'>📍 주요 거점 인프라</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">🏢 Headquarter (본사)</div>
                <div class="info-card-value">{selected['hq']}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">🇰🇷 Domestic (국내 공장/지사)</div>
                <div class="info-card-value">{selected['branchesKR']}</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        # 해외 거점이 있으면 강조 효과
        gl_color = "#0f172a" if selected['branchesGL'] != "해당 없음" else "#94a3b8"
        st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title" style="color: #0284c7;">🌐 Global (해외 법인/지사)</div>
                <div class="info-card-value" style="color: {gl_color};">{selected['branchesGL']}</div>
            </div>
        """, unsafe_allow_html=True)

    # 6-4. 주요 생산 품목
    st.markdown("<div class='section-title'>📦 핵심 생산 품목</div>", unsafe_allow_html=True)
    prod_cols = st.columns(len(selected['products']))
    
    for idx, prod in enumerate(selected['products']):
        with prod_cols[idx]:
            with st.container():
                st.markdown(f"""
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; text-align: center;">
                """, unsafe_allow_html=True)
                
                if os.path.exists(prod.get("img_path", "")):
                    st.image(prod["img_path"], use_column_width=True)
                else:
                    st.markdown(f"<div style='font-size: 48px; margin-bottom: 10px;'>{prod['emoji']}</div>", unsafe_allow_html=True)
                
                st.markdown(f"<div style='font-size: 16px; font-weight: 600; color: #1e293b;'>{prod['name']}</div></div>", unsafe_allow_html=True)

    # 하단 여백
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
