import requests
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("exchange_rate_update.log"), logging.StreamHandler()]
)

NOTION_TOKEN = "ntn_Mji634367343MHzgvNieIudYbIjS6wca8HvHmM13C9Z6uo"
DATABASE_IDS = [
    "1e3003c7f7be819b880ac6b5d6a10fe7",
    "1d7003c7f7be804cabbdef6bba0d929d"
]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_exchange_rates():
    api_key = "8c5c329c0edccb20c422ae70"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/KRW"
    
    try:
        res = requests.get(url)
        res.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        data = res.json()
        
        if data['result'] != 'success':
            raise Exception(f"환율 API 응답 오류: {data}")
        
        # 모든 환율을 1단위 기준으로 통일
        usd_krw = 1 / data['conversion_rates']['USD']
        eur_krw = 1 / data['conversion_rates']['EUR']
        jpy_krw = 1 / data['conversion_rates']['JPY']  # 1엔 기준으로 수정
        
        rates = {
            "USD": round(usd_krw, 2),
            "EUR": round(eur_krw, 2),
            "JPY": round(jpy_krw, 2)
        }
        logging.info(f"환율 정보 조회 성공: {rates}")
        return rates
        
    except requests.exceptions.RequestException as e:
        logging.error(f"환율 API 호출 중 오류 발생: {e}")
        raise

def get_all_rows(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    try:
        res = requests.post(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        return data["results"]
    except Exception as e:
        logging.error(f"데이터베이스 {database_id} 조회 중 오류: {e}")
        raise

def get_current_jpy_value(row):
    try:
        # 노션 API 응답 구조에 맞게 조정 필요
        if "properties" in row and "엔화(JPY) 환율" in row["properties"]:
            return row["properties"]["엔화(JPY) 환율"]["number"]
    except Exception as e:
        logging.error(f"JPY 값 추출 중 오류: {e}")
    return None

def fix_existing_jpy_data(database_id):
    rows = get_all_rows(database_id)
    fixed_count = 0
    
    for row in rows:
        page_id = row["id"]
        current_jpy = get_current_jpy_value(row)
        
        if current_jpy and current_jpy > 1000:  # 값이 비정상적으로 크면
            new_jpy = current_jpy / 100
            
            try:
                url = f"https://api.notion.com/v1/pages/{page_id}"
                data = {
                    "properties": {
                        "엔화(JPY) 환율": {"number": new_jpy}
                    }
                }
                res = requests.patch(url, headers=headers, json=data)
                res.raise_for_status()
                fixed_count += 1
                logging.info(f"페이지 {page_id}의 JPY 환율을 {current_jpy}에서 {new_jpy}로 수정했습니다.")
            except Exception as e:
                logging.error(f"페이지 {page_id} 업데이트 중 오류: {e}")
    
    return fixed_count

def update_row(page_id, rates):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "properties": {
            "달러(USD) 환율": {"number": rates.get("USD", 0)},
            "유로(EUR) 환율": {"number": rates.get("EUR", 0)},
            "엔화(JPY) 환율": {"number": rates.get("JPY", 0)},
            "날짜": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
        }
    }
    
    try:
        res = requests.patch(url, headers=headers, json=data)
        res.raise_for_status()
        logging.info(f"페이지 {page_id} 환율 업데이트 성공")
    except Exception as e:
        logging.error(f"페이지 {page_id} 업데이트 중 오류: {e}")

if __name__ == "__main__":
    try:
        logging.info("환율 업데이트 스크립트 시작")
        
        # 기존 데이터 수정 (일회성)
        total_fixed = 0
        for db_id in DATABASE_IDS:
            fixed = fix_existing_jpy_data(db_id)
            total_fixed += fixed
        
        logging.info(f"총 {total_fixed}개의 JPY 환율 데이터 수정 완료")
        
        # 새 환율로 업데이트
        rates = get_exchange_rates()
        for db_id in DATABASE_IDS:
            rows = get_all_rows(db_id)
            for row in rows:
                update_row(row["id"], rates)
        
        logging.info("모든 데이터베이스에 환율 자동 업데이트 완료!")
    
    except Exception as e:
        logging.error(f"스크립트 실행 중 예외 발생: {e}")
