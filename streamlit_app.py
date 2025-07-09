import streamlit as st

st.title("Finance Copilot")
st.write("This is a placeholder Streamlit UI for Finance Copilot.")

# You can later connect this to your analysis or prompt pipeline
query = st.text_input("Ask a question about your finances:")

if query:
    st.write(f"⚙️ You asked: {query}")
    st.write("✅ Response: (This is where GPT + data output will appear.)")
