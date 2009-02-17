#!/usr/bin/env python

"""Calls the main function of bbob_pproc with arguments from the
   command line. Executes the BBOB postprocessing on the given
   filename and folder arguments, using all found .info files.
Synopsis:
    python path_to_folder/bbob_pproc/run.py [OPTIONS] FILE_NAME FOLDER_NAME...
Help:
    python path_to_folder/bbob_pproc/run.py -h

"""

# this script should probably replace ../bbob_pproc.py in future?

from __future__ import absolute_import

import os
import sys
import getopt
from pdb import set_trace

# Add the path to bbob_pproc
if __name__ == "__main__":
    # append path without trailing '/bbob_pproc', using os.sep fails in mingw32
    #sys.path.append(filepath.replace('\\', '/').rsplit('/', 1)[0])
    (filepath, filename) = os.path.split(sys.argv[0])
    #Test system independent method:
    sys.path.append(os.path.join(filepath, os.path.pardir))

from bbob_pproc.readindexfiles import IndexEntries
from bbob_pproc import pproc, pptex, pprldistr, ppfigdim

# GLOBAL VARIABLES used in the routines defining desired output  for BBOB 2009.
tabDimsOfInterest = [5, 20]    # dimension which are displayed in the tables
# tabValsOfInterest = (1.0, 1.0e-2, 1.0e-4, 1.0e-6, 1.0e-8)
tabValsOfInterest = (10, 1.0, 1e-1, 1e-3, 1e-5, 1.0e-8)
# tabValsOfInterest = (10, 1.0, 1e-1, 1.0e-4, 1.0e-8)  # 1e-3 1e-5

#figValsOfInterest = (10, 1e-1, 1e-4, 1e-8)
figValsOfInterest = (10, 1, 1e-1, 1e-2, 1e-3, 1e-5, 1e-8)

rldDimsOfInterest = (5, 20)
rldValsOfInterest = (10, 1e-1, 1e-4, 1e-8)
#Put backward to have the legend in the same order as the lines.

#CLASS DEFINITIONS

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


#FUNCTION DEFINITIONS

def usage():
    print main.__doc__


def main(argv=None):
    """Generates from BBOB experiment data some outputs for a tex document.

    If provided with some index entries (from info files), this should return
    many output files in the folder 'ppdata' needed for the compilation of
    latex document templateBBOBarticle.tex. These output files will contain
    performance tables, performance scaling figures and empirical cumulative
    distribution figures.

    Keyword arguments:
    argv -- list of strings containing options and arguments.

    argv should list either names of info files or folders containing info
    files. argv can also list post-processed pickle files generated from this
    method. Furthermore, argv can begin with, in any order, facultative option
    flags listed below.

        -h, --help

            display this message

        -v, --verbose

            verbose mode, prints out operations. When not in verbose mode, no
            output is to be expected, except for errors.

        -n, --no-pickle

            prevents pickled post processed data files from being generated.

        -o, --output-dir OUTPUTDIR

            change the default output directory ('ppdata') to OUTPUTDIR

        --tab-only, --fig-only, --rld-only

            these options can be used to output respectively the tex tables,
            convergence and ENFEs graphs figures, run length distribution
            figures only. A combination of any two of these options results in
            no output.

    Exceptions raised:
    Usage --


    Examples:

    * Calling the bbob_pproc.py interface from the command line:

        $ python bbob_pproc.py OPTIONS DATA_TO_PROCESS1 DATA_TO_PROCESS2...

    * Loading this package and calling the main from the command line
      (requires that the path to this package is in python search path):

        $ python -m bbob_pproc OPTIONS DATA_TO_PROCESS1...

    * From the python interactive shell (requires that the path to this
      package is in python search path):

        >>> import bbob_pproc
        >>> python bbob_pproc.main(['', 'OPT1', 'OPT2', 'data_to_process_1',
                                    'data_to_process_2', ...])

    """

    if argv is None:
        argv = sys.argv
    try:

        try:
            opts, args = getopt.getopt(argv[1:], "hvno:",
                                       ["help", "output-dir",
                                        "tab-only", "fig-only", "rld-only",
                                        "no-pickle","verbose"])
        except getopt.error, msg:
             raise Usage(msg)

        if not (args):
            usage()
            sys.exit()

        isfigure = True
        istab = True
        isrldistr = True
        isPostProcessed = False
        isPickled = True
        verbose = False
        outputdir = 'ppdata'

        #Process options
        for o, a in opts:
            if o in ("-v","--verbose"):
                verbose = True
            elif o in ("-h", "--help"):
                usage()
                sys.exit()
            elif o in ("-n", "--no-pickle"):
                isPickled = False
            elif o in ("-o", "--output-dir"):
                outputdir = a
            #The next 3 are for testing purpose
            elif o == "--tab-only":
                isfigure = False
                isrldistr = False
            elif o == "--fig-only":
                istab = False
                isrldistr = False
            elif o == "--rld-only":
                istab = False
                isfigure = False
            else:
                assert False, "unhandled option"

        indexEntries = IndexEntries(args, verbose)
        #set_trace()
        sortedByAlg = indexEntries.sortByAlg()
        if len(sortedByAlg) > 1:
            warnings.warn('Data with multiple algId %s ' % (sortedByAlg) +
                          'will be processed together.')


        if isPickled or isfigure or istab or isrldistr:
            if not os.path.exists(outputdir):
                os.mkdir(outputdir)
                if verbose:
                    print '%s was created.' % (outputdir)

        if isPickled:
            indexEntries.pickle(outputdir, verbose)

        if isfigure:
            ppfigdim.main(indexEntries, figValsOfInterest, outputdir,
                          verbose)

        if istab:
            sortedByFunc = indexEntries.sortByFunc()
            for fun, sliceFun in sortedByFunc.items():
                sortedByDim = sliceFun.sortByDim()
                tmp = []
                for dim in tabDimsOfInterest:
                    try:
                        if len(sortedByDim[dim]) > 1:
                            warnings.warn('Func: %d, DIM %d: ' % (fun, dim) +
                                          'multiple index entries. Will only '+
                                          'process the first ' +
                                          '%s.' % sortedByDim[dim][0])
                        tmp.append(sortedByDim[dim][0])
                    except KeyError:
                        pass
                if tmp:
                    filename = os.path.join(outputdir,'ppdata_f%d' % fun)
                    pptex.main(tmp, tabValsOfInterest, filename, verbose)

        if isrldistr:
            sortedByDim = indexEntries.sortByDim()
            for dim, sliceDim in sortedByDim.items():
                if dim in rldDimsOfInterest:
                    pprldistr.main(sliceDim, rldValsOfInterest,
                                   outputdir, 'dim%02dall' % dim, verbose)
                    sortedByFG = sliceDim.sortByFuncGroup()
                    #set_trace()
                    for fGroup, sliceFuncGroup in sortedByFG.items():
                        pprldistr.main(sliceFuncGroup, rldValsOfInterest,
                                       outputdir, 'dim%02d%s' % (dim, fGroup),
                                       verbose)

        if verbose:
            tmp = []
            tmp.extend(tabValsOfInterest)
            tmp.extend(figValsOfInterest)
            tmp.extend(rldValsOfInterest)
            if indexEntries:
                print ('total ps = %g\n'
                       % indexEntries.successProbability(min(tmp)))

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use -h or --help"
        return 2


if __name__ == "__main__":
   sys.exit(main())
