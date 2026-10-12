import streamlit as st
import pandas as pd
import pydeck as pdk

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
.section-title { font-size: 22px; font-weight: 900; color: #2C2A29 !important; margin-top: 40px; margin-bottom: 25px; display: inline-block; padding-bottom: 8px; border-bottom: 3px solid #C4A47C; }
.desc-box { background-color: #FDFCFB; border: 1px solid #E5E0D8; border-radius: 12px; padding: 30px; border-left: 6px solid #C4A47C; font-size: 17px; color: #4A4441 !important; line-height: 1.8; font-weight: 400; }
.product-card { background-color: #ffffff !important; border: 1px solid #E5E0D8 !important; border-radius: 12px !important; padding: 30px 20px !important; text-align: center !important; height: 100% !important; transition: all 0.2s !important; box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.product-card:hover { transform: translateY(-4px) !important; border-color: #C4A47C !important; box-shadow: 0 10px 15px rgba(0,0,0,0.06) !important; }
.product-emoji { font-size: 48px !important; margin-bottom: 15px !important; filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.05)) !important; }
.product-title { font-size: 16px !important; font-weight: 800 !important; color: #2C2A29 !important; word-break: keep-all; line-height: 1.4;}
.stButton > button { background-color: #ffffff !important; border: 1px solid #E5E0D8 !important; border-radius: 12px !important; padding: 20px 25px !important; width: 100% !important; text-align: left !important; display: flex !important; justify-content: flex-start !important; font-size: 16px !important; font-weight: 800 !important; color: #2C2A29 !important; white-space: pre-wrap !important; line-height: 1.6 !important; transition: all 0.2s ease !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important; }
.stButton > button:hover { background-color: #FDFCFB !important; border-color: #C4A47C !important; transform: translateY(-2px) !important; box-shadow: 0 8px 12px rgba(0,0,0,0.05) !important; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. 아이콘 매핑 함수
def get_icon_html(name, category="product"):
    if category == "product":
        if "PCB" in name.upper() or "WIRE" in name.upper(): emoji = "🔌"
        elif "CASE" in name.upper() or "COVER" in name.upper(): emoji = "🗜️"
        elif "CORE" in name.upper(): emoji = "⚙️"
        elif "TERMINAL" in name.upper(): emoji = "🔩"
        else: emoji = "📦"
    elif category == "cert":
        if "IATF" in name.upper() or "ISO" in name.upper(): emoji = "🏅"
        elif "SQ" in name.upper(): emoji = "🛡️"
        else: emoji = "📜"
    return f"<div class='product-emoji'>{emoji}</div>"

# 4. 주요 고객사 [태그/뱃지 형태] HTML 생성 함수 (새로 작성됨)
def get_customer_tags_html(customers):
    if not customers:
        return "<p style='color: #8A817C; font-size: 15px;'>등록된 주요 고객사 정보가 없습니다.</p>"
    
    tags_html = "<div style='display: flex; flex-wrap: wrap; gap: 12px;'>"
    
    # 데이터가 딕셔너리 형태 (예: {"고객사": 40}) 일 때
    if isinstance(customers, dict):
        for comp, val in customers.items():
            if val is not None and val != "":
                # 값이 있을 경우 골드 색상으로 % 표시
                display_text = f"🏢 {comp} &nbsp;<span style='color:#C4A47C; font-weight:900;'>{val}%</span>"
            else:
                display_text = f"🏢 {comp}"
            tags_html += f"<div style='padding: 10px 22px; background: #ffffff; border: 1px solid #E5E0D8; border-radius: 30px; font-size: 15px; font-weight: 700; color: #4A4441; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; align-items: center;'>{display_text}</div>"
            
    # 데이터가 리스트 형태 (예: ["고객사1", "고객사2"]) 일 때
    elif isinstance(customers, list):
        for comp in customers:
            tags_html += f"<div style='padding: 10px 22px; background: #ffffff; border: 1px solid #E5E0D8; border-radius: 30px; font-size: 15px; font-weight: 700; color: #4A4441; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; align-items: center;'>🏢 {comp}</div>"

    tags_html += "</div>"
    
    return f"<div style='padding: 25px; background: #FDFCFB; border: 1px solid #E5E0D8; border-radius: 12px; margin-bottom: 10px;'>{tags_html}</div>"


# 5. 원본 엑셀파일 데이터 매핑 (비율이 없는 곳은 List 로 처리)
suppliers = [
    {
        "name": "(주)한성전장",
        "industry": "임가공(조립)",
        "hq": "양산 본사",
        "kr": "부산 공장",
        "gl": "-",
        "desc": "(주)한선전장은 첨단 생산설비와 축적된 기술을 바탕으로 고객 맞춤형 Motor 컨트롤러 및 배터리 모듈 부품을 적시에 공급하며, \n제품 기획부터 생산·평가까지 철저한 품질관리를 통해 고객만족과 신뢰를 실현하는 기업입니다.",
        "products": ["PCB ASM", "COVER ASM", "WIRE ASM"],
        "certs": ["SQ 인증"],
        "customers": {"S&T MOTIV": 46, "효성전기": 20, "스타리온": 13, "기타": 21}, # 비율이 있는 경우
        "locations": [
            {"name": "양산 본사", "type": "hq", "address": "경남 양산시 상북면 소토로 23", "lat": 35.398579, "lon": 129.056037},
            {"name": "부산 공장", "type": "kr", "address": "부산 금정구 팔송로 53번길 43", "lat": 35.281146, "lon": 129.085023}
        ]
    },
    {
        "name": "(주)성우",
        "industry": "PRESS(CASE)",
        "hq": "구미 본사",
        "kr": "천안 2공장",
        "gl": "중국 남경 공장",
        "desc": "(주)성우는 1992년 CRT TV 전자총 PRESS 제품을 시작으로, PRESS 제품과 Sub Assembly 사업을 운용하고 있는 기업입니다.",
        "products": ["CASE"],
        "certs": ["IATF 16949", "ISO 14001", "SQ 인증"],
        "customers": ["효성전기", "LG 이노텍"], # 비율 데이터가 없는 경우 (List 형태로 자동 처리)
        "locations": [
            {"name": "구미 본사", "type": "hq", "address": "경상북도 구미시", "lat": 36.119485, "lon": 128.344573},
            {"name": "천안 2공장", "type": "kr", "address": "충청남도 천안시", "lat": 36.815129, "lon": 127.113893},
            {"name": "중국 남경 공장", "type": "gl", "address": "중국 남경", "lat": 32.060255, "lon": 118.796877}
        ]
    },
    {
        "name": "(주)엠제이텍",
        "industry": "PRESS(CORE)",
        "hq": "경기도 본사",
        "kr": "-",
        "gl": "-",
        "desc": "(주)엠제이텍은 자동차 및 가전용 초정밀 모터 코어와 \n전기·전자 부품을 전문적으로 생산하는 제조기업입니다.",
        "products": ["CORE"],
        "certs": [],
        "customers": {"효성전기": 81, "(주)현대산업": 48, "두원공조": 40},
        "locations": [
            {"name": "경기도 본사", "type": "hq", "address": "경기도 안성시 죽산면 장원공단길59 장원산업단지", "lat": 37.0862, "lon": 127.3879}
        ]
    },
    {
        "name": "(주)대광오토텍",
        "industry": "PRESS(TERMINAL)",
        "hq": "부산 본사",
        "kr": "-",
        "gl": "-",
        "desc": "(주)대광오토텍은 부산 강서구 미음산업단지에 위치한 자동차 부품 제조 전문기업으로, \n자동차 모터용 정밀 부품 및 프레스 금형 설계·제작 기술을 보유하고 있습니다. \n현대·기아자동차 등 글로벌 완성차 공급망에 참여하고 있으며, 전기차 구동 모터 부품 생산 역량 강화와 고정밀 금형 기술 내재화를 통해 지속 성장하고 있습니다.",
        "products": ["TERMINAL"],
        "certs": [],
        "customers": {"효성전기": 65, "진흥공업사": 15, "삼풍하이텍": 9, "기타": 11},
        "locations": [
            {"name": "부산 본사", "type": "hq", "address": "부산 강서구 미음산단로 76번길 29", "lat": 35.132, "lon": 128.847}
        ]
    }
]

# 6. 헤더 타이틀
st.markdown("""
<div style="background-color: #2C2A29; padding: 30px 40px; border-radius: 12px; margin-bottom: 20px; border-bottom: 4px solid #C4A47C; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
    <div class="main-title">🌍 글로벌 SCM 및 파트너사 인프라 분석</div>
</div>
""", unsafe_allow_html=True)

# 7. 사이드바 구성
with st.sidebar:
    st.markdown("<h3 style='color:#C4A47C !important; font-weight:900;'>🏢 필터 및 검색</h3>", unsafe_allow_html=True)
    
    industry_list = ["전체"] + list(set(s["industry"] for s in suppliers if s["industry"] != "미분류"))
    selected_industry = st.selectbox("🏷️ 업종 필터", industry_list, on_change=reset_map_view)
    
    filtered = suppliers
    if selected_industry != "전체":
        filtered = [s for s in filtered if s["industry"] == selected_industry]
        
    search_term = st.text_input("🔍 업체명 검색", placeholder="예: 한성전장").strip()
    if search_term:
        filtered = [s for s in filtered if search_term.lower() in s["name"].lower()]

    st.markdown("<hr style='border-color: #E5E0D8; margin: 20px 0;'>", unsafe_allow_html=True)
    
    options_sidebar_map = {"🏠 종합 메인 화면": "🏠 종합 메인 화면"}
    for s in filtered:
        options_sidebar_map[s['name']] = s['name']
        
    selected_display_name = st.radio("📊 분석할 업체 선택", list(options_sidebar_map.keys()), on_change=reset_map_view)
    selected_name = options_sidebar_map[selected_display_name]

# 8. 메인 화면 출력
if selected_name == "🏠 종합 메인 화면":
    st.markdown("<div class='section-title' style='margin-top:0;'>글로벌 SCM 통합 현황</div>", unsafe_allow_html=True)
    
    total_companies = len(filtered)
    all_locations = [loc for s in filtered for loc in s["locations"]]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📌 검색된 파트너사", f"{total_companies} 개사")
    col2.metric("🏭 총 운영 거점", f"{len(all_locations)} 곳")
    col3.metric("🌐 해외 진출 거점", f"{len([l for l in all_locations if l['type'] == 'gl'])} 곳")
    
    st.markdown("<div class='section-title'>전 세계 거점 분포도</div>", unsafe_allow_html=True)
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

        st.markdown("<div class='section-title' style='margin-top:10px;'>기업 개요</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='desc-box'>{selected['desc']}</div>", unsafe_allow_html=True)
        
        # [수정] 태그 형태의 고객사 UI 출력
        st.markdown("<div class='section-title'>🤝 주요 고객사</div>", unsafe_allow_html=True)
        st.markdown(get_customer_tags_html(selected.get('customers', [])), unsafe_allow_html=True)

        st.markdown("<div class='section-title'>핵심 역량 및 품질 인증</div>", unsafe_allow_html=True)
        col_prod, col_cert = st.columns([1, 1])

        with col_prod:
            st.markdown("<div style='border-right: 2px dashed #E5E0D8; padding-right: 30px; height: 100%;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #2C2A29 !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>⚙️ 핵심 생산 품목</h4>", unsafe_allow_html=True)
            if selected['products']:
                p_cols = st.columns(2)
                for idx, prod_name in enumerate(selected['products']):
                    icon_html = get_icon_html(prod_name, "product")
                    p_cols[idx % 2].markdown(
                        f"<div class='product-card' style='margin-bottom:15px;'>{icon_html}<div class='product-title'>{prod_name}</div></div>",
                        unsafe_allow_html=True
                    )
            else:
                st.info("등록된 핵심 생산 품목이 없습니다.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_cert:
            st.markdown("<div style='padding-left: 10px; height: 100%;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #2C2A29 !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>📋 품질 및 ESG 인증</h4>", unsafe_allow_html=True)
            if selected['certs']:
                c_cols = st.columns(2)
                for idx, cert_name in enumerate(selected['certs']):
                    icon_html = get_icon_html(cert_name, "cert")
                    c_cols[idx % 2].markdown(
                        f"<div class='product-card' style='margin-bottom:15px;'>{icon_html}<div class='product-title'>{cert_name}</div></div>",
                        unsafe_allow_html=True
                    )
            else:
                st.info("등록된 품질 및 인증 내역이 없습니다.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top: 50px;'>주요 거점 네트워크</div>", unsafe_allow_html=True)
        map_col, text_col = st.columns([1.8, 1])
        df_loc = pd.DataFrame(selected["locations"])

        with text_col:
            st.markdown("<p style='color:#C4A47C !important; font-weight:800; font-size:15px; margin-bottom:10px;'>🖱️ 거점을 클릭하면 지도가 이동합니다.</p>", unsafe_allow_html=True)
            st.button("🌍 전체 뷰", on_click=set_view, args=("전체 뷰",), use_container_width=True)
            
            if selected['hq'] and selected['hq'] not in ["해당 없음", "-", "", "nan"]:
                st.write("")
                st.button(f"🏢 본사\n\n{selected['hq']}", on_click=set_view, args=("🏢 국내(본사)",), use_container_width=True)
            if selected['kr'] and selected['kr'] not in ["해당 없음", "-", "", "nan"]:
                st.write("")
                st.button(f"🏭 지사\n\n{selected['kr']}", on_click=set_view, args=("🏭 국내(지사)",), use_container_width=True)
            if selected['gl'] and selected['gl'] not in ["해당 없음", "-", "", "nan"]:
                st.write("")
                st.button(f"🌐 해외 지점\n\n{selected['gl']}", on_click=set_view, args=("🌐 해외",), use_container_width=True)

        with map_col:
            current_view = st.session_state.map_view
            
            def get_color(row):
                hi_colors = {'hq': [220, 38, 38, 255], 'kr': [37, 99, 235, 255], 'gl': [16, 185, 129, 255]} 
                dim_color = [148, 163, 184, 100]
                if current_view == "전체 뷰": return [196, 164, 124, 220]
                elif current_view == "🏢 국내(본사)" and row['type'] == 'hq': return hi_colors['hq']
                elif current_view == "🏭 국내(지사)" and row['type'] == 'kr': return hi_colors['kr']
                elif current_view == "🌐 해외" and row['type'] == 'gl': return hi_colors['gl']
                else: return dim_color

            def get_radius(row):
                if current_view == "전체 뷰": return 120000
                if current_view == "🏢 국내(본사)" and row['type'] == 'hq': return 350000
                if current_view == "🏭 국내(지사)" and row['type'] == 'kr': return 350000
                if current_view == "🌐 해외" and row['type'] == 'gl': return 350000
                return 40000 

            if not df_loc.empty:
                df_loc['color'] = df_loc.apply(get_color, axis=1)
                df_loc['radius'] = df_loc.apply(get_radius, axis=1)
                
                if current_view == "전체 뷰":
                    center_lat, center_lon = df_loc['lat'].mean(), df_loc['lon'].mean()
                    zoom_lvl = 1.2 if (df_loc['lon'].max() - df_loc['lon'].min()) > 100 else 6.0
                else:
                    target_type = 'hq' if "본사" in current_view else ('kr' if "지사" in current_view else 'gl')
                    target_df = df_loc[df_loc['type'] == target_type]
                    if not target_df.empty:
                        center_lat, center_lon = target_df['lat'].mean(), target_df['lon'].mean()
                        zoom_lvl = 5.0 if len(target_df) > 1 else 11.0 
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
