# A Debian image for compiling openTX 2.3+ for jumper T16
FROM debian:stretch

# Update and install the required components
RUN DEBIAN_FRONTEND=noninteractive apt-get -y update && apt-get -y install wget zip bzip2 cmake build-essential python python-pil git lib32ncurses5 libgtest-dev

# Retrieve and install the required version of the ARM compiler
RUN wget https://launchpad.net/gcc-arm-embedded/4.7/4.7-2013-q3-update/+download/gcc-arm-none-eabi-4_7-2013q3-20130916-linux.tar.bz2 -P /tmp --progress=bar:force
RUN tar -C /tmp -xjf /tmp/gcc-arm-none-eabi-4_7-2013q3-20130916-linux.tar.bz2
RUN mv /tmp/gcc-arm-none-eabi-4_7-2013q3 /opt/gcc-arm-none-eabi
RUN rm /tmp/gcc-arm-none-eabi-4_7-2013q3-20130916-linux.tar.bz2
RUN apt-get install -y python-clang-3.9 libclang-3.9-dev

# Declare the mount point
VOLUME ["/opentx"]

# Set the working directory to /build
WORKDIR /build

# Add the build scripts
COPY build-fw.py /build

# Update the path
ENV PATH $PATH:/opt/gcc-arm-none-eabi/bin:/opentx/radio/util

# Run the shell script to build the firmware
ENTRYPOINT ["bash", "-c", "python /build/build-fw.py $CMAKE_FLAGS"]
