import streamlit as st
import requests
import json
import time
from typing import Dict, Any, List

# --- Configuration ---
# API Key is read directly from the Streamlit Secrets manager
API_KEY = st.secrets.tool_auth.gemini_api_key
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
MODEL_NAME = "gemini-2.5-flash-preview-05-20"
MAX_RETRIES = 5

# --- Core LLM Function with Google Search Grounding ---

@st.cache_data(show_spinner=False)
def fact_check_claim(claim: str) -> Dict[str, Any]:
    """
    Sends a political claim to the Gemini model, forcing it to look up 
    real-time facts and provide a structured verification analysis.
    """
    
    # 1. Define the Impartial Fact-Checker System Prompt
    system_prompt = (
        "You are an impartial, highly detailed Political Fact-Checker and Investigative Analyst. "
        "Your primary goal is to verify the user's claim against publicly available, current information from reliable sources. "
        "You MUST structure your response into the following four distinct, fact-based sections using markdown headings: "
        
        "1. **Verification Status:** Categorize the claim as one of the following: **TRUE**, **FALSE**, **MISLEADING**, or **UNVERIFIABLE**. Provide a one-sentence justification for this status. "
        "2. **Supporting Evidence:** Provide specific, verifiable data, quotes, or events that support the claim. Cite the source type (e.g., 'Official Report,' 'Statement by X,' 'News Article'). "
        "3. **Contradicting Evidence/Context:** Provide specific data, events, or critical context that contradicts or complicates the claim. Explain any missing context that makes the claim misleading. "
        "4. **Policy/Historical Context:** Briefly place the claim within its relevant historical or legislative background (e.g., specific bill, treaty, or election cycle). "
        
        "You must use Google Search for grounding to ensure all claims are based on current, verifiable, and cited public information."
    )

    # 2. Define the User Query
    user_query = (
        f"Fact-check the political claim: '{claim}'"
    )
    
    # 3. Construct the Payload
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "tools": [{"google_search": {} }], # Enable Google Search for grounding
        "systemInstruction": {"parts": [{"text": system_prompt}]},
    }
    
    headers = {'Content-Type': 'application/json'}
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(f"{API_URL}?key={API_KEY}", headers=headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
            
            result = response.json()
            candidate = result.get('candidates', [{}])[0]
            
            if candidate and candidate.get('content', {}).get('parts', [{}])[0].get('text'):
                text = candidate['content']['parts'][0]['text']
                sources = []
                grounding_metadata = candidate.get('groundingMetadata')

                if grounding_metadata and grounding_metadata.get('groundingAttributions'):
                    sources = [
                        {'uri': attr['web']['uri'], 'title': attr['web']['title']}
                        for attr in grounding_metadata['groundingAttributions'] 
                        if 'web' in attr and attr['web'].get('uri')
                    ]
                
                return {"text": text, "sources": sources}

            else:
                return {"text": "Error: Model returned an empty response candidate. Please try again.", "sources": []}

        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                delay = 2 ** attempt
                time.sleep(delay)
            else:
                return {"text": f"Error: Failed to connect to the Fact-Checker service after {MAX_RETRIES} attempts. Details: {e}", "sources": []}
        except Exception as e:
            return {"text": f"An unexpected error occurred during API processing: {e}", "sources": []}


# --- Streamlit UI and Logic ---

def main():
    """Defines the layout and interactivity of the Streamlit app."""
    
    st.set_page_config(
        page_title="The Political Fact-Checker", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.title("🏛️ The Political Fact-Checker")
    st.markdown(
        """
        Enter any specific political statement, quote, or claim below. This tool acts as an impartial analyst, 
        using **real-time Google Search grounding** to verify the claim and provide supporting and contradicting evidence.
        """
    )
    
    # Text Area for the user's premise
    claim_input = st.text_area(
        "Enter a Specific Political Claim for Verification:",
        placeholder="E.g., 'The federal debt has increased by 10% in the last quarter.' or 'Candidate X promised to repeal the 2024 infrastructure bill.'",
        height=100
    )

    # Button to trigger the analysis
    if st.button("Verify Claim", type="primary"):
        if claim_input:
            with st.spinner("Searching current events and verifying claim..."):
                results = fact_check_claim(claim_input)
            
            # --- Display Results ---
            st.markdown("### ✅ Verification Report")
            st.markdown(results["text"])
            
            # Display the sources if they exist
            if results["sources"]:
                st.markdown("---")
                st.subheader("🌐 Grounding Sources")
                
                source_list = ""
                for i, source in enumerate(results["sources"], 1):
                    title = source.get('title') or source['uri']
                    source_list += f"- **[{title}]({source['uri']})**\n"
                
                st.markdown(source_list)
                st.caption("Note: Grounding sources are provided by Google Search to support the verification and context.")
            else:
                st.warning("No specific grounding sources were found.")
            
        else:
            st.warning("Please enter a claim to begin verification.")

if __name__ == "__main__":
    main()
