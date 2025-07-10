import os

from dotenv import load_dotenv
from openai import OpenAI

from qb import get_profit_and_loss, summarize_financials

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o")  # default to gpt-4o


def ask_gpt_about_financials(financial_summary):
    prompt = f"""Here is a profit & loss summary:
{financial_summary}

Can you explain the business performance in plain English as if you're a CFO briefing a founder?"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a CFO who explains financials clearly and concisely.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    # use your sandbox creds here
    realm_id = "9341454982920695"
    access_token = os.getenv("QB_ACCESS_TOKEN")

    report = get_profit_and_loss(realm_id, access_token)
    summary = summarize_financials(report)
    explanation = ask_gpt_about_financials(summary)

    print("\n📊 GPT Explanation of Profit & Loss:")
    print(explanation)
