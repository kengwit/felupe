# -*- coding: utf-8 -*-
"""
This file is part of FElupe.

FElupe is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

FElupe is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with FElupe.  If not, see <http://www.gnu.org/licenses/>.
"""

from ..math import eigvalsh, equivalent_von_mises, tovoigt
from ._field import ViewField


class ViewSolid(ViewField):
    """Provide Visualization methods for :class:`felupe.Field` and `felupe.SolidBody`.
    The warped (deformed) mesh is created from the values of the first field
    (displacements). By default, the "Deformation Gradient" tensor, the
    "Logarithmic Strain" tensor and the "Principal Values of Logarithmic Strain" are
    evaluated as field-related items of the cell-data dict. Optional items of given
    point- and cell-data overwrite these default field-related cell-data items.

    Parameters
    ----------
    field : felupe.FieldContainer
        The field-container.
    solid : felupe.SolidBody or felupe.SolidBodyIncompressible or None, optional
        A solid body to evaluate the (Cauchy) stress (default is None).
    stress_type : str, optional
        The type of stress, either "Cauchy" or "Kirchhoff, which is exported (default is
        "Cauchy").
    point_data : dict or None, optional
        Additional point-data dict (default is None).
    cell_data : dict or None, optional
        Additional cell-data dict (default is None).
    cell_type : pyvista.CellType or None, optional
        Cell-type of PyVista (default is None).
    project : callable or None, optional
        Callable to project stress at quadrature-points to mesh-points (default is
        None). Valid callables are :class:`~felupe.project` or
        :class:`~felupe.tools.extrapolate`.

    Attributes
    ----------
    mesh : pyvista.UnstructuredGrid
        A generalized Dataset with the mesh as well as point- and cell-data. This is
        not an instance of :class:`felupe.Mesh`.

    See Also
    --------
    felupe.project: Project given values at quadrature-points to mesh-points.
    """

    def __init__(
        self,
        field,
        solid=None,
        stress_type="Cauchy",
        point_data=None,
        cell_data=None,
        cell_type=None,
        project=None,
        **kwargs,
    ):
        if point_data is None:
            point_data = {}

        if cell_data is None:
            cell_data = {}

        point_data_from_solid = {}
        cell_data_from_solid = {}

        if solid is not None:
            stress_from_field = {
                "cauchy": solid.evaluate.cauchy_stress,
                "kirchhoff": solid.evaluate.kirchhoff_stress,
            }
            stress = stress_from_field[stress_type.lower()](field)
            stress_label = f"{stress_type.title()} Stress"

            if project is None:
                cell_data_from_solid[stress_label] = tovoigt(stress.mean(-2)).T
                cell_data_from_solid[f"Principal Values of {stress_label}"] = (
                    eigvalsh(stress).mean(-2).T
                )
                cell_data_from_solid[f"Equivalent of {stress_label}"] = (
                    equivalent_von_mises(stress).mean(-2).T
                )

            elif callable(project):
                point_data_from_solid[stress_label] = project(
                    tovoigt(stress), solid.field.region
                )
                point_data_from_solid[f"Principal Values of {stress_label}"] = project(
                    eigvalsh(stress), solid.field.region
                )
                point_data_from_solid[f"Equivalent of {stress_label}"] = project(
                    equivalent_von_mises(stress), solid.field.region
                )
            else:
                raise TypeError("The project-argument must be callable or None.")

        super().__init__(
            field=field,
            point_data={**point_data_from_solid, **point_data},
            cell_data={**cell_data_from_solid, **cell_data},
            cell_type=cell_type,
            project=project,
        )