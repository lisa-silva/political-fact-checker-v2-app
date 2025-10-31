import streamlit as st
import requests
import json
import time
from typing import Dict, Any, List

# --- Configuration ---
# NOTE: This line requires a file named .streamlit/secrets.toml
# containing the [tool_auth] section with the gemini_api_key.
API_KEY = st.secrets.tool_auth.gemini_api_key
# Using the latest stable preview model known for grounding and reasoning
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
MAX_RETRIES = 5

# --- Core LLM Function with Google Search Grounding ---

@st.cache_data(show_spinner=False)
def fact_check_claim(claim: str) -> Dict[str, Any]:
    """
    Sends a political claim to the Gemini model with Google Search enabled 
    to ground the response in real-time, verifiable information.
    """
    
    # Define the System Prompt for impartial fact-checking
    system_prompt = (
        "You are an impartial, highly detailed Political Fact-Checker. "
        "Your primary goal is to analyze the user's claim against real-time information and publicly documented sources. "
        
        "Structure your response into the following format: "
        
        "1. **Claim Analysis:** Clearly restate the claim being analyzed. "
        "2. **Factual Verification:** Use information retrieved from Google Search to verify or refute the claim. Assign a clear status (e.g., 'TRUE,' 'FALSE,' 'MISLEADING,' or 'UNVERIFIABLE'). "
        "3. **Supporting Details:** Provide a concise, balanced explanation of the evidence found, including dates, sources, and context to support your verification status. "
        
        "You MUST use Google Search for grounding to ensure accuracy. Maintain a neutral, journalistic tone."
    )

    user_query = f"Fact-check the following political claim: '{claim}'"
    
    # Construct the Payload
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "tools": [{"google_search": {} }],  # Crucial: Enable Google Search for grounding
        "systemInstruction": {"parts": [{"text": system_prompt}]},
    }
    
    headers = {'Content-Type': 'application/json'}
    
    for attempt in range(MAX_RETRIES):
        try:
            # Use the API key in the URL
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
                # Handle cases where the model response is empty or malformed
                return {"text": "Error: Model returned an empty response candidate. Please try a different query.", "sources": []}

        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                # Exponential backoff
                delay = 2 ** attempt
                time.sleep(delay)
            else:
                # Max retries reached
                return {"text": f"Error: Failed to connect to the verification service after {MAX_RETRIES} attempts. Details: {e}", "sources": []}
        except Exception as e:
            # Catch all other unexpected errors
            return {"text": f"An unexpected error occurred during API processing: {e}", "sources": []}


# --- Streamlit UI and Logic ---

def main():
    """Defines the layout and interactivity of the Streamlit app."""
    
    st.set_page_config(
        page_title="Political Fact-Checker", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.title("🗳️ Political Fact-Checker (LLM Powered)")
    st.markdown(
        """
        A neutral, AI-powered tool designed to check the veracity of political statements and claims
        by grounding them in real-time information using Google Search.
        """
    )
    
    claim_input = st.text_area(
        "Enter a Political Claim for Verification:",
        placeholder="E.g., 'Inflation reached its highest level in 40 years during the third quarter of 2025.'",
        height=100
    )

    if st.button("Verify Claim", type="primary"):
        if claim_input:
            with st.spinner("Searching and verifying claim against real-time data..."):
                results = fact_check_claim(claim_input)
            
            # --- Display Results ---
            st.markdown("### 🔎 Verification Results")
            st.markdown(results["text"])
            
            if results["sources"]:
                st.markdown("---")
                st.subheader("🌐 Grounding Sources")
                
                source_list = ""
                for i, source in enumerate(results["sources"], 1):
                    title = source.get('title') or source['uri']
                    # Using a numbered list for clarity
                    source_list += f"{i}. **[{title}]({source['uri']})**\n"
                
                st.markdown(source_list)
            else:
                st.warning("No specific grounding sources were found, or the model relied on internal knowledge.")
            
        else:
            st.warning("Please enter a claim to begin analysis.")

if __name__ == "__main__":
    main()
