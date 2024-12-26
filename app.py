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
        return pd.DataFrame()

# Filter the database based on user selections
def filter_database(df, product_features=None, entities=None, port_types=None, voltage_types=None, voltages=None):
    if product_features and "All" not in product_features:
        df = df[df['PRODUCT_FEATURE'].isin(product_features)]
    if entities and "All" not in entities:
        df = df[df['ENTITY'].isin(entities)]
    if port_types and "All" not in port_types:
        df = df[df['PORT_TYPE'].isin(port_types)]
    if voltage_types and "All" not in voltage_types:
        df = df[df['VOLTAGE_TYPE'].isin(voltage_types)]
    if voltages and "All" not in voltages:
        df = df[df['VOLTAGES'].isin(voltages)]
    return df

# Remove empty columns
def remove_empty_columns(df):
    return df.dropna(how="all", axis=1)

# Generate a formatted summary of the test plan
def generate_summary(df):
    if df.empty:
        return "No data to summarize."

    summary_set = set()
    for _, row in df.iterrows():
        test_type = row.get('TEST_TYPE', "Not Available")
        if test_type == "DC Ripple":
            frequency = row.get('DCR_Freq_[Hz]', "Not Available")
            level = row.get('DCR_Level_[%]', "Not Available")
            criteria = row.get('DCR_Criteria', "Not Available")
            line = f"{test_type}: Frequency {frequency} Hz, Level {level}%, Criteria {criteria}"
        elif test_type == "AC VDI":
            applicability = row.get('ACV_Apply', "Not Available")
            frequency = row.get('ACV_Freq_[Hz]', "Not Available")
            reduction = row.get('ACV_Red_[%]', "Not Available")
            crossing = row.get('ACV_Cross_[deg]', "Not Available")
            criteria = row.get('ACV_Criteria', "Not Available")

            # Handle Duration values
            duration_cycles = row.get('ACV_Dur_[Cycles]')
            duration_ms = row.get('ACV_Dur_[ms]')

            if pd.notnull(duration_cycles) and pd.notnull(duration_ms):
                duration = f"Duration {duration_cycles} cycles, {duration_ms} ms"
            elif pd.notnull(duration_ms):
                duration = f"Duration {duration_ms} ms"
            elif pd.notnull(duration_cycles):
                duration = f"Duration {duration_cycles} cycles"
            else:
                duration = "Duration Not Available"

            line = (
                f"{test_type}: Applicability {applicability}, Frequency {frequency} Hz, Reduction {reduction}%, "
                f"{duration}, Crossing {crossing} degrees, Criteria {criteria}"
            )
        else:
            line = f"{test_type}: No data available for summary."
        summary_set.add(line)

    unique_summary = sorted(list(summary_set))
    return "\n".join(f"{i+1}) {item}" for i, item in enumerate(unique_summary))

# Main application
def main():
    st.set_page_config(layout="wide")  # Utilize the full screen width
    st.title("Enhanced EMC Test Plan Generator")
    st.write("Select options below to generate a test plan based on your requirements.")

    # Add custom CSS for styling
    st.markdown(
        """
        <style>
        .css-18e3th9 {
            padding: 1rem 1rem 1rem 1rem;  /* Reduce padding for the sidebar */
        }
        .css-1d391kg {
            padding: 1rem 1rem 1rem 1rem;  /* Reduce padding for the main content */
        }
        .block-container {
            padding: 1rem 3rem;  /* Adjust overall padding */
            max-width: 95%;  /* Increase the content width */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Load the data
    df = load_data()
    if df.empty:
        st.error("No data available. Please check your database connection.")
        return

    # Sidebar multi-select menus
    st.sidebar.header("Filter Options")
    product_features = st.sidebar.multiselect("Select PRODUCT_FEATURE:", ["All"] + df['PRODUCT_FEATURE'].unique().tolist(), default="All")
    filtered_df = filter_database(df, product_features=product_features)

    entities = st.sidebar.multiselect("Select ENTITY:", ["All"] + filtered_df['ENTITY'].unique().tolist(), default="All")
    filtered_df = filter_database(filtered_df, entities=entities)

    port_types = st.sidebar.multiselect("Select PORT_TYPE:", ["All"] + filtered_df['PORT_TYPE'].unique().tolist(), default="All")
    filtered_df = filter_database(filtered_df, port_types=port_types)

    voltage_types = st.sidebar.multiselect("Select VOLTAGE_TYPE:", ["All"] + filtered_df['VOLTAGE_TYPE'].unique().tolist(), default="All")
    filtered_df = filter_database(filtered_df, voltage_types=voltage_types)

    voltages = st.sidebar.multiselect("Select VOLTAGES:", ["All"] + filtered_df['VOLTAGES'].unique().tolist(), default="All")
    filtered_df = filter_database(filtered_df, voltages=voltages)

    # Remove empty columns
    filtered_df = remove_empty_columns(filtered_df)

    # Display the results
    st.header("Generated Test Plan")
    if not filtered_df.empty:
        st.write("The following test cases match your selection:")
        st.dataframe(filtered_df, use_container_width=True)  # Table utilizes full width

        # Generate and display the summary
        st.subheader("Test Plan Summary")
        summary = generate_summary(filtered_df)
        st.text(summary)
    else:
        st.warning("No matching test cases found. Please modify your selections.")

if __name__ == "__main__":
    main()
