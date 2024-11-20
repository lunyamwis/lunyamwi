from django.shortcuts import render
from django_pandas.io import read_frame
from .models import DatabaseCred, DataEntry
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import os
import base64
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.embed import components
from sqlalchemy import create_engine,text
from .forms import DataEntryForm,CustomFieldValueForm,CombinedDataEntryForm 
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from api.instagram.models import CustomFieldValue
from api.instagram.forms import CustomFieldValueForm
from django.forms import modelformset_factory
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sqlalchemy import create_engine
from .serializers import CombinedDataEntrySerializer

# Create your views here.
@api_view(['GET', 'POST'])
def dashboard_api(request):
    if request.method == 'POST':
        serializer = CombinedDataEntrySerializer(data=request.data)
        
        if serializer.is_valid():
            entry = serializer.save()
            df_html = None
            
            query = entry.query  # Assuming there's a query field in DataEntry
            
            if query:
                # Database connection parameters
                db_params = {
                    'username': os.getenv('POSTGRES_USERNAME'),
                    'password': os.getenv('POSTGRES_PASSWORD'),
                    'host': os.getenv('POSTGRES_HOST'),
                    'port': os.getenv('POSTGRES_PORT'),
                    'database': os.getenv('POSTGRES_DBNAME')
                }

                # Create a connection string
                connection_string = f"postgresql+psycopg2://{db_params['username']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
                engine = create_engine(connection_string)

                try:
                    df_temp = pd.read_sql(query, engine)  # Execute the query
                    df_html = df_temp.to_html(classes='table table-striped', index=False)
                
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            chart_data = generate_charts(entry, df_temp)  # Implement this function based on your charting logic
            
            return Response({
                'dataframe': df_html,
                'charts': chart_data,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'message': 'GET method not supported for this endpoint.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

def generate_charts(entry, df):
    """ Generate charts based on entry.chart_type and return chart data. """
    chart_data = {}
    
    if entry.chart_type == 'line':
        chart_data['mpl'] = plot_matplotlib(df)  # Your existing plotting function for matplotlib
    elif entry.chart_type == 'bar':
        chart_data['bokeh_div'], chart_data['bokeh_script'] = plot_bokeh(df)  # Your existing plotting function for bokeh
    
    return chart_data




def dashboard(request):
    chart_mpl = None
    chart_bokeh_div = None
    chart_bokeh_script = None
    df_html = None

    if request.method == 'POST':
        form = CombinedDataEntryForm(request.POST)

        if form.is_valid():
            # Save DataEntry instance
            entry = form.save()

            # Save associated CustomFieldValue using selected field and input value
            # custom_field_value = CustomFieldValue()
            # custom_field_value.content_object = entry  # Link to the newly created entry
            # custom_field_value.field = form.cleaned_data['field']  # Get the selected custom field
            # custom_field_value.value = form.cleaned_data['value']  # Get the value from the form
            # custom_field_value.save()

            # Initialize an empty DataFrame for results (if needed)
            df = pd.DataFrame()
            
            # Execute queries and generate plots based on user input
            query = entry.query  # Assuming there's a query field in DataEntry
            
            if query:
                # Database connection parameters
                db_params = {
                    'username': os.getenv('POSTGRES_USERNAME'),
                    'password': os.getenv('POSTGRES_PASSWORD'),
                    'host': os.getenv('POSTGRES_HOST'),
                    'port': os.getenv('POSTGRES_PORT'),
                    'database': os.getenv('POSTGRES_DBNAME')
                }

                # Create a connection string
                connection_string = f"postgresql+psycopg2://{db_params['username']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"

                # Create an engine and fetch data using the provided query
                engine = create_engine(connection_string)

                try:
                    df_temp = pd.read_sql(query, engine)  # Execute the query
                    df = pd.concat([df, df_temp], ignore_index=True)  # Combine results if multiple queries are executed
                    df_html = df.to_html(classes='table table-striped', index=False)
                    df.columns = [f'col{i+1}' for i in range(df.shape[1])]
                
                except Exception as e:
                    print(f"Error executing query: {e}")  # Handle exceptions appropriately

            # Generate plots based on chart type from the entry
            if entry.chart_type:
                chart_type = entry.chart_type
                
                if chart_type == 'line':
                    chart_mpl = plot_matplotlib(df)  # Matplotlib for line charts
                elif chart_type == 'bar':
                    chart_bokeh_div, chart_bokeh_script = plot_bokeh(df)  # Bokeh for bar charts

    else:
        form = CombinedDataEntryForm()

    return render(request, 'analyst/dashboard.html', {
        'form': form,
        'chart_mpl': chart_mpl,
        'chart_bokeh_div': chart_bokeh_div,
        'chart_bokeh_script': chart_bokeh_script,
        'dataframe': df_html
    })


def plot_matplotlib_bar(df):
    # Create a bar plot with Matplotlib from the DataFrame
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust figure size if needed
    bars = ax.bar(df['col1'], df['col2'], color='skyblue')
    ax.set_title('Title', fontsize=16)
    ax.set_xlabel('Col1', fontsize=12)
    ax.set_ylabel('Col2', fontsize=12)

    # Rotate x-axis labels for better readability
    ax.tick_params(axis='x', rotation=45)
    ax.tick_params(axis='y', labelsize=10)

    # Add values on top of the bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # X-coordinate (center of the bar)
            height,  # Y-coordinate (top of the bar)
            f'{int(height)}',  # The value (formatted as integer)
            ha='center',  # Horizontal alignment
            va='bottom',  # Vertical alignment
            fontsize=10,  # Font size
            color='black'  # Text color
        )

    # Adjust layout to prevent clipping of x-axis labels
    fig.tight_layout()

    # Save it to a BytesIO object and encode it to base64 for rendering in HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')  # Ensure nothing gets cut off
    buf.seek(0)
    plt.close(fig)  # Close the figure to free memory
    return base64.b64encode(buf.getvalue()).decode()

def plot_matplotlib(df):
    # Create a line plot with Matplotlib from the DataFrame
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust figure size if needed
    
    # Plot the line graph
    ax.plot(df['col1'], df['col2'], marker='o', linestyle='-', color='skyblue', label='Col2')
    
    # Add labels on the line points
    for x, y in zip(df['col1'], df['col2']):
        ax.text(
            x, y + 0.1,  # Position slightly above the point
            f'{int(y)}',  # Display the value as an integer
            ha='center', fontsize=10, color='black'
        )
    
    # Set titles and labels
    ax.set_title('Title', fontsize=16)
    ax.set_xlabel('Col1', fontsize=12)
    ax.set_ylabel('Col2', fontsize=12)
    
    # Rotate x-axis labels for better readability
    ax.tick_params(axis='x', rotation=45)
    
    # Add a legend
    ax.legend()
    
    # Adjust layout to prevent clipping of x-axis labels
    fig.tight_layout()
    
    # Save it to a BytesIO object and encode it to base64 for rendering in HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')  # Ensure nothing gets cut off
    buf.seek(0)
    plt.close(fig)  # Close the figure to free memory
    return base64.b64encode(buf.getvalue()).decode()


def plot_bokeh(df):
    # Create a ColumnDataSource for the data
    source = ColumnDataSource(data=dict(col1=df['col1'].tolist(), col2=df['col2'].tolist()))

    # Create the Bokeh plot
    p = figure(
        title="Title", 
        x_axis_label='Col1', 
        y_axis_label='Col2', 
        x_range=[str(x)for x in df['col1'].tolist()], 
        y_range=(0, df['col2'].max() + 5), 
        width=800, 
        height=400
    )

    # Add bars to the plot
    p.vbar(x='col1', top='col2', width=0.9, source=source, color="skyblue")

    # Add labels on top of the bars
    labels = LabelSet(
        x='col1', 
        y='col2', 
        text='col2', 
        level='glyph', 
        x_offset=-13,  # Adjust for better alignment
        y_offset=3,  # Slightly above the bar
        source=source, 
        text_font_size="10pt", 
        text_color="black"
    )
    p.add_layout(labels)

    # Generate script and div for embedding in HTML template
    script, div = components(p)
    
    return div, script