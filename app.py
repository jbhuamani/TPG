import streamlit as st
import pandas as pd

@st.cache_resource
def load_data():
    # Data loading logic

# Load the updated database
@st.cache_data
def load_data():
    # Replace this URL with the Google Sheets CSV link
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-dcp7RM6MkGU32oBBR3afCt5ujMrlNeOVKtvXltvsvr7GbkqsJwHIDpu0Z73hYDwF8rDMzFbTnoc5/pub?gid=0&single=true&output=csv"
    data = pd.read_csv(url)
    return data

# Filter the database based on user selections
def filter_database(df, product_feature, entity, port_type, voltage_type, voltages):
    # Dynamically filter the dataframe based on selected values
    if product_feature != "All":
        df = df[df['PRODUCT_FEATURE'] == product_feature]
    if entity != "All":
        df = df[df['ENTITY'] == entity]
    if port_type != "All":
        df = df[df['PORT_TYPE'] == port_type]
    if voltage_type != "All":
        df = df[df['VOLTAGE_TYPE'] == voltage_type]
    if voltages != "All":
        df = df[df['VOLTAGES'] == voltages]
    return df

# Main application
def main():
    st.title("Enhanced EMC Test Plan Generator")
    st.write("Select options below to generate a test plan based on your requirements.")

    # Load the data
    df = load_data()

    # Sidebar dropdown menus
    st.sidebar.header("Filter Options")
    product_feature = st.sidebar.selectbox("Select PRODUCT_FEATURE:", ["All"] + df['PRODUCT_FEATURE'].unique().tolist())
    entity = st.sidebar.selectbox("Select ENTITY:", ["All"] + df['ENTITY'].unique().tolist())
    port_type = st.sidebar.selectbox("Select PORT_TYPE:", ["All"] + df['PORT_TYPE'].unique().tolist())
    voltage_type = st.sidebar.selectbox("Select VOLTAGE_TYPE:", ["All"] + df['VOLTAGE_TYPE'].unique().tolist())
    voltages = st.sidebar.selectbox("Select VOLTAGES:", ["All"] + df['VOLTAGES'].unique().tolist())

    # Filter data based on selections
    filtered_df = filter_database(df, product_feature, entity, port_type, voltage_type, voltages)

    # Display the results
    st.header("Generated Test Plan")
    if not filtered_df.empty:
        st.write("The following test cases match your selection:")
        st.dataframe(filtered_df)
    else:
        st.warning("No matching test cases found. Please modify your selections.")

if __name__ == "__main__":
    main()
