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

# Automatically deselect "All" when another option is selected
def auto_deselect(selection):
    """Ensure 'All' is deselected if any other item is selected."""
    if "All" in selection and len(selection) > 1:
        selection.remove("All")
    return selection

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

# Main application
def main():
    st.set_page_config(layout="wide")
    st.title("Enhanced EMC Test Plan Generator")
    st.write("Select options below to generate a test plan based on your requirements.")

    # Load the data
    df = load_data()
    if df.empty:
        st.error("No data available. Please check your database connection.")
        return

    # Sidebar multi-select menus with "All" auto-deselect logic
    st.sidebar.header("Filter Options")

    product_features = st.sidebar.multiselect(
        "Select PRODUCT_FEATURE:",
        ["All"] + df['PRODUCT_FEATURE'].unique().tolist(),
        default=["All"]
    )
    product_features = auto_deselect(product_features)
    filtered_df = filter_database(df, product_features=product_features)

    entities = st.sidebar.multiselect(
        "Select ENTITY:",
        ["All"] + filtered_df['ENTITY'].unique().tolist(),
        default=["All"]
    )
    entities = auto_deselect(entities)
    filtered_df = filter_database(filtered_df, entities=entities)

    port_types = st.sidebar.multiselect(
        "Select PORT_TYPE:",
        ["All"] + filtered_df['PORT_TYPE'].unique().tolist(),
        default=["All"]
    )
    port_types = auto_deselect(port_types)
    filtered_df = filter_database(filtered_df, port_types=port_types)

    voltage_types = st.sidebar.multiselect(
        "Select VOLTAGE_TYPE:",
        ["All"] + filtered_df['VOLTAGE_TYPE'].unique().tolist(),
        default=["All"]
    )
    voltage_types = auto_deselect(voltage_types)
    filtered_df = filter_database(filtered_df, voltage_types=voltage_types)

    voltages = st.sidebar.multiselect(
        "Select VOLTAGES:",
        ["All"] + filtered_df['VOLTAGES'].unique().tolist(),
        default=["All"]
    )
    voltages = auto_deselect(voltages)
    filtered_df = filter_database(filtered_df, voltages=voltages)

    # Remove empty columns
    filtered_df = remove_empty_columns(filtered_df)

    # Display the results
    st.header("Generated Test Plan")
    if not filtered_df.empty:
        st.write("The following test cases match your selection:")
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("No matching test cases found. Please modify your selections.")

if __name__ == "__main__":
    main()
