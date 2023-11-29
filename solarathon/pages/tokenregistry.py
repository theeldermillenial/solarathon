"""
Token Registry

1. Aggregate token metadata from the cardano token registry
2. Create a dictionary with token policy+name as keys and ticker name and icon as values
3. Create a custom modal that opens when you want to select tokens that shows icon, ticker name, and a selection
4. When selected, add a box similar to the dashboard that has token info
"""
import solara
import requests
from typing import Any, Dict, Optional, cast
import pandas as pd

open_dialog = solara.reactive(False)

# MIN, INDY
subjects = ["29d222ce763455e3d7a09a665ce554f00ac89d2e99a1a83d267170c64d494e","533bb94a8850ee3ccbe483106489399112b74c905342cb1792a797a0494e4459"]
properties = ["subjects", "policy", "name", "ticker", "logo"]

# Aggregate token metadata from the cardano token registry
def batchMetadataQuery():
    url = "https://tokens.cardano.org/metadata/query"
    payload = {
        "subjects": subjects,
        "properties": properties
    }
    response = requests.post(url, json=payload)
    return response.json()

# TODO: Create a custom modal that opens when you want to select tokens that shows icon, ticker name, and a selection
# @solara.component
# def CryptoModal():

@solara.component
def Page():
    column, set_column = solara.use_state(cast(Optional[str], None))
    cell, set_cell = solara.use_state(cast(Dict[str, Any], {}))
    content, set_content = solara.use_state(None)
    is_open, set_is_open = solara.use_state(False)
    print('is_open', is_open)

    metadata, _ = solara.use_state(batchMetadataQuery())
    index = 0

    # Create a dictionary with token policy+name as keys and ticker name and icon as values
    token_info_dict = {}
    for subject in metadata['subjects']:
        policy = subject['policy']
        name_value = subject['name']['value']
        ticker_value = subject['ticker']['value']
        icon_value = subject['logo']['value']
        token_info_dict[f"{policy}-{name_value}"] = {'index': index, 'ticker': ticker_value, 'icon': icon_value}
        index += 1
    def on_close():
        set_is_open(False)
        print("Closing...")

    def on_action_column(column):
        print(f"Column action on: {column}")
        set_column(column)

    def on_action_cell(column, row_index):
        print('index from row', row_index)

        for key, value in token_info_dict.items():
            print('index from token_info_dict', value['index'])
            if value['index'] == row_index:
                print('index matched')
                set_content(value)
                set_is_open(True)
                break
        print(f"Cell action on: {column} {row_index}")
        set_cell(dict(column=column, row_index=row_index))

    column_actions = [solara.ColumnAction(icon="mdi-sunglasses", name="User column action", on_click=on_action_column)]
    cell_actions = [solara.CellAction(icon="mdi-white-balance-sunny", name="User cell action", on_click=on_action_cell)]
    
    solara.Markdown(
        f"""
        # Get familiar with Cardano Token Registry
    """
    )
    df = pd.DataFrame.from_dict(token_info_dict, orient='index')
    df.index.name = 'Token Policy+Name'
    df.reset_index(inplace=True)

    solara.DataFrame(df, column_actions=column_actions, cell_actions=cell_actions)
    solara.lab.ConfirmationDialog(is_open, ok="Ok, Cancel", on_ok=on_close, content=f"Content: {content}")





