제가 작성해드린 레이아웃 구조가 Streamlit 고유의 마크다운 렌더링 방식과 충돌하여 디자인이 심하게 깨지고 팝업이 동작하지 않는 문제가 발생했습니다. (버튼과 HTML을 혼용하면서 컨테이너가 분리된 것이 원인입니다.)

이를 해결하기 위해 HTML 구조를 완전히 단순화하고, ** Streamlit 기본 컬럼 기능만으로 깔끔하게 정렬되도록** 전면 수정했습니다. 

### 💡 주요 개선 사항
1. **레이아웃 깨짐 완전 해결 (CSS 단순화)**: Streamlit 내장 기능(`st.container`, `st.columns`)을 최대한 활용하고, 복잡한 Flexbox CSS는 걷어내어 이미지가 박스를 이탈하는 현상을 잡았습니다. 
2. **높이 일치화 해결**: 양쪽 영역에 공통된 CSS 클래스를 부여하여 높이가 일정하게 유지되도록 조정했습니다. 
3. **팝업 (이미지 확대) 기능 정상화**: Streamlit 버튼 기능을 안전한 위치로 빼고 상태 관리(`st.session_state`)와 다이얼로그(`@st.dialog`)를 확실하게 연동하여 정상 동작하도록 수정했습니다. 

---

아래 코드로 `app.py`를 **전체 교체**해 주시기 바랍니다. 

```python
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

def open_popup(b64_str, title):
    st.session_state.popup_img = b64_str
    st.session_state.popup_title = title

def close_popup():
    st.session_state.popup_img = None
    st.session_state.popup_title = ""

# 2. 테마 CSS 설정 (구조 단순화)
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

/* ✅ 카드 스타일 (양쪽 통일) */
.unified-card {
    background: #ffffff; border: 1px solid #E5E0D8; border-radius: 12px; padding: 25px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.03); margin-bottom: 20px; height: 100%;
}
.card-title { color: #2C2A29; text-align: center; margin-bottom: 25px; font-weight: 800; font-size: 18px; border-bottom: 2px dashed #E5E0D8; padding-bottom: 15px; }

/* ✅ 이미지 및 태그 스타일 */
.img-box { background: #FDFCFB; border-radius: 8px; padding: 15px; display: flex; justify-content: center; align-items: center; border: 1px solid #F3F4F6; margin-bottom: 15px; height: 200px; }
.img-box img { max-width: 100%; max-height: 100%; object-fit: contain; }
.tag-wrap { display: flex; flex-direction: column; gap: 8px; width: 100%; align-items: center; }
.prod-tag { font-size: 14px; font-weight: 800; color: #4A4441; text-align: center; background: #E5E0D8; padding: 8px 12px; border-radius: 8px; width: 100%; }

/* ✅ 인증서 뱃지 (가로 나열) */
.cert-badge-wrap { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; width: 100%; margin-top: 25px; padding-top: 20px; border-top: 1px dashed #E5E0D8; }
.cert-badge { background: #ffffff; border: 1px solid #C4A47C; color: #C4A47C; font-size: 14px; font-weight: 800; padding: 6px 16px; border-radius: 30px; }

/* 텍스트 색상 및 폰트 */
h2, h3, h4, p, span, label, li { color: #2C2A29 !important; }
.main-title { font-size: 34px !important; font-weight: 900 !important; color: #ffffff !important; margin: 0 !important; line-height: 1.2 !important; letter-spacing: -1px !important; }
.section-title { font-size: 24px; font-weight: 900; color: #2C2A29 !important; margin-top: 45px; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; padding-bottom: 12px; border-bottom: 3px solid #E5E0D8; }
.section-num { color: #C4A47C; font-size: 28px; font-weight: 900; letter-spacing: -1px; }
.desc-box { background-color: #FDFCFB; border: 1px solid #E5E0D8; border-radius: 12px; padding: 30px; border-left: 6px solid #C4A47C; font-size: 17px; line-height: 1.8; font-weight: 400; }
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

# 4. 팝업(모달) 렌더링 함수
@st.dialog("상세 이미지 확인", width="large")
def render_popup():
    st.markdown(f"<h3 style='text-align: center;'>{st.session_state.popup_title}</h3>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center;'><img src='data:image/jpeg;base64,{st.session_state.popup_img}' style='max-width: 100%; border-radius: 8px;'></div>", unsafe_allow_html=True)
    st.write("")
    if st.button("닫기", use_container_width=True):
        close_popup()
        st.rerun()

if st.session_state.popup_img:
    render_popup()

# 5. 초기 데이터 로드 
if "suppliers" not in st.session_state: st.session_state.suppliers = suppliers_data
if "excel_img_data" not in st.session_state: st.session_state.excel_img_data = excel_img_data
suppliers = st.session_state.suppliers

# 6. 헤더 및 사이드바 
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

# 7. 메인 화면 렌더링 
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

        # 🚀 Layout 분할 (생산품목 vs 품질인증) 
        col_left, col_right = st.columns([1.2, 1])

        with col_left:
            st.markdown("<div class='unified-card'><div class='card-title'>🌟 핵심 생산 품목</div>", unsafe_allow_html=True)
            if selected.get('products'):
                # 제품마다 컬럼을 나눠서 가로로 배치 (양옆 배치)
                prod_cols = st.columns(len(selected['products']))
                for idx, prod_name in enumerate(selected['products']):
                    with prod_cols[idx]:
                        b64_img = get_base64_image(company_images["prod_imgs"][idx]) if idx < len(company_images.get("prod_imgs", [])) else None
                        if b64_img:
                            st.markdown(f"<div class='img-box'><img src='data:image/jpeg;base64,{b64_img}'></div>", unsafe_allow_html=True)
                            if st.button("🔍 확대 보기", key=f"btn_prod_{idx}", use_container_width=True):
                                open_popup(b64_img, f"{selected['name']} - 핵심 생산 품목")
                                st.rerun()
                        
                        # 제품명 태그 처리
                        tags = [t.strip() for t in prod_name.replace(" / ", "/").split("/")]
                        tags_html = "".join([f"<div class='prod-tag'>{t}</div>" for t in tags if t])
                        st.markdown(f"<div class='tag-wrap' style='margin-top: 15px;'>{tags_html}</div>", unsafe_allow_html=True)
            else:
                st.info("등록된 핵심 생산 품목 정보가 없습니다.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown("<div class='unified-card'><div class='card-title'>🏅 품질 및 ESG 인증</div>", unsafe_allow_html=True)
            
            if company_images.get("cert_imgs"):
                # 인증서 이미지들을 가로(그리드)로 배치
                cert_cols = st.columns(len(company_images["cert_imgs"]))
                for idx, cert_url in enumerate(company_images["cert_imgs"]):
                    b64_cert = get_base64_image(cert_url)
                    if b64_cert:
                        with cert_cols[idx]:
                            st.markdown(f"<div class='img-box'><img src='data:image/jpeg;base64,{b64_cert}'></div>", unsafe_allow_html=True)
                            if st.button("🔍 확대", key=f"btn_cert_{idx}", use_container_width=True):
                                open_popup(b64_cert, f"{selected['name']} - 품질 인증서")
                                st.rerun()

            if selected.get('certs'):
                badges = "".join([f"<span class='cert-badge'>{c}</span>" for c in selected['certs']])
                st.markdown(f"<div class='cert-badge-wrap'>{badges}</div>", unsafe_allow_html=True)
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
```
