import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# File path (update if necessary)
file_path = "/Users/luigilongo/Desktop/streamlit_prova/data.xlsx"

# Load the Excel file
try:
    df0 = pd.read_excel(file_path, engine="openpyxl", index_col=0, parse_dates=True)
except FileNotFoundError:
    st.error(f"File not found: {file_path}")
    st.stop()

# Define h_step (shift parameter)
h_step = 1  # Change this if needed

# Shift index by h_step months
df0_shifted = df0.copy()
df0_shifted.index = df0_shifted.index - pd.DateOffset(months=h_step)


# **User selects the year range**
min_year = 2019
max_year = 2030  # Get last year in data

start_year, end_year = st.slider(
    "Select the year range:",
    min_value=min_year, max_value=max_year,
    value=(2023, 2024), step=1
)

# Filter data based on selected years
df_filtered = df0_shifted.loc[str(start_year):str(end_year)]


# Create interactive Plotly figure
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_filtered.index, y=df_filtered['inflation'],
    mode='lines', name='True Inflation', line=dict(color='green', width=2.5)
))

fig.add_trace(go.Scatter(
    x=df_filtered.index, y=df_filtered['pred_signal_llama_70b'],
    mode='lines', name='Llama 70B Prediction', line=dict(color='red', width=1, dash='dash')
))

fig.add_trace(go.Scatter(
    x=df_filtered.index, y=df_filtered['pred_swap'],
    mode='lines', name='Swap Prediction', line=dict(color='blue', width=1, dash='dot')
))

# fig.add_trace(go.Scatter(
#     x=df_filtered.index, y=df_filtered['pred_ar'],
#     mode='lines', name='AR Prediction', line=dict(color='brown', width=1, dash='dot')
# ))

# Customize layout
fig.update_layout(
    title="Inflation Predictions vs. True Values (2024 Onward)",
    xaxis_title="Date",
    yaxis_title="Inflation Rate",
    legend=dict(x=0, y=1),
    hovermode="x unified",
    template="plotly_white"
)

# Streamlit app
st.title("📈 Interactive Inflation Prediction Plot")

st.plotly_chart(fig, use_container_width=True)
