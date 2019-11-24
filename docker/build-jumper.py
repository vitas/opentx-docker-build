#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import subprocess
import shutil
import time
from collections import OrderedDict

# Show a header
print("")
print("Modified script of JumperTX-Build - https://hub.docker.com/r/benlye/jumpertx-build")
print("")

# Specify some paths for the build
build_dir = "/build"
source_dir = "/tmp/opentx"
output_dir = "/opentx"
output_filename = "opentx"
output_extension = ".bin"

# Maximum size for the compiled firmware
max_size = -1
t12_max_size = 65536 * 8
t16_max_size = 2 * 1024 * 1024

# Default T12 cmake flags
t12_default_options = OrderedDict([
    ("PCB", "X7"),
    ("PCBREV", "T12"),
    ("GUI", "YES"),
    ("GVARS", "YES"),
    ("HELI", "YES"),
    ("LCD_DUAL_BUFFER", "YES"),
    ("LUA", "YES"),
    ("LUA_COMPILER", "YES"),
    ("MULTIMODULE", "YES"),
    ("PPM_CENTER_ADJUSTABLE", "YES"),
    ("PPM_UNIT", "US"),
    ("RAS", "YES"),
    ("DISABLE_COMPANION", "YES"),
    ("CMAKE_BUILD_TYPE", "Release")
])

# Generic build cmake flags
t16_default_options = OrderedDict([
    ("PCB", "X10"),
    ("PCBREV", "T16"),
    ("JUMPER_RELEASE", "YES"),
    ("GUI", "YES"),
    ("GVARS", "YES"),
    ("HELI", "YES"),
    ("LUA", "YES"),
    ("LUA_COMPILER", "YES"),
    ("MULTIMODULE", "YES"),
    ("PPM_CENTER_ADJUSTABLE", "YES"),
    ("PPM_UNIT", "US"),
    ("RAS", "YES"),
    ("DISABLE_COMPANION", "YES"),
    ("CMAKE_BUILD_TYPE", "Release"),
    ("HARDWARE_INTERNAL_MODULE", "OFF"),
    ("INTERNAL_MODULE_MULTI", "YES")
])

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
    print("ERROR: JumperTX source not found in /opentx. Did you specifiy a valid mount?")
    print("")
    exit(5)

# Parse the extra options from the command line
extra_options = OrderedDict()

if "CMAKE_FLAGS" in os.environ:
    print("Additional CMAKE Flags: %s" % os.environ["CMAKE_FLAGS"])
    flags = os.environ["CMAKE_FLAGS"].split()
    for flag in flags:
        opt, val = flag.split("=")
        extra_options[opt] = val
else:
    print ("No additional CMAKE flags specified.")

# If specified, get the PCB from the flags; default to the T16
board = "T16"
if "PCB" in extra_options:
    board = extra_options["PCB"].upper()

board_rev = ""
if "PCBREV" in extra_options:
    board_rev = extra_options["PCBREV"].upper()

# Get the board defaults
if board == "T12":
    radio = "T12"
    default_options = t12_default_options
    max_size = t12_max_size
elif board == "X10" and board_rev == "T16":
    radio = "T16"
    default_options = t16_default_options
    max_size = t16_max_size
else:
    radio = board
    default_options = generic_default_options
    print("")
    print("WARNING: Unknown board (%s) specified. Known boards are T12, T16." % board)
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
    for def_opt, def_value in default_options.items():
        if ext_opt == def_opt:
            found = True
            break

    if found:
        if ext_value != def_value:
            default_options[def_opt] = ext_value
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
shutil.copytree("/opentx", "/tmp/opentx")

# Prepare the cmake command
cmd = ["cmake"]

# Append the default flags
for opt, value in default_options.items():
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
output_filename = output_filename + "-" + radio.lower()

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
if max_size > -1:
    print("Firmware size: {0}KB ({1:.0%})".format(binsize/1024, float(binsize)/float(max_size)))
else:
    print("")
    print("WARNING: Unable to validate firmware image size")
    print("Firmware size: {0}KB".format(binsize/1024))
print("")

# Exit with an error if the firmware is too big
if max_size > -1 and binsize > max_size:
    print("ERROR: Firmware is too large for radio.")
    print("")
    exit(1)

# Exit with success result code
exit(0)

