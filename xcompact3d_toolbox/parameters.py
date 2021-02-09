# -*- coding: utf-8 -*-
"""Manipulate the physical and computational parameters.
"""

import numpy as np
import math
import traitlets
import warnings
from .param import boundary_condition, param
from .mesh import get_mesh
from .io import i3d_to_dict, dict_to_i3d, prm_to_dict, write_xdmf

possible_mesh = [
    9,
    11,
    13,
    17,
    19,
    21,
    25,
    31,
    33,
    37,
    41,
    49,
    51,
    55,
    61,
    65,
    73,
    81,
    91,
    97,
    101,
    109,
    121,
    129,
    145,
    151,
    161,
    163,
    181,
    193,
    201,
    217,
    241,
    251,
    257,
    271,
    289,
    301,
    321,
    325,
    361,
    385,
    401,
    433,
    451,
    481,
    487,
    501,
    513,
    541,
    577,
    601,
    641,
    649,
    721,
    751,
    769,
    801,
    811,
    865,
    901,
    961,
    973,
    1001,
    1025,
    1081,
    1153,
    1201,
    1251,
    1281,
    1297,
    1351,
    1441,
    1459,
    1501,
    1537,
    1601,
    1621,
    1729,
    1801,
    1921,
    1945,
    2001,
    2049,
    2161,
    2251,
    2305,
    2401,
    2431,
    2501,
    2561,
    2593,
    2701,
    2881,
    2917,
    3001,
    3073,
    3201,
    3241,
    3457,
    3601,
    3751,
    3841,
    3889,
    4001,
    4051,
    4097,
    4321,
    4375,
    4501,
    4609,
    4801,
    4861,
    5001,
    5121,
    5185,
    5401,
    5761,
    5833,
    6001,
    6145,
    6251,
    6401,
    6481,
    6751,
    6913,
    7201,
    7291,
    7501,
    7681,
    7777,
    8001,
    8101,
    8193,
    8641,
    8749,
    9001,
]
""":obj:`list` of :obj:`int`: Possible number of mesh points for no periodic boundary conditions.

Due to restrictions at the FFT library, they must be equal to:

.. math::
    n_i = 2^{1+a} \\times 3^b \\times 5^c + 1,

where :math:`a`, :math:`b` and :math:`c` are non negative integers, and :math:`i`
representes the three coordinates (**x**, **y** and **z**).

Aditionally, the derivative's stencil imposes that :math:`n_i \\ge 9`.

Notes
-----
There is no upper limit, as long as the restrictions are satisfied.
"""

possible_mesh_p = [i - 1 for i in possible_mesh]
""":obj:`list` of :obj:`int`: Possible number of mesh points for periodic boundary conditions.

Due to restrictions at the FFT library, they must be equal to:

.. math::
    n_i = 2^{1+a} \\times 3^b \\times 5^c,

where :math:`a`, :math:`b` and :math:`c` are non negative integers, and :math:`i`
representes the three coordinates (**x**, **y** and **z**).

Aditionally, the derivative's stencil imposes that :math:`n_i \\ge 8`.

Notes
-----
There is no upper limit, as long as the restrictions are satisfied.
"""


def divisorGenerator(n):
    """Yelds the possibles divisors for ``n``.

    Especially useful to compute the possible values for :obj:`p_row` and :obj:`p_col`
    as functions of the number of computational cores available (:obj:`ncores`).
    Zero is also included in the case of auto-tunning, i.e., ``p_row=p_col=0``.

    Parameters
    ----------
    n : int
        Input value.

    Yields
    ------
    int
        The next possible divisor for ``n``.

    Examples
    -------

    >>> print(list(divisorGenerator(8)))
    [0, 1, 2, 4, 8]

    """
    large_divisors = [0]
    for i in range(1, int(math.sqrt(n) + 1)):
        if n % i == 0:
            yield i
            if i * i != n:
                large_divisors.append(n / i)
    for divisor in reversed(large_divisors):
        yield int(divisor)


