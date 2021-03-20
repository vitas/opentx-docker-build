#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import subprocess
import shutil
import time
from collections import OrderedDict
from fwoptions import *

# Show a header
print("")
print("The script to build opentx firmware with docker image  vitass/opentx-fw--build")
print("")

# Specify some paths for the build
build_dir = "/build"
source_dir = "/tmp/opentx"
output_dir = "/opentx"
output_filename = "opentx"
output_extension = ".bin"

# Maximum size for the compiled firmware
maxsize = -1

# Generic build cmake flags
generic_default_options = OrderedDict([
    ("GUI", "YES"),
    ("GVARS", "YES"),
    ("HELI", "YES"),
    ("LUA", "NO"),
    ("LUA_COMPILER", "YES"),
    ("MULTIMODULE", "YES"),
    ("PPM_CENTER_ADJUSTABLE", "YES"),
    ("PPM_UNIT", "US"),
    ("RAS", "YES"),
    ("DISABLE_COMPANION", "YES"),
    ("CMAKE_BUILD_TYPE", "Release"),
])

# Available languages
available_languages = ("EN", "FR", "SE", "IT", "CZ", "DE", "PT", "ES", "PL", "NL")

# Check that the source is valid
if not os.path.exists("/opentx/CMakeLists.txt"):
    print("ERROR: OpenTX source not found in /opentx. Did you specifiy a valid mount?")
    print("")
    exit(5)

# Parse the extra options from the command line
extra_options = OrderedDict()

if "BOARD_NAME" in os.environ:
    print("Board name: %s" % os.environ["BOARD_NAME"])
    board_name = os.environ["BOARD_NAME"]
else:
    print("Target board name is not specified. Exit")
    exit(5)

if "CMAKE_FLAGS" in os.environ:
    print("Additional CMAKE Flags: %s" % os.environ["CMAKE_FLAGS"])
    flags = os.environ["CMAKE_FLAGS"].split()
    for flag in flags:
        opt, val = flag.split("=")
        extra_options[opt] = val
else:
    print ("No additional CMAKE flags specified.")

if board_name == "sky9x":
    extra_options["PCB"] = "SKY9X"
    firmware_options = options_sky9x
    maxsize = 65536 * 4
elif board_name == "9xrpro":
    extra_options["PCB"] = "9XRPRO"
    extra_options["SDCARD"] = "YES"
    firmware_options = options_sky9x
    maxsize = 65536 * 4
elif board_name == "ar9x":
    extra_options["PCB"] = "AR9X"
    extra_options["SDCARD"] = "YES"
    firmware_options = options_ar9x
    maxsize = 65536 * 4
elif board_name == "x9lite":
    extra_options["PCB"] = "X9LITE"
    firmware_options = options_taranis_x9lite
    maxsize = 65536 * 8
elif board_name == "x9lites":
    extra_options["PCB"] = "X9LITES"
    firmware_options = options_taranis_x9lite
    maxsize = 65536 * 8
elif board_name == "x7":
    extra_options["PCB"] = "X7"
    extra_options["PCBREV"] = "X7"
    firmware_options = options_taranis_x9dp
    maxsize = 65536 * 8
elif board_name == "x7access":
    extra_options["PCB"] = "X7"
    extra_options["PCBREV"] = "ACCESS"
    firmware_options = options_taranis_x9dp
    maxsize = 65536 * 8
elif board_name == "xlite":
    extra_options["PCB"] = "XLITE"
    firmware_options = options_taranis_xlite
    maxsize = 65536 * 8
elif board_name == "xlites":
    extra_options["PCB"] = "XLITES"
    firmware_options = options_taranis_xlites
    maxsize = 65536 * 8
elif board_name == "x9d":
    extra_options["PCB"] = "X9D"
    firmware_options = options_taranis_x9d
    maxsize = 65536 * 8
elif board_name == "x9d+":
    extra_options["PCB"] = "X9D+"
    firmware_options = options_taranis_x9dp
    maxsize = 65536 * 8
elif board_name == "x9d+2019":
    extra_options["PCB"] = "X9D+"
    extra_options["PCBREV"] = "2019"
    firmware_options = options_taranis_x9dp
    maxsize = 65536 * 8
elif board_name == "x9e":
    extra_options["PCB"] = "X9E"
    firmware_options = options_taranis_x9e
    maxsize = 65536 * 8
elif board_name == "x10":
    extra_options["PCB"] = "X10"
    firmware_options = options_horus_x10
    maxsize = 2 * 1024 * 1024
elif board_name == "x10express":
    extra_options["PCB"] = "X10"
    extra_options["PCBREV"] = "EXPRESS"
    firmware_options = options_horus_x10
    maxsize = 2 * 1024 * 1024
elif board_name == "x12s":
    extra_options["PCB"] = "X12S"
    firmware_options = options_horus_x12s
    maxsize = 2 * 1024 * 1024
