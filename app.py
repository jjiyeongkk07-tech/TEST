# app.py
import streamlit as st
import pandas as pd
import pydeck as pdk
import time
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
[data-testid="stSidebar"] { background-color: #Fdfcfb !important; border-right: 1px solid #E5E0D8 !important; }

/* ✅ 완벽한 50:50 분할 및 높이/너비 100% 꽉참 CSS */
[data-testid="column"] > div > div > div > div > div { padding: 0 !important; gap: 0 !important; }
[data-testid="column"] { padding-bottom: 0 !important; display: flex; flex-direction: column; width: 100%; }
div[data-testid="stVerticalBlock"] > div { display: flex; align-items: stretch; width: 100%; }

/* ✅ 카드(네모 칸) 안의 내용 정렬 및 이미지 크기 강제 통일 */
.custom-card-container {
    display: flex;
    flex-wrap: wrap; 
    gap: 15px; /* 간격 살짝 줄임 */
    width: 100%;
    height: 100%;
    justify-content: space-between;
}

.custom-card { 
    background-color: #ffffff; 
    border: 1px solid #E5E0D8; 
    border-radius: 12px; 
    padding: 15px; /* 패딩을 약간 줄여 이미지가 더 커보이게 함 */
    text-align: center; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    margin-bottom: 15px;
    height: 400px !important;  /* 카드 높이 고정 */
    display: flex;
    flex-direction: column;
    justify-content: flex-start; /* 위에서부터 채움 */
    overflow: hidden; /* 영역 밖으로 삐져나가는 것 방지 */
}
.img-container {
    height: 250px; /* 이미지 영역 높이 고정 (여기서 조절) */
    width: 100%;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #fff; /* 배경색 흰색 보장 */
}

/* 🚀 핵심 수정 1: 이미지를 네모 칸 안에 꽉 채우기 */
.img-container img {
    width: 100%;
    height: 100%;
    object-fit: cover; /* 이미지를 잘리더라도 영역에 꽉 차게 덮음 */
    object-position: center; /* 중앙 정렬 */
    border-radius: 8px;
}

.product-title { 
    font-size: 15px !important; 
    font-weight: 800 !important; 
    color: #2C2A29 !important; 
    word-break: keep-all; 
    line-height: 1.6; /* 줄간격을 넓혀서 보기 편하게 */
    margin-top: auto; 
    padding-top: 10px;
}

.cert-badge-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-top: auto; padding-top: 10px; }
.cert-badge { background: #F3F4F6; border: 1px solid #E5E7EB; color: #374151; font-size: 13px; font-weight: 700; padding: 6px 14px; border-radius: 20px; white-space: nowrap; }

h2, h3, h4, p, span, label, li { color: #2C2A29 !important; }
[data-testid="stMetricValue"] { color: #2C2A29 !important; font-weight: 900 !important; }
[data-testid="stMetricLabel"] { color: #8A817C !important; font-weight: 700 !important; }

/* 헤더 폰트 색상을 흰색으로 고정 */
.main-title { font-size: 34px !important; font-weight: 900 !important; color: #ffffff !important; margin: 0 !important; line-height: 1.2 !important; letter-spacing: -1px !important; }

.section-title { 
    font-size: 24px; font-weight: 900; color: #2C2A29 !important; 
    margin-top: 45px; margin-bottom: 25px; display: flex; align-items: center; gap: 10px;
    padding-bottom: 12px; border-bottom: 3px solid #E5E0D8; 
}
.section-num { color: #C4A47C; font-size: 28px; font-weight: 900; letter-spacing: -1px; }
.desc-box { background-color: #FDFCFB; border: 1px solid #E5E0D8; border-radius: 12px; padding: 30px; border-left: 6px solid #C4A47C; font-size: 17px; color: #4A4441 !important; line-height: 1.8; font-weight: 400; }

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

# 4. 초기 데이터 셋업 (data.py에서 로드)
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
        for loc in s["locations"]:
            all_countries_set.add(loc["country"])

    industry_list = ["전체"] + list(set(s["industry"] for s in suppliers if s["industry"] != "미분류"))
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
        filtered = [s for s in filtered if s["industry"] == selected_industry]
    if selected_country != "전체":
        filtered = [s for s in filtered if any(loc.get("country") == selected_country for loc in s["locations"])]
    if search_term:
        filtered = [s for s in filtered if search_term.lower() in s["name"].lower()]

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
    all_locations = [loc for s in filtered for loc in s["locations"]]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📌 검색된 파트너사", f"{total_companies} 개사")
    col2.metric("🏭 총 운영 거점", f"{len(all_locations)} 곳")
    col3.metric("🌐 해외 진출 거점", f"{len([l for l in all_locations if l['type'] not in ['hq', 'kr']])} 곳")
    
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
        badge_html = f"<div style='margin-bottom:25px; display:flex; align-items:center; gap:10px; flex-wrap:wrap;'><h2 style='margin:0; font-weight:900; font-size:42px; letter-spacing:-1px; color:#2C2A29 !important;'>{selected['name']}</h2><span style='background:#C4A47C; color:#ffffff !important; padding:6px 14px; font-size:16px; font-weight:900; border-radius:6px; box-shadow:0 2px 4px rgba(196, 164, 124, 0.3);'>{selected['industry']}</span>"
        if selected.get('sub_industry'):
            badge_html += f"<span style='background:#FDFCFB; border:1px solid #E5E0D8; color:#8A817C !important; padding:5px 12px; font-size:14px; font-weight:700; border-radius:4px;'>{selected['sub_industry']}</span>"
        badge_html += "</div>"
        
        st.markdown(badge_html, unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top:10px;'><span class='section-num'>01.</span> 기업 개요</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='desc-box'>📖 {selected['desc']}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'><span class='section-num'>02.</span> 핵심 역량 및 품질 인증</div>", unsafe_allow_html=True)
        
        # 좌측(생산품목)과 우측(인증서) 분할
        col_prod, col_cert = st.columns([1, 1])
        company_images = st.session_state.excel_img_data.get(selected['name'], {"prod_imgs": [], "cert_imgs": []})

        with col_prod:
            st.markdown("<div style='border-right: 2px dashed #E5E0D8; padding-right: 30px; height: 100%; display: flex; flex-direction: column;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #2C2A29 !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>🌟 핵심 생산 품목</h4>", unsafe_allow_html=True)
            
            if selected['products']:
                prod_html = "<div class='custom-card-container'>"
                for idx, prod_name in enumerate(selected['products']):
                    if idx < len(company_images["prod_imgs"]):
                        b64_img = get_base64_image(company_images["prod_imgs"][idx])
                        if b64_img:
                            # 🚀 핵심 수정 2: '/' 를 기준으로 줄바꿈(<br>) 처리
                            formatted_prod_name = prod_name.replace("/", "<br>")
                            
                            prod_html += f"""
                            <div class='custom-card' style='width: 100%; max-width: 100%; flex: 1 1 100%;'>
                                <div class='img-container'>
                                    <img src='data:image/jpeg;base64,{b64_img}'>
                                </div>
                                <div class='product-title'>{formatted_prod_name}</div>
                            </div>
                            """
                prod_html += "</div>"
                st.markdown(prod_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_cert:
            st.markdown("<div style='padding-left: 10px; height: 100%; display: flex; flex-direction: column;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #2C2A29 !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>🏅 품질 및 ESG 인증</h4>", unsafe_allow_html=True)
            
            if company_images.get("cert_imgs"):
                cert_html = "<div class='custom-card-container'>"
                cert_count = len(company_images["cert_imgs"])
                
                for idx, cert_url in enumerate(company_images["cert_imgs"]):
                    b64_cert = get_base64_image(cert_url)
                    if b64_cert:
                        cert_name = selected['certs'][idx] if idx < len(selected.get('certs', [])) else "인증서"
                        badges_html = f"<div class='cert-badge-container'><span class='cert-badge'>{cert_name}</span></div>"
                        
                        # 카드가 3개 이상일 경우 너비를 3등분
                        if cert_count >= 3:
                            card_style = "width: calc(33.3% - 10px); flex: 0 0 calc(33.3% - 10px);"
                        else:
                            card_style = "flex: 1; max-width: 300px;"
                            
                        cert_html += f"<div class='custom-card' style='{card_style}'><div class='img-container'><img src='data:image/jpeg;base64,{b64_cert}'></div>{badges_html}</div>"
                cert_html += "</div>"
                st.markdown(cert_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


        st.markdown("<div class='section-title' style='margin-top: 40px;'><span class='section-num'>03.</span> 주요 고객사</div>", unsafe_allow_html=True)
        st.markdown(get_customer_tags_html(selected.get('customers', [])), unsafe_allow_html=True)


        st.markdown("<div class='section-title' style='margin-top: 50px;'><span class='section-num'>04.</span> 글로벌 네트워크</div>", unsafe_allow_html=True)
        
        map_col, text_col = st.columns([2.5, 1]) 
        df_loc = pd.DataFrame(selected["locations"])

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
            
            # ✅ data.py의 정보를 읽어와서 동적으로 버튼 이름을 만듦
            has_hq = any(loc["type"] == "hq" for loc in selected["locations"])
            has_kr = any(loc["type"] == "kr" for loc in selected["locations"])
            has_gl_cn = any(loc["type"] == "gl_cn" for loc in selected["locations"])
            has_gl_us = any(loc["type"] == "gl_us" for loc in selected["locations"])
            
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
                st.button(f"🌐 해외(중국)\n{cn_names}", on_click=set_view, args=("🌐 해외(중국)",), use_container_width=True)
            if has_gl_us:
                st.write("")
                us_names = ", ".join([loc["name"] for loc in selected["locations"] if loc["type"] == "gl_us"])
                st.button(f"🌎 해외(북미)\n{us_names}", on_click=set_view, args=("🌎 해외(북미)",), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
