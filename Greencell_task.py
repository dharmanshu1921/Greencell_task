import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Ensuring the output directory exists
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# Loading and preprocessing the data
try:
    data = pd.read_csv('Sample_Data.csv')
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%d-%m-%Y %H:%M:%S')
except Exception as e:
    print(f"Failed to load or parse the data: {e}")
    exit()

# Calculating moving averages
data['Moving Average'] = data['Values'].rolling(window=5).mean()   # 5-point moving average 
data['MA_1000'] = data['Values'].rolling(window=1000).mean()       # Short moving average trendline
data['MA_5000'] = data['Values'].rolling(window=5000).mean()       # Long moving average trendline

# Calculating voltage change and rate of change
data['Voltage Change'] = data['Values'].diff()
data['Time Difference'] = data['Timestamp'].diff().dt.total_seconds()
data['Rate of Change'] = data['Voltage Change'] / data['Time Difference']

# Identifying peaks, troughs, and other critical points
peaks, _ = find_peaks(data['Values'])
troughs, _ = find_peaks(-data['Values'])
below_20 = data[data['Values'] < 20]
roc_diff = data['Rate of Change'].diff()
downward_acceleration = data[(data['Rate of Change'] < 0) & (roc_diff < 0)]

# Generating main figure with subplots
fig = make_subplots(
    rows=3, cols=1,
    subplot_titles=(
        "Voltage and Moving Average", 
        "Rate of Change (Change of Voltage Over Time)", 
        "Critical Voltage Points"
    )
)

# Subplot 1: Voltage and 5-Point Moving Average
fig.add_trace(
    go.Scatter(x=data['Timestamp'], y=data['Values'], name='Voltage', mode='lines+markers'),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=data['Timestamp'], y=data['Moving Average'], name='5-Point Moving Average', line=dict(color='red')),
    row=1, col=1
)
fig.update_xaxes(title_text="Timestamp", row=1, col=1)
fig.update_yaxes(title_text="Voltage", row=1, col=1)

# Subplot 2: Rate of Change
fig.add_trace(
    go.Scatter(x=data['Timestamp'], y=data['Rate of Change'], name='Rate of Change', line=dict(color='purple')),
    row=2, col=1
)
fig.update_xaxes(title_text="Timestamp", row=2, col=1)
fig.update_yaxes(title_text="Rate of Change", row=2, col=1)

# Subplot 3: Critical Voltage Points (Peaks, Troughs, Below 20, Downward Acceleration)
fig.add_trace(
    go.Scatter(x=data.iloc[peaks]['Timestamp'], y=data.iloc[peaks]['Values'], mode='markers', 
               name='Peaks', marker=dict(color='green', size=8)),
    row=3, col=1
)
fig.add_trace(
    go.Scatter(x=data.iloc[troughs]['Timestamp'], y=data.iloc[troughs]['Values'], mode='markers', 
               name='Troughs', marker=dict(color='orange', size=8)),
    row=3, col=1
)
fig.add_trace(
    go.Scatter(x=below_20['Timestamp'], y=below_20['Values'], mode='markers', 
               name='Below 20 Volts', marker=dict(color='blue', size=8)),
    row=3, col=1
)
fig.add_trace(
    go.Scatter(x=downward_acceleration['Timestamp'], y=downward_acceleration['Values'], mode='markers', 
               name='Accelerating Downward', marker=dict(color='red', size=8)),
    row=3, col=1
)
fig.update_xaxes(title_text="Timestamp", row=3, col=1)
fig.update_yaxes(title_text="Voltage", row=3, col=1)

# Updating layout and save the main figure
fig.update_layout(title='Comprehensive Voltage Analysis for NueGo Fleet Maintenance', height=1200)
fig.show()
fig.write_image(f"{output_dir}/full_voltage_analysis.png")

# Function to create and save detailed plots for subsets of data
def plot_and_save(dataframe, title, filename, marker_color):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=dataframe['Timestamp'], y=dataframe['Values'], mode='markers', 
                   marker=dict(color=marker_color, size=10))
    )
    fig.update_layout(title=title, xaxis_title='Timestamp', yaxis_title='Voltage', height=600)
    fig.write_image(f"{output_dir}/{filename}")
    fig.show()

# Generating detailed plots for each data subset
plot_and_save(data.iloc[peaks], 'Voltage Peaks', 'peaks_plot.png', 'green')
plot_and_save(data.iloc[troughs], 'Voltage Troughs', 'troughs_plot.png', 'yellow')
plot_and_save(below_20, 'Instances Below 20 Volts', 'below_20_plot.png', 'blue')
plot_and_save(downward_acceleration, 'Accelerating Downward Slopes', 'downward_acceleration_plot.png', 'red')

# Save subset data to CSV files
data.iloc[peaks].to_csv(f'{output_dir}/peaks_data.csv', index=False)
data.iloc[troughs].to_csv(f'{output_dir}/troughs_data.csv', index=False)
below_20.to_csv(f'{output_dir}/instances_below_20.csv', index=False)
downward_acceleration.to_csv(f'{output_dir}/accelerating_downward_slopes.csv', index=False)

# Printing tabulated data to console
print("Peaks Data:")
print(data.iloc[peaks])
print("\nTroughs Data:")
print(data.iloc[troughs])
print("\nInstances Below 20 Volts:")
print(below_20)
print("\nAccelerating Downward Slopes:")
print(downward_acceleration)

print("\nData saved and plots generated successfully.")

# Plot: Voltage vs. Timestamp with 1000 & 5000 Moving Average Trendlines
fig_trendlines = go.Figure()
fig_trendlines.add_trace(
    go.Scatter(x=data['Timestamp'], y=data['Values'], name='Voltage', mode='lines', line=dict(color='blue'))
)
fig_trendlines.add_trace(
    go.Scatter(x=data['Timestamp'], y=data['MA_1000'], name='1000-Value Moving Average', mode='lines', line=dict(color='red'))
)
fig_trendlines.add_trace(
    go.Scatter(x=data['Timestamp'], y=data['MA_5000'], name='5000-Value Moving Average', mode='lines', line=dict(color='green'))
)
fig_trendlines.update_layout(
    title='Voltage vs. Timestamp with Trendlines',
    xaxis_title='Timestamp',
    yaxis_title='Voltage',
    height=600
)
fig_trendlines.show()
fig_trendlines.write_image(f"{output_dir}/voltage_trendlines.png")
