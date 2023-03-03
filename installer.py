import os, subprocess, sys, shutil
from zipfile import ZipFile

path_to_ndstool = "ndstool"

path_to_roms = "roms"

try:
    os.remove(path_to_roms + "/" + "Dragon Quest IV English Party Chat Patched.nds")
except:
    pass

regions = ["us", "ja"]

roms = {"us" : "none",
        "ja" : "none"}

obb = "none"

for i in os.listdir("roms"):
    if i.endswith(".nds"):
        rom = subprocess.run("ndstool -i " + path_to_roms + "/" + i, shell=True, stdout=subprocess.PIPE)

        if "YIVE (NTR-YIVE-USA)" in str(rom.stdout):
            roms["us"] = path_to_roms + "/" + i
        elif "YIVJ (NTR-YIVJ-JPN)" in str(rom.stdout):
            roms["ja"] = path_to_roms + "/" + i
    elif i.endswith(".obb"):
        obb = i

for i in regions:
    if os.path.exists(path_to_roms + "/" + i):
        shutil.rmtree(path_to_roms + "/" + i)
        pass

for i in roms:
    if roms[i] == "none":
        print("Please provide a " + i + " DQIV rom in the roms folder.")
        sys.exit(1)

if obb == "none":
    print("Please provide a DQIV android .obb file in the roms folder.")
    sys.exit(1)

def extract_roms(regions: list):
    for i in regions:
        path_to_region_folder = path_to_roms + "/" + i
        if os.path.exists(path_to_region_folder) == False:
            os.makedirs(path_to_region_folder)

            print("Extracting " + i + " rom...")
            subprocess.run(path_to_ndstool + " -x " + roms[i] + " -9 " + path_to_region_folder + "/arm9.bin -7 " + path_to_region_folder + "/arm7.bin -y9 " + path_to_region_folder + "/y9.bin -y7 " + path_to_region_folder + "/y7.bin -t " + path_to_region_folder + "/banner.bin -h " + path_to_region_folder + "/header.bin -d " + path_to_region_folder + "/data -y " + path_to_region_folder + "/overlay ", shell=True, stdout=subprocess.PIPE)
            print("Extraction of " + i + " rom complete.")

    path_to_en_ds_files = path_to_roms + "/" + \
    "us" + "/data/data/MESS/en"
    for i in os.listdir(path_to_en_ds_files):
        shutil.copy(path_to_en_ds_files + "/" + i, "en/" + i)

    mpt_list = ['assets/msg/en/b0500000.mpt', 'assets/msg/en/b0501000.mpt', 'assets/msg/en/b0502000.mpt', 'assets/msg/en/b0503000.mpt', 'assets/msg/en/b0504000.mpt', 'assets/msg/en/b0505000.mpt', 'assets/msg/en/b0506000.mpt', 'assets/msg/en/b0507000.mpt', 'assets/msg/en/b0508000.mpt', 'assets/msg/en/b0509000.mpt', 'assets/msg/en/b0512000.mpt', 'assets/msg/en/b0513000.mpt', 'assets/msg/en/b0516000.mpt', 'assets/msg/en/b0517000.mpt', 'assets/msg/en/b0520000.mpt', 'assets/msg/en/b0521000.mpt', 'assets/msg/en/b0522000.mpt', 'assets/msg/en/b0523000.mpt', 'assets/msg/en/b0524000.mpt', 'assets/msg/en/b0525000.mpt', 'assets/msg/en/b0526000.mpt', 'assets/msg/en/b0527000.mpt', 'assets/msg/en/b0528000.mpt',
            'assets/msg/en/b0529000.mpt', 'assets/msg/en/b0530000.mpt', 'assets/msg/en/b0531000.mpt', 'assets/msg/en/b0532000.mpt', 'assets/msg/en/b0533000.mpt', 'assets/msg/en/b0534000.mpt', 'assets/msg/en/b0535000.mpt', 'assets/msg/en/b0536000.mpt', 'assets/msg/en/b0537000.mpt', 'assets/msg/en/b0538000.mpt', 'assets/msg/en/b0539000.mpt', 'assets/msg/en/b0540000.mpt', 'assets/msg/en/b0541000.mpt', 'assets/msg/en/b0542000.mpt', 'assets/msg/en/b0543000.mpt', 'assets/msg/en/b0544000.mpt', 'assets/msg/en/b0545000.mpt', 'assets/msg/en/b0547000.mpt', 'assets/msg/en/b0548000.mpt', 'assets/msg/en/b0549000.mpt', 'assets/msg/en/b0550000.mpt', 'assets/msg/en/b0551000.mpt', 'assets/msg/en/b0552000.mpt']

    print("Extracting files from obb...")

    for i in mpt_list:
        with ZipFile(path_to_roms + "/" + obb, 'r') as zObject:
            zObject.extract(i, path="en/")
            os.rename("en/" + i, "en/" + i.split("assets/msg/en/")[1])

    print("Extraction of obb files complete.")
    
    shutil.rmtree("en/assets")

extract_roms(regions)

command = "python3 dqiv_patch.py --lang ja"

subprocess.run(command, shell=True)

def repack(mode_lang : str):
    
    path = path_to_roms + "/" + "repack" + "/data/data/MESS/" + mode_lang

    shutil.copytree(path_to_roms + "/" + "ja", path_to_roms + "/" + "repack")

    path_to_repack = path_to_roms + "/" + "repack"

    for i in os.listdir(path):
        os.remove(path + "/" + i)
    for i in os.listdir("out/" + mode_lang):
        os.rename("out/" + mode_lang + "/" + i, path + "/" + i)
    
    path_to_repack = path_to_roms + "/" + "repack"

    print("Repacking rom...")
    repacking = subprocess.run(path_to_ndstool + " -c \"" + path_to_roms + "/" + "Dragon Quest IV English Party Chat Patched.nds\"" + " -9 " + path_to_repack + "/arm9.bin -7 " + path_to_repack + "/arm7.bin -y9 " + path_to_repack + "/y9.bin -y7 " +
                   path_to_repack + "/y7.bin -t " + path_to_repack + "/banner.bin -h " + path_to_repack + "/header.bin -d " + path_to_repack + "/data -y " + path_to_repack + "/overlay ", shell=True, stdout=subprocess.PIPE)
    print("Rom repacked!")

    shutil.rmtree(path_to_repack)

repack(mode_lang="ja")