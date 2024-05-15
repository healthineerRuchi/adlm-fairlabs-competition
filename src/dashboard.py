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


def upload_file():
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


def main():
    selected = option_menu(
        menu_title=None,
        options=["Upload", "Explore", "Analyse"],
        icons=["house", "book", "envelope"],
        orientation="horizontal",
    )
    # upload_file()


if __name__ == "__main__":
    main()
