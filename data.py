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
            {"name": "중국 남경 사업장(설립예정)", "type": "gl_cn", "address": "No.9, Hengda Road, Nanjing, China", "lat": 32.0602, "lon": 118.7968, "country": "중국"},
            {"name": "중국 추저우 사업장(설립예정)", "type": "gl_cn", "address": "중국 안후이성 추저우시", "lat": 32.3024, "lon": 118.3186, "country": "중국"},
            {"name": "북미 사업장(설립예정)", "type": "gl_us", "address": "미국 오하이오 주", "lat": 39.9611, "lon": -82.9987, "country": "미국"}
        ]
    },
    {
        "name": "(주)한성전장",
        "industry": "임가공(조립)",
        "sub_industry": "자동차 전장 및 전자부품",
        "hq": "경남 양산 본사", 
        "kr": "부산 공장", 
        "gl": "-",
        "desc": "(주)한성전장은 첨단 생산설비와 축적된 기술을 바탕으로 고객 맞춤형 Motor 컨트롤러 및 배터리 모듈 부품을 적시에 공급하며, \n제품 기획부터 생산·평가까지 철저한 품질관리를 통해 고객만족과 신뢰를 실현하는 기업입니다.",
        "products": [
            "자동차용 센서 및 일반 전장품 / 자동차용 컨트롤러 / 전기차 배터리 부품 및 와이어 하네스"
        ],
        "certs": ["IATF16949", "ISO14001", "SQ 인증"],
        "customers": {"S&T MOTIV": 46, "효성전기": 20, "스타리온": 13, "현대모비스": 10, "기타": 11},
        "locations": [
            {"name": "양산 본사", "type": "hq", "address": "경남 양산시 상북면 소토리 650번지", "lat": 35.398579, "lon": 129.056037, "country": "대한민국"},
            {"name": "부산 공장", "type": "kr", "address": "부산광역시 금정구 남산동 974-34번지", "lat": 35.267605, "lon": 129.091172, "country": "대한민국"}
        ]
    },
    {
        "name": "(주)브이씨텍",
        "industry": "PCB",
        "sub_industry": "제어장치 및 전장품",
        "hq": "경기 군포 본사",
        "kr": "-",
        "gl": "-",
        "desc": "(주)브이씨텍은 철도차량용 추진제어장치 및 보조전원장치(APU), 전기차 및 골프카용 구동 인버터 등을 개발·제조하는 전력변환 및 제어장치 전문기업입니다.",
        "products": ["철도차량용 전장품/골프카용 전장품/전기차용 전장품"],
        "certs": ["IATF16949", "ISO14001"],
        "customers": {"현대로템": 50, "CT&T": 30, "Fulu Motor": 10, "기타": 10},
        "locations": [
            {"name": "(주)브이씨텍 본사 및 공장", "type": "hq", "address": "경기도 군포시 엘에스로45번길 107", "lat": 37.3601, "lon": 126.9535, "country": "대한민국"}
        ]
    },
    {
        "name": "(주)상농전선",
        "industry": "가공(MAGNET WIRE)",
        "sub_industry": "에나멜선 및 절연코드",
        "hq": "경남 양산 본사",
        "kr": "-",
        "gl": "-",
        "desc": "(주)상농전선은 2003년 설립되어 에나멜 와이어, 절연코드 및 기기 내부 배선용 리드와이어 등을 전문적으로 제조하는 기업으로, KS, UL, ISO 등 다양한 품질 인증을 바탕으로 신뢰받는 제품을 공급하고 있습니다.",
        "products": [
            "에나멜 와이어"
        ],
        "certs": ["IATF 16949", "ISO 14001"],
        "customers": {"국내 가전 및 전장업체": 70, "기타 대리점": 30},
        "locations": [
            {"name": "(주)상농전선 본사 및 공장", "type": "hq", "address": "경상남도 양산시 유산공단9길 6-1", "lat": 35.3560, "lon": 129.0250, "country": "대한민국"}
        ]
    },
    {
        "name": "(주)김천베아링",
        "industry": "Bearing",
        "sub_industry": "Rotary Components/Actuator",
        "hq": "부산 본사",
        "kr": "경기 지사",
        "gl": "-",
        "desc": "(주)김천베아링은 한국NMB(MinebeaMitsumi)의 공식 지정 대리점으로서 미니어처 볼베어링, 스테핑 모터, 팬 모터 및 레졸버 등 첨단 정밀 부품을 자동차 부품 및 가전 산업 분야에 적기 공급하는 유통 전문기업입니다.",
        "products": [
            "미니어처 볼베어링 / 스테핑 모터 / 팬 모터 / 레졸버 및 정밀기계부품"
        ],
        "certs": ["MAIN-BIZ", "공식 대리점 인증"],
        "customers": {"현대모비스": 40, "LG마그나": 30, "SNT모티브": 20, "기타": 10},
        "locations": [
            {"name": "부산 본사", "type": "hq", "address": "부산광역시 사상구 새벽로167번길 85-6(감전동)", "lat": 35.1538, "lon": 128.9830, "country": "대한민국"},
            {"name": "경기 지사", "type": "kr", "address": "경기도 성남시 분당구", "lat": 37.3827, "lon": 127.1189, "country": "대한민국"},
            {"name": "부산 물류창고", "type": "kr", "address": "부산광역시 강서구 대저동", "lat": 35.2155, "lon": 128.9813, "country": "대한민국"}
        ]
    },
    # 💡 새롭게 추가된 업체 정보
    {
        "name": "한국NMB(주)",
        "industry": "Bearing",
        "sub_industry": "Rotary Components/Actuator",
        "hq": "부산 본사",
        "kr": "모덕 및 경기 사무소",
        "gl": "중국 법인",
        "desc": "글로벌 네트워크를 기반으로 Ball Bearing 및 Rotary Components(Actuator) 등 정밀기계 부품을 전문적으로 생산 및 공급하는 기업입니다.",
        "products": [
            "Ball Bearing",
            "Rotary Components/Actuator"
        ],
        "certs": [], 
        "customers": {}, 
        "locations": [
            {"name": "본사", "type": "hq", "address": "부산광역시 사상구 새벽로 167번길 85-6(감전동, 제1,2,3,4층 제에이동호)", "lat": 35.1538, "lon": 128.9830, "country": "대한민국"},
            {"name": "모덕Office", "type": "kr", "address": "부산광역시 사상구 모덕로 57 3층", "lat": 35.1743, "lon": 128.9822, "country": "대한민국"},
            {"name": "경기(분당)사무소", "type": "kr", "address": "경기도 성남시 분당구 황새울로 360번길 21 신영펠리스타워11층", "lat": 37.3827, "lon": 127.1189, "country": "대한민국"},
            {"name": "중국(소주)법인", "type": "gl_cn", "address": "3-103 No.61 Jiepu Road SIP, 215126 Suzhou, China", "lat": 31.3285, "lon": 120.7850, "country": "중국"}
        ]
    }
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
    },
    "(주)한성전장": {
        "prod_imgs": [
            "http://hansungeec.co.kr/data/editor/2303/68f8713e9ce1b074a95162e5d3d4e265_1679371328_4312.png"
        ],
        "cert_imgs": [
            "http://www.hansungeec.co.kr/data/file/sub0204/thumb-3730931109_k4BbP3Xf_4b392b2ae34b33eca5ce6b46f911883a7c81ca00_800x600.jpg",
            "http://www.hansungeec.co.kr/data/file/sub0204/thumb-3730931109_2nYRHtuK_ddc0920cf4043d7d29869df505f78a0cad78dd9f_800x600.jpg",
            "http://www.hansungeec.co.kr/data/file/sub0204/thumb-3730931109_lKOVB7QU_592a0b51d658de8d226c4d807cdfa8928f2ad0e6_800x600.jpg"
        ]
    },
    "(주)브이씨텍": {
        "prod_imgs": [
            "http://www.vctech.co.kr/data/file/s2_1/thumb-1935335402_tQVnDyF3_385c1a0d238922837141fa6ad27fc6dc7970737a_1320x658.jpg",
            "http://www.vctech.co.kr/data/file/s2_2/thumb-1935335402_V29TJaYb_44f0acae6d689f722c1459c9b63470dd91ebd019_1320x656.jpg",
            "http://www.vctech.co.kr/data/file/s2_3/thumb-1935335402_7v6DUh92_5097fe52bb7984fa8ef695134836f25e92075f8c_1320x656.jpg"
        ],
        "cert_imgs": [
            "http://www.vctech.co.kr/data/file/s3_6/1935335402_pckJlNFe_d2e70ac413b6da88f760445d8c245b03d0570a88.jpg",
            "http://www.vctech.co.kr/data/file/s3_6/1935335402_WO2iTjL6_2cc23dbe35e8db9898584bc1ebe7cc649d2f5df8.jpg"
        ]
    },
    "(주)상농전선": {
        "prod_imgs": [
            "https://www.snccable.co.kr/_product/photo/12_1.jpg"
        ],
        "cert_imgs": [
            "https://www.snccable.co.kr/_company/image/certiA16949.gif",
            "https://www.snccable.co.kr/_company/image/certiA14001.gif"
        ]
    },
    "(주)김천베아링": {
        "prod_imgs": [
            "http://www.kimchunbrg.com/images/main/visual_01.jpg",
            "http://www.kimchunbrg.com/images/main/visual_02.jpg"
        ],
        "cert_imgs": [
            "http://www.kimchunbrg.com/images/sub/cert_01.jpg"
        ]
    },
    # 💡 새롭게 추가된 업체 이미지 매핑
    "한국NMB(주)": {
        "prod_imgs": [
            "https://product.minebeamitsumi.com/en/product/category/bearing/spherical/__icsFiles/afieldfile/2026/01/14/file_01_90.png",
            "https://product.minebeamitsumi.com/en/product/category/rotary/steppingmotor/hybrid/__icsFiles/afieldfile/2024/08/02/hybrid_1.png"
        ],
        "cert_imgs": []
    }
}

# 3. 글로벌 네트워크 (지도 시각화) 관련 설정값 모음
map_view_mapping = {
    "전체 뷰": "all",
    "🏢 국내(본사)": "hq",
    "🏭 국내(지사)": "kr",
    "🌐 해외(중국)": "gl_cn",
    "🌎 해외(북미)": "gl_us"
}

location_colors = {
    "hq": [220, 38, 38, 255],     
    "kr": [37, 99, 235, 255],     
    "gl_cn": [16, 185, 129, 255], 
    "gl_us": [245, 158, 11, 255], 
    "default_dim": [148, 163, 184, 100], 
    "all_view": [196, 164, 124, 220]     
}

map_radius_settings = {
    "all_view": 120000,
    "highlighted": 300000,
    "dimmed": 40000
}
