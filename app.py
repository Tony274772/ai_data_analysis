import os
import json
import sqlite3
import pandas as pd
import re
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import plotly.graph_objs as go
import plotly.utils
from dotenv import load_dotenv

# Load API Key from .env
load_dotenv()

app = Flask(__name__)


# --- UPDATED SYSTEM PROMPT ---
SYSTEM_PROMPT = """Role: Nykaa BI Data Architect. 
Table: campaign_data
Columns: Campaign_ID, Campaign_Type, Target_Audience, Duration, Channel_Used, Impressions, Clicks, Leads, Conversions, Revenue, Acquisition_Cost, ROI, Language, Engagement_Score, Customer_Segment, Date (stored as YYYY-MM-DD).

Instructions:
1. Use SQLite syntax.
2. For trends/time-series, use 'Date' for the x-axis. 
3. If the user asks for "Trend", "Over time", or "Monthly", set chart_type to "line".
4. Return ONLY JSON with keys: analysis, sql, chart_type, chart_config (x_axis, y_axis).
"""

def init_database():
    """Load Nykaa CSV and strictly format dates for Line Charts."""
    if not os.path.exists('cleaned_nykaa_data.csv'):
        print("Error: cleaned_nykaa_data.csv not found.")
        return
    
    df = pd.read_csv('cleaned_nykaa_data.csv')
    
    # CRITICAL: Convert DD-MM-YYYY to YYYY-MM-DD so SQLite can sort and group dates
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
    
    # Remove any rows where date conversion failed
    df = df.dropna(subset=['Date'])

    with sqlite3.connect('bi_database.db') as conn:
        df.to_sql('campaign_data', conn, if_exists='replace', index=False)
        print("Database Synced: Dates formatted for Line Charts.")

def execute_sql_query(sql_query):
    try:
        with sqlite3.connect('bi_database.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql_query)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        return {"error": str(e)}

def get_llm_response(user_query, history=None):
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        chat = model.start_chat(history=history if history else [])
        
        response = chat.send_message(
            f"{SYSTEM_PROMPT}\n\nUser Request: {user_query}",
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text.strip())
    except Exception as e:
        return {"error": str(e)}

def create_chart(data, chart_type, config):
    if not data: return None
    try:
        ct = str(chart_type).lower()
        cols = list(data[0].keys())
        
        # Determine X and Y axes
        x = config.get('x_axis') if config.get('x_axis') in cols else cols[0]
        y = config.get('y_axis') if config.get('y_axis') in cols else (cols[1] if len(cols) > 1 else cols[0])

        x_vals = [r[x] for r in data]
        y_vals = [r[y] for r in data]

        # Chart Logic
        if 'pie' in ct:
            fig = go.Figure(data=[go.Pie(labels=x_vals, values=y_vals)])
        elif 'line' in ct or 'trend' in ct:
            # Line charts need sorted X-axis (dates) to look correct
            combined = sorted(zip(x_vals, y_vals))
            x_sorted, y_sorted = zip(*combined)
            fig = go.Figure(data=[go.Scatter(x=x_sorted, y=y_sorted, mode='lines+markers', line=dict(color='#2563eb'))])
        elif 'area' in ct:
            fig = go.Figure(data=[go.Scatter(x=x_vals, y=y_vals, fill='tonexty')])
        else: # Default Bar
            fig = go.Figure(data=[go.Bar(x=x_vals, y=y_vals, marker_color='#3b82f6')])

        fig.update_layout(
            template='plotly_white', 
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified"
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except: return None

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def handle_query():
    payload = request.json
    query = payload.get('query', '')
    history = payload.get('history', [])
    
    llm_res = get_llm_response(query, history)
    if "error" in llm_res: return jsonify(llm_res)
    
    data = execute_sql_query(llm_res.get('sql', ''))
    chart = create_chart(data, llm_res.get('chart_type'), llm_res.get('chart_config', {}))
    
    return jsonify({
        "analysis": llm_res.get('analysis', ''),
        "sql": llm_res.get('sql', ''),
        "data": data,
        "chart": chart
    })

if __name__ == '__main__':
    init_database()
    app.run(debug=True, port=5000)