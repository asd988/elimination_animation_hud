import os
from PIL import Image
import json
from rectpack import newPacker
import re 

def run_script(
        input_folder,
        input_name_start,
        animation_name,
        output_path,
        frame_rate,
        resource_pack_path,
        provider_path,
        characters,
        identifier_color,
    ):

    rgba = (identifier_color >> 24) & 0xFF, (identifier_color >> 16) & 0xFF, (identifier_color >> 8) & 0xFF, identifier_color & 0xFF

    print(f"""Inputs:
    animation input folder: {input_folder}
    animation_name: {animation_name}
    resource_pack_path: {resource_pack_path}
    output_path: {output_path}
    provider_path: {provider_path}
    {characters = }
    identifier_color: {rgba}
    """)

    og_dim = None

    files: list[tuple[int, str]] = []

    for file in os.listdir(input_folder):
        if file.endswith(".png") and file.startswith(input_name_start):
            
            # last number in the file name is the index
            res = re.findall(r"\d+", file)
            if len(res) == 0:
                continue
            index = int(res[-1])
            file = os.path.join(input_folder, file)
            print(f"index: {index}, file: {file}")

            files.append((index, file))

    files.sort(key=lambda x: x[0])

    file_crops = []
    for _, file in files:
        image = Image.open(file)
        image = image.convert("RGBA")

        top_left     = None # smallest: (0, 0)
        bottom_right = None # largest: (width-1, height-1)

        if og_dim is None:
            og_dim = (image.width, image.height)

        for ix, (r, g, b, a) in enumerate(image.getdata()):
            if a == 0:
                continue
            x, y = ix % image.width, ix // image.width

            if top_left is None:
                top_left = (x, y)
            if bottom_right is None:
                bottom_right = (x, y)

            top_left = (min(top_left[0], x), min(top_left[1], y))
            bottom_right = (max(bottom_right[0], x+1), max(bottom_right[1], y+1))

        file_crops.append((top_left, bottom_right))
            

    cropped: list[tuple[Image.Image, tuple[int, int]]] = []
    cropped_sizes: list[tuple[int, int]] = []
    for (_, file), ((left, top), (right, bottom)) in zip(files, file_crops):
        image = Image.open(file)

        width, height = right - left, bottom - top
        image = image.crop((left, top, right, bottom))

        assert (width, height) == (image.width, image.height), f"cropped image dimensions do not match: {width, height} != {image.width, image.height}"

        cropped.append((image, (left, top)))
        cropped_sizes.append((width, height))

    # pack the images into a spritesheet
    packer = newPacker(rotation=True)
    packer.add_bin(256, 255, count=float("inf"))

    for ix, (width, height) in enumerate(cropped_sizes):
        packer.add_rect(width, height, rid=ix)

    packer.pack()

    bins: list[dict[int, tuple[bool, tuple[int, int]]]] = []
    for abin in packer:
        bin = dict()
        for rect in abin:
            rotated = rect.width != cropped_sizes[rect.rid][0]
            bin[rect.rid] = (rotated, (rect.x, rect.y+1))
        bins.append(bin)

    sheets: list[Image.Image] = []
    bin_owner = [0] * len(cropped)
    for ix, bin in enumerate(bins):
        sheet = Image.new("RGBA", (256, 256))
        for image_ix, (rotated, (x, y)) in bin.items():
            image = cropped[image_ix][0]
            if rotated:
                image = image.transpose(Image.Transpose.ROTATE_90)

            sheet.paste(image, (x, y))

            bin_owner[image_ix] = ix
        
        sheet.putpixel((0, 0), rgba)
        sheet.putpixel((1, 0), (len(files), *og_dim, frame_rate))

        sheets.append(sheet)

    # first row encoding (4 bytes per pixel):
    # 0: identifier
    # 1: (frames, full_width, full_height, frame_rate)
    # 2<=: frame data: (if all 0, then empty frame)
    #   0: (pos_x, pos_y, width, height)
    #   1: (offset_x, offset_y, rotated, ... free space)
    for ix, ((image, (offset_x, offset_y)), bin_ix, (width, height)) in enumerate(zip(cropped, bin_owner, cropped_sizes)):
        sheet = sheets[bin_ix]
        bin = bins[bin_ix]

        rotated = int(bin[ix][0]) * 255
        pos_x, pos_y = bin[ix][1]
        sheet.putpixel((2+ix*2, 0), (pos_x, pos_y, width, height))
        sheet.putpixel((2+ix*2+1, 0), (offset_x, offset_y, rotated, 255))


    out_files = []
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    for ix, sheet in enumerate(sheets):
        file_name = f"{animation_name}_sheet_{ix}.png"
        path = os.path.join(output_path, file_name)
        sheet.save(path)
        out_files.append(file_name)

    providers = []
    for ix, name in enumerate(out_files):
        provider = {
            "type": "bitmap",
            "file": f"{resource_pack_path}/{name}",
            "height": 0,
            "ascent": 0,
            "chars": [
                characters[ix]
            ]
        }
        providers.append(provider)

    with open(provider_path, "w") as f:
        json.dump(providers, f, indent=4)