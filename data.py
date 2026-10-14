import streamlit as st

# ==========================================
# 1. 데이터 정의 (업데이트된 유니온머티리얼즈 반영)
# ==========================================
suppliers_data = [
    # ... (생략된 다른 기업 데이터는 필요시 기존 코드에서 복사해 넣으시면 됩니다) ...
    {
        "name": "유니온머티리얼즈",
        "industry": "소결(MAGNET)", 
        "sub_industry": "자동차 및 전기전자용 부품소재",
        "hq": "대구 본사", 
        "kr": "포항 공장", 
        "gl": "중국 및 베트남 법인",
        "desc": "유니온머티리얼즈는 2000년 설립된 파인세라믹스 및 자성재료 전문 기업으로, 페라이트 마그네트, 세라믹 절삭공구, 산업용 세라믹 부품 등을 생산해 전 세계 자동차, 전기전자, 기계 산업에 핵심 소재를 공급하고 있습니다.",
        "products": [
            "파인세라믹스",
            "페라이트마그네트"
        ],
        "certs": [
            "KSA-ISO-인증서",
            "품질/환경경영 시스템 인증"
        ],
        "customers": {"Bosch 등 글로벌 부품사": 50, "국내 자동차/모터 부품사": 30, "가전/전자부품사": 15, "기타": 5},
        "locations": [
            {"name": "대구 본사 및 공장", "type": "hq", "address": "대구광역시 달서구 성서공단남로 151(월암동)", "lat": 35.8364, "lon": 128.4837, "country": "대한민국"},
            {"name": "포항 공장", "type": "kr", "address": "경상북도 포항시 남구 대송로", "lat": 35.9904, "lon": 129.3800, "country": "대한민국"},
            {"name": "중국 법인(유니온툴텍공구)", "type": "gl_cn", "address": "중국 허베이성 싼허시 옌자오", "lat": 39.9500, "lon": 116.8167, "country": "중국"}
        ]
    }
]

excel_img_data = {
    # ... (생략된 다른 기업 이미지는 필요시 기존 코드에서 복사) ...
    "유니온머티리얼즈": {
        "prod_imgs": [
            "https://unionmaterials.com/kor/images/products/01_02_img_02.jpg",
            "https://unionmaterials.com/kor/images/products/01_02_img_03.jpg"
        ],
        "cert_imgs": [
            "https://unionmaterials.com/kor/images/products/01_img_02.gif",
            "https://unionmaterials.com/kor/images/products/02_img_03.gif"
        ]
    }
}

# ==========================================
# 2. 화면 렌더링 (UI 구성)
# ==========================================
# CSS 스타일링 (배지, 박스 등)
st.markdown("""
    <style>
    .badge-industry { background-color: #d4b886; color: white; padding: 4px 12px; border-radius: 4px; font-size: 14px; font-weight: bold; margin-right: 8px;}
    .badge-sub { border: 1px solid #ccc; color: #555; padding: 4px 12px; border-radius: 4px; font-size: 14px;}
    .desc-box { border-left: 4px solid #d4b886; background-color: #f9f9f9; padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 30px; font-size: 15px; color: #333;}
    .pill-btn { display: inline-block; border: 1px solid #d4b886; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: bold; color: #333; margin: 4px; background: white;}
    </style>
""", unsafe_allow_html=True)

# 현재 선택된 업체 (테스트용 하드코딩)
target_company = "유니온머티리얼즈"
company_info = next((item for item in suppliers_data if item["name"] == target_company), None)
company_imgs = excel_img_data.get(target_company, {"prod_imgs": [], "cert_imgs": []})

if company_info:
    # --- 타이틀 영역 ---
    st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 30px;'>
            <h1 style='margin: 0; padding: 0;'>{company_info['name']}</h1>
            <span class='badge-industry'>{company_info['industry']}</span>
            <span class='badge-sub'>{company_info['sub_industry']}</span>
        </div>
    """, unsafe_allow_html=True)

    # --- 01. 기업 개요 ---
    st.markdown("### 01. 기업 개요")
    st.markdown(f"<div class='desc-box'>📖 {company_info['desc']}</div>", unsafe_allow_html=True)

    # --- 02. 핵심 역량 및 품질 인증 ---
    st.markdown("### 02. 핵심 역량 및 품질 인증")
    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h5 style='text-align: center;'>🌟 핵심 생산 품목</h5>", unsafe_allow_html=True)
        # ✔️ 핵심 포인트: 여기서 이미지를 출력합니다!
        if company_imgs["prod_imgs"]:
            for i, img_url in enumerate(company_imgs["prod_imgs"]):
                st.image(img_url, caption=company_info["products"][i] if i < len(company_info["products"]) else "", use_column_width=True)
        else:
            st.write("등록된 이미지가 없습니다.")

    with col2:
        st.markdown("<h5 style='text-align: center;'>🏅 품질 및 ESG 인증</h5>", unsafe_allow_html=True)
        # ✔️ 핵심 포인트: 여기서 인증서 이미지를 출력합니다!
        if company_imgs["cert_imgs"]:
            for i, img_url in enumerate(company_imgs["cert_imgs"]):
                st.image(img_url, caption=company_info["certs"][i] if i < len(company_info["certs"]) else "", use_column_width=True)
        else:
            st.write("등록된 이미지가 없습니다.")

    # --- 03. 주요 고객사 ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 03. 주요 고객사")
    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
    
    customers_html = ""
    for customer, share in company_info["customers"].items():
        customers_html += f"<div class='pill-btn'>🤝 {customer} ({share}%)</div>"
    st.markdown(customers_html, unsafe_allow_html=True)
