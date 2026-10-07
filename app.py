import streamlit as st
import os

# 1. 페이지 기본 설정 (무조건 가장 먼저 와야 함)
st.set_page_config(page_title="협력사별 글로벌 현황", page_icon="🌍", layout="wide")

# 2. 강제 CSS 주입 (상단 여백 제거 및 기본 헤더 숨김)
st.markdown("""
    <style>
        /* Streamlit 기본 상단 여백을 1rem으로 대폭 축소 */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        /* 우측 상단 기본 메뉴(햄버거 버튼) 및 빈 헤더 숨김 */
        header {
            visibility: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# 3. 메인 화면 제목 (이제 화면 맨 위에 딱 붙어서 나옵니다)
st.markdown("""
    <div style='background-color: #0f172a; padding: 20px; border-radius: 10px; margin-bottom: 20px; margin-top: 0px;'>
        <h1 style='color: white; text-align: center; margin: 0;'>🌍 협력사별 글로벌 현황</h1>
    </div>
""", unsafe_allow_html=True)

# 4. 가상 데이터 설정
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

# 5. 좌측 사이드바: 검색 및 리스트
st.sidebar.header("🔍 협력사 검색")
search_term = st.sidebar.text_input("업체명 또는 업종 검색", "").strip()

# 검색 필터링 로직
filtered_data = []
for s in suppliers:
    if search_term.lower() in s["name"].lower() or search_term.lower() in s["industry"].lower():
        filtered_data.append(s)

# 검색 결과 예외 처리
if len(filtered_data) == 0:
    st.sidebar.error("검색 결과가 없습니다. 전체 목록을 표시합니다.")
    filtered_data = suppliers

supplier_names = [s["name"] for s in filtered_data]
selected_name = st.sidebar.radio("협력사 목록 (선택)", supplier_names, index=0)

selected = None
for s in filtered_data:
    if s["name"] == selected_name:
        selected = s
        break

# 6. 우측 메인 상세 화면
if selected:
    st.header(f"🏢 {selected['name']}")
    st.markdown(f"**업종:** `{selected['industry']}`")
    
    st.markdown("### 📍 글로벌 및 국내 거점 현황")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**🏢 본사**\n\n{selected['hq']}")
    with col2:
        st.success(f"**🇰🇷 한국 (지사/공장)**\n\n{selected['branchesKR']}")
    with col3:
        st.warning(f"**🌐 해외 (지사/법인)**\n\n{selected['branchesGL']}")

    st.write("---")
    
    st.markdown("### 📦 대표 생산 품목")
    num_products = len(selected['products'])
    prod_cols = st.columns(num_products)
    
    for idx, prod in enumerate(selected['products']):
        with prod_cols[idx]:
            with st.container(border=True):
                # 로컬 이미지 파일이 있으면 띄우고, 없으면 이모지 출력
                if os.path.exists(prod.get("img_path", "")):
                    st.image(prod["img_path"], use_column_width=True)
                else:
                    st.markdown(f"<h1 style='text-align: center; font-size: 50px; margin: 0;'>{prod['emoji']}</h1>", unsafe_allow_html=True)
                
                st.markdown(f"<h4 style='text-align: center; margin-top: 10px;'>{prod['name']}</h4>", unsafe_allow_html=True)

    st.write("---")
    
    st.markdown("### 📝 기업 상세 설명")
    st.write(selected['desc'])

    st.markdown("### ✨ AI 구매 전략 인사이트")
    st.success(selected['ai'])
