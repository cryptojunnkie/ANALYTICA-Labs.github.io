import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import numpy as np
import time

# Fetching stock data from Yahoo Finance
def get_stock_data(symbol, time_range="max"):
    stock = yf.Ticker(symbol)
    stock_data = stock.history(period=time_range)
    
    if stock_data.empty:
        st.error("Error: Unable to fetch stock data.")
        return None

    stock_data = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']]
    return stock_data

# Calculate price differences based on days
def calculate_price_differences(stock_data):
    daily_diff = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
    weekly_diff = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-6]
    monthly_diff = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-22]
    days_90_diff = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-90]
    months_6_diff = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-132]
    return daily_diff, weekly_diff, monthly_diff, days_90_diff, months_6_diff

# Calculate a regression curve for the data and bands
def calculate_regression_curve(x_values, y_values, degree=2, num_bands=4):
    x_numeric = np.arange(len(x_values))  # Use an array of indices as numeric values
    y_numeric = y_values.values  # Extract the actual array from the pandas Series

    x_transformed = x_numeric / np.max(x_numeric)  # Normalize x values to [0, 1]
    degree_transformed = np.sqrt(degree)  # Apply a square root transformation to adjust the smoothing effect

    coefficients = np.polyfit(x_transformed, y_numeric, degree_transformed)
    polynomial = np.poly1d(coefficients)
    regression_values = polynomial(x_transformed)

    residuals = y_numeric - regression_values
    std_residuals = np.std(residuals)
    
    bands = []
    colors = ['green', 'blue', 'red', 'purple']  # Define unique colors for the bands
    band_annotations = [
        ('Take Profit Level 1', 'black', 'DCA Buy Level 1', 'green'),
        ('Take Profit Level 2', 'blue', 'DCA Buy Level 2', 'blue'),
        ('Take Profit Level 3', 'red', 'DCA Buy Level 3', 'red'),
        ('Take Profit Level 4', 'purple', 'DCA Buy Level 4', 'purple')
    ]

    for i in range(1, num_bands + 1):
        lower_band = regression_values - i * std_residuals
        upper_band = regression_values + i * std_residuals
        bands.append((lower_band, upper_band, colors[i - 1], band_annotations[i - 1]))

    return regression_values, bands, degree

