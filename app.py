import subprocess
import sys
import os
import time
import re
import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv

# --- 1. Configuration & API Key ---
load_dotenv()

# Try getting key from Environment (Best for GitHub/HuggingFace)
api_key = os.getenv("GEMINI_API_KEY")

# Fallback: Check Colab Userdata
if not api_key:
    try:
        from google.colab import userdata
        api_key = userdata.get('GEMINI_API_KEY')
    except:
        pass

# Fallback: Manual Paste (For local testing only - DO NOT COMMIT REAL KEY TO GITHUB)
if not api_key:
    # api_key = "PASTE_YOUR_AIza_KEY_HERE" 
    pass

if not api_key:
    print("⚠️ WARNING: No API Key found. Please set GEMINI_API_KEY in environment variables.")
else:
    genai.configure(api_key=api_key)

# Use Flash for speed
MODEL_ID = "gemini-1.5-flash"

# --- 2. Python Tools (Manual Execution) ---

def budget_calculator(days, daily_budget, flight_cost):
    """Calculates total trip cost."""
    try:
        # Cleanup inputs (remove commas, text)
        d = int(re.search(r'\d+', str(days)).group())
        b = int(re.search(r'\d+', str(daily_budget)).group())
        f = int(re.search(r'\d+', str(flight_cost)).group())
        total = (d * b) + f
        return f"Total: ₹{total} (Days: {d}, Daily: ₹{b}, Flight: ₹{f})"
    except:
        return "Could not calculate budget (Missing numeric inputs)."

def get_mock_weather(city_name):
    """Checks string for cities and returns mock weather."""
    weather_db = {
        "london": "Rainy, 10°C - Pack an umbrella!",
        "paris": "Sunny, 18°C - Perfect for walking.",
        "tokyo": "Cloudy, 22°C - Humid conditions.",
        "mumbai": "Humid, 32°C - Light cotton clothes.",
        "delhi": "Hazy, 25°C - Check air quality.",
        "nagpur": "Sunny, 38°C - Very hot and dry.",
        "new york": "Windy, 15°C - Bring a jacket.",
        "bangalore": "Pleasant, 24°C - Light jacket needed.",
        "goa": "Sunny, 29°C - Beach wear ready.",
        "pune": "Breezy, 26°C - Pleasant evening.",
        "dubai": "Hot, 40°C - Stay indoors afternoon."
    }
    
    city_key = city_name.lower().strip()
    # Partial match check
    for key, val in weather_db.items():
        if key in city_key:
            return f"{key.title()}: {val}"
            
    return f"{city_name}: Sunny, 25°C (General Forecast)"

# --- 3. Logic Helper Functions ---

extractor_model = genai.GenerativeModel(MODEL_ID)

def extract_budget_params_robust(text):
    """Attempts to extract numbers using Regex."""
    days, budget, flight = 0, 0, 0
    
    # Try to find specific numbers first
    day_match = re.search(r'(\d+)\s*day', text.lower())
    if day_match: days = int(day_match.group(1))

    flight_match = re.search(r'(flight|ticket|airfare).*?(\d+)', text.lower())
    if flight_match: flight = int(flight_match.group(2))

    budget_match = re.search(r'(budget|cost|spend|money).*?(\d+)', text.lower())
    if budget_match:
        val = int(budget_match.group(2))
        if val != flight: budget = val

    # Defaults if extraction fails
    if days == 0: days = 3 
    if budget == 0: budget = 5000 
    if flight == 0: flight = 2000 
    
    return days, budget, flight

# --- 4. Main Orchestration Function ---

