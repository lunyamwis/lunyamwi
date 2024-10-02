import gradio as gr
import io
import sys

# Function to execute the submitted code and return output
def execute_code(code, cells):
    # Capture the output
    output = io.StringIO()
    sys.stdout = output
    sys.stderr = output

    try:
        # Execute the code
        exec(code, globals())  # Execute in the global scope
        result = output.getvalue()  # Get the printed output
    except Exception as e:
        result = str(e)  # Catch any errors
    finally:
        # Reset stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    # Add the new cell
    cells.append({"input": code, "output": result})
    return cells

# The Gradio app layout
def create_jupyter_clone():
    with gr.Blocks() as demo:
        cells = gr.State([])  # Keep track of input/output pairs
        code_input = gr.Textbox(label="Enter Python code here", lines=4, placeholder="Enter Python code...")
        cells_display = gr.Markdown(value="", label="Code History")

        # Button to run the code
        def update_cells(code, cell_state):
            updated_cells = execute_code(code, cell_state)
            cell_display_str = ""
            for idx, cell in enumerate(updated_cells):
                cell_display_str += f"### Cell {idx+1}\n"
                cell_display_str += f"**Input**:\n```python\n{cell['input']}\n```\n"
                cell_display_str += f"**Output**:\n```\n{cell['output']}\n```\n"
            return updated_cells, cell_display_str

        run_button = gr.Button("Run Code")
        run_button.click(fn=update_cells, inputs=[code_input, cells], outputs=[cells, cells_display])

    return demo

# Launch the app
demo = create_jupyter_clone()
demo.launch()

