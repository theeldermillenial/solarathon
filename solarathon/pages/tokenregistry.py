"""
Token Registry
this page is showing all tokens from the token registry dated 2023-11-28
content is loaded from public folder
content in DataFrame (Table)
when you click on the token, it opens a modal with token info
token info is loaded from public folder tokens.json

1. Aggregate token metadata from the cardano token registry
2. Create a dictionary with token policy+name as keys and ticker name and icon as values
3. Create a custom modal that opens when you want to select tokens that shows icon, ticker name, and a selection
4. When selected, add a box similar to the dashboard that has token info
"""
from concurrent.futures import ThreadPoolExecutor
import dataclasses

import json
import solara
from solara.alias import rv

from pathlib import Path
from typing import Any, Dict, Optional, cast
import pandas as pd
from PIL import Image
import base64
from io import BytesIO
import reacton.ipyvuetify as v
from typing import Callable
import hashlib
import matplotlib.pyplot as plt

open_dialog = solara.reactive(False)

properties = ["subject", "policy", "name", "ticker", "logo"]

token_paths = list(
    Path(__file__).parent.parent.joinpath("public").joinpath("mappings").iterdir()
)
subjects = list(f.name for f in token_paths)

token_verified_info = json.load(open(Path(__file__).parent.parent / "public" / "tokens" / "tokens.json"))

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

def load_icon(icon_value):
    if icon_value:
            try:
                # Decode the Base64 string into bytes
                decoded = base64.b64decode(icon_value)
                # Open the image using PIL from the decoded bytes
                img = Image.open(BytesIO(decoded))
                # Convert the image to HTML format and store it
                if isinstance(img, Image.Image):
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    icon_value = f'<img src="data:image/png;base64,{img_str}" width="20px" height="20px">'
            except Exception as e:
                print(f"Failed to process image: {e}")
                icon_value = None
    return icon_value

def render_html(val):
    return solara.HTML(tag="html", unsafe_innerHTML=val) if val else None

@solara.component
def TokenItem(item, on_close: Callable[[], None]):
        solara.Button("", icon_name="mdi-window-close", icon=True, on_click=on_close, class_="token-item-close-button", style_="position: absolute; top: 0; right: 0; color: white; z-index: 1; font-size: 0.5rem")
        CryptoModal(item)


@solara.component
def TokenListItem(items, open_dialog: bool, set_open_dialog: Any):
    solara.Style(
        """
        .v-dialog {
            position: relative !important;
        }
        """
    )
   
    with v.ListItem():
        with v.Dialog(v_model=open_dialog, persistent=True, max_width="500px", on_v_model=set_open_dialog, class_="token-item-container"):
            if open_dialog:
                TokenItem(items, on_close=lambda: set_open_dialog(False))


@solara.component
def CryptoModal(item):
        # print('itemCryptoModal', item)
        with rv.Card(
                    style_=f"width: 100%; height: 100%; font-family: sans-serif; padding: 20px 20px; background-color: #1B2028; color: #ffff; box-shadow: rgba(0, 0, 0, 0) 0px 0px, rgba(0, 0, 0, 0) 0px 0px, rgba(0, 0, 0, 0.2) 0px 4px 6px -1px, rgba(0, 0, 0, 0.14) 0px 2px 4px -1px",
                ) as main:
                    rv.CardTitle(
                        # children=[GeckoIcon("", "")],
                        children=[solara.Text(item["ticker"])],
                        style_="padding: 0px 0px; padding-bottom: 5px;",
                    )
                    with solara.Div():
                        with solara.Div(
                            style={
                                "display": "inline",
                                "color": "white",
                                "position": "relative",
                            },
                        ):
                            solara.Text('Here it will show token info, like categories, project, website, etc. (from tokens.json)')
                           
                            with solara.GridFixed(
                                columns=2, justify_items="space-between", align_items="baseline"
                            ):
                                if 'project' in item:
                                    solara.Text(
                                        item['project'], style={"font-size": "1.5rem", "font-weight": 500}
                                    )
                                    solara.Text(str("project"), style={"font-size": "0.6rem"})
                                if 'categories' in item:
                                    solara.Text(item['categories'], style={"font-weight": 400})
                                    solara.Text(str("categories"), style={"font-size": "0.6rem"})
                                if 'socialLinks' in item and 'website' in item['socialLinks']:
                                    solara.Text(item['socialLinks']['website'], style={"font-weight": 500})
                                    solara.Text(
                                        str("website"), style={"font-size": "0.6rem"}
                                    )
                                if 'socialLinks' in item and 'coinGecko' in item['socialLinks']:
                                    solara.Text(item['socialLinks']['coinGecko'], style={"font-weight": 500})
                                    solara.Text(
                                        str("coinGecko"), style={"font-size": "0.6rem"}
                                    )
                                    if not item:
                                        solara.Text("No data available")
                    return main

