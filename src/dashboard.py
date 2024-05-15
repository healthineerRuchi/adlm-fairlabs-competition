import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import base64

import utils

from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="My Streamlit App",
    page_icon=":guardsman:",  # Example emoji as an icon
    layout="wide",  # This sets the layout to wide screen
    initial_sidebar_state="expanded",  # Sidebar state can be "expanded" or "collapsed"
)


def page_upload_file():
    st.title("Page 1: Upload File")

    uploaded_files = st.file_uploader(
        "Choose files", type=["csv", "txt", "xlsx"], accept_multiple_files=True
    )
    if uploaded_files:
        for uploaded_file in uploaded_files:
            df = utils.read_file(uploaded_file)
            if st.checkbox("Preview DataFrame"):
                st.write("Preview of the DataFrame:")
                st.write(df)

            if df is not None:
                col1, col2 = st.columns(2)
                with col1:
                    sensitive_column = st.selectbox(
                        "Select sensitive column",
                        df.columns,
                    )
                with col2:
                    output_column = st.multiselect(
                        "Select output column", df.columns, default="cps_reporting_date"
                    )

                df["cps_reported"] = df[output_column].notna().astype(int)
                drug_tst_cols = [col for col in df.columns if "detected" in col]
                df["uds_positive"] = df[drug_tst_cols].any(axis=1).astype(int)
                df["uds_ordered"] = df["uds_collection_date"].apply(
                    lambda x: 1 if pd.notnull(x) and x != "" else 0
                )

                outliers, outliers_encounter_id = utils.detect_outliers_iqr(
                    df, "maternal_age", 2.5
                )

                remove = st.checkbox("Remove outliers", value=True)
                if remove:
                    df = utils.remove_rows_by_column_value(
                        df, "encounter_id", outliers_encounter_id
                    )
                    st.success("Outliers removed!")

                thresh = st.slider(
                    "Select minimum frequency threshold (%) to include rows", 0, 100, 3
                )
                st.write("Selected Threshold:", thresh, "%")

                df = utils.filter_with_percentage(df, "maternal_race", thresh)
                before_df, after_df = utils.split_data_by_date(df, "2028-03-01")

                # Store dataframes in session state
                st.session_state.df = df
                st.session_state.before_df = before_df
                st.session_state.after_df = after_df


def page_explore_data():
    st.title("Explore Data")

    utils.add_custom_css()

    # Check if the dataframe is in the session state
    if "df" not in st.session_state or st.session_state.df is None:
        st.warning("No data available. Please upload a file on Page 1.")
        return

    df = st.session_state.df

    # Create responsive columns
    col1, col2 = st.columns(2)

    with col1:
        if st.checkbox("Maternal Age Distribution"):
            st.subheader("Histogram Settings")
            bin_size = st.slider("Bin Size", min_value=1, max_value=10, value=3)
            utils.create_histogram(df["maternal_age"], bin_size)

    with col2:
        if st.checkbox("View Race Distribution"):
            st.subheader("Race Distribution Pie Chart")
            fig = utils.create_pie_chart(
                df, "maternal_race", colors=["#009999", "gray", "brown"]
            )
            st.plotly_chart(fig)


def page_track_fairness():
    st.title("Insights")

    # Check if the before_df, after_df, and df are in the session state
    if "before_df" not in st.session_state or st.session_state.before_df is None:
        st.warning("No data available. Please upload a file on Page 1.")
        return

    if "after_df" not in st.session_state or st.session_state.after_df is None:
        st.warning("No data available. Please upload a file on Page 1.")
        return

    if "df" not in st.session_state or st.session_state.df is None:
        st.warning("No data available. Please upload a file on Page 1.")
        return

    time_period = st.radio(
        "Select Time Period:", ("All Time", "Before Intervention", "After Intervention")
    )

    # Determine which DataFrame to use based on the selected checkbox
    # Determine which DataFrame to use based on the selected radio button
    if time_period == "All Time":
        selected_df = st.session_state.df
    elif time_period == "Before Intervention":
        selected_df = st.session_state.before_df
    elif time_period == "After Intervention":
        selected_df = st.session_state.after_df
    else:
        st.warning("Please select a time period.")
        return

    # Calculate fairness metrics
    result_df = utils.calculate_fairness_metrics(
        df=selected_df, sensitive_column="maternal_race"
    )

    if time_period == "After Intervention":
        utils.plot_order_indication_counts(st.session_state.after_df)
    st.write(result_df)


def main():
    # Initialize session state variables
    if "df" not in st.session_state:
        st.session_state.df = None
    if "before_df" not in st.session_state:
        st.session_state.before_df = None
    if "after_df" not in st.session_state:
        st.session_state.after_df = None

    selected = option_menu(
        menu_title=None,
        options=["Upload", "Explore", "Insights"],
        icons=["cloud-upload", "bar-chart", "lightbulb"],
        orientation="horizontal",
    )

    if selected == "Upload":
        page_upload_file()
    if selected == "Explore":
        page_explore_data()
    if selected == "Insights":
        page_track_fairness()


if __name__ == "__main__":
    main()
