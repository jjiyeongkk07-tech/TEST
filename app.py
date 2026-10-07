import streamlit as st
import os
import base64

# 1. 페이지 기본 설정 (반드시 가장 상단에 위치해야 합니다!)
st.set_page_config(page_title="협력사 글로벌 현황", page_icon="🌍", layout="wide")

# 2. Noto Sans KR 폰트 및 프리미엄 CSS 주입
st.markdown("""
    <style>
        /* Noto Sans KR 폰트 임포트 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap');

        /* 글로벌 폰트 강제 적용 */
        html, body, [class*="css"] {
            font-family: 'Noto Sans KR', sans-serif !important;
        }

        /* 기본 여백 최소화 및 불필요한 요소 숨김 */
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }
        header { visibility: hidden; }
        footer { visibility: hidden; }

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
        .dashboard-header h1 { margin: 0; font-size: 28px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;}
        .dashboard-header p { margin: 5px 0 0 0; color: #94a3b8; font-size: 15px; font-weight: 400;}

        /* 정보 카드 (거점 현황) 스타일 */
        .info-card {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 24px;
            height: 100%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: all 0.2s ease-in-out;
        }
        .info-card:hover { box-shadow: 0 6px 12px rgba(0,0,0,0.08); transform: translateY(-2px); }
        .info-card-title { font-size: 15px; color: #64748b; font-weight: 700; margin-bottom: 12px; }
        .info-card-value { font-size: 17px; color: #0f172a; font-weight: 600; line-height: 1.6; }
        
        /* 생산 품목 카드 스타일 (네모칸과 내용물 통합) */
        .product-card {
            background: white;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: all 0.2s ease-in-out;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .product-card:hover { box-shadow: 0 6px 12px rgba(0,0,0,0.08); transform: translateY(-2px); border-color: #94a3b8; }
        .product-title { font-size: 18px; font-weight: 700; color: #1e293b; margin-top: 16px; }

        /* 섹션 타이틀 */
        .section-title {
            font-size: 22px; font-weight: 800; color: #0f172a; 
            margin-top: 40px; margin-bottom: 20px;
            padding-bottom: 12px; border-bottom: 2px solid #e2e8f0;
        }
        
        /* 사이드바 스타일링 */
        [data-testid="stSidebar"] { background-color: #f8fafc; border-right: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# 3. 메인 화면 상단 헤더
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

# 4. 가상 데이터 설정
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
    st.markdown("<h3 style='color: #0f172a; margin-bottom: 20px; font-weight: 800;'>🏢 파트너사 목록</h3>", unsafe_allow_html=True)
    
    search_term = st.text_input("🔍 업체명 / 업종 검색", placeholder="예: PCB, A업체").strip()

    # 검색 필터링
    filtered_data = [s for s in suppliers if search_term.lower() in s["name"].lower() or search_term.lower() in s["
