import metadata

################################################################################
# For fanatic NFT.
################################################################################

# Output directory to where all metadata files generated and saved.
# The tail "/" should be added.
output_dir = "./build/json/"

# Metadata JSON structure
# https://docs.opensea.io/docs/metadata-standards
nft_name = "Fanatic NFT"
nft_symbol = "FNT"
nft_description = "Fanatic NFT"
# The tail "/" should be added.
nft_image_url = "https://fanatic-nft.s3.ap-northeast-2.amazonaws.com/image/"
# The tail "/" should be added.
nft_glb_url = "https://fanatic-nft.s3.ap-northeast-2.amazonaws.com/glb/"
# The tail "/" should be added.
nft_vrm_url = "https://fanatic-nft.s3.ap-northeast-2.amazonaws.com/vrm/"

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

# * For hair.
# list_hair = [
#     "pinkblond", "purplelong", "short", "twintail"
# ]
list_hair = [
    "none"
]

# * For face.
list_face = [
    "face"
]

# * For face accessories.
# list_top = [
#     "angle", "sunstrawhat"
# ]
# list_middle = [
#     "alien", "round"
# ]
# list_side = [
#     "crown", "sunflower"
# ]
# list_bottom = [
#     "candy", "rose"
# ]
list_top = [
    "none"
]
list_middle = [
    "none"
]
list_side = [
    "none"
]
list_bottom = [
    "none"
]

# * For body.
list_body = [
    "girl"
]

# * For body clothes.
list_body_top = [
    "blazer", "blazerpink", "bluecloud", "cowcatsuit",
    "downjacket", "school", "snow", "sunsmile", "sweater", "whitecloud"
]
# list_body_top = [
#     "bluecloud"
# ]
list_body_bottom = [
    "chino", "chinobeige", "cowcatsuit", "jeans", "jeanschain", "jeanssky",
    "khaki", "school", "shorts", "shortscotton"
]
# list_body_bottom = [
#     "chino"
# ]

metadata.generate_metadata(
    output_dir, nft_name, nft_symbol, nft_description, nft_image_url,
    nft_glb_url, nft_vrm_url, list_hair, list_face, list_top, list_middle,
    list_side, list_bottom, list_body, list_body_top, list_body_bottom,
    list_background)
