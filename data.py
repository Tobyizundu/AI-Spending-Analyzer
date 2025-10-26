# data.py
from flask import Flask, render_template, jsonify, send_file
import pandas as pd
import random
from datetime import datetime, timedelta
import plotly.express as px
import plotly.io as pio
import json
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import base64

app = Flask(__name__)

def ensure_template_directory():
    """Create templates directory if it doesn't exist"""
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("Created templates directory")
    
    # Create index.html if it doesn't exist
    index_path = os.path.join('templates', 'index.html')
    if not os.path.exists(index_path):
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Spending Analyzer</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            padding: 20px;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .btn-group {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 15px;
            flex-wrap: wrap;
        }

        .btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid white;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .btn:hover {
            background: white;
            color: #667eea;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-card h3 {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .stat-card h2 {
            color: #333;
            font-size: 1.8em;
            font-weight: bold;
        }

        .ai-summary {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            line-height: 1.6;
        }

        .ai-summary h3 {
            color: #667eea;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .chart-container .plotly-graph-div {
            width: 100% !important;
        }

        .transactions-section {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .transactions-section h3 {
            color: #333;
            margin-bottom: 20px;
        }

        .transactions-table {
            width: 100%;
            border-collapse: collapse;
        }

        .transactions-table th,
        .transactions-table td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }

        .transactions-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #555;
        }

        .transactions-table tr:hover {
            background: #f8f9fa;
        }

        .category-badge {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 500;
        }

        .amount-positive {
            color: #27ae60;
            font-weight: 600;
        }

        .amount-high {
            color: #e74c3c;
            font-weight: 600;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #666;
        }

        .statement-section {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .statement-section h3 {
            color: #333;
            margin-bottom: 20px;
        }

        .statement-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .statement-item {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            text-align: center;
        }

        .statement-item h4 {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }

        .statement-item .value {
            color: #333;
            font-size: 1.2em;
            font-weight: bold;
        }

        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .btn-group {
                flex-direction: column;
                align-items: center;
            }
            
            .btn {
                width: 100%;
                max-width: 300px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>💰 AI Spending Analyzer</h1>
            <p>Smart insights into your spending habits powered by AI</p>
            <div class="btn-group">
                <button class="btn" onclick="refreshData()">
                    🔄 Generate New Data
                </button>
                <button class="btn" onclick="generateStatement()">
                    📄 Generate Monthly Statement
                </button>
                <button class="btn" onclick="downloadStatement()">
                    💾 Download PDF Statement
                </button>
            </div>
        </div>

        <!-- Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Spent</h3>
                <h2 id="totalSpent">${{ stats.total_spent }}</h2>
            </div>
            <div class="stat-card">
                <h3>Total Transactions</h3>
                <h2 id="totalTransactions">{{ stats.total_transactions }}</h2>
            </div>
            <div class="stat-card">
                <h3>Average Transaction</h3>
                <h2 id="avgTransaction">${{ stats.average_transaction }}</h2>
            </div>
            <div class="stat-card">
                <h3>Top Category</h3>
                <h2 id="topCategory">{{ stats.favorite_category }}</h2>
            </div>
        </div>

        <!-- Monthly Statement Summary -->
        <div class="statement-section">
            <h3>Monthly Statement Summary</h3>
            <div class="statement-summary">
                <div class="statement-item">
                    <h4>Current Month Spending</h4>
                    <div class="value" id="monthSpending">${{ stats.this_month_spending }}</div>
                </div>
                <div class="statement-item">
                    <h4>Month Transactions</h4>
                    <div class="value" id="monthTransactions">{{ stats.transactions_this_month }}</div>
                </div>
                <div class="statement-item">
                    <h4>Daily Average</h4>
                    <div class="value" id="dailyAverage">${{ stats.daily_average }}</div>
                </div>
                <div class="statement-item">
                    <h4>Statement Period</h4>
                    <div class="value" id="statementPeriod">{{ stats.statement_period }}</div>
                </div>
            </div>
        </div>

        <!-- AI Summary -->
        <div class="ai-summary">
            <h3>AI Spending Analysis</h3>
            <p id="aiSummary">{{ ai_summary }}</p>
        </div>

        <!-- Charts -->
        <div class="charts-grid">
            <div class="chart-container">
                {{ category_chart|safe }}
            </div>
            <div class="chart-container">
                {{ monthly_chart|safe }}
            </div>
            <div class="chart-container">
                {{ daily_chart|safe }}
            </div>
        </div>

        <!-- Recent Transactions -->
        <div class="transactions-section">
            <h3>Recent Transactions</h3>
            <div class="loading" id="loadingIndicator">
                Loading new data...
            </div>
            <table class="transactions-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Merchant</th>
                        <th>Category</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody id="transactionsBody">
                    {% for transaction in recent_transactions %}
                    <tr>
                        <td>{{ transaction.date }}</td>
                        <td>{{ transaction.merchant }}</td>
                        <td>
                            <span class="category-badge">{{ transaction.category }}</span>
                        </td>
                        <td class="{% if transaction.amount > 100 %}amount-high{% else %}amount-positive{% endif %}">
                            ${{ "%.2f"|format(transaction.amount) }}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // This JavaScript function communicates with data.py
        async function refreshData() {
            const button = document.querySelector('.btn');
            const loading = document.getElementById('loadingIndicator');
            const transactionsBody = document.getElementById('transactionsBody');
            
            // Show loading
            button.disabled = true;
            button.innerHTML = '🔄 Generating...';
            loading.style.display = 'block';
            transactionsBody.innerHTML = '';
            
            try {
                // Call the /refresh endpoint in data.py
                const response = await fetch('/refresh');
                const data = await response.json();
                
                // Update statistics with data from Python
                document.getElementById('totalSpent').textContent = '$' + data.stats.total_spent.toFixed(2);
                document.getElementById('totalTransactions').textContent = data.stats.total_transactions;
                document.getElementById('avgTransaction').textContent = '$' + data.stats.average_transaction.toFixed(2);
                document.getElementById('topCategory').textContent = data.stats.favorite_category;
                document.getElementById('monthSpending').textContent = '$' + data.stats.this_month_spending.toFixed(2);
                document.getElementById('monthTransactions').textContent = data.stats.transactions_this_month;
                document.getElementById('dailyAverage').textContent = '$' + data.stats.daily_average.toFixed(2);
                document.getElementById('statementPeriod').textContent = data.stats.statement_period;
                
                // Update AI summary with data from Python
                document.getElementById('aiSummary').textContent = data.ai_summary;
                
                // Update transactions table with data from Python
                transactionsBody.innerHTML = data.recent_transactions.map(transaction => `
                    <tr>
                        <td>${transaction.date}</td>
                        <td>${transaction.merchant}</td>
                        <td><span class="category-badge">${transaction.category}</span></td>
                        <td class="${transaction.amount > 100 ? 'amount-high' : 'amount-positive'}">
                            $${transaction.amount.toFixed(2)}
                        </td>
                    </tr>
                `).join('');
                
                // Reload page to refresh charts (they need full page reload)
                setTimeout(() => {
                    location.reload();
                }, 1000);
                
            } catch (error) {
                console.error('Error refreshing data:', error);
                alert('Error refreshing data. Please try again.');
            } finally {
                button.disabled = false;
                button.innerHTML = '🔄 Generate New Data';
                loading.style.display = 'none';
            }
        }

        async function generateStatement() {
            try {
                const response = await fetch('/generate_statement');
                const data = await response.json();
                
                // Update statement summary
                document.getElementById('monthSpending').textContent = '$' + data.statement_summary.current_month_spending.toFixed(2);
                document.getElementById('monthTransactions').textContent = data.statement_summary.transactions_this_month;
                document.getElementById('dailyAverage').textContent = '$' + data.statement_summary.daily_average.toFixed(2);
                document.getElementById('statementPeriod').textContent = data.statement_summary.statement_period;
                
                alert('Monthly statement generated successfully!');
                
            } catch (error) {
                console.error('Error generating statement:', error);
                alert('Error generating statement. Please try again.');
            }
        }

        async function downloadStatement() {
            try {
                const response = await fetch('/download_statement');
                const blob = await response.blob();
                
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'monthly_statement.pdf';
                
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
            } catch (error) {
                console.error('Error downloading statement:', error);
                alert('Error downloading statement. Please try again.');
            }
        }
    </script>
</body>
</html>""")
        print("📄 Created index.html template")

# Call this function before running the app
ensure_template_directory()

def generate_transactions(num_records=150):
    """Generate realistic transaction data with accurate spending patterns"""
    categories = {
        'Food & Dining': ['Restaurant', 'Groceries', 'Coffee Shop', 'Fast Food', 'Supermarket', 'Food Delivery'],
        'Shopping': ['Amazon', 'Clothing Store', 'Electronics', 'Department Store', 'Online Shopping', 'Home Goods'],
        'Transportation': ['Gas Station', 'Uber/Lyft', 'Public Transport', 'Parking', 'Car Maintenance', 'Auto Insurance'],
        'Entertainment': ['Netflix', 'Movies', 'Concert', 'Games', 'Sports', 'Streaming Services'],
        'Bills & Utilities': ['Electricity', 'Internet', 'Phone Bill', 'Water Bill', 'Rent', 'Mortgage'],
        'Healthcare': ['Pharmacy', 'Doctor', 'Dental', 'Health Insurance', 'Gym', 'Medical'],
        'Personal Care': ['Hair Salon', 'Spa', 'Cosmetics', 'Skincare'],
        'Travel': ['Airline', 'Hotel', 'Vacation', 'Travel Agency']
    }
    
    transactions = []
    start_date = datetime.now() - timedelta(days=90)
    
    # Generate more transactions for current month to simulate realistic patterns
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    for _ in range(num_records):
        category = random.choice(list(categories.keys()))
        merchant = random.choice(categories[category])
        
        # Realistic amount ranges based on categories
        amount_ranges = {
            'Food & Dining': (3, 120),
            'Shopping': (15, 450),
            'Transportation': (8, 180),
            'Entertainment': (9, 150),
            'Bills & Utilities': (25, 800),
            'Healthcare': (12, 300),
            'Personal Care': (20, 200),
            'Travel': (50, 2000)
        }
        
        min_amt, max_amt = amount_ranges[category]
        
        # Create more realistic distribution (fewer large transactions)
        if random.random() < 0.8:  # 80% of transactions are smaller
            amount = round(random.uniform(min_amt, max_amt * 0.4), 2)
        else:  # 20% are larger transactions
            amount = round(random.uniform(max_amt * 0.4, max_amt), 2)
        
        # Weight transactions towards current month
        if random.random() < 0.6:  # 60% of transactions in current month
            days_ago = random.randint(0, 30)
        else:
            days_ago = random.randint(31, 90)
            
        transaction_date = (start_date + timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        transactions.append({
            'date': transaction_date,
            'amount': amount,
            'merchant': merchant,
            'category': category
        })
    
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    return df.sort_values('date', ascending=False)

def analyze_spending(df):
    """Calculate comprehensive spending statistics"""
    df['date'] = pd.to_datetime(df['date'])
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Current month data
    this_month_df = df[(df['date'].dt.month == current_month) & (df['date'].dt.year == current_year)]
    this_month_spending = this_month_df['amount'].sum()
    
    # Previous month data
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1
    prev_month_df = df[(df['date'].dt.month == prev_month) & (df['date'].dt.year == prev_year)]
    prev_month_spending = prev_month_df['amount'].sum()
    
    # Calculate daily average for current month
    days_in_current_month = min(30, len(this_month_df))
    daily_average = this_month_spending / days_in_current_month if days_in_current_month > 0 else 0
    
    # Statement period
    statement_start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    statement_end = datetime.now().strftime('%Y-%m-%d')
    
    stats = {
        'total_spent': round(df['amount'].sum(), 2),
        'total_transactions': len(df),
        'average_transaction': round(df['amount'].mean(), 2),
        'largest_transaction': round(df['amount'].max(), 2),
        'favorite_category': df['category'].mode().iloc[0] if not df['category'].mode().empty else 'N/A',
        'this_month_spending': round(this_month_spending, 2),
        'prev_month_spending': round(prev_month_spending, 2),
        'transactions_this_month': len(this_month_df),
        'daily_average': round(daily_average, 2),
        'statement_period': f"{statement_start} to {statement_end}",
        'spending_change': round(this_month_spending - prev_month_spending, 2)
    }
    
    return stats

def generate_ai_summary(stats, df):
    """Generate AI-like spending summary with accurate insights"""
    category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
    top_category = category_totals.index[0]
    top_category_amount = category_totals.iloc[0]
    
    df['day_of_week'] = df['date'].dt.day_name()
    daily_spending = df.groupby('day_of_week')['amount'].mean()
    highest_day = daily_spending.idxmax()
    highest_day_amount = daily_spending.max()
    
    # Current month vs previous month comparison
    change_percentage = ((stats['this_month_spending'] - stats['prev_month_spending']) / 
                        stats['prev_month_spending'] * 100) if stats['prev_month_spending'] > 0 else 0
    
    summary = f"""
    💰 **Spending Overview**: You've spent ${stats['total_spent']:,.2f} across {stats['total_transactions']} transactions, averaging ${stats['average_transaction']:.2f} per transaction.

    🏆 **Top Category**: {top_category} is your highest spending category at ${top_category_amount:,.2f}. Current month spending: ${stats['this_month_spending']:,.2f}.

    📈 **Monthly Comparison**: {'Increase' if change_percentage > 0 else 'Decrease'} of {abs(change_percentage):.1f}% from last month (${stats['prev_month_spending']:,.2f} → ${stats['this_month_spending']:,.2f}).

    📊 **Daily Patterns**: You spend the most on {highest_day}s (${highest_day_amount:.2f} average). Largest single transaction: ${stats['largest_transaction']:.2f}.

    💡 **Budget Insight**: Consider allocating specific budgets for {top_category} and monitoring daily spending on {highest_day}s.
    """
    
    return summary.strip()

def create_charts(df):
    """Create accurate Plotly charts"""
    # Spending by Category Pie Chart - Fixed
    category_totals = df.groupby('category')['amount'].sum().reset_index()
    fig1 = px.pie(
        category_totals, 
        values='amount', 
        names='category',
        title='Spending Distribution by Category',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig1.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percent}'
    )
    fig1.update_layout(
        uniformtext_minsize=12, 
        uniformtext_mode='hide',
        showlegend=True
    )
    category_chart = pio.to_html(fig1, full_html=False, div_id="categoryChart")
    
    # Monthly Trend with accurate data
    df['month_year'] = df['date'].dt.to_period('M').astype(str)
    monthly_data = df.groupby('month_year')['amount'].sum().reset_index()
    monthly_data = monthly_data.sort_values('month_year')
    
    fig2 = px.line(
        monthly_data, 
        x='month_year', 
        y='amount',
        title='Monthly Spending Trend',
        labels={'amount': 'Amount ($)', 'month_year': 'Month'},
        markers=True,
        line_shape='spline'
    )
    fig2.update_traces(
        hovertemplate='<b>%{x}</b><br>Total: $%{y:,.2f}'
    )
    monthly_chart = pio.to_html(fig2, full_html=False, div_id="monthlyChart")
    
    # Daily Spending Pattern
    df['day_of_week'] = df['date'].dt.day_name()
    daily_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_avg = df.groupby('day_of_week')['amount'].mean().reindex(daily_order).fillna(0)
    
    fig3 = px.bar(
        x=daily_avg.index, 
        y=daily_avg.values,
        title='Average Spending by Day of Week',
        labels={'x': 'Day of Week', 'y': 'Average Amount ($)'},
        color=daily_avg.values,
        color_continuous_scale='Blues'
    )
    fig3.update_traces(
        hovertemplate='<b>%{x}</b><br>Average: $%{y:.2f}'
    )
    daily_chart = pio.to_html(fig3, full_html=False, div_id="dailyChart")
    
    return category_chart, monthly_chart, daily_chart

def generate_monthly_statement(df):
    """Generate comprehensive monthly statement data"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Filter current month transactions
    monthly_df = df[(df['date'].dt.month == current_month) & (df['date'].dt.year == current_year)]
    
    if monthly_df.empty:
        # Use last available month if current month has no data
        monthly_df = df[df['date'] == df['date'].max()]
    
    category_totals = monthly_df.groupby('category')['amount'].sum().sort_values(ascending=False)
    
    statement_summary = {
        'current_month_spending': round(monthly_df['amount'].sum(), 2),
        'transactions_this_month': len(monthly_df),
        'daily_average': round(monthly_df['amount'].sum() / len(monthly_df['date'].dt.day.unique()), 2),
        'statement_period': f"{monthly_df['date'].min().strftime('%Y-%m-%d')} to {monthly_df['date'].max().strftime('%Y-%m-%d')}",
        'top_category': category_totals.index[0] if not category_totals.empty else 'N/A',
        'top_category_amount': round(category_totals.iloc[0], 2) if not category_totals.empty else 0
    }
    
    return statement_summary, monthly_df

@app.route('/')
def index():
    """Main page route"""
    df = generate_transactions(150)
    stats = analyze_spending(df)
    ai_summary = generate_ai_summary(stats, df)
    category_chart, monthly_chart, daily_chart = create_charts(df)
    recent_transactions = df.head(15).to_dict('records')
    
    return render_template(
        'index.html',
        stats=stats,
        ai_summary=ai_summary,
        category_chart=category_chart,
        monthly_chart=monthly_chart,
        daily_chart=daily_chart,
        recent_transactions=recent_transactions
    )

@app.route('/refresh')
def refresh_data():
    """API endpoint to refresh data"""
    df = generate_transactions(150)
    stats = analyze_spending(df)
    ai_summary = generate_ai_summary(stats, df)
    recent_transactions = df.head(15).to_dict('records')
    
    return jsonify({
        'stats': stats,
        'ai_summary': ai_summary,
        'recent_transactions': recent_transactions
    })

@app.route('/generate_statement')
def generate_statement():
    """API endpoint to generate monthly statement"""
    df = generate_transactions(150)
    statement_summary, monthly_df = generate_monthly_statement(df)
    
    return jsonify({
        'statement_summary': statement_summary,
        'monthly_transactions': monthly_df.head(20).to_dict('records')
    })

@app.route('/download_statement')
def download_statement():
    """Download PDF monthly statement"""
    df = generate_transactions(150)
    statement_summary, monthly_df = generate_monthly_statement(df)
    
    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 100, "Monthly Bank Statement")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 130, f"Statement Period: {statement_summary['statement_period']}")
    
    # Summary
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 180, "Summary")
    p.setFont("Helvetica", 12)
    
    y_position = height - 210
    summaries = [
        f"Total Spending: ${statement_summary['current_month_spending']:.2f}",
        f"Number of Transactions: {statement_summary['transactions_this_month']}",
        f"Daily Average: ${statement_summary['daily_average']:.2f}",
        f"Top Category: {statement_summary['top_category']} (${statement_summary['top_category_amount']:.2f})"
    ]
    
    for summary in summaries:
        p.drawString(120, y_position, summary)
        y_position -= 25
    
    # Transactions
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y_position - 30, "Recent Transactions")
    p.setFont("Helvetica", 10)
    
    y_position -= 60
    for _, transaction in monthly_df.head(15).iterrows():
        if y_position < 100:
            p.showPage()
            p.setFont("Helvetica", 10)
            y_position = height - 100
        
        p.drawString(120, y_position, 
                    f"{transaction['date'].strftime('%Y-%m-%d')} - {transaction['merchant']} - "
                    f"{transaction['category']} - ${transaction['amount']:.2f}")
        y_position -= 20
    
    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"monthly_statement_{datetime.now().strftime('%Y%m')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/api/transactions')
def get_transactions():
    """API endpoint to get all transactions"""
    df = generate_transactions(150)
    return jsonify(df.to_dict('records'))

if __name__ == '__main__':
    print("🚀 Starting AI Spending Analyzer...")
    print("📊 Open http://localhost:5000 in your browser")
    print("📈 Features: Fixed pie chart, accurate spending history, monthly statements")
    print("💾 Buttons: Refresh Data, Generate Statement, Download PDF")
    app.run(debug=True, host='0.0.0.0', port=5000)