import pandas as pd
import numpy as np
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
    freq_df = value_counts_with_percentage(df, "maternal_race")
    filtered_df = df[
        df[column].isin(freq_df[freq_df["percentage"] > percent_thresh].index)
    ]
    return filtered_df


def split_data_by_date(data, split_date="2028-03-01"):
    before_df = data[data["uds_collection_date"] < split_date]
    after_df = data[data["uds_collection_date"] >= split_date]
    return before_df, after_df
