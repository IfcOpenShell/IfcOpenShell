# the SVG_FILE should be the file that contains all the icons (each icon should be in a unique layer group, and colored for dark mode)
# the EXPORT_FOLDER is where the png files get exported to
# the script will export dark mode version and modify colors for a light mode verion
# requires inkscape to run
# to run on mac: python3 generate_png_icons.py

import os
import subprocess
import xml.etree.ElementTree as ET
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SVG_FILE = os.path.join(SCRIPT_DIR, "bonsai_icons.svg")
EXPORT_FOLDER = os.path.join(SCRIPT_DIR, "..", "bonsai", "bim", "data", "icons")

overwrite_all = False
skip_all = False


def dark_to_light(svg_content):
    svg_content = re.sub(r"#ffffff", "#434343", svg_content, flags=re.IGNORECASE)  # white to drak grey

    svg_content = re.sub(r"#00d27b", "#009d5c", svg_content, flags=re.IGNORECASE)  # make green darker
    svg_content = re.sub(r"#009a5f", "#00663f", svg_content, flags=re.IGNORECASE)  # make dark green darker
    svg_content = re.sub(r"#75ffaf", "#3dff8f", svg_content, flags=re.IGNORECASE)  # make light green darker

    svg_content = re.sub(r"#cce3ff", "#3391ff", svg_content, flags=re.IGNORECASE)  # make blue darker
    svg_content = re.sub(r"#4c9fff", "#005fcc", svg_content, flags=re.IGNORECASE)  # make dark blue darker
    svg_content = re.sub(r"#c9e0ff", "#80b8ff", svg_content, flags=re.IGNORECASE)  # make light blue darker

    return svg_content


def prompt_overwrite(file_path, png_name):
    global overwrite_all, skip_all

    if skip_all and os.path.exists(file_path):
        return "n"

    if overwrite_all:
        return "y"

    if os.path.exists(file_path):
        while True:
            response = (
                input(
                    f"File '{png_name}' already exists.\nOverwrite? (Enter = yes, s = skip, y = yes all, n = no all): "
                )
                .strip()
                .lower()
            )
            if response in {"", "y", "n", "s"}:
                if response == "y":
                    overwrite_all = True
                elif response == "n":
                    skip_all = True
                return response
            else:
                print("Invalid option. Please enter Enter, y, n, or s.")
    return ""


def export_svg_group(group_content, group_label, mode, output_folder):
    temp_svg_file = os.path.join(output_folder, f"{group_label}_{mode}.svg")
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"
    width="31.999998" height="31.999998" viewBox="0 0 8.4666661 8.4666661">
    {group_content}
    </svg>"""

    with open(temp_svg_file, "w") as file:
        file.write(svg_content)

    png_name = f"{mode}_{group_label}.png"
    output_png_file = os.path.join(output_folder, png_name)

    user_choice = prompt_overwrite(output_png_file, png_name)

    if user_choice in {"y", ""}:
        subprocess.run(["inkscape", temp_svg_file, "--export-type=png", "--export-filename=" + output_png_file])
        print(f"\033[32mExported PNG file: {output_png_file}\033[0m")

    elif user_choice == "n":
        print(f"Skipping {png_name}")

    elif user_choice == "s":
        print(f"Skipped exporting {output_png_file}.")

    os.remove(temp_svg_file)


def export_svg_groups_to_png(svg_file, output_folder):
    tree = ET.parse(svg_file)
    root = tree.getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}

    for group in root.findall(".//svg:g", ns):
        group_label = group.get("{http://www.inkscape.org/namespaces/inkscape}label")
        if not group_label:
            continue

        style = group.get("style", "")
        if "display:none" in style:
            style = style.replace("display:none", "display:inline")
        elif "display" not in style:
            style += ";display:inline"
        group.set("style", style)

        group_content = ET.tostring(group, encoding="unicode", method="xml")
        export_svg_group(group_content, group_label, "dm", output_folder)
        light_mode_svg = dark_to_light(group_content)
        export_svg_group(light_mode_svg, group_label, "lm", output_folder)


if __name__ == "__main__":
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    export_svg_groups_to_png(SVG_FILE, EXPORT_FOLDER)
