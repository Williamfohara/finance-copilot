# Finance Copilot 🚀

**One-liner**  
Connect an ERP in 10 min, ask in plain English, and get CFO-grade answers, charts, and a PowerPoint.

## Feature roadmap
- 🔄 OAuth connectors (QuickBooks today, NetSuite CSV mock)
- 💬 NL → SQL chain with transparent SQL + fix editor
- 📊 Variance analysis + GPT narrative + matplotlib chart
- 📈 Scenario planner & Monte-Carlo sims
- 📥 Export: pandas → pptx / xlsx

## Tech stack
DuckDB · dbt Core · LangChain · OpenAI gpt-4o · FastAPI · Streamlit · python-pptx

## Local setup
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # or: poetry install
cp .env.example .env                   # then add keys
python main.py
```

## License
MIT
