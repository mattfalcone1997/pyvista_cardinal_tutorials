# Using PyVista to post-process amd visualise data from Cardinal

This repository contains tutorials and useful scripts for processing and visualising data from the MOOSE application Cardinal. Pyvista documentaion can be found [here](https://docs.pyvista.org/). You should start with the `pebble_laminar.ipynb` example. The others are doable in any order.

If you have any suggestions, examples you wish to add or issues, please raise an issue or PR.
## Install `pyvista` for Jupyter
To get interactive plotting windows in Jupyter notebooks install `pyvista` with the `all` optional dependency.
`pip install pyvista[all]`

## Repository structure
* pebble_cht
  * `pebble.exo.gz`: gzipped fluid mesh file from Cubit.
  * `pebble.nek5000.gz` and `pebble0.f0000*.gz`: gzipped results data from nekRS.
  * `solid_out.e`: results from MOOSE thermal conduction solve.
* turbChannel
  * `turbChannel.nek5000.gz` and `turbChannel0.f0000*.gz` gzipped turbulent channel flow data.
* turbPipe
  * `turbPipe.nek5000.gz` and `turbPipe0.f0000*.gz` gzipped turbulent pipe flow data.
* vtk_build_openmp: directory containing scipts for installing VTK from source. More info found [here](vtk_build_openmp/README.md).
* [`pebble_laminar.ipynb`](pebble_laminar.ipynb): Jupyter notebook with a basic introduction of to Pyvista and Cardinal.
* [`visualising_vortices.ipynb`](visualising_vortices.ipynb): Jupyter notebook using direct access to data arrays to show vortices in turbulent channel flow.
* [`skin_friction.ipynb`](skin_friction.ipynb): Jupyter notebook using direct access to data arrays to compute the skin friction coefficient of turbulent pipe flow.
* [`pyvista_matplotlib.ipynb`](pyvista_matplotlib.ipynb): Notebook showing how Pyvista can be combined with matplotlib to produce publication quality figures.
* high_order: shows how one may use high-order lagrange elements to represent NekRS data. Come here to feel sad!
  * [`high_order.ipynb`](high_order/high_order.ipynb): Jupyter notebook showing how to convert nekRS data to use high-order Lagrange elements.
  * [`lagrange_convert.py`](high_order/lagrange_convert.py): Module with functions to convert data from NekRS to use high-order Lagrange elements.
* pyvista_cardinal_talk.pdf: Presentation highlighting some key features from `pyvista` and their application to Cardinal.