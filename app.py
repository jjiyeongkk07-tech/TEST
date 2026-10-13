import urllib.request
import ssl

def safe_image_render(image_source):
    if isinstance(image_source, str) and image_source.startswith("http"):
        try:
            # 1. SSL 인증서 검증 강제 무시 (사내망 통신 에러 우회)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            # 2. 완벽한 크롬 브라우저인 것처럼 헤더 위조
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Referer': 'https://www.google.com/' # 구글에서 타고 들어온 것처럼 위장
            }
            req = urllib.request.Request(image_source, headers=headers)
            
            # 3. 타임아웃 5초 설정 후 이미지 가져오기
            response = urllib.request.urlopen(req, context=ctx, timeout=5)
            img_bytes = response.read()
            st.image(img_bytes, use_container_width=True)
            
        except Exception as e:
            # 어떤 이유로 막혔는지 에러 메시지 출력
            st.warning(f"다운로드 실패: {str(e)}") 
    else:
        st.image(image_source, use_container_width=True)
