import gradio as gr
import json
import re
from crewai import Crew, Agent, Task
from crewai_tools import ScrapeWebsiteTool
from tools.google_maps_tool import GoogleMapsScraperTool

# JSONC configuration load karne ka function (handles inline & block comments)
def load_jsonc(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*', '', content)
    return json.loads(content)

# AI process trigger karne ka main function
def run_lead_generation(category, country):
    if not category or not country:
        return "Error: Please select both a Category and a Country."
    
    # UI par real-time status update
    yield f"Initializing AI Agents for {category} in {country}...\nTerritory Planner is finding top cities..."

    # Configs load karna
    crew_config = load_jsonc('crew.jsonc')
    planner_config = load_jsonc('agents/territory_planner.jsonc')
    scraper_config = load_jsonc('agents/maps_scraper.jsonc')
    enricher_config = load_jsonc('agents/data_enricher.jsonc')

    # Agents initialize karna
    planner = Agent(
        role=planner_config['role'],
        goal=planner_config['goal'],
        backstory=planner_config['backstory']
    )
    scraper = Agent(
        role=scraper_config['role'],
        goal=scraper_config['goal'],
        backstory=scraper_config['backstory'],
        tools=[GoogleMapsScraperTool()]
    )
    enricher = Agent(
        role=enricher_config['role'],
        goal=enricher_config['goal'],
        backstory=enricher_config['backstory'],
        tools=[ScrapeWebsiteTool()]
    )

    # Tasks map karna
    task1 = Task(description=crew_config['tasks'][0]['description'], expected_output=crew_config['tasks'][0]['expected_output'], agent=planner)
    task2 = Task(description=crew_config['tasks'][1]['description'], expected_output=crew_config['tasks'][1]['expected_output'], agent=scraper)
    task3 = Task(description=crew_config['tasks'][2]['description'], expected_output=crew_config['tasks'][2]['expected_output'], agent=enricher, output_file='bulk_leads.csv')

    # Crew start karna
    lead_crew = Crew(agents=[planner, scraper, enricher], tasks=[task1, task2, task3])
    inputs = {'category': category, 'country': country}
    
    result = lead_crew.kickoff(inputs=inputs)
    
    # Final data UI par bhejna
    yield f"Extraction Complete! 🚀\nData saved to 'bulk_leads.csv'.\n\nAgent Summary:\n{result}"

# Gradio UI Configuration
categories = ['HVAC Contractors', 'Plumbers', 'Electricians', 'Dentists', 'Law Firms', 'Real Estate Agents', 'Auto Dealership', 'Hair Saloons', 'Beauty Saloons', 'Gyms', 'Hotels', 'Restaurants']
countries = ['UK', 'US']

with gr.Blocks(title="AI Lead Generation Agent") as ui:
    gr.Markdown("# 🚀 AI Lead Generation Agent")
    gr.Markdown("Select your target business category and country to start finding leads across top cities.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Search Configuration")
            category_dropdown = gr.Dropdown(choices=categories, label="Category")
            country_dropdown = gr.Dropdown(choices=countries, label="Country")
            run_btn = gr.Button("Run Agent", variant="primary")
            
        with gr.Column(scale=3):
            gr.Markdown("### 📋 Agent Dashboard")
            output_box = gr.Textbox(label="Agent Status / Results", lines=15, interactive=False)
            
    # Click event linking UI to Backend
    run_btn.click(
        fn=run_lead_generation,
        inputs=[category_dropdown, country_dropdown],
        outputs=[output_box]
    )

if __name__ == "__main__":
    ui.launch(theme=gr.themes.Soft())