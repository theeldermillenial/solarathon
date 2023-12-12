"""
https://github.com/widgetti/solara/blob/9dc4e6b282602664a7c73930ee64ddfd714594a5/solara/components/datatable.py
"""

from typing import List, cast

import numpy as np
import reacton.ipyvuetify as v
import reacton.ipywidgets as w

import solara
from solara.components import ui_checkbox, ui_dropdown
from solara.hooks import use_cross_filter
from solara.lab.hooks.dataframe import use_df_column_names
from solara.lab.utils.dataframe import df_unique


cardheight = "100%"

@solara.component
def Table(df):
   return solara.DataFrame(
            df, 
            # column_actions=column_actions, 
            # cell_actions=cell_actions
        )

@solara.component
def TableCard(df):
    filter, set_filter = use_cross_filter(id(df), "table")
    dff = df
    filtered = False
    if filter is not None:
        filtered = True
        dff = df[filter]
    if filtered:
        title = "Filtered"
    else:
        title = "Showing all"
    title = "Get familiar with Cardano Token Registry"
    progress = len(dff) / len(df) * 100
    with v.Card(elevation=2, height=cardheight) as main:
        with v.CardTitle(children=[title]):
            if filtered:
                v.ProgressLinear(value=progress)
        with v.CardText():
            Table(dff)
    return main


cardheight = "100%"

@solara.component
def SummaryCard(df):
    filter, set_filter = use_cross_filter(id(df), "table")
    dff = df
    filtered = False
    if filter is not None:
        filtered = True
        dff = df[filter]
    if filtered:
        title = "Filtered"
    else:
        title = "Showing all"
    progress = len(dff) / len(df) * 100
    with v.Card(elevation=2, height=cardheight) as main:
        with v.CardTitle(children=[title]):
            if filtered:
                v.ProgressLinear(value=progress)
        with v.CardText():
            icon = "mdi-filter"
            v.Icon(children=[icon], style_="opacity: 0.1" if not filtered else "")
            if filtered:
                summary = f"{len(dff):,} / {len(df):,}"
            else:
                summary = f"{len(dff):,}"
            v.Html(tag="h3", children=[summary], style_="display: inline")
    return main


@solara.component
def DropdownCard(df, column=None):
    max_unique = 100
    filter, set_filter = use_cross_filter(id(df), "filter-dropdown")
    columns = use_df_column_names(df)
    column, set_column = solara.use_state(columns[4] if column is None else column)
    uniques = df_unique(df, column, limit=max_unique + 1)
    value, set_value = solara.use_state(None)
    # to avoid confusing vuetify about selecting 'None' and nothing
    magic_value_missing = "__missing_value__"

    def set_value_and_filter(value):
        set_value(value)
        if value is None:
            set_filter(None)
        else:
            value = value["value"]
            if value == magic_value_missing:
                set_filter(str(df[column].ismissing()))
            else:
                filter = df[column] == value
                set_filter(filter)

    with v.Card(elevation=2, height=cardheight) as main:
        with v.CardTitle(children=["Filter out list"]):
            pass
        with v.CardText():
            with v.Btn(v_on="x.on", icon=True, absolute=True, style_="right: 10px; top: 10px") as btn:
                v.Icon(children=["mdi-settings"])
            with v.Dialog(v_slots=[{"name": "activator", "variable": "x", "children": btn}], width="500"):
                with v.Sheet():
                    with v.Container(pa_4=True, ma_0=True):
                        with v.Row():
                            with v.Col():
                                v.Select(v_model=column, items=columns, on_v_model=set_column, label="Choose column")
            # we use objects to we can distinguish between selecting nothing or None
            items = [{"value": magic_value_missing if k is None else k, "text": str(k)} for k in uniques]

            v.Select(v_model=value, items=items, on_v_model=set_value_and_filter, label=f"Choose {column} value", clearable=True, return_object=True)
            if len(uniques) > max_unique:
                v.Alert(type="warning", text=True, prominent=True, icon="mdi-alert", children=[f"Too many unique values, will only show first {max_unique}"])

    return main