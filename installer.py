import os, subprocess, sys, shutil
from zipfile import ZipFile

path_to_ndstool = "ndstool"

path_to_roms = "roms"

us_rom_indicator = "us"
ja_rom_indicator = "ja"

regions = [us_rom_indicator, ja_rom_indicator]

roms = {us_rom_indicator : path_to_roms + "/" + us_rom_indicator + ".nds", 
        ja_rom_indicator : path_to_roms + "/" + ja_rom_indicator + ".nds"}

for i in regions:
    if os.path.exists(path_to_roms + "/" + i):
        #shutil.rmtree(path_to_roms + "/" + i)
        pass

for i in roms:
    if os.path.exists(roms[i]) == False:
        print(roms[i] + " must exist. Please provide this file.")
        sys.exit(1)

def extract_roms(regions: list):
    for i in regions:
        path_to_region_folder = path_to_roms + "/" + i
        if os.path.exists(path_to_region_folder) == False:
            os.makedirs(path_to_region_folder)
            subprocess.run(path_to_ndstool + " -x " + roms[i] + " -9 " + path_to_region_folder + "/arm9.bin -7 " + path_to_region_folder + "/arm7.bin -y9 " + path_to_region_folder + "/y9.bin -y7 " + path_to_region_folder + "/y7.bin -t " + path_to_region_folder + "/banner.bin -h " + path_to_region_folder + "/header.bin -d " + path_to_region_folder + "/data -y " + path_to_region_folder + "/overlay ", shell=True)

def repack_roms(regions: list):
   for i in regions:
        path_to_region_folder = path_to_roms + "/" + i
        if os.path.exists(path_to_region_folder) == False:
            os.makedirs(path_to_region_folder)
        subprocess.run(path_to_ndstool + " -c " + path_to_roms + "/" + us_rom_indicator + "copy.nds" + " -9 " + path_to_region_folder + "/arm9.bin -7 " + path_to_region_folder + "/arm7.bin -y9 " + path_to_region_folder + "/y9.bin -y7 " + path_to_region_folder + "/y7.bin -t " + path_to_region_folder + "/banner.bin -h " + path_to_region_folder + "/header.bin -d " + path_to_region_folder + "/data -y " + path_to_region_folder + "/overlay ", shell=True)

#extract_roms(regions)

#repack_roms(regions)
obb = "none"

for i in os.listdir(path_to_roms):
    print(i)
    if i.endswith(".obb"):
        if obb == "none":
            obb = i

if obb == "none":
    print("Please provide a DQIV android .obb file in the roms folder.")
    sys.exit(1)

os.rename(path_to_roms + "/" + obb, path_to_roms + "/" + obb[0:-3] + "zip")

mpt_list = ['assets/msg/en/b0500000.mpt', 'assets/msg/en/b0501000.mpt', 'assets/msg/en/b0502000.mpt', 'assets/msg/en/b0503000.mpt', 'assets/msg/en/b0504000.mpt', 'assets/msg/en/b0505000.mpt', 'assets/msg/en/b0506000.mpt', 'assets/msg/en/b0507000.mpt', 'assets/msg/en/b0508000.mpt', 'assets/msg/en/b0509000.mpt', 'assets/msg/en/b0512000.mpt', 'assets/msg/en/b0513000.mpt', 'assets/msg/en/b0516000.mpt', 'assets/msg/en/b0517000.mpt', 'assets/msg/en/b0520000.mpt', 'assets/msg/en/b0521000.mpt', 'assets/msg/en/b0522000.mpt', 'assets/msg/en/b0523000.mpt', 'assets/msg/en/b0524000.mpt', 'assets/msg/en/b0525000.mpt', 'assets/msg/en/b0526000.mpt', 'assets/msg/en/b0527000.mpt', 'assets/msg/en/b0528000.mpt',
            'assets/msg/en/b0529000.mpt', 'assets/msg/en/b0530000.mpt', 'assets/msg/en/b0531000.mpt', 'assets/msg/en/b0532000.mpt', 'assets/msg/en/b0533000.mpt', 'assets/msg/en/b0534000.mpt', 'assets/msg/en/b0535000.mpt', 'assets/msg/en/b0536000.mpt', 'assets/msg/en/b0537000.mpt', 'assets/msg/en/b0538000.mpt', 'assets/msg/en/b0539000.mpt', 'assets/msg/en/b0540000.mpt', 'assets/msg/en/b0541000.mpt', 'assets/msg/en/b0542000.mpt', 'assets/msg/en/b0543000.mpt', 'assets/msg/en/b0544000.mpt', 'assets/msg/en/b0545000.mpt', 'assets/msg/en/b0547000.mpt', 'assets/msg/en/b0548000.mpt', 'assets/msg/en/b0549000.mpt', 'assets/msg/en/b0550000.mpt', 'assets/msg/en/b0551000.mpt', 'assets/msg/en/b0552000.mpt']

for i in mpt_list:
    with ZipFile(path_to_roms + "/" + obb[0:-3] + "zip", 'r') as zObject:
        #zObject.extractall(path=path_to_roms + "/" + "obb")
        zObject.extract(i, path="en/")
        os.rename("en/" + i, "en/" + i.split("assets/msg/en/")[1])

shutil.rmtree("en/assets")

os.rename(path_to_roms + "/" + obb[0:-3] + "zip", path_to_roms + "/" + obb)