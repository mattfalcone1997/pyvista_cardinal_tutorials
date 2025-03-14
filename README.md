# Using PyVista to post-process amd visualise data from Cardinal

This repository contains tutorials and useful scripts for processing and
visualising data from the MOOSE application Cardinal.

## Install `pyvista` for Jupyter
To get interactive plotting windows in Jupyter notebooks install `pyvista` with the `jupyter` optional dependency.
`pip install pyvista[jupyter]`

## Repository structure
* pebble_cht
  * `pebble.exo`: fluid mesh file from Cubit.
  * `pebble.nek5000` and `pebble0.f0000*`: results data from nekRS.
  * `solid_out.e`: results from MOOSE thermal conduction solve.
* high_order
  * `high_order.ipynb`: Jupyter notebook showing how to convert nekRS data to use high-order Lagrange elements.
* vtk_build_openmp
  * `build_wheel.sh`: Script to install threaded version of VTK. `vtk_options.cmake` should be in the same directory.
  * `vtk_options.cmake`: Cmake configuration file for threaded VTK build.
  * `pyvista_parallel.def`: Singularity container definition file installing pyvista with the threaded VTK build.
* `pebble_laminar.ipynb`: Jupyter notebook with a basic introduction of to Pyvista and Cardinal.

## Todo's
* [ ] Add script with OpenMP build of VTK
* [ ] Add singularity container with parallel VTK install
* [ ] Add Pyvista tutorial replicating the layered binned side average from the pebble example.
* [ ] Add tutorial using direct access to point and cell data.