import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import pydeck as pdk
import urllib.request
import ssl
import base64
import re
from datetime import datetime

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

            // ✅ 마우스 휠로 확대/축소
            container.addEventListener('wheel', (e) => {{
                let zoomSpeed = 0.002;
                scale += e.deltaY * -zoomSpeed;
                scale = Math.min(Math.max(0.5, scale), 10); 
                img.style.transform = `translate(${{translateX}}px, ${{translateY}}px) scale(${{scale}})`;
            }}, {{ passive: true }}); 

            // 마우스 클릭 드래그로 이미지 이동
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


# 🚀 팝업 모달 함수 정의
if hasattr(st, "dialog"):
    @st.dialog("🔍 이미지 확대 보기", width="large")
    def show_popup_modal(img_data):
        render_zoomable_image(img_data)
elif hasattr(st, "experimental_dialog"):
    @st.experimental_dialog("🔍 이미지 확대 보기", width="large")
    def show_popup_modal(img_data):
        render_zoomable_image(img_data)
else:
    def show_popup_modal(img_data):
        st.session_state.popup_img = img_data
        st.rerun()

# 2. 테마 CSS 설정
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

/* 사이드바 영역 CSS 추가 */
[data-testid="stSidebar"] { 
    background-color: #Fdfcfb !important; 
    border-right: 1px solid #E5E0D8 !important; 
}
[data-testid="stSidebar"] h3 { font-size: 24px !important; }

div[data-testid="stSidebar"] button[data-baseweb="tab"] p,
div[data-testid="stSidebar"] button[data-baseweb="tab"] span,
div[data-testid="stSidebar"] button[data-baseweb="tab"] div[data-testid="stMarkdownContainer"] p {
    font-size: 17.5px !important; 
    font-weight: 900 !important;
    color: #2C2A29 !important;
}
div[data-testid="stSidebar"] button[data-baseweb="tab"] { padding: 10px 5px !important; }

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
[data-testid="stSidebar"] .stTextInput input { font-size: 16px !important; }

[data-testid="stMetricLabel"], 
[data-testid="stMetricLabel"] div,
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] span,
[data-testid="stMetricLabel"] label {
    font-size: 19px !important; 
    font-weight: 900 !important;
    color: #2C2A29 !important;
}

