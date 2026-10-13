import streamlit as st
import pandas as pd
import pydeck as pdk
import time
import urllib.request
import ssl
import base64

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

.custom-card-container {
    display: flex;
    gap: 20px;
    width: 100%;
    height: 100%;
}

.custom-card { 
    flex: 1; 
    background-color: #ffffff; 
    border: 1px solid #E5E0D8; 
    border-radius: 12px; 
    padding: 20px; 
    text-align: center; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    margin-bottom: 15px;
    height: 380px !important; 
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.img-container {
    height: 270px; 
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
}
.img-container img {
    max-height: 100%;
    max-width: 100%;
    object-fit: contain; 
    border-radius: 8px;
}
.product-title { font-size: 16px !important; font-weight: 800 !important; color: #2C2A29 !important; word-break: keep-all; line-height: 1.4; margin-top: auto; padding-top: 10px;}
.cert-badge-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-top: auto; padding-top: 10px; }
.cert-badge { background: #F3F4F6; border: 1px solid #E5E7EB; color: #374151; font-size: 13px; font-weight: 700; padding: 6px 14px; border-radius: 20px; }

h2, h3, h4, p, span, label, li { color: #2C2A29 !important; }
[data-testid="stMetricValue"] { color: #2C2A29 !important; font-weight: 900 !important; }
[data-testid="stMetricLabel"] { color: #8A817C !important; font-weight: 700 !important; }
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

# 4. 초기 데이터 셋업
if "suppliers" not in st.session_state:
    st.session_state.suppliers = [
        {
            "name": "(주)성우",
            "industry": "PRESS(CASE)", # ✅ 분류는 사내 기준 고정
            "sub_industry": "2차전지 및 전장부품", # ✅ 서브 텍스트 분리
            "hq": "경북 구미 본사", 
            "kr": "천안 공장", 
            "gl": "중국 및 북미 법인",
            "desc": "(주)성우는 1992년 설립 이래 초정밀 프레스(PRESS) 기술을 기반으로 성장하여, 현재는 전기차 배터리용 핵심 안전부품(원통형 Top Cap 어셈블리 등) 및 자동차 전장부품 생산을 주도하는 정밀 부품 제조 전문기업입니다.",
            "products": ["2차전지 제품", "전장부품 및 기타제품"],
            "certs": ["IATF16949", "ISO14001", "SQ 인증", "ESG 경영"],
            "customers": {"LG에너지솔루션": 55, "효성전기": 25, "LG이노텍": 15, "기타": 5},
            "locations": [
                {"name": "(주)성우 구미1사업장(본사)", "type": "hq", "address": "경북 구미시 3공단2로 107", "lat": 36.1018, "lon": 128.4223, "country": "대한민국"},
                {"name": "(주)성우 R&D Center", "type": "kr", "address": "경북 구미시 산동읍 도중리 115", "lat": 36.1601, "lon": 128.4682, "country": "대한민국"},
                {"name": "천안사업장", "type": "kr", "address": "충남 천안시 동남구 성남면 5산단2로 133", "lat": 36.7580, "lon": 127.2750, "country": "대한민국"},
                {"name": "중국 남경사업장", "type": "gl_cn", "address": "No.9, Hengda Road, Nanjing, China", "lat": 32.0602, "lon": 118.7968, "country": "중국"},
                {"name": "중국 추저우 사업장 (설립예정)", "type": "gl_cn", "address": "중국 안후이성 추저우시", "lat": 32.3024, "lon": 118.3186, "country": "중국"},
                {"name": "북미 사업장 (설립예정)", "type": "gl_us", "address": "미국 오하이오 주", "lat": 39.9611, "lon": -82.9987, "country": "미국"}
            ]
        },
        {
            "name": "(주)한성전장",
            "industry": "임가공(조립)",
            "sub_industry": "",
            "hq": "양산 본사", "kr": "부산 공장", "gl": "-",
            "desc": "(주)한선전장은 첨단 생산설비와 축적된 기술을 바탕으로 고객 맞춤형 Motor 컨트롤러 및 배터리 모듈 부품을 적시에 공급하며, \n제품 기획부터 생산·평가까지 철저한 품질관리를 통해 고객만족과 신뢰를 실현하는 기업입니다.",
            "products": ["PCB ASM", "COVER ASM", "WIRE ASM"],
            "certs": ["SQ 인증"],
            "customers": {"S&T MOTIV": 46, "효성전기": 20, "스타리온": 13, "기타": 21},
            "locations": [
                {"name": "양산 본사", "type": "hq", "address": "경남 양산시 상북면 소토로 23", "lat": 35.398579, "lon": 129.056037, "country": "대한민국"},
                {"name": "부산 공장", "type": "kr", "address": "부산 금정구 팔송로 53번길 43", "lat": 35.281146, "lon": 129.085023, "country": "대한민국"}
            ]
        }
    ]

# 🌟 이미지 URL 적용 🌟
if "excel_img_data" not in st.session_state:
    st.session_state.excel_img_data = {
        "(주)성우": {
            "prod_imgs": [
                "https://www.e-sungwoo.co.kr/img/sub/prd_111.jpg", 
                "https://www.e-sungwoo.co.kr/img/sub/prd_112.jpg"
            ],
            "cert_imgs": [
                "https://www.e-sungwoo.co.kr/img/sub/cpn-wp1_2.jpg"
            ]
        }
    }

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
        # ✅ 메인 태그 렌더링 방식 수정 (PRESS CASE를 강조하고 서브 텍스트 추가)
        badge_html = f"""
        <div style='display:flex; align-items:center; gap: 10px; flex-wrap: wrap; margin-bottom:25px;'>
            <h2 style='margin:0; font-weight:900; font-size:42px; letter-spacing: -1px; color:#2C2A29 !important;'>{selected['name']}</h2>
            <span style='background:#C4A47C; color:#ffffff !important; padding: 6px 14px; font-size: 16px; font-weight: 900; border-radius: 6px; box-shadow: 0 2px 4px rgba(196, 164, 124, 0.3);'>
                {selected['industry']}
            </span>
        """
        if selected.get('sub_industry'):
            badge_html += f"""
            <span style='background:#FDFCFB; border: 1px solid #E5E0D8; color:#8A817C !important; padding: 4px 12px; font-size: 14px; font-weight: 700; border-radius: 4px;'>
                {selected['sub_industry']}
            </span>
            """
        badge_html += "</div>"
        
        st.markdown(badge_html, unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top:10px;'><span class='section-num'>01.</span> 기업 개요</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='desc-box'>📖 {selected['desc']}</div>", unsafe_allow_html=True)
        
        # ✅ 핵심 역량 및 품질 인증
        st.markdown("<div class='section-title'><span class='section-num'>02.</span> 핵심 역량 및 품질 인증</div>", unsafe_allow_html=True)
        
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
                            prod_html += f"<div class='custom-card'><div class='img-container'><img src='data:image/jpeg;base64,{b64_img}'></div><div class='product-title'>{prod_name}</div></div>"
                prod_html += "</div>"
                st.markdown(prod_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_cert:
            st.markdown("<div style='padding-left: 10px; height: 100%; display: flex; flex-direction: column;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #2C2A29 !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>🏅 품질 및 ESG 인증</h4>", unsafe_allow_html=True)
            
            if company_images.get("cert_imgs"):
                b64_cert = get_base64_image(company_images["cert_imgs"][0])
                if b64_cert:
                    badges_html = "<div class='cert-badge-container'>"
                    if selected.get('certs'):
                        for cert in selected['certs']:
                            badges_html += f"<span class='cert-badge'>{cert}</span>"
                    badges_html += "</div>"
                    
                    cert_card = f"<div class='custom-card-container'><div class='custom-card' style='height: 100%;'><div class='img-container'><img src='data:image/jpeg;base64,{b64_cert}'></div>{badges_html}</div></div>"
                    st.markdown(cert_card, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


        # ✅ 주요 고객사
        st.markdown("<div class='section-title' style='margin-top: 40px;'><span class='section-num'>03.</span> 주요 고객사</div>", unsafe_allow_html=True)
        st.markdown(get_customer_tags_html(selected.get('customers', [])), unsafe_allow_html=True)


        # ✅ 글로벌 네트워크 
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
            
            has_hq = any(loc["type"] == "hq" for loc in selected["locations"])
            has_kr = any(loc["type"] == "kr" for loc in selected["locations"])
            has_gl_cn = any(loc["type"] == "gl_cn" for loc in selected["locations"])
            has_gl_us = any(loc["type"] == "gl_us" for loc in selected["locations"])
            
            if has_hq:
                st.write("")
                st.button(f"🏢 국내(본사)\n구미 1사업장", on_click=set_view, args=("🏢 국내(본사)",), use_container_width=True)
            if has_kr:
                st.write("")
                st.button(f"🏭 국내(지사)\nR&D센터, 천안사업장", on_click=set_view, args=("🏭 국내(지사)",), use_container_width=True)
            if has_gl_cn:
                st.write("")
                st.button(f"🌐 해외(중국)\n남경, 추저우(예정)", on_click=set_view, args=("🌐 해외(중국)",), use_container_width=True)
            if has_gl_us:
                st.write("")
                st.button(f"🌎 해외(북미)\n미국 법인(예정)", on_click=set_view, args=("🌎 해외(북미)",), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
