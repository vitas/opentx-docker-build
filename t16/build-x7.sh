docker run --rm -it -e "BOARD_NAME=x7" -e "CMAKE_FLAGS=HELI=NO FAI=CHOICE FONT=SQT5 INTERNAL_MODULE_MULTI=NO BLUETOOTH=NO VERSION_SUFFIX=VR" -v ~/git/qt/opentx:/opentx vitass/opentx-fw-build
