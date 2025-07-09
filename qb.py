import requests

def get_profit_and_loss(realm_id, access_token):
    url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/reports/ProfitAndLoss"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def summarize_financials(data):
    rows = data.get("Rows", {}).get("Row", [])
    summary = {}

    for row in rows:
        if "Summary" in row:
            label = row.get("Summary", {}).get("ColData", [{}])[0].get("value", "")
            value = row.get("Summary", {}).get("ColData", [{}])[1].get("value", "")
            if label:
                summary[label] = value

    return summary
