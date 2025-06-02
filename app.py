import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Matiks - Data Analyst Data - Sheet1.csv", parse_dates=['Signup_Date', 'Last_Login'])
    df['Signup_Date'] = pd.to_datetime(df['Signup_Date'], errors='coerce')
    df['Last_Login'] = pd.to_datetime(df['Last_Login'], errors='coerce')
    return df

df = load_data()

st.title("📊 Matiks User Engagement & Revenue Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
device_filter = st.sidebar.multiselect("Device Type", df['Device_Type'].unique(), default=df['Device_Type'].unique())
game_filter = st.sidebar.multiselect("Preferred Game Mode", df['Preferred_Game_Mode'].unique(), default=df['Preferred_Game_Mode'].unique())

# Apply filters
filtered_df = df[(df['Device_Type'].isin(device_filter)) & (df['Preferred_Game_Mode'].isin(game_filter))]

# Summary Stats
st.subheader("🔢 Key Metrics")
total_users = filtered_df.shape[0]
total_revenue = filtered_df['Total_Revenue_USD'].sum()
avg_revenue = filtered_df['Total_Revenue_USD'].mean()
total_sessions = filtered_df['Total_Play_Sessions'].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Users", total_users)
col2.metric("Total Revenue ($)", f"{total_revenue:,.2f}")
col3.metric("Avg Revenue/User ($)", f"{avg_revenue:,.2f}")
col4.metric("Total Sessions", total_sessions)

# Revenue Trend
st.subheader("📈 Revenue by Signup Date")
daily_rev = filtered_df.groupby('Signup_Date')['Total_Revenue_USD'].sum().reset_index()
fig1 = px.line(daily_rev, x='Signup_Date', y='Total_Revenue_USD', title='Revenue Over Time')
st.plotly_chart(fig1, use_container_width=True)

# User Engagement
st.subheader("📊 Sessions vs Revenue")
fig2 = px.scatter(filtered_df, x='Total_Play_Sessions', y='Total_Revenue_USD', color='Device_Type', hover_data=['Username'])
st.plotly_chart(fig2, use_container_width=True)

# Game Mode Breakdown
st.subheader("🎮 Revenue by Game Mode")
game_rev = filtered_df.groupby('Preferred_Game_Mode')['Total_Revenue_USD'].sum().reset_index().sort_values(by='Total_Revenue_USD', ascending=False)
fig3 = px.bar(game_rev, x='Preferred_Game_Mode', y='Total_Revenue_USD', title='Revenue by Game Mode')
st.plotly_chart(fig3, use_container_width=True)

# High-Value Users
st.subheader("💎 Top 10 Revenue Users")
top_users = filtered_df[['Username', 'Total_Revenue_USD']].sort_values(by='Total_Revenue_USD', ascending=False).head(10)
st.dataframe(top_users)

# Churn Analysis
st.subheader("⚠️ Potential Churn Signals")
filtered_df['Days_Since_Last_Login'] = (datetime.today() - filtered_df['Last_Login']).dt.days

# Less strict threshold to ensure visibility
churn_users = filtered_df[(filtered_df['Total_Play_Sessions'] < 10) & (filtered_df['Days_Since_Last_Login'] > 7)][['Username', 'Days_Since_Last_Login', 'Total_Play_Sessions']]

if churn_users.empty:
    st.write("No high-risk churn users found based on the current filters.")
else:
    st.write("Users with <10 sessions and >7 days since last login:")
    st.dataframe(churn_users.sort_values(by='Days_Since_Last_Login', ascending=False).head(10))

st.caption("Made with ❤️ by [Palak Soni]")