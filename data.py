# data.py
# 💡 앞으로 새로운 업체가 추가되면 이 파일만 수정하시면 됩니다!

# 1. 업체 상세 정보 리스트
suppliers_data = [
    {
        "name": "(주)성우",
        "industry": "PRESS(CASE)", 
        "sub_industry": "2차전지 및 전장부품",
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
    # ⬇️ 여기에 3번째, 4번째 등 10개 업체를 계속 이어서 추가하시면 됩니다! (복사+붙여넣기 활용)
]


# 2. 업체별 이미지 URL 딕셔너리
excel_img_data = {
    "(주)성우": {
        "prod_imgs": [
            "https://www.e-sungwoo.co.kr/img/sub/prd_111.jpg", 
            "https://www.e-sungwoo.co.kr/img/sub/prd_112.jpg"
        ],
        "cert_imgs": [
            "https://www.e-sungwoo.co.kr/img/sub/cpn-wp1_2.jpg"
        ]
    }
    # ⬇️ 여기에 다른 업체의 이미지도 추가해주세요. (업체명이 위 리스트의 name과 똑같아야 합니다)
}
