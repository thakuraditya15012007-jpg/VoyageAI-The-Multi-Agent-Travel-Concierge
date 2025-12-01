✈️ VoyageAI: The Multi-Agent Travel Concierge
🌍 Track: Concierge Agents
1. The Problem: The "Tab Fatigue"
Travel planning is currently fragmented and stressful.
Disconnected Data: A user has to juggle 10+ tabs—one for weather, one for flights, and another for budgeting.
No Context: A flight search engine doesn't know that it's going to rain at your destination, or that the ticket price eats up 80% of your daily budget.
Time Consuming: What should take 5 minutes often takes 5 hours of manual research.
2. The Solution: VoyageAI
VoyageAI is a Multi-Agent System that acts as your intelligent travel architect. It transforms a simple prompt (e.g., "Plan a trip to Mumbai with 5000 Rs") into a structured, feasibility-checked itinerary.
💡 Why AI Agents?
A standard chatbot can write a generic itinerary, but it cannot calculate math accurately or check real-time constraints. VoyageAI uses a Hub-and-Spoke Architecture to orchestrate specialized agents, ensuring that the financial math is correct and the weather advice is relevant.
🚀 Key Capabilities
Multi-Agent Orchestration: Decomposes complex queries into sub-tasks (Weather check, Budget calculation, Itinerary synthesis).
Tool Use: Uses deterministic Python tools for math (preventing LLM calculation errors) and data retrieval.
Smart Routing: Automatically detects Origin and Destination context from natural language.
Safety Fallbacks: Includes a local template engine to generate results even if the API experiences latency.
3. Agent Architecture
VoyageAI uses a Hub-and-Spoke design powered by Google Gemini 1.5 Flash:
🧠 Orchestrator (The Hub): The Brain. It parses the user's intent, identifies missing information, and delegates tasks to sub-agents.
🌤️ WeatherBot (Agent-W): The Perception Layer. It acts as a specialized tool to retrieve environmental context for the specific route.
💰 FinanceBot (Agent-F): The Logic Layer. It extracts numeric parameters (budget, duration) and performs strict arithmetic to ensure cost accuracy.
📝 Synthesizer: The Orchestrator compiles the structured outputs from WeatherBot and FinanceBot into a final, enthusiastic narrative.
4. Technical Implementation
This project demonstrates 3 Key Agent Concepts:
Multi-Agent Systems: Parallel execution of specialized agents (Weather & Finance) coordinated by a central LLM.
Tool Use: Custom Python functions (budget_calculator, get_mock_weather) integrated into the agent workflow.
Observability: The Gradio UI features a real-time "Agent Workflow Log" that visualizes the internal thought process and tool outputs for the user.
5. How to Run Locally
Prerequisites
Python 3.10+
A Google Gemini API Key (Free tier works)
Git installed
Installation Steps
