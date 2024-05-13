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


def split_data_by_date(data, split_date="2028-03-01"):
    before_df = df[df["uds_collection_date"] < split_date]
    after_df = df[df["uds_collection_date"] >= split_date]
    return before_df, after_df


def create_barh_chart(
    categories, values, xlabel="", ylabel="", title="", color=COLOR, figsize=(10, 6)
):
    plt.figure(figsize=figsize)
    plt.barh(categories, values, color=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()
