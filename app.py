import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# User selects the region
region = st.radio("Select Region:", ["US (Core PCE)", "Europe (HICP)"])

# Load the data based on user selection
if region == "US (Core PCE)":
    file_path = os.path.join(os.getcwd(), "data.xlsx")
    try:
        df0 = pd.read_excel(file_path, engine="openpyxl", index_col=0, parse_dates=True)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        st.stop()
    pred_col = 'pred_swap'
    target_var = 'inflation'
else:
    file_path = os.path.join(os.getcwd(), "data_infl_europe_120.xlsx")
    try:
        df0 = pd.read_excel(file_path, engine="openpyxl", index_col=0, parse_dates=True)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        st.stop()
    pred_col = 'pred_ar'
    target_var = 'inflation'

# Define h_step (shift parameter)
h_step = 1
# Shift index by h_step months
df0_shifted = df0.copy()
df0_shifted.index = df0_shifted.index - pd.DateOffset(months=h_step)

# User selects the year range
min_year = 2019
max_year = 2026
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
    x=df_filtered.index, y=df_filtered[target_var],
    mode='lines', name='True Inflation', line=dict(color='green', width=2.5)
))
fig.add_trace(go.Scatter(
    x=df_filtered.index, y=df_filtered['pred_signal_llama_70b'],
    mode='lines+markers', name='Llama 70B Prediction',
    line=dict(color='red', width=1, dash='dash'),
    marker=dict(size=6, symbol='circle', color='red')
))
fig.add_trace(go.Scatter(
    x=df_filtered.index, y=df_filtered[pred_col],
    if region == "US (Core PCE)":
        mode='lines+markers', name=f'Swap Prediction',
    else:
        mode='lines+markers', name=f'AR Prediction',
    line=dict(color='blue', width=1, dash='dot'),
    marker=dict(size=6, symbol='diamond', color='blue')
))

# Customize layout
fig.update_layout(
    title=f"Inflation Predictions vs. True Values ({region})",
    xaxis_title="Date",
    yaxis_title="Inflation Rate",
    legend=dict(x=0, y=1),
    hovermode="x unified",
    template="plotly_white"
)

# Streamlit app
st.title(f"📈 Inflation Nowcast ({region})")
st.plotly_chart(fig, use_container_width=True)

# Checkbox to toggle the error plot
show_loss_plot = st.checkbox("Show Prediction Error (MAE)")
if show_loss_plot:
    st.write('Mean absolute deviation from the target_var, over time.')
    df_filtered['loss_llama_70b'] = abs(df_filtered[target_var] - df_filtered['pred_signal_llama_70b'])
    df_filtered['loss_pred'] = abs(df_filtered[target_var] - df_filtered[pred_col])
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['loss_llama_70b'],
        mode='lines+markers', name='Llama 70B Error',
        line=dict(color='red', width=1, dash='dash'),
        marker=dict(size=6, symbol='circle', color='red')
    ))
    fig2.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['loss_pred'],
        mode='lines+markers', name=f'{region} Prediction Error',
        line=dict(color='blue', width=1, dash='dot'),
        marker=dict(size=6, symbol='diamond', color='blue')
    ))
    fig2.update_layout(
        title=f"Prediction Errors (Absolute Loss) ({start_year}-{end_year})",
        xaxis_title="Date",
        yaxis_title="Absolute Error",
        legend=dict(x=0, y=1),
        hovermode="x unified",
        template="plotly_white"
    )
    st.plotly_chart(fig2, use_container_width=True)

# Checkbox to toggle the cumulative squared error plot
show_loss_plot_mse = st.checkbox("Show Prediction Error (MSE)")
if show_loss_plot_mse:
    st.write('Cumulative mean squared errors: the best model presents the lowest.')
    df_filtered['loss_llama_70b'] = (df_filtered[target_var] - df_filtered['pred_signal_llama_70b'])**2
    df_filtered['loss_pred'] = (df_filtered[target_var] - df_filtered[pred_col])**2
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['loss_llama_70b'].cumsum(),
        mode='lines+markers', name='Llama 70B Cumulative MSE',
        line=dict(color='red', width=1, dash='dash'),
        marker=dict(size=6, symbol='circle', color='red')
    ))
    fig3.add_trace(go.Scatter(
        x=df_filtered.index, y=df_filtered['loss_pred'].cumsum(),
        mode='lines+markers', name=f'{region} Prediction Cumulative MSE',
        line=dict(color='blue', width=1, dash='dot'),
        marker=dict(size=6, symbol='diamond', color='blue')
    ))
    fig3.update_layout(
        title=f"Cumulative Squared Prediction Errors (MSE) ({start_year}-{end_year})",
        xaxis_title="Date",
        yaxis_title="Cumulative Squared Error",
        legend=dict(x=0, y=1),
        hovermode="x unified",
        template="plotly_white"
    )
    fig3.update_layout(yaxis=dict(tickformat=".2e"))  # Scientific notation with 2 decimals
    st.plotly_chart(fig3, use_container_width=True)
