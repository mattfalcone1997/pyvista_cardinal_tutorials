# Building VTK with OpenMP
When VTK is installed using pip, a serial version is installed and there is not pre-built Python Wheel which is threaded. It is also built without dependencies, so some functionality in Paraview may not be there in VTK python. The solution is to build VTK from source, but this is not always straightforward. This directory provides some useful scripts.

* [`build_wheel.sh`](build_wheel.sh): Script to install threaded version of VTK. `vtk_options.cmake` should be in the same directory.
* [`vtk_options.cmake`](vtk_options.cmake): Cmake configuration file derived from VTK CI pipeline which allows certain options to be easily installed through environment variables.
* [`pyvista_parallel.def`](pyvista_parallel.def): Singularity container definition file installing pyvista with the threaded VTK build.

## Building locally from source
1. Place `build_wheel.sh` and `vtk_options.cmake` in directory where you wish VTK to be downloaded
2. Set environment variables
```bash
export CMAKE_CONFIGURATION=openmp_python
export PYTHON_PREFIX=/path/to/python
export VTK_VERSION=9.4.2
```
3. Run `./build_wheel.sh` to download and install VTK
4. You may need to set `LD_LIBRARY_PATH` to point to the VTK libraries

If you wish to install VTK with MPI this can be done using `export CMAKE_CONFIGURATION=openmp_python_mpi`

## Using Singularity/Apptainer
The definition file for a Singularity container is shown in `pyvista_parallel.def`. It can be built using
```bash
sudo singularity build pyvista_parallel.sif pyvista_parallel.def
```
A Python script can then be run using
```bash
singularity run pyvista_parallel.sif script.py
```
or
```bash
singularity ./pyvista_parallel.sif script.py
```
The container can be run as a shell using
```bash
singularity shell pyvista_parallel.sif
```
This container has also been uploaded to the Sylabs Cloud so it can be pulled from cloud without you having to build it yourself.
```bash
singularity pull pyvista_parallel.sif library://mattfalcone1997/VTK/pyvista_parallel.sif:latest
```
Depending on whether you are using Singularity or Apptainer you may need to point the remote to a different source.
```bash
singularity remote add SylabsCloud cloud.sylabs.io
```
