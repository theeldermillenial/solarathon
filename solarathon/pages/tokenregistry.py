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

import json
import solara

from pathlib import Path
from typing import Dict
import pandas as pd
from PIL import Image
import base64
from io import BytesIO
import numpy as np

from solarathon.components.token_registry_components import TableCard, SummaryCard, DropdownCard


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
                    icon_value = f"""<img src="data:image/png;base64,{img_str}" width="20px" height="20px">"""
            except Exception as e:
                print(f"Failed to process image: {e}")
                icon_value = None
    return icon_value


def render_html(val):
    return solara.HTML(tag="div", unsafe_innerHTML=val
    ) if val else ''

def format_links(links):
    if links:
        return '\n'.join(links.values())
    else:
        return ""

@solara.component
def Page():
    metadata, _ = solara.use_state(solara.use_memo(lambda: batchMetadataQuery(), dependencies=[]))

    # Create a dictionary with token policy+name as keys and ticker name and icon as values
    token_info_dict = {}
    for index, subject in enumerate(metadata):
        policy = subject["policy"] if subject["policy"] is not None else ''
        name_value = subject["name"]["value"] if subject["name"] is not None else ''
        ticker_value = subject["ticker"]["value"] if subject["ticker"] is not None else ''
        icon_value = subject["logo"]["value"] if subject["logo"] is not None else ''
        if policy:
            token_key = f"{policy}-{name_value}"
        else:
            token_key = f"non policy-{name_value}"
    
        token_info = {
            "index": index,
            # "icon": load_icon(icon_value),
            "policy-token": token_key,
            "ticker": ticker_value,

            "project": "",
            "categories": "",
            "verified": False,
            "socialLinks": "",
            "icon": icon_value,
        }
        common_key = subject["subject"]  # Assuming "subject" is the common key

        common_key_array = np.array(list(token_verified_info.keys()))
        matching_indices = np.where([common_key.startswith(key) for key in common_key_array])[0]
        if len(matching_indices) > 0:
            matched_key = common_key_array[matching_indices[0]]
            print("matched key", matched_key)

            token_info.update(token_verified_info[matched_key])
            token_info["policy-token"] = f"{matched_key}-{name_value}"
            token_info["verified"] = True
        else:
            print("No matching key found for", common_key)

        token_info_dict[token_key] = token_info

    with solara.VBox() as main:
        df = pd.DataFrame.from_dict(token_info_dict, orient="index")

        # here do not work because of the index from table not match to original index
        df = df.sort_values(by=["verified", "ticker"], ascending=[False, True])

        df = df.reset_index(drop=True)

        # df["icon"] = df["icon"].apply(load_icon)
        # TODO render icon
        # df["icon"] = df["icon"].apply(render_html)

        # for now drop icon
        df = df.drop(columns=['icon'])

        df["categories"] = df["categories"].apply(lambda x: ', '.join(x))
        df = df.rename(columns={'verified': 'verified by minswap'})
        df["socialLinks"] = df["socialLinks"].apply(format_links)

        with solara.Div(
                style={
                    "paddingBottom": "20px",
                },
            ):
            TableCard(df)
            
        DropdownCard(df)

        with solara.Div(
                style={
                    "paddingTop": "20px",
                },
            ):
            SummaryCard(df)

        return main

    
