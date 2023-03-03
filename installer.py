import os, subprocess, sys, shutil

path_to_ndstool = "ndstool"

path_to_roms = "roms"

us_rom_indicator = "us"
ja_rom_indicator = "ja"

regions = [us_rom_indicator, ja_rom_indicator]

roms = {us_rom_indicator : path_to_roms + "/" + us_rom_indicator + ".nds", 
        ja_rom_indicator : path_to_roms + "/" + ja_rom_indicator + ".nds"}

for i in regions:
    shutil.rmtree(path_to_roms + "/" + i)

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
            subprocess.run(path_to_ndstool + " -c " + path_to_roms + "/" + us_rom_indicator + ".copy.nds" + " -9 " + path_to_region_folder + "/arm9.bin -7 " + path_to_region_folder + "/arm7.bin -y9 " + path_to_region_folder + "/y9.bin -y7 " + path_to_region_folder + "/y7.bin -t " + path_to_region_folder + "/banner.bin -h " + path_to_region_folder + "/header.bin -d " + path_to_region_folder + "/data -y " + path_to_region_folder + "/overlay ", shell=True)

extract_roms(regions)

repack_roms(regions)