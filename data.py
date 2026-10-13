# data.py

# 💡 새로운 업체가 추가될 때는 아래 리스트에 동일한 양식으로 추가하시면 됩니다.

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
            {"name": "중국 남경 사업장", "type": "gl_cn", "address": "No.9, Hengda Road, Nanjing, China", "lat": 32.0602, "lon": 118.7968, "country": "중국"},
            {"name": "중국 추저우 사업장", "type": "gl_cn", "address": "중국 안후이성 추저우시", "lat": 32.3024, "lon": 118.3186, "country": "중국"},
            {"name": "북미 사업장", "type": "gl_us", "address": "미국 오하이오 주", "lat": 39.9611, "lon": -82.9987, "country": "미국"}
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
    }
    # ➕ 여기에 새로운 업체 딕셔너리를 계속 추가하시면 됩니다.
]

# 2. 업체별 이미지 URL 딕셔너리
# 💡 업체명(name)과 키값이 정확히 일치해야 이미지를 불러올 수 있습니다.
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
    }
}

# 3. 글로벌 네트워크 (지도 시각화) 관련 설정값 모음
# 버튼 레이블(View명)과 내부 코드(type)를 매핑합니다.
map_view_mapping = {
    "전체 뷰": "all",
    "🏢 국내(본사)": "hq",
    "🏭 국내(지사)": "kr",
    "🌐 해외(중국)": "gl_cn",
    "🌎 해외(북미)": "gl_us"
}

# 거점 타입별 마커(점) 색상 [R, G, B, A]
location_colors = {
    "hq": [220, 38, 38, 255],     # 빨강 (본사)
    "kr": [37, 99, 235, 255],     # 파랑 (국내 지사)
    "gl_cn": [16, 185, 129, 255], # 초록 (중국)
    "gl_us": [245, 158, 11, 255], # 주황 (북미)
    "default_dim": [148, 163, 184, 100], # 선택되지 않은 거점(희미하게)
    "all_view": [196, 164, 124, 220]     # 전체 뷰일 때의 공통 색상
}

# 지도 렌더링 시 반경(마커 크기) 설정값
map_radius_settings = {
    "all_view": 120000,
    "highlighted": 300000,
    "dimmed": 40000
}
