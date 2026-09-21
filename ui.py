import gradio as gr

# List of predefined business categories
CATEGORIES = [
    'HVAC Contractors',
    'Plumbers',
    'Electricians',
    'Dentists',
    'Law Firms',
    'Real Estate Agents',
    'Auto Dealership',
    'Hair Saloon',
    'Beauty Saloon',
    'Gyms',
    'Hotels',
    'Restaurants',
    'Cleaning Companies',
    'Landscaping',
    'Roofing Companies',
    'Property Management',
    'Vet Clinics',
    'Child care'
]

# List of supported target countries
COUNTRIES = ['UK', 'US']


def trigger_agent(category: str, country: str) -> str:
    """
    Simulates triggering the backend AI Lead Generation Agent.
    Validates inputs and returns status/warning messages.
    """
    if not category or not country:
        return "⚠️ Warning: Please select both a Category and a Country before running the agent."

    return f"Initializing agents to find top cities for {category} in {country}..."


# Build the Gradio UI using Blocks
with gr.Blocks(title="AI Lead Generation Agent") as demo:
    gr.Markdown("# 🚀 AI Lead Generation Agent")
    gr.Markdown("Select your target business category and country to start finding leads.")

    with gr.Row():
        # Sidebar Panel (scale=1)
        with gr.Column(scale=1, variant="panel"):
            gr.Markdown("### ⚙️ Search Configuration")

            category_dropdown = gr.Dropdown(
                label="Category",
                choices=CATEGORIES,
                interactive=True
            )

            country_dropdown = gr.Dropdown(
                label="Country",
                choices=COUNTRIES,
                interactive=True
            )

        # Main Panel (scale=3)
        with gr.Column(scale=3):
            gr.Markdown("### 📋 Agent Dashboard")

            run_btn = gr.Button(
                value="Run Agent",
                variant="primary",
                size="lg"
            )

            output_box = gr.Textbox(
                label="Agent Status / Results",
                placeholder="Agent output and status updates will appear here...",
                lines=10,
                interactive=False
            )

    # Event Listeners
    run_btn.click(
        fn=trigger_agent,
        inputs=[category_dropdown, country_dropdown],
        outputs=[output_box]
    )


if __name__ == "__main__":
    demo.launch()
