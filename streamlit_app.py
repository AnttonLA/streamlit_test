import pandas as pd
import streamlit as st
import altair as alt
import numpy as np
import plotly.graph_objs as go
import webbrowser


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


def altair_plot_genome_position_v_pval(df: pd.DataFrame, column_name_map: dict, has_link: bool = False) -> None:
    """
    Function to plot the p-values on the genome using altair (https://altair-viz.github.io/)
    :param df: DataFrame
    :param column_name_map: Dictionary mapping the default column names to the actual column names
    :param has_link: Boolean indicating if the df has a dbSNP link column. The name of the column must be 'dbSNP'
    :return: None
    """
    # Add -log10(p) column
    df['-log10(p)'] = -np.log10(df[column_name_map['p']])

    # Plot
    if not has_link:
        c = alt.Chart(df).mark_point().encode(
            x=column_name_map['bp'], y='-log10(p)',
            tooltip=[column_name_map['snp'], column_name_map['p']])
    else:
        c = alt.Chart(df).mark_point().encode(
            x=column_name_map['bp'], y='-log10(p)',
            tooltip=[column_name_map['snp'], column_name_map['p'], 'dbSNP'])
    st.altair_chart(c)


def plotly_plot_genome_position_v_pval(df: pd.DataFrame, column_name_map: dict, has_link: bool = False) -> None:
    """
    Function to plot the p-values on the genome using plotly (https://plotly.com/python/)
    :param df: DataFrame
    :param column_name_map: Dictionary mapping the default column names to the actual column names
    :param has_link: Boolean indicating if the df has a dbSNP link column. The name of the column must be 'dbSNP'
    :return: None
    """

    # Add -log10(p) column
    df['-log10(p)'] = -np.log10(df[column_name_map['p']])

    tab1, tab2 = st.tabs(["By exponent of p-value (default)", "By p-value"])
    with tab1:
        scatter = go.Scatter(
            x=df[column_name_map['bp']],
            y=df['-log10(p)'],
            mode='markers',
            marker=dict(size=15, color='blue', opacity=0.5),
            text=df[column_name_map['snp']],
            customdata=df[column_name_map['p']],
        )

        fig = go.Figure(scatter)
        hovertemplate_string = 'variant: %{text}<br>p-value: %{customdata}<extra></extra>'
        fig.update_traces(hovertemplate=hovertemplate_string)
        st.plotly_chart(fig)

    with tab2:
        scatter = go.Scatter(
            x=df[column_name_map['bp']],
            y=df[column_name_map['p']],
            mode='markers',
            marker=dict(size=15, color='blue', opacity=0.5),
            text=df[column_name_map['snp']],
            customdata=df[column_name_map['p']],
        )

        fig = go.Figure(scatter)
        hovertemplate_string = 'variant: %{text}<br>p-value: %{customdata}<extra></extra>'
        fig.update_traces(hovertemplate=hovertemplate_string)
        st.plotly_chart(fig)


def get_dbsnp_link(chromosome: str, position: int) -> str:
    """
    Function to get the dbSNP link for a given chromosome and position
    :param chromosome: Chromosome
    :param position: Position
    :return: dbSNP link
    """
    return f"https://www.ncbi.nlm.nih.gov/snp/?term={chromosome}%5BChromosome%5D+AND+{position}%5Bchrpos%5D"


def open_dbsnp_link(url) -> None:
    """
    Function to open a dbSNP link in a new tab
    :param url: dbSNP link
    :return: None
    """
    webbrowser.open_new_tab(url)


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

            # Add dbSNP link as a column
            df['dbSNP'] = df.apply(lambda row: get_dbsnp_link(row[column_name_map['chr']],
                                                              row[column_name_map['bp']]), axis=1)

            plotly_plot_genome_position_v_pval(df, column_name_map, has_link=True)

            # st.dataframe(df)

            # TODO: add further checks. E.g. check that the chr column is the same for all rows, check that the bp
            #  column is not too spread out, check that the p column is between 0 and 1, etc.


if __name__ == '__main__':
    main()
