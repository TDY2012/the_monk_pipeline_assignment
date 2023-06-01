#!/usr/bin/env python


import argparse
import datetime
import glob
import logging
import os
import sys
import re
import json
import shutil


# FOR CANDIDATE: suggestion: copy "INTERNAL" folder to the same directory with this script
#   The command os.path.join is preferred when concatenating the file path
#   because the delimiter of a file path is different across operating systems.
INTERNAL_DIR = os.path.join(os.path.dirname(__file__), "INTERNAL")
INTERNAL_DIR = os.path.normpath(INTERNAL_DIR)

# FOR CANDIDATE: DO NOT MODIFY THESE VARIABLE
MNK_IMG_DIR = "img"
RES_WIDTH = "2048"
RES_HEIGHT = "858"

def pack_images(scene_data_dict):
    """
    copy the latest final images of all shots contained in the input scene

    Args:

    - *scene_data_dict* (dict):
        Example:
            {
                "job_name": "nine",
                "class_name": "cmp",
                "element_name": "Master",
                "scene_list": "sq0100",
                "output_dir": "/proj/nine/for_DI/20220412",
                "test_mode": False
            }

    """

    job_name = scene_data_dict.get("job_name", "")
    class_name = scene_data_dict.get("class_name", "")
    element_name = scene_data_dict.get("element_name", "")
    input_scene_name = scene_data_dict.get("scene_name", "")
    output_dir = scene_data_dict.get("output_dir", "")
    is_test = scene_data_dict.get("test_mode", False)

    #   An output directory should be normalized here just once.
    output_dir = os.path.normpath(output_dir)

    element_class = "{}_{}".format(element_name, class_name)
    resolution = "r{w}x{h}".format(w=RES_WIDTH, h=RES_HEIGHT)

    failed_list = []

    if not os.path.exists(output_dir):
        print("!! output directory not found : {}".format(output_dir))
        failed_list.append(
            {
                "scene": input_scene_name, "shot": "",
                "message": "output directory not found",
            }
        )
        return

    # FOR CANDIDATE: DO NOT MODIFY THIS JOB DIRECTORY, ITS PATTERN IS ALWAYS "/img/nine"
    job_dir = os.path.join(INTERNAL_DIR, MNK_IMG_DIR, job_name)

    #   Define a scene directory variable here for clarity.
    scene_dir = os.path.normpath(os.path.join(job_dir, input_scene_name))

    output_list = []
    latest_final_image_dir_list = []

    #   We will use a base shot directory name again and there is no
    #   restriction on a shot naming convention. Just use os.listdir.
    shot_name_list = os.listdir(scene_dir)

    for shot_name in shot_name_list:

        #   For clarity and reusability sake.
        element_dir = os.path.join(
            scene_dir,
            shot_name,
            element_class,
        )

        # get all final image (exr) directories
        # /img/nine/sq0700/12000/Master_cmp/v010.r2048x858.exr/sq0700_12000.Master_cmp.1003.exr
        final_image_list = glob.glob(
            os.path.join(
                element_dir,
                "v[0-9][0-9][0-9].{res}.exr".format(res=resolution),
            )
        )

        if not final_image_list:

            #   A scene name is unchanged and we have already got a shot name.
            #   No need to extract them from the final image directory again.
            print(
                "!! not found any image of shot {}_{}".format(input_scene_name, shot_name)
            )
            failed_list.append(
                {
                    "scene": input_scene_name,
                    "shot": shot_name,
                    "message": "image not found",
                }
            )
            continue

        # get latest version of final image
        latest_final_image_dir_list.append(max(final_image_list))

        #   Since glob cannot match a variable length string,
        #   I decided to use regex instead.
        final_matte_image_name_list = os.listdir(element_dir)

        matte_name_to_final_matte_image_dict = dict()

        for final_matte_image_name in final_matte_image_name_list:

            #   Match each matte image name with the predefined pattern.
            final_matte_image_name_matching = re.match(
                "^v[0-9][0-9][0-9].{res}.(?P<matte>\w+)\.tif$".format(res=resolution),
                final_matte_image_name
            )

            #   Store only latest version for each matte name.
            if final_matte_image_name_matching:
                matte_name = final_matte_image_name_matching.group("matte")

                if matte_name not in matte_name_to_final_matte_image_dict.keys() or matte_name_to_final_matte_image_dict[matte_name] < final_matte_image_name:
                    matte_name_to_final_matte_image_dict[matte_name] = final_matte_image_name

        if not matte_name_to_final_matte_image_dict:
            print(
                "!! not found any matte image of shot {}_{}".format(input_scene_name, shot_name)
            )
            failed_list.append(
                {
                    "scene": input_scene_name,
                    "shot": shot_name,
                    "message": "matte image not found",
                }
            )
            continue

        final_matte_image_list = [
            os.path.join(element_dir, final_matte_image)
            for final_matte_image in matte_name_to_final_matte_image_dict.values()
        ]

        # get latest version of final matte image
        latest_final_image_dir_list.extend(final_matte_image_list)

    for latest_final_image_dir in latest_final_image_dir_list:
        latest_final_image_dir = os.path.normpath(latest_final_image_dir)

        #   NOTE: This is quite dangerous. I suggested we should construct a
        #   new output directory from parts instead of this substitution technique.
        output_image_dir = latest_final_image_dir.replace(INTERNAL_DIR, output_dir)

        print("## source      : {}".format(latest_final_image_dir))
        print("## destination : {}\n".format(output_image_dir))

        #   Make sure the output directory exists.
        os.makedirs(output_image_dir, exist_ok=True)

        if not is_test:

            #   Copy only .exr files instead of an entire folder.
            latest_final_image_file_list = glob.glob(
                os.path.join(
                    latest_final_image_dir,
                    "*.exr",
                )
            )

            #   Now, include .tif files.
            latest_final_image_file_list.extend(
                glob.glob(
                    os.path.join(
                        latest_final_image_dir,
                        "*.tif",
                    )
                )
            )

            for latest_final_image_file in latest_final_image_file_list:
                shutil.copy2(latest_final_image_file, output_image_dir)

        output_list.append(output_image_dir)

    # summary
    if failed_list:
        print("\n##=================ERROR: Scene/Shot=================")

        #   NOTE:   Some versions of Python does not support a
        #           traditional dictionary sorting.
        for failed_item in sorted(failed_list, key=lambda x: x["scene"]):
            print(
                "{scene}{separator}{shot}: {message}".format(
                    scene=failed_item.get("scene", ""),
                    separator="_" if failed_item.get("shot", "") else "",
                    shot=failed_item.get("shot", ""),
                    message=failed_item.get("message", ""),
                )
            )

    print("\n###=================FINISH=================")
    for out_file in sorted(output_list):
        print(out_file)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="pack_image_cmp.py",
        description=(
            "pack exr and matte image sequence\n"
            "command example: python pack_cmp_img.py -scene sq0500 -o /directory/OUT"
        ),
    )

    parser.add_argument(
        "-sc",
        "-scene",
        dest="scene_name_list",
        required=True,
        nargs='+',
        help="a scene name ex. -scene sq0100",
    )

    parser.add_argument(
        "-o",
        "-output_dir",
        dest="output_dir",
        required=True,
        default="",
        help="output directory",
    )

    parser.add_argument(
        "-t",
        "-test",
        dest="is_test_mode",
        action="store_true",
        help="test mode (do not copy any file)",
    )

    args = parser.parse_args()

    for scene_name in args.scene_name_list:
        pack_image_dict = {
            "job_name": "nine",
            "class_name": "cmp",
            "element_name": "Master",
            "scene_name": scene_name,
            "output_dir": args.output_dir,
            "test_mode": args.is_test_mode,
        }
        pack_images(pack_image_dict)