elif board_name == "t12":
    extra_options["PCB"] = "X7"
    extra_options["PCBREV"] = "T12"
    firmware_options = options_jumper_t12
    maxsize = 65536 * 8
elif board_name == "t16":
    extra_options["PCB"] = "X10"
    extra_options["PCBREV"] = "T16"
    firmware_options = options_jumper_t16
    maxsize = 2 * 1024 * 1024
elif board_name == "tx16s":
    extra_options["PCB"] = "X10"
    extra_options["PCBREV"] = "TX16S"
    firmware_options = options_radiomaster_tx16s
    maxsize = 2 * 1024 * 1024
elif board_name == "t18":
    extra_options["PCB"] = "X10"
    extra_options["PCBREV"] = "T18"
    firmware_options = options_jumper_t18
    maxsize = 2 * 1024 * 1024
else:
    firmware_options = generic_default_options
    print("")
    print("WARNING: Unknown board (%s) specified" % board_name)
    print("Firmware will be built with generic defaults and any specified CMAKE flags.")
    print("")
#exit(3)

# If specified, validate the language from the flags
if "TRANSLATIONS" in extra_options:
    if not extra_options["TRANSLATIONS"].upper() in available_languages:
        print("")
        print("ERROR: Invalid language (%s) specified. Valid languages are: %s." % (extra_options["TRANSLATIONS"], " ".join(available_languages)))
        print("")
        exit(6)

# Compare the extra options to the board's defaults
extra_command_options = OrderedDict()
for ext_opt, ext_value in extra_options.items():
    found = False
    for def_opt, def_value in firmware_options.items():
        if ext_opt == def_opt:
            found = True
            break

    if found:
        if ext_value != def_value:
            firmware_options[def_opt] = ext_value
            print ("Overriding default flag: %s=%s => %s=%s" % (def_opt, def_value, def_opt, ext_value))
        else:
            if def_opt != "PCB" and def_opt != "PCBREV":
                print ("Override for default flag matches default value: %s=%s" % (def_opt, def_value))
    else:
        print ("Adding additional flag: %s=%s" % (ext_opt, ext_value))
        extra_command_options[ext_opt] = ext_value

# Start the timer
start = time.time()

# Change to the build directory
os.chdir(build_dir)

# Copy the source tree to the temporary folder - makes build 3x faster than building against the mount on Windows
print("")
print ("Copying source from /opentx to /tmp/opentx ...")
print("")
shutil.copytree("/opentx", "/tmp/opentx", ignore=shutil.ignore_patterns(".git"))

# Prepare the cmake command
cmd = ["cmake"]

# Append the default flags
for opt, value in firmware_options.items():
    cmd.append("-D%s=%s" % (opt, value))

# Append the extra flags
for opt, value in extra_command_options.items():
    cmd.append("-D%s=%s" % (opt, value))

# Append the source directory
cmd.append(source_dir)

# Output the cmake command line

print(" ".join(cmd))
print("")

# Launch cmake
proc = subprocess.Popen(cmd)
proc.wait()

# Exit if cmake errored
if proc.returncode != 0:
    print("")
    print("ERROR: cmake configuration failed.")
    print("")
    exit(2)


proc = subprocess.Popen(["make", "clean"])
proc.wait()

# Launch make with two threads
proc = subprocess.Popen(["make", "-j2", "firmware"])
proc.wait()

# Exit if make errored
if proc.returncode != 0:
    print("")
    print("ERROR: make compilation failed.")
    print("")
    exit(2)

# Stop the timer
end = time.time()

# Append the PCB type to the output file name
output_filename = output_filename + "-" + board_name.lower()

# Get the firmware version
stampfile = "radio/src/stamp.h"
for line in open(stampfile):
 if "#define VERSION " in line:
   firmware_version = line.split()[2].replace('"','')

# Append the version to the output file name
if firmware_version:
    output_filename = output_filename + "-" + firmware_version

# Append the language to the output file name if one is specified
if "TRANSLATIONS" in extra_command_options:
    output_filename = output_filename + "-" + extra_command_options["TRANSLATIONS"].lower()

# Append the extension to the output file name
output_filename = output_filename + output_extension

# Assemble the output path
output_path = os.path.join(output_dir, output_filename)

# Move the new binary to the output path
shutil.move("firmware.bin", output_path)

# Get the size of the binary
binsize = os.stat(output_path).st_size

# Print out the file name and size
print("")
print("Build completed in {0:.1f} seconds.".format((end-start)))
print("")
print("Firmware file: %s" % (output_path))
if maxsize > -1:
    print("Firmware size: {0}KB ({1:.0%})".format(binsize/1024, float(binsize)/float(maxsize)))
else:
    print("")
    print("WARNING: Unable to validate firmware image size")
    print("Firmware size: {0}KB".format(binsize/1024))
print("")

# Exit with an error if the firmware is too big
if maxsize > -1 and binsize > maxsize:
    print("ERROR: Firmware is too large for radio.")
    print("")
    exit(1)

# Exit with success result code
exit(0)

