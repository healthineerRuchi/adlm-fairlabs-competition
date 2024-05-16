import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import plotly.graph_objs as go


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

    # st.write(
    #     f"Outliers detected in the column {column} using IQR method with multiplier {multiplier}:"
    # )
    # for i, outlier in enumerate(outliers):
    # st.write(f"Outlier: {outlier}, Encounter ID: {outliers_encounter_id[i]}")

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
    # st.write("Dataframe shape before removing rows:", data.shape)

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
    before_df = data[pd.to_datetime(data["delivery_date"]) < split_date]
    after_df = data[pd.to_datetime(data["delivery_date"]) >= split_date]
    # st.write(before_df.shape, after_df.shape, data.shape)
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
        # title=f"{column} Distribution",
        color_discrete_sequence=colors,
    )

    # Customize the chart
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), width=width, height=height)

    return fig


def create_pie_charts(dataframe, column_name, index, colors=None):
    """
    Generates a pie chart for a specified column at a given index from the dataframe.

    This function creates a pie chart with two segments: the specified percentage from
    the dataframe and the remaining percentage to make up 100%.

    Args:
        dataframe (pd.DataFrame): The dataframe containing the data.
        column_name (str): The name of the column for which the pie chart is generated.
                           This column should contain the percentage value.
        index (int): The index of the row in the dataframe from which to generate the pie chart.

    Returns:
        go.Figure: A Plotly graph object Figure containing the pie chart.
    """
    # Retrieve the specific row based on index
    row = dataframe.iloc[index]

    # Prepare labels and values for the pie chart
    labels = [column_name, "Remaining (%)"]
    values = [
        row[column_name],
        100 - row[column_name],
    ]  # Calculate the remaining percentage

    # Create a Plotly pie chart figure
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    # Update layout with a title using the race column, adapt this if your DataFrame has a different title column
    fig.update_layout(title=f"{row['maternal_race']}")

    if colors:
        fig.update_traces(marker=dict(colors=colors))

    return fig


def create_histogram(data, bin_size=3, width=600, height=400):
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
        title="",
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


def calculate_fairness_metrics(
    df, sensitive_column, truth_col="uds_positive", predicted_col="uds_ordered"
):
    # Calculate count and percentage of uds_ordered
    ordered_count = df.groupby("maternal_race")["uds_ordered"].sum()
    total_count = df.groupby("maternal_race")["uds_ordered"].count()
    percent_ordered = (ordered_count / total_count) * 100

    # Calculate count and percentage of uds_positive
    positive_count = (
        df[df["uds_ordered"] == 1].groupby("maternal_race")["uds_positive"].sum()
    )
    percent_positive = (positive_count / ordered_count) * 100

    # Initialize an empty dictionary to store the results
    result_dict = {
        sensitive_column: [],
        "Total Count": [],
        "Ordered Count": [],
        "(Ordered/Total) %": [],
        "Positive Count": [],
        "(Positive/Ordered) %": [],
        "tp": [],
        "tn": [],
        "fp": [],
        "fn": [],
        "proportion_positive": [],
        "tpr": [],
        "tnr": [],
        "fpr": [],
        "ppp": [],
    }

    # Group the DataFrame by the sensitive column
    grouped = df.groupby(sensitive_column)

    # Calculate metrics for each group
    for group, data in grouped:
        tp = sum((data[truth_col] == 1) & (data[predicted_col] == 1))
        tn = sum((data[truth_col] == 0) & (data[predicted_col] == 0))
        fp = sum((data[truth_col] == 0) & (data[predicted_col] == 1))
        fn = sum((data[truth_col] == 1) & (data[predicted_col] == 0))

        total = len(data)
        proportion_positive = data[predicted_col].mean()
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        tnr = tn / (tn + fp) if (tn + fp) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        ### predicted as positive
        ppp = (tp + fp) / (tp + fp + tn + fn)

        # Append metrics to the result dictionary
        result_dict[sensitive_column].append(group)
        result_dict["tp"].append(tp)
        result_dict["tn"].append(tn)
        result_dict["fp"].append(fp)
        result_dict["fn"].append(fn)
        result_dict["proportion_positive"].append(proportion_positive)
        result_dict["tpr"].append(tpr)
        result_dict["tnr"].append(tnr)
        result_dict["fpr"].append(fpr)
        result_dict["ppp"].append(ppp)

        if group in ordered_count.index:
            result_dict["Total Count"].append(total_count[group])
            result_dict["Ordered Count"].append(ordered_count[group])
            result_dict["(Ordered/Total) %"].append(percent_ordered[group])
            result_dict["Positive Count"].append(positive_count.get(group, 0))
            result_dict["(Positive/Ordered) %"].append(percent_positive.get(group, 0))
        else:
            result_dict["Total Count"].append(0)
            result_dict["Ordered Count"].append(0)
            result_dict["(Ordered/Total) %"].append(0)
            result_dict["Positive Count"].append(0)
            result_dict["(Positive/Ordered) %"].append(0)

    # Convert the dictionary to a DataFrame
    result_df = pd.DataFrame(result_dict)

    return result_df


def plot_order_indication_counts(df):
    order_counts = df["order_indication"].value_counts().reset_index()
    order_counts.columns = ["order_indication", "count"]
    order_counts = order_counts.sort_values(by="count", ascending=False)

    # Create a horizontal bar graph using Plotly with custom colors
    fig = px.bar(
        order_counts,
        x="count",
        y="order_indication",
        orientation="h",
        labels={"count": "Count", "order_indication": "Order Indication"},
        title="Frequency of Order Indications",
        category_orders={"order_indication": order_counts["order_indication"].tolist()},
        color_discrete_sequence=["#009999"],
    )  # Customize the color here

    st.plotly_chart(fig)


def demographic_parity(df, group1, group2):
    group1_ordered_total_pct = df[df["maternal_race"] == group1][
        "(Ordered/Total) %"
    ].values[0]
    group2_ordered_total_pct = df[df["maternal_race"] == group2][
        "(Ordered/Total) %"
    ].values[0]
    demographic_parity_ratio = group1_ordered_total_pct / group2_ordered_total_pct
    return demographic_parity_ratio


def get_counts(df):
    mothers = df.mother_id.nunique()
    encounters = df.encounter_id.nunique()
    uds_ordered = df.uds_ordered.sum()
    positive_cases = df.uds_positive.sum()
    cps_reported = df.cps_reported.sum()
    return mothers, encounters, uds_ordered, positive_cases, cps_reported


def remove_corrupted_rows(df, column_name):
    """
    Filter DataFrame to remove rows containing '\r' or '\n' in the specified column.

    Args:
    - df: DataFrame to filter
    - column: Column to check for '\r' or '\n'

    Returns:
    - Filtered DataFrame
    """
    return df[~df[column_name].str.contains(r"\r|\n")]
