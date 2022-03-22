import pytest
import inspect
from xcompact3d_toolbox.parameters.configparser import BaseParser, ConfigParser


@pytest.fixture
def prm_file():
    return inspect.cleandoc(
        """
        ! -*- mode: f90 -*-

        !===================
        &BasicParam
        !===================

        ! Flow type (1=Lock-exchange, 2=TGV, 3=Channel, 4=Periodic hill, 5=Cylinder, 6=dbg-schemes)
        itype = 1

        C_filter = 0.49

        ! Domain decomposition
        p_row=0               ! Row partition
        p_col=0               ! Column partition

        ! Mesh
        nx=181               ! X-direction nodes
        ny=29                ! Y-direction nodes
        nz=27                ! Z-direction nodes
        istret = 0            ! y mesh refinement (0:no, 1:center, 2:both sides, 3:bottom)
        beta = 0.259065151    ! Refinement parameter (beta)

        ! Domain
        xlx = 18.0            ! Lx (Size of the box in x-direction)
        yly = 2.0             ! Ly (Size of the boy in y-direction)
        zlz = 2.0             ! Lz (Size of the boz in z-direction)

        ! Gravity vector
        gravx = 0.0
        gravy = -1.0
        gravz = 0.0

        ! Boundary conditions
        nclx1 = 1 
        nclxn = 1 
        ncly1 = 2 
        nclyn = 1 
        nclz1 = 1 
        nclzn = 1 

        ! Flow parameters
        iin = 1               ! Inflow conditions (1: classic, 2: turbinit)
        re = 2236.0           ! nu=1/re (Kinematic Viscosity)
        init_noise = 0.01     ! Turbulence intensity (1=100%) !! Initial condition
        inflow_noise = 0.0    ! Turbulence intensity (1=100%) !! Inflow condition

        ! Time stepping
        dt = 0.0048           ! Time step
        ifirst = 1            ! First iteration
        ilast = 100000        ! Last iteration

        ! Enable modelling tools
        ilesmod=0             ! if 0 then DNS
        numscalar=0           ! If iscalar=0 (no scalar), if iscalar=1 (scalar)
        iibm=0                ! Flag for immersed boundary method
        ilmn = .TRUE.         ! Enable low Mach number

        ! Enable io
        ivisu=1               ! Store snapshots
        ipost=1               ! Do online postprocessing
        /End

        !====================
        &NumOptions
        !====================

        ! Spatial derivatives
        ifirstder = 4         ! (1->2nd central, 2->4th central, 3->4th compact, 4-> 6th compact)
        isecondder = 5        ! (1->2nd central, 2->4th central, 3->4th compact, 4-> 6th compact, 5->hyperviscous 6th)
        ipinter = 3
        ! Time scheme
        itimescheme = 2       ! Time integration scheme (1->Euler,2->AB2, 3->AB3, 4->AB4,5->RK3,6->RK4)
        ! Dissipation control
        nu0nu = 4.0             ! Ratio between hyperviscosity/viscosity at nu
        cnu = 0.44               ! Ratio between hypervisvosity at k_m=2/3pi and k_c= pi

        /End

        !=================
        &ScalarParam
        !=================
        
        !! Schmidt numbers
        sc(1) = 1.0
        
        !! Richardson numbers
        ri(1) = 1.0
        
        !! Settling velocities
        uset(1) = 0.02
        
        !! Initial concentrations
        cp(1) = 1.0
        
        /End

        !=================
        &InOutParam
        !=================

        ! Basic I/O
        irestart = 0          ! Read initial flow field ?
        icheckpoint = 5000    ! Frequency for writing backup file
        ioutput = 1667        ! Frequency for visualization
        ilist = 25            ! Frequency for writing on screen
        nvisu = 1             ! Size for visualisation collection
        iprocessing = 20

        /End
        """
    )

def test_baseparser_read(prm_file):
    config = BaseParser()
    config.read_string(prm_file)

def test_configparser_read(prm_file):
    config = ConfigParser(_base_parser=BaseParser())
    config.read_string(prm_file)
