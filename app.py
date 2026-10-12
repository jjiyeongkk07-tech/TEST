import streamlit as st
import pandas as pd
import pydeck as pdk
import base64
import os

# 1. 페이지 설정
st.set_page_config(page_title="글로벌 SCM 분석", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

# [세션 상태 초기화]
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
    background-color: #ffffff; padding: 3rem 4rem !important; margin-top: 2rem; margin-bottom: 3rem;
    border-radius: 16px; max-width: 1400px; border: 1px solid #E5E0D8; box-shadow: 0 15px 35px rgba(100, 90, 80, 0.08);
}
header { visibility: hidden; } footer { visibility: hidden; }
[data-testid="stSidebar"] { background-color: #Fdfcfb !important; border-right: 1px solid #E5E0D8 !important; }
h2, h3, h4, p, span, label, li { color: #2C2A29 !important; }
[data-testid="stMetricValue"] { color: #2C2A29 !important; font-weight: 900 !important; }
[data-testid="stMetricLabel"] { color: #8A817C !important; font-weight: 700 !important; }
.main-title { font-size: 34px !important; font-weight: 900 !important; color: #ffffff !important; margin: 0 !important; line-height: 1.2 !important; letter-spacing: -1px !important; }
.section-title { font-size: 22px; font-weight: 900; color: #2C2A29 !important; margin-top: 40px; margin-bottom: 25px; display: inline-block; padding-bottom: 8px; border-bottom: 3px solid #C4A47C; }
.desc-box { background-color: #FDFCFB; border: 1px solid #E5E0D8; border-radius: 12px; padding: 30px; border-left: 6px solid #C4A47C; font-size: 17px; color: #4A4441 !important; line-height: 1.8; font-weight: 400; }
.product-card { background-color: #ffffff !important; border: 1px solid #E5E0D8 !important; border-radius: 12px !important; padding: 25px 15px !important; text-align: center !important; height: 100% !important; transition: all 0.2s !important; box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.product-card:hover { transform: translateY(-4px) !important; border-color: #C4A47C !important; box-shadow: 0 10px 15px rgba(0,0,0,0.06) !important; }
.product-emoji { font-size: 42px !important; margin-bottom: 12px !important; filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.05)) !important; }
.product-title { font-size: 15px !important; font-weight: 800 !important; color: #2C2A29 !important; word-break: keep-all; line-height: 1.4;}
.stButton > button { background-color: #ffffff !important; border: 1px solid #E5E0D8 !important; border-radius: 12px !important; padding: 20px 25px !important; width: 100% !important; text-align: left !important; display: flex !important; justify-content: flex-start !important; font-size: 16px !important; font-weight: 800 !important; color: #2C2A29 !important; white-space: pre-wrap !important; line-height: 1.6 !important; transition: all 0.2s ease !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important; }
.stButton > button:hover { background-color: #FDFCFB !important; border-color: #C4A47C !important; transform: translateY(-2px) !important; box-shadow: 0 8px 12px rgba(0,0,0,0.05) !important; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. Z드라이브 이미지 연동 함수
def get_media_html(filename):
    if not filename or filename == "nan":
        return "<div class='product-emoji'>📦</div>"
    
    filename = str(filename).strip()
    ext = filename.split('.')[-1].lower()
    
    if ext in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
        return "<div class='product-emoji'>📜</div>"
        
    base_path = r"Z:\★업  무★\Ai\images"
    filepath = os.path.join(base_path, filename)
    
    if os.path.exists(filepath):
        try:
            with open(filepath, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            mime = "image/png" if ext == "png" else "image/jpeg"
            img_b64 = f"data:{mime};base64,{encoded}"
            return f"<img src='{img_b64}' style='width:100%; height:90px; object-fit:contain; margin-bottom:12px;'/>"
        except:
            pass
    return "<div class='product-emoji'>🖼️</div>"

# 4. 내장 데이터 (보안 DRM 회피용 하드코딩)
suppliers = [
    {
        "name": "한성전장(주)", "industry": "PCB",
        "hq": "경상남도 양산시", "kr": "경상남도 양산시", "gl": "해당 없음",
        "desc": "한성전장은 1993년 설립되어 자동차 부품, 가전 부품용 PCB 어셈블리 전문 기업입니다. 우수한 품질 관리 능력을 바탕으로 SQ 인증을 보유하고 있으며, 국내 주요 고객사에 핵심 전장 부품을 안정적으로 공급하고 있습니다.",
        "products": [
            {"name": "PCB", "file": "PCB.png"},
            {"name": "임가공(조립)", "file": "임가공(조립).png"}
        ],
        "certs": [{"name": "SQ 인증", "file": "SQ 인증.png"}],
        "locations": [
            {"name": "본사", "lat": 35.398579, "lon": 129.056037, "type": "hq", "address": "경남 양산시 상북면 소토로 23"},
            {"name": "양산공장", "lat": 35.398579, "lon": 129.056037, "type": "kr", "address": "경남 양산시 상북면 소토로 23"}
        ]
    },
    {
        "name": "효성전기(주)", "industry": "모터/제어기",
        "hq": "부산광역시 기장군", "kr": "충남 천안시", "gl": "중국 강소성, 인도 안드라프라데시, 베트남 하이퐁",
        "desc": "1973년 설립된 효성전기는 자동차용 모터 분야의 글로벌 선도 기업입니다. 브로워 모터, EPS 모터 등을 주력으로 생산하며, 국내는 물론 중국, 인도, 멕시코, 폴란드, 베트남 등 글로벌 네트워크를 구축하여 전 세계 고객 요구에 대응하고 있습니다.",
        "products": [
            {"name": "Blower Motor", "file": "Blower Motor.png"},
            {"name": "ABS Motor", "file": "ABS Motor.png"},
            {"name": "EPS Motor", "file": "EPS Motor.png"}
        ],
        "certs": [
            {"name": "IATF16949", "file": "IATF 16949 인증서-효성전기_국문.pdf"},
            {"name": "ISO 9001", "file": "ISO 9001 인증서_효성전기.pdf"}
        ],
        "locations": [
            {"name": "본사(명례공장)", "lat": 35.326756, "lon": 129.262846, "type": "hq", "address": "부산광역시 기장군 장안읍 명례산단5로 40"},
            {"name": "정관공장", "lat": 35.318413, "lon": 129.176662, "type": "kr", "address": "부산광역시 기장군 정관읍 산단4로 95-21"},
            {"name": "청계공장", "lat": 35.281146, "lon": 129.085023, "type": "kr", "address": "부산 금정구 팔송로 53 (청룡동)"},
            {"name": "중국 강소성", "lat": 31.984090, "lon": 118.739794, "type": "gl", "address": "중국 강소성 난징"},
            {"name": "인도 법인", "lat": 16.506174, "lon": 80.648015, "type": "gl", "address": "인도 안드라프라데시 비자야와다"},
            {"name": "베트남 하이퐁", "lat": 20.844911, "lon": 106.688084, "type": "gl", "address": "베트남 하이퐁"}
        ]
    }
]

# 5. 헤더 타이틀 출력
st.markdown("""
<div style="background-color: #2C2A29; padding: 30px 40px; border-radius: 12px; margin-bottom: 40px; border-bottom: 4px solid #C4A47C; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
    <div class="main-title">🌍 글로벌 SCM 및 파트너사 인프라 분석</div>
</div>
""", unsafe_allow_html=True)

# 6. 사이드바 구성
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
    options_sidebar = ["🏠 종합 메인 화면"] + [s["name"] for s in filtered]
    selected_name = st.radio("📊 분석할 업체 선택", options_sidebar, on_change=reset_map_view)

# 7. 메인 화면 렌더링
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

        st.markdown("<div class='section-title'>핵심 역량 및 품질 인증</div>", unsafe_allow_html=True)
        col_prod, col_cert = st.columns([1, 1])

        with col_prod:
            st.markdown("<div style='border-right: 2px dashed #E5E0D8; padding-right: 30px; height: 100%;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #2C2A29 !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>📦 핵심 생산 품목</h4>", unsafe_allow_html=True)
            p_cols = st.columns(2)
            for idx, p in enumerate(selected['products']):
                media_html = get_media_html(p['file'])
                p_cols[idx % 2].markdown(
                    f"<div class='product-card' style='margin-bottom:15px;'>{media_html}<div class='product-title'>{p['name']}</div></div>",
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with col_cert:
            st.markdown("<div style='padding-left: 10px; height: 100%;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #2C2A29 !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>📜 품질 및 ESG 인증</h4>", unsafe_allow_html=True)
            c_cols = st.columns(2)
            for idx, c in enumerate(selected['certs']):
                media_html = get_media_html(c['file'])
                c_cols[idx % 2].markdown(
                    f"<div class='product-card' style='margin-bottom:15px;'>{media_html}<div class='product-title'>{c['name']}</div></div>",
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top: 50px;'>주요 거점 네트워크</div>", unsafe_allow_html=True)
        map_col, text_col = st.columns([1.8, 1])
        df_loc = pd.DataFrame(selected["locations"])

        with text_col:
            st.markdown("<p style='color:#C4A47C !important; font-weight:800; font-size:15px; margin-bottom:10px;'>🖱️ 거점을 클릭하면 지도가 이동합니다.</p>", unsafe_allow_html=True)
            st.button("🌍 전체 뷰", on_click=set_view, args=("전체 뷰",), use_container_width=True)
            
            if selected['hq'] != "-":
                st.write("")
                st.button(f"🏢 본사\n\n{selected['hq']}", on_click=set_view, args=("🏢 국내(본사)",), use_container_width=True)
            if selected['kr'] != "-":
                st.write("")
                st.button(f"🏭 지사\n\n{selected['kr']}", on_click=set_view, args=("🏭 국내(지사)",), use_container_width=True)
            if selected['gl'] not in ["해당 없음", "-", ""]:
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