def voyage_ai_main(origin, destination, user_plan):
    if not user_plan:
        yield "Please enter a travel plan.", ""
        return
    
    if not api_key:
        yield "❌ Error: API Key is missing. Please set GEMINI_API_KEY environment variable.", ""
        return

    # 1. SETUP LOGS & CONTEXT
    # Use the inputs provided by the user
    start_point = origin if origin else "Nagpur, India"
    end_point = destination if destination else "Unknown Destination"
    
    # If destination wasn't typed in the specific box, try to find it in the text
    if end_point == "Unknown Destination":
        cities = ["mumbai", "delhi", "bangalore", "london", "paris", "tokyo", "goa", "pune", "dubai"]
        for c in cities:
            if c in user_plan.lower():
                end_point = c.title()
                break

    logs = f"🔵 User Request: {user_plan}\n"
    logs += f"📍 Route: {start_point} ➝ {end_point}\n"
    context = f"Origin: {start_point}\nDestination: {end_point}\n"
    yield logs, "..."

    # 2. WEATHER BOT (Checks both Origin and Destination)
    logs += "\n🌤️ Activating WeatherBot...\n"
    yield logs, "..."
    
    w_origin = get_mock_weather(start_point)
    w_dest = get_mock_weather(end_point)
    
    w_res = f"Origin: {w_origin} | Destination: {w_dest}"
    logs += f"   ↳ Result: {w_res}\n"
    context += f"[Weather Report]: {w_res}\n"
    yield logs, "..."

    # 3. FINANCE BOT
    logs += "\n💰 Activating FinanceBot...\n"
    yield logs, "..."
    
    logs += "   ↳ Extracting parameters...\n"
    d, b, f = extract_budget_params_robust(user_plan)
    
    b_res = budget_calculator(d, b, f)
    logs += f"   ↳ Result: {b_res}\n"
    context += f"[Financial Report]: {b_res}\n"
    yield logs, "..."

    # 4. ORCHESTRATOR (With Safety Timeout)
    logs += "\n🧠 Orchestrator Synthesizing (Please wait)...\n"
    yield logs, "..."
    
    final_prompt = f"""
    You are VoyageAI, a professional travel agent.
    
    TRIP DATA:
    - Origin: {start_point}
    - Destination: {end_point}
    - Details: "{user_plan}"
    
    SUB-AGENT REPORTS:
    {context}
    
    INSTRUCTIONS:
    Write a short, enthusiastic travel plan.
    1. Start with "Here is your plan from {start_point} to {end_point}!"
    2. Summarize the costs from the Financial Report.
    3. Give clothing advice based on the Weather Report.
    4. Provide a bulleted Day-by-Day itinerary.
    """
    
    final_output = ""
    try:
        # 8 second timeout to prevent hanging
        response = extractor_model.generate_content(final_prompt, request_options={'timeout': 8})
        final_output = response.text
    except Exception as e:
        # EMERGENCY FALLBACK (If API Hangs)
        print(f"Orchestrator Error: {e}")
        final_output = f"""
        **✈️ Trip Itinerary (Generated Locally)**
        
        **Route:** {start_point} to {end_point}
        
        **💰 Budget Summary:**
        {b_res}
        
        **🌤️ Weather Forecast:**
        * {start_point}: {w_origin}
        * {end_point}: {w_dest}
        
        **📝 Quick Plan:**
        * **Day 1:** Depart from {start_point}. Arrive in {end_point}. Check-in.
        * **Day 2:** Explore local attractions in {end_point}.
        * **Day 3:** Shopping and return flight.
        
        *(Note: The AI Agent was busy, so this is a simplified plan.)*
        """

    yield logs, final_output

# --- 5. Launch Interface ---

if __name__ == "__main__":
    with gr.Blocks(theme=gr.themes.Soft(), title="VoyageAI Capstone") as demo:
        gr.Markdown("# ✈️ VoyageAI: The Multi-Agent Travel Concierge")
        gr.Markdown("Submitted for Google AI Agents Capstone. Powered by Gemini 1.5 Flash.")
        
        with gr.Row():
            with gr.Column(scale=1):
                # NEW INPUTS
                origin_box = gr.Textbox(label="From (Origin City)", value="Nagpur")
                dest_box = gr.Textbox(label="To (Destination City)", placeholder="e.g. Mumbai")
                
                plan_box = gr.Textbox(label="Trip Details", placeholder="Budget 5000 Rs, Flight 2000 Rs, 3 Days.", lines=2)
                
                btn = gr.Button("🚀 Generate Itinerary", variant="primary")
                
                gr.Examples([
                    ["Nagpur", "Mumbai", "Budget 5000 Rs, Flight 2000 Rs, 3 Days"],
                    ["Delhi", "London", "Weather check and estimated cost?"],
                    ["Nagpur", "Bangalore", "Trip for 2 days. Cost 2000 total."]
                ], inputs=[origin_box, dest_box, plan_box])
                
            with gr.Column(scale=1):
                out_log = gr.Textbox(label="Agent Workflow (Logs)", lines=12, interactive=False)
                
        out_final = gr.Markdown(label="Final Itinerary")
        
        btn.click(fn=voyage_ai_main, inputs=[origin_box, dest_box, plan_box], outputs=[out_log, out_final])

    print("🚀 Launching VoyageAI...")
    demo.launch(share=True)
