import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Political Fact-Checker", layout="centered")

# Load API key from Streamlit Secrets or environment
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY missing. Add it to .streamlit/secrets.toml or Streamlit Cloud Secrets.")
    st.stop()

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "You are an impartial political fact-checker. "
        "Analyze the claim using search results only. "
        "Verdict: True, False, Misleading, Lacks Context, or Unverifiable. "
        "Provide concise analysis with evidence and sources."
    ),
    tools=["google_search_retrieval"]
)

st.title("🏛️ Political Fact-Checker")
st.markdown("Enter a political claim to get an instant, sourced fact-check.")

claim = st.text_area("Political claim:", height=120, placeholder="e.g., Trump said he won the 2020 election")
context = st.text_input("Context (optional)", placeholder="e.g., USA 2024, UK Parliament")

if st.button("Verify Claim", type="primary"):
    if not claim.strip():
        st.error("Please enter a claim.")
        st.stop()

    with st.spinner("Searching & verifying..."):
        response = model.generate_content(
            f"Claim: {claim}\nContext: {context or 'None'}"
        )

    st.subheader("Verdict & Analysis")
    st.write(response.text)

    # Display sources if available
    try:
        attributions = response.candidates[0].grounding_attributions
        if attributions:
            st.subheader("Sources")
            for attr in attributions:
                web = attr.grounding_support[0].web
                st.markdown(f"- [{web.title}]({web.uri})")
        else:
            st.info("No external sources cited.")
    except Exception:
        st.info("No external sources cited.")
