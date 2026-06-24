import gradio as gr
import plotly.express as px
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from ddgs import DDGS
import requests
import tempfile

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent

NSE_SYMBOL_MAP_PATH = Path(os.getenv("NSE_SYMBOL_MAP_PATH", BASE_DIR / "nse_symbol_map.json"))
BSE_SYMBOL_MAP_PATH = Path(os.getenv("BSE_SYMBOL_MAP_PATH", BASE_DIR / "bse_symbol_map.json"))


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Symbol map not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

nse_map = load_json(NSE_SYMBOL_MAP_PATH)
bse_map = load_json(BSE_SYMBOL_MAP_PATH)

# --- Calculation Utilities ---
def sip_calculator(amount, months, rate):
    monthly_rate = rate / (12 * 100)
    future_value = amount * (((1 + monthly_rate)**months - 1) / monthly_rate) * (1 + monthly_rate)
    return round(future_value, 2), amount * months

def lumpsum_calculator(principal, years, rate):
    future_value = round(principal * ((1 + rate / 100) ** years), 2)
    return future_value, principal

def emi_calculator(principal, years, rate):
    months = years * 12
    monthly_rate = rate / (12 * 100)
    emi = (principal * monthly_rate * (1 + monthly_rate)*months) / ((1 + monthly_rate)*months - 1)
    total = emi * months
    return round(emi, 2), round(total, 2), round(total - principal, 2)

from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY environment variable")
if not ELEVENLABS_API_KEY:
    raise ValueError("Missing ELEVENLABS_API_KEY environment variable")

# Initialize Groq client once using environment variables
client = Groq(api_key=GROQ_API_KEY)

# --- Stock Analysis Function ---pip install prophet

def analyse_stock(name, exchange):
    symbol = None
    key = name.strip().lower()
    if exchange == "NSE":
        symbol = nse_map.get(key)
    elif exchange == "BSE":
        symbol = bse_map.get(key)

    if not symbol:
        return f"❌ Couldn’t find symbol for {name} in {exchange}"

    # Get stock fundamentals + news
    fundamentals = search_duckduckgo(f"{name} financial fundamentals site:moneycontrol.com OR site:trendlyne.com", max_results=3)
    valuation = search_duckduckgo(f"{name} valuation ratios P/E P/B PEG site:moneycontrol.com", max_results=2)
    news = search_duckduckgo(f"{name} latest stock news", max_results=2)
    future = search_duckduckgo(f"{name} future growth plans expansion 2025", max_results=2)
    competition = search_duckduckgo(f"{name} industry competitors comparison", max_results=2)
    governance = search_duckduckgo(f"{name} promoter holding corporate governance", max_results=2)
    dividends = search_duckduckgo(f"{name} dividend history shareholder returns", max_results=2)
    technicals = search_duckduckgo(f"{name} technical analysis chart trend", max_results=2)
    macro = search_duckduckgo(f"{name} sector outlook India economy impact", max_results=2)
    risks = search_duckduckgo(f"{name} risks lawsuits regulatory issues", max_results=2)

    combined_prompt = f"""
    You are Deena, a smart Indian financial assistant.
    Give me a *detailed investment analysis* of {name} ({exchange}:{symbol}).

    📊 Financial Health:
    {fundamentals}

    🏦 Valuation Check:
    {valuation}

    📰 Key News Impact:
    {news}

    🚀 Future Growth Plans:
    {future}

    🏭 Industry & Competition:
    {competition}

    ⚖ Management & Governance:
    {governance}

    💰 Dividends & Returns:
    {dividends}

    📈 Technical Trend:
    {technicals}

    🌍 Macro Factors:
    {macro}

    ⚠ Risks & Red Flags:
    {risks}

    Please write a structured, easy-to-read report with these headings:

    - 📊 Financial Health
    - 🏦 Valuation Check
    - 📰 Key News Impact
    - 🚀 Future Growth Plans
    - 🏭 Industry & Competition
    - ⚖ Management & Governance
    - 💰 Dividends & Returns
    - 📈 Technical Trend
    - 🌍 Macro Factors
    - ⚠ Risks & Red Flags
    - ✅ Final Verdict: Long-term / Short-term / Avoid
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": combined_prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error analysing stock: {e}"

def analyse_stock_and_chat(name, exchange, history):
    result = analyse_stock(name, exchange)   # run full analysis
    history.append(("🔎 Stock Analysis", result))
    return history


def search_duckduckgo(query, max_results=10):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            formatted = []
            for r in results:
                if "title" in r and "href" in r:
                    formatted.append(f"- [{r['title']}]({r['href']})")
            return formatted if formatted else ["No results found "]
    except Exception as e:
        return [f"Search error: {str(e)}"]


def chat_only(user_input, history, web_toggle):

    if web_toggle:
    # Use DuckDuckGo + Groq
        deena_prompt = """
