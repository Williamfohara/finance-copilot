import requests
import streamlit as st

st.title("🧠 Finance Copilot")
st.write("Ask finance questions in plain English — get SQL + answers.")

query = st.text_input("🔍 Ask a question about your finances:")

if query:
    with st.spinner("Contacting GPT Copilot..."):
        try:
            # Send the query to your FastAPI backend with timeout
            response = requests.get(
                "http://localhost:8000/query", params={"query": query}, timeout=60
            )
            data = response.json()

            if "error" in data:
                st.error(f"❌ Error: {data['error']}")
            else:
                st.success("✅ Answer received!")
                st.code(data["generated_sql"], language="sql")

                # Display raw result if available
                if "raw_result" in data and data["raw_result"]:
                    st.dataframe(data["raw_result"])

                # 🧠 Natural language explanation
                if "explanation" in data:
                    st.markdown("### 📊 Explanation")
                    st.write(data["explanation"])

        except requests.exceptions.Timeout:
            st.error("⚠️ Request timed out. Please try a simpler question.")
        except requests.exceptions.ConnectionError:
            st.error("⚠️ Could not connect to the server. Make sure your FastAPI server is running.")
        except Exception as e:
            st.error(f"⚠️ Request failed: {e}")

print(
    "👉 Sending GET request with params:",
    {"query": query} if "query" in locals() else "No query yet",
)