/* ✅ 다크모드 대응 글씨체 색상 고정 (중요) */
.section-header { 
    color: #2C2A29 !important; text-align: center; font-weight: 900; font-size: 20px; 
    border-bottom: 3px solid #E5E0D8; padding-bottom: 12px; margin-bottom: 15px; 
}
.img-container { 
    height: 220px; background: #ffffff; border: 1px solid #E5E0D8; 
    border-radius: 12px; padding: 15px; display: flex; 
    justify-content: center; align-items: center; margin-bottom: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.img-container img { max-width: 100%; max-height: 100%; object-fit: contain; }

/* 태그 및 구분선 CSS */
.unified-tag { 
    font-size: 15.5px; font-weight: 800; color: #4A4441 !important; text-align: center; 
    background: #F8F9FA; padding: 12px 18px; border-radius: 30px; 
    border: 1px solid #D1D5DB; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}

/* 텍스트 및 기본 요소 */
h2, h3, h4, p, span, label, li { color: #2C2A29 !important; }
.main-title { font-size: 34px !important; font-weight: 900 !important; color: #ffffff !important; margin: 0 !important; line-height: 1.2 !important; letter-spacing: -1px !important; }
.section-title { font-size: 24px; font-weight: 900; color: #2C2A29 !important; margin-top: 45px; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; padding-bottom: 12px; border-bottom: 3px solid #E5E0D8; }
.section-num { color: #C4A47C; font-size: 28px; font-weight: 900; letter-spacing: -1px; }

/* ✅ 회사 개요 박스 다크모드 대응 텍스트 고정 (!important 추가) */
.desc-box { 
    background-color: #FDFCFB; border: 1px solid #E5E0D8; border-radius: 12px; 
    padding: 30px; border-left: 6px solid #C4A47C; font-size: 17px; 
    line-height: 1.8; font-weight: 400; color: #2C2A29 !important; 
}

/* 일반 버튼 스타일 */
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

/* 거점 표시 전용 버튼 스타일 */
div.stButton > button[kind="primary"] {
    padding: 14px 20px !important; 
    border-radius: 12px !important;
}
div.stButton > button[kind="primary"] p {
    font-size: 17.5px !important; 
}

/* 메인 타이틀 버튼 스타일 */
div.element-container:has(.main-title-anchor) { 
    height: 0px !important; margin: 0 !important; padding: 0 !important; overflow: hidden !important; 
}
div.element-container:has(.main-title-anchor) + div.element-container button {
    background-color: #2C2A29 !important; padding: 30px 40px !important; 
    border-radius: 12px !important; margin-bottom: 20px !important; 
    border: none !important; border-bottom: 4px solid #C4A47C !important;
    width: 100% !important; text-align: left !important;
    display: block !important; box-shadow: none !important; cursor: pointer !important;
}
div.element-container:has(.main-title-anchor) + div.element-container button:hover { background-color: #353332 !important; }
div.element-container:has(.main-title-anchor) + div.element-container button p {
    font-size: 34px !important; font-weight: 900 !important; color: #ffffff !important; 
    margin: 0 !important; line-height: 1.2 !important; letter-spacing: -1px !important; text-align: left !important;
}

/* 홈페이지 링크 배지 */
.hp-link{
    display: inline-flex; align-items: center; gap: 8px;
    padding: 7px 16px 7px 13px; background: #FDFCFB;
    border: 1px solid #E5E0D8; border-left: 3px solid #C4A47C;
    border-radius: 30px; font-size: 15px; font-weight: 800;
    text-decoration: none !important; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    transition: all 0.2s ease; white-space: nowrap;
}
.hp-link span{ color: #8A6F43 !important; }
.hp-link:hover{ background: #ffffff; border-color: #C4A47C; box-shadow: 0 6px 12px rgba(196,164,124,0.20); transform: translateY(-2px); }
.hp-link:hover span{ color: #2C2A29 !important; }
.hp-arw{ font-size: 13px; opacity: 0.7; }
.hp-link:hover .hp-arw{ opacity: 1; }

/* 주요 고객사 매입 비중 */
.cust-box { padding: 24px 28px; background: #FDFCFB; border: 1px solid #E5E0D8; border-radius: 12px; margin-bottom: 10px; }
.cust-stack { display: flex; height: 56px; border-radius: 8px; overflow: hidden; border: 1px solid #E5E0D8; }
.cust-seg { display: flex; align-items: center; justify-content: center; font-size: 18px !important; font-weight: 900 !important; letter-spacing: -0.5px; white-space: nowrap; overflow: hidden; transition: filter 0.2s ease; cursor: default; }
.cust-seg.seg-md { font-size: 15px !important; }
.cust-seg.seg-sm { font-size: 13px !important; }
.cust-seg:hover { filter: brightness(1.08); }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. 데이터 및 변환 함수
CUSTOMER_TOP_N = 4                      
CUSTOMER_SHOW_ETC = False               

CUSTOMER_PALETTE = [                    
    ("#5A3D22", "#ffffff"),  
    ("#9A7B54", "#ffffff"),  
    ("#D1BA9C", "#2C2A29"),  
    ("#F4EBE3", "#2C2A29"),  
]

ETC_COLOR = ("#EFE9DE", "#2C2A29")      

def _parse_ratio(v):
    if v is None or isinstance(v, bool): return None
    if isinstance(v, (int, float)): return float(v)
    m = re.search(r"(\d+(?:\.\d+)?)", str(v).replace(",", ""))
    return float(m.group(1)) if m else None

def _is_etc(name):
    return name.strip() in ("기타", "기타고객", "기타 고객사", "기타 등", "ETC", "etc", "Others")

def _fmt_ratio(v):
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}"

def _short_name(name):
    s = str(name).strip()
    s = re.sub(r"^$\s*주\s*$\s*|^㈜\s*|^주식회사\s*", "", s)
    s = re.sub(r"\s*$\s*주\s*$$|\s*㈜$|\s*주식회사$", "", s)
    return s.strip() or str(name).strip()

def _legacy_customer_tags(names):
    tags_html = "<div style='display:flex; flex-wrap:wrap; gap:15px;'>"
    for comp in names:
        tags_html += (
            "<div style='padding:14px 28px; background:#ffffff; border:2px solid #C4A47C;"
            " border-radius:40px; font-size:18px; font-weight:900; color:#2C2A29 !important;" 
            " box-shadow:0 6px 12px rgba(196,164,124,0.15); display:flex; align-items:center;'>"
            f"🤝 {comp}</div>"
        )
    tags_html += "</div>"
    return f"<div class='cust-box'>{tags_html}</div>"

def get_customer_tags_html(customers):
    if not customers: return "<p style='color:#8A817C; font-size:15px;'>등록된 주요 고객사 정보가 없습니다.</p>"
    if not isinstance(customers, dict): return _legacy_customer_tags(list(customers))

    items = [(str(k).strip(), _parse_ratio(v)) for k, v in customers.items()]
    rated = [(k, v) for k, v in items if v is not None and v > 0 and not _is_etc(k)]

    if not rated: return _legacy_customer_tags([k for k, _ in items])

    rated.sort(key=lambda x: -x[1])
    top = rated[:CUSTOMER_TOP_N]

    rows = []
    if CUSTOMER_SHOW_ETC:
        total_all = sum(v for _, v in rated)
        base = total_all if total_all > 100.0 else 100.0
        for i, (name, val) in enumerate(top):
            bg, fg = CUSTOMER_PALETTE[i % len(CUSTOMER_PALETTE)]
            rows.append((name, val, val / base * 100.0, bg, fg, ""))
        etc_val = sum(v for _, v in rated[CUSTOMER_TOP_N:]) + max(0.0, 100.0 - total_all)
        if etc_val > 0.5:
            rows.append(("기타", etc_val, etc_val / base * 100.0, ETC_COLOR[0], ETC_COLOR[1], ""))
    else:
        base = sum(v for _, v in top) or 100.0
        for i, (name, val) in enumerate(top):
            bg, fg = CUSTOMER_PALETTE[i % len(CUSTOMER_PALETTE)]
            rows.append((name, val, val / base * 100.0, bg, fg, ""))

    segs = ""
    for name, val, w, bg, fg, tip in rows:
        disp = _short_name(name)
        cls = "cust-seg"
        if w >= 26: label = f"{disp} {_fmt_ratio(val)}%"
        elif w >= 13: label = f"{disp} {_fmt_ratio(val)}%"; cls += " seg-md"
        elif w >= 3: label = f"{_fmt_ratio(val)}%"; cls += " seg-sm"
        else: label = ""
        title = tip or f"{name} {_fmt_ratio(val)}%"
        
        if label:
            label_html = f"""
            <svg width="100%" height="100%" style="min-width: 50px;">
                <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{fg}" font-size="inherit" font-weight="900" font-family="inherit">
                    {label}
                </text>
            </svg>
            """
        else:
            label_html = ""
        segs += f"<div class='{cls}' style='width:{w:.4f}%; background:{bg};' title='{title}'>{label_html}</div>"

    return f"<div class='cust-box'><div class='cust-stack'>{segs}</div></div>"

def get_homepage_link_html(company):
    url = str(company.get("homepage", "") or "").strip()
    if not url or url == "-": return ""
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

if not hasattr(st, "dialog") and not hasattr(st, "experimental_dialog"):
    if st.session_state.popup_img:
        st.markdown("<hr style='border: 2px solid #2C2A29;'>", unsafe_allow_html=True)
        pop_col1, pop_col2 = st.columns([8, 2])
        with pop_col1: st.markdown("<h3 style='margin-top:0;'>🔍 이미지 확대 보기</h3>", unsafe_allow_html=True)
        with pop_col2:
            if st.button("❌ 닫기", use_container_width=True, key="fallback_close"):
                st.session_state.popup_img = None
                st.rerun()
        render_zoomable_image(st.session_state.popup_img)
        st.markdown("<hr style='border: 2px solid #2C2A29; margin-bottom: 40px;'>", unsafe_allow_html=True)

# 4. 초기 데이터 로드 
if "suppliers" not in st.session_state: st.session_state.suppliers = suppliers_data
if "excel_img_data" not in st.session_state: st.session_state.excel_img_data = excel_img_data
suppliers = st.session_state.suppliers

# 5. 헤더 및 사이드바 
st.markdown("<div class='main-title-anchor'></div>", unsafe_allow_html=True)

def go_to_main():
    st.session_state.selected_company = "🏠 종합 메인 화면"
    st.session_state.map_view = "전체 뷰"

st.button("🌍 글로벌 SCM 및 파트너사 인프라 분석", on_click=go_to_main, use_container_width=True)

with st.sidebar:
    st.markdown("<h3 style='color:#C4A47C !important; font-weight:900;'>🔍 상세 검색</h3>", unsafe_allow_html=True)
    
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
    for s in sorted(filtered, key=lambda x: x.get('name', '')): options_sidebar_map[s['name']] = s['name']
    options_list = list(options_sidebar_map.keys())

    if st.session_state.selected_company not in options_list: st.session_state.selected_company = "🏠 종합 메인 화면"

    selected_display_name = st.radio("", options_list, key="selected_company", on_change=reset_map_view, label_visibility="collapsed")
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
        def get_main_color(row): return [41, 128, 185, 220] if row.get('type') in ['hq', 'kr'] else [196, 164, 124, 220]
        df_all['color'] = df_all.apply(get_main_color, axis=1)

        view_state = pdk.ViewState(latitude=35.0, longitude=127.0, zoom=1.5, min_zoom=1.5, max_zoom=15, pitch=0)
        layer = pdk.Layer("ScatterplotLayer", data=df_all, get_position='[lon, lat]', get_fill_color='color', get_line_color=[255, 255, 255], stroked=True, line_width_min_pixels=1, get_radius=100000, radius_min_pixels=6, radius_max_pixels=15, pickable=True)
        view = pdk.View(type="MapView", controller=True, repeat=False)
        st.pydeck_chart(pdk.Deck(map_style="light", initial_view_state=view_state, views=[view], layers=[layer], tooltip={"text": "{name}\n{address}"}))

elif selected_name:
    selected = next((s for s in filtered if s["name"] == selected_name), None)
    if selected:
        badge_html = f"<div style='margin-bottom:25px; display:flex; align-items:center; gap:10px; flex-wrap:wrap;'><h2 style='margin:0; font-weight:900; font-size:42px; letter-spacing:-1px;'>{selected.get('name', '')}</h2><span style='background:#C4A47C; color:#ffffff !important; padding:6px 14px; font-size:16px; font-weight:900; border-radius:6px;'>{selected.get('industry', '')}</span>"
        if selected.get('sub_industry'): badge_html += f"<span style='background:#FDFCFB; border:1px solid #E5E0D8; color:#8A817C !important; padding:5px 12px; font-size:14px; font-weight:700; border-radius:4px;'>{selected.get('sub_industry', '')}</span>"
        st.markdown(badge_html + "</div>", unsafe_allow_html=True)

        st.markdown(
            "<div class='section-title'><span class='section-num'>01.</span> <span>기업 개요</span>"
            f"<span style='margin-left:auto;'>{get_homepage_link_html(selected)}</span>"
            "</div>",
            unsafe_allow_html=True
        )
        
        desc_text = str(selected.get('desc', '등록된 기업 개요가 없습니다.')).replace('\n', '<br>')
        st.markdown(f"<div class='desc-box'>📖 {desc_text}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'><span class='section-num'>02.</span> 핵심 역량 및 품질 인증</div>", unsafe_allow_html=True)
        company_images = st.session_state.excel_img_data.get(selected['name'], {"prod_imgs": [], "cert_imgs": []})

        # ==========================================
        # 🔔 [추가] 인증서 유효기간 상태 계산 함수
        # ==========================================
        def check_cert_status(expiry_str):
            if not expiry_str or expiry_str == "-":
                return "none", "기한없음", "#8A817C"
            try:
                today = datetime.today()
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                days_left = (expiry_date - today).days

                if days_left < 0:
                    return "expired", "만료됨", "#DC2626"      # 빨강
                elif days_left <= 90:
                    return "warning", f"{days_left}일 남음", "#F59E0B" # 주황 (90일 이내 임박)
                else:
                    return "valid", "유효", "#10B981"         # 초록
            except ValueError:
                return "error", "날짜오류", "#8A817C"

        # ==========================================
        # 🔔 [추가] 만료/임박 알림 배너 렌더링
        # ==========================================
        all_certs = selected.get('certs', [])
        expired_list = []
        warning_list = []
        
        for cert in all_certs:
            # 문자열일 경우 하위 호환성 유지, 딕셔너리일 경우 만료일 확인
            if isinstance(cert, dict) and cert.get("expiry"):
                status, _, _ = check_cert_status(cert["expiry"])
                if status == "expired":
                    expired_list.append(cert["name"])
                elif status == "warning":
                    warning_list.append(cert["name"])
        
        if expired_list or warning_list:
            alert_html = """
            <div style='padding: 16px 20px; border-radius: 12px; margin-bottom: 25px; background-color: #FEF2F2; border: 1px solid #FCA5A5;'>
                <div style='font-size: 16px; font-weight: 900; color: #DC2626; margin-bottom: 8px;'>
                    ⚠️ 인증서 유효기간 확인 요망
                </div>
            """
            if expired_list:
                alert_html += f"<div style='font-size: 14.5px; color: #991B1B;'><b>🔴 갱신 필요 (만료됨):</b> {', '.join(expired_list)}</div>"
            if warning_list:
                alert_html += f"<div style='font-size: 14.5px; color: #9A3412; margin-top: 4px;'><b>🟠 만료 임박 (90일 이내):</b> {', '.join(warning_list)}</div>"
            alert_html += "</div>"
            st.markdown(alert_html, unsafe_allow_html=True)

        col_left, col_right = st.columns(2)

        # ✅ 왼쪽 : 핵심 생산 품목 
        with col_left:
            st.markdown("<div class='section-header'>🌟 핵심 생산 품목</div>", unsafe_allow_html=True)
            prod_list = company_images.get("prod_imgs", [])
            
            all_tags = []
            for prod_name in selected.get('products', []):
                tags = [t.strip() for t in prod_name.replace(" / ", "/").split("/")]
                all_tags.extend([t for t in tags if t])
                
            if not prod_list and not all_tags:
                st.info("등록된 품목 및 이미지가 없습니다.")
            else:
                num_cols = max(len(prod_list), len(all_tags), 1)
                img_cols = st.columns(num_cols)
                
                for idx in range(num_cols):
                    with img_cols[idx]:
                        # 1. 이미지 및 버튼 렌더링
                        if idx < len(prod_list):
                            img_data = get_base64_image(prod_list[idx])
                            if img_data:
                                st.markdown(f"<div class='img-container'><img src='data:image/jpeg;base64,{img_data}'></div>", unsafe_allow_html=True)
                                if st.button("🔍 확대 보기", key=f"btn_prod_{idx}", use_container_width=True): show_popup_modal(img_data)
                            else:
                                st.markdown("<div class='img-container' style='background:#f8f9fa;'><span style='color:#888;'>로드 실패</span></div>", unsafe_allow_html=True)
                                st.markdown("""<div style='visibility: hidden; margin-bottom: 16px;'><div style='padding: 8px 14px; border: 1px solid transparent; font-size: 14px; line-height: 1.5;'>🔍 확대 보기</div></div>""", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='img-container' style='visibility:hidden;'></div>", unsafe_allow_html=True)
                            st.markdown("""<div style='visibility: hidden; margin-bottom: 16px;'><div style='padding: 8px 14px; border: 1px solid transparent; font-size: 14px; line-height: 1.5;'>🔍 확대 보기</div></div>""", unsafe_allow_html=True)
                            
                        # 2. 점선 및 태그(품목명) 렌더링
                        tag_text = all_tags[idx] if idx < len(all_tags) else ""
                        if tag_text:
                            st.markdown(
                                f"<div style='border-top: 2px dashed #E5E0D8; margin-top: 15px; padding-top: 15px; text-align: center;'>"
                                f"<div class='unified-tag' style='display: inline-block; white-space: normal; word-break: keep-all; line-height: 1.3;'>{tag_text}</div>"
                                f"</div>", unsafe_allow_html=True
                            )
                        else:
                            st.markdown("<div style='border-top: 2px dashed #E5E0D8; margin-top: 15px; padding-top: 15px; text-align: center;'><div class='unified-tag' style='visibility:hidden;'>-</div></div>", unsafe_allow_html=True)


        # ✅ 오른쪽 : 품질 및 ESG 인증 (상태 배지 추가됨)
        with col_right:
            st.markdown("<div class='section-header'>🏅 품질 및 ESG 인증</div>", unsafe_allow_html=True)
            cert_list = company_images.get("cert_imgs", [])
            
            if not cert_list and not all_certs:
                st.info("등록된 인증서 및 이미지가 없습니다.")
            else:
                num_cols_cert = max(len(cert_list), len(all_certs), 1)
                cert_cols = st.columns(num_cols_cert)
                
                for idx in range(num_cols_cert):
                    with cert_cols[idx]:
                        # 1. 이미지 및 버튼 렌더링
                        if idx < len(cert_list):
                            cert_data = get_base64_image(cert_list[idx])
                            if cert_data:
                                st.markdown(f"<div class='img-container'><img src='data:image/jpeg;base64,{cert_data}'></div>", unsafe_allow_html=True)
                                if st.button("🔍 확대 보기", key=f"btn_cert_{idx}", use_container_width=True): show_popup_modal(cert_data)
                            else:
                                st.markdown("<div class='img-container' style='background:#f8f9fa;'><span style='color:#888;'>로드 실패</span></div>", unsafe_allow_html=True)
                                st.markdown("""<div style='visibility: hidden; margin-bottom: 16px;'><div style='padding: 8px 14px; border: 1px solid transparent; font-size: 14px; line-height: 1.5;'>🔍 확대 보기</div></div>""", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='img-container' style='visibility:hidden;'></div>", unsafe_allow_html=True)
                            st.markdown("""<div style='visibility: hidden; margin-bottom: 16px;'><div style='padding: 8px 14px; border: 1px solid transparent; font-size: 14px; line-height: 1.5;'>🔍 확대 보기</div></div>""", unsafe_allow_html=True)
                            
                        # 2. 점선 및 태그(인증서명, 유효기간) 렌더링
                        cert_info = all_certs[idx] if idx < len(all_certs) else None
                        
                        if cert_info:
                            # 문자열 형태일 경우 호환성 지원 (이전 방식)
                            if isinstance(cert_info, str):
                                display_html = cert_info
                            # 딕셔너리 형태일 경우 (유효기간 포함)
                            else:
                                cert_name = cert_info.get("name", "")
                                expiry = cert_info.get("expiry", "")
                                status, badge_text, color = check_cert_status(expiry)
                                
                                if expiry:
                                    # ✅ 수정된 부분: color: white !important; 와 color: #8A817C !important; 추가
                                    badge_html = f"<span style='background-color:{color}; color: white !important; padding:2px 6px; border-radius:4px; font-size:12px; margin-left:6px; vertical-align:middle;'>{badge_text}</span><br><span style='font-size:13px; color: #8A817C !important; display:block; margin-top:4px;'>만료일: {expiry}</span>"
                                else:
                                    badge_html = ""
                                    
                                display_html = f"<span>{cert_name}</span>{badge_html}"

                            st.markdown(
                                f"<div style='border-top: 2px dashed #E5E0D8; margin-top: 15px; padding-top: 15px; text-align: center;'>"
                                f"<div class='unified-tag' style='display: inline-block; white-space: normal; word-break: keep-all; line-height: 1.3;'>{display_html}</div>"
                                f"</div>", unsafe_allow_html=True
                            )
                        else:
                            st.markdown("<div style='border-top: 2px dashed #E5E0D8; margin-top: 15px; padding-top: 15px; text-align: center;'><div class='unified-tag' style='visibility:hidden;'>-</div></div>", unsafe_allow_html=True)


        st.markdown("<div class='section-title' style='margin-top: 40px;'><span class='section-num'>03.</span> 주요 매출처 및 매입 비중</div>", unsafe_allow_html=True)
        st.markdown(get_customer_tags_html(selected.get('customers', [])), unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top: 50px;'><span class='section-num'>04.</span> 글로벌 네트워크</div>", unsafe_allow_html=True)
        
        map_col, text_col = st.columns([2.5, 1]) 
        df_loc = pd.DataFrame(selected.get("locations", []))

        with map_col:
            current_view = st.session_state.map_view
            target_type_key = map_view_mapping.get(current_view, "all")

            def get_color(row):
                is_domestic = row.get('type') in ['hq', 'kr']
                active_color = [41, 128, 185, 220] if is_domestic else [196, 164, 124, 220]
                dim_color = [200, 200, 200, 100]
                
                if current_view == "전체 뷰": return active_color
                if row['type'] == target_type_key: return active_color
                return dim_color

            def get_radius(row):
                if current_view == "전체 뷰": return map_radius_settings["all_view"]
                if row['type'] == target_type_key: return map_radius_settings["highlighted"]
                return map_radius_settings["dimmed"]

            if not df_loc.empty:
                df_loc['color'] = df_loc.apply(get_color, axis=1)
                df_loc['radius'] = df_loc.apply(get_radius, axis=1)
                
                center_lat, center_lon, zoom_lvl = 35.0, 150.0, 1.5 
                if current_view != "전체 뷰":
                    target_df = df_loc[df_loc['type'] == target_type_key]
                    if not target_df.empty: 
                        center_lat, center_lon, zoom_lvl = target_df['lat'].mean(), target_df['lon'].mean(), (5.5 if len(target_df) > 1 else 9.0)
                
                view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=zoom_lvl, min_zoom=1.5, max_zoom=15, pitch=0, transition_duration=1200)
                layer = pdk.Layer("ScatterplotLayer", data=df_loc, get_position='[lon, lat]', get_fill_color='color', get_line_color=[255, 255, 255], stroked=True, line_width_min_pixels=2, get_radius='radius', radius_min_pixels=6, radius_max_pixels=30, pickable=True)
                view = pdk.View(type="MapView", controller=True, repeat=False)
                st.pydeck_chart(pdk.Deck(map_style="light", initial_view_state=view_state, views=[view], layers=[layer], tooltip={"text": "{name}\n{address}"}), height=600)

        with text_col:
            st.markdown("<p style='color:#C4A47C !important; font-weight:800; font-size:15px; margin-bottom:10px;'>🖱️ 거점을 클릭하면 지도가 이동합니다.</p>", unsafe_allow_html=True)
            st.button("🌍 전체 뷰\n모든 거점 확인", on_click=set_view, args=("전체 뷰",), use_container_width=True, type="primary")
            
            for typ, btn_label in [("hq", "🏢 국내(본사)"), ("kr", "🏭 국내(지사)"), ("gl_cn", "🌐 해외(중국)"), ("gl_us", "🌎 해외(북미)")]:
                if any(loc.get("type") == typ for loc in selected.get("locations", [])):
                    names = ", ".join([loc["name"] for loc in selected["locations"] if loc["type"] == typ])
                    st.button(f"{btn_label}\n{names}", on_click=set_view, args=(btn_label,), use_container_width=True, type="primary")
