import streamlit as st
import pandas as pd

# Load the updated database
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-dcp7RM6MkGU32oBBR3afCt5ujMrlNeOVKtvXltvsvr7GbkqsJwHIDpu0Z73hYDwF8rDMzFbTnoc5/pub?gid=0&single=true&output=csv"
    try:
        data = pd.read_csv(url)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Remove redundant lines and identify justifiable test cases
def process_test_cases(df):
    unique_cases = []
    justifiable_cases = []

    # Group by all columns except Criteria to detect redundancy
    grouped = df.groupby(['Applicability', 'Frequency_[Hz]', 'Reduction_[%]', 'Duration_[Cycles]', 
                          'Duration_[ms]', 'Crossing_[deg]', 'Criteria'])

    # Create a mapping of stricter to less strict criteria
    criteria_hierarchy = {'A': 1, 'B': 2, 'C': 3}  # Lower values are stricter

    # Process each group
    for _, group in grouped:
        strictest_case = None
        for _, row in group.iterrows():
            if strictest_case is None or criteria_hierarchy[row['Criteria']] < criteria_hierarchy[strictest_case['Criteria']]:
                if strictest_case is not None:
                    justifiable_cases.append(strictest_case)
                strictest_case = row
            else:
                justifiable_cases.append(row)
        unique_cases.append(strictest_case)

    unique_df = pd.DataFrame(unique_cases)
    justifiable_df = pd.DataFrame(justifiable_cases)
    return unique_df, justifiable_df

# Generate a formatted summary for display
def generate_summary(df, title):
    summary = f"### {title}\n"
    for i, row in df.iterrows():
        summary += (f"{i + 1}) AC VDI: Applicability {row['Applicability']}, Frequency {row['Frequency_[Hz]']} Hz, "
                    f"Reduction {row['Reduction_[%]']}%, Duration {row['Duration_[Cycles]']} cycles, "
                    f"{row['Duration_[ms]'] if pd.notnull(row['Duration_[ms]']) else '-'} ms, "
                    f"Crossing {row['Crossing_[deg]']} degrees, Criteria {row['Criteria']}\n")
    return summary

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
    product_feature = st.sidebar.multiselect("Select PRODUCT_FEATURE:", options=df['PRODUCT_FEATURE'].unique())
    entity = st.sidebar.multiselect("Select ENTITY:", options=df['ENTITY'].unique())
    port_type = st.sidebar.multiselect("Select PORT_TYPE:", options=df['PORT_TYPE'].unique())
    voltage_type = st.sidebar.multiselect("Select VOLTAGE_TYPE:", options=df['VOLTAGE_TYPE'].unique())
    voltages = st.sidebar.multiselect("Select VOLTAGES:", options=df['VOLTAGES'].unique())

    # Filter data
    filtered_df = df
    if product_feature:
        filtered_df = filtered_df[filtered_df['PRODUCT_FEATURE'].isin(product_feature)]
    if entity:
        filtered_df = filtered_df[filtered_df['ENTITY'].isin(entity)]
    if port_type:
        filtered_df = filtered_df[filtered_df['PORT_TYPE'].isin(port_type)]
    if voltage_type:
        filtered_df = filtered_df[filtered_df['VOLTAGE_TYPE'].isin(voltage_type)]
    if voltages:
        filtered_df = filtered_df[filtered_df['VOLTAGES'].isin(voltages)]

    # Display filtered data
    st.header("Generated Test Plan")
    if not filtered_df.empty:
        st.dataframe(filtered_df)
        
        # Process test cases
        unique_cases, justifiable_cases = process_test_cases(filtered_df)

        # Generate summaries
        summary = generate_summary(unique_cases, "Test Plan Summary")
        justifiable_summary = generate_summary(justifiable_cases, "Justifiable")

        # Display summaries
        st.markdown(summary)
        if not justifiable_cases.empty:
            st.markdown(justifiable_summary)
    else:
        st.warning("No matching test cases found. Please modify your selections.")

if __name__ == "__main__":
    main()
