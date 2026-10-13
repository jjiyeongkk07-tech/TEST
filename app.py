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

def set_view(view):
    st.session_state.map_view = view

def reset_map_view():
    st.session_state.map_view = "전체 뷰"

# 2. 테마 CSS 설정 (좌우 높이 맞춤 & 가로 배치 로직 완벽 적용)
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

/* ✅ Streamlit 컬럼(좌우) 높이 완벽 통일을 위한 Flexbox 설정 */
[data-testid="column"] > div { height: 100%; display: flex; flex-direction: column; }
[data-testid="column"] { display: flex; flex-direction: column; }
.st-emotion-cache-11r0f1r { display: flex; flex-wrap: wrap; align-items: stretch; } /* Streamlit 내장 Row Flexbox 강제 지정 */

/* ✅ 핵심 역량 품목 양옆 배치 */
.grid-container { display: flex; flex-wrap: wrap; gap: 20px; width: 100%; height: 100%; align-content: flex-start; }
.grid-item { flex: 1; min-width: 200px; display: flex; flex-direction: column; }

/* ✅ 모든 카드(생산품목, 인증서) 높이 100% 매칭 */
.unified-card {
    background: #ffffff; border: 1px solid #E5E0D8; border-radius: 12px; padding: 20px;
    display: flex; flex-direction: column; justify-content: space-between; align-items: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.03); height: 100%; flex: 1;
}

/* 이미지 박스 기본 설정 */
.img-box {
    width: 100%; display: flex; align-items: center; justify-content: center;
    background: #FDFCFB; border-radius: 8px; padding: 10px; overflow: hidden;
}
.prod-img-box { height: 240px; margin-bottom: 20px; }

/* 🚀 인증서 박스 가로 배치(Row) 설정 */
.cert-img-box {
    flex: 1; /* 카드 내부에서 남는 공간을 모두 차지하게 하여 하단 뱃지를 바닥으로 밀어냄 */
    display: flex; flex-direction: row; flex-wrap: wrap; gap: 15px;
    justify-content: center; align-content: center;
    background: transparent; padding: 10px; margin-bottom: 20px;
}

/* 🚀 마우스 오버 시 이미지 확대 및 크기 설정 */
.img-box img { max-width: 100%; max-height: 100%; object-fit: contain; transition: transform 0.3s ease-in-out; }
.prod-img-box:hover img { transform: scale(1.15); }

/* 🚀 여러 인증서 이미지가 무조건 가로로 예쁘게 들어가도록 % 비율 및 높이 제한 */
.cert-img-box img { 
    max-height: 220px; /* 너무 길어지지 않게 방어 */
    flex: 1 1 calc(33% - 15px); /* 기본적으로 3개씩 가로 배치 (공간 부족시 2개씩 자동 조절) */
    min-width: 120px; /* 최소 너비 보장 */
    object-fit: contain; transition: transform 0.3s ease-in-out; 
}
.cert-img-box img:hover { transform: scale(1.15); z-index: 10; position: relative;}

/* 태그 및 뱃지 디자인 */
.tag-container { display: flex; flex-direction: column; gap: 8px; width: 100%; align-items: center; }
.prod-tag {
    font-size: 14.5px; font-weight: 800; color: #4A4441; text-align: center;
    word-break: keep-all; background: #F3F4F6; padding: 8px 12px;
    border-radius: 8px; width: 100%; line-height: 1.4;
}
.cert-badge-wrap {
    display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; align-items: flex-end;
    width: 100%; margin-top: auto; padding-top: 20px; border-top: 1px dashed #E5E0D8;
}
.cert-badge {
    background: #ffffff; border: 1px solid #C4A47C; color: #C4A47C; font-size: 14px;
    font-weight: 800; padding: 6px 16px; border-radius: 30px; box-shadow: 0 2px 4px rgba(196, 164, 124, 0.1); white-space: nowrap;
}

