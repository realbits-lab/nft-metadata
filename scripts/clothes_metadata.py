import metadata

################################################################################
# For clothes NFT.
################################################################################

# Output directory to where all metadata files generated and saved.
# The tail "/" should be added.
output_dir = "../build/json/"

# Metadata JSON structure
# https://docs.opensea.io/docs/metadata-standards
nft_name = "testNFT"
nft_symbol = "TNT"
nft_description = "testNFT for realbits"
# The tail "/" should be added.
nft_image_url = "https://js-nft.s3.ap-northeast-2.amazonaws.com/image/"
# The tail "/" should be added.
nft_glb_url = "https://js-nft.s3.ap-northeast-2.amazonaws.com/glb/"
# The tail "/" should be added.
nft_vrm_url = "https://js-nft.s3.ap-northeast-2.amazonaws.com/vrm/"

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
    "angel", "devel", "flower", "hairband", "sprout"
]
list_middle = [
    "aviator", "cheek", "goggle", "mole", "smart", "thuglife"
]
list_side = [
    "bigring", "earphones", "headset", "pearlear", "pencil", "piercing"
]
list_bottom = [
    "bowtie", "candy", "cat", "goldchain", "mask", "mustache", "pearl"
]

# For body.
list_body = [
    "casual"
]

# For body clothes.
list_body_top = [
    "none",
]
list_body_bottom = [
    "none"
]

metadata.generate_metadata(
    "body_bottom", output_dir, nft_name, nft_symbol, nft_description,
    nft_image_url, nft_glb_url, nft_vrm_url, list_hair, list_face, list_top,
    list_middle, list_side, list_bottom, list_body, list_body_top,
    list_body_bottom, list_background)
