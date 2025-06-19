import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import numpy as np

# Set global Plotly theme
pio.templates.default = "plotly_dark"

# Page configuration
st.set_page_config(page_title="Cost of Living Dashboard", page_icon="📊", layout="wide")

# Optional dark theme styling
st.markdown("""
    <style>
    .main { background-color: #333333; }
    h1, h2, h3 { color: #ffffff; font-weight: 800; font-size: 2em; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    .metric-card { background-color: #4a4a4a; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    </style>
""", unsafe_allow_html=True)

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("Cost_of_Living_Index_2022.csv")

df = load_data()

# Clean and validate data
df.columns = df.columns.str.strip()
for col in ['Country', 'City']:
    if col in df.columns:
        df = df.dropna(subset=[col])

# Keep only numeric rows for plotting
numeric_cols = ['Cost of Living Index', 'Rent Index', 'Groceries Index',
                'Restaurant Price Index', 'Local Purchasing Power Index']
existing_numeric_cols = [col for col in numeric_cols if col in df.columns]
df = df.dropna(subset=existing_numeric_cols)

# Country filter
countries = sorted(df["Country"].dropna().unique().tolist())
selected_countries = st.sidebar.multiselect("🌍 Filter by Country", countries, default=countries[:1])
filtered_df = df[df["Country"].isin(selected_countries)] if selected_countries else df

# Title
st.title("📊 Cost of Living Analysis Dashboard")
st.markdown("Explore cost-of-living metrics for global cities based on 2022 data.")

# KPIs
col1, col2, col3 = st.columns(3)
if "Cost of Living Index" in filtered_df.columns:
    col1.metric("Avg Cost of Living Index", f"{filtered_df['Cost of Living Index'].mean():.2f}")
if "Rent Index" in filtered_df.columns:
    col2.metric("Avg Rent Index", f"{filtered_df['Rent Index'].mean():.2f}")
if "Local Purchasing Power Index" in filtered_df.columns:
    col3.metric("Avg Purchasing Power", f"{filtered_df['Local Purchasing Power Index'].mean():.2f}")

st.markdown("---")

# Scatter: Cost of Living vs Rent Index
if all(col in filtered_df.columns for col in ['Cost of Living Index', 'Rent Index', 'Country']):
    st.subheader("🟣 Cost of Living vs Rent Index")
    fig1 = px.scatter(
        filtered_df,
        x='Cost of Living Index',
        y='Rent Index',
        color='Country',
        size=filtered_df.get('Local Purchasing Power Index', None),
        hover_name=filtered_df.get('City', None),
        title='Cost of Living vs Rent Index'
    )
    st.plotly_chart(fig1, use_container_width=True)

# Two-column charts
col_left, col_right = st.columns(2)

with col_left:
    if "Cost of Living Index" in df.columns and "Country" in df.columns:
        st.subheader("🏙️ Top 10 Countries by Cost of Living")
        top_cost = filtered_df.groupby("Country")["Cost of Living Index"].mean().reset_index()
        top_cost = top_cost.sort_values('Cost of Living Index', ascending=False).head(10)
        fig2 = px.bar(top_cost, x='Cost of Living Index', y='Country', orientation='h')
        st.plotly_chart(fig2, use_container_width=True)

with col_right:
    if "Local Purchasing Power Index" in df.columns and "Country" in df.columns:
        st.subheader("💵 Top 10 Countries by Purchasing Power")
        top_power = filtered_df.groupby("Country")["Local Purchasing Power Index"].mean().reset_index()
        top_power = top_power.sort_values('Local Purchasing Power Index', ascending=False).head(10)
        fig3 = px.bar(top_power, x='Local Purchasing Power Index', y='Country', orientation='h')
        st.plotly_chart(fig3, use_container_width=True)

# Groceries index distribution
if "Groceries Index" in filtered_df.columns:
    st.subheader("🛒 Groceries Index Distribution")
    fig4 = px.histogram(filtered_df, x='Groceries Index', nbins=25)
    st.plotly_chart(fig4, use_container_width=True)

# Restaurant vs Purchasing Power
if "Restaurant Price Index" in filtered_df.columns and "Local Purchasing Power Index" in filtered_df.columns:
    st.subheader("🍽️ Restaurant Price vs Purchasing Power")
    fig5 = px.scatter(
        filtered_df,
        x='Restaurant Price Index',
        y='Local Purchasing Power Index',
        color='Country',
        hover_name=filtered_df.get('City', None),
        title="Restaurant Price vs Purchasing Power Index"
    )
    st.plotly_chart(fig5, use_container_width=True)

# Correlation heatmap
if len(existing_numeric_cols) >= 2:
    st.subheader("🧮 Correlation Matrix of Indices")
    fig6 = px.imshow(filtered_df[existing_numeric_cols].corr(), text_auto=True, aspect="auto")
    st.plotly_chart(fig6, use_container_width=True)

# Download filtered data
st.markdown("---")
st.download_button(
    label="⬇️ Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_cost_of_living.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.caption("Developed for Economic Data Analysis Project | Source: Cost_of_Living_Index_2022.csv")