h2, h3, h4, p, span, label, li { color: #2C2A29 !important; }
[data-testid="stMetricValue"] { color: #2C2A29 !important; font-weight: 900 !important; }
[data-testid="stMetricLabel"] { color: #8A817C !important; font-weight: 700 !important; }
.main-title { font-size: 34px !important; font-weight: 900 !important; color: #ffffff !important; margin: 0 !important; line-height: 1.2 !important; letter-spacing: -1px !important; }
.section-title { font-size: 24px; font-weight: 900; color: #2C2A29 !important; margin-top: 45px; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; padding-bottom: 12px; border-bottom: 3px solid #E5E0D8; }
.section-num { color: #C4A47C; font-size: 28px; font-weight: 900; letter-spacing: -1px; }
.desc-box { background-color: #FDFCFB; border: 1px solid #E5E0D8; border-radius: 12px; padding: 30px; border-left: 6px solid #C4A47C; font-size: 17px; color: #4A4441 !important; line-height: 1.8; font-weight: 400; height: 100%; }

div.stButton > button { background-color: #ffffff !important; border: 1px solid #E5E0D8 !important; border-radius: 12px !important; padding: 15px 25px !important; width: 100% !important; height: auto !important; display: block !important; text-align: left !important; transition: all 0.2s ease !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important; }
div.stButton > button p { font-size: 16px !important; font-weight: 800 !important; color: #2C2A29 !important; white-space: pre-wrap !important; line-height: 1.5 !important; text-align: left !important; margin: 0 !important; display: block !important; }
div.stButton > button:hover { background-color: #FDFCFB !important; border-color: #C4A47C !important; transform: translateY(-2px) !important; box-shadow: 0 8px 12px rgba(0,0,0,0.05) !important; }
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

# 4. 초기 데이터 셋업 
if "suppliers" not in st.session_state:
    st.session_state.suppliers = suppliers_data

if "excel_img_data" not in st.session_state:
    st.session_state.excel_img_data = excel_img_data

suppliers = st.session_state.suppliers

# 5. 헤더 타이틀
st.markdown("""
<div style="background-color: #2C2A29; padding: 30px 40px; border-radius: 12px; margin-bottom: 20px; border-bottom: 4px solid #C4A47C; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
    <div class="main-title">🌍 글로벌 SCM 및 파트너사 인프라 분석</div>
</div>
""", unsafe_allow_html=True)


# 6. 사이드바 구성
with st.sidebar:
    st.markdown("<h3 style='color:#C4A47C !important; font-weight:900;'>🔍 상세 검색</h3>", unsafe_allow_html=True)
    
    all_countries_set = set()
    for s in suppliers:
        for loc in s.get("locations", []):
            all_countries_set.add(loc["country"])

    industry_list = ["전체"] + list(set(s.get("industry", "미분류") for s in suppliers if s.get("industry") != "미분류"))
    country_list = ["전체"] + list(all_countries_set)

    tab_industry, tab_company, tab_country = st.tabs(["🏷️ 업종", "🏢 업체", "🌍 국가"])
    
    with tab_industry:
        selected_industry = st.selectbox("조회할 업종을 선택하세요", industry_list, on_change=reset_map_view, label_visibility="collapsed")
    with tab_company:
        search_term = st.text_input("업체명을 입력하세요", placeholder="예: 한성전장", label_visibility="collapsed").strip()
    with tab_country:
        selected_country = st.selectbox("조회할 국가를 선택하세요", country_list, on_change=reset_map_view, label_visibility="collapsed")

    filtered = suppliers
    if selected_industry != "전체":
        filtered = [s for s in filtered if s.get("industry") == selected_industry]
    if selected_country != "전체":
        filtered = [s for s in filtered if any(loc.get("country") == selected_country for loc in s.get("locations", []))]
    if search_term:
        filtered = [s for s in filtered if search_term.lower() in s.get("name", "").lower()]

    st.markdown("<hr style='border-color: #E5E0D8; margin: 20px 0;'>", unsafe_allow_html=True)
    
    options_sidebar_map = {"🏠 종합 메인 화면": "🏠 종합 메인 화면"}
    for s in filtered:
        options_sidebar_map[s['name']] = s['name']
        
    selected_display_name = st.radio("📊 분석할 업체 선택", list(options_sidebar_map.keys()), on_change=reset_map_view)
    selected_name = options_sidebar_map[selected_display_name]


# 7. 메인 화면 출력 
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
        layer = pdk.Layer(
            "ScatterplotLayer", data=df_all, get_position='[lon, lat]',
            get_fill_color=[196, 164, 124, 200], get_line_color=[255, 255, 255], 
            stroked=True, line_width_min_pixels=1, get_radius=100000, 
            radius_min_pixels=6, radius_max_pixels=15, pickable=True,
        )
        st.pydeck_chart(pdk.Deck(map_style="light", initial_view_state=view_state, layers=[layer], tooltip={"text": "{name}\n{address}"}))

elif selected_name:
    selected = next((s for s in filtered if s["name"] == selected_name), None)
    
    if selected:
        badge_html = f"<div style='margin-bottom:25px; display:flex; align-items:center; gap:10px; flex-wrap:wrap;'><h2 style='margin:0; font-weight:900; font-size:42px; letter-spacing:-1px; color:#2C2A29 !important;'>{selected.get('name', '')}</h2><span style='background:#C4A47C; color:#ffffff !important; padding:6px 14px; font-size:16px; font-weight:900; border-radius:6px; box-shadow:0 2px 4px rgba(196, 164, 124, 0.3);'>{selected.get('industry', '')}</span>"
        if selected.get('sub_industry'):
            badge_html += f"<span style='background:#FDFCFB; border:1px solid #E5E0D8; color:#8A817C !important; padding:5px 12px; font-size:14px; font-weight:700; border-radius:4px;'>{selected.get('sub_industry', '')}</span>"
        badge_html += "</div>"
        
        st.markdown(badge_html, unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top:10px;'><span class='section-num'>01.</span> 기업 개요</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='desc-box'>📖 {selected.get('desc', '등록된 기업 개요가 없습니다.')}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'><span class='section-num'>02.</span> 핵심 역량 및 품질 인증</div>", unsafe_allow_html=True)
        
        # 🚀 좌우 컬럼 생성 (CSS로 stretch 강제 적용됨)
        col_prod, col_cert = st.columns([1.2, 1])
        company_images = st.session_state.excel_img_data.get(selected['name'], {"prod_imgs": [], "cert_imgs": []})

        with col_prod:
            # 컨테이너 높이를 100%로 설정하여 안쪽 요소들이 공간을 채우게 함
            st.markdown("<div style='border-right: 2px dashed #E5E0D8; padding-right: 30px; height: 100%; display: flex; flex-direction: column;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #2C2A29 !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>🌟 핵심 생산 품목</h4>", unsafe_allow_html=True)
            
            if selected.get('products'):
                prod_html = "<div class='grid-container'>"
                for idx, prod_name in enumerate(selected['products']):
                    b64_img = ""
                    if idx < len(company_images.get("prod_imgs", [])):
                        b64_img = get_base64_image(company_images["prod_imgs"][idx])
                    
                    img_tag = f"<img src='data:image/jpeg;base64,{b64_img}'>" if b64_img else ""
                    
                    tags = [t.strip() for t in prod_name.replace(" / ", "/").split("/")]
                    tags_html = "".join([f"<div class='prod-tag'>{t}</div>" for t in tags if t])
                    
                    prod_html += f"<div class='grid-item'><div class='unified-card'><div class='img-box prod-img-box'>{img_tag}</div><div class='tag-container'>{tags_html}</div></div></div>"
                    
                prod_html += "</div>"
                st.markdown(prod_html, unsafe_allow_html=True)
            else:
                st.info("등록된 핵심 생산 품목 정보가 없습니다.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_cert:
            # 컨테이너 높이를 100%로 설정
            st.markdown("<div style='padding-left: 10px; height: 100%; display: flex; flex-direction: column;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #2C2A29 !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>🏅 품질 및 ESG 인증</h4>", unsafe_allow_html=True)
            
            cert_html = "<div class='unified-card'>"
            
            # 1. 인증서 이미지 박스 (이미지가 여러 개일 경우 Flex wrap으로 가로 정렬됨)
            if company_images.get("cert_imgs"):
                cert_html += "<div class='cert-img-box'>"
                for cert_url in company_images["cert_imgs"]:
                    b64_cert = get_base64_image(cert_url)
                    if b64_cert:
                        cert_html += f"<img src='data:image/jpeg;base64,{b64_cert}'>"
                cert_html += "</div>"
            
            # 2. 인증서 하단 뱃지
            if selected.get('certs'):
                badges = "".join([f"<span class='cert-badge'>{c}</span>" for c in selected['certs']])
                cert_html += f"<div class='cert-badge-wrap'>{badges}</div>"
            
            cert_html += "</div>"
            
            if not company_images.get("cert_imgs") and not selected.get('certs'):
                st.info("등록된 품질 및 인증 정보가 없습니다.")
            else:
                st.markdown(cert_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


        st.markdown("<div class='section-title' style='margin-top: 40px;'><span class='section-num'>03.</span> 주요 고객사</div>", unsafe_allow_html=True)
        st.markdown(get_customer_tags_html(selected.get('customers', [])), unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top: 50px;'><span class='section-num'>04.</span> 글로벌 네트워크</div>", unsafe_allow_html=True)
        
        map_col, text_col = st.columns([2.5, 1]) 
        df_loc = pd.DataFrame(selected.get("locations", []))

        with map_col:
            current_view = st.session_state.map_view
            
            def get_color(row):
                hi_colors = {'hq': [220, 38, 38, 255], 'kr': [37, 99, 235, 255], 'gl_cn': [16, 185, 129, 255], 'gl_us': [245, 158, 11, 255]} 
                dim_color = [148, 163, 184, 100]
                if current_view == "전체 뷰": return [196, 164, 124, 220]
                elif current_view == "🏢 국내(본사)" and row['type'] == 'hq': return hi_colors['hq']
                elif current_view == "🏭 국내(지사)" and row['type'] == 'kr': return hi_colors['kr']
                elif current_view == "🌐 해외(중국)" and row['type'] == 'gl_cn': return hi_colors['gl_cn']
                elif current_view == "🌎 해외(북미)" and row['type'] == 'gl_us': return hi_colors['gl_us']
                else: return dim_color

            def get_radius(row):
                if current_view == "전체 뷰": return 120000
                if current_view == "🏢 국내(본사)" and row['type'] == 'hq': return 300000
                if current_view == "🏭 국내(지사)" and row['type'] == 'kr': return 300000
                if current_view == "🌐 해외(중국)" and row['type'] == 'gl_cn': return 300000
                if current_view == "🌎 해외(북미)" and row['type'] == 'gl_us': return 300000
                return 40000 

            if not df_loc.empty:
                df_loc['color'] = df_loc.apply(get_color, axis=1)
                df_loc['radius'] = df_loc.apply(get_radius, axis=1)
                
                if current_view == "전체 뷰":
                    center_lat, center_lon = 35.0, 150.0 
                    zoom_lvl = 1.0 
                else:
                    target_type = 'hq' if "본사" in current_view else ('kr' if "지사" in current_view else ('gl_cn' if "중국" in current_view else 'gl_us'))
                    target_df = df_loc[df_loc['type'] == target_type]
                    
                    if not target_df.empty:
                        center_lat, center_lon = target_df['lat'].mean(), target_df['lon'].mean()
                        zoom_lvl = 5.5 if len(target_df) > 1 else 9.0 
                    else:
                        center_lat, center_lon = df_loc['lat'].mean(), df_loc['lon'].mean()
                        zoom_lvl = 1.5
        
                view_state = pdk.ViewState(
                    latitude=center_lat, longitude=center_lon, 
                    zoom=zoom_lvl, pitch=0, transition_duration=1200
                )
                
                layer = pdk.Layer(
                    "ScatterplotLayer", data=df_loc,
                    get_position='[lon, lat]', get_fill_color='color', get_line_color=[255, 255, 255], 
                    stroked=True, line_width_min_pixels=2, get_radius='radius', 
                    radius_min_pixels=6, radius_max_pixels=30, pickable=True,
                )
                
                with st.container():
                    st.pydeck_chart(pdk.Deck(
                        map_style="light",
                        initial_view_state=view_state,
                        layers=[layer],
                        tooltip={"text": "{name}\n{address}"} 
                    ), height=600)
            else:
                st.info("해당 업체의 등록된 거점 정보가 없습니다.")

        with text_col:
            st.markdown("<p style='color:#C4A47C !important; font-weight:800; font-size:15px; margin-bottom:10px; padding-left:15px;'>🖱️ 거점을 클릭하면 지도가 이동합니다.</p>", unsafe_allow_html=True)
            
            st.markdown("<div style='padding-left: 15px;'>", unsafe_allow_html=True)
            st.button(f"🌍 전체 뷰\n모든 거점 확인", on_click=set_view, args=("전체 뷰",), use_container_width=True)
            
            has_hq = any(loc.get("type") == "hq" for loc in selected.get("locations", []))
            has_kr = any(loc.get("type") == "kr" for loc in selected.get("locations", []))
            has_gl_cn = any(loc.get("type") == "gl_cn" for loc in selected.get("locations", []))
            has_gl_us = any(loc.get("type") == "gl_us" for loc in selected.get("locations", []))
            
            if has_hq:
                st.write("")
                hq_names = ", ".join([loc["name"] for loc in selected["locations"] if loc["type"] == "hq"])
                st.button(f"🏢 국내(본사)\n{hq_names}", on_click=set_view, args=("🏢 국내(본사)",), use_container_width=True)
            if has_kr:
                st.write("")
                kr_names = ", ".join([loc["name"] for loc in selected["locations"] if loc["type"] == "kr"])
                st.button(f"🏭 국내(지사)\n{kr_names}", on_click=set_view, args=("🏭 국내(지사)",), use_container_width=True)
            if has_gl_cn:
                st.write("")
                cn_names = ", ".join([loc["name"] for loc in selected["locations"] if loc["type"] == "gl_cn"])
                st.button(f"🌐 해외(중국)_설립 예정\n{cn_names}", on_click=set_view, args=("🌐 해외(중국)",), use_container_width=True)
            if has_gl_us:
                st.write("")
                us_names = ", ".join([loc["name"] for loc in selected["locations"] if loc["type"] == "gl_us"])
                st.button(f"🌎 해외(북미)_설립 예정\n{us_names}", on_click=set_view, args=("🌎 해외(북미)",), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
