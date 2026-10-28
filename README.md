# Multimodal Construction Intelligence Platform
Skill Wallet Capstone Project 1: a Streamlit decision-support app using a multimodal LLM (Google Gemini).

## Features
- **Site Safety & PPE Audit**: upload a site photo, get a safety score, PPE checklist and hazards (JSON report).
- **Crack Diagnostics**: classify crack type, width (mm), causes, repairs, urgency.
- **Planning & Valuation**: budget, capex, asset value in INR, steel/cement needs, 3D concept render prompt.
- **Daily Assistant**: weather-aware safety alerts and a multi-turn engineering chatbot.
- Works in **demo mode** without an API key.

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```
Paste a Gemini API key in the sidebar (free key: https://aistudio.google.com/apikey).

## Architecture
Streamlit UI -> prompt builders -> Gemini (text + vision) -> strict JSON contracts -> metric cards / downloads.
No database required.

## Known limitations
AI output is advisory only, not a substitute for a licensed structural engineer or safety officer.
Valuation uses simplified per-sqft rates. Demo mode returns sample data.
