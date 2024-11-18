from django.shortcuts import render
from django_pandas.io import read_frame
from .models import DatabaseCred
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
from .forms import DateRangeForm   

# Create your views here.

def index(request):
    return render(request, 'analyst/index.html')


def dashboard(request):
    # Initialize the form
    form = DateRangeForm(request.POST or None)

    # Initialize DataFrame variable
    df = pd.DataFrame()

    if request.method == 'POST' and form.is_valid():
        # Get cleaned data from the form
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

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

        # Create an engine
        engine = create_engine(connection_string)

        # SQL query to fetch data using the provided date range
        query = text(f"""
        SELECT 
            ("django_celery_beat_periodictask"."last_run_at")::date AS "day", 
            COUNT("django_celery_beat_periodictask"."id") AS "count" 
        FROM 
            "django_celery_beat_periodictask" 
        WHERE 
            "django_celery_beat_periodictask"."last_run_at" 
            BETWEEN :start_date AND :end_date 
        GROUP BY 
            1 
        ORDER BY 
            1 ASC;
        """)

        # Load data into a DataFrame using parameters for safety against SQL injection
        df = pd.read_sql(query, engine, params={'start_date': start_date, 'end_date': end_date})

    # Example transformation: Calculate log of values (if applicable)
    if not df.empty:
        df['day'] = df['day'].apply(str)

    if df.empty:
        # If the DataFrame is empty, display a message
        df = pd.DataFrame({'day': [], 'count': []})
        message = 'No data available for the selected date range.'
    # Generate plots
    chart_mpl = plot_matplotlib(df)
    chart_bokeh_div, chart_bokeh_script = plot_bokeh(df)

    return render(request, 'analyst/dashboard.html', {
        'form': form,
        'chart_mpl': chart_mpl,
        'chart_bokeh_div': chart_bokeh_div,
        'chart_bokeh_script': chart_bokeh_script,
    })

def plot_matplotlib_bar(df):
    # Create a bar plot with Matplotlib from the DataFrame
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust figure size if needed
    bars = ax.bar(df['day'], df['count'], color='skyblue')
    ax.set_title('Outreach Evaluation', fontsize=16)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Outreach Numbers', fontsize=12)

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
    ax.plot(df['day'], df['count'], marker='o', linestyle='-', color='skyblue', label='Outreach Numbers')
    
    # Add labels on the line points
    for x, y in zip(df['day'], df['count']):
        ax.text(
            x, y + 0.1,  # Position slightly above the point
            f'{int(y)}',  # Display the value as an integer
            ha='center', fontsize=10, color='black'
        )
    
    # Set titles and labels
    ax.set_title('Outreach Evaluation', fontsize=16)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Outreach Numbers', fontsize=12)
    
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
    source = ColumnDataSource(data=dict(day=df['day'].tolist(), count=df['count'].tolist()))

    # Create the Bokeh plot
    p = figure(
        title="Outreach Evaluation", 
        x_axis_label='Date', 
        y_axis_label='Outreach Numbers', 
        x_range=df['day'].tolist(), 
        y_range=(0, df['count'].max() + 1), 
        width=800, 
        height=400
    )

    # Add bars to the plot
    p.vbar(x='day', top='count', width=0.9, source=source, color="skyblue")

    # Add labels on top of the bars
    labels = LabelSet(
        x='day', 
        y='count', 
        text='count', 
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