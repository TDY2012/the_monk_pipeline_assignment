---------------------------------------------------
Attached files for the assignment
---------------------------------------------------
    1. "pack_image_cmp.py" python script
    2. "INTERNAL" folder: Assume that this is a Monk's internal folder
    3. "OUTPUT_EX1" folder: output folder/files we expect for Instruction > I1
    4. "OUTPUT_EX1.txt" : command and output we expect for Instruction > I1
    5. "OUTPUT_EX2" folder: output folder/files we expect for Instruction > I2
    6. "OUTPUT_EX2.txt" : command and output we expect for Instruction > I2


---------------------------------------------------
Code description for pack_image_cmd.py
---------------------------------------------------
The script is used for copying .exr image files ONLY, from INTERNAL_DIR to OUTPUT_DIR, depending on the input added from the command (-o : an output dir, -sc : a scene name)

    - copy ONLY .exr files inside
    - keep the same structure when copy to, just change the source directory
    - be able to overwrite existing output files

e.g.

    your folder location <root>:
        C:/workspace/test

    command:
        python pack_image_cmp.py -scene sq0700 -o C:/workspace/test/OUTPUT_TEST

    - from the command, the inputs are
        scene name: sq0700
        OUTPUT_DIR: C:/workspace/test/OUTPUT_TEST
    - INTERNAL_DIR: C:/workspace/test/INTERNAL

    the process when running the command:
        - copy .exr image sequence from the scene folder 'sq0700' only
            <latest version> : the first character must be "v" followed by 3 digits (e.g. v045, v003)

            copy from
                INTERNAL_DIR/img/nine/sq0700/11000/Master_cmp/<latest version>.r2048x858.exr/<all exr files in folder>
            to
                OUTPUT_DIR/img/nine/sq0700/11000/Master_cmp/<latest version>.r2048x858.exr/<all exr file in folder>


---------------------------------------------------
Instructions
---------------------------------------------------

The script was developed on Python 2 but it would be good if the candidate can continually develop on Python 3,
depending on the python version installed on your machine.


I1. Refactor and Fix bug: Suppose that you get the assignment to refactor/fix the script named "pack_cmp_image.py"
    ***see command and output example in "OUTPUT_EX1.txt" and "OUTPUT_EX1" folder***

    1.1 try testing this code. If you think this code is messy or works incorrectly, modify and save as a new file named "pack_image_cmd_v02.py"
    1.2 commenting in the code why you're modifying will be appreciated

I2. Add the new features from the modified code from 1. ( "pack_image_cmd_v02.py") and save as ("pack_image_cmd_v03.py")

Implement them in the order that suits you, depending on time and feasibility. Feel free to version the progression using git if you want (this is optional).

    ***see expected command and output example in "OUTPUT_EX2.txt" and "OUTPUT_EX2" folder***

    3.1 new feature1: be able to input more than one scene name like this

        pack_cmp_img.py -scene sq0500 sq0600 -o /toClient/tmp/workspace/misc/recruit/toClient

    3.2 new feature2: copy only .tif files from the Matte folder with the pattern as follows  (HINT: can use regular expression https://docs.python.org/3/library/re.html)

        Matte folder pattern: /img/nine/<scene_name>/<shot_name>/Master_cmp/<version>.r2048x858.<matte>.tif
        <version> : the first character must be "v" followed by 3 digits (e.g. v045, v003)
        <matte> : contains only the English alphabets with upper or lower case (a-z, A-Z), underscore (_) and digits (0-9)

    3.3 new feature3: increment version number by one from the version of an original folder, such as increment from v044 to v045


    e.g. : final images
        copy exr files from:
            INTERNAL_DIR/img/nine/sq0700/11000/Master_cmp/
                v044.r2048x858.exr
        to
            OUTPUT_DIR/img/nine/sq0700/11000/Master_cmp/
                v045.r2048x858.monkey_02.exr

    e.g. : matte images
        copy tif files from:
            INTERNAL_DIR/img/nine/sq0700/11000/Master_cmp/
                v044.r2048x858.monkey_02.tif
                v045.r2048x858.catA.tif
                v043.r2048x858.Bg.tif
                v044.r2048x858.EFX_candle.tif
                v005.r2048x858.tv005.tif
        to
            OUTPUT_DIR/img/nine/sq0700/11000/Master_cmp/
                v045.r2048x858.monkey_02.tif
                v046.r2048x858.catA.tif
                v044.r2048x858.Bg.tif
                v045.r2048x858.EFX_candle.tif
                v006.r2048x858.tv005.tif
