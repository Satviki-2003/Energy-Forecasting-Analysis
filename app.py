import streamlit as st
import pandas as pd
from utils import create_advanced_features
import pickle


# loading the model
@st.cache_resource
def load_model():
    with open('model/model.pkl','rb') as file:
        model=pickle.load(file)
        return model

st.title("⚡ PJMW Regional Grid: Predictive Load Forecasting Dashboard")
st.info("**System Overview:** Interactive SARIMAX dashboard forecasting true out-of-sample energy demand for the PJM Western Region (PJMW) grid. The pipeline automatically engineers holiday and weekend features to capture complex consumption cycles.")

with st.sidebar:
    horizon_days=st.slider("Predict for next days:",1,30)

# Last timestamp
last_timestamp=pd.Timestamp("2018-08-03 00:00:00")

# Starting timstamp of predictions
new_start_timestamp=last_timestamp+pd.Timedelta(hours=1)

#  Total hours
total_hrs=24*horizon_days

# Future index
future_index=pd.date_range(new_start_timestamp,periods=total_hrs,freq='h')

# Creating features
features_df=create_advanced_features(future_index)

# Loading model
sarimax_model=load_model()

# predicting
predictions=sarimax_model.forecast(steps=len(future_index),exog=features_df)

# KPI cards
st.write("### 📊 Summary")

# creating three cols side by side
col1,col2,col3=st.columns([1,1,1])

with col1:
    with st.container(border=True):
        st.markdown("<hr style='margin: 0px 0px 10px 0px; border: 2px solid #FF4B4B;'>", unsafe_allow_html=True)
        max_val=round(predictions.max(),2)
        max_date=predictions.idxmax()
        st.metric(
            label="⚡ Peak Demand (Max)", 
            value=f"{max_val} MW", 
            help=f"Highest projected load expected on {max_date}"
        )

with col2:
    with st.container(border=True):
        st.markdown("<hr style='margin: 0px 0px 10px 0px; border: 2px solid #FF4B4B;'>", unsafe_allow_html=True)
        min_val=round(predictions.min(),2)
        min_date=predictions.idxmin()
        st.metric(
            label="📉 Baseline Demand (Min)",
            value=f"{min_val} MW", 
            help=f"Least projected load expected on {min_date}"
        )

with col3:
    with st.container(border=True):
        st.markdown("<hr style='margin: 0px 0px 10px 0px; border: 2px solid #FF4B4B;'>", unsafe_allow_html=True)
        total=round(predictions.sum(),0)
        st.metric(
            label="🔋 Total Volume Forecasted",
            value=f"{round(total/1000)} GWh", 
            help="Cumulative energy consumption across the full selected horizon"
    )
        
# Interactive prediction graph
st.write("### 📈 Predicted Load Profile Timeline")
predictions_df=pd.DataFrame(predictions).rename(columns={'predicted_mean':'Predicted Load (MW)'})
# Render the high-contrast line chart
st.line_chart(predictions_df, y="Predicted Load (MW)", width='stretch')

# Expandable data table
with st.expander("📋 View Complete Hourly Forecast Data Table"):
    # Naming index
    predictions_df.index.name='Timestamp'
    # displaying Df
    st.dataframe(predictions_df,width='stretch')
    # Df to csv
    csv_file=predictions_df.to_csv().encode('utf-8')
    # Download button
    st.download_button(
        label="📥 Download Forecast as CSV",
        data=csv_file,
        file_name="pjm_load_forecast.csv",
        mime='text/csv',
        width='stretch'
    )
