import metadata

################################################################################
# For Dulls NFT.
################################################################################

# Output directory to where all metadata files generated and saved.
# The tail "/" should be added.
output_dir = "./build/json/"

# Metadata JSON structure
# https://docs.opensea.io/docs/metadata-standards
nft_name = "Dulls"
nft_symbol = "DLL"
nft_description = "Dulls NFT project for realbits"

# NFT token base uri
# https://dulls-nft.s3.ap-northeast-2.amazonaws.com/json/

# The tail "/" should be added.
nft_image_url = "https://dulls-nft.s3.ap-northeast-2.amazonaws.com/image/"
# The tail "/" should be added.
nft_glb_url = "https://dulls-nft.s3.ap-northeast-2.amazonaws.com/glb/"
# The tail "/" should be added.
nft_vrm_url = "https://dulls-nft.s3.ap-northeast-2.amazonaws.com/vrm/"

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
    "bob", "bubble", "buzz", "hime", "octopus", "pigtail"
]

# For face.
list_face = [
    "dull",
]

# For face accessories.
list_top = [
    "angel", "devil", "flower", "hairband", "sprout"
]
list_middle = [
    "aviator", "cheek", "goggle", "mole", "smart", "thuglife"
]
list_side = [
    "bigring", "headset", "pearlear", "pencil", "piercing"
]
list_bottom = [
    "bowtie", "candy", "cat", "goldchain", "mask", "mustache", "pearl"
]

# For body.
list_body = [
    # "hoodies", "sweater"
    "hoodies"
]

# For body clothes.
list_body_top = [
    "none",
]
list_body_bottom = [
    "none"
]

metadata.generate_metadata(
    output_dir, nft_name, nft_symbol, nft_description, nft_image_url,
    nft_glb_url, nft_vrm_url, list_hair, list_face, list_top, list_middle,
    list_side, list_bottom, list_body, list_body_top, list_body_bottom,
    list_background)
