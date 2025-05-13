import requests
from datetime import datetime
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
    res = requests.get(url)
    data = res.json()
    print("API 응답:", data)
    if data['result'] != 'success':
        raise Exception(f"환율 API 응답 오류: {data}")
    # USD, EUR, JPY 환율 (KRW 기준)
    usd_krw = 1 / data['conversion_rates']['USD']
    eur_krw = 1 / data['conversion_rates']['EUR']
    jpy_krw = 100 / data['conversion_rates']['JPY']  # 100엔 기준
    rates = {
        "USD": round(usd_krw, 2),
        "EUR": round(eur_krw, 2),
        "JPY": round(jpy_krw, 2)
    }
    print("최종 환율:", rates)
    return rates
def get_all_rows(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    res = requests.post(url, headers=headers)
    data = res.json()
    return data["results"]
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
if name == "main":
    rates = get_exchange_rates()
    for db_id in DATABASE_IDS:
        rows = get_all_rows(db_id)  # db_id를 넘겨줌
        for row in rows:
            update_row(row["id"], rates)
    print("모든 데이터베이스에 환율 자동 업데이트 완료!")
