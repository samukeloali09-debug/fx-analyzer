import streamlit as st
from PIL import Image
import google.generativeai as genai
import os

# ------------------------------------------------------------------------------
# 1. Page Configuration & Title
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Forex & Gold Chart Analyzer",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI Forex & Gold Chart Analyzer")
st.markdown("Upload your chart screenshot, set your strategy parameters, and get instant technical analysis.")

# ------------------------------------------------------------------------------
# 2. Sidebar Setup: API Key & Trading Strategy Settings
# ------------------------------------------------------------------------------
st.sidebar.header("⚙️ Configuration & Strategy")

# API Key handling (reads from Replit Secrets or manual user input)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("Strategy Parameters")

pair_symbol = st.sidebar.text_input("Asset / Pair Symbol", value="XAUUSD (Gold)")
timeframe = st.sidebar.selectbox("Timeframe", ["M1", "M5", "M15", "M30", "H1", "H4", "D1"])

strategy_type = st.sidebar.selectbox(
    "Select Strategy Type",
    [
        "Support & Resistance Bounce",
        "Breakout & Retest",
        "Smart Money Concepts (SMC / FVG)",
        "Moving Average Trend Following",
        "Custom Strategy Search"
    ]
)

if strategy_type == "Custom Strategy Search":
    custom_strategy = st.sidebar.text_area("Describe your custom strategy or rules:", value="Look for RSI divergence and trendline breaks.")
else:
    custom_strategy = strategy_type

# ------------------------------------------------------------------------------
# 3. Main Interface: Image Upload
# ------------------------------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Upload Chart Screenshot")
    uploaded_image = st.file_uploader("Choose a PNG or JPG chart image", type=["png", "jpg", "jpeg"])
    
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        # Updated width parameter to 'stretch' (fixes the Streamlit error)
        st.image(image, caption=f"Uploaded Chart: {pair_symbol} ({timeframe})", width="stretch")
        

# ------------------------------------------------------------------------------
# 4. Analysis Logic & AI Execution
# ------------------------------------------------------------------------------
with col2:
    st.subheader("2. AI Technical Analysis")
    
    if st.button("🚀 Analyze Chart Setup", type="primary"):
        if not api_key:
            st.error("Please provide a Gemini API Key in the sidebar or Replit Secrets.")
        elif uploaded_image is None:
            st.warning("Please upload a chart screenshot first.")
        else:
            with st.spinner("Analyzing market structure and evaluating setup..."):
                try:
                    # Configure Gemini API
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-pro")
                    
                    # Prompt Construction
                    prompt = f"""
                    You are an expert technical analyst in the forex and commodities market.
                    Analyze the attached chart screenshot for {pair_symbol} on the {timeframe} timeframe.
                    
                    Evaluate the price action based on this strategy context: "{custom_strategy}".
                    
                    Provide a structured analysis output formatted as follows:
                    
                    ### 📊 Market Structure Overview
                    * **Trend Direction:** (Bullish / Bearish / Ranging)
                    * **Key Levels Identified:** (Support & Resistance zones visible on the chart)
                    * **Chart/Candlestick Patterns:** (e.g., Engulfing candles, Pin bars, Double Tops, Fair Value Gaps)
                    
                    ---
                    
                    ### 🎯 Strategy Alignment & Trade Signal
                    * **Bias / Hint:** [BUY] / [SELL] / [NO TRADE / WAIT]
                    * **Confluence Rating:** Rate alignment with strategy rules on a scale of 1-10.
                    
                    ---
                    
                    ### 📐 Hypothetical Execution Parameters
                    * **Suggested Entry Zone:**
                    * **Stop Loss (SL):**
                    * **Take Profit Targets:** (TP1, TP2)
                    
                    ---
                    
                    ### ⚠️ Risk Factors & Invalidation
                    * Describe key conditions that would invalidate this trade setup.
                    """
                    
                    # Generate AI response
                    response = model.generate_content([prompt, image])
                    
                    # Output Results
                    st.success("Analysis Complete!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    
