import os
import io
import re
import json
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import plotly.graph_objs as go
import plotly.utils
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

SYSTEM_PROMPT = """Role: Nykaa BI Data Architect. 
Table: campaign_data
Columns: Campaign_ID, Campaign_Type, Target_Audience, Duration, Channel_Used, Impressions, Clicks, Leads, Conversions, Revenue, Acquisition_Cost, ROI, Language, Engagement_Score, Customer_Segment, Date (YYYY-MM-DD).

Instructions:
1. Use SQLite syntax.
2. If the user asks for "Trend", "Over time", or "Monthly", set chart_type to "line".
3. If the user asks for something not in the data or irrelevant, explain why in 'analysis' and return an empty 'sql' string.
4. Return ONLY JSON with keys: analysis, sql, chart_type, chart_config (x_axis, y_axis).
"""

def process_data(file_stream):
    try:
        content = file_stream.read().decode('utf-8', errors='ignore')
        match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
        csv_text = match.group(1).strip() if match else content
        if "Campaign_ID" in csv_text:
            csv_text = csv_text[csv_text.find("Campaign_ID"):]
        df = pd.read_csv(io.StringIO(csv_text))
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
        return df.dropna(subset=['Date'])
    except: return None

def create_chart(data, chart_type, config):
    if not data: return None
    try:
        ct = str(chart_type).lower()
        cols = list(data[0].keys())
        x, y = config.get('x_axis', cols[0]), config.get('y_axis', cols[1] if len(cols)>1 else cols[0])
        x_vals, y_vals = [r[x] for r in data], [r[y] for r in data]
        if 'pie' in ct: fig = go.Figure(data=[go.Pie(labels=x_vals, values=y_vals)])
        elif 'line' in ct: fig = go.Figure(data=[go.Scatter(x=x_vals, y=y_vals, mode='lines+markers')])
        else: fig = go.Figure(data=[go.Bar(x=x_vals, y=y_vals, marker_color='#3b82f6')])
        fig.update_layout(template='plotly_white', margin=dict(l=10, r=10, t=10, b=10))
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except: return None

@app.route('/')
def index(): return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    df = process_data(request.files['file'])
    if df is not None:
        with sqlite3.connect('bi_database.db') as conn:
            df.to_sql('campaign_data', conn, if_exists='replace', index=False)
        return jsonify({"success": True, "message": "Database updated successfully!"})
    return jsonify({"error": "Failed to process file"}), 400

@app.route('/query', methods=['POST'])
def handle_query():
    payload = request.json
    query, history = payload.get('query', ''), payload.get('history', [])
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-flash')
    try:
        chat = model.start_chat(history=history if history else [])
        response = chat.send_message(f"{SYSTEM_PROMPT}\n\nUser: {query}", generation_config={"response_mime_type": "application/json"})
        res = json.loads(response.text.strip())
        if not res.get('sql'): return jsonify({"analysis": res.get('analysis', 'I cannot find that in the data.'), "error": True})
        with sqlite3.connect('bi_database.db') as conn:
            conn.row_factory = sqlite3.Row
            data = [dict(row) for row in conn.execute(res.get('sql')).fetchall()]
        if not data: return jsonify({"analysis": "Query returned no results.", "error": True})
        chart = create_chart(data, res.get('chart_type'), res.get('chart_config', {}))
        return jsonify({"analysis": res.get('analysis'), "sql": res.get('sql'), "data": data, "chart": chart})
    except Exception as e: return jsonify({"analysis": f"System Error: {str(e)}", "error": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)