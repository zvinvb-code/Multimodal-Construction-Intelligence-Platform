import json, re, urllib.parse
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Multimodal Construction Intelligence", page_icon="🏗️", layout="wide")
st.markdown("""<style>
.pill{display:inline-block;padding:4px 14px;border-radius:999px;font-weight:600;color:#fff}
.ok{background:#16a34a}.warn{background:#d97706}.bad{background:#dc2626}
.card{border:1px solid #e5e7eb;border-radius:12px;padding:14px;margin-bottom:8px}
h1{background:linear-gradient(90deg,#2563eb,#7c3aed);-webkit-background-clip:text;color:transparent}
</style>""", unsafe_allow_html=True)

DEMO = {
 "safety": {"safety_score": 62, "overall_status": "Needs Improvement",
  "ppe_detection": {"helmet": True, "high_vis_vest": True, "steel_toe_boots": False, "safety_harness": False},
  "hazards": [{"hazard": "Work at height without harness", "severity": "Critical", "remedy": "Mandate full-body harness with anchor points (OSHA 1926.501)."},
              {"hazard": "Loose materials near edge", "severity": "Medium", "remedy": "Install toe boards and stack materials away from edges."}]},
 "crack": {"defect_type": "Settlement", "estimated_width_mm": 3.5, "severity": "Moderate",
  "root_causes": ["Differential foundation settlement", "Poor soil compaction"],
  "repairs": ["Epoxy injection", "Structural re-grouting", "Geotechnical review"], "urgency": "Within 2 weeks"},
}
RATES = {"RCC Residential": 1800, "Commercial": 2500, "Industrial Shed": 1400, "Villa / Premium": 3200}
TIER = {"Tier 1": 1.3, "Tier 2": 1.0, "Tier 3": 0.8}
MARKET = {"Tier 1": 9000, "Tier 2": 5500, "Tier 3": 3200}
WEATHER = {
 "High Wind": ["Suspend crane and tower-crane operations", "Secure scaffolding, sheets and loose materials", "Halt work at height"],
 "Heavy Rain": ["Electrical hazard: de-energise temporary supply, use GFCI", "Cover fresh concrete; protect curing", "Check excavation and slope stability"],
 "Extreme Heat": ["Mandatory hydration and shade breaks", "Pour concrete early morning; wet-cure 7+ days (IS 456)", "Monitor workers for heat stress"],
 "Normal": ["Routine toolbox talk", "Inspect PPE and equipment", "Standard curing and housekeeping"]}

def inr(v):
    return f"₹{v/1e7:.2f} Cr" if v >= 1e7 else f"₹{v/1e5:.2f} Lakhs"

def ask_ai(prompt, image=None):
    model = genai.GenerativeModel(st.session_state.model)
    r = model.generate_content([prompt, image] if image else prompt)
    return r.text

def ask_json(prompt, image):
    txt = ask_ai(prompt + "\nReturn ONLY valid JSON, no markdown.", image)
    m = re.search(r"\{.*\}", txt, re.S)
    return json.loads(m.group(0))

genai = None
with st.sidebar:
    st.header("⚙️ Settings")
    key = st.text_input("Google Gemini API key", type="password")
    st.session_state.model = st.text_input("Model", "gemini-2.0-flash")
    if key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
        except Exception as e:
            st.error(f"Gemini setup failed: {e}"); genai = None
    live = bool(key and genai)
    st.success("Live mode" if live else "Demo mode (no key)")
    st.markdown("**Architecture**\n\nReact-style UI → Prompts → Multimodal LLM → JSON contracts → Reports")
    st.caption("Advisory only; consult licensed professionals.")

st.title("🏗️ Multimodal Construction Intelligence Platform")
t1, t2, t3, t4 = st.tabs(["🦺 Safety & PPE", "🧱 Crack Diagnostics", "📐 Planning & Valuation", "🌦️ Daily Assistant"])

