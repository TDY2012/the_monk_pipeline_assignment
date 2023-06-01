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
INTERNAL_DIR = os.path.dirname(__file__) + "/INTERNAL"
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

    element_class = "{}_{}".format(element_name, class_name)
    resolution = "r{w}x{h}".format(w=RES_WIDTH, h=RES_HEIGHT)

    failed_list = []

    if not os.path.exists(output_dir):
        print("!! directory not found : {}".format(output_dir))
        failed_list.append(
            {"scene": input_scene_name, "shot": "", "message": "directory not found",}
        )
        return

    # FOR CANDIDATE: DO NOT MODIFY THIS JOB DIRECTORY, ITS PATTERN IS ALWAYS "/img/nine"
    job_dir = os.path.join(INTERNAL_DIR, MNK_IMG_DIR, job_name)

    output_list = []
    latest_final_image_dir_list = []

    shot_dir_list = glob.glob(
        os.path.join(job_dir, input_scene_name, "*",).replace("\\", "/")
    )
    for shot_dir in shot_dir_list:

        # get all final image (exr) directories
        # /img/nine/sq0700/12000/Master_cmp/v010.r2048x858.exr/sq0700_12000.Master_cmp.1003.exr
        final_image_list = glob.glob(
            os.path.join(
                shot_dir,
                element_class,
                "v[0-9][0-9][0-9].{res}.exr".format(res=resolution),
            )
        )

        if not final_image_list:
            scene_shot_re = re.search("(sq[0-9]{4})/([0-9]{5})$", shot_dir)
            if scene_shot_re:
                scene_name = scene_shot_re.group(1)
                shot_name = scene_shot_re.group(2)
                print(
                    "!! not found any image of shot {}_{}".format(scene_name, shot_name)
                )
                failed_list.append(
                    {
                        "scene": scene_name,
                        "shot": shot_name,
                        "message": "image not found",
                    }
                )
            continue

        # get latest version of final image
        latest_final_image_dir_list.append(max(final_image_list))

    for latest_final_image_dir in latest_final_image_dir_list:
        latest_final_image_dir = os.path.normpath(latest_final_image_dir)
        output_dir = os.path.normpath(output_dir)
        output_image_dir = latest_final_image_dir.replace(INTERNAL_DIR, output_dir)

        print("## source      : {}".format(latest_final_image_dir))
        print("## destination : {}\n".format(output_image_dir))

        if not is_test:
            shutil.copytree(latest_final_image_dir, output_image_dir)

        output_list.append(output_image_dir)

    # summary
    if failed_list:
        print("\n##=================ERROR: Scene/Shot=================")
        for failed_item in sorted(failed_list):
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
        dest="scene_name",
        required=True,
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

    pack_image_dict = {
        "job_name": "nine",
        "class_name": "cmp",
        "element_name": "Master",
        "scene_name": args.scene_name,
        "output_dir": args.output_dir,
        "test_mode": args.is_test_mode,
    }
    pack_images(pack_image_dict)
