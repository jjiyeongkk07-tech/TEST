import streamlit as st

st.set_page_config(page_title="협력사 글로벌 현황", page_icon="🌍", layout="wide")

css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap');
html, body, [class*='css'] { font-family: 'Noto Sans KR', sans-serif !important; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }
header { visibility: hidden; } footer { visibility: hidden; }
.dashboard-header { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 24px 32px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); color: white; display: flex; justify-content: space-between; align-items: center; }
.dashboard-header h1 { margin: 0; font-size: 28px; font-weight: 800; color: #ffffff; }
.dashboard-header p { margin: 5px 0 0 0; color: #94a3b8; font-size: 15px; }
.info-card { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 24px; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.info-card-title { font-size: 15px; color: #64748b; font-weight: 700; margin-bottom: 12px; }
.info-card-value { font-size: 17px; color: #0f172a; font-weight: 600; line-height: 1.6; }
.product-card { background: white; border: 1px solid #cbd5e1; border-radius: 12px; padding: 30px 20px; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; }
.product-title { font-size: 18px; font-weight: 700; color: #1e293b; margin-top: 16px; }
.section-title { font-size: 22px; font-weight: 800; color: #0f172a; margin-top: 40px; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid #e2e8f0; }
[data-testid='stSidebar'] { background-color: #f8fafc; border-right: 1px solid #e2e8f0; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

st.markdown("""
<div class='dashboard-header'>
    <div><h1>🌍 협력사별 글로벌 현황</h1><p>글로벌 공급망 및 파트너사 인프라 보고</p></div>
    <div><span style='background:#3b82f6; padding:6px 12px; border-radius:20px; font-size:13px; font-weight:600;'>Confidential</span></div>
</div>
""", unsafe_allow_html=True)

suppliers = [
    {
        "name": "A업체", "industry": "PCB 제조",
        "hq": "서울 서초구", "kr": "천안 공장, 구미 R&D센터", "gl": "베트남 하노이 공장, 미국 산호세 영업소",
        "products": [{"name": "서버용 PCB", "img": "🖲️"}, {"name": "통신 컨트롤러", "img": "🔌"}, {"name": "고성능 칩셋", "img": "💾"}],
        "desc": "국내 천안 및 구미에서 핵심 R&D 및 초기 양산을 진행하며, 대량 생산은 베트남 하노이 공장에서 담당하고 있습니다. 북미 주요 고객사 대응을 위해 미국 산호세에 직영 영업소를 운영 중입니다."
    },
    {
        "name": "B업체", "industry": "정밀 가공",
        "hq": "부산 사하구", "kr": "창원 공장", "gl": "중국 칭다오 공장, 미국 텍사스 법인",
        "products": [{"name": "정밀 모터", "img": "⚙️"}, {"name": "로봇 암", "img": "🤖"}],
        "desc": "부산 본사를 중심으로 창원과 중국 칭다오에서 주요 장비 부품을 가공하고 있습니다. 최근 북미 IRA 법안 대응 및 직납 체계 구축을 위해 미국 텍사스에 조립 법인을 신설하였습니다."
    },
    {
        "name": "C업체", "industry": "원재료 (사출/화학)",
        "hq": "인천 남동구", "kr": "울산 공장, 여수 공장", "gl": "해당 없음 (국내 집중)",
        "products": [{"name": "합성수지", "img": "🧪"}, {"name": "특수 코팅액", "img": "💧"}, {"name": "산업용 접착제", "img": "🍯"}],
        "desc": "해외 지사는 없으나, 국내 핵심 화학 단지인 울산과 여수에 대규모 생산 플랜트를 운영하여 매우 안정적인 내수 공급망을 확보하고 있는 건실한 기업입니다."
    }
]

with st.sidebar:
    st.markdown("<h3 style='color:#0f172a; margin-bottom:20px; font-weight:800;'>🏢 파트너사 목록</h3>", unsafe_allow_html=True)
    search_term = st.text_input("🔍 업체명 / 업종 검색", "").strip()
    filtered = [s for s in suppliers if search_term.lower() in s["name"].lower() or search_term.lower() in s["industry"].lower()]
    if not filtered: filtered = suppliers
    selected_name = st.radio("상세 분석할 업체 선택", [s["name"] for s in filtered])

selected = next(s for s in filtered if s["name"] == selected_name)

if selected:
    st.markdown(f"<div style='margin-bottom:10px;'><h2 style='margin:0; color:#0f172a; font-weight:800; font-size:36px;'>{selected['name']}</h2><p style='margin:8px 0 0 0; color:#475569; font-size:18px; font-weight:500;'>업종 : <span style='color:#0f172a; font-weight:700;'>{selected['industry']}</span></p></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>📝 기업 개요</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background-color:#f8fafc; border-left:4px solid #64748b; padding:20px;'><p style='margin:0; font-size:17px; color:#334155; line-height:1.7; font-weight:500;'>{selected['desc']}</p></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>📍 주요 거점 인프라</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='info-card'><div class='info-card-title'>🏢 Headquarter (본사)</div><div class='info-card-value'>{selected['hq']}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='info-card'><div class='info-card-title'>🇰🇷 Domestic (국내 공장/지사)</div><div class='info-card-value'>{selected['kr']}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='info-card'><div class='info-card-title' style='color:#0284c7;'>🌐 Global (해외 법인/지사)</div><div class='info-card-value'>{selected['gl']}</div></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>📦 핵심 생산 품목</div>", unsafe_allow_html=True)
    cols = st.columns(len(selected['products']))
    for idx, p in enumerate(selected['products']):
        cols[idx].markdown(f"<div class='product-card'><div style='font-size:56px; line-height:1; margin-bottom:10px;'>{p['img']}</div><div class='product-title'>{p['name']}</div></div>", unsafe_allow_html=True)
