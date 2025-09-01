import streamlit as st
import pandas as pd
import io
import json # Import the json library

def read_xlsx_to_dfs(file_content: io.BytesIO) -> dict[str, pd.DataFrame]:
    """
    Reads an XLSX file content and converts its data into a dictionary of pandas DataFrames.
    If any cell is NaN, it takes the value of the cell above it (forward fill).

    Each sheet in the Excel file becomes a key in the returned dictionary.
    The value for each sheet key is a pandas DataFrame representing that sheet's data.

    Args:
        file_content (io.BytesIO): The byte stream of the uploaded XLSX file.

    Returns:
        dict[str, pd.DataFrame]: A dictionary where keys are sheet names and values are
                                  pandas DataFrames. Returns an empty dictionary if an error occurs.
    """
    try:
        # Read all sheets from the Excel file content into an ordered dictionary of DataFrames
        # sheet_name=None reads all sheets.
        xls_data = pd.read_excel(file_content, sheet_name=None)

        processed_dataframes = {}
        for sheet_name, df in xls_data.items():
            # Apply forward fill to handle NaN values
            # This fills NaN values with the last valid observation in the column
            processed_dataframes[sheet_name] = df.ffill()
        
        return processed_dataframes

    except Exception as e:
        st.error(f"An error occurred during conversion: {e}")
        return {}

# --- Streamlit Application ---
st.set_page_config(
    page_title="XLSX to DataFrame Converter",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("📊 XLSX to DataFrame Converter")
st.markdown("""
Upload your Excel (.xlsx) file below to convert its contents into **pandas DataFrames**.
**NaN values will be filled with the value of the cell directly above them.**
You can then select a specific sheet to preview and download as a `.txt` file,
formatted as a JSON string for easy embedding.
""")

uploaded_file = st.file_uploader("Choose an XLSX file", type="xlsx")

if uploaded_file is not None:
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    file_content = io.BytesIO(uploaded_file.read())
    data_dataframes = read_xlsx_to_dfs(file_content)

    if data_dataframes:
        st.subheader("Converted DataFrame Data")

        # Allow user to select a sheet if there are multiple
        sheet_names = list(data_dataframes.keys())
        if len(sheet_names) > 1:
            selected_sheet = st.selectbox("Select a sheet to display:", sheet_names)
        else:
            selected_sheet = sheet_names[0]
            st.info(f"Displaying data from the '{selected_sheet}' sheet.")

        # Display the selected DataFrame
        df_to_display = data_dataframes[selected_sheet]
        st.dataframe(df_to_display)

        # Convert DataFrame to a list of dictionaries (records) and then to a JSON string
        # This makes it easy to embed as a dictionary in other programs
        json_output = json.dumps(df_to_display.to_dict(orient='records'), indent=4)

        # Provide download option for the selected DataFrame as TXT (JSON string)
        st.download_button(
            label=f"Download '{selected_sheet}' Data as TXT",
            data=json_output,
            file_name=f"{uploaded_file.name.split('.')[0]}_{selected_sheet}.txt",
            mime="text/plain"
        )
    else:
        st.warning("No data was converted. Please check your Excel file format.")

st.markdown("---")
st.info("Developed with ❤️ using Streamlit, pandas, and io.")
