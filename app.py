import streamlit as st
import os
import base64

# 1. 페이지 기본 설정
st.set_page_config(page_title="협력사별 글로벌 현황", page_icon="🌍", layout="wide")

# (선택) 로컬 이미지가 있을 때 불러오는 함수
def load_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# 2. 가상 데이터 설정 (품목 2~3개씩 배치)
@st.cache_data
def load_data():
    return [
        {
            "id": 1, "name": "A업체", "industry": "PCB",
            "hq": "서울 서초구", "branchesKR": "천안 공장, 구미 R&D센터", "branchesGL": "베트남 하노이 공장, 미국 산호세 영업소",
            "products": [
                {"name": "서버용 PCB", "emoji": "🖲️", "img_path": "pcb.png"},
                {"name": "통신 컨트롤러", "emoji": "🔌", "img_path": "controller.png"},
                {"name": "고성능 칩셋", "emoji": "💾", "img_path": "chip.png"}
            ],
            "desc": "국내 천안 및 구미에서 핵심 R&D 및 초기 양산을 진행하며, 대량 생산은 베트남 하노이 공장에서 담당. 북미 시장 대응을 위해 미국 산호세에 영업소 운영 중.",
            "ai": "💡 [분석] 베트남 지사를 적극 활용한 동남아 소싱 확대로 물류비 및 인건비 단가 15% 추가 절감 가능성이 분석됩니다."
        },
        {
            "id": 2, "name": "B업체", "industry": "가공(일반)",
            "hq": "부산 사하구", "branchesKR": "창원 공장", "branchesGL": "중국 칭다오 공장, 미국 텍사스 법인",
            "products": [
                {"name": "정밀 모터", "emoji": "⚙️", "img_path": "motor.png"}, 
                {"name": "로봇 암", "emoji": "🤖", "img_path": "robot.png"}
            ],
            "desc": "부산 본사를 중심으로 창원과 중국 칭다오에서 주요 부품 가공. 최근 미국 텍사스에 조립 법인을 신설하여 북미향 장비 직납 체계 구축 완료.",
            "ai": "💡 [분석] 미국 텍사스 공장 신설로 북미향 설비 조달 시 발생하던 해상 물류 리스크가 크게 감소할 것으로 예측됩니다."
        },
        {
            "id": 3, "name": "C업체", "industry": "원재료(사출)",
            "hq": "인천 남동구", "branchesKR": "울산 공장, 여수 공장", "branchesGL": "해당 없음",
            "products": [
                {"name": "합성수지", "emoji": "🧪", "img_path": "resin.png"}, 
                {"name": "특수 코팅액", "emoji": "💧", "img_path": "coating.png"},
                {"name": "산업용 접착제", "emoji": "🍯", "img_path": "glue.png"}
            ],
            "desc": "해외 지사는 없으나, 국내 핵심 화학 단지인 울산과 여수에 대규모 공장을 운영하여 안정적인 내수 공급망 확보.",
            "ai": "💡 [분석] 국내 단일 공급망이나 재무 건전성이 우수합니다. 단, 원자재 수입 의존도가 높아 환율 변동에 따른 단가 모니터링이 필요합니다."
        }
    ]

suppliers = load_data()

# 3. 메인 화면 제목 (훨씬 눈에 띄게 강조)
st.markdown("""
    <div style="background-color:#0f172a; padding:20px; border-radius:10px; margin-bottom:25px;">
        <h1 style="color:white; margin:0; text-align:center;">🌍 협력사별 글로벌 현황</h1>
    </div>
""", unsafe_allow_html=True)

# 4. 좌측 사이드바: 검색 및 리스트
st.sidebar.header("🔍 협력사 검색")
search_term = st.sidebar.text_input("업체명 또는 업종 검색", "").strip()

filtered_data = [s for s in suppliers if search_term.lower() in s["name"].lower() or search_term.lower() in s["industry"].lower()]

if not filtered_data:
    st.sidebar.warning("검색 결과가 없습니다.")
else:
    supplier_names = [s["name"] for s in filtered_data]
    selected_name = st.sidebar.radio("협력사 목록 (선택)", supplier_names)
    selected = next(s for s in filtered_data if s["name"] == selected_name)

    # 5. 우측 메인

