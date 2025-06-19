import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import plotly.io as pio

# Set global plotly template to dark
pio.templates.default = "plotly_dark"

# Streamlit page settings
st.set_page_config(page_title="Cost of Living Dashboard", page_icon="📊", layout="wide")

# Custom styling (optional)
st.markdown("""
    <style>
    .main { background-color: #333333; }
    h1, h2, h3 { color: #ffffff; font-weight: 800; font-size: 2em; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
    .metric-card { background-color: #4a4a4a; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    </style>
""", unsafe_allow_html=True)

# Load default or uploaded dataset
@st.cache_data
def load_default_data():
    return pd.read_csv("Cost_of_Living_Index_2022.csv")

st.sidebar.header("Data Source")
uploaded_file = st.sidebar.file_uploader("Upload your Cost of Living CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = load_default_data()

# Preprocessing
df.dropna(subset=['Country', 'City'], inplace=True)
df.columns = df.columns.str.strip()
df = df[df.select_dtypes(include=[np.number]).notna().all(axis=1)]

# Country filter (multiselect)
countries = df["Country"].dropna().unique().tolist()
selected_countries = st.sidebar.multiselect("Select Country/Countries", sorted(countries), default=countries[:1])
filtered_df = df[df["Country"].isin(selected_countries)] if selected_countries else df

# Title and description
st.title("📊 Cost of Living Analysis Dashboard")
st.markdown("Interactive dashboard to explore global cost-of-living indicators using 2022 data.")

# KPI Cards
col1, col2, col3 = st.columns(3)
col1.metric("Avg Cost of Living Index", f"{filtered_df['Cost of Living Index'].mean():.2f}")
col2.metric("Avg Rent Index", f"{filtered_df['Rent Index'].mean():.2f}")
col3.metric("Avg Purchasing Power", f"{filtered_df['Local Purchasing Power Index'].mean():.2f}")

st.markdown("---")

# Scatter: Cost of Living vs Rent
st.subheader("🟣 Cost of Living vs Rent Index")
fig1 = px.scatter(
    filtered_df, x='Cost of Living Index', y='Rent Index', color='Country',
    size='Local Purchasing Power Index', hover_name='City',
    title='Cost of Living vs Rent Index (Size = Purchasing Power)',
    labels={'Cost of Living Index': 'Cost of Living Index', 'Rent Index': 'Rent Index'}
)
st.plotly_chart(fig1, use_container_width=True)

# Two column layout for bar charts and histograms
col_left, col_right = st.columns(2)

# Top countries by cost of living
with col_left:
    st.subheader("🏙️ Top 10 Countries by Cost of Living")
    top_cost = filtered_df[['Country', 'Cost of Living Index']].groupby("Country").mean().reset_index()
    top_cost = top_cost.sort_values('Cost of Living Index', ascending=False).head(10)
    fig2 = px.bar(top_cost, x='Cost of Living Index', y='Country', orientation='h')
    st.plotly_chart(fig2, use_container_width=True)

# Top countries by purchasing power
with col_right:
    st.subheader("💵 Top 10 Countries by Purchasing Power")
    top_power = filtered_df[['Country', 'Local Purchasing Power Index']].groupby("Country").mean().reset_index()
    top_power = top_power.sort_values('Local Purchasing Power Index', ascending=False).head(10)
    fig3 = px.bar(top_power, x='Local Purchasing Power Index', y='Country', orientation='h')
    st.plotly_chart(fig3, use_container_width=True)

# Groceries Index Distribution
st.subheader("🛒 Groceries Index Distribution")
fig4 = px.histogram(filtered_df, x='Groceries Index', nbins=25,
                    labels={'Groceries Index': 'Groceries Index'})
st.plotly_chart(fig4, use_container_width=True)

# Restaurant Price vs. Purchasing Power
st.subheader("🍽️ Restaurant Price vs Purchasing Power")
fig5 = px.scatter(filtered_df, x='Restaurant Price Index', y='Local Purchasing Power Index',
                  color='Country', hover_name='City')
st.plotly_chart(fig5, use_container_width=True)

# Correlation Matrix
st.subheader("🧮 Index Correlation Matrix")
corr_data = filtered_df.drop(columns=["City", "Country"], errors='ignore').corr()
fig6 = px.imshow(corr_data, text_auto=True, aspect="auto")
st.plotly_chart(fig6, use_container_width=True)

# Data download option
st.markdown("---")
st.download_button("⬇️ Download Filtered Data as CSV",
                   data=filtered_df.to_csv(index=False),
                   file_name="filtered_cost_of_living.csv",
                   mime="text/csv")

# Footer
st.markdown("---")
st.caption("Developed for Economic Data Analysis Project | Source: Numbeo (2022)")
