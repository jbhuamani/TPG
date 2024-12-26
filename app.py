import streamlit as st
import pandas as pd

# Load the Google Sheet data
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-dcp7RM6MkGU32oBBR3afCt5ujMrlNeOVKtvXltvsvr7GbkqsJwHIDpu0Z73hYDwF8rDMzFbTnoc5/pub?gid=0&single=true&output=csv"
    data = pd.read_csv(url)
    # Ensure that multi-entry columns are split into lists
    for col in ['PORT_TYPE', 'VOLTAGES']:
        data[col] = data[col].apply(lambda x: x.split(", ") if isinstance(x, str) else x)
    return data

# Filter the database based on user selections
def filter_database(df, product_feature, entity, port_type, voltage_type, voltages):
    filtered_df = df[
        (df['PRODUCT_FEATURE'] == product_feature) &
        (df['ENTITY'] == entity) &
        (df['PORT_TYPE'].apply(lambda x: port_type in x if isinstance(x, list) else False)) &
        (df['VOLTAGE_TYPE'] == voltage_type) &
        (df['VOLTAGES'].apply(lambda x: voltages in x if isinstance(x, list) else False))
    ]
    return filtered_df

# Main app
def main():
    st.title("EMC Test Plan Generator")

    # Load the database
    df = load_data()

    # User input
    st.sidebar.header("Filter Options")
    product_feature = st.sidebar.selectbox("Select Product Feature:", df['PRODUCT_FEATURE'].unique())
    entity = st.sidebar.selectbox("Select Entity:", df['ENTITY'].unique())
    port_type = st.sidebar.selectbox("Select Port Type:", [item for sublist in df['PORT_TYPE'] for item in sublist])
    voltage_type = st.sidebar.selectbox("Select Voltage Type:", df['VOLTAGE_TYPE'].unique())
    voltages = st.sidebar.selectbox("Select Voltages:", [item for sublist in df['VOLTAGES'] for item in sublist])

    # Filter and generate test plan
    st.header("Generated Test Plan")
    filtered_df = filter_database(df, product_feature, entity, port_type, voltage_type, voltages)
    if not filtered_df.empty:
        st.dataframe(filtered_df)
    else:
        st.warning("No matching tests found for the given criteria.")

if __name__ == "__main__":
    main()
