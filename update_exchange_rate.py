import requests
from datetime import datetime

NOTION_TOKEN = "NOTION_TOKEN = "ntn_Mji634367343MHzgvNieIudYbIjS6wca8HvHmM13C9Z6uo"
"
DATABASE_ID = "1e3003c7f7be819b880ac6b5d6a10fe7"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_exchange_rates():
    # KRW 기준으로 USD, EUR, JPY 환율을 가져옴
    url = "https://api.exchangerate.host/latest?base=KRW&symbols=USD,EUR,JPY"
    res = requests.get(url)
    data = res.json()
    print("API 응답:", data)
    if 'rates' not in data:
        raise Exception(f"환율 API 응답 오류: {data}")
    usd_krw = 1 / data['rates']['USD']
    eur_krw = 1 / data['rates']['EUR']
    jpy_krw = 100 / data['rates']['JPY']  # 100엔 기준
    rates = {
        "USD": round(usd_krw, 2),
        "EUR": round(eur_krw, 2),
        "JPY": round(jpy_krw, 2)
    }
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
