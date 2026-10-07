import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="AI 공급망 대시보드", page_icon="🌍", layout="wide")

# 2. 가상 데이터 설정 (추후 pd.read_excel('데이터.xlsx') 로 대체 가능)
@st.cache_data
def load_data():
    return [
        {
            "id": 1, "name": "(주)테크솔루션", "category": "전기/전자 부품",
            "hq": "서울 서초구", "branchesKR": "천안 공장, 구미 R&D센터", "branchesGL": "베트남 하노이 공장, 미국 산호세 영업소",
            "products": "서버용 고성능 PCB, 통신 모듈 컨트롤러, 전원 공급 장치",
            "desc": "국내 천안 및 구미에서 핵심 R&D 및 초기 양산을 진행하며, 대량 생산은 베트남 하노이 공장에서 담당. 북미 시장 대응을 위해 미국 산호세에 영업소 운영 중.",
            "ai": "💡 [분석] 베트남 지사를 적극 활용한 동남아 소싱 확대로 물류비 및 인건비 단가 15% 추가 절감 가능성이 분석됩니다."
        },
        {
            "id": 2, "name": "글로벌기계(주)", "category": "기계/설비",
            "hq": "부산 사하구", "branchesKR": "창원 공장", "branchesGL": "중국 칭다오 공장, 미국 텍사스 법인",
            "products": "산업용 정밀 모터, 자동화 로봇 암",
            "desc": "부산 본사를 중심으로 창원과 중국 칭다오에서 주요 부품 가공. 최근 미국 텍사스에 조립 법인을 신설하여 북미향 장비 직납 체계 구축 완료.",
            "ai": "💡 [분석] 미국 텍사스 공장 신설로 북미향 설비 조달 시 발생하던 해상 물류 리스크가 크게 감소할 것으로 예측됩니다."
        },
        {
            "id": 3, "name": "에코머티리얼즈", "category": "원부자재",
            "hq": "인천 남동구", "branchesKR": "울산 공장, 여수 공장", "branchesGL": "해당 없음",
            "products": "친환경 합성수지, 특수 표면 코팅액, 산업용 접착제",
            "desc": "해외 지사는 없으나, 국내 핵심 화학 단지인 울산과 여수에 대규모 공장을 운영하여 안정적인 내수 공급망 확보.",
            "ai": "💡 [분석] 국내 단일 공급망이나 재무 건전성이 우수합니다. 단, 원자재 수입 의존도가 높아 환율 변동에 따른 단가 모니터링이 필요합니다."
        }
    ]

suppliers = load_data()

# 3. 메인 화면 제목
st.title("🏆 구매팀 AI 공급망 가시성 대시보드 (Prototype)")
st.caption("사내 AI 경진대회 출품작 - 협력사별 글로벌 거래 현황 분석")
st.markdown("---")

# 4. 좌측 사이드바: 검색 및 리스트
st.sidebar.header("🔍 협력사 검색")
search_term = st.sidebar.text_input("업체명 또는 업종 검색", "").strip()

# 검색 필터링
filtered_data = [s for s in suppliers if search_term.lower() in s["name"].lower() or search_term.lower() in s["category"].lower()]

if not filtered_data:
    st.sidebar.warning("검색 결과가 없습니다.")
else:
    # 선택 라디오 버튼
    supplier_names = [s["name"] for s in filtered_data]
    selected_name = st.sidebar.radio("협력사 목록 (선택)", supplier_names)
    
    # 선택된 업체 매칭
    selected = next(s for s in filtered_data if s["name"] == selected_name)

    # 5. 우측 메인 상세 화면
    st.header(f"🏢 {selected['name']}")
    st.markdown(f"**분류:** `{selected['category']}`")
    
    st.markdown("### 📍 글로벌 및 국내 거점 현황")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**🏢 본사**\n\n{selected['hq']}")
    with col2:
        st.success(f"**🇰🇷 한국 (지사/공장)**\n\n{selected['branchesKR']}")
    with col3:
        st.warning(f"**🌐 해외 (지사/법인)**\n\n{selected['branchesGL']}")

    st.write("")
    
    st.markdown("### 📦 대표 생산 품목")
    st.code(selected['products'], language='plaintext')

    st.markdown("### 📝 기업 상세 설명")
    st.write(selected['desc'])

    st.markdown("---")
    st.markdown("### ✨ AI 구매 전략 인사이트")
    st.success(selected['ai'])
