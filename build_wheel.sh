#!/bin/bash
# This script installs a VTK python wheel with Open MP enabled
# The following envionrment variables must be set
# * CMAKE_CONFURATION
# * PYTHON_PREFIX
# * VTK_VERSION
# The CMAKE configuration file vtk_options must be present.

#===============================================================
# Helper functions

test_return () {
      if [ $? -ne 0 ]; then
            echo -e "Error: $1"
            exit $?
      fi
}

#Check cmake cache available
if [ ! -f vtk_options.cmake ]; then
      echo -e "Cannot find vtk_options.cmake"
      exit 1
fi
CMAKE_CONFIG_FILE=${PWD}/vtk_options.cmake

#===============================================================
# Use ninja to build if available
if command -v ninja &> /dev/null ; then
      CMD=ninja
      GENERATOR="Ninja"
else
      CMD="make -j ${NTHREADS}"
      GENERATOR="Unix Makefiles"
fi

echo -e "Using cmake generator ${CMD}"
VTK_DIR=VTK-${VTK_VERSION}

#===========================================================
# Determine if VTK needs to be untared
UNTAR=OFF
if  ! [ -d ${VTK_DIR} ]; then
      UNTAR=ON
fi
TARBALL=${VTK_DIR}.tar.gz

# Determine if vtk needs to be downloaded
DOWNLOAD=OFF
if ! [ -f ${TARBALL} ]; then
      DOWNLOAD=ON
fi

#============================================================
# download tar file
if [ $DOWNLOAD = "ON" ]; then
      wget https://www.vtk.org/files/release/${VTK_VERSION::-2}/${TARBALL}
      test_return "Error downloading $TARBALL"
else
      echo -e "$TARBALL already downloaded"
fi

# untar file
if [ $UNTAR = "ON" ]; then
      tar -xvf $TARBALL
      test_return "Error extracting $TARBALL"
else
      echo -e "${VTK_DIR} already extracted from tarball $TARBALL"
fi

#============================================================
# create build directory
cd $VTK_DIR
mkdir -p build
cd build

# set environment variables for cmake

# Run cmake
cmake -G"${GENERATOR}" \
      -DCMAKE_BUILD_TYPE=Release \
      -DVTK_BUILD_TESTING=OFF \
      -DVTK_BUILD_DOCUMENTATION=OFF \
      -DVTK_BUILD_EXAMPLES=OFF \
      -DVTK_MODULE_ENABLE_VTK_opengl=YES \
      -DVTK_MODULE_ENABLE_VTK_PythonInterpreter:STRING=NO \
      -C "${CMAKE_CONFIG_FILE}" \
      -B . -S ../

test_return "Error during configuration"

# build VTK
$CMD
test_return "Error during VTK build"

PYBIN=$PYTHON_PREFIX/bin/python

# Create wheel file for VTK
$PYBIN setup.py bdist_wheel
test_return "Error building VTK wheel"

#Install VTK wheel
$PYBIN -m pip install dist/vtk-*.whl
test_return "Error installing VTK wheel"