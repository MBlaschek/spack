# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install rttov
#
# You can edit this file again by typing:
#
#     spack edit rttov
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack import *


class Rttov(Package):
    """Radiative Transfer for TOVS is a very fast radiative transfer model for passive visible, infrared and microwave downward-viewing satellite radiometers, spectrometers and interferometers."""

    homepage = "https://nwp-saf.eumetsat.int/site/software/rttov/"
    url      = "https://gitlab.phaidra.org/dataassimilation/rttov/-/archive/v12.3/rttov-v12.3.tar.gz"

    # notify when the package is updated.
    maintainers = ['blaschm7']

    # version('13.0')
    version('12.3', sha256='a3c81b38ffe53afbbcdc391eb3f3f92ade2daab5475d7c3b822bbd5c31e2702d')
    # version('12.2')
    # version('11.3')

    variant('lapack', default=False, description='Enable Lapack support.')
    variant('hdf5', default=False, description='Enable HDF5 support.')
    variant('netcdf', default=False, description='Enable NetCDF4 support.')
    variant('openmp', default=False, description='Enable OpenMP support.')
    variant('python', default=False, description='Enable Python support.')
    variant('gui', default=False, description='Enable GUI.')
    
    # Minimum Dependencies
    depends_on('perl@5.6:')
    depends_on('lapack', when='+lapack')
    # Optional, however recommended
    depends_on('hdf5', when='+hdf5')
    depends_on('zlib', when='+hdf5')
    depends_on('netcdf-c@4:', when='+netcdf')
    depends_on('netcdf-fortran', when='+netcdf')
    # Python Interface / Wrapper
    depends_on('python@3:', when='+python')
    # GUI maybe needs Python2 in earlier versions?
    depends_on('py-numpy', when='+python')

    def install(self, spec, prefix):
        with working_dir('./src'):
            import subprocess
            subprocess.check_call('../build/Makefile.PL', 'RTTOV_HDF=0', 'RTTOV_F2PY=0', 'RTTOV_USER_LAPACK=0')
            # $ ../build/Makefile.PL RTTOV_HDF=0 RTTOV_F2PY=0 RTTOV_USER_LAPACK=0
            # $ make ARCH=gfortran INSTALLDIR=./ 
            if spec.satisfies('%gcc'):
                if 'openmp' in spec:
                    make('ARCH=gfortran-openmp INSTALLDIR={}'.format(prefix))
                else:
                    make('ARCH=gfortran INSTALLDIR={}'.format(prefix))
            elif spec.satisfies('%intel'):
                if 'openmp' in spec:
                    make('ARCH=ifort-openmp INSTALLDIR={}'.format(prefix))
                else:
                    make('ARCH=ifort INSTALLDIR={}'.format(prefix))
            else:
                make()
                make('install', parallel=False)  # -j Option

    @run_after('install')
    def coefficients(self, spec, prefix):
        pass
        # What about coefficients ?
        # PATH, script, copy ?
        # install(src, dest)

    
    def configure(self, spec):
        with open('./build/Makefile.local', 'w') as f:
            if 'hdf5' in spec:
                f.write('HDF5_PREFIX = ' + spec['hdf5'].prefix)  # HDF5 PREFIX
                # For most compilers:
                f.write('FFLAGS_HDF5  = -D_RTTOV_HDF $(FFLAG_MOD)$(HDF5_PREFIX)/include\n')
                # For xlf on AIX:
                # FFLAGS_HDF5  = -WF,-D_RTTOV_HDF $(FFLAG_MOD)$(HDF5_PREFIX)/include
                # --- Uncomment one LDFLAGS_HDF5 line:
                # In most cases:
                f.write('LDFLAGS_HDF5 = -L$(HDF5_PREFIX)/lib -lhdf5hl_fortran -lhdf5_hl -lhdf5_fortran -lhdf5 -lz\n')
                # (NB for NAG Fortran you may also need to add -ldl)

            if 'netcdf-fortran' in spec:
                f.write('NETCDF_PREFIX = ' + spec['netcdf-fortran'].prefix)  # NETCDF PREFIX
                # For most other compilers:
                f.write('FFLAGS_NETCDF  = -D_RTTOV_NETCDF -I$(NETCDF_PREFIX)/include \n')
                if spec.satisfies('netcdf-c@:4.1.9'):
                    # For NetCDF v4.1:
                    f.write('LDFLAGS_NETCDF = -L$(NETCDF_PREFIX)/lib -lnetcdff -lnetcdf \n')
                if spec.satisfies('netcdf-c@4.2:'):
                    # For NetCDF v4.2 and later:
                    f.write('LDFLAGS_NETCDF = -L$(NETCDF_PREFIX)/lib -lnetcdff \n')
            if 'lapack' in spec:
                f.write('LAPACK_PREFIX = ' + spec['lapack'].prefix + '\n')  # LAPACK
                f.write('FFLAGS_LAPACK = $(FFLAG_MOD)$(LAPACK_PREFIX)/include\n')
                f.write('LDFLAGS_LAPACK = -L$(LAPACK_PREFIX)/lib -llapack\n')
    
