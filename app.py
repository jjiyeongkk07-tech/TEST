import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import pydeck as pdk
import urllib.request
import ssl
import base64
import re

# 🌟 data.py 파일에서 데이터 및 설정 정보 가져오기
from data import suppliers_data, excel_img_data, map_view_mapping, location_colors, map_radius_settings, get_homepage_domain

# 1. 페이지 설정
st.set_page_config(page_title="글로벌 SCM 분석", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

# --- 세션 초기화 ---
if "map_view" not in st.session_state:
    st.session_state.map_view = "전체 뷰"
if "popup_img" not in st.session_state:
    st.session_state.popup_img = None
if "selected_company" not in st.session_state:
    st.session_state.selected_company = "🏠 종합 메인 화면"

def set_view(view):
    st.session_state.map_view = view

def reset_map_view():
    st.session_state.map_view = "전체 뷰"

# 🚀 줌/드래그가 가능한 이미지 HTML 컴포넌트 함수 정의
def render_zoomable_image(img_data):
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; background: #F9F8F6; overflow: hidden; border-radius: 12px; }}
        .img-container {{ width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; position: relative; }}
        img {{ max-width: 95%; max-height: 95%; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); cursor: grab; transform-origin: center; }}
        img:active {{ cursor: grabbing; }}
    </style>
    </head>
    <body>
        <div class="img-container" id="container">
            <img id="zoom-img" src="data:image/jpeg;base64,{img_data}">
        </div>
        <script>
            const img = document.getElementById('zoom-img');
            const container = document.getElementById('container');
            let scale = 1;
            let translateX = 0;
            let translateY = 0;
            let isDragging = false;
            let startX, startY;

            // ✅ 마우스 휠로 확대/축소 (브라우저 전체 페이지 줌과 충돌 방지)
            container.addEventListener('wheel', (e) => {{
                // e.preventDefault(); <- 브라우저 고유의 줌(Ctrl+휠) 및 스크롤을 막지 않도록 제거함
                let zoomSpeed = 0.002;
                scale += e.deltaY * -zoomSpeed;
                scale = Math.min(Math.max(0.5, scale), 10); // 0.5배 ~ 10배까지 허용
                img.style.transform = `translate(${{translateX}}px, ${{translateY}}px) scale(${{scale}})`;
            }}, {{ passive: true }}); // passive: true를 통해 브라우저 전체 확대/축소를 절대 막지 않음

            // 마우스 클릭 드래그로 이미지 이동 (Pan 기능)
            img.addEventListener('mousedown', (e) => {{
                e.preventDefault();
                isDragging = true;
                startX = e.clientX - translateX;
                startY = e.clientY - translateY;
            }});

            window.addEventListener('mouseup', () => {{
                isDragging = false;
            }});

            window.addEventListener('mouseleave', () => {{
                isDragging = false;
            }});

            window.addEventListener('mousemove', (e) => {{
                if (!isDragging) return;
                e.preventDefault();
                translateX = e.clientX - startX;
                translateY = e.clientY - startY;
                img.style.transform = `translate(${{translateX}}px, ${{translateY}}px) scale(${{scale}})`;
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=650, scrolling=False)


# 🚀 팝업 모달 함수 정의 (Streamlit 공식 다이얼로그 기능 활용)
if hasattr(st, "dialog"):
    @st.dialog("🔍 이미지 확대 보기", width="large")
    def show_popup_modal(img_data):
        render_zoomable_image(img_data)
elif hasattr(st, "experimental_dialog"):
    @st.experimental_dialog("🔍 이미지 확대 보기", width="large")
    def show_popup_modal(img_data):
        render_zoomable_image(img_data)
else:
    # 구버전 Streamlit 호환성 유지용 폴백
    def show_popup_modal(img_data):
        st.session_state.popup_img = img_data
        st.rerun()

# 2. 테마 CSS 설정 (레이아웃 1400px 제한 등 완벽 유지)
css = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
html, body, [class*='css'] { font-family: 'Pretendard', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #F9F8F6 0%, #EFEBE5 100%); }
.block-container { 
    background-color: #ffffff; padding: 3rem 4rem !important; margin-top: 1rem; margin-bottom: 3rem;
    border-radius: 16px; max-width: 1400px; border: 1px solid #E5E0D8; box-shadow: 0 15px 35px rgba(100, 90, 80, 0.08);
}
#MainMenu { visibility: hidden; } 
footer { visibility: hidden; }
header { background-color: transparent !important; }

/* 사이드바 영역 CSS 추가: 글자 크기 키우기 */
[data-testid="stSidebar"] { 
    background-color: #Fdfcfb !important; 
    border-right: 1px solid #E5E0D8 !important; 
}
[data-testid="stSidebar"] h3 { 
    font-size: 24px !important; 
}

/* 업종, 업체, 국가 탭 글씨 크기를 '분석할 업체 선택'과 완벽히 동일하게(17.5px) 강제 적용 */
div[data-testid="stSidebar"] button[data-baseweb="tab"] p,
div[data-testid="stSidebar"] button[data-baseweb="tab"] span,
div[data-testid="stSidebar"] button[data-baseweb="tab"] div[data-testid="stMarkdownContainer"] p {
    font-size: 17.5px !important; 
    font-weight: 900 !important;
    color: #2C2A29 !important;
}
div[data-testid="stSidebar"] button[data-baseweb="tab"] {
    padding: 10px 5px !important; 
}

/* 다른 선택박스, 라디오 버튼 텍스트 크기 유지 */
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] div.stRadio > label,
[data-testid="stSidebar"] .stSelectbox label {
    font-size: 16.5px !important; 
    font-weight: 700 !important;
    color: #2C2A29 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label p,
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span {
    font-size: 16px !important; 
    color: #4A4441 !important;
}
[data-testid="stSidebar"] .stTextInput input {
    font-size: 16px !important;
}

/* ✅ 메트릭(검색된 파트너사 등) 라벨 폰트 크기 강력 적용 */
[data-testid="stMetricLabel"], 
[data-testid="stMetricLabel"] div,
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] span,
[data-testid="stMetricLabel"] label {
    font-size: 19px !important; 
    font-weight: 900 !important;
    color: #2C2A29 !important;
}

/* 완벽한 가로 정렬을 위한 내부 컴포넌트 높이 고정 */
.section-header { 
    color: #2C2A29; text-align: center; font-weight: 900; font-size: 20px; 
    border-bottom: 3px solid #E5E0D8; padding-bottom: 12px; margin-bottom: 15px; 
}
.img-container { 
    height: 220px; background: #ffffff; border: 1px solid #E5E0D8; 
    border-radius: 12px; padding: 15px; display: flex; 
    justify-content: center; align-items: center; margin-bottom: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.img-container img { max-width: 100%; max-height: 100%; object-fit: contain; }

/* 하단 태그 가로 정렬 (양쪽 모두 동일한 디자인 적용) */
.tag-wrap-box { 
    display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; 
    align-items: flex-start; padding-top: 20px; margin-top: 20px;
    border-top: 1px dashed #E5E0D8; min-height: 70px;
}
.unified-tag { 
    font-size: 16.5px; font-weight: 800; color: #4A4441; text-align: center; 
    background: #F8F9FA; padding: 12px 24px; border-radius: 30px; 
    border: 1px solid #D1D5DB; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    white-space: nowrap;
}

/* 텍스트 및 기본 요소 */
h2, h3, h4, p, span, label, li { color: #2C2A29 !important; }
.main-title { font-size: 34px !important; font-weight: 900 !important; color: #ffffff !important; margin: 0 !important; line-height: 1.2 !important; letter-spacing: -1px !important; }
.section-title { font-size: 24px; font-weight: 900; color: #2C2A29 !important; margin-top: 45px; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; padding-bottom: 12px; border-bottom: 3px solid #E5E0D8; }
.section-num { color: #C4A47C; font-size: 28px; font-weight: 900; letter-spacing: -1px; }
.desc-box { background-color: #FDFCFB; border: 1px solid #E5E0D8; border-radius: 12px; padding: 30px; border-left: 6px solid #C4A47C; font-size: 17px; line-height: 1.8; font-weight: 400; }

/* 일반 버튼 스타일 (확대 보기 - 크기 축소 유지) */
div.stButton > button { 
    background-color: #ffffff !important; border: 1px solid #E5E0D8 !important; 
    border-radius: 10px !important; color: #2C2A29 !important; 
    padding: 8px 14px !important; width: 100% !important; height: auto !important; 
    display: block !important; text-align: center !important; 
    transition: all 0.2s ease !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important; 
}
div.stButton > button p { 
    font-size: 14px !important; font-weight: 800 !important; color: #2C2A29 !important; 
    white-space: pre-wrap !important; line-height: 1.5 !important; 
    text-align: center !important; 
    margin: 0 !important; display: block !important; 
}
div.stButton > button:hover { 
    background-color: #FDFCFB !important; border-color: #C4A47C !important; 
    transform: translateY(-2px) !important; box-shadow: 0 8px 12px rgba(0,0,0,0.05) !important; 
}

/* 거점 표시 전용 버튼 스타일 (글자 크기 및 여백 확대) */
div.stButton > button[kind="primary"] {
    padding: 14px 20px !important; 
    border-radius: 12px !important;
}
div.stButton > button[kind="primary"] p {
    font-size: 17.5px !important; 
}

/* 🚨 렌더링 에러 해결: div 대신 div.element-container로 명확히 타겟팅 */
div.element-container:has(.main-title-anchor) { 
    height: 0px !important; 
    margin: 0 !important; 
    padding: 0 !important; 
    overflow: hidden !important; 
}
div.element-container:has(.main-title-anchor) + div.element-container button {
    background-color: #2C2A29 !important; 
    padding: 30px 40px !important; 
    border-radius: 12px !important; 
    margin-bottom: 20px !important; 
    border: none !important;
    border-bottom: 4px solid #C4A47C !important;
    width: 100% !important;
    text-align: left !important;
    display: block !important;
    box-shadow: none !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}
div.element-container:has(.main-title-anchor) + div.element-container button:hover {
    background-color: #353332 !important;
    transform: none !important;
}
div.element-container:has(.main-title-anchor) + div.element-container button p {
    font-size: 34px !important; 
    font-weight: 900 !important; 
    color: #ffffff !important; 
    margin: 0 !important; 
    line-height: 1.2 !important; 
    letter-spacing: -1px !important; 
    text-align: left !important;
}

/* 🌐 홈페이지 링크 배지 (베이지/골드 테마) */
.hp-link{
    display: inline-flex; align-items: center; gap: 8px;
    padding: 7px 16px 7px 13px;
    background: #FDFCFB;
    border: 1px solid #E5E0D8;
    border-left: 3px solid #C4A47C;
    border-radius: 30px;
    font-size: 15px; font-weight: 800;
    text-decoration: none !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    transition: all 0.2s ease;
    white-space: nowrap;
}
.hp-link span{ color: #8A6F43 !important; }
.hp-link:hover{
    background: #ffffff;
    border-color: #C4A47C;
    box-shadow: 0 6px 12px rgba(196,164,124,0.20);
    transform: translateY(-2px);
}
.hp-link:hover span{ color: #2C2A29 !important; }
.hp-arw{ font-size: 13px; opacity: 0.7; }
.hp-link:hover .hp-arw{ opacity: 1; }

/* 섹션 헤더(01. 기업 개요) 안에 들어간 배지는 제목과 균형 맞춰 축소 */
.section-title .hp-link{
    font-size: 14px;
    font-weight: 700;
    padding: 5px 14px 5px 11px;
}
.section-title .hp-arw{ font-size: 12px; }

/* === 03. 주요 고객사 매입 비중 (TOP 4 전용, 100% 스택바) === */
/* ✅ 수정 1: 글자 크기 축소 (21px -> 16px), 막대 높이 64px -> 56px */
/* ✅ 수정 2: 폭에 따라 16px / 14px / 12.5px 3단계 자동 적용 */
.cust-box { padding: 24px 28px; background: #FDFCFB; border: 1px solid #E5E0D8;
            border-radius: 12px; margin-bottom: 10px; }
.cust-stack { display: flex; height: 56px; border-radius: 8px; overflow: hidden;
              border: 1px solid #E5E0D8; }
.cust-seg { display: flex; align-items: center; justify-content: center;
            font-size: 16px !important; font-weight: 800 !important;
            letter-spacing: -0.3px;
            text-shadow: 0 1px 2px rgba(0,0,0,0.10);
            white-space: nowrap; overflow: hidden;
            padding: 0 4px;
            transition: filter 0.2s ease; cursor: default; }
.cust-seg.seg-md { font-size: 14px !important; }
.cust-seg.seg-sm { font-size: 12.5px !important; text-shadow: none; padding: 0 2px; }
.cust-seg:hover { filter: brightness(1.08); }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. 데이터 및 변환 함수
CUSTOMER_TOP_N = 4                      # 개별 표기할 상위 고객사 수
CUSTOMER_SHOW_ETC = False               # ✅ True로 바꾸면 '기타' 구간이 다시 표시됨
CUSTOMER_PALETTE = [                    # TOP 4 전용 (진한 → 연한 골드)
    ("#8A6F43", "#ffffff"),
    ("#A9865A", "#ffffff"),
    ("#C4A47C", "#ffffff"),
    ("#D8C19D", "#2C2A29"),
]
ETC_COLOR = ("#EFE9DE", "#2C2A29")      # '기타' 구간 (CUSTOMER_SHOW_ETC=True일 때만 사용)

def _parse_ratio(v):
    """35, 35.5, '35%', '약 35' 등을 float으로 변환. 불가하면 None."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    m = re.search(r"(\d+(?:\.\d+)?)", str(v).replace(",", ""))
    return float(m.group(1)) if m else None

def _is_etc(name):
    return name.strip() in ("기타", "기타고객", "기타 고객사", "기타 등", "ETC", "etc", "Others")

def _fmt_ratio(v):
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}"

def _short_name(name):
    """막대 안에 표기할 때 법인 접두/접미어를 제거해 글자 수 절약. (툴팁은 원본 유지)"""
    s = str(name).strip()
    s = re.sub(r"^$\s*주\s*$\s*|^㈜\s*|^주식회사\s*", "", s)
    s = re.sub(r"\s*$\s*주\s*$$|\s*㈜$|\s*주식회사$", "", s)
    return s.strip() or str(name).strip()

def _legacy_customer_tags(names):
    """비중 정보가 전혀 없는 업체는 기존 둥근 태그 방식 그대로 유지."""
    tags_html = "<div style='display:flex; flex-wrap:wrap; gap:15px;'>"
    for comp in names:
        tags_html += (
            "<div style='padding:14px 28px; background:#ffffff; border:2px solid #C4A47C;"
            " border-radius:40px; font-size:18px; font-weight:900; color:#2C2A29;"
            " box-shadow:0 6px 12px rgba(196,164,124,0.15); display:flex; align-items:center;'>"
            f"🤝 {comp}</div>"
        )
    tags_html += "</div>"
    return f"<div class='cust-box'>{tags_html}</div>"

def get_customer_tags_html(customers):
    if not customers:
        return "<p style='color:#8A817C; font-size:15px;'>등록된 주요 고객사 정보가 없습니다.</p>"

    # 리스트(비중 미입력)로 들어온 기존 데이터는 기존 디자인 유지
    if not isinstance(customers, dict):
        return _legacy_customer_tags(list(customers))

    items = [(str(k).strip(), _parse_ratio(v)) for k, v in customers.items()]

    # ✅ 수정 1: '기타' 키와 비중 미기재 업체는 집계에서 제외 (TOP 4만 사용)
    rated = [(k, v) for k, v in items if v is not None and v > 0 and not _is_etc(k)]

    if not rated:
        return _legacy_customer_tags([k for k, _ in items])

    # 비중 내림차순 → 상위 4개사만 개별 표기
    rated.sort(key=lambda x: -x[1])
    top = rated[:CUSTOMER_TOP_N]

    rows = []
    if CUSTOMER_SHOW_ETC:
        # (옵션) 기타 구간 포함 모드 — 100% 기준으로 잔여분을 기타로 표시
        total_all = sum(v for _, v in rated)
        base = total_all if total_all > 100.0 else 100.0
        for i, (name, val) in enumerate(top):
            bg, fg = CUSTOMER_PALETTE[i % len(CUSTOMER_PALETTE)]
            rows.append((name, val, val / base * 100.0, bg, fg, ""))
        etc_val = sum(v for _, v in rated[CUSTOMER_TOP_N:]) + max(0.0, 100.0 - total_all)
        if etc_val > 0.5:
            rows.append(("기타", etc_val, etc_val / base * 100.0,
                         ETC_COLOR[0], ETC_COLOR[1], ""))
    else:
        # ✅ 기본 모드: TOP 4 합계를 100%로 환산해 막대를 꽉 채움 (라벨은 입력값 그대로)
        base = sum(v for _, v in top) or 100.0
        for i, (name, val) in enumerate(top):
            bg, fg = CUSTOMER_PALETTE[i % len(CUSTOMER_PALETTE)]
            rows.append((name, val, val / base * 100.0, bg, fg, ""))

    # ✅ 수정 2: 구간 폭에 따라 글자 크기와 라벨 형태를 3단계로 자동 조절
    segs = ""
    for name, val, w, bg, fg, tip in rows:
        disp = _short_name(name)
        cls = "cust-seg"
        if w >= 26:
            label = f"{disp} {_fmt_ratio(val)}%"
        elif w >= 13:
            label = f"{disp} {_fmt_ratio(val)}%"
            cls += " seg-md"
        elif w >= 3:
            label = f"{_fmt_ratio(val)}%"
            cls += " seg-sm"
        else:
            label = ""
        title = tip or f"{name} {_fmt_ratio(val)}%"
        segs += (
            f"<div class='{cls}' style='width:{w:.4f}%; background:{bg};"
            f" color:{fg} !important;' title='{title}'>{label}</div>"
        )

    # 막대바 아래 비율 축(0% / 25% / 50% / 75% / 100%)은 표시하지 않음
    return f"<div class='cust-box'><div class='cust-stack'>{segs}</div></div>"

# 🌐 홈페이지 링크 배지 HTML 생성 (<a> 태그만 반환하여 원하는 위치에 삽입)
def get_homepage_link_html(company):
    url = str(company.get("homepage", "") or "").strip()
    if not url or url == "-":
        return ""
    domain = get_homepage_domain(url) or url
    return (
        f"<a class='hp-link' href='{url}' target='_blank' rel='noopener noreferrer' title='{url}'>"
        f"<span style='font-size:15px;'>🌐</span>"
        f"<span>{domain}</span>"
        f"<span class='hp-arw'>↗</span></a>"
    )

@st.cache_data(show_spinner=False)
def get_base64_image(url):
    if not url or not str(url).startswith("http"): return None
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req, context=ctx, timeout=5)
        return base64.b64encode(res.read()).decode('utf-8')
    except Exception:
        return None

# 구버전 Streamlit 팝업 렌더링 폴백
if not hasattr(st, "dialog") and not hasattr(st, "experimental_dialog"):
    if st.session_state.popup_img:
        st.markdown("<hr style='border: 2px solid #2C2A29;'>", unsafe_allow_html=True)
        pop_col1, pop_col2 = st.columns([8, 2])
        with pop_col1:
            st.markdown("<h3 style='margin-top:0;'>🔍 이미지 확대 보기</h3>", unsafe_allow_html=True)
        with pop_col2:
            if st.button("❌ 닫기", use_container_width=True, key="fallback_close"):
                st.session_state.popup_img = None
                st.rerun()
        # 폴백 시에도 줌 기능이 포함된 컴포넌트로 호출
        render_zoomable_image(st.session_state.popup_img)
        st.markdown("<hr style='border: 2px solid #2C2A29; margin-bottom: 40px;'>", unsafe_allow_html=True)

# 4. 초기 데이터 로드 
if "suppliers" not in st.session_state: st.session_state.suppliers = suppliers_data
if "excel_img_data" not in st.session_state: st.session_state.excel_img_data = excel_img_data
suppliers = st.session_state.suppliers

# 5. 헤더 및 사이드바 
# 타이틀 클릭 시 메인 화면으로 돌아가는 버튼 
st.markdown("<div class='main-title-anchor'></div>", unsafe_allow_html=True)

def go_to_main():
    st.session_state.selected_company = "🏠 종합 메인 화면"
    st.session_state.map_view = "전체 뷰"

st.button("🌍 글로벌 SCM 및 파트너사 인프라 분석", on_click=go_to_main, use_container_width=True)

with st.sidebar:
    st.markdown("<h3 style='color:#C4A47C !important; font-weight:900;'>🔍 상세 검색</h3>", unsafe_allow_html=True)
    
    # 필터 옵션 리스트 생성
    all_countries_set = set()
    for s in suppliers:
        for loc in s.get("locations", []): all_countries_set.add(loc["country"])
    
    raw_industry_list = list(set(s.get("industry", "미분류") for s in suppliers if s.get("industry") != "미분류"))
    raw_country_list = list(all_countries_set)
    
    industry_list = ["전체"] + sorted(raw_industry_list)
    country_list = ["전체"] + sorted(raw_country_list)

    tab_industry, tab_company, tab_country = st.tabs(["🏷️ 업종", "🏢 업체", "🌍 국가"])
    with tab_industry: selected_industry = st.selectbox("조회할 업종을 선택하세요", industry_list, on_change=reset_map_view, label_visibility="collapsed")
    with tab_company: search_term = st.text_input("업체명을 입력하세요", placeholder="예: 한성전장", label_visibility="collapsed").strip()
    with tab_country: selected_country = st.selectbox("조회할 국가를 선택하세요", country_list, on_change=reset_map_view, label_visibility="collapsed")

    filtered = suppliers
    if selected_industry != "전체": filtered = [s for s in filtered if s.get("industry") == selected_industry]
    if selected_country != "전체": filtered = [s for s in filtered if any(loc.get("country") == selected_country for loc in s.get("locations", []))]
    if search_term: filtered = [s for s in filtered if search_term.lower() in s.get("name", "").lower()]

    st.markdown("<hr style='border-color: #E5E0D8; margin: 20px 0;'>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size: 17.5px; font-weight: 900; color: #2C2A29; margin-bottom: 10px;'>📊 분석할 업체 선택</div>", unsafe_allow_html=True)
    
    options_sidebar_map = {"🏠 종합 메인 화면": "🏠 종합 메인 화면"}
    
    for s in sorted(filtered, key=lambda x: x.get('name', '')): 
        options_sidebar_map[s['name']] = s['name']
        
    options_list = list(options_sidebar_map.keys())

    if st.session_state.selected_company not in options_list:
        st.session_state.selected_company = "🏠 종합 메인 화면"

    selected_display_name = st.radio(
        "", 
        options_list, 
        key="selected_company",
        on_change=reset_map_view, 
        label_visibility="collapsed"
    )
    selected_name = options_sidebar_map[selected_display_name]


# 6. 메인 화면 렌더링 
if selected_name == "🏠 종합 메인 화면":
    st.markdown("<div class='section-title' style='margin-top:0;'>📊 글로벌 SCM 통합 현황</div>", unsafe_allow_html=True)
    total_companies = len(filtered)
    all_locations = [loc for s in filtered for loc in s.get("locations", [])]
    col1, col2, col3 = st.columns(3)
    col1.metric("📌 검색된 파트너사", f"{total_companies} 개사")
    col2.metric("🏭 총 운영 거점", f"{len(all_locations)} 곳")
    col3.metric("🌐 해외 진출 거점", f"{len([l for l in all_locations if l.get('type') not in ['hq', 'kr']])} 곳")
    
    st.markdown("<div class='section-title'>🗺️ 전 세계 거점 분포도</div>", unsafe_allow_html=True)
    if all_locations:
        df_all = pd.DataFrame(all_locations)
        
        # ✅ 종합 메인화면: 국내(파란색) / 해외(골드색) 구분
        def get_main_color(row):
            if row.get('type') in ['hq', 'kr']:
                return [41, 128, 185, 220] # 파란색 (국내)
            else:
                return [196, 164, 124, 220] # 골드색 (해외)
                
        df_all['color'] = df_all.apply(get_main_color, axis=1)

        # ✅ min_zoom=1.5 추가: 축소를 제한하여 가로 반복 생성 원천 차단
        view_state = pdk.ViewState(latitude=35.0, longitude=127.0, zoom=1.5, min_zoom=1.5, max_zoom=15, pitch=0)
        layer = pdk.Layer(
            "ScatterplotLayer", 
            data=df_all, 
            get_position='[lon, lat]', 
            get_fill_color='color', 
            get_line_color=[255, 255, 255], 
            stroked=True, 
            line_width_min_pixels=1, 
            get_radius=100000, 
            radius_min_pixels=6, 
            radius_max_pixels=15, 
            pickable=True
        )
        
        # ✅ 줌, 마우스 드래그 조작 활성화 (controller=True)
        view = pdk.View(type="MapView", controller=True, repeat=False)
        st.pydeck_chart(pdk.Deck(map_style="light", initial_view_state=view_state, views=[view], layers=[layer], tooltip={"text": "{name}\n{address}"}))

elif selected_name:
    selected = next((s for s in filtered if s["name"] == selected_name), None)
    if selected:
        badge_html = f"<div style='margin-bottom:25px; display:flex; align-items:center; gap:10px; flex-wrap:wrap;'><h2 style='margin:0; font-weight:900; font-size:42px; letter-spacing:-1px;'>{selected.get('name', '')}</h2><span style='background:#C4A47C; color:#ffffff !important; padding:6px 14px; font-size:16px; font-weight:900; border-radius:6px;'>{selected.get('industry', '')}</span>"
        if selected.get('sub_industry'): badge_html += f"<span style='background:#FDFCFB; border:1px solid #E5E0D8; color:#8A817C !important; padding:5px 12px; font-size:14px; font-weight:700; border-radius:4px;'>{selected.get('sub_industry', '')}</span>"
        st.markdown(badge_html + "</div>", unsafe_allow_html=True)

        # 🌐 '01. 기업 개요' 헤더 줄 오른쪽 끝에 홈페이지 링크 배지 배치
        st.markdown(
            "<div class='section-title'><span class='section-num'>01.</span> 기업 개요"
            f"<span style='margin-left:auto;'>{get_homepage_link_html(selected)}</span>"
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown(f"<div class='desc-box'>📖 {selected.get('desc', '등록된 기업 개요가 없습니다.')}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'><span class='section-num'>02.</span> 핵심 역량 및 품질 인증</div>", unsafe_allow_html=True)
        company_images = st.session_state.excel_img_data.get(selected['name'], {"prod_imgs": [], "cert_imgs": []})

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("<div class='section-header'>🌟 핵심 생산 품목</div>", unsafe_allow_html=True)
            prod_list = company_images.get("prod_imgs", [])
            if prod_list:
                img_cols = st.columns(len(prod_list))
                for idx, img_url in enumerate(prod_list):
                    with img_cols[idx]:
                        img_data = get_base64_image(img_url)
                        if img_data:
                            st.markdown(f"<div class='img-container'><img src='data:image/jpeg;base64,{img_data}'></div>", unsafe_allow_html=True)
                            if st.button("🔍 확대 보기", key=f"btn_prod_{idx}", use_container_width=True):
                                show_popup_modal(img_data)
            else:
                st.info("등록된 이미지가 없습니다.")
                
            all_tags = []
            for prod_name in selected.get('products', []):
                tags = [t.strip() for t in prod_name.replace(" / ", "/").split("/")]
                all_tags.extend([t for t in tags if t])
                
            if all_tags:
                tags_html = "".join([f"<div class='unified-tag'>{t}</div>" for t in all_tags])
                st.markdown(f"<div class='tag-wrap-box'>{tags_html}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='tag-wrap-box'><div class='unified-tag' style='visibility:hidden;'>-</div></div>", unsafe_allow_html=True)


        with col_right:
            st.markdown("<div class='section-header'>🏅 품질 및 ESG 인증</div>", unsafe_allow_html=True)
            cert_list = company_images.get("cert_imgs", [])
            if cert_list:
                cert_cols = st.columns(len(cert_list))
                for idx, cert_url in enumerate(cert_list):
                    with cert_cols[idx]:
                        cert_data = get_base64_image(cert_url)
                        if cert_data:
                            st.markdown(f"<div class='img-container'><img src='data:image/jpeg;base64,{cert_data}'></div>", unsafe_allow_html=True)
                            if st.button("🔍 확대 보기", key=f"btn_cert_{idx}", use_container_width=True):
                                show_popup_modal(cert_data)
            else:
                st.info("등록된 인증서 이미지가 없습니다.")
            
            if selected.get('certs'):
                badges = "".join([f"<div class='unified-tag'>{c}</div>" for c in selected['certs']])
                st.markdown(f"<div class='tag-wrap-box'>{badges}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='tag-wrap-box'><div class='unified-tag' style='visibility:hidden;'>-</div></div>", unsafe_allow_html=True)


        st.markdown("<div class='section-title' style='margin-top: 40px;'><span class='section-num'>03.</span> 주요 고객사 및 매입 비중[TOP4]</div>", unsafe_allow_html=True)
        st.markdown(get_customer_tags_html(selected.get('customers', [])), unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top: 50px;'><span class='section-num'>04.</span> 글로벌 네트워크</div>", unsafe_allow_html=True)
        
        map_col, text_col = st.columns([2.5, 1]) 
        df_loc = pd.DataFrame(selected.get("locations", []))

        with map_col:
            current_view = st.session_state.map_view
            target_type_key = map_view_mapping.get(current_view, "all")

            # ✅ 개별 업체 화면: 기본적으로 국내(파란색), 해외(골드색) 구분
            def get_color(row):
                is_domestic = row.get('type') in ['hq', 'kr']
                active_color = [41, 128, 185, 220] if is_domestic else [196, 164, 124, 220]
                dim_color = [200, 200, 200, 100]
                
                if current_view == "전체 뷰": 
                    return active_color
                if row['type'] == target_type_key: 
                    return active_color
                return dim_color

            def get_radius(row):
                if current_view == "전체 뷰": return map_radius_settings["all_view"]
                if row['type'] == target_type_key: return map_radius_settings["highlighted"]
                return map_radius_settings["dimmed"]

            if not df_loc.empty:
                df_loc['color'] = df_loc.apply(get_color, axis=1)
                df_loc['radius'] = df_loc.apply(get_radius, axis=1)
                
                # ✅ 특정 업체의 초기 줌 레벨을 1.5로 고정하여 충돌 방지
                center_lat, center_lon, zoom_lvl = 35.0, 150.0, 1.5 
                if current_view != "전체 뷰":
                    target_df = df_loc[df_loc['type'] == target_type_key]
                    if not target_df.empty: 
                        center_lat, center_lon, zoom_lvl = target_df['lat'].mean(), target_df['lon'].mean(), (5.5 if len(target_df) > 1 else 9.0)
                
                # ✅ min_zoom=1.5 추가: 축소를 제한하여 가로 반복 생성 원천 차단
                view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=zoom_lvl, min_zoom=1.5, max_zoom=15, pitch=0, transition_duration=1200)
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
                    pickable=True
                )
                
                # ✅ 줌, 마우스 드래그 조작 활성화 (controller=True)
                view = pdk.View(type="MapView", controller=True, repeat=False)
                st.pydeck_chart(pdk.Deck(map_style="light", initial_view_state=view_state, views=[view], layers=[layer], tooltip={"text": "{name}\n{address}"}), height=600)

        with text_col:
            st.markdown("<p style='color:#C4A47C !important; font-weight:800; font-size:15px; margin-bottom:10px;'>🖱️ 거점을 클릭하면 지도가 이동합니다.</p>", unsafe_allow_html=True)
            st.button("🌍 전체 뷰\n모든 거점 확인", on_click=set_view, args=("전체 뷰",), use_container_width=True, type="primary")
            
            for typ, btn_label in [("hq", "🏢 국내(본사)"), ("kr", "🏭 국내(지사)"), ("gl_cn", "🌐 해외(중국)"), ("gl_us", "🌎 해외(북미)")]:
                if any(loc.get("type") == typ for loc in selected.get("locations", [])):
                    names = ", ".join([loc["name"] for loc in selected["locations"] if loc["type"] == typ])
                    st.button(f"{btn_label}\n{names}", on_click=set_view, args=(btn_label,), use_container_width=True, type="primary")
