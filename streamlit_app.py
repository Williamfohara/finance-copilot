import base64

import requests
import streamlit as st

st.title("Finance Copilot")
st.write("Ask finance questions in plain English — get SQL + answers.")

query = st.text_input("Ask a question about your finances:")

if query:
    with st.spinner("Contacting GPT Copilot..."):
        try:
            response = requests.get(
                "http://localhost:8000/query", params={"query": query}, timeout=60
            )
            data = response.json()

            if "error" in data:
                st.error(f"❌ Error: {data['error']}")
            else:
                st.success("✅ Answer received!")
                generated_sql = data["generated_sql"]
                edited_sql = st.text_area(
                    "✏️ Edit SQL if needed:", generated_sql, height=200, key="sql_editor"
                )

                if st.button("Run Edited SQL"):
                    with st.spinner("Executing your edited SQL..."):
                        sql_response = requests.post(
                            "http://localhost:8000/query_sql", json={"sql": edited_sql}, timeout=60
                        )
                        sql_data = sql_response.json()

                        if "error" in sql_data:
                            st.error(f"❌ Error: {sql_data['error']}")
                        else:
                            st.success("✅ Edited SQL executed successfully!")
                            st.dataframe(sql_data["results"])

                            if "explanation" in sql_data:
                                st.markdown("### 📊 Explanation of Edited Query")
                                st.write(sql_data["explanation"])

                # Display initial query result
                if "raw_result" in data and data["raw_result"]:
                    st.markdown("### Initial Result from GPT-generated SQL")
                    st.dataframe(data["raw_result"])

                if "explanation" in data:
                    st.markdown("### Explanation")
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

if st.button("Run Variance Analysis"):
    with st.spinner("Computing budget vs actual..."):
        try:
            analysis = requests.get("http://localhost:8000/analyze").json()

            if "error" in analysis:
                st.error(f"❌ Analysis Error: {analysis['error']}")
            else:
                st.success("✅ Analysis Complete")

                st.markdown("### GPT Summary")
                st.write(analysis["summary"])

                st.markdown("### Variance Chart")
                st.image(base64.b64decode(analysis["chart_base64"]))

                st.markdown("### Variance Table")
                st.dataframe(analysis["variance_table"])
        except Exception as e:
            st.error(f"⚠️ Failed to run variance analysis: {e}")
