import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# File path (update if necessary)
file_path = os.path.join(os.getcwd(), "data.xlsx")

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
max_year = 2026  # Get last year in data

start_year, end_year = st.slider(
    "Select the year range:",
    min_value=min_year, max_value=max_year,
    value=(2020, 2023), step=1
)

# Filter data based on selected years
df_filtered = df0_shifted.loc[str(start_year):str(end_year)]


# Create interactive Plotly figure
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_filtered.index, y=df_filtered['inflation'],
    mode='lines', name='True Inflation: Core PCE yoy', line=dict(color='green', width=2.5)
))

fig.add_trace(go.Scatter(
    x=df_filtered.index, y=df_filtered['pred_signal_llama_70b'],
    mode='lines+markers',  # ✅ Markers added here
    name='Llama 70B Prediction',
    line=dict(color='red', width=1, dash='dash'),
    marker=dict(size=6, symbol='circle', color='red')  # ✅ Customize markers
))

fig.add_trace(go.Scatter(
    x=df_filtered.index, y=df_filtered['pred_swap'],
    mode='lines+markers',  # ✅ Markers added here
    name='Swap Prediction',
    line=dict(color='blue', width=1, dash='dot'),
    marker=dict(size=6, symbol='diamond', color='blue')  # ✅ Customize markers
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
st.title("📈 Inflation Nowcast (Core PCE)")

st.plotly_chart(fig, use_container_width=True)






# Checkbox to toggle the error plot
show_loss_plot = st.checkbox("Show Prediction Error (Loss)")

if show_loss_plot:
    # Compute absolute errors
    df_filtered['loss_llama_70b'] = abs(df_filtered['inflation'] - df_filtered['pred_signal_llama_70b'])
    df_filtered['loss_swap'] = abs(df_filtered['inflation'] - df_filtered['pred_swap'])

    # Create interactive Plotly figure for Loss/Error
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['loss_llama_70b'],
        mode='lines+markers',  
        name='Llama 70B Error',
        line=dict(color='red', width=1, dash='dash'),
        marker=dict(size=6, symbol='circle', color='red')  
    ))

    fig2.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['loss_swap'],
        mode='lines+markers',  
        name='Swap Prediction Error',
        line=dict(color='blue', width=1, dash='dot'),
        marker=dict(size=6, symbol='diamond', color='blue')  
    ))

    # Customize layout
    fig2.update_layout(
        title=f"Prediction Errors (Absolute Loss) ({start_year}-{end_year})",
        xaxis_title="Date",
        yaxis_title="Absolute Error",
        legend=dict(x=0, y=1),
        hovermode="x unified",
        template="plotly_white"
    )

    # Show the loss plot
    st.plotly_chart(fig2, use_container_width=True)
