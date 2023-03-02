import streamlit as st
import plotly.express as px

from utils.transformation import export_drift_timeseries
from utils.export import structure

import os, sys

sys.path.insert(0, os.path.abspath("./"))

from whitebox import Whitebox


def create_drift_tab(wb: Whitebox, model_id: str) -> None:
    """
    Creates the dift tab in Streamlit.

    Gets the drift object and plots via streamlit the drifting graphs.
    It creates 2 tabs of graphs, one with the combined drifts of variables
    and one tab with graphs for each one variable.
    """
    with st.spinner("Loading model drift..."):
        structure()
        st.title("Drifting")
        drift = wb.get_drifting_metrics(model_id)
        # Isolate timeseties parts from the drift object
        value_df, drift_df = export_drift_timeseries(drift)
        # Keep the columns except the time/index
        df_columns = value_df.drop("index", axis=1).columns
        # We have 2 different representations
        common_tab, sep_tab = st.tabs(
            ["Common representation", "Separeted representation"]
        )

        with sep_tab:
            # Create a graph for each column/variable
            for column in df_columns:
                # Check if we have drift in order to mention it (as a subtitle)
                drift_detected = (drift_df[[column]] == True).any()[0]
                viz_df = value_df[[column, "index"]]
                viz_df.columns = ["drift_score", "time"]
                subtitle = ""

                if drift_detected:
                    subtitle = "Drift detected"

                fig = px.line(
                    viz_df,
                    x="time",
                    y="drift_score",
                    title=f"{column} <br><sup>{subtitle}</sup>",
                )
                st.plotly_chart(fig)

        with common_tab:
            # If dift is detected in at least one column/variable it
            # mentions drift as a whole
            drift_detected = True in drift_df.values
            subtitle = ""

            if drift_detected:
                subtitle = "Drift detected"

            fig = px.line(
                value_df,
                x="index",
                y=df_columns,
                title=f"All variables <br><sup>{subtitle}</sup>",
                markers=True,
            )
            st.plotly_chart(fig)
