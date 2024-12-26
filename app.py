import streamlit as st
import pandas as pd

# Load the updated database
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-dcp7RM6MkGU32oBBR3afCt5ujMrlNeOVKtvXltvsvr7GbkqsJwHIDpu0Z73hYDwF8rDMzFbTnoc5/pub?gid=1351032631&single=true&output=csv"
    try:
        data = pd.read_csv(url)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on failure

# Filter the database based on user selections
def filter_database(df, product_feature, entity, port_type, voltage_type, voltages):
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

# Generate a summary of the test plan
def generate_summary(df):
    if df.empty:
        return "No data to summarize."
    
    summary = []
    for _, row in df.iterrows():
        criteria = row['Criteria'] if pd.notnull(row['Criteria']) else "Not Available"
        frequency = row['Frequency_[Hz]'] if pd.notnull(row['Frequency_[Hz]']) else "Not Available"
        reduction = row['Level_[%]'] if pd.notnull(row['Level_[%]']) else "Not Available"
        test_class = row['TEST_TYPE'] if pd.notnull(row['TEST_TYPE']) else "Not Available"
        summary.append(f"{frequency}Hz, {reduction}%, Criteria {criteria} ({test_class})")

    # Combine all summary points
    return "\n".join(f"{i+1}) {item}" for i, item in enumerate(summary))

# Main application
def main():
    st.title("Enhanced EMC Test Plan Generator")
    st.write("Select options below to generate a test plan based on your requirements.")

    # Load the data
    df = load_data()
    if df.empty:
        st.error("No data available. Please check your database connection.")
        return

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

        # Generate and display the summary
        st.subheader("Test Plan Summary")
        summary = generate_summary(filtered_df)
        st.text(summary)
    else:
        st.warning("No matching test cases found. Please modify your selections.")

if __name__ == "__main__":
    main()
