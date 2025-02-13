import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.secret_key = 'green_cell_voltage_analysis'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maximum file size: 16 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    """Checking if the file has an acceptable extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_html_table(data):
    """Generating a simple HTML table from a dictionary of key-value pairs."""
    html = "<table border='1'>"
    for key, value in data.items():
        html += f"<tr><th>{key}</th><td>{value}</td></tr>"
    html += "</table>"
    return html

def generate_detailed_html_table(dataframe, title):
    """Creating an HTML table for detailed data display with a title."""
    if dataframe.empty:
        return f"<h3>{title}</h3><p>No data to display.</p>"
    html = f"<h3>{title}</h3>"
    html += "<table border='1'><tr><th>Timestamp</th><th>Voltage</th></tr>"
    for _, row in dataframe.iterrows():
        # Format the timestamp for better readability
        time_str = row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(row['Timestamp'], pd.Timestamp) else str(row['Timestamp'])
        html += f"<tr><td>{time_str}</td><td>{row['Voltage']}</td></tr>"
    html += "</table>"
    return html

def analyze_data(file_path):
    try:
        # Loading the CSV data into a DataFrame
        df = pd.read_csv(file_path)
        
        # Adjusting the column name if necessary
        if 'Values' in df.columns:
            df.rename(columns={'Values': 'Voltage'}, inplace=True)
        
        # Converting the Timestamp column to datetime objects (using day-first format)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d-%m-%Y %H:%M:%S')
        
        # Printing  a sample for debugging purposes
        print("Data loaded successfully. Here’s a peek at the first few rows:")
        print(df.head())
        
        # Smoothing the voltage readings with a 5-day moving average
        df['Moving Average'] = df['Voltage'].rolling(window=5).mean()

        # Calculating changes in voltage and the corresponding time intervals
        df['Voltage Change'] = df['Voltage'].diff()
        df['Time Difference'] = df['Timestamp'].diff().dt.total_seconds()
        df['Rate of Change'] = df['Voltage Change'] / df['Time Difference']
        
        # Calculating additional moving averages for trendlines
        df['MA_1000'] = df['Voltage'].rolling(window=1000).mean()
        df['MA_5000'] = df['Voltage'].rolling(window=5000).mean()
        
        # Identifying peaks and troughs in the voltage data
        peaks, _ = find_peaks(df['Voltage'])
        troughs, _ = find_peaks(-df['Voltage'])
        
        # Extracting the data where voltage falls below 20 volts
        below_20 = df[df['Voltage'] < 20]
        
        # Detecting periods when the voltage is dropping at an accelerated rate
        roc_diff = df['Rate of Change'].diff()
        downward_accel = df[(df['Rate of Change'] < 0) & (roc_diff < 0)]
        
        # Preparing subsets for detailed tables
        peaks_data = df.iloc[peaks]
        troughs_data = df.iloc[troughs]
        below_20_data = below_20
        downward_data = downward_accel
        
        # Saving these subsets as CSV files for download
        base = os.path.splitext(os.path.basename(file_path))[0]
        peaks_csv = f"{base}_peaks.csv"
        troughs_csv = f"{base}_troughs.csv"
        below_20_csv = f"{base}_below_20.csv"
        downward_csv = f"{base}_downward.csv"
        
        peaks_data.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], peaks_csv), index=False)
        troughs_data.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], troughs_csv), index=False)
        below_20_data.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], below_20_csv), index=False)
        downward_data.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], downward_csv), index=False)
        
        csv_files = {
            'peaks': peaks_csv,
            'troughs': troughs_csv,
            'below_20': below_20_csv,
            'downward': downward_csv
        }
        
        # Building individual plots for each metric (store HTML strings in memory)
        metrics = {
            'Peaks': {'indices': peaks, 'color': 'green'},
            'Troughs': {'indices': troughs, 'color': 'yellow'},
            'Below 20': {'indices': below_20.index, 'color': 'blue'},
            'Downward Acceleration': {'indices': downward_accel.index, 'color': 'red'}
        }
        graphs = {}
        for label, info in metrics.items():
            idx = info['indices']
            col = info['color']
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.iloc[idx]['Timestamp'],
                y=df.iloc[idx]['Voltage'],
                mode='markers',
                name=label,
                marker=dict(color=col)
            ))
            fig.update_layout(title=label, xaxis_title='Timestamp', yaxis_title='Voltage')
            graphs[label] = fig.to_html(full_html=False)
        
        # Creating a comprehensive main plot with three subplots
        main_fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=(
                "Voltage and 5-Day Moving Average",
                "Rate of Change (Voltage over Time)",
                "Critical Voltage Points"
            )
        )

        # First subplot: Voltage readings and the moving average
        main_fig.add_trace(
            go.Scatter(
                x=df['Timestamp'],
                y=df['Voltage'],
                name='Voltage',
                mode='lines+markers'
            ),
            row=1, col=1
        )
        main_fig.add_trace(
            go.Scatter(
                x=df['Timestamp'],
                y=df['Moving Average'],
                name='5-Day Moving Average',
                line=dict(color='red')
            ),
            row=1, col=1
        )

        # Second subplot: Rate of change in voltage
        main_fig.add_trace(
            go.Scatter(
                x=df['Timestamp'],
                y=df['Rate of Change'],
                name='Rate of Change',
                line=dict(color='purple')
            ),
            row=2, col=1
        )

        # Third subplot: Markers for critical voltage events
        main_fig.add_trace(
            go.Scatter(
                x=df.iloc[peaks]['Timestamp'],
                y=df.iloc[peaks]['Voltage'],
                mode='markers',
                name='Peaks',
                marker=dict(color='green', size=8)
            ),
            row=3, col=1
        )
        main_fig.add_trace(
            go.Scatter(
                x=df.iloc[troughs]['Timestamp'],
                y=df.iloc[troughs]['Voltage'],
                mode='markers',
                name='Troughs',
                marker=dict(color='orange', size=8)
            ),
            row=3, col=1
        )
        main_fig.add_trace(
            go.Scatter(
                x=below_20['Timestamp'],
                y=below_20['Voltage'],
                mode='markers',
                name='Below 20 Volts',
                marker=dict(color='blue', size=8)
            ),
            row=3, col=1
        )
        main_fig.add_trace(
            go.Scatter(
                x=downward_accel['Timestamp'],
                y=downward_accel['Voltage'],
                mode='markers',
                name='Accelerating Downward',
                marker=dict(color='red', size=8)
            ),
            row=3, col=1
        )

        # Customizing axis labels and types for each subplot
        main_fig.update_xaxes(title_text="Timestamp", type="date", row=1, col=1)
        main_fig.update_yaxes(title_text="Voltage", row=1, col=1)
        main_fig.update_xaxes(title_text="Timestamp", type="date", row=2, col=1)
        main_fig.update_yaxes(title_text="Rate of Change", row=2, col=1)
        main_fig.update_xaxes(title_text="Timestamp", type="date", row=3, col=1)
        main_fig.update_yaxes(title_text="Voltage", row=3, col=1)

        # Setting an overall title and adjust the layout
        main_fig.update_layout(
            title='Comprehensive Voltage Analysis for NueGo Electric Bus (Greencell)',
            height=1200,
            showlegend=True
        )

        # Converting the main plot to JSON so it can be embedded on the results page
        main_graph_json = main_fig.to_json()
        
        # Plot: Voltage vs. Timestamp with 1000 & 5000 Moving Average Trendlines
        trend_fig = go.Figure()
        trend_fig.add_trace(
            go.Scatter(
                x=df['Timestamp'],
                y=df['Voltage'],
                name='Voltage',
                mode='lines',
                line=dict(color='blue')
            )
        )
        trend_fig.add_trace(
            go.Scatter(
                x=df['Timestamp'],
                y=df['MA_1000'],
                name='1000-Value Moving Average',
                mode='lines',
                line=dict(color='red')
            )
        )
        trend_fig.add_trace(
            go.Scatter(
                x=df['Timestamp'],
                y=df['MA_5000'],
                name='5000-Value Moving Average',
                mode='lines',
                line=dict(color='green')
            )
        )
        trend_fig.update_layout(
            title='Voltage vs. Timestamp with Trendlines',
            xaxis_title='Timestamp',
            yaxis_title='Voltage',
            height=600
        )
        # Storing the trendline plot in the graphs dictionary
        graphs['Trendlines'] = trend_fig.to_html(full_html=False)
        
        # Preparing a summary of our analysis for display
        summary = {
            'Peaks Count': len(peaks),
            'Troughs Count': len(troughs),
            'Instances Below 20': len(below_20),
            'Downward Acceleration Count': len(downward_accel),
            'Total Records': len(df),
            'Date Range': f"{df['Timestamp'].min()} to {df['Timestamp'].max()}"
        }
        print("Analysis summary:", summary)
        
        # Generating detailed HTML tables for each critical metric
        detailed_tables = {
            'peaks': generate_detailed_html_table(peaks_data, 'Voltage Peaks'),
            'troughs': generate_detailed_html_table(troughs_data, 'Voltage Troughs'),
            'below_20': generate_detailed_html_table(below_20_data, 'Instances Below 20 Volts'),
            'downward': generate_detailed_html_table(downward_data, 'Accelerating Downward Slopes')
        }
        
        return main_graph_json, summary, detailed_tables, graphs, csv_files, None
        
    except Exception as e:
        error_msg = str(e)
        return None, None, None, None, None, error_msg

@app.route('/', methods=['GET', 'POST'])
def index():
    # Handling file uploads and trigger data analysis
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash('No file selected.')
            return redirect(request.url)
        if file.filename == '':
            flash('Please select a CSV file.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            fname = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
            try:
                file.save(file_path)
            except Exception as e:
                flash(f"Error saving the file: {e}")
                return redirect(request.url)
            main_plot_json, summary, detailed_tables, graphs, csv_files, err = analyze_data(file_path)
            if err:
                flash(f"Error during analysis: {err}")
                return redirect(request.url)
            summary_html = generate_html_table(summary)
            return render_template('results.html',
                                   main_plot=main_plot_json,
                                   summary_table=summary_html,
                                   detailed_tables=detailed_tables,
                                   graphs=graphs,
                                   csv_file=fname,
                                   table_csvs=csv_files)
        else:
            flash('Only CSV files are allowed.')
            return redirect(request.url)
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
