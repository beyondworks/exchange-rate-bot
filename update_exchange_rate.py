import requests
from datetime import datetime

NOTION_TOKEN = "ntn_Mji634367343MHzgvNieIudYbIjS6wca8HvHmM13C9Z6uo력"
DATABASE_ID = "1e3003c7f7be819b880ac6b5d6a10fe7"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_exchange_rates():
    api_key = "QBso6Jd7FDgbzTUsxz2ZFtFTJHtFpUNG"
    today = datetime.now().strftime("%Y%m%d")
    url = f"https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey={api_key}&searchdate={today}&data=AP01"
    res = requests.get(url)
    data = res.json()
    print("API 응답:", data)

    rates = {}
    for item in data:
        if item['cur_unit'] == 'USD':
            rates['USD'] = float(item['deal_bas_r'].replace(',', ''))
        elif item['cur_unit'] == 'EUR':
            rates['EUR'] = float(item['deal_bas_r'].replace(',', ''))
        elif item['cur_unit'] == 'JPY(100)':
            rates['JPY'] = round(float(item['deal_bas_r'].replace(',', '')) / 100, 2)
    print("최종 환율:", rates)
    return rates

def get_all_rows():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    res = requests.post(url, headers=headers)
    return res.json()["results"]

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
    requests.patch(url, headers=headers, json=data)

if __name__ == "__main__":
    rates = get_exchange_rates()
    rows = get_all_rows()
    for row in rows:
        update_row(row["id"], rates)
    print("환율 자동 업데이트 완료!") 
