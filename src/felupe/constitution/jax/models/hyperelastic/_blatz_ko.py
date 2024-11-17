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
from functools import wraps

from jax.numpy import sqrt, trace
from jax.numpy.linalg import det

from ....tensortrax.models.hyperelastic import blatz_ko as blatz_ko_docstring


@wraps(blatz_ko_docstring)
def blatz_ko(C, mu):

    I1 = trace(C)
    I2 = (I1**2 - trace(C @ C)) / 2
    I3 = det(C)

    return mu * (I2 / I3 + 2 * sqrt(I3) - 5)