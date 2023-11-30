"""
Token Registry

1. Aggregate token metadata from the cardano token registry
2. Create a dictionary with token policy+name as keys and ticker name and icon as values
3. Create a custom modal that opens when you want to select tokens that shows icon, ticker name, and a selection
4. When selected, add a box similar to the dashboard that has token info
"""
from concurrent.futures import ThreadPoolExecutor
import json
import solara

from pathlib import Path
from typing import Any, Dict, Optional, cast
import pandas as pd

open_dialog = solara.reactive(False)

properties = ["subject", "policy", "name", "ticker", "logo"]

token_paths = list(
    Path(__file__).parent.parent.joinpath("public").joinpath("mappings").iterdir()
)
subjects = list(f.name for f in token_paths)


# Aggregate token metadata from the cardano token registry
def load_token(path: Path) -> Dict[str, str]:
    with open(path, "r") as fr:
        try:
            token_info = json.load(fr)
        except UnicodeDecodeError:
            return None

    return {key: token_info.get(key, None) for key in properties}


def batchMetadataQuery():
    with ThreadPoolExecutor() as executor:
        tokens = executor.map(load_token, token_paths)

    return list(t for t in tokens if t is not None)


# TODO: Create a custom modal that opens when you want to select tokens that shows icon, ticker name, and a selection
# @solara.component
# def CryptoModal():


@solara.component
def Page():
    column, set_column = solara.use_state(cast(Optional[str], None))
    cell, set_cell = solara.use_state(cast(Dict[str, Any], {}))
    content, set_content = solara.use_state(None)
    is_open, set_is_open = solara.use_state(False)

    metadata, _ = solara.use_state(batchMetadataQuery())
    index = 0

    # Create a dictionary with token policy+name as keys and ticker name and icon as values
    token_info_dict = {}
    for subject in metadata:
        policy = subject["policy"]
        name_value = subject["name"]["value"]
        ticker_value = None if subject["ticker"] is None else subject["ticker"]["value"]
        icon_value = None if subject["logo"] is None else subject["logo"]["value"]
        token_info_dict[f"{policy}-{name_value}"] = {
            "index": index,
            "ticker": ticker_value,
            "icon": icon_value,
        }
        index += 1

    def on_close():
        set_is_open(False)
        print("Closing...")

    def on_action_column(column):
        print(f"Column action on: {column}")
        set_column(column)

    def on_action_cell(column, row_index):
        print("index from row", row_index)

        for key, value in token_info_dict.items():
            print("index from token_info_dict", value["index"])
            if value["index"] == row_index:
                print("index matched")
                set_content(value)
                set_is_open(True)
                break
        print(f"Cell action on: {column} {row_index}")
        set_cell(dict(column=column, row_index=row_index))

    column_actions = [
        solara.ColumnAction(
            icon="mdi-sunglasses", name="User column action", on_click=on_action_column
        )
    ]
    cell_actions = [
        solara.CellAction(
            icon="mdi-white-balance-sunny",
            name="User cell action",
            on_click=on_action_cell,
        )
    ]

    solara.Markdown(
        f"""
        # Get familiar with Cardano Token Registry
    """
    )
    df = pd.DataFrame.from_dict(token_info_dict, orient="index")
    df.index.name = "Token Policy+Name"
    df.reset_index(inplace=True)

    solara.DataFrame(df, column_actions=column_actions, cell_actions=cell_actions)
    solara.lab.ConfirmationDialog(
        is_open, ok="Ok, Cancel", on_ok=on_close, content=f"Content: {content}"
    )
