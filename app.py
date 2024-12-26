import streamlit as st
import pandas as pd

# Load the updated database
@st.cache_data
def load_data():
    # Updated URL for the Google Sheet
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-dcp7RM6MkGU32oBBR3afCt5ujMrlNeOVKtvXltvsvr7GbkqsJwHIDpu0Z73hYDwF8rDMzFbTnoc5/pub?gid=1351032631&single=true&output=csv"
    try:
        data = pd.read_csv(url)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on failure

# Filter the database based on user selections
def filter_database(df, product_feature=None, entity=None, port_type=None, voltage_type=None, voltages=None):
    if product_feature and product_feature != "All":
        df = df[df['PRODUCT_FEATURE'] == product_feature]
    if entity and entity != "All":
        df = df[df['ENTITY'] == entity]
    if port_type and port_type != "All":
        df = df[df['PORT_TYPE'] == port_type]
    if voltage_type and voltage_type != "All":
        df = df[df['VOLTAGE_TYPE'] == voltage_type]
    if voltages and voltages != "All":
        df = df[df['VOLTAGES'] == voltages]
    return df

# Generate a summary of the test plan
def generate_summary(df):
    if df.empty:
        return "No data to summarize."
    
    summary_set = set()  # Use a set to ensure uniqueness
    for _, row in df.iterrows():
        criteria = row['Criteria'] if pd.notnull(row['Criteria']) else "Not Available"
        frequency = row['Frequency_[Hz]'] if pd.notnull(row['Frequency_[Hz]']) else "Not Available"
        reduction = row['Level_[%]'] if pd.notnull(row['Level_[%]']) else "Not Available"
        test_class = row['TEST_TYPE'] if pd.notnull(row['TEST_TYPE']) else "Not Available"
        line = f"{frequency}Hz, {reduction}%, Criteria {criteria} ({test_class})"
        summary_set.add(line)  # Add each unique line to the set

    # Combine all unique summary points
    unique_summary = sorted(list(summary_set))  # Sort for consistent order
    return "\n".join(f"{i+1}) {item}" for i, item in enumerate(unique_summary))

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
    filtered_df = filter_database(df, product_feature=product_feature)

    entity = st.sidebar.selectbox("Select ENTITY:", ["All"] + filtered_df['ENTITY'].unique().tolist())
    filtered_df = filter_database(filtered_df, entity=entity)

    port_type = st.sidebar.selectbox("Select PORT_TYPE:", ["All"] + filtered_df['PORT_TYPE'].unique().tolist())
    filtered_df = filter_database(filtered_df, port_type=port_type)

    voltage_type = st.sidebar.selectbox("Select VOLTAGE_TYPE:", ["All"] + filtered_df['VOLTAGE_TYPE'].unique().tolist())
    filtered_df = filter_database(filtered_df, voltage_type=voltage_type)

    voltages = st.sidebar.selectbox(
        "Select VOLTAGES:", 
        ["All"] + filtered_df['VOLTAGES'].unique().tolist(), 
        format_func=lambda x: x if x == "All" or x in filtered_df['VOLTAGES'].unique() else f"{x} (Unavailable)"
    )
    if voltages.endswith("(Unavailable)"):
        st.sidebar.warning("Selected value is unavailable in the filtered table.")
    else:
        filtered_df = filter_database(filtered_df, voltages=voltages)

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
