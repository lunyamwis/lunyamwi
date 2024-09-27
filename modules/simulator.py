import gradio as gr

def greet(name):
    return f"Hello {name}!"

with gr.Blocks() as demo:
    gr.Markdown("# Jupyter-like Gradio App")
    with gr.Row():
        with gr.Column():
            gr.Markdown("## Input")
            input_text = gr.Textbox(label="Enter your name")
        with gr.Column():
            gr.Markdown("## Output")
            output_text = gr.Textbox(label="Greeting")

    greet_btn = gr.Button("Greet")
    greet_btn.click(fn=greet, inputs=input_text, outputs=output_text)

demo.launch()

