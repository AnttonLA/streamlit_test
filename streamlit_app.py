import pandas as pd
import streamlit as st
import altair as alt
import numpy as np


def is_valid_file_extension(file_path: str, valid_extensions: list) -> bool:
    """
    Function to check if the file extension is valid
    """
    file_extension = '.' + file_path.split('.')[-1]
    return file_extension.lower() in valid_extensions


def has_valid_column_names(df: pd.DataFrame, required_columns_list_of_lists: list) -> bool:
    """
    Function to check if the column names are valid
    :param df: DataFrame
    :param required_columns_list_of_lists: List of lists containing all possible valid column names per column.
    At least one element of each sublist must be present
    :return: True if valid, False otherwise
    """
    columns = [x.lower() for x in df.columns.to_list()]
    if len(columns) < len(required_columns_list_of_lists):
        return False

    # Check per required column if at least one of the possible names is present
    success_bool_list = [False] * len(required_columns_list_of_lists)

    for i, possible_column_names in enumerate(required_columns_list_of_lists):
        for column in columns:
            if column in possible_column_names:
                success_bool_list[i] = True
                break

    # TODO: Check if there are multiple names for a single category. What if there's a 'chr' and a 'chromosome' column?

    # Check that all required columns are present
    return all(success_bool_list)


def plot_genome_position_v_pval(df: pd.DataFrame, column_name_map: dict) -> None:
    """
    Function to plot the p-values on the genome
    :param df: DataFrame
    :param column_name_map: Dictionary mapping the default column names to the actual column names
    :return: None
    """
    # Add -log10(p) column
    df['-log10(p)'] = -np.log10(df[column_name_map['p']])

    # Plot
    c = alt.Chart(df).mark_point().encode(
        x=column_name_map['bp'], y='-log10(p)',
        tooltip=[column_name_map['snp'], column_name_map['p']])
    st.altair_chart(c)


# Streamlit app
def main():
    # Set permitted file extensions and required column names. See https://software.broadinstitute.org/software/igv/GWAS
    permitted_extensions = ['.linear', '.logistic', '.assoc', '.qassoc', '.gwas']
    required_columns = [['chr', 'chromosome'],
                        ['bp', 'pos', 'position'],
                        ['snp', 'rs', 'rsid', 'rsnum', 'id', 'marker', 'markername'],
                        ['p', 'pval', 'p-value', 'pvalue', 'p.value']]
    st.title("GWAS file check")
    st.write("Check if your GWAS file has the proper IGV format!\n")
    st.write("For full information about the format, check the [IGV documentation]"
             "(https://software.broadinstitute.org/software/igv/GWAS)")

    # File upload
    file = st.file_uploader("Upload your GWAS file here", type=permitted_extensions)

    if file is not None:

        # Check file extension
        if not is_valid_file_extension(file.name, permitted_extensions):
            st.error(f"Invalid file extension. Permitted extensions: {', '.join(permitted_extensions)}")
        else:
            # Read the file as DataFrame
            df = pd.read_csv(file, delimiter='\t')

            # Check column names
            if not has_valid_column_names(df, required_columns):
                st.error("Invalid column names. Each required column must have exactly one valid option.")
            else:
                st.success("File is valid. All checks passed.")

            # Map the df column names to chr, bp, snp, p for internal consistency
            column_name_map = {}  # Key: default name, value: actual name on df
            for i, default_name in enumerate(['chr', 'bp', 'snp', 'p']):
                for column in df.columns.to_list():
                    if column.lower() in required_columns[i]:
                        column_name_map[default_name] = column

            plot_genome_position_v_pval(df, column_name_map)
            st.dataframe(df)

            # TODO: add further checks. E.g. check that the chr column is the same for all rows, check that the bp
            #  column is not too spread out, check that the p column is between 0 and 1, etc.


if __name__ == '__main__':
    main()
