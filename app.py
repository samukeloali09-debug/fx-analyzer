import streamlit as st
from PIL import Image
import google.generativeai as genai
from openai import OpenAI
import base64
import io

# --- Page Configuration ---
st.set_page_config(page_title="FX Pro Strategy Analyzer", layout="wide", page_icon="📈")

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .status-box { padding: 20px; border-radius: 10px; border: 1px solid #ccc; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---
def encode_image(image):
    """Convert PIL image to base64 string for OpenAI."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_with_gemini(api_key, prompt, image):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content([prompt, image])
    return response.text

def analyze_with_openai(api_key, prompt, image):
    client = OpenAI(api_key=api_key)
    base64_image = encode_image(image)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ],
            }
        ],
        max_tokens=1500,
    )
    return response.choices[0].message.content

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("⚙️ Settings")
    ai_provider = st.radio("Select AI Engine", ["Google Gemini", "OpenAI GPT-4o"])
    api_key = st.text_input(f"Enter {ai_provider} API Key", type="password")
    st.info("Your API key is used only for this session and is not stored.")
    
    st.divider()
    st.markdown("### 💡 Tips for better results")
    st.caption("1. Ensure key levels (S/R) are visible.")
    st.caption("2. Include indicator data (RSI/MACD) in screenshot.")
    st.caption("3. Use clear, high-res PNG/JPG files.")

# --- Main App UI ---
st.title("📊 FX Chart & Strategy Analyzer")
st.markdown("Professional-grade technical analysis using multimodal AI.")

col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.subheader("📸 Upload Chart")
    uploaded_file = st.file_uploader("Upload Forex/Gold Chart", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Current Market View", use_container_width=True)

with col2:
    st.subheader("🛠️ Setup Parameters")
    pair_name = st.text_input("Asset Name", value="XAUUSD (Gold)")
    timeframe = st.selectbox("Timeframe", ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"])
    strategy_query = st.text_area("Strategy Context", 
                                  value="Identify high-probability S/R bounces with RSI confluence. Look for divergence if present.",
                                  height=100)
    
    with st.expander("Advanced Analysis Options"):
        include_risk = st.checkbox("Include Risk-to-Reward calculation", value=True)
        include_news = st.checkbox("Suggest potential news impact items", value=False)

# --- Analysis Logic ---
if st.button("🚀 Run Technical Analysis"):
    if not api_key:
        st.warning("Please provide an API key in the sidebar.")
    elif not uploaded_file:
        st.warning("Please upload a chart image first.")
    else:
        # Improved Professional Prompt
        prompt = f"""
        Act as a 15-year veteran FX Institutional Trader. Analyze the {pair_name} chart on {timeframe} timeframe.
        Strategy Context: {strategy_query}
        
        Provide a professional report with:
        1. **Market Structure**: Identify Trend (Bullish/Bearish/Range) and Major/Minor Swing points.
        2. **Key Zones**: List major Support/Resistance and Supply/Demand zones visible.
        3. **Strategy Alignment**: Does this specific image confirm or conflict with "{strategy_query}"?
        4. **The "Trade Hint"**: State BUY, SELL, or NO TRADE in bold.
        5. **Tactical Execution**:
           - Entry Zone (Price Range)
           - Stop Loss (Reasoning: e.g., below previous swing)
           - Take Profit 1 & 2
        6. **Risk Factors & Invalidation**: What specific price action would prove this trade wrong?
        7. **Risk/Reward**: Estimated ratio based on suggested targets.
        
        Tone: Objective, data-driven, and cautious.
        """
        
        with st.spinner(f"Requesting deep-dive analysis from {ai_provider}..."):
            try:
                if ai_provider == "Google Gemini":
                    result = analyze_with_gemini(api_key, prompt, image)
                else:
                    result = analyze_with_openai(api_key, prompt, image)
                
                st.divider()
                st.subheader("📋 Analysis Report")
                st.markdown(result)
                
                # Export functionality
                st.download_button(
                    label="📥 Download Analysis as .md",
                    data=result,
                    file_name=f"{pair_name}_{timeframe}_analysis.md",
                    mime="text/markdown"
                )
                
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")

# --- Footer ---
st.divider()
st.caption("⚠️ Disclaimer: This is an AI-generated hint. Trading involves significant risk. Always use your own judgment and risk management.")
