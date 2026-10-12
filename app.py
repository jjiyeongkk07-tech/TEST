import streamlit as st
import pandas as pd
import pydeck as pdk
import base64
import os
import re
import requests

# 1. 페이지 설정
st.set_page_config(page_title="글로벌 SCM 분석", page_icon="🌍", layout="wide")

# [세션 상태 초기화] 지도 뷰 상태 관리
if "map_view" not in st.session_state:
    st.session_state.map_view = "전체 뷰"

def set_view(view):
    st.session_state.map_view = view

def reset_map_view():
    st.session_state.map_view = "전체 뷰"

# 2. 고급스러운 테마 CSS
css = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
html, body, [class*='css'] { font-family: 'Pretendard', sans-serif !important; }

/* 배경 */
.stApp { background: linear-gradient(135deg, #F9F8F6 0%, #EFEBE5 100%); }

/* 메인 대시보드 컨테이너 */
.block-container { 
    background-color: #ffffff; padding: 3rem 4rem !important; margin-top: 2rem; margin-bottom: 3rem;
    border-radius: 16px; max-width: 1400px; border: 1px solid #E5E0D8; box-shadow: 0 15px 35px rgba(100, 90, 80, 0.08);
}
header { visibility: hidden; } footer { visibility: hidden; }

/* 사이드바 스타일 */
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

# 3. 백엔드 함수 (이미지 로드, 위경도 지오코딩, 엑셀 파싱)
def get_media_html(filename):
    if pd.isna(filename) or not str(filename).strip():
        return "<div class='product-emoji'>📦</div>"
    
    filename = str(filename).strip()
    ext = filename.split('.')[-1].lower()
    
    # 문서는 아이콘으로 대체
    if ext in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
        return "<div class='product-emoji'>📜</div>"
        
    # Z드라이브 지정 경로에서 이미지 읽어오기
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

@st.cache_data
def geocode_korean_address(address):
    """오픈 API를 이용해 주소를 위도/경도로 변환합니다."""
    address = str(address).strip()
    
    # 누락 방지용 (엑셀 내 기존 데이터 매칭)
    if "소토로" in address and "23" in address: return 35.3986, 129.0560
    if "팔송로" in address and "53" in address: return 35.2811, 129.0850
    
    headers = {"User-Agent": "SCM-Dashboard/1.0"}
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json"
    try:
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code == 200 and res.json():
            return float(res.json()[0]['lat']), float(res.json()[0]['lon'])
    except:
        pass
    
    # 상세주소에서 건물 번호를 제외하고 시/군/구 단위로 재검색
    parts = address.split()
    if len(parts) >= 3:
        short_addr = " ".join(parts[:3])
        url = f"https://nominatim.openstreetmap.org/search?q={short_addr}&format=json"
        try:
            res = requests.get(url, headers=headers, timeout=3)
            if res.status_code == 200 and res.json():
                return float(res.json()[0]['lat']), float(res.json()[0]['lon'])
        except:
            pass
            
    return 37.5665, 126.9780  # 검색 불가 시 서울 시청 반환

@st.cache_data
def load_and_parse_excel(uploaded_file):
    try:
        # 엑셀 헤더는 2번째 줄(header=1)
        df_company = pd.read_excel(uploaded_file, sheet_name="업체 정보", header=1)
        df_location = pd.read_excel(uploaded_file, sheet_name="거점 정보", header=1)
        
        df_company = df_company.dropna(subset=['업체명'])
        df_location = df_location.dropna(subset=['업체명'])
        
        suppliers = []
        for _, row in df_company.iterrows():
            name = str(row['업체명']).strip()
            clean_name = re.sub(r'$주$|주식회사|\s', '', name) # 매칭용 텍스트 정제
            
            locs = []
            for _, lrow in df_location.iterrows():
                lname = str(lrow['업체명']).strip()
                lclean = re.sub(r'$주$|주식회사|\s', '', lname)
                
                # 업체명이 거점시트의 업체명과 매칭되면 좌표 생성
                if lclean in clean_name or clean_name in lclean:
                    lat, lon = lrow.get('위도(lat)', None), lrow.get('경도(lon)', None)
                    address = str(lrow.get('주소', ''))
                    
                    if pd.isna(lat) or pd.isna(lon):
                        lat, lon = geocode_korean_address(address)
                        
                    locs.append({
                        "name": str(lrow['거점명']),
                        "lat": float(lat), "lon": float(lon),
                        "type": str(lrow['거점유형(type)']),
                        "address": address
                    })
                    
            # 제품 분리 (콤마 단위)
            prod_str = str(row['핵심 생산 품목']) if not pd.isna(row['핵심 생산 품목']) else "제품 정보 없음"
            prod_file = row['핵심 생산 품목_파일명']
            prods = [{"name": p.strip(), "file": prod_file} for p in prod_str.split(',') if p.strip()]
            
            # 인증서 추출 로직 (파일명에서 확장자 떼고 이름 정리)
            cert_file = row['품질 및 ESG 인증_파일명']
            cert_name = "인증서/평가서"
            if pd.notna(cert_file) and isinstance(cert_file, str):
                cert_name = cert_file.split('.')[0].replace(name, '').replace('-', '').strip()
                
            certs = [{"name": cert_name if cert_name else "품질/ESG 인증", "file": cert_file}]
            
            suppliers.append({
                "name": name,
                "industry": str(row['업종']) if not pd.isna(row['업종']) else "미분류",
                "hq": str(row['본사 위치']) if not pd.isna(row['본사 위치']) else "-",
                "kr": str(row['국내 지사']) if not pd.isna(row['국내 지사']) else "-",
                "gl": str(row['해외 거점']) if not pd.isna(row['해외 거점']) else "해당 없음",
                "desc": str(row['기업 개요']) if not pd.isna(row['기업 개요']) else "기업 개요 정보가 없습니다.",
                "products": prods,
                "certs": certs,
                "locations": locs
            })
            
        return suppliers
    except Exception as e:
        st.error(f"엑셀 데이터를 읽는 중 오류가 발생했습니다: {e}")
        return []

# 4. 헤더 타이틀 출력
st.markdown("""
<div style="background-color: #2C2A29; padding: 30px 40px; border-radius: 12px; margin-bottom: 40px; border-bottom: 4px solid #C4A47C; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
    <div class="main-title">🌍 글로벌 SCM 및 파트너사 인프라 분석</div>
</div>
""", unsafe_allow_html=True)

# 5. 사이드바 구성 및 엑셀 데이터 로드
with st.sidebar:
    st.markdown("<h3 style='color:#C4A47C !important; font-weight:900;'>📂 데이터 업데이트</h3>", unsafe_allow_html=True)
    
    # 💡 엑셀 업로드 위젯
    uploaded_file = st.file_uploader("최신 SCM 엑셀 파일(.xlsx)을 업로드하세요", type=['xlsx'])
    
    suppliers = []
    if uploaded_file is not None:
        suppliers = load_and_parse_excel(uploaded_file)
    else:
        # 기본 파일 탐색 시도
        default_file = "글로벌 SCM 및 파트너사 인프라 분석.xlsx"
        if os.path.exists(default_file):
            suppliers = load_and_parse_excel(default_file)
        else:
            st.warning("👈 위에서 최신 SCM 엑셀 파일을 업로드해주세요.")
            st.stop()
            
    if not suppliers:
        st.warning("엑셀에 분석할 수 있는 데이터가 없습니다.")
        st.stop()

    st.markdown("<hr style='border-color: #E5E0D8; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#C4A47C !important; font-weight:900;'>🏢 필터 및 업체 검색</h3>", unsafe_allow_html=True)
    
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
    selected_name = st.radio("📊 상세 분석할 업체 선택", options_sidebar, on_change=reset_map_view)

# 6. 메인 화면 출력
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

else:
    # --- [상세 업체 화면] ---
    selected = next((s for s in filtered if s["name"] == selected_name), None)
    
    st.markdown(
        f"<div style='margin-bottom:25px; display:flex; align-items:baseline; gap: 15px;'>"
        f"<h2 style='margin:0; font-weight:900; font-size:42px; letter-spacing: -1px; color:#2C2A29 !important;'>{selected['name']}</h2>"
        f"<span style='background:#FDFCFB; border: 1px solid #C4A47C; color:#C4A47C !important; padding: 4px 12px; font-size: 15px; font-weight: 800; border-radius: 4px;'>{selected['industry']}</span></div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='section-title' style='margin-top:10px;'>기업 개요</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='desc-box'>{selected['desc']}</div>", unsafe_allow_html=True)

    # 🚀 핵심 역량 및 품질 인증
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

    # 🚀 거점 네트워크 
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
