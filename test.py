import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def save_legion_power_to_excel(nicknames):
    options = Options()
    # 인원이 많으므로 효율을 위해 headless 모드 권장 (창을 보고 싶으시면 주석 처리하세요)
    options.add_argument("--headless") 
    options.add_argument("--window-size=1200,800")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    results = []

    print(f"🚀 총 {len(nicknames)}명의 데이터 수집을 시작합니다. 잠시만 기다려 주세요...")

    for i, name in enumerate(nicknames):
        try:
            # 다이렉트 검색 URL 접속 (서버 2014 기준)
            target_url = f"https://aion2.plaync.com/ko-kr/characters/index?race=2&serverId=2014&keyword={name}"
            driver.get(target_url)
            
            # 1. 검색 결과 리스트에서 첫 번째 항목 클릭
            first_item = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "search-result__item")))
            first_item.click()
            
            # 2. 상세 페이지에서 전투력 추출
            power_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".profile__info-power-level span")))
            power_val = power_element.text
            
            results.append({"닉네임": name, "전투력": power_val, "상태": "성공"})
            print(f"[{i+1}/{len(nicknames)}] {name}: {power_val} 완료")

        except Exception:
            print(f"[{i+1}/{len(nicknames)}] {name}: 실패 (캐릭터 없음 또는 로딩 지연)")
            results.append({"닉네임": name, "전투력": "-", "상태": "실패"})
        
        # 서버 부하 방지를 위한 미세한 간격
        time.sleep(0.5)

    driver.quit()
    
    # 데이터프레임 생성 및 엑셀 저장
    df = pd.DataFrame(results)
    file_name = "아이온2_레기온_전투력_현황.xlsx"
    df.to_excel(file_name, index=False)
    
    print("\n" + "="*45)
    print(f"✨ 수집 완료! 파일이 생성되었습니다: {file_name}")
    print("="*45)

# ---------------------------------------------------------
# 요청하신 전체 닉네임 리스트 (104명)
# ---------------------------------------------------------
legion_list = [
    "태윈", "연하", "존귀", "천뢰", "태식", "hori", "i힐i", "NAVER", "걱정마", "건투",
    "검성창팔", "결사단", "골D로저", "공", "공격수", "공대", "구릉", "궁무신", "궁슈", "기몽",
    "까칠한송이", "꿩", "끵뀽", "나마쵸조", "누구냐넌", "달험", "당근", "대령", "대정령사", "도람치유",
    "도람푸틴", "도움", "돈워리", "돌돌", "돌풍", "뒤치기전문", "디뉴", "또치뭉치", "레바태윈", "로윈",
    "마강", "마라탱", "목화맛쿠키", "몰", "므므", "미즈", "민하", "밍젤", "병사", "뽀쁠",
    "사단", "살추", "상상", "샤르티아", "선다간판", "성연", "소름", "슌", "신짱구", "신철수",
    "쌰", "양말", "엔터", "우우우", "월연", "유뚱", "유스티아", "윤디", "윤미", "이향",
    "인우", "인하", "잉잉", "자네", "전투힐러", "조이궁박휘", "조이성박휘", "조이호박휘", "죠아요", "중령",
    "참새", "천화", "체링", "치루성", "칼리온", "칼세이건", "큐나", "크림카레", "킹받은링크", "타나타토스",
    "탑건", "태풍", "탱쿠", "팻멉", "펭", "푸하", "할리", "햄니", "호키", "화려", "히메사마"
]

# 실행
if __name__ == "__main__":
    save_legion_power_to_excel(legion_list)