# Main app function
def app():
    st.set_page_config(page_title="Stock Dashboard", layout="wide", page_icon="📈")
    st.title("📈 Stock Dashboard")

    popular_symbols = ["AAL", "AAPL", "ADBE", "ABNB", "ADSK", "ADP", "ALXN", "ALGN", "ALLK", "ALNY", "AMAT", "AMZN", "ASML", "ADP", "ATVI", "AVGO", "BABA", "BILI", "BIIB", "BKNG", "BMRN", "CDNS", "CELG", "CERN", "CHTR", "COUP", "CRWD", "DDOG", "DOCU", "DXCM", "EA", "EBAY", "EXPE", "FAST", "FISV", "FTNT", "GILD", "GME", "GOOGL", "GOOG", "HAS", "HOLX", "IDXX", "ILMN", "INCY", "INTC", "INTU", "ISRG", "JD", "KLAC", "LRCX", "LULU", "MAR", "MELI", "META", "MRVL", "MDLZ", "MNST", "MSFT", "MU", "NFLX", "NVDA", "NXPI", "OKTA", "ORLY", "PEP", "PANW", "PAYC", "PYPL", "QCOM", "REGN", "ROST", "SGEN", "SIRI", "SMAR", "SNAP", "SPLK", "SWKS", "TCBI", "TEAM", "TMUS", "TSLA", "TXN", "VRSK", "VRSN", "VRTX", "WBA", "WDAY", "XEL", "XLNX", "ZM", "ZS", "AAVE-USD", "ADA-USD", "ALGO-USD", "APT21794-USD", "AR-USD", "AXS-USD", "AVAX-USD", "BCH-USD", "BGB-USD", "BNB-USD", "BONK-USD", "BRETT29743-USD", "BTCB-USD", "BTC-USD", "BEAM28298-USD", "CHEEL-USD", "CHZ-USD", "CORE23254-USD", "CRO-USD", "DAI-USD", "DOGE-USD", "DOT-USD", "DYDX-USD", "EETH-USD", "ENA-USD", "ETC-USD", "ETH-USD", "EZETH-USD", "FET-USD", "FIL-USD", "FLR-USD", "FLOW-USD", "FLOKI-USD", "FDUSD-USD", "GALA-USD", "GRT6719-USD", "HBAR-USD", "IMX10603-USD", "INJ-USD", "ICP-USD", "JITO-USD", "SOL-USD", "JASMY-USD", "JUP29210-USD", "KAS-USD", "LINK-USD", "LEO-USD", "LDO-USD", "LTC-USD", "MATIC-USD", "METH29035-USD", "MKR-USD", "MNT27075-USD", "NEAR-USD", "NOT-USD", "OKB-USD", "ONDO-USD", "OP-USD", "ORDI-USD", "PEPE24478-USD", "PYTH-USD", "RNDR-USD", "RETH-USD", "RSETH-USD", "RUNE-USD", "SEI-USD", "SHIB-USD", "SOL-USD", "STRK22691-USD", "STX4847-USD", "STETH-USD", "SUI20947-USD", "SUSDE-USD", "TAO22974-USD", "TIA22861-USD", "TON11419-USD", "THETA-USD", "TRX-USD", "UNI7083-USD", "USDC-USD", "USDE29470-USD", "USDT-USD", "VET-USD", "VBNB-USD", "W-USD", "WBNB-USD", "WBETH-USD", "WETH-USD", "WEETH-USD", "WSTETH-USD", "WTRX-USD", "XLM-USD", "XMR-USD", "XRP-USD", "ZBU-USD"]
    symbol = st.sidebar.selectbox("Select a stock symbol:", popular_symbols, index=0)
    chart_types = ["Candlestick Chart", "Line Chart"]
    chart_type = st.sidebar.radio("Select Chart Type:", chart_types)
    
    degree = st.sidebar.slider("Select Polynomial Degree for Regression Curve", min_value=1, max_value=200, value=12, step=1, format="%d", help="Changing the line shape on the stock price chart can affect how often you buy stocks regularly. If the line is wavy, you might buy stocks more often when the price changes a little. This means you'll put a bit of money in more often, which can make your investments more diverse but might cost you more in fees. On the other hand, if the line is smoother, you might buy stocks less frequently based on larger trends, so each time you invest more money but less often. This can make your plan simpler but you might miss some short-term deals. So, it's like deciding how many times you want to buy, how much you want to invest each time, and how much extra it might cost you when you pick how the line looks on the chart.")
    
    # Custom HTML and CSS code for the tooltip with adjusted width and height
    st.sidebar.markdown('''
        <style>
            .tooltip {
                position: relative;
                display: inline-block;
                cursor: help;
            }
            .tooltip .tooltiptext {
                visibility: hidden; 
                width: 250px; /* Set the desired width for the tooltip */
                max-height: 300px; /* Set the maximum height for the tooltip */
                background-color: #EFF2F6; 
                color: black; 
                text-align: center; 
                border-radius: 6px; 
                padding: 5px; 
                position: absolute; 
                z-index: 1;
                left: 65%;
                bottom: 100%; /* Adjust the distance below the info icon */
                transform: translateX(-50%);
                overflow-y: auto; /* Add vertical scrollbar when content exceeds max-height */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Add box shadow with 8px blur and 0.1 opacity */
            }
            .tooltip:hover .tooltiptext {
                visibility: visible;
            }
        </style>
        <div class="tooltip">
            <b style="font-size: 20px;"> 
                NASDAQ TOP STOCKS LIST
            </b>
            <span class="tooltiptext">
                "Apple Inc. (AAPL)",
                "Microsoft Corporation (MSFT)",
                "Alphabet Inc. (GOOG, GOOGL)",
                "Amazon.com Inc. (AMZN)",
                "Tesla Inc. (TSLA)",
                "Meta Platforms Inc. (META)",
                "NVIDIA Corporation (NVDA)",
                "PepsiCo Inc. (PEP)"
            </span>
        </div>
    ''', unsafe_allow_html=True)
    
    if symbol:
        stock_data = get_stock_data(symbol)
        
        if stock_data is not None:
            stock_info = yf.Ticker(symbol).info
            if 'longName' in stock_info:
                stock_name = stock_info['longName']
            elif 'shortName' in stock_info:
                stock_name = stock_info['shortName']
            else:
                stock_name = symbol

            # Display stock name with customized font size and weight
            st.markdown(f"<p style='font-size:30px; font-weight:bold;'>{stock_name}</p>", unsafe_allow_html=True)
    
            daily_diff, weekly_diff, monthly_diff, days_90_diff, months_6_diff = calculate_price_differences(stock_data)
            percentage_difference_daily = (daily_diff / stock_data['Close'].iloc[-2]) * 100
            percentage_difference_weekly = (weekly_diff / stock_data['Close'].iloc[-6]) * 100
            percentage_difference_monthly = (monthly_diff / stock_data['Close'].iloc[-22]) * 100
            percentage_difference_days_90 = (days_90_diff / stock_data['Close'].iloc[-90]) * 100
            percentage_difference_months_6 = (months_6_diff / stock_data['Close'].iloc[-132]) * 100
            
            latest_close_price = stock_data['Close'].iloc[-1]
            max_52_week_high = stock_data['Close'].rolling(window=252).max().iloc[-1]
            min_52_week_low = stock_data['Close'].rolling(window=252).min().iloc[-1]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Close Price", f"${latest_close_price:,.2f}")
            with col2:
                st.metric("52-Week High", f"${max_52_week_high:,.2f}")
            with col3:
                st.metric("52-Week Low", f"${min_52_week_low:,.2f}")

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Daily Price Difference", f"${daily_diff:,.2f}", f"{percentage_difference_daily:+.2f}%")
            with col2:
                st.metric("Weekly Price Difference", f"${weekly_diff:,.2f}",f"{percentage_difference_weekly:+.2f}%")
            with col3:
                st.metric("Monthly Price Difference", f"${monthly_diff:.2f}",f"{percentage_difference_monthly:+.2f}%")
            with col4:
                st.metric("90 Days Price Difference", f"${days_90_diff:,.2f}",f"{percentage_difference_days_90:+.2f}%")
            with col5:
                st.metric("6 Months Price Difference", f"${months_6_diff:,.2f}",f"{percentage_difference_months_6:+.2f}%")

            st.subheader(chart_type)
            chart_data = go.Figure()
            if chart_type == "Candlestick Chart":
                chart_data.add_trace(go.Candlestick(x=stock_data.index, open=stock_data['Open'], high=stock_data['High'], low=stock_data['Low'], close=stock_data['Close']))

            regression_values, bands, degree = calculate_regression_curve(stock_data.index, stock_data['Close'], degree)
            chart_data.add_trace(go.Scatter(x=stock_data.index, y=regression_values, mode='lines', name=f'Regression Curve', line=dict(color='orange', width=2)))

            for i, (lower_band, upper_band, color, (upper_text, upper_color, lower_text, lower_color)) in enumerate(bands):
                chart_data.add_trace(go.Scatter(x=stock_data.index, y=upper_band, mode='lines', name= "Take Profit Zones", line=dict(color=color, width=1), showlegend=False))
                chart_data.add_trace(go.Scatter(x=stock_data.index, y=lower_band, mode='lines', name= "DCA Buy Zones",line=dict(color=color, width=1), showlegend=False))

                annotation_offset = 0.2 * len(stock_data)  # Adjust this value for the desired offset
                
                # Set x-position of annotations to move freely from the right end of the stock data
                annotation_x = stock_data.index[-1] + pd.DateOffset(days=annotation_offset)

                chart_data.add_annotation(x=annotation_x, y=upper_band[-1], text=upper_text, font=dict(color=upper_color, size=12), showarrow=False)
                chart_data.add_annotation(x=annotation_x, y=lower_band[-1], text=lower_text, font=dict(color=lower_color, size=12), showarrow=False)

            if chart_type == "Line Chart":
                chart_data.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='Close Price', line=dict(color='blue', width=1)))

            # Update layout to remove extra annotations
            chart_data.update_layout(title=f"{symbol} - {chart_type}", xaxis_rangeslider_visible=False, yaxis=dict(title="Price", tickprefix="$"), xaxis_title="")
            st.plotly_chart(chart_data, use_container_width=True)

            st.subheader("Summary")
            st.dataframe(stock_data.tail(30))  # Display the last 30 days of data
            
            st.markdown("""
                <style>
                    .reportview-container {
                        margin-top: -2em;
                    }
                    .stDeployButton {display:none;}
                    footer {visibility: hidden;}
                    #stDecoration {display:none;}
                </style>
            """, unsafe_allow_html=True)
            
        # Refresh the app every 5 minutes
        time.sleep(60)
        st.experimental_rerun()


if __name__ == "__main__":
     app()
