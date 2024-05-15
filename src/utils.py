import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st


def read_file(uploaded_file):
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension == "csv":
        return pd.read_csv(uploaded_file)
    elif file_extension == "txt":
        return pd.read_csv(uploaded_file, sep="\t")
    elif file_extension == "xlsx":
        return pd.read_excel(uploaded_file)
    else:
        st.error("Unsupported file type")
        return None


def detect_outliers_iqr(data, column, multiplier=1.5):
    """
    Detect outliers using the Interquartile Range (IQR) method.

    Parameters:
        data (DataFrame): DataFrame to detect outliers from.
        column (str): Column name to detect outliers in.
        multiplier (float): Multiplier for the IQR. Defaults to 1.5.

    Returns:
        outliers (list): List of outlier values.
        outliers_encounter_id (list): List of encounter IDs for the outliers.
    """
    # Calculate the first and third quartiles
    Q1 = np.percentile(data[column], 25)
    Q3 = np.percentile(data[column], 75)

    # Calculate the interquartile range (IQR)
    IQR = Q3 - Q1

    # Define the outlier bounds
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR

    # Identify outliers
    outliers = [
        value for value in data[column] if value < lower_bound or value > upper_bound
    ]
    outliers_encounter_id = data.loc[
        (data[column] < lower_bound) | (data[column] > upper_bound), "encounter_id"
    ].tolist()

    st.write(
        f"Outliers detected in the column {column} using IQR method with multiplier {multiplier}:"
    )
    for i, outlier in enumerate(outliers):
        st.write(f"Outlier: {outlier}, Encounter ID: {outliers_encounter_id[i]}")

    return outliers, outliers_encounter_id


def remove_rows_by_column_value(data, column_name, column_values):
    """
    Remove rows with specified column values from the DataFrame.

    Parameters:
        data (DataFrame): DataFrame containing the data.
        column_name (str): Name of the column to check for values.
        column_values (list): List of values to remove.

    Returns:
        cleaned_data (DataFrame): DataFrame with specified rows removed.
    """
    cleaned_data = data[~data[column_name].isin(column_values)].copy()
    st.write("Dataframe shape before removing rows:", data.shape)
    st.write("Dataframe shape after removing rows:", cleaned_data.shape)

    return cleaned_data


def value_counts_with_percentage(df, column):
    """
    Calculate value counts and percentage for each unique value in the specified column.

    Args:
    - df: DataFrame to calculate value counts and percentages
    - column: Column for which value counts and percentages are calculated

    Returns:
    - DataFrame with value counts and percentage for each unique value in the column
    """
    value_counts = df[column].value_counts()
    total_count = len(df)
    percentage = (value_counts / total_count) * 100

    result_df = pd.DataFrame({"count": value_counts, "percentage": percentage})
    return result_df


def filter_with_percentage(data, column, percent_thresh):
    freq_df = value_counts_with_percentage(data, "maternal_race")
    filtered_df = data[
        data[column].isin(freq_df[freq_df["percentage"] > percent_thresh].index)
    ]
    return filtered_df


def split_data_by_date(data, split_date="2028-03-01"):
    before_df = data[data["uds_collection_date"] < split_date]
    after_df = data[data["uds_collection_date"] >= split_date]
    return before_df, after_df


def create_pie_chart(df, column, colors=None, width=600, height=400):
    """
    Create a fancy pie chart using Plotly based on the frequency of a column.

    Parameters:
    df (pd.DataFrame): The data frame containing the data.
    column (str): The column name for which to plot the pie chart.
    colors (list): List of colors to use for the pie chart slices.
    width (int): Width of the chart.
    height (int): Height of the chart.

    Returns:
    fig (plotly.graph_objs._figure.Figure): The Plotly figure object.
    """
    # Calculate the frequency of each unique value in the column
    freq_df = df[column].value_counts().reset_index()
    freq_df.columns = [column, "Count"]

    # Create the pie chart
    fig = px.pie(
        freq_df,
        names=column,
        values="Count",
        title=f"{column} Distribution",
        color_discrete_sequence=colors,
    )

    # Customize the chart
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), width=width, height=height)

    return fig


def create_histogram(data, bin_size, width=600, height=400):
    """
    Create a fancy interactive histogram.

    Parameters:
        data (array-like): Data to plot.
        bin_size (int): Size of bins.

    Returns:
        None
    """

    fig = px.histogram(
        data,
        x=data,
        nbins=int((data.max() - data.min()) / bin_size),
        title="Distribution of Maternal Ages",
        labels={"x": "Maternal Age", "y": "Frequency"},
        color_discrete_sequence=["#009999"],
    )

    # Update traces to add bar outlines
    fig.update_traces(marker=dict(line=dict(color="black", width=1.5)))

    # Add a vertical line at the mean
    fig.add_vline(x=data.mean(), line=dict(color="red", dash="dash"), name="Mean Age")

    # Update layout for better visualization
    fig.update_layout(
        xaxis_title="Maternal Age",
        yaxis_title="Frequency",
        title_font_size=20,
        xaxis_title_font_size=18,
        yaxis_title_font_size=18,
        showlegend=False,
        plot_bgcolor="#cbcbcb",
        margin=dict(l=20, r=20, t=40, b=20),
        width=width,
        height=height,
    )

    # Show the figure in Streamlit
    st.plotly_chart(fig)


def add_custom_css():
    st.markdown(
        """
    <style>
    .plot-container {
        border: 2px solid black;
        padding: 15px;
        border-radius: 4px;
        margin-top: 20px;
        background-color: white;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
