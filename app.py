import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# User selects the region
region = st.radio("Select Region:", ["US (Core PCE)", "Europe (HICP)", "Europe (Unemployment)"])

# Load the data based on user selection
if region == "US (Core PCE)":
    file_path = os.path.join(os.getcwd(), "PCEPILFE_Economics_optimized.xlsx")
    try:
        df0 = pd.read_excel(file_path, engine="openpyxl", index_col=0, parse_dates=True)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        st.stop()
    pred_col = 'pred_swap'
    target_var = 'inflation'
elif region == "Europe (HICP)":
    file_path = os.path.join(os.getcwd(), "HICP_europe_optimized.xlsx")
    try:
        df0 = pd.read_excel(file_path, engine="openpyxl", index_col=0, parse_dates=True)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        st.stop()
    pred_col = 'pred_ar'
    target_var = 'inflation'

else:
    file_path = os.path.join(os.getcwd(), "Unemployment_europe_optimized.xlsx")
    try:
        df0 = pd.read_excel(file_path, engine="openpyxl", index_col=0, parse_dates=True)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        st.stop()
    pred_col = 'pred_ar'
    target_var = 'Unemployment'


# Upload the uncertainty file
if region == "US (Core PCE)":
    file_path_unc = os.path.join(os.getcwd(), "collection_results.csv")                                         
elif region == "Europe (HICP)":
    file_path_unc = os.path.join(os.getcwd(), "HICP_collection_results.csv")   
else:
    file_path_unc = os.path.join(os.getcwd(), "Unemployment_collection_results.csv")
    
df_uncertainty = pd.read_csv(file_path_unc)

mean_value = df_uncertainty["Value"].mean()
std_dev = df_uncertainty["Value"].std()
conf_int_68 = 1.0 * std_dev  # Approximate for normal distribution





####################################################################
#############Define parameters for plot#############################
####################################################################
h_step = 1
# Shift index by h_step months
df0_shifted = df0.copy()
if region == "US (Core PCE)":
    df0_shifted.index = df0_shifted.index - pd.DateOffset(months=h_step)

# User selects the year range
min_year = 2019
max_year = 2026
start_year, end_year = st.slider(
    "Select the year range:",
    min_value=min_year, max_value=max_year,
    value=(2024, 2026), step=1
)

df_filtered = df0_shifted.loc[str(start_year):str(end_year)]

# Display the last available annual inflation rate and the Llama prediction
df_display = df0.copy()
if region == "US (Core PCE)":
    df_display.index = df_display.index - pd.DateOffset(months=h_step)
elif region == "Europe (HICP)":
    df_display.index = df_display.index + pd.DateOffset(months=h_step)



last_inflation_index = df_display[target_var].last_valid_index()
last_llama_index = df_display['pred_signal_llama_70b'].last_valid_index()
if region == 'Europe (Unemployment)':
    last_inflation_value = df_display.loc[last_inflation_index, target_var] if last_inflation_index else None
    last_llama_value = df_display.loc[last_llama_index, 'pred_signal_llama_70b'] if last_inflation_index else None
else:
    last_inflation_value = df_display.loc[last_inflation_index, target_var]*100 if last_inflation_index else None
    last_llama_value = df_display.loc[last_llama_index, 'pred_signal_llama_70b']*100 if last_inflation_index else None



# Find last and second last available data points for 'pred_signal_llama_70b'
valid_indices = df_filtered['pred_signal_llama_70b'].dropna().index
if len(valid_indices) >= 2:
    last_valid_index = valid_indices[-1]
    second_last_valid_index = valid_indices[-2]
    last_valid_value = df_filtered.loc[last_valid_index, 'pred_signal_llama_70b']
    second_last_valid_value = df_filtered.loc[second_last_valid_index, 'pred_signal_llama_70b']
    lower_bound_last = last_valid_value - conf_int_68
    upper_bound_last = last_valid_value + conf_int_68
    lower_bound_second_last = second_last_valid_value
    upper_bound_second_last = second_last_valid_value
else:
    last_valid_index = None
    second_last_valid_index = None
    lower_bound_last = None
    upper_bound_last = None
    lower_bound_second_last = None
    upper_bound_second_last = None


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
    mode='lines+markers', name=f'Benchmark model',
    line=dict(color='blue', width=1, dash='dot'),
    marker=dict(size=6, symbol='diamond', color='blue')
))

# Add confidence intervals for last and second last predictions
if last_valid_index is not None and lower_bound_last is not None and upper_bound_last is not None:
    fig.add_trace(go.Scatter(
        x=[second_last_valid_index, last_valid_index, last_valid_index, second_last_valid_index],
        y=[lower_bound_second_last, lower_bound_last, upper_bound_last, upper_bound_second_last],
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.3)',
        mode='none',
        name='68% Confidence Interval'
    ))

# Customize layout
if region == 'Europe (Unemployment)':
    fig.update_layout(
        title=f"Unemployment Predictions vs. True Values ({region})",
        xaxis_title="Date",
        yaxis_title="Unemployment Rate",
        legend=dict(x=0, y=1),
        hovermode="x unified",
        template="plotly_white"
    )
else:
    fig.update_layout(
        title=f"Inflation Predictions vs. True Values ({region})",
        xaxis_title="Date",
        yaxis_title="Inflation Rate",
        legend=dict(x=0, y=1),
        hovermode="x unified",
        template="plotly_white"
    )





####################################################################
#############Streamlit app (main part)##############################
####################################################################
st.title(f"📈 Real-time Nowcast: {region}")
st.markdown('Views are my own and do not necessarily represent the ones of European Commission')
if region == 'Europe (Unemployment)':
    st.markdown(
        f"""
        ### 📊 Latest Inflation Data
        - **Last available annual unemployment rate:** {last_inflation_value:.4f}% (Month: {last_inflation_index.strftime('%B%Y')})
        - **Llama 70B Model Prediction:** {last_llama_value:.4f}% (next month)        
        """
    )
else:
    st.markdown(
        f"""
        ### 📊 Latest Inflation Data
        - **Last available annual inflation rate:** {last_inflation_value:.4f}% (Month: {last_inflation_index.strftime('%B%Y')})
        - **Llama 70B Model Prediction:** {last_llama_value:.4f}% (next month)     
        """
    )
    

st.write('For the US the benchmark (blue) is a prediction using the Inflation-SWAP, for Europe is an AR(1).') 
st.plotly_chart(fig, use_container_width=True)



####################################################################
#############Streamlit app (error plot)#############################
####################################################################
show_loss_plot = st.checkbox("Show Prediction Error (MAE)")
if show_loss_plot:
    st.write(f'Mean absolute deviation from the {target_var}, over time.')
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
        mode='lines+markers', name=f'Benchmark model Error',
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
        mode='lines+markers', name=f'Benchamrk model Cumulative MSE',
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
