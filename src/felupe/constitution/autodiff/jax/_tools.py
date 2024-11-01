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

import inspect
from functools import wraps


def vmap(fun, in_axes=0, out_axes=0, **kwargs):
    """Vectorizing map. Creates a function which maps ``fun`` over argument axes. This
    decorator treats all non-specified arguments and keyword-arguments as static.

    See Also
    --------
    jax.vmap : Vectorizing map. Creates a function which maps ``fun`` over argument
        axes.
    """

    import jax

    @wraps(fun)
    def vmap_with_static_kwargs(*args, **keywordargs):
        # sorted list of all parameter keys, including kwargs with default values
        sig = inspect.signature(fun)
        keys = [
            key
            for key, value in sig.parameters.items()
            if not (key in ["args", "kwargs"] and value.default == inspect._empty)
        ]

        if not (
            "kwargs" in sig.parameters.keys()
            and sig.parameters["kwargs"].default == inspect._empty
        ):
            # check if unexpected keyword-argument is given
            for key in keywordargs.keys():
                if key not in keys:
                    raise TypeError(
                        f"{fun.__name__}() got an unexpected keyword argument '{key}'"
                    )

        # dict with default values for all parameters
        parameters = dict(
            [(key, value.default) for key, value in sig.parameters.items()]
        )

        # merge dict of default values with custom keyword arguments
        items = {**parameters, **keywordargs}

        # create sorted list of values of keyword-arguments, including default kwargs
        keyword_args = [items[key] for key in keys[len(args) :]]

        # don't map non-given arguments and keyword-arguments
        if not hasattr(in_axes, "__len__"):
            in_axes_tuple = (in_axes,)
        else:
            in_axes_tuple = in_axes

        static_argnums = len(args) + len(keyword_args) - len(in_axes_tuple)
        in_axes_new = (*in_axes_tuple, *([None] * static_argnums))

        vfun = jax.vmap(fun, in_axes=in_axes_new, out_axes=out_axes, **kwargs)

        return vfun(*args, *keyword_args)

    return vmap_with_static_kwargs


def vmap2(fun, in_axes=0, out_axes=0, **kwargs):
    "Nested vectorizing map."
    return vmap(
        vmap(fun, in_axes=in_axes, out_axes=out_axes, **kwargs),
        in_axes=in_axes,
        out_axes=out_axes,
        **kwargs,
    )


def total_lagrange(fun):
    import jax.numpy as jnp

    @wraps(fun)
    def evaluate(F, *args, **kwargs):
        i, j = jnp.triu_indices(3)
        C_triu = jnp.einsum("ia,ia->a", F[:, i], F[:, j])
        C = C_triu[jnp.array([[0, 1, 2], [1, 3, 4], [2, 4, 5]])]
        return fun(C, *args, **kwargs)

    return evaluate
