docker run --rm -it -e "BOARD_NAME=t16" -e "CMAKE_FLAGS=HELI=NO FAI=CHOICE INTERNAL_MODULE_MULTI=NO VERSION_SUFFIX=VR PXX1=YES" -v ~/git/qt/opentx:/opentx vitass/opentx-fw-build
