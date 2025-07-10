import requests
import streamlit as st

st.title("🧠 Finance Copilot")
st.write("Ask finance questions in plain English — get SQL + answers.")

query = st.text_input("🔍 Ask a question about your finances:")

if query:
    with st.spinner("Contacting GPT Copilot..."):
        try:
            # Send the query to your FastAPI backend
            response = requests.get("http://localhost:8000/query", params={"query": query})
            data = response.json()

            if "error" in data:
                st.error(f"❌ Error: {data['error']}")
            else:
                st.success("✅ Answer received!")
                st.code(data["generated_sql"], language="sql")
                st.dataframe(data["result"])
        except Exception as e:
            st.error(f"⚠️ Request failed: {e}")

print("👉 Sending GET request with params:", {"query": query})