with t1:
    up = st.file_uploader("Site photo", type=["jpg", "jpeg", "png"], key="s")
    if up:
        img = Image.open(up); st.image(img, width=400)
        if st.button("Run safety audit"):
            try:
                if live:
                    data = ask_json("Audit worker PPE (helmets, high-vis vests, steel-toe boots, safety harnesses) under OSHA and IS 456. "
                        'JSON keys: safety_score (0-100), overall_status, ppe_detection (object of booleans), '
                        'hazards (list of {hazard, severity: Low|Medium|High|Critical, remedy}).', img)
                else:
                    data = DEMO["safety"]
                st.session_state.safety = data
            except Exception as e:
                st.error(f"Analysis failed: {e}")
    d = st.session_state.get("safety")
    if d:
        sc = d.get("safety_score", 0)
        cls = "ok" if sc >= 80 else "warn" if sc >= 60 else "bad"
        c1, c2 = st.columns(2)
        c1.metric("Safety score", f"{sc}/100")
        c2.markdown(f"<span class='pill {cls}'>{d.get('overall_status','')}</span>", unsafe_allow_html=True)
        for k, v in d.get("ppe_detection", {}).items():
            st.write(("✅ " if v else "❌ ") + k.replace("_", " ").title())
        for h in d.get("hazards", []):
            st.markdown(f"<div class='card'><b>{h.get('hazard')}</b> — {h.get('severity')}<br>🛠 {h.get('remedy')}</div>", unsafe_allow_html=True)
        st.download_button("Download JSON report", json.dumps(d, indent=2), "safety_report.json")

with t2:
    up = st.file_uploader("Concrete / wall surface", type=["jpg", "jpeg", "png"], key="c")
    if up:
        img = Image.open(up); st.image(img, width=400)
        if st.button("Diagnose crack"):
            try:
                if live:
                    data = ask_json("Classify the defect as one of Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling. "
                        "JSON keys: defect_type, estimated_width_mm, severity, root_causes (list), repairs (list, e.g. epoxy injection, re-grouting), urgency.", img)
                else:
                    data = DEMO["crack"]
                st.session_state.crack = data
            except Exception as e:
                st.error(f"Analysis failed: {e}")
    d = st.session_state.get("crack")
    if d:
        a, b, c = st.columns(3)
        a.metric("Defect", d.get("defect_type")); b.metric("Width (mm)", d.get("estimated_width_mm")); c.metric("Urgency", d.get("urgency"))
        st.write("**Root causes:**", ", ".join(d.get("root_causes", [])))
        st.write("**Repairs:**", ", ".join(d.get("repairs", [])))
        st.download_button("Download JSON report", json.dumps(d, indent=2), "crack_report.json")

with t3:
    c1, c2 = st.columns(2)
    stype = c1.selectbox("Structure type", list(RATES)); tier = c1.selectbox("Location tier", list(TIER))
    sqft = c2.number_input("Built-up sqft", 200, 500000, 2000, 100)
    pct = c2.slider("Completion %", 0, 100, 40)
    budget = sqft * RATES[stype] * TIER[tier]
    capex = budget * pct / 100
    value = sqft * MARKET[tier] * (1.25 if "Villa" in stype else 1.0) * (0.4 + 0.6 * pct / 100)
    m = st.columns(4)
    m[0].metric("Total budget", inr(budget)); m[1].metric("Capex incurred", inr(capex))
    m[2].metric("Asset valuation", inr(value)); m[3].metric("Steel / Cement", f"{sqft*4/1000:.1f} t / {int(sqft*0.4)} bags")
    st.progress(pct / 100, text=f"Milestone progress: {pct}%")
    prompt = st.text_input("Render prompt", f"Architectural 3D render of a modern {stype} building, {sqft} sqft, India, photorealistic")
    if st.button("Generate concept render"):
        st.image("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt), caption="Pollinations AI")

with t4:
    w = st.selectbox("Weather condition", list(WEATHER))
    for a in WEATHER[w]:
        (st.success if w == "Normal" else st.warning)(a)
    st.subheader("Site engineering assistant")
    st.session_state.setdefault("chat", [])
    for r, t in st.session_state.chat:
        st.chat_message(r).write(t)
    if q := st.chat_input("Ask a construction question"):
        st.session_state.chat.append(("user", q)); st.chat_message("user").write(q)
        try:
            ans = ask_ai(f"You are a construction engineer. Weather: {w}. Conversation: {st.session_state.chat}\nAnswer concisely.") if live \
                else "Demo mode: add a Gemini API key in the sidebar for live answers. Tip: follow IS 456 curing guidance."
        except Exception as e:
            ans = f"Error: {e}"
        st.session_state.chat.append(("assistant", ans)); st.chat_message("assistant").write(ans)
