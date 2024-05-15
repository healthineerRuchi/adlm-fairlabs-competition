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
    st.title("Data Summary")
    st.markdown(
        """
        <style>
        .metric-box {
            border: 1px solid #ccc;
            border-radius: 5px;
            box-shadow: 5px 5px 20px rgba(0,0,0,0.1);
            padding: 10px;
            margin: 10px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col1:
        st.markdown(
            f"""
            <div class="metric-box">
                <h4 style="margin-bottom:0;color:#009999">Total Mothers</h2>
                <h1 style="margin-top:5px;">{format("6528")}</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-box">
                <h4 style="margin-bottom:0;color:#009999">Total Encounters</h2>
                <h1 style="margin-top:5px;">{format("6643")}</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-box">
                <h4 style="margin-bottom:0;color:#009999">Total UDS ordered</h2>
                <h1 style="margin-top:5px;">{format("700")}</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-box">
                <h4 style="margin-bottom:0;color:#009999"">Total positive cases</h2>
                <h1 style="margin-top:5px;">{format("442")}</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f"""
            <div class="metric-box">
                <h4 style="margin-bottom:0;color:#009999">Total CPS Reporting</h2>
                <h1 style="margin-top:5px;">{format("385")}</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
    # st.metric(
    #     label="Number of Mothers",
    #     value=format("371"),
    # )

    utils.add_custom_css()

    # Check if the dataframe is in the session state
    if "df" not in st.session_state or st.session_state.df is None:
        st.warning("No data available. Please upload a file on Page 1.")
        return

    df = st.session_state.df

    # Create responsive columns
    col1, col2 = st.columns(2)

    with col1:
        # if st.checkbox("Maternal Age Distribution"):
        st.subheader("Maternal Age Distribution")
        # bin_size = st.slider("Bin Size", min_value=1, max_value=10, value=3)
        utils.create_histogram(df["maternal_age"], bin_size=2)

    with col2:
        # if st.checkbox("View Race Distribution"):
        st.subheader("Race Distribution")
        fig = utils.create_pie_chart(
            df, "maternal_race", colors=["#009999", "gray", "brown"]
        )
        st.plotly_chart(fig)


def page_track_fairness():
    # st.title("Insights")

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

    # Move the radio buttons to the sidebar
    time_period = st.sidebar.radio(
        "Select Time Period:", ("All Time", "Pre-Intervention", "Post-Intervention")
    )

    # Determine which DataFrame to use based on the selected radio button
    if time_period == "All Time":
        selected_df = st.session_state.df
    elif time_period == "Pre-Intervention":
        selected_df = st.session_state.before_df
    elif time_period == "Post-Intervention":
        selected_df = st.session_state.after_df
    else:
        st.warning("Please select a time period.")
        return

    # Calculate fairness metrics
    result_df = utils.calculate_fairness_metrics(
        df=selected_df, sensitive_column="maternal_race"
    )
    result_df = result_df.sort_values(by="Total Count", ascending=False)

    st.write(result_df)

    black_ordered_total_pct = result_df[
        result_df["maternal_race"] == "Black or African American"
    ]["(Ordered/Total) %"].values[0]
    white_ordered_total_pct = result_df[result_df["maternal_race"] == "White"][
        "(Ordered/Total) %"
    ].values[0]
    demographic_parity_ratio = black_ordered_total_pct / white_ordered_total_pct

    before_result_df = utils.calculate_fairness_metrics(
        df=st.session_state.before_df, sensitive_column="maternal_race"
    )
    after_result_df = utils.calculate_fairness_metrics(
        df=st.session_state.after_df, sensitive_column="maternal_race"
    )
    demographic_parity_before = utils.demographic_parity(
        before_result_df, "Black or African American", "White"
    )
    demographic_parity_after = utils.demographic_parity(
        after_result_df, "Black or African American", "White"
    )
    delta = None
    if time_period == "Post-Intervention":
        delta = (
            (demographic_parity_before - demographic_parity_after)
            * 100
            / demographic_parity_before
        )
        delta = format(delta, ".2f")

    st.metric(
        label="Demographic Parity Ratio",
        value=format(demographic_parity_ratio, ".2f"),
        delta=delta,
        help="Proportion of positive predictions in Blacks / Proportion of positive predictions in Whites",
    )

    # st.markdown(
    #     """
    #     <style>
    #     .metric-box {
    #         border: 1px solid #ccc;
    #         border-radius: 5px;
    #         box-shadow: 5px 5px 20px rgba(0,0,0,0.1);
    #         padding: 10px;
    #         margin: 10px 0;
    #     }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )

    # col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    # with col1:
    #     st.markdown(
    #         f"""
    #             <div class="metric-box">
    #                 <h4 style="margin-bottom:0;">Demographic Parity</h2>
    #                 <h1 style="margin-top:5px;">{format(demographic_parity_ratio, ".2f")}</h1>
    #             </div>
    #             """,
    #         unsafe_allow_html=True,
    #     )

    cols = st.columns(len(result_df))
    for i in range(len(result_df)):
        # Create columns within the Streamlit app; adjust the number as needed
        with cols[
            i % 3
        ]:  # This ensures distribution across the columns; adjust modulus as per number of columns
            fig = utils.create_pie_charts(
                dataframe=result_df,
                column_name="(Ordered/Total) %",
                index=i,
                colors=["#009999", "#ec6602"],
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Tested Positive")
    cols = st.columns(len(result_df))
    for i in range(len(result_df)):
        # Create columns within the Streamlit app; adjust the number as needed
        with cols[
            i % 3
        ]:  # This ensures distribution across the columns; adjust modulus as per number of columns
            fig = utils.create_pie_charts(
                dataframe=result_df,
                column_name="(Positive/Ordered) %",
                index=i,
                colors=["#ec6602", "#009999"],
            )
            st.plotly_chart(fig, use_container_width=True)

    if time_period == "Post-Intervention":
        utils.plot_order_indication_counts(st.session_state.after_df)


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
