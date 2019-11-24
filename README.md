# opentx-docker-build

A Docker container for building [OpenTX](https://github.com/opentx/opentx), 

The container contains a Debian Linux image pre-configured with the tools required to build OpenTX.  
Running the container will compile the firmware from a local source tree and produce a compiled firmware image.

# Instructions
## Setup
1. [Install Docker](https://docs.docker.com/install/)
   * If installing on Windows choose **Linux Containers** when prompted
   
1. Pull the container:

   `docker pull vitass/opentx-fw-build`

1. Clone the OpenTX repository:

   `git clone --recursive -b 2.3 https://github.com/opentx/opentx.git`


## Modify the Firmware
Use your tool of choice to make changes to the OpenTX source.


## Build the Firmware
1. Run the container, specifying the path to the JumperTX source as a mount volume:

   `docker run --rm -it -v [OpenTX Source Path]:/opentx vitass/opentx-fw-build`
   
   example:
 
   docker run --rm -it -v "/home/vitas/github/opentx.git:/opentxtx" vitass/opentx-fw-build`

The compiled firmware image will be placed in the root of the source directory when the build has finished.  

The default output name is `opentx-t16-2.3.3-en.bin` but this will vary depending on any optional flags that may have been passed.

## Changing the Build Flags
Build flags can be changed by passing a switch to the Docker container when it is run.

The syntax is `-e "CMAKE_FLAGS=FLAG1=VALUE1 FLAG2=VALUE2"`.

Default flags will be replaced by the new value, additional flags will be appended.

### Examples

1. Build from the source in `/home/vitas/opentx.git` and disable `HELI`:

   `docker run --rm -it -v "/home/vitas/opentx.git/:/opentx" -e "CMAKE_FLAGS=HELI=NO" vitass/opentx-fw-build`

## Changing the Language
The default language is English.  Alternative languages can by setting the `TRANSLATIONS=` CMAKE flag with a valid language code.

Valid language codes are: 
* EN (English) 
* FR (French) 
* SE (Swedish)
* IT (Italian)
* CZ (Czech)
* DE (German)
* PT (Portugese)
* ES (Spanish)
* PL (Polish)
* NL (Dutch)

