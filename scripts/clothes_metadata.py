import metadata

################################################################################
# For clothes NFT.
################################################################################

# Output directory to where all metadata files generated and saved.
# The tail "/" should be added.
output_dir = "./build/json/"

# Metadata JSON structure
# https://docs.opensea.io/docs/metadata-standards
nft_name = "Clothes NFT"
nft_symbol = "CNT"
nft_description = "For people who like clothes."
# The tail "/" should be added.
nft_image_url = "https://clothes-nft.s3.ap-northeast-2.amazonaws.com/image/"
# The tail "/" should be added.
nft_glb_url = "https://clothes-nft.s3.ap-northeast-2.amazonaws.com/glb/"
# The tail "/" should be added.
nft_vrm_url = "https://clothes-nft.s3.ap-northeast-2.amazonaws.com/vrm/"

# For background.
list_background = [
    "berry",
    "black",
    "blue",
    "hotpink",
    "laim",
    "lemon",
    "mint",
    "olive",
    "orange",
    "pink",
    "red",
    "skyblue",
    "white"
]

# For hair.
list_hair = [
    "none",
]

# For face.
list_face = [
    "none",
]

# For face accessories.
list_top = [
    # "1", "2",
    "none",
]
list_middle = [
    "none",
]
list_side = [
    "none",
]
list_bottom = [
    # "1", "2",
    "none",
]

# For body.
list_body = [
    # "1", "2",
    "1",
]

# For body clothes.
# list_body_top = ["1", "2", "3", "4", "5", "6", "7",
#                  "8", "9", "10", "11", "12", "13", "14", "15", ]
list_body_top = ["1", ]

list_body_bottom = ["1", "2", "3", "4", "5", "6", "7",
                    "8", "9", "10", "11", "12", "13", "14", "15", ]
# list_body_bottom = ["1", ]

metadata.generate_metadata(
    output_dir, nft_name, nft_symbol, nft_description, nft_image_url,
    nft_glb_url, nft_vrm_url, list_hair, list_face, list_top, list_middle,
    list_side, list_bottom, list_body, list_body_top, list_body_bottom,
    list_background)