You are Deena, an AI Financial Advisor.
- You are a highly analytical, data-driven, and intelligent financial expert who explains, compares, and predicts market behavior using logic, reasoning, and live financial data from the web.
- You operate in web search mode, meaning you can fetch and analyze current stock prices, mutual fund NAVs, index movements, and financial news from reliable sources.
- You specialize in equity markets, mutual funds, SIPs, ETFs, portfolio diversification, valuation metrics, and personal finance.
- You analyze, compare, and provide real-time insights about stocks, mutual funds, SIP plans, ETFs, government schemes, and investment strategies.
- When you use live data, always mention the date/time or source clearly (e.g., “as per latest NSE data” or “according to Moneycontrol”).
- If the user asks for information not available on the web, politely explain that some data may be limited and give your best analytical reasoning based on context.
- You can reason about market trends, risk vs. reward, and portfolio allocation, using both live web data and historical knowledge.
- You clearly differentiate between factual data (from the web) and your logical insights or predictions.
- You explain concepts and insights in simple, structured language using sections, bullet points, or short paragraphs.
- You maintain a professional yet friendly tone — confident, analytical, calm, and motivating like a helpful financial advisor.
- You use evidence-based insights, and when predicting, use words like “likely”, “possibly”, or “based on current data trends”.
- You never give guaranteed profit advice or insider information.
- You educate users about financial literacy, teaching them concepts like CAGR, NAV, PE ratio, ROE, diversification, inflation, taxation, and indexation.
- You summarize each analysis with a short, clear conclusion and a polite disclaimer: “This is not certified financial advice, just a data-based analytical insight.”
- When users talk casually, you respond warmly but always try to connect the conversation to finance, learning, or personal growth.
- If users seem confused or unsure, you patiently explain and encourage them to build confidence in financial decisions.
- Always stay structured, factual, and kind — making finance feel insightful, data-backed, and empowering.
"""

        search_results = search_duckduckgo(user_input)  # your existing search function
        '''combined_prompt = f"User asked: {user_input}\n\nDuckDuckGo results:\n{search_results}\n\nNow answer based on this."'''
        combined_prompt = f"User asked: {user_input}\n\nDuckDuckGo results:\n{chr(10).join(search_results)}\n\nNow answer based on this."

        messages = [
            {
                "role": "system",
                "content": deena_prompt
            }
        ]

        recent_history = history[-15:] if history else []

        for human, ai in recent_history:
            messages.append({
                "role": "user",
                "content": str(human)
            })

            messages.append({
                "role": "assistant",
                "content": str(ai)
            })

        messages.append({
            "role": "user",
            "content": combined_prompt
        })

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1500,
            temperature=0.7
        )
    else:
    # Groq only (no DuckDuckGo, no local model)
        deena_personality_prompt= """
            -You are Deena, an AI Financial Advisor.
            - You are a highly analytical, data-driven, and intelligent financial expert who explains, compares, and predicts market behavior using logical reasoning and historical data.
            - You operate fully offline, relying on your trained financial knowledge, not live internet data.
            - You specialize in equity markets, mutual funds, SIPs, ETFs, portfolio diversification, valuation metrics, and personal finance.
            - You analyze, compare, and provide insights about stocks, mutual funds, SIP plans, ETFs, government schemes, and investment strategies.
            - You can reason about market patterns, risk vs. reward, and portfolio allocation, using past data and sound logic.
            - You explain clearly and simply, structuring your answers with sections, bullet points, or step-by-step logic.
            - You maintain a professional yet friendly tone — confident, calm, and motivating like a supportive financial mentor.
            - You use probability-based insights (e.g., “likely”, “historically suggests”) rather than absolute predictions.
            - You never give guaranteed profit advice or insider information.
            - You educate users about financial literacy, helping them understand concepts like CAGR, NAV, PE ratio, ROE, diversification, inflation, and taxation.
            - You summarize each analysis with a short, clear conclusion and a polite disclaimer: “This is not certified financial advice, just an analytical insight.”
            - When users talk casually, you respond warmly yet stay focused on finance and self-growth.
            - If users seem unsure, you guide them patiently and motivate them to learn investing step-by-step.
            - Always stay structured, data-backed, and kind — making finance feel simple, logical, and empowering.
            - If a user asks for live or real-time information (like current stock price, NAV, or market updates), politely tell them:I don’t have live data in offline mode. Please switch me to web search mode for the latest details.
            """

       

        # Build conversation memory

        messages = [
            {
                "role": "system",
                "content": deena_personality_prompt
            }
        ]

        # Keep last 15 conversations
        recent_history = history[-15:] if history else []

        for human, ai in recent_history:
            messages.append({
                "role": "user",
                "content": str(human)
            })

            messages.append({
                "role": "assistant",
                "content": str(ai)
            })

        # Current question
        messages.append({
            "role": "user",
            "content": user_input
        })

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )

    reply = response.choices[0].message.content.strip()

    history = history + [(user_input, reply)]

    return history, history, web_toggle

def fetch_stock_data(name, exchange):
    symbol = None
    key = name.strip().lower()

    if exchange == "NSE":
        symbol = nse_map.get(key)
    elif exchange == "BSE":
        symbol = bse_map.get(key)

    if not symbol:
        return f"Symbol not found for '{name}' in {exchange}", None, None, None

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.history(period="1d")

        if info.empty:
            return f"No recent data available for '{name.upper()}' on {exchange}", None, None, None
        
        latest_price = info["Close"].iloc[-1]

        def plot_hist(period, label):
            hist = ticker.history(period=period)
            if hist.empty:
                return go.Figure().update_layout(title=f"No data for {symbol} - {label}")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode='lines', name=label))
            fig.update_layout(title=f"{symbol} - {label}", xaxis_title="Date", yaxis_title="Price (INR)")
            return fig

        return (
            f"{exchange} Price for {name.upper()}: ₹{latest_price:.2f}",
            plot_hist("7d", "1 Week"),
            plot_hist("6mo", "6 Months"),
            plot_hist("1y", "1 Year")
        )
    except Exception as e:
        return f"Error: {e}", None, None, None


def activate_web_mode(current_state):
    new_state = not current_state
    text = "🌐 Web Search ON" if new_state else "🌐 Web Search OFF"
    css_class = "violet" if new_state else ""
    return new_state, gr.update(value=text, elem_classes=[css_class])




API_KEY = ELEVENLABS_API_KEY

if not VOICE_ID:
    raise ValueError("Missing ELEVENLABS_VOICE_ID environment variable")

def tts_deena(text: str):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.7
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.content

def read_last_message(chat_history):
    if not chat_history:
        return None  # No reply yet
    last_reply = chat_history[-1][1]
    audio_bytes = tts_deena(last_reply)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tmpfile.write(audio_bytes)
        return tmpfile.name



# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    <h1 style='text-align: center; color: #f97316;'>  Deena - Your Friendly & Financial Chatbot</h1>
    <p style='text-align: center;'>  Be specific with her </p>
    """)
    gr.HTML("""
    <style>
    #web_toggle_btn.violet {
        background-color: #7c3aed !important;
        color: white !important;
    }
    </style>
    """)
    



    

    chatbot_ui = gr.Chatbot(label="Chat with Deena")
    with gr.Row():
        user_input = gr.Textbox(placeholder="Type a message to Deena and press Enter...", show_label=False)
        tools_dropdown = gr.Dropdown(["Select Tool", "SIP Calculator", "Lumpsum Calculator", "EMI Calculator", "Goal Planner", "FD Calculator","📊 Live Stocks & ETFs"], label="Tools", scale=1)
        web_button = gr.Button("🌐 Web search OFF",elem_id="web_toggle_btn", size="sm")
        read_button = gr.Button("🔊 Read Last Reply")
        read_audio = gr.Audio(label="Deena Speaks", autoplay=True)
    chat_history = gr.State([])
    web_toggle = gr.State(False)
    web_button.click(fn=activate_web_mode,inputs=[web_toggle],outputs=[web_toggle, web_button])
    read_button.click(fn=read_last_message,inputs=[chat_history],outputs=[read_audio])

    user_input.submit(fn=chat_only, inputs=[user_input, chat_history,web_toggle], outputs=[chatbot_ui, chat_history,web_toggle])

    
        # 📈 SIP
    with gr.Column(visible=False) as sip_section:
        gr.Markdown("<b>📈 SIP Calculator</b>")
        sip_amt = gr.Number(label="Monthly Amount", value=1000)
        sip_mon = gr.Number(label="Months", value=12)
        sip_rate = gr.Number(label="Annual Rate (%)", value=12)

        with gr.Row():
            sip_btn = gr.Button("Calculate SIP")
            sip_search_btn = gr.Button("🔎 Search SIP (AI Suggestions)")  # NEW button

        sip_result = gr.Textbox(label="Result")
        sip_chart = gr.Plot()

        # Normal calculator
        def sip_with_chart(amount, months, rate):
            value, invested = sip_calculator(amount, months, rate)
            gain = value - invested
            df = pd.DataFrame({"Type": ["Invested", "Gain"], "Amount": [invested, gain]})
            fig = px.pie(df, names='Type', values='Amount', title='SIP Returns Breakdown')
            return f"Maturity Value: ₹{value:,.2f}", fig

        sip_btn.click(
            fn=sip_with_chart,
            inputs=[sip_amt, sip_mon, sip_rate],
            outputs=[sip_result, sip_chart]
        )

        # AI SIP Search
        def search_sip_options(amount, months, rate):
            query = f"Best SIP mutual funds in India for monthly ₹{amount}, duration {months} months, expected {rate}% annual return"
            with DDGS() as ddgs:
                results = [r["title"] + " - " + r.get("href", "") for r in ddgs.text(query, max_results=5)]
            
            combined_prompt = f"""
            User SIP Plan:
            - Monthly: ₹{amount}
            - Duration: {months} months
            - Expected Rate: {rate}%

            DuckDuckGo search results about SIP funds:
            {results}

            Based on this, suggest:
            - Top 3–5 mutual funds/SIP schemes suitable
            - Which category (Large/Mid/Small cap, Debt, Hybrid)
            - Risk level
            - Final short advice for the investor
            """

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": combined_prompt}],
                max_tokens=500,
                temperature=0.7,
            )

            reply = response.choices[0].message.content.strip()
            return [("🔎 SIP Search Result", reply)] 

        sip_search_btn.click(
            fn=search_sip_options,
            inputs=[sip_amt, sip_mon, sip_rate],
            outputs=[chatbot_ui]   # result will appear in same chat window with Deena
        )




    # 💰 Lumpsum
    with gr.Column(visible=False) as lump_section:
        gr.Markdown("<b>💰 Lumpsum Calculator</b>")
        lump_amt = gr.Number(label="Lumpsum Amount", value=100000)
        lump_years = gr.Number(label="Years", value=5)
        lump_rate = gr.Number(label="Annual Rate (%)", value=10)

        with gr.Row():
            lump_btn = gr.Button("Calculate Lumpsum")
            lump_search_btn = gr.Button("🔎 Search Lumpsum Options")

        lump_result = gr.Textbox(label="Result")
        lump_chart = gr.Plot()

        # Calculator
        def lumpsum_with_chart(principal, years, rate):
            value, invested = lumpsum_calculator(principal, years, rate)
            gain = value - invested
            df = pd.DataFrame({"Type": ["Invested", "Gain"], "Amount": [invested, gain]})
            fig = px.pie(df, names='Type', values='Amount', title='Lumpsum Returns Breakdown')
            return f"Future Value: ₹{value:,.2f}", fig

        lump_btn.click(fn=lumpsum_with_chart, inputs=[lump_amt, lump_years, lump_rate], outputs=[lump_result, lump_chart])

        
        # Search Options
        # 💰 Lumpsum Search
        def search_lumpsum_options(amount, years, rate):
            query = f"Best lumpsum investment options in India for ₹{amount} over {years} years at {rate}% expected return"
            with DDGS() as ddgs:
                results = [r["title"] + " - " + r.get("href", "") for r in ddgs.text(query, max_results=5)]

            combined_prompt = f"""
            User Lumpsum Plan:
            - Amount: ₹{amount}
            - Duration: {years} years
            - Expected Rate: {rate}%

            DuckDuckGo search results about lumpsum investments:
            {results}

            Based on this, suggest:
            - Top 3–5 options (Mutual Funds, FDs, Govt Schemes, Gold, Equity, etc.)
            - Which type suits short-term vs long-term
            - Risk level
            - Final short advice for the investor
            """

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": combined_prompt}],
                max_tokens=500,
                temperature=0.7,
            )

            reply = response.choices[0].message.content.strip()
            return [("🔎 Lumpsum Search Result", reply)]


        # Button hook
        lump_search_btn.click(
            fn=search_lumpsum_options,
            inputs=[lump_amt, lump_years, lump_rate],
            outputs=[chatbot_ui]  # show result inside Deena's chat
        )

    # 🏦 EMI
    with gr.Column(visible=False) as emi_section:
        gr.Markdown("<b>🏦 EMI Calculator</b>")
        emi_amt = gr.Number(label="Loan Amount (₹)", value=200000)
        emi_years = gr.Number(label="Loan Tenure (Years)", value=2)
        emi_rate = gr.Number(label="Annual Interest Rate (%)", value=10)
        emi_btn = gr.Button("Calculate EMI")
        emi_result = gr.Textbox(label="EMI Details")
        emi_chart = gr.Plot()
        def emi_with_chart(principal, years, rate):
            emi, total, interest = emi_calculator(principal, years, rate)
            df = pd.DataFrame({"Type": ["Principal", "Interest"], "Amount": [principal, interest]})
            fig = px.pie(df, names='Type', values='Amount', title='EMI Breakdown')
            return f"Monthly EMI: ₹{emi:,.2f}\nTotal Payment: ₹{total:,.2f}\nInterest Paid: ₹{interest:,.2f}", fig
        emi_btn.click(fn=emi_with_chart, inputs=[emi_amt, emi_years, emi_rate], outputs=[emi_result, emi_chart])

    # 🎯 Goal Planner
    with gr.Column(visible=False) as goal_section:
        gr.Markdown("<b>🎯 Goal Planner</b>")
        goal_target = gr.Number(label="Goal Amount (₹)", value=500000)
        goal_years = gr.Number(label="Years to Reach Goal", value=5)
        goal_rate = gr.Number(label="Expected Annual Return (%)", value=12)
        goal_btn = gr.Button("Calculate Monthly Investment")
        goal_result = gr.Textbox(label="Goal Plan")
        goal_chart = gr.Plot()
        def calc_goal(goal_target, goal_years, goal_rate):
            r = goal_rate / 12 / 100
            n = goal_years * 12
            monthly = goal_target * r / (((1 + r) ** n - 1) * (1 + r))
            maturity = monthly * (((1 + r)**n - 1) / r) * (1 + r)
            invested = monthly * n
            df = pd.DataFrame({"Type": ["Invested", "Gain"], "Amount": [invested, maturity - invested]})
            fig = px.pie(df, names='Type', values='Amount', title='Goal Planner Breakdown')
            return f"You need to invest ₹{monthly:,.2f} per month", fig
        goal_btn.click(fn=calc_goal, inputs=[goal_target, goal_years, goal_rate], outputs=[goal_result, goal_chart])

    # 🏦 FD Calculator
    with gr.Column(visible=False) as fd_section:
        gr.Markdown("<b>🏦 FD Calculator</b>")
        fd_amount = gr.Number(label="Deposit Amount (₹)", value=100000)
        fd_years = gr.Number(label="FD Tenure (Years)", value=5)
        fd_rate = gr.Number(label="Interest Rate (%)", value=7)
        fd_btn = gr.Button("Calculate FD")
        fd_result = gr.Textbox(label="FD Result")
        fd_chart = gr.Plot()
        def calc_fd(fd_amount, fd_years, fd_rate):
            maturity = fd_amount * ((1 + fd_rate / 100) ** fd_years)
            interest = maturity - fd_amount
            df = pd.DataFrame({"Type": ["Principal", "Interest"], "Amount": [fd_amount, interest]})
            fig = px.pie(df, names='Type', values='Amount', title='FD Returns Breakdown')
            return f"Maturity Value: ₹{maturity:,.2f}", fig
        fd_btn.click(fn=calc_fd, inputs=[fd_amount, fd_years, fd_rate], outputs=[fd_result, fd_chart])

    # 📊 Live Stocks & ETFs
    with gr.Column(visible=False) as live_section:
        gr.Markdown("<b>📊 Live Stock/ETF Tracker</b>")
        stock_input = gr.Textbox(label="Enter Stock or ETF Name", placeholder="E.g. TCS, RELIANCE, GOLDBEES", interactive=True)
        exchange_dropdown = gr.Radio(["NSE", "BSE"], label="Select Exchange", value="NSE")
        
        with gr.Row():
            stock_btn = gr.Button("Fetch Price & Graphs")
            analyse_btn = gr.Button("🔎 Analyse Stock (AI Research)")
        

        stock_price = gr.Textbox(label="Latest Price")
        stock_chart_1w = gr.Plot(label="📅 1 Week Chart")
        stock_chart_6m = gr.Plot(label="🗓 6 Month Chart")
        stock_chart_1y = gr.Plot(label="📈 1 Year Chart")

    stock_btn.click(
    fn=fetch_stock_data,
    inputs=[stock_input, exchange_dropdown],
    outputs=[stock_price, stock_chart_1w, stock_chart_6m, stock_chart_1y]
)
    analyse_btn.click(
        fn=analyse_stock_and_chat,
        inputs=[stock_input, exchange_dropdown, chat_history],
        outputs=[chatbot_ui]
    )

    # Tool Toggle
    tools_dropdown.change(
        fn=lambda choice: (
            gr.update(visible=choice == "SIP Calculator"),
            gr.update(visible=choice == "Lumpsum Calculator"),
            gr.update(visible=choice == "EMI Calculator"),
            gr.update(visible=choice == "Goal Planner"),
            gr.update(visible=choice == "FD Calculator"),
            gr.update(visible=choice == "📊 Live Stocks & ETFs")
        ),
        inputs=tools_dropdown,
        outputs=[sip_section, lump_section, emi_section, goal_section, fd_section,live_section]
    )

app.launch(pwa=True)
