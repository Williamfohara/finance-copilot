Finance Copilot

SUMMARY
Connect an ERP in 10 minutes, ask questions in plain English, and get CFO-grade answers, charts, and PowerPoint exports.

FEATURES AND ROADMAP
- OAuth connectors (QuickBooks Online Sandbox today, NetSuite CSV mock in progress)
- Natural Language to SQL pipeline with transparent SQL output and manual fix editor
- Variance analysis with GPT-generated narrative and matplotlib visualizations
- Scenario planner with Monte Carlo simulation capabilities
- Export functionality to generate reports in Excel and PowerPoint formats

STACK
- Python 3.11 or higher

- DuckDB for local analytics

- dbt Core for data modeling

- LangChain and OpenAI (GPT-4o) for natural language reasoning

- FastAPI for backend services

- Streamlit for dashboard UI

- python-pptx for PowerPoint export

LOCAL DEVELOPMENT SETUP
Step 1: Clone the repo
  - git clone https://github.com/YOUR_USERNAME/finance-copilot.git
  - cd finance-copilot

Step 2: Set up the environment
- python3.11 -m venv .venv
- source .venv/bin/activate

Step 3: Install dependencies (choose one):
Option A using Poetry:
  - poetry install
Option B using pip:
  - pip install -r requirements.txt

Step 4: Add environment variables
- cp .env.example .env
- Then fill in your API keys and tokens inside the .env file

Step 5: Run the app
- python main.py 
