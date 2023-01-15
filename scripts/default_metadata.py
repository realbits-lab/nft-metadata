import metadata

################################################################################
# For default vrm model for avame.
################################################################################

# Output directory to where all metadata files generated and saved.
# The tail "/" should be added.
output_dir = "./build/json/"

# Metadata JSON structure
# https://docs.opensea.io/docs/metadata-standards
nft_name = "Default Avame Avatar"
nft_symbol = "DAA"
nft_description = "Default avame avatar for realbits"

# * We don't use these url. Url is unavailable.
# The tail "/" should be added.
nft_image_url = "https://default-nft.s3.ap-northeast-2.amazonaws.com/image/"
# The tail "/" should be added.
nft_glb_url = "https://default-nft.s3.ap-northeast-2.amazonaws.com/glb/"
# The tail "/" should be added.
nft_vrm_url = "https://default-nft.s3.ap-northeast-2.amazonaws.com/vrm/"

# For background.
list_background = [
    "white"
]

# For hair.
list_hair = [
    "none"
]

# For face.
list_face = [
    "dull",
]

# For face accessories.
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

# For body.
list_body = [
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
    "body", output_dir, nft_name, nft_symbol, nft_description, nft_image_url,
    nft_glb_url, nft_vrm_url, list_hair, list_face, list_top, list_middle,
    list_side, list_bottom, list_body, list_body_top, list_body_bottom,
    list_background)
