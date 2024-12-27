import streamlit as st
import pandas as pd
import io

# -------------------------------------------------------
# 1. Data loading (with caching)
# -------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load data from a Google Sheets CSV link and return as a DataFrame.
    """
    url = (
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-dcp7RM6MkGU32oBBR3afCt5ujMrlNeOVKtvXltvsvr7GbkqsJwHIDpu0Z73hYDwF8rDMzFbTnoc5/pub"
        "?gid=1351032631&single=true&output=csv"
    )
    try:
        data = pd.read_csv(url)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# -------------------------------------------------------
# 2. Data filtering
# -------------------------------------------------------
def filter_database(
    df: pd.DataFrame,
    product_features: list[str] = None,
    entities: list[str] = None,
    port_types: list[str] = None,
    voltage_types: list[str] = None,
    voltages: list[str] = None,
) -> pd.DataFrame:
    """
    Filter the input DataFrame based on the provided lists.
    Only apply a filter if a non-empty list of values is provided.
    """
    # Make a copy to avoid mutating the original DataFrame
    filtered_df = df.copy()

    if product_features:
        filtered_df = filtered_df[filtered_df.get('PRODUCT_FEATURE', pd.Series([])).isin(product_features)]
    if entities:
        filtered_df = filtered_df[filtered_df.get('ENTITY', pd.Series([])).isin(entities)]
    if port_types:
        filtered_df = filtered_df[filtered_df.get('PORT_TYPE', pd.Series([])).isin(port_types)]
    if voltage_types:
        filtered_df = filtered_df[filtered_df.get('VOLTAGE_TYPE', pd.Series([])).isin(voltage_types)]
    if voltages:
        filtered_df = filtered_df[filtered_df.get('VOLTAGES', pd.Series([])).isin(voltages)]

    return filtered_df

# -------------------------------------------------------
# 3. Remove empty columns
# -------------------------------------------------------
def remove_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove columns that are entirely empty (all NaN/None).
    """
    return df.dropna(how="all", axis=1)

# -------------------------------------------------------
# 4. Summary Generator
# -------------------------------------------------------
def generate_summary(filtered_df: pd.DataFrame) -> str:
    """
    Generate a summary of the test plan from the filtered DataFrame.
    Currently handles different TEST_TYPE categories (DC Ripple, AC VDI).
    This function can be extended for additional test types in the future.
    """
    if filtered_df.empty:
        return "No test plan available for the selected criteria."

    summary_lines = set()

    # Identify each test type in the filtered data.
    test_types = filtered_df.get('TEST_TYPE', pd.Series([])).unique()

    # Iterate through each unique TEST_TYPE
    for test_type in test_types:
        subset = filtered_df[filtered_df['TEST_TYPE'] == test_type]

        # --------------------------------
        #  A. DC Ripple
        # --------------------------------
        if test_type == "DC Ripple":
            for _, row in subset.iterrows():
                frequency = row.get('DCR_Freq_[Hz]', 'N/A')
                level = row.get('DCR_Level_[%]', 'N/A')
                criteria = row.get('DCR_Criteria', 'N/A')
                summary_lines.add(
                    f"DC Ripple: Frequency {frequency} Hz, Level {level}%, Criteria {criteria}"
                )

        # --------------------------------
        #  B. AC VDI
        # --------------------------------
        elif test_type == "AC VDI":
            for _, row in subset.iterrows():
                applicability = row.get('ACV_Apply', 'N/A')
                frequency = row.get('ACV_Freq_[Hz]', 'N/A')
                reduction = row.get('ACV_Red_[%]', 'N/A')
                duration_cycles = row.get('ACV_Dur_[Cycles]', None)
                duration_ms = row.get('ACV_Dur_[ms]', None)
                crossing = row.get('ACV_Cross_[deg]', 'N/A')
                criteria = row.get('ACV_Criteria', 'N/A')

                # Build a human-readable string for duration
                duration_str = []
                if pd.notnull(duration_cycles):
                    duration_str.append(f"{duration_cycles} cycles")
                if pd.notnull(duration_ms):
                    duration_str.append(f"{duration_ms} ms")
                duration_str = ", ".join(duration_str)

                summary_lines.add(
                    f"AC VDI: Applicability {applicability}, Frequency {frequency} Hz, "
                    f"Reduction {reduction}%, Duration {duration_str}, "
                    f"Crossing {crossing}°, Criteria {criteria}"
                )

        # --------------------------------
        #  C. Other TEST_TYPE
        # --------------------------------
        else:
            # This is a catch-all for other test types
            # or a place to add more specialized logic
            summary_lines.add(f"No specialized summary for TEST_TYPE: {test_type}")

    # Sort lines to ensure consistent output order
    return "\n".join(sorted(summary_lines))

# -------------------------------------------------------
# 5. Main App
# -------------------------------------------------------
def main():
    # Streamlit settings
    st.set_page_config(layout="wide", page_title="Enhanced EMC Test Plan Generator")

    st.title("Enhanced EMC Test Plan Generator")
    st.write(
        "Use the filters in the sidebar to refine which test cases appear below. "
        "Click **Submit Filters** to generate your custom test plan."
    )

    # Load data
    df = load_data()
    if df.empty:
        st.error("No data available. Please check your database connection.")
        return

    # ---------------------------------------------------
    # A. Filter form (single pass filtering)
    # ---------------------------------------------------
    st.sidebar.header("Filter Options")
    with st.sidebar.form(key="filter_form"):
        product_features = st.multiselect(
            "Select PRODUCT_FEATURE:",
            sorted(df['PRODUCT_FEATURE'].dropna().unique().tolist())
        )
        entities = st.multiselect(
            "Select ENTITY:",
            sorted(df['ENTITY'].dropna().unique().tolist())
        )
        port_types = st.multiselect(
            "Select PORT_TYPE:",
            sorted(df['PORT_TYPE'].dropna().unique().tolist())
        )
        voltage_types = st.multiselect(
            "Select VOLTAGE_TYPE:",
            sorted(df['VOLTAGE_TYPE'].dropna().unique().tolist())
        )
        voltages = st.multiselect(
            "Select VOLTAGES:",
            sorted(df['VOLTAGES'].dropna().unique().tolist())
        )

        # Submit button
        submit_button = st.form_submit_button(label="Submit Filters")

    # Only filter data when form is submitted
    if submit_button:
        # Apply all filters at once
        filtered_df = filter_database(
            df,
            product_features=product_features,
            entities=entities,
            port_types=port_types,
            voltage_types=voltage_types,
            voltages=voltages
        )

        # Remove empty columns
        filtered_df = remove_empty_columns(filtered_df)

        # Show results in the main panel
        st.header("Generated Test Plan")
        if not filtered_df.empty:
            st.success(f"Found {len(filtered_df)} matching rows.")
            st.dataframe(filtered_df, use_container_width=True)

            # ------------------------------------------------
            # Test Plan Summary
            # ------------------------------------------------
            st.subheader("Test Plan Summary")
            summary_text = generate_summary(filtered_df)
            st.text(summary_text)

            # ------------------------------------------------
            # Download button
            # ------------------------------------------------
            csv_buffer = io.StringIO()
            filtered_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download Filtered Data as CSV",
                data=csv_buffer.getvalue(),
                file_name="filtered_test_plan.csv",
                mime="text/csv",
            )
        else:
            st.warning("No matching test cases found. Please modify your selections.")
    else:
        # Instructions if filters haven't been submitted yet
        st.info("Select filters in the sidebar and click **Submit Filters** to generate a test plan.")

# -------------------------------------------------------
# Entry point
# -------------------------------------------------------
if __name__ == "__main__":
    main()
