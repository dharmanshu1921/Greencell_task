# Greencell Internship Assignment

This repository contains my solutions for the Greencell Mobility internship assignment, focusing on data visualization and analysis of electric bus voltage data. The assignment was split into two main tasks: Excel-based visualization and Python-based analysis.

## Task 1: Excel Data Visualization

### Overview
The first task involved creating visualizations and analyzing voltage data using Excel/Google Sheets.

### Implementation Details
- Created a time series plot with voltage readings on the Y-axis and timestamps on the X-axis
- Added trendlines to identify patterns in voltage fluctuations
- Performed data interpretation and analysis

### Visualizations
#### Excel Implementation
![Excel Graph](https://github.com/dharmanshu1921/Greencell_task/blob/main/Greencell_task(Excel).png)

#### Google Sheets Implementation
![Google Sheets Graph](https://github.com/dharmanshu1921/Greencell_task/blob/main/Greencell_ExcelTask(sheets).png)

### Data Interpretation
1. The voltage data shows significant fluctuations over time, with clear peaks and troughs in the readings.
2. There's a general downward trend in voltage levels as indicated by the trendline.
3. The voltage readings frequently oscillate between high and low values, suggesting regular charging and discharging cycles.
4. Several instances show voltage dropping below critical thresholds, which could indicate battery performance issues.
5. The pattern suggests systematic voltage behavior with predictable peaks during charging periods.

### Demo
[![Excel Task Demo](https://img.youtube.com/vi/lhN98-gE8PA/0.jpg)](https://youtu.be/lhN98-gE8PA)

## Task 2: Python Data Analysis and Visualization

### Overview
The second task involved creating a comprehensive Python-based analysis tool with advanced visualizations and data processing capabilities.

### Features
1. Interactive web interface for data upload and analysis
2. Multiple visualization types:
   - Main voltage analysis plot
   - Critical points identification
   - Peaks and troughs analysis
   - Voltage below 20V instances
   - Accelerating downward trends
   - Moving averages and trendlines

### Key Visualizations

#### Main Analysis Plot
![Main Analysis](https://github.com/dharmanshu1921/Greencell_task/blob/main/Results%26Images/main_plot.png)

#### Critical Points Graph
![Critical Points](https://github.com/dharmanshu1921/Greencell_task/blob/main/Results%26Images/crtical_points_graph.png)

#### Peaks Analysis
![Peaks](https://github.com/dharmanshu1921/Greencell_task/blob/main/Results%26Images/peaks_graph.png)

#### Troughs Analysis
![Troughs](https://github.com/dharmanshu1921/Greencell_task/blob/main/Results%26Images/troughs_graph.png)

#### Below 20V Instances
![Below 20V](https://github.com/dharmanshu1921/Greencell_task/blob/main/Results%26Images/Voltage_below20_graph.png)

#### Accelerating Downward Trends
![Downward Trends](https://github.com/dharmanshu1921/Greencell_task/blob/main/Results%26Images/Accelerating_downward_graphs.png)

#### Trendline Analysis
![Trendline](https://github.com/dharmanshu1921/Greencell_task/blob/main/Results%26Images/trendline.png)

### Technical Implementation
- Built using Flask web framework
- Data processing with Pandas and NumPy
- Interactive visualizations using Plotly
- CSV export functionality for detailed analysis
- Responsive web design for better accessibility

### Deployment
The application is deployed and accessible at [greencell-task-2.onrender.com](https://greencell-task-2.onrender.com/)

### Demo
[![Python Implementation Demo](https://img.youtube.com/vi/ZpoO37bbjuk/0.jpg)](https://youtu.be/ZpoO37bbjuk)


## Technologies Used
- Microsoft Excel/Google Sheets
- Python
- Flask
- Pandas
- NumPy
- Plotly
- Scipy
- HTML/CSS

## Getting Started
1. Clone the repository
2. Install required Python packages: `pip install -r requirements.txt`
3. Run the Flask application: `python app.py`
4. Access the application at `localhost:8000`

## Author
Dharmanshu
