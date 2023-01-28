import json
import os
from os import path
import random
import re
import shutil


def get_random_background_attribute(list_background):
    random_background = random.choice(list_background)

    attr = {
        "trait_type": "Background",
        "value": random_background
    }

    return attr


def generate_metadata(
        body_mode, output_dir, nft_name, nft_symbol, nft_description,
        nft_image_url, nft_glb_url, nft_vrm_url, list_hair, list_face, list_top,
        list_middle, list_side, list_bottom, list_body, list_body_top,
        list_body_bottom, list_background):
    ############################################################################
    # Check output directory exists.
    ############################################################################
    if path.exists(output_dir) == False:
        print(
            f"ERROR: Output directory({output_dir}) does not exist. We will make it.")
        # Make output_dir directory.
        os.makedirs(output_dir, exist_ok=True)

    ###########################################################################
    # Remove all files in json output directory.
    ###########################################################################
    for f in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, f))

    print("Start generating metadata ...")

    # Create content list.
    content_list = []

    ###########################################################################
    # Make all-permutated metadata.
    ###########################################################################
    for hair_element in list_hair:
        for face_element in list_face:
            for top_element in list_top:
                for middle_element in list_middle:
                    for side_element in list_side:
                        for bottom_element in list_bottom:
                            for body_element in list_body:
                                for body_top_element in list_body_top:
                                    for body_bottom_element in list_body_bottom:
                                        attributes = []

                                        if hair_element != "none":
                                            attributes.append(
                                                {"trait_type": "Hair",
                                                 "value": hair_element},
                                            )
                                        if face_element != "none":
                                            attributes.append(
                                                {"trait_type": "Face",
                                                 "value": face_element},
                                            )
                                        if top_element != "none":
                                            attributes.append(
                                                {"trait_type": "Top",
                                                 "value": top_element},
                                            )
                                        if middle_element != "none":
                                            attributes.append(
                                                {"trait_type": "Middle",
                                                 "value": middle_element},
                                            )
                                        if side_element != "none":
                                            attributes.append(
                                                {"trait_type": "Side",
                                                 "value": side_element},
                                            )
                                        if bottom_element != "none":
                                            attributes.append(
                                                {"trait_type": "Bottom",
                                                 "value": bottom_element},
                                            )
                                        if body_element != "none":
                                            attributes.append(
                                                {"trait_type": "Body",
                                                 "value": body_element},
                                            )
                                        if body_top_element != "none":
                                            attributes.append(
                                                {"trait_type": "Body_Top",
                                                 "value": body_top_element},
                                            )
                                        if body_bottom_element != "none":
                                            attributes.append(
                                                {"trait_type": "Body_Bottom",
                                                 "value": body_bottom_element}
                                            )

                                        attribute = {
                                            "attributes": attributes
                                        }

                                        # Add random selected background.
                                        background_attribute = get_random_background_attribute(
                                            list_background)
                                        attribute["attributes"].append(
                                            background_attribute)

                                        content_list.append(attribute)

    ###########################################################################
    # Create metadata.
    ###########################################################################
    # TODO: Check the tail "/" of url and path, and if not, add the tail "/".
    for i, content in enumerate(content_list):
        # Make token id should start from 1 with i+1.
        token_id = str(i + 1)

        obj = {
            "name": f"{nft_name} #{token_id}",
            "symbol": nft_symbol,
            "description": nft_description,
            "image": f"{nft_image_url}{token_id}.png",
            "realbits": {
                "glb_url": f"{nft_glb_url}{token_id}.glb",
                "vrm_url": f"{nft_vrm_url}{token_id}.vrm"
            },
            "attributes": content["attributes"]
        }

        # Write json metadata file.
        output_filename = f"{output_dir}{token_id}"
        with open(output_filename, "w") as outjson:
            json.dump(obj, outjson, indent=4)

        print(f"nft id: {token_id}")

    print("Done.")
