KEY_COLUMN_NAME = "encounter_id"
ACTION_COLUMN_NAME = "uds_order_id"
RESULTS_COLUMN_NAME = "cps_reporting_date"

SENSITIVE_COLUMN_NAME = "maternal_race"

COLOR = "#009999"


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
    return cleaned_data
