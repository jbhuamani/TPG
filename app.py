import streamlit as st
import pandas as pd

# Load the Google Sheet data
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-dcp7RM6MkGU32oBBR3afCt5ujMrlNeOVKtvXltvsvr7GbkqsJwHIDpu0Z73hYDwF8rDMzFbTnoc5/pub?output=csv"
    data = pd.read_csv(url)
    data['Port Type'] = data['Port Type'].apply(lambda x: x.split(", ") if isinstance(x, str) else x)
    data['Test Details'] = data['Test Details'].apply(lambda x: x.split(", ") if isinstance(x, str) else x)
    return data

# Filter the database
def filter_database(df, product_standard, port_type):
    filtered_df = df[
        (df['Test Type'] == product_standard) &
        (df['Port Type'].apply(lambda x: port_type in x if isinstance(x, list) else False))
    ]
    return filtered_df

# Main app
def main():
    st.title("EMC Test Plan Generator")

    # Load the database
    df = load_data()

    # User input
    st.sidebar.header("Filter Options")
    product_standard = st.sidebar.selectbox("Select Product Standard:", df['Test Type'].unique())
    port_type = st.sidebar.selectbox("Select Port Type:", [item for sublist in df['Port Type'] for item in sublist])

    # Filter and generate test plan
    st.header("Generated Test Plan")
    filtered_df = filter_database(df, product_standard, port_type)
    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            st.subheader(f"Test Type: {row['Test Type']}")
            st.write(f"**Port Type:** {', '.join(row['Port Type'])}")
            st.write(f"**Test Details:** {', '.join(row['Test Details'])}")
    else:
        st.warning("No matching tests found for the given criteria.")

if __name__ == "__main__":
    main()
