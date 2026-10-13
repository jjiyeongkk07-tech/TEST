# app.py
import streamlit as st
import pandas as pd
import pydeck as pdk
import urllib.request
import ssl
import base64

# 🌟 data.py 파일에서 데이터(업체정보 및 글로벌 위치 정보) 가져오기
from data import suppliers_data, excel_img_data

# 1. 페이지 설정
st.set_page_config(page_title="글로벌 SCM 분석", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

if "map_view" not in st.session_state:
    st.session_state.map_view = "전체 뷰"
if "popup_img" not in st.session_state:
    st.session_state.popup_img = None
if "popup_title" not in st.session_state:
    st.session_state.popup_title = ""

def set_view(view):
    st.session_state.map_view = view

def reset_map_view():
    st.session_state.map_view = "전체 뷰"

# 2. 테마 CSS 설정 (깨짐 유발하던 박스 래퍼 모두 제거하고 깔끔하게 정돈)
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
[data-testid="stSidebar"] { background-color: #Fdfcfb !important; border-right: 1px solid #E5E0D8 !important; }

/* ✅ 완벽한 가로 정렬을 위한 내부 컴포넌트 높이 고정 */
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

/* ✅ 하단 태그 가로 정렬 (양쪽 모두 동일한 디자인 적용) */
.tag-wrap-box { 
    display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; 
    align-items: flex-start; padding-top: 20px; margin-top: 20px;
    border-top: 1px dashed #E5E0D8; min-height: 70px;
}
.unified-tag { 
    font-size: 14.5px; font-weight: 800; color: #4A4441; text-align: center; 
    background: #F8F9FA; padding: 10px 18px; border-radius: 30px; 
    border: 1px solid #D1D5DB; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    white-space: nowrap;
}

/* ✅ 텍스트 및 기본 요소 */
h2, h3, h4, p, span, label, li { color: #2C2A29 !important; }
.main-title { font-size: 34px !important; font-weight: 900 !important; color: #ffffff !important; margin: 0 !important; line-height: 1.2 !important; letter-spacing: -1px !important; }
.section-title { font-size: 24px; font-weight: 900; color: #2C2A29 !important; margin-top: 45px; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; padding-bottom: 12px; border-bottom: 3px solid #E5E0D8; }
.section-num { color: #C4A47C; font-size: 28px; font-weight: 900; letter-spacing: -1px; }
.desc-box { background-color: #FDFCFB; border: 1px solid #E5E0D8; border-radius: 12px; padding: 30px; border-left: 6px solid #C4A47C; font-size: 17px; line-height: 1.8; font-weight: 400; }

/* ✅ 깔끔한 버튼 스타일 */
div.stButton > button { background-color: #ffffff !important; border: 1px solid #E5E0D8 !important; border-radius: 8px !important; color: #4A4441 !important; font-weight: 700 !important; transition: all 0.2s ease !important; }
div.stButton > button:hover { border-color: #C4A47C !important; color: #C4A47C !important; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. 데이터 및 변환 함수
def get_customer_tags_html(customers):
    if not customers: return "<p style='color: #8A817C; font-size: 15px;'>등록된 주요 고객사 정보가 없습니다.</p>"
    tags_html = "<div style='display: flex; flex-wrap: wrap; gap: 15px;'>"
    customer_list = customers.keys() if isinstance(customers, dict) else customers
    for comp in customer_list:
        tags_html += f"<div style='padding: 14px 28px; background: #ffffff; border: 2px solid #C4A47C; border-radius: 40px; font-size: 18px; font-weight: 900; color: #2C2A29; box-shadow: 0 6px 12px rgba(196, 164, 124, 0.15); display: flex; align-items: center;'>🤝 {comp}</div>"
    tags_html += "</div>"
    return f"<div style='padding: 30px; background: #FDFCFB; border: 1px solid #E5E0D8; border-radius: 12px; margin-bottom: 10px;'>{tags_html}</div>"

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


# 4. 초기 데이터 로드 
if "suppliers" not in st.session_state: st.session_state.suppliers = suppliers_data
if "excel_img_data" not in st.session_state: st.session_state.excel_img_data = excel_img_data
suppliers = st.session_state.suppliers

# 5. 헤더 및 사이드바 
st.markdown("<div style='background-color: #2C2A29; padding: 30px 40px; border-radius: 12px; margin-bottom: 20px; border-bottom: 4px solid #C4A47C;'><div class='main-title'>🌍 글로벌 SCM 및 파트너사 인프라 분석</div></div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h3 style='color:#C4A47C !important; font-weight:900;'>🔍 상세 검색</h3>", unsafe_allow_html=True)
    all_countries_set = set()
    for s in suppliers:
        for loc in s.get("locations", []): all_countries_set.add(loc["country"])
    industry_list = ["전체"] + list(set(s.get("industry", "미분류") for s in suppliers if s.get("industry") != "미분류"))
    country_list = ["전체"] + list(all_countries_set)

    tab_industry, tab_company, tab_country = st.tabs(["🏷️ 업종", "🏢 업체", "🌍 국가"])
    with tab_industry: selected_industry = st.selectbox("조회할 업종을 선택하세요", industry_list, on_change=reset_map_view, label_visibility="collapsed")
    with tab_company: search_term = st.text_input("업체명을 입력하세요", placeholder="예: 한성전장", label_visibility="collapsed").strip()
    with tab_country: selected_country = st.selectbox("조회할 국가를 선택하세요", country_list, on_change=reset_map_view, label_visibility="collapsed")

    filtered = suppliers
    if selected_industry != "전체": filtered = [s for s in filtered if s.get("industry") == selected_industry]
    if selected_country != "전체": filtered = [s for s in filtered if any(loc.get("country") == selected_country for loc in s.get("locations", []))]
    if search_term: filtered = [s for s in filtered if search_term.lower() in s.get("name", "").lower()]

    st.markdown("<hr style='border-color: #E5E0D8; margin: 20px 0;'>", unsafe_allow_html=True)
    options_sidebar_map = {"🏠 종합 메인 화면": "🏠 종합 메인 화면"}
    for s in filtered: options_sidebar_map[s['name']] = s['name']
    selected_display_name = st.radio("📊 분석할 업체 선택", list(options_sidebar_map.keys()), on_change=reset_map_view)
    selected_name = options_sidebar_map[selected_display_name]


# 🚀 이미지 팝업(모달) 렌더링 영역 (안전하게 화면 상단에 띄움)
if st.session_state.popup_img:
    st.markdown("<hr style='border: 2px solid #2C2A29;'>", unsafe_allow_html=True)
    pop_col1, pop_col2 = st.columns([8, 2])
    with pop_col1:
        st.markdown(f"<h3 style='margin-top:0;'>🔍 {st.session_state.popup_title}</h3>", unsafe_allow_html=True)
    with pop_col2:
        if st.button("❌ 닫기", use_container_width=True):
            st.session_state.popup_img = None
            st.rerun()
    st.markdown(f"<div style='text-align: center; background:#F9F8F6; padding: 20px; border-radius: 12px; margin-bottom: 20px;'><img src='data:image/jpeg;base64,{st.session_state.popup_img}' style='max-width: 100%; border-radius: 8px;'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 2px solid #2C2A29; margin-bottom: 40px;'>", unsafe_allow_html=True)


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
        view_state = pdk.ViewState(latitude=35.0, longitude=127.0, zoom=1.5, pitch=0)
        layer = pdk.Layer("ScatterplotLayer", data=df_all, get_position='[lon, lat]', get_fill_color=[196, 164, 124, 200], get_line_color=[255, 255, 255], stroked=True, line_width_min_pixels=1, get_radius=100000, radius_min_pixels=6, radius_max_pixels=15, pickable=True)
        st.pydeck_chart(pdk.Deck(map_style="light", initial_view_state=view_state, layers=[layer], tooltip={"text": "{name}\n{address}"}))

elif selected_name:
    selected = next((s for s in filtered if s["name"] == selected_name), None)
    if selected:
        badge_html = f"<div style='margin-bottom:25px; display:flex; align-items:center; gap:10px; flex-wrap:wrap;'><h2 style='margin:0; font-weight:900; font-size:42px; letter-spacing:-1px;'>{selected.get('name', '')}</h2><span style='background:#C4A47C; color:#ffffff !important; padding:6px 14px; font-size:16px; font-weight:900; border-radius:6px;'>{selected.get('industry', '')}</span>"
        if selected.get('sub_industry'): badge_html += f"<span style='background:#FDFCFB; border:1px solid #E5E0D8; color:#8A817C !important; padding:5px 12px; font-size:14px; font-weight:700; border-radius:4px;'>{selected.get('sub_industry', '')}</span>"
        st.markdown(badge_html + "</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'><span class='section-num'>01.</span> 기업 개요</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='desc-box'>📖 {selected.get('desc', '등록된 기업 개요가 없습니다.')}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'><span class='section-num'>02.</span> 핵심 역량 및 품질 인증</div>", unsafe_allow_html=True)
        company_images = st.session_state.excel_img_data.get(selected['name'], {"prod_imgs": [], "cert_imgs": []})

        # 🚀 좌우 레이아웃 완전 일치화 (똑같은 컴포넌트 순서 적용)
        col_left, col_right = st.columns(2)

        # ---------------- 좌측: 핵심 생산 품목 ----------------
        with col_left:
            st.markdown("<div class='section-header'>🌟 핵심 생산 품목</div>", unsafe_allow_html=True)
            
            # 1. 이미지 및 버튼 영역
            prod_list = company_images.get("prod_imgs", [])
            if prod_list:
                img_cols = st.columns(len(prod_list))
                for idx, b64_img in enumerate(prod_list):
                    with img_cols[idx]:
                        img_data = get_base64_image(b64_img)
                        if img_data:
                            st.markdown(f"<div class='img-container'><img src='data:image/jpeg;base64,{img_data}'></div>", unsafe_allow_html=True)
                            if st.button("🔍 확대 보기", key=f"btn_prod_{idx}", use_container_width=True):
                                st.session_state.popup_img = img_data
                                st.session_state.popup_title = f"{selected['name']} - 핵심 생산 품목"
                                st.rerun()
            else:
                st.info("등록된 이미지가 없습니다.")
                
            # 2. 태그 영역 (하단에 공통으로 가로 배치)
            all_tags = []
            for prod_name in selected.get('products', []):
                tags = [t.strip() for t in prod_name.replace(" / ", "/").split("/")]
                all_tags.extend([t for t in tags if t])
                
            if all_tags:
                tags_html = "".join([f"<div class='unified-tag'>{t}</div>" for t in all_tags])
                st.markdown(f"<div class='tag-wrap-box'>{tags_html}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='tag-wrap-box'><div class='unified-tag' style='visibility:hidden;'>-</div></div>", unsafe_allow_html=True)


        # ---------------- 우측: 품질 및 ESG 인증 ----------------
        with col_right:
            st.markdown("<div class='section-header'>🏅 품질 및 ESG 인증</div>", unsafe_allow_html=True)
            
            # 1. 이미지 및 버튼 영역
            cert_list = company_images.get("cert_imgs", [])
            if cert_list:
                cert_cols = st.columns(len(cert_list))
                for idx, cert_url in enumerate(cert_list):
                    with cert_cols[idx]:
                        cert_data = get_base64_image(cert_url)
                        if cert_data:
                            st.markdown(f"<div class='img-container'><img src='data:image/jpeg;base64,{cert_data}'></div>", unsafe_allow_html=True)
                            if st.button("🔍 확대 보기", key=f"btn_cert_{idx}", use_container_width=True):
                                st.session_state.popup_img = cert_data
                                st.session_state.popup_title = f"{selected['name']} - 품질 및 ESG 인증"
                                st.rerun()
            else:
                st.info("등록된 인증서 이미지가 없습니다.")
            
            # 2. 태그 영역 (하단에 공통으로 가로 배치)
            if selected.get('certs'):
                badges = "".join([f"<div class='unified-tag'>{c}</div>" for c in selected['certs']])
                st.markdown(f"<div class='tag-wrap-box'>{badges}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='tag-wrap-box'><div class='unified-tag' style='visibility:hidden;'>-</div></div>", unsafe_allow_html=True)


        st.markdown("<div class='section-title' style='margin-top: 40px;'><span class='section-num'>03.</span> 주요 고객사</div>", unsafe_allow_html=True)
        st.markdown(get_customer_tags_html(selected.get('customers', [])), unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top: 50px;'><span class='section-num'>04.</span> 글로벌 네트워크</div>", unsafe_allow_html=True)
        
        map_col, text_col = st.columns([2.5, 1]) 
        df_loc = pd.DataFrame(selected.get("locations", []))

        with map_col:
            current_view = st.session_state.map_view
            def get_color(row):
                hi_colors = {'hq': [220, 38, 38, 255], 'kr': [37, 99, 235, 255], 'gl_cn': [16, 185, 129, 255], 'gl_us': [245, 158, 11, 255]} 
                if current_view == "전체 뷰": return [196, 164, 124, 220]
                elif current_view == "🏢 국내(본사)" and row['type'] == 'hq': return hi_colors['hq']
                elif current_view == "🏭 국내(지사)" and row['type'] == 'kr': return hi_colors['kr']
                elif current_view == "🌐 해외(중국)" and row['type'] == 'gl_cn': return hi_colors['gl_cn']
                elif current_view == "🌎 해외(북미)" and row['type'] == 'gl_us': return hi_colors['gl_us']
                return [148, 163, 184, 100]

            def get_radius(row):
                if current_view == "전체 뷰": return 120000
                if row['type'] in ['hq', 'kr', 'gl_cn', 'gl_us'] and current_view != "전체 뷰": return 300000
                return 40000 

            if not df_loc.empty:
                df_loc['color'] = df_loc.apply(get_color, axis=1)
                df_loc['radius'] = df_loc.apply(get_radius, axis=1)
                
                center_lat, center_lon, zoom_lvl = 35.0, 150.0, 1.0 
                if current_view != "전체 뷰":
                    target_type = 'hq' if "본사" in current_view else ('kr' if "지사" in current_view else ('gl_cn' if "중국" in current_view else 'gl_us'))
                    target_df = df_loc[df_loc['type'] == target_type]
                    if not target_df.empty: center_lat, center_lon, zoom_lvl = target_df['lat'].mean(), target_df['lon'].mean(), (5.5 if len(target_df) > 1 else 9.0)
                
                view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=zoom_lvl, pitch=0, transition_duration=1200)
                layer = pdk.Layer("ScatterplotLayer", data=df_loc, get_position='[lon, lat]', get_fill_color='color', get_line_color=[255, 255, 255], stroked=True, line_width_min_pixels=2, get_radius='radius', radius_min_pixels=6, radius_max_pixels=30, pickable=True)
                st.pydeck_chart(pdk.Deck(map_style="light", initial_view_state=view_state, layers=[layer], tooltip={"text": "{name}\n{address}"}), height=600)

        with text_col:
            st.markdown("<p style='color:#C4A47C !important; font-weight:800; font-size:15px; margin-bottom:10px;'>🖱️ 거점을 클릭하면 지도가 이동합니다.</p>", unsafe_allow_html=True)
            st.button(f"🌍 전체 뷰\n모든 거점 확인", on_click=set_view, args=("전체 뷰",), use_container_width=True)
            for typ, btn_label in [("hq", "🏢 국내(본사)"), ("kr", "🏭 국내(지사)"), ("gl_cn", "🌐 해외(중국)"), ("gl_us", "🌎 해외(북미)")]:
                if any(loc.get("type") == typ for loc in selected.get("locations", [])):
                    names = ", ".join([loc["name"] for loc in selected["locations"] if loc["type"] == typ])
                    st.button(f"{btn_label}\n{names}", on_click=set_view, args=(btn_label,), use_container_width=True)
