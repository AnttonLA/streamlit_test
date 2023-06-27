import streamlit as st
import pandas as pd

"""
This streamlit app aims to be a micro-tool to re-format genomic data files. Currently WIP.
"""


def edit_df_columns(df, column_names, column_order):
    # Rename the columns
    df.columns = column_names

    # Reorder the columns
    df = df[column_order]

    return df


def main():
    st.title("Data File Re-formatter")
    st.write("Re-format a text file table so that its columns are in the desired order and have the desired name.")
    # Set default separator and column names
    separator = st.text_input("Separator (default: '\\t')", "\t")
    column_names = st.sidebar.text_input("Column Names (comma-separated)", "").split(",")
    column_order = ''
    # Upload data file
    data_file = st.file_uploader("Upload Data File")

    if data_file is not None:
        # Read the uploaded file
        in_df = pd.read_csv(data_file, sep=separator)

        if column_order:
            # Re-format the data
            df = edit_df_columns(in_df, column_names, column_order)
        else:
            df = in_df

        # Display the contents of the file
        st.subheader("Data File Contents")
        st.dataframe(df)

        # Define column order
        column_order = st.multiselect("Column Order", column_names)



if __name__ == "__main__":
    main()
