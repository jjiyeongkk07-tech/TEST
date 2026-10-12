import streamlit as st
import pandas as pd
import pydeck as pdk
import base64
import os
from geopy.geocoders import Nominatim

# 1. 페이지 설정 (사이드바 기본 열림)
st.set_page_config(page_title="글로벌 SCM 분석", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

# =====================================================================
# 🎯 [엑셀 파일 경로 지정] 
# 알려주신 실제 파일명으로 경로를 설정했습니다.
# =====================================================================
EXCEL_PATH = r"Z:\★업  무★\Ai\글로벌 SCM 및 파트너사 인프라 분석.xlsx" 


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
    if not filename or pd.isna(filename) or str(filename).strip() == "":
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

# 4. 주소를 위도/경도로 변환하는 함수 (Geocoding)
@st.cache_data
def get_lat_lon(address):
    if not address or pd.isna(address):
        return 37.5665, 126.9780 
    try:
        geolocator = Nominatim(user_agent="scm_dashboard_agent")
        location = geolocator.geocode(address, timeout=5)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        pass
    return 37.5665, 126.9780

# 엑셀 데이터 파싱
@st.cache_data
def load_data(file_path):
    df_company = pd.read_excel(file_path, sheet_name='업체 정보')
    df_location = pd.read_excel(file_path, sheet_name='거점 정보')
    
    parsed_suppliers = []
    
    for _, row in df_company.iterrows():
        comp_name = str(row.get('업체명', '')).strip()
        industry = str(row.get('업종', '미분류')).strip()
        if not comp_name or comp_name == 'nan':
            continue
            
        products = []
        if pd.notna(row.get('핵심 생산 품목_파일명')) and str(row.get('핵심 생산 품목_파일명')).strip():
            products.append({"name": "핵심 생산 품목", "file": str(row['핵심 생산 품목_파일명']).strip()})
            
        certs = []
        cert_columns = {'IATF 16949_파일명': 'IATF 16949', 'ISO14001_파일명': 'ISO 14001', 'SQ인증_파일명': 'SQ 인증', 'ESG 경영 우수_파일명': 'ESG 경영 우수'}
        for col, cert_name in cert_columns.items():
            if pd.notna(row.get(col)) and str(row.get(col)).strip():
                certs.append({"name": cert_name, "file": str(row[col]).strip()})
                
        comp_locs = df_location[df_location['업체명'].astype(str).str.strip() == comp_name]
        locations = []
        for _, loc_row in comp_locs.iterrows():
            address = str(loc_row.get('주소', '')).strip()
            
            if '위도' in loc_row and '경도' in loc_row and pd.notna(loc_row['위도']) and pd.notna(loc_row['경도']):
                lat, lon = float(loc_row['위도']), float(loc_row['경도'])
            else:
                lat, lon = get_lat_lon(address) 
                
            locations.append({
                "name": str(loc_row.get('거점명', '')).strip(),
                "lat": lat,
                "lon": lon,
                "type": str(loc_row.get('구분', 'kr')).strip(),
                "address": address
            })
            
        parsed_suppliers.append({
            "name": comp_name,
            "industry": industry,
            "hq": str(row.get('본사', '-')).strip(),
            "kr": str(row.get('지사', '-')).strip(),
            "gl": str(row.get('해외 지점', '-')).strip(),
            "desc": str(row.get('기업 개요', '')).strip(),
            "products": products,
            "certs": certs,
            "locations": locations
        })
        
    return parsed_suppliers

# 5. 헤더 타이틀
st.markdown("""
<div style="background-color: #2C2A29; padding: 30px 40px; border-radius: 12px; margin-bottom: 40px; border-bottom: 4px solid #C4A47C; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
    <div class="main-title">🌍 글로벌 SCM 및 파트너사 인프라 분석</div>
</div>
""", unsafe_allow_html=True)

# 엑셀 파일 로드 및 에러 처리
if not os.path.exists(EXCEL_PATH):
    st.error(f"⚠️ 지정된 경로에 엑셀 파일이 없습니다: `{EXCEL_PATH}`\n\n해당 경로에 파일이 정확히 있는지 확인해주세요. (확장자가 .xls일 경우 코드의 경로를 수정해야 합니다.)")
    st.stop()

with st.spinner("엑셀 데이터를 분석 및 지도 좌표를 생성 중입니다..."):
    suppliers = load_data(EXCEL_PATH)

# 6. 사이드바 (필터 및 검색 구성)
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
        display_label = f"{s['name']} ({s['industry']})"
        options_sidebar_map[display_label] = s['name']
        
    selected_display_name = st.radio("📊 분석할 업체 선택", list(options_sidebar_map.keys()), on_change=reset_map_view)
    selected_name = options_sidebar_map[selected_display_name]

# 7. 메인 화면 출력
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
            if selected['products']:
                p_cols = st.columns(2)
                for idx, p in enumerate(selected['products']):
                    media_html = get_media_html(p['file'])
                    p_cols[idx % 2].markdown(
                        f"<div class='product-card' style='margin-bottom:15px;'>{media_html}<div class='product-title'>{p['name']}</div></div>",
                        unsafe_allow_html=True
                    )
            else:
                st.info("등록된 핵심 생산 품목 파일이 없습니다.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_cert:
            st.markdown("<div style='padding-left: 10px; height: 100%;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #2C2A29 !important; text-align: center; margin-bottom: 25px; font-weight: 800;'>📜 품질 및 ESG 인증</h4>", unsafe_allow_html=True)
            if selected['certs']:
                c_cols = st.columns(2)
                for idx, c in enumerate(selected['certs']):
                    media_html = get_media_html(c['file'])
                    c_cols[idx % 2].markdown(
                        f"<div class='product-card' style='margin-bottom:15px;'>{media_html}<div class='product-title'>{c['name']}</div></div>",
                        unsafe_allow_html=True
                    )
            else:
                st.info("등록된 품질 및 인증 파일이 없습니다.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top: 50px;'>주요 거점 네트워크</div>", unsafe_allow_html=True)
        map_col, text_col = st.columns([1.8, 1])
        df_loc = pd.DataFrame(selected["locations"])

        with text_col:
            st.markdown("<p style='color:#C4A47C !important; font-weight:800; font-size:15px; margin-bottom:10px;'>🖱️ 거점을 클릭하면 지도가 이동합니다.</p>", unsafe_allow_html=True)
            st.button("🌍 전체 뷰", on_click=set_view, args=("전체 뷰",), use_container_width=True)
            
            if selected['hq'] and selected['hq'] != "-" and selected['hq'] != "nan":
                st.write("")
                st.button(f"🏢 본사\n\n{selected['hq']}", on_click=set_view, args=("🏢 국내(본사)",), use_container_width=True)
            if selected['kr'] and selected['kr'] != "-" and selected['kr'] != "nan":
                st.write("")
                st.button(f"🏭 지사\n\n{selected['kr']}", on_click=set_view, args=("🏭 국내(지사)",), use_container_width=True)
            if selected['gl'] not in ["해당 없음", "-", "", "nan"]:
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
