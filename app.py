import streamlit as st
import pandas as pd

# 1) IMPORT AGGRID LIBRARIES
from st_aggrid import AgGrid, GridOptionsBuilder

@st.cache_data
def load_data():
    """
    Loads the updated database from a public Google Sheets link.
    """
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-dcp7RM6MkGU32oBBR3afCt5ujMrlNeOVKtvXltvsvr7GbkqsJwHIDpu0Z73hYDwF8rDMzFbTnoc5/pub?gid=1351032631&single=true&output=csv"
    try:
        data = pd.read_csv(url)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def filter_database(
    df: pd.DataFrame,
    product_features=None,
    entities=None,
    port_types=None,
    voltage_types=None,
    voltages=None
) -> pd.DataFrame:
    """
    Filters the DataFrame based on the provided criteria.
    """
    if product_features:
        df = df[df['PRODUCT_FEATURE'].isin(product_features)]
    if entities:
        df = df[df['ENTITY'].isin(entities)]
    if port_types:
        df = df[df['PORT_TYPE'].isin(port_types)]
    if voltage_types:
        df = df[df['VOLTAGE_TYPE'].isin(voltage_types)]
    if voltages:
        df = df[df['VOLTAGES'].isin(voltages)]
    return df

def generate_summary(filtered_df: pd.DataFrame) -> str:
    """
    Creates a structured, more readable summary of the test plan
    by grouping rows with similar parameters and avoiding redundant lines.
    """
    if filtered_df.empty:
        return "No test plan available for the selected criteria."

    output_lines = []

    # --- DC Ripple Section ---
    dc_ripple_df = filtered_df[filtered_df['TEST_TYPE'] == "DC Ripple"]
    if not dc_ripple_df.empty:
        output_lines.append("### DC Ripple Tests")
        # Group DC Ripple by (Frequency, Level) so repeated lines get condensed
        grouped_dc = dc_ripple_df.groupby(["DCR_Freq_[Hz]", "DCR_Level_[%]"], dropna=False)
        for (freq, level), group_df in grouped_dc:
            all_criteria = sorted(group_df["DCR_Criteria"].dropna().unique())
            criteria_str = ", ".join(all_criteria) if all_criteria else "TBD"
            output_lines.append(f"- Frequency: {freq} Hz, Level: {level}%, Criteria: {criteria_str}")
        output_lines.append("")  # Blank line separator

    # --- AC VDI Section ---
    ac_vdi_df = filtered_df[filtered_df['TEST_TYPE'] == "AC VDI"]
    if not ac_vdi_df.empty:
        output_lines.append("### AC VDI Tests")
        # Group AC VDI by (Applicability, Frequency, Crossing)
        grouped_ac_vdi = ac_vdi_df.groupby(["ACV_Apply", "ACV_Freq_[Hz]", "ACV_Cross_[deg]"], dropna=False)

        for (applicability, freq, crossing), group_df in grouped_ac_vdi:
            # Header line for this combination
            output_lines.append(
                f"- **Applicability**: {applicability}, **Frequency**: {freq} Hz, **Crossing**: {crossing}°"
            )

            # Within each group, further group by (Reduction, Duration cycles, Duration ms)
            sub_group = group_df.groupby(["ACV_Red_[%]", "ACV_Dur_[Cycles]", "ACV_Dur_[ms]"], dropna=False)
            for (reduction, dur_cycles, dur_ms), row_df in sub_group:
                # Collect unique criteria in this sub-group
                all_criteria = sorted(row_df["ACV_Criteria"].dropna().unique())
                criteria_str = ", ".join(all_criteria) if all_criteria else "TBD"

                # Safely build a duration string (avoid ValueError for non-integer)
                duration_parts = []

                # Handle cycles
                if pd.notnull(dur_cycles):
                    try:
                        val_float = float(dur_cycles)
                        if val_float.is_integer():
                            duration_parts.append(f"{int(val_float)} cycles")
                        else:
                            duration_parts.append(f"{val_float} cycles")
                    except ValueError:
                        duration_parts.append(f"{dur_cycles} cycles")

                # Handle milliseconds
                if pd.notnull(dur_ms):
                    try:
                        val_float = float(dur_ms)
                        if val_float.is_integer():
                            duration_parts.append(f"{int(val_float)} ms")
                        else:
                            duration_parts.append(f"{val_float} ms")
                    except ValueError:
                        duration_parts.append(f"{dur_ms} ms")

                # If no valid duration was found
                if not duration_parts:
                    duration_parts = ["-"]

                duration_str = ", ".join(duration_parts)

                # Sub-bullet for each reduction entry
                output_lines.append(
                    f"   - **Reduction**: {reduction}%, **Duration**: {duration_str}, **Criteria**: {criteria_str}"
                )

            output_lines.append("")  # Extra blank line after each group

    # Combine everything into a single string
    final_summary = "\n".join(output_lines).strip()
    return final_summary if final_summary else "No test plan available for the selected criteria."

def remove_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes columns that are entirely empty (NaN).
    """
    return df.dropna(how="all", axis=1)

def main():
    st.set_page_config(layout="wide")
    st.title("Enhanced EMC Test Plan Generator")
    st.write("Select options in the sidebar to generate a test plan based on your requirements.")

    # Load the data
    df = load_data()
    if df.empty:
        st.error("No data available. Please check your database connection.")
        return

    # Sidebar multi-select menus
    st.sidebar.header("Filter Options")
    product_features = st.sidebar.multiselect(
        "Select PRODUCT_FEATURE:",
        df['PRODUCT_FEATURE'].dropna().unique().tolist()
    )
    entities = st.sidebar.multiselect(
        "Select ENTITY:",
        df['ENTITY'].dropna().unique().tolist()
    )
    port_types = st.sidebar.multiselect(
        "Select PORT_TYPE:",
        df['PORT_TYPE'].dropna().unique().tolist()
    )
    voltage_types = st.sidebar.multiselect(
        "Select VOLTAGE_TYPE:",
        df['VOLTAGE_TYPE'].dropna().unique().tolist()
    )
    voltages = st.sidebar.multiselect(
        "Select VOLTAGES:",
        df['VOLTAGES'].dropna().unique().tolist()
    )

    # Filter data once after all selections
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

    # Make a copy for display and set up 1-based indexing
    df_display = filtered_df.copy()
    df_display.reset_index(drop=True, inplace=True)
    df_display.index = df_display.index + 1
    df_display.index.name = "No."

    # -------------------------------
    #    DISPLAY WITH ST-AGGRID
    # -------------------------------
    st.header("Generated Test Plan")
    if not df_display.empty:
        st.write("Below are the test cases matching your selection:")

        # 2) BUILD THE GRID OPTIONS WITH PER-COLUMN FILTERS
        gb = GridOptionsBuilder.from_dataframe(df_display)
        # Turn on filters, sorting, etc.
        gb.configure_default_column(filter=True, sortable=True, resizable=True)
        # Build final grid options
        gridOptions = gb.build()

        # 3) RENDER THE AGGRID TABLE
        AgGrid(
            df_display,
            gridOptions=gridOptions,
            theme="streamlit",  # Other themes: "light", "dark", "blue", "material"
            enable_enterprise_modules=False,  # Set True if you have a license or want enterprise features
            allow_unsafe_jscode=True,         # For potential advanced customizations
            reload_data=True
        )

        # Generate and display the test plan summary
        st.subheader("Organized Test Plan Summary")
        summary = generate_summary(df_display)
        st.markdown(summary)
    else:
        st.warning("No matching test cases found. Please modify your selections.")

if __name__ == "__main__":
    main()
