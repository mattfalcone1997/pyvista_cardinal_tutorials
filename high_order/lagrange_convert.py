"""lagrange_convert

A module to facilitate conversion of UnstructuredGrid to high-order lagrange
elements. This should in principle retain the spectral accuracy of NekRS in
pyvista
"""

import numpy as np
import pyvista as pv
import vtk

def np_array(ordering):
    """Wrapper for np.array to simplify common modifications"""
    return np.array(ordering, dtype=np.float64)

def _n_verts_between(n, frm, to):
    """Places `n` vertices on the edge between `frm` and `to`"""
    edge_verts = np.stack((
        np.linspace(frm[0], to[0], num=n+1, endpoint=False, axis=0),
        np.linspace(frm[1], to[1], num=n+1, endpoint=False, axis=0),
        np.linspace(frm[2], to[2], num=n+1, endpoint=False, axis=0),
        ), axis=1)
    return edge_verts[1:] # remove start point

def _number_quadrilateral(corner_verts, order, skip=False):
    """Outputs the list of coordinates of a right-angled quadrilateral
    of arbitrary order in the right ordering"""
    # first: corner vertices
    n = order -1 if skip else order+1
    coords = np.zeros((n*n, 3), dtype='f8')
    idx = 0
    if not skip:
        coords[:4] = corner_verts
        idx += 4

    # second: edges
    num_verts_on_edge = order -1
    edges = [(0,1), (1,2), (3,2), (0,3)]
    if not skip:
        for frm, to in edges:
            coords[idx:idx+num_verts_on_edge, :] = _n_verts_between(num_verts_on_edge,
                                                          corner_verts[frm],
                                                          corner_verts[to])
            idx += num_verts_on_edge

    # third: face
    e_x = (corner_verts[1] - corner_verts[0]) / order
    e_y = (corner_verts[3] - corner_verts[0]) / order
    pos_y = corner_verts[0].copy()
    pos_y = np.expand_dims(pos_y, axis=0)
    for i in range(num_verts_on_edge):
        for j in range(num_verts_on_edge):
            coords[idx + num_verts_on_edge*i + j, :] = corner_verts[0] + (i+1)*e_y + (j+1)*e_x

    return coords.astype('i4')


def _number_hexahedron(corner_verts, order):
    """Outputs the list of coordinates of a right-angled hexahedron of arbitrary
    order in the right ordering"""
    # first: corner vertices

    n = order+1
    coords = np.zeros((n*n*n, 3), dtype='f8')
    coords[:8] = corner_verts


    # second: edges
    num_verts_on_edge = order - 1
    edges = [(0,1), (1,2), (3,2), (0,3), (4,5), (5,6),
             (7,6), (4,7), (0,4), (1,5), (2,6), (3,7)]
    for i, (frm, to) in enumerate(edges):
        start = 8+i*num_verts_on_edge
        end = 8+(i+1)*num_verts_on_edge
        coords[start:end] = _n_verts_between(num_verts_on_edge, corner_verts[frm], corner_verts[to])

    # third: faces
    faces = [(0,3,7,4), (1,2,6,5), (0,1,5,4), (3,2,6,7),
             (0,1,2,3), (4,5,6,7)]
    for i, indices in enumerate(faces):
        start = 8 + 12*num_verts_on_edge + i*num_verts_on_edge*num_verts_on_edge
        end = 8 + 12*num_verts_on_edge + (i+1)*num_verts_on_edge*num_verts_on_edge

        sub_corner_verts = np.array([corner_verts[q] for q in indices], dtype='f8')
        coords[start:end] = _number_quadrilateral(sub_corner_verts, order, skip=True)

    # fourth: interior
    e_x = (corner_verts[1] - corner_verts[0]) / order
    e_y = (corner_verts[3] - corner_verts[0]) / order
    e_z = (corner_verts[4] - corner_verts[0]) / order

    pos_z = corner_verts[0].copy()
    pos_z = np.expand_dims(pos_z, axis=0)
    start = 8 + 12*num_verts_on_edge + 6*num_verts_on_edge*num_verts_on_edge
    for i in range(num_verts_on_edge):
        for j in range(num_verts_on_edge):
            for k in range(num_verts_on_edge):
                idx = start + i*num_verts_on_edge*num_verts_on_edge + j*num_verts_on_edge + k
                coords[idx] = corner_verts[0] + (i+1)*e_z + (j+1)*e_y + (k+1)*e_x

    return coords.astype('i4')

