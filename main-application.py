import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from io import StringIO
import datetime
import warnings
warnings.filterwarnings('ignore')

def fetch_retail_data():
    """Fetch retail sales data from a public GitHub repository"""
    url = "https://raw.githubusercontent.com/microsoft/sql-server-samples/master/samples/databases/adventureworks/data/csv/Sales.SalesOrderHeader.csv"
    response = requests.get(url)
    sales_data = pd.read_csv(StringIO(response.text))
    
    # Additional product data
    product_url = "https://raw.githubusercontent.com/microsoft/sql-server-samples/master/samples/databases/adventureworks/data/csv/Production.Product.csv"
    product_response = requests.get(product_url)
    product_data = pd.read_csv(StringIO(product_response.text))
    
    return sales_data, product_data

def prepare_data(sales_data, product_data):
    """Clean and prepare the data for analysis"""
    # Convert date columns
    sales_data['OrderDate'] = pd.to_datetime(sales_data['OrderDate'])
    
    # Extract relevant columns
    sales_data = sales_data[['SalesOrderID', 'OrderDate', 'TotalDue', 'Status', 'CustomerID']]
    product_data = product_data[['ProductID', 'Name', 'ListPrice', 'ProductLine']]
    
    return sales_data, product_data

def create_dashboard(sales_data, product_data):
    """Create and display the dashboard"""
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Monthly Sales Trend', 'Sales Status Distribution',
                       'Price Distribution', 'Top Products by Price'),
        specs=[[{"secondary_y": True}, {}],
               [{}, {}]]
    )
    
    # 1. Monthly Sales Trend
    monthly_sales = sales_data.groupby(sales_data['OrderDate'].dt.strftime('%Y-%m'))\
        .agg({'TotalDue': 'sum', 'SalesOrderID': 'count'})\
        .reset_index()
    
    fig.add_trace(
        go.Scatter(x=monthly_sales['OrderDate'], y=monthly_sales['TotalDue'],
                  name="Total Sales", line=dict(color='blue')),
        row=1, col=1, secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=monthly_sales['OrderDate'], y=monthly_sales['SalesOrderID'],
                  name="Order Count", line=dict(color='red')),
        row=1, col=1, secondary_y=True
    )
    
    # 2. Sales Status Distribution
    status_dist = sales_data['Status'].value_counts()
    fig.add_trace(
        go.Pie(labels=status_dist.index, values=status_dist.values,
               name="Status Distribution"),
        row=1, col=2
    )
    
    # 3. Price Distribution
    fig.add_trace(
        go.Histogram(x=product_data['ListPrice'], name="Price Distribution",
                    nbinsx=30),
        row=2, col=1
    )
    
    # 4. Top Products by Price
    top_products = product_data.nlargest(10, 'ListPrice')
    fig.add_trace(
        go.Bar(x=top_products['Name'], y=top_products['ListPrice'],
               name="Top Products"),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(height=800, width=1200, title_text="Sales & Pricing Operations Dashboard",
                     showlegend=True)
    fig.update_xaxes(tickangle=45)
    
    # Save the dashboard
    fig.write_html("sales_dashboard.html")
    
def generate_insights(sales_data, product_data):
    """Generate key insights from the data"""
    insights = {
        "total_sales": sales_data['TotalDue'].sum(),
        "total_orders": len(sales_data),
        "avg_order_value": sales_data['TotalDue'].mean(),
        "avg_product_price": product_data['ListPrice'].mean(),
        "most_expensive_product": product_data.loc[product_data['ListPrice'].idxmax(), 'Name']
    }
    
    # Save insights to file
    with open("insights.txt", "w") as f:
        f.write("Key Business Insights:\n\n")
        f.write(f"Total Sales: ${insights['total_sales']:,.2f}\n")
        f.write(f"Total Orders: {insights['total_orders']:,}\n")
        f.write(f"Average Order Value: ${insights['avg_order_value']:,.2f}\n")
        f.write(f"Average Product Price: ${insights['avg_product_price']:,.2f}\n")
        f.write(f"Most Expensive Product: {insights['most_expensive_product']}\n")

def main():
    # Fetch data
    print("Fetching data...")
    sales_data, product_data = fetch_retail_data()
    
    # Prepare data
    print("Preparing data...")
    sales_data, product_data = prepare_data(sales_data, product_data)
    
    # Create dashboard
    print("Creating dashboard...")
    create_dashboard(sales_data, product_data)
    
    # Generate insights
    print("Generating insights...")
    generate_insights(sales_data, product_data)
    
    print("\nDashboard and insights have been generated successfully!")
    print("Open 'sales_dashboard.html' in your web browser to view the dashboard.")
    print("Check 'insights.txt' for key business metrics.")

if __name__ == "__main__":
    main()
