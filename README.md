
### 🏛️ The Political Fact-Checker

A Streamlit-powered app that leverages Gemini 2.5 with Google Search grounding to verify political claims in real time. Designed for journalists, researchers, and civic-minded users, this tool delivers structured, impartial fact-checking reports with cited sources and historical context.

---

### 🔍 Features

- **Real-Time Verification**: Uses Gemini 2.5 with Google Search tools to analyze claims against current public data.
- **Structured Analysis**: Outputs four markdown-formatted sections:
  1. **Verification Status** — TRUE, FALSE, MISLEADING, or UNVERIFIABLE
  2. **Supporting Evidence** — Quotes, data, and events that support the claim
  3. **Contradicting Evidence/Context** — Counterpoints and missing context
  4. **Policy/Historical Context** — Legislative or historical background
- **Source Attribution**: Displays clickable links to grounding sources from Google Search.
- **Streamlit UI**: Clean, responsive layout with collapsible sidebar and spinner feedback.

---

### 🚀 Getting Started

#### Prerequisites
- Python 3.9+
- Streamlit
- A valid Gemini API key stored in `.streamlit/secrets.toml`:
```toml
[tool_auth]
gemini_api_key = "YOUR_API_KEY"
```

#### Installation
```bash
pip install streamlit requests
```

#### Run the App
```bash
streamlit run app.py
```

---

### 🧠 How It Works

The app sends user-submitted political claims to Gemini 2.5 with a custom system prompt that enforces impartiality and structured output. Google Search grounding ensures that all responses are based on current, verifiable public information. The app retries failed requests up to five times for robustness.

---

### 📁 File Structure

```
├── app.py                  # Main Streamlit app
├── README.md               # Project documentation
└── .streamlit/
    └── secrets.toml        # API key configuration
```

---

### 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### 🙌 Acknowledgments

- Gemini 2.5 by Google DeepMind
- Streamlit for rapid UI deployment
- Political fact-checking inspiration from PolitiFact and FactCheck.org

---

Let me know if you’d like a tagline, badge set, or visual branding prompt to match this project’s theme!