def reorder_points_3d(n):
    """Returns list index to re-order 3D spectral element points to be
       compatible with vtkLagrangeHexahedron."""
    corner_verts = np.array([[0,0,0], [n,0,0],[n,n,0], [0,n,0],
                             [0,0,n], [n,0,n], [n,n,n], [0,n,n]], 'f4')
    coords = _number_hexahedron(corner_verts, n)
    npoints = n + 1
    return np.array([x + y*npoints + npoints*npoints*z for x, y, z in coords])


def reorder_points_2d(n):
    """Returns list index to re-order 2D spectral element points to be
       compatible with vtkLagrangeQuadrilateral."""
    corner_verts = np.array([[0,0,0], [n,0,0],[n,n,0], [0,n,0]], 'f4')
    coords = _number_quadrilateral(corner_verts, n)
    npoints = n + 1
    return np.array([x + y*npoints + npoints*npoints*z for x, y, z in coords])


def to_lagrange(data: pv.UnstructuredGrid) -> pv.UnstructuredGrid:
    """Takes input Unstructured grid from nekRS and returns a new unstructured grid
      with high-order lagrange elements.

    Parameters
    ----------
    data : pv.UnstructuredGrid
        Input data from NekRS

    Returns
    -------
    pv.UnstructuredGrid
        data from NekRS with high-order elements
    """

    threeD = data.get_cell(0).type == pv.CellType.HEXAHEDRON

    n_elements = data.cell_data['spectral element id'].max()+1
    element = data.extract_values(values=0,
                                  preference='cell',
                                  scalars='spectral element id')
    n_points = element.n_points

    if threeD:
        order = int(np.cbrt(n_points) - 1)
        index_mapper = reorder_points_3d(order)
        cell_type = pv.CellType.LAGRANGE_HEXAHEDRON
        print("Converting hexahedral data")
    else:
        order = int(np.sqrt(n_points) - 1)
        index_mapper = reorder_points_2d(order)
        cell_type = pv.CellType.LAGRANGE_QUADRILATERAL
        print("Converting quadrilateral data")

    scalars = data.point_data.keys()

    # prepare point data for reordering
    point_data = {}
    for key in data.point_data.keys():
        point_data[key] = np.zeros(data.point_data[key].shape)


    new_grid = pv.UnstructuredGrid()
    new_points = vtk.vtkPoints()
    hex_array = vtk.vtkCellArray()


    for i in range(n_elements):
        element = data.extract_values(values=i,
                                    preference='cell',
                                    scalars='spectral element id')
        hex_cell = vtk.vtkLagrangeHexahedron() if threeD else vtk.vtkLagrangeQuadrilateral()
        hex_cell.GetPointIds().SetNumberOfIds(element.n_points)
        hex_cell.GetPoints().SetNumberOfPoints(element.n_points)

        for scalar in scalars:
            start = i*element.n_points
            end = (i+1)*element.n_points
            point_data[scalar][start:end] = element.point_data[scalar][index_mapper]

        for j in range(element.n_points):

            hex_cell.GetPointIds().SetId(j, i*element.n_points + j)
            hex_cell.GetPoints().SetPoint(j, *element.points[index_mapper[j]])
            new_points.InsertNextPoint(element.points[index_mapper[j]])

        hex_cell.SetUniformOrderFromNumPoints(element.n_points)

        hex_array.InsertNextCell(hex_cell)

    new_grid.SetPoints(new_points)
    new_grid.SetCells(cell_type, hex_array)

    for scalar in scalars:
        new_grid.point_data[scalar] = point_data[scalar]

    return new_grid
