import streamlit as st
import pandas as pd

# Load the updated database
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/your_google_sheet_id/export?format=csv"
    data = pd.read_csv(url)
    return data

# Filter the database based on user selections
def filter_database(df, product_feature, entity, port_type, voltage_type, voltages):
    filtered_df = df[
        (df['PRODUCT_FEATURE'] == product_feature) &
        (df['ENTITY'] == entity) &
        (df['PORT_TYPE'] == port_type) &
        (df['VOLTAGE_TYPE'] == voltage_type) &
        (df['VOLTAGES'] == voltages)
    ]
    return filtered_df

# Main app
def main():
    st.title("Enhanced EMC Test Plan Generator")

    # Load the database
    df = load_data()

    # Sidebar dropdown menus
    st.sidebar.header("Filter Options")
    product_feature = st.sidebar.selectbox("Select PRODUCT_FEATURE:", df['PRODUCT_FEATURE'].unique())
    entity = st.sidebar.selectbox("Select ENTITY:", df['ENTITY'].unique())
    port_type = st.sidebar.selectbox("Select PORT_TYPE:", df['PORT_TYPE'].unique())
    voltage_type = st.sidebar.selectbox("Select VOLTAGE_TYPE:", df['VOLTAGE_TYPE'].unique())
    voltages = st.sidebar.selectbox("Select VOLTAGES:", df['VOLTAGES'].unique())

    # Filter the database
    st.header("Filtered Test Plan Data")
    filtered_df = filter_database(df, product_feature, entity, port_type, voltage_type, voltages)

    if not filtered_df.empty:
        st.dataframe(filtered_df)
    else:
        st.warning("No matching data found for the selected criteria.")

if __name__ == "__main__":
    main()