@solara.component
def Page():
    column, set_column = solara.use_state(cast(Optional[str], None))
    cell, set_cell = solara.use_state(cast(Dict[str, Any], {}))
    content, set_content = solara.use_state(None)
    is_open, set_is_open = solara.use_state(False)

    # print('content', content)

    solara.Style(
        """
        .v-dialog {
            position: relative !important;
        }

        .token-item-close-button {
            position: absolute !important;
            top: 0 !important;
            right: 0 !important;
            color: white !important;
        }
        """
    )

    metadata = solara.use_memo(lambda: batchMetadataQuery(), [])
    #TODO reoder the list of tokens to show top_tickers first
    top_tickers = ["AGIX", "WMT", "COPI", "LENFI", "NTX", "MELD", "IAG", "SNEK", "MIN", "MILK", "INDY", "BOOK", "iUSD", "SOC", "SHEN", "LQ", "ENCS", "OPT", "HUNT", "NEWM", "GENS", "RJV", "SUNDAE", "JPG", "LIFI", "iBTC", "DJED", "FLAC", "cNETA", "NMKR", "HOSKY", "iETH", "WRT", "VYFI", "DISCO", "OPTIM", "EMP", "PAVIA", "FACT", "CLAY", "CHRY", "CBLP", "CGI", "GENSX", "CLAP", "SPF"]
    metadata = solara.use_memo(lambda: [subject for subject in metadata if subject["name"]["value"] in top_tickers] + [subject for subject in metadata if subject["name"]["value"] not in top_tickers], [metadata, top_tickers])

    # Create a dictionary with token policy+name as keys and ticker name and icon as values
    token_info_dict = {}
    for index, subject in enumerate(metadata):
        policy = subject["policy"]
        name_value = subject["name"]["value"]
        ticker_value = subject["ticker"]["value"] if subject["ticker"] is not None else ''
        icon_value = subject["logo"]["value"] if subject["logo"] is not None else None
        if policy:
            token_key = f"{policy}-{name_value}"
        else:
            token_key = f"non policy-{name_value}"
    
        token_info = {
            "index": index,
            "policy-token": token_key,
            "ticker": ticker_value,
            "icon": icon_value,
            # "icon": load_icon(icon_value),
        }

        common_key = subject["subject"]  # Assuming "subject" is the common key

        #TODO: you need to fix matching, common_key should match token_verified_info.keys() 
        # common_key is longer than token_verified_info.keys()
        # probably difference is in the end of the common string which is hashed name, but not sure
        if common_key in token_verified_info:
            print("matched key", common_key)
            token_info.update(token_verified_info[common_key])
            token_info["verified"] = True

       
        token_info_dict[token_key] = token_info

    def on_action_column(column):
        print(f"Column action on: {column}")
        set_column(column)

    def on_action_cell(column, row_index):
        print("index from row", row_index)
        print("column", column)

        for key, value in token_info_dict.items():
            print("index from token_info_dict", value["index"])
            if value["index"] == row_index:
                print("index matched")
                set_content(value)
                set_is_open(True)
                break
        else:
            print("No matching index found")

        set_cell(dict(column=column, row_index=row_index))
    column_actions = [
        solara.ColumnAction(
            icon="mdi-sunglasses", name="User column action", on_click=on_action_column
        )
    ]
    cell_actions = [
        solara.CellAction(
            icon="mdi-information-outline",
            name="Open Details",
            on_click=on_action_cell,
        )
    ]

    df = pd.DataFrame.from_dict(token_info_dict, orient="index")
    # here do not work because of the index from table not match to original index
    # df = df.sort_values(by=["verified", "ticker"], ascending=[False, True])
    # top_tickers = "AGIX, WMT, COPI, LENFI, NTX, MELD, IAG, SNEK, MIN, MILK, INDY, BOOK, iUSD, SOC, SHEN, LQ, ENCS, OPT, HUNT, NEWM, GENS, RJV, SUNDAE, JPG, LIFI, iBTC, DJED, FLAC, cNETA, NMKR, HOSKY, iETH, WRT, VYFI, DISCO, OPTIM, EMP, PAVIA, FACT, CLAY, CHRY, CBLP, CGI, GENSX, CLAP, SPF"
    # top_tickers_list = top_tickers.split(", ")
    # df = df[df['ticker'].isin(top_tickers_list)]
    # df = df.reset_index(drop=True)

    # inject html icon into dataframe
    # df['icon'] = df['icon'].apply(render_html)

    df = df.drop(columns=['index', 'icon', 'verified', 'project', 'categories', 'socialLinks'])

    with solara.VBox() as main:
        solara.Markdown(
            f"""
            # Get familiar with Cardano Token Registry
            """
        )
    
        solara.DataFrame(
            df, 
            column_actions=column_actions, 
            cell_actions=cell_actions,
        )

        TokenListItem(content, is_open, set_is_open)
        return main

    
