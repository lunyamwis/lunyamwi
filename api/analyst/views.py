from django.shortcuts import render
from django_pandas.io import read_frame
from .models import DatabaseCred
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from bokeh.plotting import figure
from bokeh.embed import components

# Create your views here.

def index(request):
    return render(request, 'analyst/index.html')

def dashboard(request):
    # Retrieve all entries from the database using Django QuerySet
    queryset = DatabaseCred.objects.all()
    
    # Convert the QuerySet to a Pandas DataFrame using django-pandas
    df = read_frame(queryset)

    # Example transformation: Calculate log of values (if applicable)
    df['log_value'] = df['value'].apply(lambda x: np.log(x) if x > 0 else 0)

    # Generate plots
    chart_mpl = plot_matplotlib(df)
    chart_bokeh_div, chart_bokeh_script = plot_bokeh(df)

    return render(request, 'analyst/dashboard.html', {
        'chart_mpl': chart_mpl,
        'chart_bokeh_div': chart_bokeh_div,
        'chart_bokeh_script': chart_bokeh_script,
    })

def plot_matplotlib(df):
    # Create a bar plot with Matplotlib from the DataFrame
    fig, ax = plt.subplots()
    ax.bar(df['name'], df['log_value'])
    ax.set_title('Log Transformed Values')
    ax.set_xlabel('Names')
    ax.set_ylabel('Log Values')

    # Save it to a BytesIO object and encode it to base64 for rendering in HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode()

def plot_bokeh(df):
    # Create a Bokeh plot from the DataFrame
    # p = figure(title="Log Transformed Values", x_axis_label='Names', y_axis_label='Log Values')
    p = figure(title="Log Transformed Values", x_axis_label='Names', y_axis_label='Log Values', 
           x_range=df['name'].tolist(), y_range=(0, df['log_value'].max() + 1))
    
    p.vbar(x=df['name'], top=df['log_value'], width=0.9)
    # print(df)
    # p.circle([1, 2, 3], [4, 5, 6], size=10)
    
    
    # Generate script and div for embedding in HTML template
    script, div = components(p)
    
    return div, script