class Parameters(traitlets.HasTraits):
    """The physical and computational parameters are built on top of `traitlets`_.

    It is a framework that lets Python classes have attributes with type checking,
    dynamically calculated default values, and ‘on change’ callbacks.
    In addition, there are `ipywidgets`_ for a friendly user interface.

    .. warning:: There is a bug reported affecting the widgets `#2`_,
        they are not working properly at the moment.

    .. _traitlets:
        https://traitlets.readthedocs.io/en/stable/index.html
    .. _ipywidgets:
        https://ipywidgets.readthedocs.io/en/latest/
    .. _#2:
        https://github.com/fschuch/xcompact3d_toolbox/issues/2

    Attributes
    ----------
    nclx1 : int
        Boundary condition for velocity field where :math:`x=0`, the options are:

        * 0 - Periodic;
        * 1 - Free-slip;
        * 2 - Inflow.

    nclxn : int
        Boundary condition for velocity field where :math:`x=L_x`, the options are:

        * 0 - Periodic;
        * 1 - Free-slip;
        * 2 - Convective outflow.

    ncly1 : int
        Boundary condition for velocity field where :math:`y=0`, the options are:

        * 0 - Periodic;
        * 1 - Free-slip;
        * 2 - No-slip.

    nclyn : int
        Boundary condition for velocity field where :math:`y=L_y`, the options are:

        * 0 - Periodic;
        * 1 - Free-slip;
        * 2 - No-slip.

    nclz1 : int
        Boundary condition for velocity field where :math:`z=0`, the options are:

        * 0 - Periodic;
        * 1 - Free-slip;
        * 2 - No-slip.

    nclzn : int
        Boundary condition for velocity field where :math:`z=L_z`, the options are:

        * 0 - Periodic;
        * 1 - Free-slip;
        * 2 - No-slip.

    nclxS1 : int
        Boundary condition for scalar field(s) where :math:`x=0`, the options are:

        * 0 - Periodic;
        * 1 - No-flux;
        * 2 - Inflow.

    nclxSn : int
        Boundary condition for scalar field(s) where :math:`x=L_x`, the options are:

        * 0 - Periodic;
        * 1 - No-flux;
        * 2 - Convective outflow.

    nclyS1 : int
        Boundary condition for scalar field(s) where :math:`y=0`, the options are:

        * 0 - Periodic;
        * 1 - No-flux;
        * 2 - Dirichlet.

    nclySn : int
        Boundary condition for scalar field(s) where :math:`y=L_y`, the options are:

        * 0 - Periodic;
        * 1 - No-flux;
        * 2 - Dirichlet.

    nclzS1 : int
        Boundary condition for scalar field(s) where :math:`z=0`, the options are:

        * 0 - Periodic;
        * 1 - No-flux;
        * 2 - Dirichlet.

    nclzSn : int
        Boundary condition for scalar field(s) where :math:`z=L_z`, the options are:

        * 0 - Periodic;
        * 1 - No-flux;
        * 2 - Dirichlet.

    ivisu : bool
        Enables store snapshots if :obj:`True`.

    ipost : bool
        Enables online postprocessing if :obj:`True`.

    ilesmod : bool
        Enables Large-Eddy methodologies if :obj:`True`.

    ifirst : int
        The number for the first iteration.

    ilast : int
        The number for the last iteration.

    icheckpoint : int
        Frequency for writing restart file.

    ioutput : int
        Frequency for visualization (3D snapshots).

    iprocessing : int
        Frequency for online postprocessing.

        Notes
        -----
            The exactly output may be different according to each flow configuration.
    """

    #
    # # BasicParam
    #

    p_row, p_col = [
        traitlets.Int(default_value=0, min=0).tag(
            group="BasicParam", desc="Domain decomposition for parallel computation"
        )
        for name in ["p_row", "p_col"]
    ]
    """int: Defines the domain decomposition for (large-scale) parallel computation.

    Notes
    -----
        The product ``p_row * p_col`` must be equal to the number of
        computational cores where Xcompact3d will run.
        More information can be found at `2DECOMP&FFT`_.

        ``p_row = p_col = 0`` activates auto-tunning.

    .. _2DECOMP&FFT:
        http://www.2decomp.org
    """

    itype = traitlets.Int(default_value=10, min=0, max=10).tag(
        group="BasicParam",
        desc="Flow configuration (1=Lock-exchange, 2=TGV, 3=Channel, 4=Periodic hill, 5=Cylinder, and others)",
    )
    """int: Sets the flow configuration, each one is specified in a different
    ``BC.<flow-configuration>.f90`` file (see `Xcompact3d/src`_), they are:

    * 0 - User configuration;
    * 1 - Turbidity Current in Lock-Release;
    * 2 - Taylor-Green Vortex;
    * 3 - Periodic Turbulent Channel;
    * 5 - Flow around a Cylinder;
    * 6 - Debug Schemes (for developers);
    * 7 - Mixing Layer;
    * 9 - Turbulent Boundary Layer;
    * 10 - `Sandbox`_.

    .. _Xcompact3d/src:
        https://github.com/fschuch/Xcompact3d/tree/master/src
    """

    iin = traitlets.Int(default_value=0, min=0, max=2).tag(
        group="BasicParam", desc="Defines pertubation at initial condition"
    )
    """int: Defines perturbation at the initial condition:

    * 0 - No random noise (default);
    * 1 - Random noise with amplitude of :obj:`init_noise`;
    * 2 - Random noise with fixed seed
      (important for reproducibility, development and debugging)
      and amplitude of :obj:`init_noise`.

    Notes
    -----
        The exactly behavior may be different according to each flow configuration.
    """

    nx, ny, nz = [
        traitlets.Int(default_value=17, min=0).tag(
            group="BasicParam", desc=f"Number of mesh points in {name} direction"
        )
        for name in "x y z".split()
    ]
    """int: Number of mesh points.

    Notes
    -----
        See :obj:`possible_mesh` and :obj:`possible_mesh_p`.
    """

    xlx, yly, zlz = [
        traitlets.Float(default_value=1.0, min=0).tag(
            group="BasicParam", desc=f"Domain size in {name} direction"
        )
        for name in "x y z".split()
    ]
    """float: Domain size.
    """

    # Docstrings included together with the class
    nclx1 = traitlets.Int(default_value=2, min=0, max=2).tag(
        group="BasicParam", desc="Velocidy boundary condition where x=0"
    )

    # Docstrings included together with the class
    nclxn = traitlets.Int(default_value=2, min=0, max=2).tag(
        group="BasicParam", desc="Velocidy boundary condition where x=xlx"
    )

    # Docstrings included together with the class
    ncly1, nclyn, nclz1, nclzn = [
        traitlets.Int(default_value=2, min=0, max=2).tag(
            group="BasicParam", desc=f"Velocidy boundary condition where {name}"
        )
        for name in "y=0 y=yly z=0 z=zlz".split()
    ]

    # Docstrings included together with the class
    ivisu, ipost, ilesmod = [traitlets.Bool(default_value=True) for i in range(3)]

    istret = traitlets.Int(default_value=0, min=0, max=3).tag(group="BasicParam")
    """int: Controls mesh refinement in **y**:

    * 0 - No refinement (default);
    * 1 - Refinement at the center;
    * 2 - Both sides;
    * 3 - Just near the bottom.

    Notes
    -----
        See :obj:`beta`.
    """

    beta = traitlets.Float(default_value=1.0, min=0).tag(group="BasicParam")
    """float: Refinement factor in **y**.

    Notes
    -----
        Only necessary if :obj:`istret` :math:`\\ne` 0.
    """

    dt = traitlets.Float(default_value=1e-3, min=0.0).tag(group="BasicParam")
    """float: Time step :math:`(\\Delta t)`.
    """

    # Docstrings included together with the class
    ifirst, ilast = [
        traitlets.Int(default_value=0, min=0).tag(group="BasicParam")
        for name in ["ifirst", "ilast"]
    ]

    re = traitlets.Float(default_value=1e3).tag(group="BasicParam")
    """float: Reynolds number :math:`(Re)`.
    """

    init_noise = traitlets.Float(default_value=0.0).tag(group="BasicParam")
    """float: Random number amplitude at initial condition.

    Notes
    -----
        The exactly behavior may be different according to each flow configuration.

        Only necessary if :obj:`iin` :math:`\\ne` 0.
    """

    inflow_noise = traitlets.Float(default_value=0.0).tag(group="BasicParam")
    """float: Random number amplitude at inflow boundary (where :math:`x=0`).

    Notes
    -----
        Only necessary if :obj:`nclx1` is equal to 2.
    """

    ilesmod, ivisu, ipost = [
        traitlets.Int(default_value=1, min=0, max=1).tag(group="BasicParam")
        for name in ["ilesmod", "ivisu", "ipost"]
    ]

    iibm = traitlets.Int(default_value=0, min=0, max=2).tag(group="BasicParam")
    """int: Enables Immersed Boundary Method (IBM):

    * 0 - Off (default);
    * 1 - On with direct forcing method, i.e.,
      it sets velocity to zero inside the solid body;
    * 2 - On with alternating forcing method, i.e, it uses
      Lagrangian Interpolators to define the velocity inside the body
      and imposes no-slip condition at the solid/fluid interface.
    """

    numscalar = traitlets.Int(default_value=0, min=0, max=9).tag(group="BasicParam")
    """int: Number of scalar fraction, which can have different properties.

    Notes
    -----
        More than 9 will bug Xcompact3d, because it handles the I/O for
        scalar fields with just one digit
    """

    gravx, gravy, gravz = [
        traitlets.Float(default_value=0.0).tag(group="BasicParam")
        for name in ["gravx", "gravy", "gravz"]
    ]
    """float: Component of the unitary vector pointing in the gravity's direction.
    """

    #
    # # NumOptions
    #

    ifirstder = traitlets.Int(default_value=4, min=1, max=4).tag(group="NumOptions")
    """int: Scheme for first order derivative:

    * 1 - 2nd central;
    * 2 - 4th central;
    * 3 - 4th compact;
    * 4 - 6th compact (default).
    """

    isecondder = traitlets.Int(default_value=4, min=1, max=5).tag(group="NumOptions",)
    """int: Scheme for second order derivative:

    * 1 - 2nd central;
    * 2 - 4th central;
    * 3 - 4th compact;
    * 4 - 6th compact (default);
    * 5 - Hyperviscous 6th.
    """

    ipinter = traitlets.Int(3)

    itimescheme = traitlets.Int(default_value=3, min=1, max=7).tag(group="NumOptions")
    """int: Time integration scheme:

    * 1 - Euler;
    * 2 - AB2;
    * 3 - AB3 (default);
    * 5 - RK3;
    * 7 - Semi-implicit.
    """

    nu0nu = traitlets.Float(default_value=4, min=0.0).tag(group="NumOptions")
    """float: Ratio between hyperviscosity/viscosity at nu.
    """

    cnu = traitlets.Float(default_value=0.44, min=0.0).tag(group="NumOptions")
    """float: Ratio between hypervisvosity at :math:`k_m=2/3\\pi` and :math:`k_c= \\pi`.
    """

    #
    # # InOutParam
    #

    irestart = traitlets.Int(default_value=0, min=0, max=1).tag(group="InOutParam")
    """int: Reads initial flow field if equals to 1.
    """

    nvisu = traitlets.Int(default_value=1, min=1).tag(group="InOutParam")
    """int: Size for visual collection.
    """

    icheckpoint, ioutput, iprocessing = [
        traitlets.Int(default_value=1000, min=1).tag(group="InOutParam")
        for i in range(3)
    ]

    ifilenameformat = traitlets.Int(default_value=9, min=1)

    #
    # # ScalarParam
    #

    _iscalar = traitlets.Bool(False)

    # Include widgets for list demands some planning about code design
    sc = traitlets.List(trait=traitlets.Float()).tag(group="ScalarParam")
    """:obj:`list` of :obj:`float`: Schmidt number(s).
    """

    ri = traitlets.List(trait=traitlets.Float()).tag(group="ScalarParam")
    """:obj:`list` of :obj:`float`: Richardson number(s).
    """

    uset = traitlets.List(trait=traitlets.Float()).tag(group="ScalarParam")
    """:obj:`list` of :obj:`float`: Settling velocity(s).
    """

    cp = traitlets.List(trait=traitlets.Float()).tag(group="ScalarParam")
    """:obj:`list` of :obj:`float`: Initial concentration(s).
    """

    scalar_lbound = traitlets.List(trait=traitlets.Float(default_value=-1e6)).tag(
        group="ScalarParam"
    )
    """:obj:`list` of :obj:`float`: Lower scalar bound(s), for clipping methodology.
    """

    scalar_ubound = traitlets.List(trait=traitlets.Float(default_value=1e6)).tag(
        group="ScalarParam"
    )
    """:obj:`list` of :obj:`float`: Upper scalar bound(s), for clipping methodology.
    """

    iibmS = traitlets.Int(default_value=0, min=0, max=3).tag(group="ScalarParam")
    """int: Enables Immersed Boundary Method (IBM) for scalar field(s):

    * 0 - Off (default);
    * 1 - On with direct forcing method, i.e.,
      it sets scalar concentration to zero inside the solid body;
    * 2 - On with alternating forcing method, i.e, it uses
      Lagrangian Interpolators to define the scalar field inside the body
      and imposes zero value at the solid/fluid interface.
    * 3 - On with alternating forcing method, but now the Lagrangian
      Interpolators are set to impose no-flux for the scalar field at the
      solid/fluid interface.

      .. note:: It is only recommended if the normal vectors to the object's
            faces are aligned with one of the coordinate axes.
    """

    # Docstrings included together with the class
    nclxS1, nclxSn, nclyS1, nclySn, nclzS1, nclzSn = [
        traitlets.Int(default_value=2, min=0, max=2).tag(group="ScalarParam")
        for name in ["nclxS1", "nclxSn", "nclyS1", "nclySn", "nclzS1", "nclzSn"]
    ]

    #
    # # LESModel
    #

    jles = traitlets.Int(default_value=0, min=0, max=4).tag(group="LESModel")
    """int: Chooses LES model, they are:

    * 0 - No model (DNS);
    * 1 - Phys Smag;
    * 2 - Phys WALE;
    * 3 - Phys dyn. Smag;
    * 4 - iSVV.

    """
    #
    # # ibmstuff
    #

    nobjmax = traitlets.Int(default_value=1, min=0).tag(group="ibmstuff")
    """int: Maximum number of objects in any direction. It is defined
        automatically at :obj:`gene_epsi_3D`.
    """

    nraf = traitlets.Int(default_value=10, min=1).tag(group="ibmstuff")
    """int: Refinement constant.
    """

    # Auxiliar
    filename = traitlets.Unicode(default_value="input.i3d").tag()
    """str: Filename for the ``.i3d`` file.
    """

    _mx, _my, _mz = [traitlets.Int(default_value=1, min=1) for i in range(3)]

    dx, dy, dz = [
        traitlets.Float(default_value=0.0625, min=0.0).tag() for dir in "x y z".split()
    ]
    """float: Mesh resolution.
    """

    _nclx, _ncly, _nclz = [traitlets.Bool() for i in range(3)]
    """bool: Auxiliar variable for boundary condition,
        it is :obj:`True` if Periodic and :obj:`False` otherwise.
    """

    _possible_mesh_x, _possible_mesh_y, _possible_mesh_z = [
        traitlets.List(trait=traitlets.Int(), default_value=possible_mesh)
        for i in range(3)
    ]
    """:obj:`list` of :obj:`int`: Auxiliar variable for mesh points widgets,
        it stores the avalilable options according to the boudary conditions.
    """

    ncores = traitlets.Int(default_value=4, min=1).tag()
    """int: Number of computational cores where Xcompact3d will run.
    """

    _possible_p_row, _possible_p_col = [
        traitlets.List(trait=traitlets.Int(), default_value=list(divisorGenerator(4)))
        for i in range(2)
    ]
    """:obj:`list` of :obj:`int`: Auxiliar variable for parallel domain decomposition,
        it stores the avalilable options according to :obj:`ncores`.
    """

    # cfl = traitlets.Float(0.0)
    size = traitlets.Unicode().tag()
    """str: Auxiliar variable indicating the demanded space in disc
    """

    def __init__(self, **kwargs):
        """Initializes the Parameters Class.

        Parameters
        ----------
        **kwargs
            Keyword arguments for valid atributes.

        Raises
        -------
        KeyError
            Exception is raised when an Keyword arguments is not a valid atribute.

        Examples
        -------

        There are a few ways to initialize the class.

        First, calling it with no
        arguments initializes all variables with default value:

        >>> prm = xcompact3d_toolbox.Parameters()

        It is possible to set any values afterwards (including new atributes):

        >>> prm.re = 1e6

        Second, we can specify some values, and let the missing ones be
        initialized with default value:

        >>> prm = x3d.Parameters(
        ...     filename = 'example.i3d',
        ...     itype = 10,
        ...     nx = 257,
        ...     ny = 129,
        ...     nz = 32,
        ...     xlx = 15.0,
        ...     yly = 10.0,
        ...     zlz = 3.0,
        ...     nclx1 = 2,
        ...     nclxn = 2,
        ...     ncly1 = 1,
        ...     nclyn = 1,
        ...     nclz1 = 0,
        ...     nclzn = 0,
        ...     re = 300.0,
        ...     init_noise = 0.0125,
        ...     dt = 0.0025,
        ...     ilast = 45000,
        ...     ioutput = 200,
        ...     iprocessing = 50
        ... )

        And finally, it is possible to read the parameters from the disc:

        >>> prm = xcompact3d_toolbox.Parameters(filename = 'example.i3d')
        >>> prm.read()

        """

        super(Parameters, self).__init__()

        # Boundary conditions are high priority in order to avoid bugs
        for bc in "nclx1 nclxn ncly1 nclyn nclz1 nclzn".split():
            if bc in kwargs:
                setattr(self, bc, kwargs[bc])

        if "loadfile" in kwargs.keys():
            self.filename = kwargs["loadfile"]
            self.load()
            del kwargs["loadfile"]

        for key, arg in kwargs.items():
            if key not in self.trait_names():
                warnings.warn(f"{key} is not a valid parameter and was not loaded")
            setattr(self, key, arg)

    def __repr__(self):

        dictionary = {}
        for name in self.trait_names():
            group = self.trait_metadata(name, "group")
            if group != None:
                if group not in dictionary.keys():
                    dictionary[group] = {}
                dictionary[group][name] = getattr(self, name)
        string = ""

        string += "! -*- mode: f90 -*-\n"

        for blockkey, block in dictionary.items():
            if blockkey == "auxiliar":
                continue

            string += "\n"
            string += "!===================\n"
            string += "&" + blockkey + "\n"
            string += "!===================\n"
            string += "\n"

            for paramkey, param in block.items():
                # Check if param is a list or not
                if isinstance(param, list):
                    for n, p in enumerate(param):
                        string += f"{paramkey+'('+str(n+1)+')':>15} = {p:<15} {'! '+description.get(paramkey,'')}\n"
                # Check if param is a string
                elif isinstance(param, str):
                    param = "'" + param + "'"
                    string += f"{paramkey:>15} = {param:<15} {'! '+description.get(paramkey,'')}\n"
                else:
                    string += f"{paramkey:>15} = {param:<15} {'! '+description.get(paramkey,'')}\n"
            string += "\n"
            string += "/End\n"

        return string

    @traitlets.validate("nx")
    def _validade_mesh_nx(self, proposal):
        _validate_mesh(proposal["value"], self._nclx, self.nclx1, self.nclxn, "x")
        return proposal["value"]

    @traitlets.validate("ny")
    def _validade_mesh_ny(self, proposal):
        _validate_mesh(proposal["value"], self._ncly, self.ncly1, self.nclyn, "y")
        return proposal["value"]

    @traitlets.validate("nz")
    def _validade_mesh_nz(self, proposal):
        _validate_mesh(proposal["value"], self._nclz, self.nclz1, self.nclzn, "z")
        return proposal["value"]

    @traitlets.observe("dx", "nx", "xlx", "dy", "ny", "yly", "dz", "nz", "zlz")
    def _observe_resolution(self, change):
        # for name in "name new old".split():
        #     print(f"    {name:>5} : {change[name]}")

        dim = change["name"][-1]  # It will be x, y or z
        #
        if change["name"] == f"n{dim}":
            if getattr(self, f"_ncl{dim}"):
                setattr(self, f"_m{dim}", change["new"])
            else:
                setattr(self, f"_m{dim}", change["new"] - 1)
            setattr(
                self,
                f"d{dim}",
                getattr(self, f"{dim}l{dim}") / getattr(self, f"_m{dim}"),
            )
        if change["name"] == f"d{dim}":
            new_l = change["new"] * getattr(self, f"_m{dim}")
            if new_l != getattr(self, f"{dim}l{dim}"):
                setattr(self, f"{dim}l{dim}", new_l)
        if change["name"] == f"{dim}l{dim}":
            new_d = change["new"] / getattr(self, f"_m{dim}")
            if new_d != getattr(self, f"d{dim}"):
                setattr(self, f"d{dim}", new_d)

    @traitlets.observe(
        "nclx1",
        "nclxn",
        "nclxS1",
        "nclxSn",
        "ncly1",
        "nclyn",
        "nclyS1",
        "nclySn",
        "nclz1",
        "nclzn",
        "nclzS1",
        "nclzSn",
    )
    def _observe_bc(self, change):
        #
        dim = change["name"][3]  # It will be x, y or z
        #
        if change["new"] == 0:
            for i in f"ncl{dim}1 ncl{dim}n ncl{dim}S1 ncl{dim}Sn".split():
                setattr(self, i, 0)
            setattr(self, f"_ncl{dim}", True)
        if change["old"] == 0 and change["new"] != 0:
            for i in f"ncl{dim}1 ncl{dim}n ncl{dim}S1 ncl{dim}Sn".split():
                setattr(self, i, change["new"])
            setattr(self, f"_ncl{dim}", False)

    @traitlets.observe("_nclx", "_ncly", "_nclz")
    def _observe_periodicity(self, change):
        #
        dim = change["name"][-1]  # It will be x, y or z
        #
        if change["new"]:
            tmp = getattr(self, f"n{dim}") - 1
            setattr(self, f"_possible_mesh_{dim}", possible_mesh_p)
            setattr(self, f"n{dim}", tmp)
        else:
            tmp = getattr(self, f"n{dim}") + 1
            setattr(self, f"_possible_mesh_{dim}", possible_mesh)
            setattr(self, f"n{dim}", tmp)

    @traitlets.observe("p_row", "p_col", "ncores")
    def _observe_2Decomp(self, change):
        if change["name"] == "ncores":
            possible = list(divisorGenerator(change["new"]))
            self._possible_p_row = possible
            self._possible_p_col = possible
            self.p_row, self.p_col = 0, 0
        elif change["name"] == "p_row":
            try:
                self.p_col = self.ncores // self.p_row
            except:
                self.p_col = 0
        elif change["name"] == "p_col":
            try:
                self.p_row = self.ncores // self.p_col
            except:
                self.p_row = 0

    @traitlets.observe("ilesmod")
    def _observe_ilesmod(self, change):
        if change["new"] == 0:
            self.nu0nu, self.cnu, self.isecondder = 4.0, 0.44, 4
            self.trait_metadata("nu0nu", "widget").disabled = True
            self.trait_metadata("cnu", "widget").disabled = True
            self.trait_metadata("isecondder", "widget").disabled = True
        else:
            self.trait_metadata("nu0nu", "widget").disabled = False
            self.trait_metadata("cnu", "widget").disabled = False
            self.trait_metadata("isecondder", "widget").disabled = False

    @traitlets.observe("numscalar")
    def _observe_numscalar(self, change):
        self._iscalar = True if change["new"] == 0 else False

    @traitlets.observe(
        "numscalar",
        "nx",
        "ny",
        "nz",
        "nvisu",
        "icheckpoint",
        "ioutput",
        "iprocessing",
        "ilast",
    )
    def _observe_size(self, change):
        def convert_bytes(num):
            """
            this function will convert bytes to MB.... GB... etc
            """
            step_unit = 1000.0  # 1024 bad the size

            for x in ["bytes", "KB", "MB", "GB", "TB"]:
                if num < step_unit:
                    return "%3.1f %s" % (num, x)
                num /= step_unit

        prec = 4 if param["mytype"] == np.float32 else 8

        # Restart Size from tools.f90
        count = 3 + self.numscalar  # ux, uy, uz, phi
        # Previous time-step if necessary
        if self.itimescheme in [3, 7]:
            count *= 3
        elif self.itimescheme == 2:
            count *= 2
        count += 1  # pp
        count *= (
            self.nx * self.ny * self.nz * prec * (self.ilast // self.icheckpoint - 1)
        )

        # 3D from visu.f90: ux, uy, uz, pp and phi
        count += (
            (4 + self.numscalar)
            * self.nx
            * self.ny
            * self.nz
            * prec
            * self.ilast
            // self.ioutput
        )

        # 2D planes from BC.Sandbox.f90
        if self.itype == 10:
            # xy planes avg and central plane for ux, uy, uz and phi
            count += (
                2
                * (3 + self.numscalar)
                * self.nx
                * self.ny
                * prec
                * self.ilast
                // self.iprocessing
            )
            # xz planes avg, top and bot for ux, uy, uz and phi
            count += (
                3
                * (3 + self.numscalar)
                * self.nx
                * self.nz
                * prec
                * self.ilast
                // self.iprocessing
            )

        self.size = convert_bytes(count)

    def get_boundary_condition(self, var=""):
        """This method returns the appropriate boundary parameters that are
        expected by the derivative functions.

        Parameters
        ----------
        var : str
            Variable name (the default is ""). The supported options are `ux`,
            `uy`, `uz`, `pp` and `phi`, otherwise the method returns a default
            option.

        Returns
        -------
        dict
            Constants the boundary conditions for the desired variable.

        Examples
        -------

        >>> prm = x3d.Parameters()
        >>> prm.get_boundary_condition('ux')
        {'x': {'ncl1': 1, 'ncln': 1, 'npaire': 0},
        'y': {'ncl1': 1, 'ncln': 2, 'npaire': 1, 'istret': 0, 'beta': 0.75},
        'z': {'ncl1': 0, 'ncln': 0, 'npaire': 1}}

        >>> DataArray.attrs['BC'] = prm.get_boundary_condition('ux')

        >>> DataArray.x3d.first_derivative('x')
        """

        return boundary_condition(self, var)

    def load(self):
        """Loads all valid attributes from the parameters file.

        An attribute is considered valid if it has a ``tag`` named ``group``,
        witch assigns it to the respective namespace at the ``.i3d`` file.

        It also includes support for the previous format ``.prm``.

        Examples
        -------

        >>> prm = xcompact3d_toolbox.Parameters(filename = 'example.i3d')
        >>> prm.load()

        or just:
        >>> prm = xcompact3d_toolbox.Parameters(loadfile = 'example.i3d')

        """

        if self.filename.split(".")[-1] == "i3d":
            dictionary = {}

            # unpacking the nested dictionary
            for key_out, value_out in i3d_to_dict(self.filename).items():
                for key_in, value_in in value_out.items():
                    dictionary[key_in] = value_in

        elif self.filename.split(".")[-1] == "prm":
            dictionary = prm_to_dict(self.filename)

        else:
            raise IOError(
                f"{self.filename} is invalid. Supported formats are .i3d and .prm."
            )

        # Boundary conditions are high priority in order to avoid bugs
        for bc in "nclx1 nclxn ncly1 nclyn nclz1 nclzn".split():
            if bc in dictionary:
                setattr(self, bc, dictionary[bc])

        for key, value in dictionary.items():
            try:
                if self.trait_metadata(key, "group") != None:
                    setattr(self, key, dictionary[key])
            except:
                warnings.warn(f"{key} is not a valid parameter and was not loaded")

    def read(self):
        """See :obj:`xcompact3d_toolbox.Parameters.load`."""
        warnings.warn("read is deprecated, use load", DeprecationWarning)
        self.load()

    def write(self):
        """Writes all valid attributes to an ``.i3d`` file.

        An attribute is considered valid if it has a ``tag`` named ``group``,
        witch assigns it to the respective namespace at the ``.i3d`` file.

        Examples
        -------

        >>> prm = xcompact3d_toolbox.Parameters(filename = 'example.i3d'
        ...     nx = 101,
        ...     ny = 65,
        ...     nz = 11,
        ...     # end so on...
        ... )
        >>> prm.write()

        """
        if self.filename.split(".")[-1] == "i3d":
            with open(self.filename, "w", encoding="utf-8") as file:
                file.write(self.__str__())
        else:
            raise filename("Format error, only .i3d is supported")

    def write_xdmf(self):
        """Writes four xdmf files:

        * ``./data/3d_snapshots.xdmf`` for 3D snapshots in ``./data/3d_snapshots/*``;
        * ``./data/xy_planes.xdmf`` for planes in ``./data/xy_planes/*``;
        * ``./data/xz_planes.xdmf`` for planes in ``./data/xz_planes/*``;
        * ``./data/yz_planes.xdmf`` for planes in ``./data/yz_planes/*``.

        Shape and time are inferted from folder structure and filenames.
        File list is obtained automatically with :obj:`glob`.

        .. note:: This is only compatible with the new filename structure,
            the conversion is exemplified in `convert_filenames_x3d_toolbox`_.

        .. _`convert_filenames_x3d_toolbox`: https://gist.github.com/fschuch/5a05b8d6e9787d76655ecf25760e7289

        Parameters
        ----------
        prm : :obj:`xcompact3d_toolbox.parameters.Parameters`
            Contains the computational and physical parameters.

        Examples
        -------

        >>> prm = x3d.Parameters()
        >>> prm.write_xdmf()

        """
        write_xdmf(self)

    @property
    def get_mesh(self):
        """Get mesh point locations for the three coordinates.

        Returns
        -------
        :obj:`dict` of :obj:`numpy.ndarray`
            It contains the mesh point locations at three dictionary keys,
            for **x**, **y** and **z**.

        Examples
        -------

        >>> prm = xcompact3d_toolbox.Parameters()
        >>> prm.get_mesh

        """
        return get_mesh(self)


def _validate_mesh(n, ncl, ncl1, ncln, dim):

    pmin = 8 if ncl else 9

    if n < pmin:
        # Because of the derivatives' stencil
        raise traitlets.TraitError(f"{n} is invalid, n{dim} must be larger than {pmin}")

    if not ncl:
        n = n - 1

    if n % 2 == 0:
        n //= 2

        for val in [2, 3, 5]:
            while True:
                if n % val == 0:
                    n //= val
                else:
                    break

    if n != 1:
        # Because of the FFT library
        raise traitlets.TraitError(f"Invalid value for mesh points (n{dim})")


description = dict(
    # Basic Parameters
    p_row="Domain decomposition for parallel computation",
    p_col="Domain decomposition for parallel computation",
    itype="Flow configuration (Taylor-Green Vortex,  Flow around a Cylinder...)",
    nx="Number of mesh points in x direction",
    ny="Number of mesh points in y direction",
    nz="Number of mesh points in z direction",
    xlx="Domain size in x direction",
    yly="Domain size in y direction",
    zlz="Domain size in z direction",
    nclx1="Velocidy boundary condition at begin of x direction",
    nclxn="Velocidy boundary condition at end of x direction",
    ncly1="Velocidy boundary condition at begin of y direction",
    nclyn="Velocidy boundary condition at end of y direction",
    nclz1="Velocidy boundary condition at begin of z direction",
    nclzn="Velocidy boundary condition at end of z direction",
    istret="Mesh refinement in y direction at certain location",
    beta="Refinement parameter",
    iin="Defines pertubation at initial condition",
    re="Reynolds number",
    init_noise="Value to initial noise, turbulence intensity",
    inflow_noise="Random amplitude value at inflow boundary, turbulence intensity",
    dt="Value to time step",
    ifirst="Value to first iteration",
    ilast="Value to last iteration",
    ilesmod="Enables Large-Eddy methodologies",
    iscalar="Enables scalar fields",
    numscalar="Number of scalar fractions",
    iibm="Immersed boundary configuration for velocity",
    ilmn="Enables Low Mach Number methodology (compressible flows)",
    ivisu="Enable store snapshots",
    ipost="Enables online postprocessing",
    gravx="Value to x component in gravity unitary vector",
    gravy="Value to y component in gravity unitary vector",
    gravz="Value to z component in gravity unitary vector",
    # Numeric Options
    ifirstder="Scheme for first order derivative",
    isecondder="Scheme for second order derivative",
    itimescheme="Scheme for time integration",
    nu0nu="Ratio between hyperviscosity/viscosity at nu (dissipation factor intensity)",
    cnu="Ratio between hypervisvosity at km=2/3π and kc=π (dissipation factor range)",
    # In/Out Parameters
    irestart="Flag to read initial flow field",
    icheckpoint="Frequency for writing backup file",
    ioutput="Frequency for visualization file",
    nvisu="Size for visual collection",
    iprocessing="Frequency for online postprocessing",
    # Statistics
    spinup_time="Time in seconds after which statistics are collected",
    nstat="Statistic array size",
    wrotation="Rotation speed to trigger turbulence",
    # Scalar Parameters
    nclxS1="Scalar boundary condition at begin of x direction",
    nclxSn="Scalar boundary condition at end of x direction",
    nclyS1="Scalar boundary condition at begin of y direction",
    nclySn="Scalar boundary condition at end of y direction",
    nclzS1="Scalar boundary condition at begin of z direction",
    nclzSn="Scalar boundary condition at end of z direction",
    sc="Schmidt number(s)",
    ri="Richardson number(s)",
    uset="Settling velocity(ies)",
    cp="Initial concentration(s)",
    iibmS="Immersed boundary configuration for scalar (alpha version)",
    scalar_lbound="Lower scalar bound",
    scalar_ubound="Upper scalar bound",
    # LES Model
    jles="LES model",
    smagcst="Value to Smagorinsky constant",
    # IBM stuff
    nraf="Refinement constant which each axis will be multiplicated",
    nobjmax="Maximum number of objects in any direction",
    # Force balance
    iforces="Flag to drag and sustentation coefficients",
    nvol="Number of volumes for computing force balance",
    xld="Volume left bound",
    xrd="Volume right bound",
    yld="Volume lower bound",
    yud="Volume upper bound",
)
