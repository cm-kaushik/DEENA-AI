# 🚀 Deena AI - Smart Financial Assistant

Deena AI is an intelligent finance-focused chatbot designed to make investing, personal finance, and market analysis simple and accessible. Built with Python, Gradio, Groq LLM, and various financial data tools, Deena acts as a friendly financial mentor that can explain concepts, perform calculations, analyze stocks, and assist users in making informed financial decisions.

---

# ✨ Features

## 💬 Conversational Financial Assistant

* Natural language chat interface
* Context-aware conversations
* Beginner-friendly explanations
* Personalized financial guidance
* Investment education and learning support

## 🌐 Web Search Mode

When enabled, Deena can:

* Search the web for financial information
* Analyze recent stock market news
* Research companies and sectors
* Gather investment-related insights
* Provide current market context

## 📊 Stock & ETF Analysis

* Live stock price tracking
* Historical performance charts
* AI-powered stock analysis
* Company research assistance
* Investment risk evaluation
* Sector and competition analysis

## 📈 SIP Calculator

Calculate:

* Monthly SIP growth
* Total invested amount
* Expected maturity value
* Returns breakdown visualization

## 💰 Lumpsum Calculator

Calculate:

* Future value of investments
* Expected returns
* Profit estimation
* Investment growth projections

## 🏦 EMI Calculator

Calculate:

* Monthly EMI
* Total repayment amount
* Total interest payable
* Loan cost visualization

## 🎯 Goal Planner

Plan financial goals such as:

* Buying a house
* Purchasing a car
* Higher education
* Retirement planning
* Emergency fund creation

## 🏛 Fixed Deposit Calculator

Calculate:

* FD maturity amount
* Interest earned
* Long-term savings projections

## 🔊 Voice Responses

Deena can:

* Read responses aloud
* Generate natural speech output
* Improve accessibility and user experience

---

# 🧠 What Makes Deena Different?

Unlike basic chatbots, Deena focuses specifically on finance and investing.

Deena can explain:

* Stocks
* Mutual Funds
* SIPs
* ETFs
* Bonds
* Fixed Deposits
* Government Schemes
* Inflation
* Diversification
* CAGR
* NAV
* PE Ratio
* ROE
* Asset Allocation
* Portfolio Management

All explanations are designed to be easy for beginners while remaining useful for experienced investors.

---

# 🏗 Tech Stack

### Frontend

* Gradio

### Backend

* Python

### AI Models

* Groq API
* Llama 3.3 70B Versatile

### Data Sources

* Yahoo Finance
* DuckDuckGo Search

### Visualization

* Plotly
* Pandas

### Speech

* ElevenLabs Text-to-Speech

---

# 📦 Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/deena-ai.git
cd deena-ai
```

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install gradio
pip install groq
pip install yfinance
pip install pandas
pip install plotly
pip install requests
pip install ddgs
```

---

# API Keys Required

## Groq API

Create an account and generate an API key.

Replace:

```python
client = Groq(api_key="YOUR_GROQ_API_KEY")
```

---

## ElevenLabs API

Replace:

```python
API_KEY = "YOUR_ELEVENLABS_API_KEY"
VOICE_ID = "YOUR_VOICE_ID"
```

---

# Required Files

Place the following files in your project:

```text
nse_symbol_map.json
bse_symbol_map.json
```

These files are used for stock symbol lookup.

Example:

```json
{
  "tcs": "TCS.NS",
  "reliance": "RELIANCE.NS"
}
```

---

# Running Deena

```bash
python app.py
```

Gradio will launch a local server.

Open:

```text
http://127.0.0.1:7860
```

in your browser.

---

# How To Use

## Ask Financial Questions

Examples:

```text
What is a SIP?
```

```text
Explain mutual funds.
```

```text
How do bonds work?
```

```text
Difference between ETF and Mutual Fund?
```

---

## Analyze Stocks

1. Select:

   * 📊 Live Stocks & ETFs

2. Enter:

```text
TCS
```

or

```text
RELIANCE
```

3. Select:

   * NSE
   * BSE

4. Click:

```text
Fetch Price & Graphs
```

or

```text
Analyse Stock
```

---

## Use Investment Calculators

Select a calculator from:

```text
Tools Dropdown
```

Available tools:

* SIP Calculator
* Lumpsum Calculator
* EMI Calculator
* Goal Planner
* FD Calculator

Enter values and click Calculate.

---

## Enable Web Search

Click:

```text
🌐 Web Search OFF
```

to turn it into:

```text
🌐 Web Search ON
```

This allows Deena to search the web for current information.

---

## Listen To Responses

Click:

```text
🔊 Read Last Reply
```

Deena will generate a voice version of the latest response.

---

# Example Questions

## Learning

```text
What is CAGR?
```

```text
Explain PE Ratio.
```

```text
What is NAV?
```

---

## Investment

```text
I have ₹5000 monthly. Which SIP should I choose?
```

```text
How should a beginner start investing?
```

```text
What are low-risk investments?
```

---

## Market Research

```text
Analyze TCS stock.
```

```text
Should I invest in banking ETFs?
```

```text
What are the latest trends in renewable energy stocks?
```

---

# Project Structure

```text
deena-ai/
│
├── app.py
├── nse_symbol_map.json
├── bse_symbol_map.json
├── requirements.txt
├── assets/
│   └── deena_logo.png
│
└── README.md
```

---

# Future Roadmap

Planned features:

* Portfolio Tracking
* Stock Price Alerts
* Mutual Fund Comparison
* Risk Assessment Tool
* Financial Goal Dashboard
* Retirement Planner
* Tax Calculator
* Portfolio Rebalancing Suggestions
* Multi-Language Support
* Mobile App Version

---

# Disclaimer

Deena AI is an educational and informational assistant.

The information provided is not certified financial advice and should not be considered a recommendation to buy, sell, or hold any security. Always perform your own research and consult a qualified financial advisor before making investment decisions.

---

# Contributing

Contributions are welcome.

You can contribute by:

* Reporting bugs
* Improving UI/UX
* Adding new calculators
* Enhancing stock analysis
* Improving AI prompts
* Adding new financial tools

Fork the repository and submit a Pull Request.

---

# License

This project is licensed under the MIT License.

Feel free to use, modify, and distribute with proper attribution.

---

# Author

**Kaushik Babu**

Built with ❤️ using Python, Gradio, Groq, Yahoo Finance, Plotly, DuckDuckGo, and ElevenLabs.

### ⭐ If you find this project useful, consider giving it a star on GitHub!
