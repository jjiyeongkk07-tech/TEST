import streamlit as st
import pandas as pd
import pydeck as pdk
import time
import urllib.request
import ssl

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
.product-card { background-color: #ffffff !important; border: 1px solid #E5E0D8 !important; border-radius: 12px !important; padding: 30px 20px !important; text-align: center !important; height: 100% !important; transition: all 0.2s !important; box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.product-card:hover { transform: translateY(-4px) !important; border-color: #C4A47C !important; box-shadow: 0 10px 15px rgba(0,0,0,0.06) !important; }
.product-emoji { font-size: 48px !important; margin-bottom: 15px !important; filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.05)) !important; }
.product-title { font-size: 16px !important; font-weight: 800 !important; color: #2C2A29 !important; word-break: keep-all; line-height: 1.4;}

div.stButton > button { 
    background-color: #ffffff !important; 
    border: 1px solid #E5E0D8 !important; 
    border-radius: 12px !important; 
    padding: 15px 25px !important; 
    width: 100% !important; 
    height: auto !important;
    display: block !important; 
    text-align: left !important;
    transition: all 0.2s ease !important; 
    box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important; 
}
div.stButton > button p {
    font-size: 16px !important; 
    font-weight: 800 !important; 
    color: #2C2A29 !important; 
    white-space: pre-wrap !important; 
    line-height: 1.5 !important;
    text-align: left !important; 
    margin: 0 !important;
    display: block !important;
}
div.stButton > button:hover { 
    background-color: #FDFCFB !important; 
    border-color: #C4A47C !important; 
    transform: translateY(-2px) !important; 
    box-shadow: 0 8px 12px rgba(0,0,0,0.05) !important; 
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. 아이콘 & 태그 및 이미지 로드 우회 함수
def get_icon_html(name, category="product"):
    if category == "product":
        if "PCB" in name.upper() or "WIRE" in name.upper(): emoji = "🔌"
        elif "CASE" in name.upper() or "COVER" in name.upper() or "VENT" in name.upper(): emoji = "🗜️"
        elif "CORE" in name.upper() or "CAP" in name.upper(): emoji = "⚙️"
        elif "TERMINAL" in name.upper(): emoji = "🔩"
        else: emoji = "📦"
    elif category == "cert":
        if "IATF" in name.upper() or "ISO" in name.upper(): emoji = "🏅"
        elif "SQ" in name.upper(): emoji = "🛡️"
        else: emoji = "📜"
    return f"<div class='product-emoji'>{emoji}</div>"

def get_customer_tags_html(customers):
    if not customers:
        return "<p style='color: #8A817C; font-size: 15px;'>등록된 주요 고객사 정보가 없습니다.</p>"
    
    tags_html = "<div style='display: flex; flex-wrap: wrap; gap: 15px;'>"
    customer_list = customers.keys() if isinstance(customers, dict) else customers
    for comp in customer_list:
        tags_html += f"<div style='padding: 14px 28px; background: #ffffff; border: 2px solid #C4A47C; border-radius: 40px; font-size: 18px; font-weight: 900; color: #2C2A29; box-shadow: 0 6px 12px rgba(196, 164, 124, 0.15); display: flex; align-items: center;'>🤝 {comp}</div>"
    tags_html += "</div>"
    return f"<div style='padding: 30px; background: #FDFCFB; border: 1px solid #E5E0D8; border-radius: 12px; margin-bottom: 10px;'>{tags_html}</div>"

# ✅ 강력한 우회 다운로더
def safe_image_render(image_source):
    if isinstance(image_source, str) and image_source.startswith("http"):
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Referer': 'https://www.google.com/'
            }
            req = urllib.request.Request(image_source, headers=headers)
            
            response = urllib.request.urlopen(req, context=ctx, timeout=5)
            img_bytes = response.read()
            st.image(img_bytes, use_container_width=True)
            
        except Exception as e:
            st.warning(f"이미지 차단됨: {str(e)[:50]}...")
    else:
        st.image(image_source, use_container_width=True)


# 4. 초기 데이터 셋업 (성우 6개 거점 완벽 반영 및 제품명 정리)
if "suppliers" not in st.session_state:
    st.session_state.suppliers = [
        {
            "name": "(주)성우",
            "industry": "2차전지 및 전장부품",
            "hq": "경북 구미 본사", 
            "kr": "천안 공장", 
            "gl": "중국 및 북미 법인",
            "desc": "(주)성우는 1992년 설립 이래 초정밀 프레스(PRESS) 기술을 기반으로 성장하여, 현재는 전기차 배터리용 핵심 안전부품(원통형 Top Cap 어셈블리 등) 및 자동차 전장부품 생산을 주도하는 정밀 부품 제조 전문기업입니다.",
            "products": ["2차전지 제품", "전장부품 및 기타제품"],  # ✅ 수정됨: 2개로 정확히 맞춤
            "certs": ["IATF 16949", "ISO 14001", "ISO 45001", "SQ 인증"],
            "customers": {"LG에너지솔루션": 55, "효성전기": 25, "LG이노텍": 15, "기타": 5},
            "locations": [
                # ✅ 수정됨: 글로벌 6개 거점 완벽 반영
                {"name": "(주)성우 구미1사업장(본사)", "type": "hq", "address": "경북 구미시 3공단2로 107", "lat": 36.1018, "lon": 128.4223, "country": "대한민국"},
                {"name": "(주)성우 R&D Center", "type": "kr", "address": "경북 구미시 산동읍 도중리 115", "lat": 36.1601, "lon": 128.4682, "country": "대한민국"},
                {"name": "천안사업장", "type": "kr", "address": "충남 천안시 동남구 성남면 5산단2로 133", "lat": 36.7580, "lon": 127.2750, "country": "대한민국"},
                {"name": "중국 남경사업장", "type": "gl_cn", "address": "No.9, Hengda Road, Nanjing, China", "lat": 32.0602, "lon": 118.7968, "country": "중국"},
                {"name": "중국 추저우 사업장 (설립예정)", "type": "gl_cn", "address": "중국 안후이성 추저우시", "lat": 32.3024, "lon": 118.3186, "country": "중국"},
                {"name": "북미 사업장 (설립예정)", "type": "gl_us", "address": "미국 테네시주 또는 오하이오주 일대", "lat": 39.9611, "lon": -82.9987, "country": "미국"}
            ]
        },
        {
            "name": "(주)한성전장",
            "industry": "임가공(조립)",
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

if "excel_img_data" not in st.session_state:
    st.session_state.excel_img_data = {
        "(주)성우": {
            "prod_imgs": [
                "https://www.e-sungwoo.co.kr/img/sub/prd_111.jpg", 
                "https://www.e-sungwoo.co.kr/img/sub/prd_112.jpg"
            ],
            "cert_imgs": []
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


    # --- 6-3. 관리자용 데이터 연동 메뉴 ---
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #E5E0D8; margin: 20px 0;'>", unsafe_allow_html=True)
    
    with st.popover("⚙️ 관리자 설정 (데이터 연동)", use_container_width=True):
        admin_tab1, admin_tab2 = st.tabs(["📁 파일 업로드", "🌐 웹 주소 연동"])
        
        with admin_tab1:
            uploaded_files = st.file_uploader(
                "파일 및 엑셀 업로드", 
                type=["xlsx", "xls", "png", "jpg", "jpeg", "webp"], 
                accept_multiple_files=True, 
                label_visibility="collapsed"
            )
            
            if uploaded_files:
                excel_file = None
                uploaded_images = {}
                
                for file in uploaded_files:
                    if file.name.endswith(('.xlsx', '.xls')):
                        excel_file = file
                    else:
                        uploaded_images[file.name] = file

                if excel_file:
                    try:
                        df_ex = pd.read_excel(excel_file, sheet_name='업체정보')
                        cols = df_ex.columns

                        for _, row in df_ex.iterrows():
                            comp_name = str(row.iloc[0]).strip()
                            
                            def get_img_source(val):
                                if pd.isna(val) or str(val).strip() == "": return None
                                val_str = str(val).strip()
                                if val_str.startswith("http"): return val_str
                                for img_name, img_file in uploaded_images.items():
                                    if img_name in val_str: return img_file
                                return None

                            p1 = get_img_source(row.iloc[11]) if len(row) > 11 else None
                            p2 = get_img_source(row.iloc[12]) if len(row) > 12 else None
                            c1 = get_img_source(row.iloc[13]) if len(row) > 13 else None
                            c2 = get_img_source(row.iloc[14]) if len(row) > 14 else None
                            
                            prod_imgs = [x for x in [p1, p2] if x is not None]
                            cert_imgs = [x for x in [c1, c2] if x is not None]
                            st.session_state.excel_img_data[comp_name] = {"prod_imgs": prod_imgs, "cert_imgs": cert_imgs}
                            
                            target_supplier = next((s for s in st.session_state.suppliers if s['name'] == comp_name), None)
                            if target_supplier:
                                if '업종' in cols and pd.notna(row['업종']): target_supplier['industry'] = str(row['업종'])
                                if '기업개요' in cols and pd.notna(row['기업개요']): target_supplier['desc'] = str(row['기업개요'])
                                if '본사' in cols and pd.notna(row['본사']): target_supplier['hq'] = str(row['본사'])
                                if '지사' in cols and pd.notna(row['지사']): target_supplier['kr'] = str(row['지사'])
                                if '해외' in cols and pd.notna(row['해외']): target_supplier['gl'] = str(row['해외'])
                                if '핵심생산품목' in cols and pd.notna(row['핵심생산품목']): target_supplier['products'] = [x.strip() for x in str(row['핵심생산품목']).split(',')]
                                if '품질인증' in cols and pd.notna(row['품질인증']): target_supplier['certs'] = [x.strip() for x in str(row['품질인증']).split(',')]

                        st.success("✅ 파일 데이터 연동 완료!")
                    except Exception as e:
                        st.error("오류: 엑셀 파일 형식 또는 '업체정보' 시트 구성을 확인해주세요.")

        with admin_tab2:
            st.markdown("<p style='font-size:13px; color:#8A817C;'>💡 홈페이지 주소를 입력하면 웹 데이터를 분석하여 SCM 정보를 자동 등록합니다.</p>", unsafe_allow_html=True)
            input_comp = st.text_input("업체명", placeholder="예: (주)테스트기업")
            input_url = st.text_input("홈페이지 URL", placeholder="https://www.example.com")
            
            if st.button("AI 데이터 추출 및 연동", use_container_width=True):
                if input_comp and input_url:
                    with st.spinner("웹 사이트 분석 및 위경도 추출 중... (AI API 연동 필요)"):
                        time.sleep(2)
                        
                        new_supplier = {
                            "name": input_comp,
                            "industry": "자동 추출(AI)",
                            "hq": "서울 본사", "kr": "수원 공장", "gl": "-",
                            "desc": f"{input_comp}는 AI 모델이 {input_url}에서 자동으로 분석하여 요약한 기업 소개글입니다. 향후 실제 데이터로 대체됩니다.",
                            "products": ["테스트 부품 1", "테스트 부품 2"],
                            "certs": ["ISO 9001"],
                            "customers": ["A자동차", "B전자"],
                            "locations": [
                                {"name": "서울 본사", "type": "hq", "address": "서울특별시 강남구 테헤란로", "lat": 37.500, "lon": 127.036, "country": "대한민국"},
                                {"name": "수원 공장", "type": "kr", "address": "경기도 수원시 영통구", "lat": 37.263, "lon": 127.028, "country": "대한민국"}
                            ]
                        }
                        
                        existing_idx = next((i for i, s in enumerate(st.session_state.suppliers) if s["name"] == input_comp), None)
                        if existing_idx is not None:
                            st.session_state.suppliers[existing_idx] = new_supplier
                        else:
                            st.session_state.suppliers.append(new_supplier)
                            
                        st.session_state.excel_img_data[input_comp] = {
                            "prod_imgs": ["https://images.unsplash.com/photo-1617774136473-03e5c98d6263?w=500&q=80", "https://images.unsplash.com/photo-1518985289947-0bfa7d2bcebd?w=500&q=80"],
                            "cert_imgs": []
                        }
                        
                        st.success(f"✅ {input_comp} 데이터 추출 및 연동 완료! 좌측 업체 목록에서 확인하세요.")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.warning("업체명과 URL을 모두 입력해주세요.")


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
        st.markdown(
            f"<div style='margin-bottom:25px; display:flex; align-items:baseline; gap: 15px;'>"
            f"<h2 style='margin:0; font-weight:900; font-size:42px; letter-spacing: -1px; color:#2C2A29 !important;'>{selected['name']}</h2>"
            f"<span style='background:#FDFCFB; border: 1px solid #C4A47C; color:#C4A47C !important; padding: 4px 12px; font-size: 15px; font-weight: 800; border-radius: 4px;'>{selected['industry']}</span></div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='section-title' style='margin-top:10px;'><span class='section-num'>01.</span> 기업 개요</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='desc-box'>📖 {selected['desc']}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'><span class='section-num'>02.</span> 주요 고객사</div>", unsafe_allow_html=True)
        st.markdown(get_customer_tags_html(selected.get('customers', [])), unsafe_allow_html=True)

        st.markdown("<div class='section-title'><span class='section-num'>03.</span> 핵심 역량 및 품질 인증</div>", unsafe_allow_html=True)
        col_prod, col_cert = st.columns([1, 1])

        company_images = st.session_state.excel_img_data.get(selected['name'], {"prod_imgs": [], "cert_imgs": []})

        with col_prod:
            st.markdown("<div style='border-right: 2px dashed #E5E0D8; padding-right: 30px; height: 100%;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #2C2A29 !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>🌟 핵심 생산 품목</h4>", unsafe_allow_html=True)
            if selected['products']:
                p_cols = st.columns(2)
                for idx, prod_name in enumerate(selected['products']):
                    with p_cols[idx % 2]:
                        if idx < len(company_images["prod_imgs"]):
                            st.markdown(f"<div class='product-card' style='margin-bottom:15px; padding: 10px !important;'>", unsafe_allow_html=True)
                            safe_image_render(company_images["prod_imgs"][idx])
                            st.markdown(f"<div class='product-title' style='margin-top:10px;'>{prod_name}</div></div>", unsafe_allow_html=True)
                        else:
                            icon_html = get_icon_html(prod_name, "product")
                            st.markdown(f"<div class='product-card' style='margin-bottom:15px;'>{icon_html}<div class='product-title'>{prod_name}</div></div>", unsafe_allow_html=True)
            else:
                st.info("등록된 핵심 생산 품목이 없습니다.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_cert:
            st.markdown("<div style='padding-left: 10px; height: 100%;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #2C2A29 !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>🏅 품질 및 ESG 인증</h4>", unsafe_allow_html=True)
            if selected['certs']:
                c_cols = st.columns(2)
                for idx, cert_name in enumerate(selected['certs']):
                    with c_cols[idx % 2]:
                        if idx < len(company_images["cert_imgs"]):
                            st.markdown(f"<div class='product-card' style='margin-bottom:15px; padding: 10px !important;'>", unsafe_allow_html=True)
                            safe_image_render(company_images["cert_imgs"][idx])
                            st.markdown(f"<div class='product-title' style='margin-top:10px;'>{cert_name}</div></div>", unsafe_allow_html=True)
                        else:
                            icon_html = get_icon_html(cert_name, "cert")
                            st.markdown(f"<div class='product-card' style='margin-bottom:15px;'>{icon_html}<div class='product-title'>{cert_name}</div></div>", unsafe_allow_html=True)
            else:
                st.info("등록된 품질 및 인증 내역이 없습니다.")
            st.markdown("</div>", unsafe_allow_html=True)

        # ✅ 거점 6개에 맞춰 지도 뷰 전환 버튼 고도화
        st.markdown("<div class='section-title' style='margin-top: 50px;'><span class='section-num'>04.</span> 주요 거점 네트워크</div>", unsafe_allow_html=True)
        map_col, text_col = st.columns([1.8, 1])
        df_loc = pd.DataFrame(selected["locations"])

        with text_col:
            st.markdown("<p style='color:#C4A47C !important; font-weight:800; font-size:15px; margin-bottom:10px;'>🖱️ 거점을 클릭하면 지도가 이동합니다.</p>", unsafe_allow_html=True)
            
            st.button(f"🌍 전체 뷰\n모든 거점 확인", on_click=set_view, args=("전체 뷰",), use_container_width=True)
            
            # 국내 본사/지사
            has_hq = any(loc["type"] == "hq" for loc in selected["locations"])
            has_kr = any(loc["type"] == "kr" for loc in selected["locations"])
            
            if has_hq:
                st.write("")
                st.button(f"🏢 국내(본사)\n구미 1사업장", on_click=set_view, args=("🏢 국내(본사)",), use_container_width=True)
            if has_kr:
                st.write("")
                st.button(f"🏭 국내(지사)\nR&D센터, 천안사업장", on_click=set_view, args=("🏭 국내(지사)",), use_container_width=True)

            # 해외 법인(중국, 북미 분리)
            has_gl_cn = any(loc["type"] == "gl_cn" for loc in selected["locations"])
            has_gl_us = any(loc["type"] == "gl_us" for loc in selected["locations"])

            if has_gl_cn:
                st.write("")
                st.button(f"🌐 해외(중국)\n남경, 추저우(예정)", on_click=set_view, args=("🌐 해외(중국)",), use_container_width=True)
            if has_gl_us:
                st.write("")
                st.button(f"🌎 해외(북미)\n미국 법인(예정)", on_click=set_view, args=("🌎 해외(북미)",), use_container_width=True)


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
                
                # 시점(Camera) 이동 세팅
                if current_view == "전체 뷰":
                    center_lat, center_lon = 35.0, 150.0 # 태평양 중심 (한국-미국 모두 보이게)
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
                    ))
            else:
                st.info("해당 업체의 등록된 거점 정보가 없습니다.")
