import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from config import SUMMARY_FIELD_DISPLAY_NAMES, format_value
from widgets.table_difference import show_table_difference


def create_summary_comparison_viz(file1_data, file2_data):
    """Create visualizations comparing summary data between two files"""
    file1_name = file1_data["name"]
    file2_name = file2_data["name"]

    summary_df1 = file1_data["summary_df"]
    summary_df2 = file2_data["summary_df"]

    st.subheader(f"Summary Data Comparison: {file1_name} vs {file2_name}")

    # Check if we have summary data to compare
    if not summary_df1.empty and not summary_df2.empty:
        # Use table difference widget for detailed comparison if we have common columns
        if "wbe_code" in summary_df1.columns and "wbe_code" in summary_df2.columns:
            st.subheader("Detailed Summary Comparison")

            # Filter numeric columns for comparison
            numeric_columns = ["wbe_direct_cost", "contribution_margin"]

            if numeric_columns:
                # Use table difference widget
                with st.expander("Table Difference View", expanded=True):
                    show_table_difference(
                        summary_df1,
                        summary_df2,
                        "wbe_code",
                        numeric_columns,
                        df1_title=file1_name,
                        df2_title=file2_name,
                    )

    # Check if we have necessary data for direct cost comparison
    if (
        not summary_df1.empty
        and not summary_df2.empty
        and "wbe_direct_cost" in summary_df1.columns
        and "wbe_direct_cost" in summary_df2.columns
    ):
        st.subheader(
            f"Changes in {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_direct_cost', {'display_name': 'Direct Cost'})['display_name']} by {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_code', {'display_name': 'WBE Code'})['display_name']}: {file1_name} vs {file2_name}"
        )

        # Get common WBE codes
        common_codes = set(summary_df1["wbe_code"]).intersection(
            set(summary_df2["wbe_code"])
        )

        if common_codes:
            # Create comparison DataFrame
            comparison_data = []
            for code in common_codes:
                cost1 = summary_df1[summary_df1["wbe_code"] == code][
                    "wbe_direct_cost"
                ].iloc[0]
                cost2 = summary_df2[summary_df2["wbe_code"] == code][
                    "wbe_direct_cost"
                ].iloc[0]
                desc = summary_df1[summary_df1["wbe_code"] == code][
                    "wbe_description"
                ].iloc[0]

                comparison_data.append(
                    {
                        SUMMARY_FIELD_DISPLAY_NAMES.get(
                            "wbe_code", {"display_name": "WBE Code"}
                        )["display_name"]: code,
                        SUMMARY_FIELD_DISPLAY_NAMES.get(
                            "wbe_description", {"display_name": "Description"}
                        )["display_name"]: desc,
                        f"{file1_name} {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_direct_cost', {'display_name': 'Direct Cost'})['display_name']}": cost1,
                        f"{file2_name} {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_direct_cost', {'display_name': 'Direct Cost'})['display_name']}": cost2,
                        "Difference": cost2 - cost1,
                        "Percent Change": (
                            ((cost2 - cost1) / cost1 * 100) if cost1 != 0 else 0
                        ),
                    }
                )

            comparison_df = pd.DataFrame(comparison_data)

            # Sort by absolute difference
            comparison_df["Abs Difference"] = comparison_df["Difference"].abs()
            comparison_df = comparison_df.sort_values("Abs Difference", ascending=False)
            comparison_df = comparison_df.drop("Abs Difference", axis=1)

            # Create a copy for display with formatted values
            display_df = comparison_df.copy()
            display_df[
                f"{file1_name} {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_direct_cost', {'display_name': 'Direct Cost'})['display_name']}"
            ] = display_df[
                f"{file1_name} {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_direct_cost', {'display_name': 'Direct Cost'})['display_name']}"
            ].map(
                lambda x: format_value("wbe_direct_cost", x, "summary")
            )
            display_df[
                f"{file2_name} {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_direct_cost', {'display_name': 'Direct Cost'})['display_name']}"
            ] = display_df[
                f"{file2_name} {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_direct_cost', {'display_name': 'Direct Cost'})['display_name']}"
            ].map(
                lambda x: format_value("wbe_direct_cost", x, "summary")
            )
            display_df["Difference"] = display_df["Difference"].map(
                lambda x: format_value("wbe_direct_cost", x, "summary")
            )
            display_df["Percent Change"] = display_df["Percent Change"].map(
                lambda x: "{:,.2f}%".format(x) if pd.notna(x) else "N/A"
            )

            # Display the comparison table
            st.dataframe(display_df, use_container_width=True)

            # Create visualization
            fig = go.Figure()

            # Add bars for each file's direct costs
            fig.add_trace(
                go.Bar(
                    name=file1_name,
                    x=comparison_df[
                        SUMMARY_FIELD_DISPLAY_NAMES.get(
                            "wbe_code", {"display_name": "WBE Code"}
                        )["display_name"]
                    ],
                    y=comparison_df[
                        f"{file1_name} {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_direct_cost', {'display_name': 'Direct Cost'})['display_name']}"
                    ],
                    text=display_df[
                        f"{file1_name} {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_direct_cost', {'display_name': 'Direct Cost'})['display_name']}"
                    ],
                    textposition="auto",
                )
            )

            fig.add_trace(
                go.Bar(
                    name=file2_name,
                    x=comparison_df[
                        SUMMARY_FIELD_DISPLAY_NAMES.get(
                            "wbe_code", {"display_name": "WBE Code"}
                        )["display_name"]
                    ],
                    y=comparison_df[
                        f"{file2_name} {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_direct_cost', {'display_name': 'Direct Cost'})['display_name']}"
                    ],
                    text=display_df[
                        f"{file2_name} {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_direct_cost', {'display_name': 'Direct Cost'})['display_name']}"
                    ],
                    textposition="auto",
                )
            )

            # Update layout
            fig.update_layout(
                title=f'Comparison of {SUMMARY_FIELD_DISPLAY_NAMES.get("wbe_direct_cost", {'display_name': 'Direct Cost'})['display_name']} by {SUMMARY_FIELD_DISPLAY_NAMES.get("wbe_code", {'display_name': 'WBE Code'})['display_name']}',
                xaxis_title=SUMMARY_FIELD_DISPLAY_NAMES.get(
                    "wbe_code", {"display_name": "WBE Code"}
                )["display_name"],
                yaxis_title=SUMMARY_FIELD_DISPLAY_NAMES.get(
                    "wbe_direct_cost", {"display_name": "Direct Cost"} 
                )["display_name"],
                barmode="group",
                yaxis_tickformat=",.2f",
            )

            st.plotly_chart(fig, use_container_width=True)

            # Price distribution comparison
            if (
                "wbe_list_price" in summary_df1.columns
                and "wbe_list_price" in summary_df2.columns
            ):
                # Create box plots for price comparison
                fig = go.Figure()

                # Add box plot for file 1
                fig.add_trace(
                    go.Box(
                        y=summary_df1["wbe_list_price"].dropna(),
                        name=f"{file1_name} {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_list_price', {'display_name': 'List Price'})['display_name']}",
                        boxmean=True,
                        marker_color="#636EFA",
                    )
                )

                # Add box plot for file 2
                fig.add_trace(
                    go.Box(
                        y=summary_df2["wbe_list_price"].dropna(),
                        name=f"{file2_name} {SUMMARY_FIELD_DISPLAY_NAMES.get('wbe_list_price', {'display_name': 'List Price'})['display_name']}",
                        boxmean=True,
                        marker_color="#EF553B",
                    )
                )

                # Update layout
                fig.update_layout(
                    title=f'{SUMMARY_FIELD_DISPLAY_NAMES.get("wbe_list_price", {'display_name': 'List Price'})['display_name']} Distribution Comparison: {file1_name} vs {file2_name}',
                    yaxis_title=SUMMARY_FIELD_DISPLAY_NAMES.get(
                        "wbe_list_price", {"display_name": "List Price"}
                    )["display_name"],
                    yaxis_tickformat=",.2f",
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cannot compare direct costs - missing data from one or both files.")
