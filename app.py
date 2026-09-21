import gradio as gr
import json
import csv
import os
import re
from dotenv import load_dotenv
from crewai import Crew, Agent, Task
from crewai_tools import ScrapeWebsiteTool
from tools.google_maps_tool import GoogleMapsScraperTool
import database  # Humari nayi database file import kar li
from llm import get_llm

# Load environment variables (.env)
load_dotenv()

# Ensure database is initialized when app starts
database.init_db()

def load_jsonc(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*', '', content)
    return json.loads(content)

def fetch_db_data():
    """Database se leads fetch kar ke list of lists mein return karta hai for Gradio Dataframe"""
    rows = database.get_all_leads()
    return rows

def run_lead_generation(category, country):
    if not category or not country:
        return "Error: Please select both a Category and a Country.", fetch_db_data()
    
    status_msg = f"Initializing AI Agents for {category} in {country}...\nAgents are working..."
    
    crew_config = load_jsonc('crew.jsonc')
    planner_config = load_jsonc('agents/territory_planner.jsonc')
    scraper_config = load_jsonc('agents/maps_scraper.jsonc')
    enricher_config = load_jsonc('agents/data_enricher.jsonc')

    agent_llm = get_llm()
    planner = Agent(
        role=planner_config['role'],
        goal=planner_config['goal'],
        backstory=planner_config['backstory'],
        llm=agent_llm
    )
    scraper = Agent(
        role=scraper_config['role'],
        goal=scraper_config['goal'],
        backstory=scraper_config['backstory'],
        tools=[GoogleMapsScraperTool()],
        llm=agent_llm
    )
    enricher = Agent(
        role=enricher_config['role'],
        goal=enricher_config['goal'],
        backstory=enricher_config['backstory'],
        tools=[ScrapeWebsiteTool()],
        llm=agent_llm
    )

    task1 = Task(description=crew_config['tasks'][0]['description'], expected_output=crew_config['tasks'][0]['expected_output'], agent=planner)
    task2 = Task(description=crew_config['tasks'][1]['description'], expected_output=crew_config['tasks'][1]['expected_output'], agent=scraper)
    task3 = Task(description=crew_config['tasks'][2]['description'], expected_output=crew_config['tasks'][2]['expected_output'], agent=enricher, output_file='bulk_leads.csv')

    lead_crew = Crew(agents=[planner, scraper, enricher], tasks=[task1, task2, task3])
    lead_crew.kickoff(inputs={'category': category, 'country': country})
    
    # AI Process complete hone ke baad CSV read kar ke DB mein dalna
    if os.path.exists('bulk_leads.csv'):
        with open('bulk_leads.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Fallbacks in case AI changes header names slightly
                company = row.get('Company Name', 'N/A')
                owner = row.get("Owner's Name", row.get("Owner Name", "Unknown"))
                address = row.get('Address', 'N/A')
                email = row.get('Email', 'N/A')
                phone = row.get('Contact number', row.get('Contact Number', 'N/A'))
                website = row.get('Website URL', row.get('Website', 'N/A'))
                
                # DB mein insert function call (Duplicates ignore ho jayenge)
                database.insert_lead(company, owner, address, email, phone, website, category, country)
                
    final_status = f"Extraction Complete! 🚀\nNew leads successfully processed and saved to the Database."
    
    # Update status aur fresh table data return karna
    return final_status, fetch_db_data()

# Gradio UI Configuration
categories = ['HVAC Contractors', 'Plumbers', 'Electricians', 'Dentists', 'Law Firms', 'Real Estate Agents', 'Auto Dealership', 'Hair Saloons', 'Beauty Saloons', 'Gyms', 'Hotels', 'Restaurants']
countries = ['UK', 'US']
headers = ["Company Name", "Owner Name", "Address", "Email", "Phone", "Website", "Category", "Country", "Timestamp"]

with gr.Blocks(title="AI Lead Generation Agent") as ui:
    gr.Markdown("# 🚀 AI Lead Generation Agent")
    gr.Markdown("Select your target business category and country to start finding leads. Duplicates are automatically filtered.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Search Configuration")
            category_dropdown = gr.Dropdown(choices=categories, label="Category")
            country_dropdown = gr.Dropdown(choices=countries, label="Country")
            run_btn = gr.Button("Run Agent", variant="primary")
            
            gr.Markdown("### 📋 Agent Status")
            output_box = gr.Textbox(label="Logs", lines=4, interactive=False)
            
        with gr.Column(scale=3):
            gr.Markdown("### 🗃️ Leads Database")
            # Interactive table jo page load hotay hi DB se current data show karega
            leads_table = gr.Dataframe(
                headers=headers,
                value=fetch_db_data(),
                interactive=False,
                wrap=True
            )
            
    # Jab button click ho to agent run ho, aur textbox + table dono update hon
    run_btn.click(
        fn=run_lead_generation,
        inputs=[category_dropdown, country_dropdown],
        outputs=[output_box, leads_table]
    )

if __name__ == "__main__":
    ui.launch(theme=gr.themes.Soft())