"""
Token Registry

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


@dataclasses.dataclass(frozen=True)
class TodoItem:
    text: str
    done: bool



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
                            with solara.GridFixed(
                                columns=2, justify_items="space-between", align_items="baseline"
                            ):
                                solara.Text(
                                    "todo", style={"font-size": "1.5rem", "font-weight": 500}
                                )
                                solara.Text(str("price"), style={"font-size": "0.6rem"})
                                solara.Text("todo", style={"font-weight": 400})
                                solara.Text(str("market cap"), style={"font-size": "0.6rem"})
                                solara.Text("todo", style={"font-weight": 500})
                                solara.Text(
                                    str("24h change price"), style={"font-size": "0.6rem"}
                                )
                                solara.Text("todo", style={"font-weight": 500})
                                solara.Text(
                                    str("24h change market cap"), style={"font-size": "0.6rem"}
                                )
                    return main


@solara.component
def GeckoIcon(name: str, img: str):
    with solara.v.Html(
        tag="a",
        attributes={"href": f"https://www.binance.com/en/trade", "target": "_blank"},
    ):
        with solara.v.ListItem(class_="pa-0"):
            with solara.v.ListItemAvatar(color="white"):
                solara.v.Img(
                    class_="elevation-6",
                    src=img,
                )
            with solara.v.ListItemContent():
                solara.v.ListItemTitle(children=[name], style_=f"color: white")


@solara.component
def Page():
    column, set_column = solara.use_state(cast(Optional[str], None))
    cell, set_cell = solara.use_state(cast(Dict[str, Any], {}))
    content, set_content = solara.use_state(None)
    is_open, set_is_open = solara.use_state(False)

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

    # Create a dictionary with token policy+name as keys and ticker name and icon as values
    token_info_dict = {}
    for index, subject in enumerate(metadata):
        policy = subject["policy"]
        name_value = subject["name"]["value"]
        ticker_value = subject["ticker"]["value"] if subject["ticker"] is not None else None
        icon_value = subject["logo"]["value"] if subject["logo"] is not None else None

        # LOAD ICONS - heavy
        # if icon_value:
        #     try:
        #         # Decode the Base64 string into bytes
        #         decoded = base64.b64decode(icon_value)
        #         # Open the image using PIL from the decoded bytes
        #         img = Image.open(BytesIO(decoded))
        #         # Convert the image to HTML format and store it
        #         if isinstance(img, Image.Image):
        #             buffered = BytesIO()
        #             img.save(buffered, format="PNG")
        #             img_str = base64.b64encode(buffered.getvalue()).decode()
        #             icon_value = f'<img src="data:image/png;base64,{img_str}" width="20px" height="20px">'
        #     except Exception as e:
        #         print(f"Failed to process image: {e}")
        #         icon_value = None

        token_info_dict[f"{policy}-{name_value}"] = {
            "index": index,
            "ticker": ticker_value,
            "icon": icon_value,
        }

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
            icon="mdi-information-outline",
            name="Open Details",
            on_click=on_action_cell,
        )
    ]

    solara.Markdown(
        f"""
        # Get familiar with Cardano Token Registry
    """
    )
    
    # def render_html(val):
    #     return solara.HTML(tag="div", unsafe_innerHTML=val) if val else None

    df = pd.DataFrame.from_dict(token_info_dict, orient="index")

    # inject html into dataframe
    # df["Icon"] = df["icon"].apply(render_html)

    df.reset_index(inplace=True)


    # cols = df.columns.tolist()
    # cols = ['Icon'] + [col for col in cols if col != 'Icon']
    # df = df[cols]

    with solara.VBox() as main:
        solara.DataFrame(
            df, 
            column_actions=column_actions, 
            cell_actions=cell_actions,
        )

        TokenListItem(content, is_open, set_is_open)
        # CryptoModal(False, on_close)
        return main

    
