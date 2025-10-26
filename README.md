# AI-Spending-Analyzer
This is a Flask web application that creates realistic transaction data and provides AI-powered spending analysis through interactive visualizations. It's designed to demonstrate data generation, web development, and financial analytics skills.





*How It Works*
Core Components:
-Flask Backend: Python server that generates data and handles web requests
-Dynamic Data Generation: Creates realistic transaction data with categories, amounts, and dates
-Plotly Visualizations: Interactive charts showing spending patterns
-AI Analysis: Generates intelligent insights from spending data
-Responsive Frontend: Modern web interface with real-time updates

Data Flow:
-Generates → 120 synthetic transactions across 6 categories
-Analyzes → Calculates statistics and patterns
-Visualizes → Creates interactive charts
-Summarizes → Provides AI-like insights

Tech Stack
Backend:
- Python 3.x
- Flask (Web framework)
-Pandas (Data manipulation)
-Plotly (Data visualization)

Frontend:
-HTML5, CSS3, JavaScript
-Plotly.js for charts
-Responsive CSS grid layout





*How to Run Locally*
1)Prerequisites:
Python 3.x installed
pip (Python package manager)

Step-by-Step Setup:
2)Create project folder:
-bash-mkdir spending-analyzer
-cd spending-analyzer
-Save the code as data.py in the folder

3)Install required packages:
-bash
-pip install flask pandas plotly

4)Run the application:
bash
python data.py

5)Open your browser:
http://localhost:5000

What Happens:
The script automatically creates a templates folder with index.html
Flask server starts on port 5000
Generates fresh transaction data on each visit
Displays interactive dashboard with charts and insights

Key Features
Real-time Data Generation: New synthetic data on every refresh

Interactive Charts:
Category spending pie chart
Monthly trend line chart
Daily pattern bar chart
Smart Analytics: AI-generated spending insights
Responsive Design: Works on desktop and mobile
Live Updates: JavaScript fetches new data without page reload

Sample Output
The application generates:
Statistics: Total spent, transaction count, averages
Visualizations: Three interactive charts
AI(rule based) Summary: Personalized spending recommendations
Transaction Table: Recent spending history










