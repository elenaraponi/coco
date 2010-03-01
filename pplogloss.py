#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
These comparisons are based on computing the ratio between an ERT value and a
reference (best) ERT value (or the inverse)

ERT loss ratio of an algorithm A for comparison to BBOB-2009. This works
only as comparison to a set of algorithms that reach at least the same
target values. Let f=f_A(EVALS) be the smallest target value such that the
expected running time of algorithm A was smaller than or equal to EVALS.
Let ERT_A=EVALS, if ERT_best(next difficult f) < EVALS and
ERT_A=ERT_A(f_A(EVALS)) otherwise (we have ERT_A(f_A(EVALS)) <= EVALS).
The ERT loss ratio for algorithm A is defined as:
    Loss_A = stat_fcts(exp(CrE_A) * ERT_A / ERT_best(f))

    + where f is a function of EVALS and stat_fcts is the desired statistics
      over the values from all functions (or a subgroup of functions), for
      example the geometric mean, min, max or any quantile. More specific: we
      plot versus 'the budget EVALS' the geometric mean (line) and Box-Whisker
      error bars at EVALS=2*D, 10*D, 100*D,...: a box between 25% and 75% with
      the median as additional symbol, a line with "T" as end-marker between
      10% and 90% (the box covers the line) and a single point for min, max.
      For a function subgroup the Box-Whisker is replaced with the four or five
      actual points with the function number written.
      Caption: ERT loss ratio: expected running time, ERT (measured in number
      of function evaluations), divided by the best ERT seen in BBOB-2009 for
      the respectively same function and target function value, plotted versus
      number of function evaluations for the functions $f_1$--$f_{24}$ in
      dimension $D=XXX$, corrected by the parameter-crafting-effort
      $\exp(CrE)==YYY$. Line: geometric mean over all functions. Box-Whisker
      error bars: 25-75\%-percentile range with median (box),
      10-90\%-percentile range (line), and minimum and maximum ERT loss ratio
      (points). Alternative Box-Whisker sentence: Points: ERT loss ratio for
      each function
    + The problem: how to find out CrE_A? Possible solution: ask for input in
      the script and put the given number into the caption and put exp(CrE_A)
      as small symbol on the y-axis of the figure for cross-checking.
    + This should make a collection of graphs for all functions and all
      subgroups which gives an additional page in the 'single algorithm'
      template. Respective tables could be side-by-side the graphs.
    + Example for how to read the graph: a loss ratio of 4 for ERT=20D means,
      that the function value reached with ERT=20D could be reached with the
      respective best algorithm in ERT_best=5D function evaluations on average.
      Therefore, given a budget of 20*D function evaluations, the best
      algorithm could have further improved the function value using the
      remaining 15*D ($75\%=1-1/4$) function evaluations.
"""

from __future__ import absolute_import

import os
import warnings
import cPickle as pickle
import gzip
from pdb import set_trace
import numpy
from matplotlib import pyplot as plt
from matplotlib import mlab as mlab

from bbob_pproc import bootstrap
from bbob_pproc.bestalg import BestAlgSet
from bbob_pproc.pptex import writeFEvals2

figformat = ('eps', 'pdf')
f_thresh = 1.e-8
bestalgentries = {}
#bestalgfilepath = os.path.join(os.path.split(__file__)[0], 'bestalg')
#for fun in range(1, 25)+range(101, 131):
    #for D in [2, 3, 5, 10, 20, 40]:
        #picklefilename = os.path.join(bestalgfilepath,
                                      #'bestalg_f%03d_%02d.pickle.gz' % (fun, D))
        ##TODO: what if file is not found?
        #fid = gzip.open(picklefilename, 'r')
        #bestalgentries[(D, fun)] = pickle.load(fid)
        #fid.close()

bestalgfilepath = os.path.split(__file__)[0]
picklefilename = os.path.join(bestalgfilepath, 'bestalgentries2009.pickle.gz')
#TODO: what if file is not found?
fid = gzip.open(picklefilename, 'r')
bestalgentries = pickle.load(fid)
fid.close()

def detERT(entry, funvals):
    res = []
    for f in funvals:
        idx = (entry.target<=f)
        #set_trace()
        try:
            #if numpy.isnan(entry.ert[idx][0]):
                #set_trace()
            res.append(entry.ert[idx][0])
        except IndexError:
            res.append(numpy.inf)
    return res

def detf(entry, evals):
    """Determines a function value given a number of function evaluations.
    Let A be the algorithm considered. Let f=f_A(evals) be the smallest target
    value such that the expected running time of algorithm A was smaller than
    or equal to evals.
    ----
    Keyword arguments:
    entry
    evals -- list of number of function evaluations considered

    Returns:
    res -- list of the target function values
    """

    res = []
    for fevals in evals:
        tmp = (entry.ert <= fevals)
        #set_trace()
        #if len(entry.target[tmp]) == 0:
            #set_trace()
        idx = numpy.argmin(entry.target[tmp])
        res.append(max(entry.target[idx], f_thresh))
        #res2.append(entry.ert[dix])
        #TODO numpy.min(empty)
    return res

def generateData(dsList, evals, CrE_A):
    res = {}

    D = set(i.dim for i in dsList).pop() # should have only one element
    #if D == 5:
    #    set_trace()

    for fun, tmpdsList in dsList.dictByFunc().iteritems():
        entry = tmpdsList[0] # TODO: check for problems

        # Load bestalgentry:
        #picklefilename = os.path.join(bestalgfilepath,
                                      #'bestalg_f%03d_%02d.pickle.gz' % (fun, D))
        ##TODO: what if file is not found?
        #fid = gzip.open(picklefilename, 'r')
        #bestalgentry = pickle.load(fid)
        #fid.close()
        bestalgentry = bestalgentries[(D, fun)]

        #ERT_A
        f_A = detf(entry, evals)

        ERT_best = detERT(bestalgentry, f_A)
        ERT_A = detERT(entry, f_A)
        #runlengths = entry.generateRLData(f_A)
        #for i, f in enumerate(f_A):
            #tmp = numpy.isnan(runlengths)
            #perc, allerts = bootstrap.drawSP(runlengths[i][tmp == False],
                                             #entry.maxevals[tmp],
                                             #percentiles=[0, 10, ,25, 50, 75, 90, 100],
                                             #samplesize=100)
            #res[fun] = perc / ERT_best[i]
        nextbestf = []
        for i in f_A:
            if i == 0.:
                nextbestf.append(0.)
            else:
                tmp = bestalgentry.target[bestalgentry.target < i]
                try:
                    nextbestf.append(tmp[0])
                except IndexError:
                    nextbestf.append(i * 10.**(-0.2)) # TODO: this is a hack
                    #set_trace()

        ERT_best_nextbestf = detERT(bestalgentry, nextbestf)

        for i in range(len(ERT_A)):
            # nextbestf[i] >= f_thresh: this is tested because if it is not true
            # ERT_best_nextbestf[i] is supposed to be infinite.
            if nextbestf[i] >= f_thresh and ERT_best_nextbestf[i] < evals[i]:
                ERT_A[i] = evals[i]

        ERT_A = numpy.array(ERT_A)
        ERT_best = numpy.array(ERT_best)
        #CrE_A = 0 #TODO: set!
        loss_A = numpy.exp(CrE_A) * ERT_A / ERT_best
        #set_trace()
        #if numpy.isnan(loss_A).any() or numpy.isinf(loss_A).any() or (loss_A == 0.).any():
        #    txt = 'Problem with entry %s' % str(entry)
        #    warnings.warn(txt)
        #    #set_trace()
        res[fun] = loss_A

        #set_trace()
    return res

def boxplot(x, notch=0, sym='b+', positions=None, widths=None):
    """
    Adapted from matplotlib.axes 0.98.5.2
    Modified such that the caps are set to the 10th and 90th percentiles.

    call signature::

      boxplot(x, notch=0, sym='+', positions=None, widths=None)

    Make a box and whisker plot for each column of *x* or each
    vector in sequence *x*.  The box extends from the lower to
    upper quartile values of the data, with a line at the median.
    The whiskers extend from the box to show the range of the
    data.  Flier points are those past the end of the whiskers.

    - *notch* = 0 (default) produces a rectangular box plot.
    - *notch* = 1 will produce a notched box plot

    *sym* (default 'b+') is the default symbol for flier points.
    Enter an empty string ('') if you don't want to show fliers.

    *whis* (default 1.5) defines the length of the whiskers as
    a function of the inner quartile range.  They extend to the
    most extreme data point within ( ``whis*(75%-25%)`` ) data range.

    *positions* (default 1,2,...,n) sets the horizontal positions of
    the boxes. The ticks and limits are automatically set to match
    the positions.

    *widths* is either a scalar or a vector and sets the width of
    each box. The default is 0.5, or ``0.15*(distance between extreme
    positions)`` if that is smaller.

    *x* is an array or a sequence of vectors.

    Returns a dictionary mapping each component of the boxplot
    to a list of the :class:`matplotlib.lines.Line2D`
    instances created.

    **Example:**

    .. plot:: pyplots/boxplot_demo.py
    """
    whiskers, caps, boxes, medians, fliers = [], [], [], [], []

    # convert x to a list of vectors
    if hasattr(x, 'shape'):
        if len(x.shape) == 1:
            if hasattr(x[0], 'shape'):
                x = list(x)
            else:
                x = [x,]
        elif len(x.shape) == 2:
            nr, nc = x.shape
            if nr == 1:
                x = [x]
            elif nc == 1:
                x = [x.ravel()]
            else:
                x = [x[:,i] for i in xrange(nc)]
        else:
            raise ValueError, "input x can have no more than 2 dimensions"
    if not hasattr(x[0], '__len__'):
        x = [x]
    col = len(x)

    # get some plot info
    if positions is None:
        positions = range(1, col + 1)
    if widths is None:
        distance = max(positions) - min(positions)
        widths = min(0.15*max(distance,1.0), 0.5)
    if isinstance(widths, float) or isinstance(widths, int):
        widths = numpy.ones((col,), float) * widths

    # loop through columns, adding each to plot
    for i,pos in enumerate(positions):
        d = numpy.ravel(x[i])
        row = len(d)
        # get median and quartiles
        wisk_lo, q1, med, q3, wisk_hi = mlab.prctile(d,[10,25,50,75,90])
        # get high extreme
        #iq = q3 - q1
        #hi_val = q3 + whis*iq
        #wisk_hi = numpy.compress( d <= hi_val , d )
        #if len(wisk_hi) == 0:
            #wisk_hi = q3
        #else:
            #wisk_hi = max(wisk_hi)
        ## get low extreme
        #lo_val = q1 - whis*iq
        #wisk_lo = numpy.compress( d >= lo_val, d )
        #if len(wisk_lo) == 0:
            #wisk_lo = q1
        #else:
            #wisk_lo = min(wisk_lo)
        # get fliers - if we are showing them
        flier_hi = []
        flier_lo = []
        flier_hi_x = []
        flier_lo_x = []
        if len(sym) != 0:
            flier_hi = numpy.compress( d > wisk_hi, d )
            flier_lo = numpy.compress( d < wisk_lo, d )
            flier_hi_x = numpy.ones(flier_hi.shape[0]) * pos
            flier_lo_x = numpy.ones(flier_lo.shape[0]) * pos

        # get x locations for fliers, whisker, whisker cap and box sides
        box_x_min = pos - widths[i] * 0.5
        box_x_max = pos + widths[i] * 0.5

        wisk_x = numpy.ones(2) * pos

        cap_x_min = pos - widths[i] * 0.25
        cap_x_max = pos + widths[i] * 0.25
        cap_x = [cap_x_min, cap_x_max]

        # get y location for median
        med_y = [med, med]

        # calculate 'regular' plot
        if notch == 0:
            # make our box vectors
            box_x = [box_x_min, box_x_max, box_x_max, box_x_min, box_x_min ]
            box_y = [q1, q1, q3, q3, q1 ]
            # make our median line vectors
            med_x = [box_x_min, box_x_max]
        # calculate 'notch' plot
        else:
            notch_max = med + 1.57*iq/numpy.sqrt(row)
            notch_min = med - 1.57*iq/numpy.sqrt(row)
            if notch_max > q3:
                notch_max = q3
            if notch_min < q1:
                notch_min = q1
            # make our notched box vectors
            box_x = [box_x_min, box_x_max, box_x_max, cap_x_max, box_x_max,
                     box_x_max, box_x_min, box_x_min, cap_x_min, box_x_min,
                     box_x_min ]
            box_y = [q1, q1, notch_min, med, notch_max, q3, q3, notch_max,
                     med, notch_min, q1]
            # make our median line vectors
            med_x = [cap_x_min, cap_x_max]
            med_y = [med, med]

        doplot = plt.plot
        whiskers.extend(doplot(wisk_x, [q1, wisk_lo], 'b--',
                               wisk_x, [q3, wisk_hi], 'b--'))
        caps.extend(doplot(cap_x, [wisk_hi, wisk_hi], 'k-',
                           cap_x, [wisk_lo, wisk_lo], 'k-'))
        boxes.extend(doplot(box_x, box_y, 'b-'))
        medians.extend(doplot(med_x, med_y, 'r-'))
        fliers.extend(doplot(flier_hi_x, flier_hi, sym,
                             flier_lo_x, flier_lo, sym))

    # fix our axes/ticks up a little
    newlimits = min(positions)-0.5, max(positions)+0.5
    plt.gca().set_xlim(newlimits)
    plt.gca().set_xticks(positions)

    return dict(whiskers=whiskers, caps=caps, boxes=boxes,
                medians=medians, fliers=fliers)

def plot(xdata, ydata):
    res = []

    tmp = list(10**numpy.mean(i) for i in ydata)
    res.extend(plt.plot(xdata, tmp, ls='-', color='k', lw=3, #marker='+',
                        markersize=20, markeredgewidth=3))

    if max(len(i) for i in ydata) < 20: # TODO: subgroups of function, hopefully.
        for i, y in enumerate(ydata):
            res.extend(plt.plot([xdata[i]]*len(y), 10**numpy.array(y),
                                marker='+', color='b',
                                ls='', markersize=20, markeredgewidth=3))
    else:
        dictboxwhisker = boxplot(list(10**numpy.array(i) for i in ydata),
                                 sym='', notch=0, widths=None,
                                 positions=xdata)
        #'medians', 'fliers', 'whiskers', 'boxes', 'caps'
        plt.setp(dictboxwhisker['medians'], lw=3)
        plt.setp(dictboxwhisker['boxes'], lw=3)
        plt.setp(dictboxwhisker['caps'], lw=3)
        plt.setp(dictboxwhisker['whiskers'], lw=3)
        for i in dictboxwhisker.values():
            res.extend(i)
        res.extend(plt.plot(xdata, list(10**min(i) for i in ydata), marker='.',
                            markersize=20, color='k', ls=''))
        res.extend(plt.plot(xdata, list(10**max(i) for i in ydata), marker='.',
                             markersize=20, color='k', ls=''))

    return res

def beautify(figureName, fileFormat, verbose):
    """Format the figure."""

    a = plt.gca()
    a.set_yscale('log')
    plt.ylim(ymin=1e-1, ymax=1e7)
    ydata = numpy.power(10., numpy.arange(-1., 8))
    yticklabels = list(str(i) for i in range(-1, 8))
    plt.yticks(ydata, yticklabels)
    plt.xlabel('#Evals / dimension')
    plt.ylabel('log10 of ERT loss ratio')
    #a.yaxis.grid(True, which='minor')
    a.yaxis.grid(True, which='major')

    if isinstance(fileFormat, basestring):
        filename = '.'.join((figureName, fileFormat))
        plt.savefig(filename, dpi=300, format=fileFormat)
        if verbose:
            print 'Wrote figure in %s.' %(filename)
    else:
        for entry in fileFormat:
            filename = '.'.join((figureName, entry))
            plt.savefig(filename, dpi=300, format=entry)
            if verbose:
                print 'Wrote figure in %s.' %(filename)

def generateTable(dsList, CrE, outputdir, suffix, verbose=True):
    """Generates ERT loss ratio tables.
    dsList is a list of the DataSet instance for a given algorithm in a given
    dimension.
    """

    res = []

    #Set variables
    prcOfInterest = [0, 10, 25, 50, 75, 90]
    D = set()
    maxevals = []
    funcs = []
    mFE = []
    for i in dsList:
        D.add(i.dim)
        maxevals.append(max(i.ert[numpy.isinf(i.ert)==False]))
        funcs.append(i.funcId)
        mFE.append(max(i.maxevals))

    maxevals = max(maxevals)
    mFE = max(mFE)
    D = D.pop() # should have only one element
    EVALS = [2.*D]
    EVALS.extend(numpy.power(10., numpy.arange(1, numpy.ceil(numpy.log10(maxevals))))*D)
    #Set variables: Done

    data = generateData(dsList, EVALS, CrE)

    #TODO: runlength distribution for which 1e-8 was not reached.
    tmp = "f%d-%d in %d-D, maxFE=%s" % (min(funcs), max(funcs), D, writeFEvals2(int(mFE), maxdigits=6))
    res.append(r" & \multicolumn{" + str(len(prcOfInterest)) + "}{|c}{" + tmp + "}")

    header = ["evals/D"]
    for i in prcOfInterest:
        if i == 0:
            tmp = "best"
        elif i == 50:
            tmp = "med"
        else:
            tmp = "%d\\%%" % i
        header.append(tmp)

    #set_trace()
    res.append(" & ".join(header))
    for i in range(len(EVALS)):
        tmpdata = list(data[f][i] for f in data)
        #set_trace()
        tmpdata = bootstrap.prctile(tmpdata, prcOfInterest)
        # format entries
        #tmp = [writeFEvals(EVALS[i]/D, '.0')]
        tmp = [writeFEvals2(EVALS[i]/D, 1)]
        for j in tmpdata:
            #tmp.append(writeFEvals(j, '.2'))
            tmp.append(writeFEvals2(j, 2))
        res.append(" & ".join(tmp))

    # add last line
    #lastline = [writeFEVals2(numpy.inf)]
    #for

    res = (r"\\"+ "\n").join(res)
    res = r"\begin{tabular}{c|" + len(prcOfInterest) * "c" +"}\n" + res
    #res = r"\begin{tabular}{ccccc}" + "\n" + res
    res = res + r"\end{tabular}" + "\n"

    filename = os.path.join(outputdir, 'pploglosstable_%s.tex' % (suffix))
    f = open(filename, 'w')
    f.write(res)
    f.close()
    if verbose:
        print "Wrote ERT loss ratio table in %s." % filename
    return res

def generateTable2(dsList, CrE, outputdir, suffix, verbose=True):
    """Generates ERT loss ratio tables.
    dsList is a list of the DataSet instance for a given algorithm in a given
    dimension.
    """

    res = []

    #Set variables
    prcOfInterest = [0, 10, 25, 50, 75, 90]
    D = set()
    maxevals = []
    funcs = []
    mFE = []
    for i in dsList:
        D.add(i.dim)
        maxevals.append(max(i.ert[numpy.isinf(i.ert)==False]))
        funcs.append(i.funcId)
        mFE.append(max(i.maxevals))

    maxevals = max(maxevals)
    mFE = max(mFE)
    D = D.pop() # should have only one element
    EVALS = [2.*D]
    EVALS.extend(numpy.power(10., numpy.arange(1, numpy.ceil(numpy.log10(maxevals))))*D)
    #Set variables: Done

    data = generateData(dsList, EVALS, CrE)

    #TODO: runlength distribution for which 1e-8 was not reached.
    tmp = "f%d-%d in %d-D, maxFE=%s" % (min(funcs), max(funcs), D, writeFEvals2(int(mFE), maxdigits=6))
    res.append(r" & \multicolumn{" + str(len(prcOfInterest)) + "}{|c}{" + tmp + "}")

    header = ["evals/D"]
    for i in prcOfInterest:
        if i == 0:
            tmp = "best"
        elif i == 50:
            tmp = "med"
        else:
            tmp = "%d\\%%" % i
        header.append(tmp)

    #set_trace()
    res.append(" & ".join(header))
    for i in range(len(EVALS)):
        tmpdata = list(data[f][i] for f in data)
        #set_trace()
        tmpdata = bootstrap.prctile(tmpdata, prcOfInterest)
        # format entries
        #tmp = [writeFEvals(EVALS[i]/D, '.0')]
        tmp = [writeFEvals2(EVALS[i]/D, 1)]
        for j in tmpdata:
            #tmp.append(writeFEvals(j, '.2'))
            tmp.append(writeFEvals2(j, 2))
        res.append(" & ".join(tmp))

    # add last line
    #lastline = [writeFEVals2(numpy.inf)]
    #for

    res = (r"\\"+ "\n").join(res)
    res = r"\begin{tabular}{c|" + len(prcOfInterest) * "c" +"}\n" + res
    #res = r"\begin{tabular}{ccccc}" + "\n" + res
    res = res + r"\end{tabular}" + "\n"

    filename = os.path.join(outputdir, 'pploglosstable_%s.tex' % (suffix))
    f = open(filename, 'w')
    f.write(res)
    f.close()
    if verbose:
        print "Wrote ERT loss ratio table in %s." % filename
    return res

def onealg(dsList, allmintarget, allertbest):
    """Helper routine for the generation of a table for one algorithm."""

    table = []
    unsolved = {}

    for t in sorted(allmintarget.keys()):
        erts = []
        soltrials = 0
        nbtrials = 0
        solinstances = 0
        nbinstances = 0
        solfcts = 0
        nbfcts = 0
        for i, entry in enumerate(dsList):
            try:
                if numpy.isnan(allmintarget[t][(entry.funcId, entry.dim)]):
                    continue
            except KeyError:
                continue
            nbtrials += numpy.shape(entry.evals)[1] - 1
            dictinstance = entry.createDictInstance()
            nbinstances += len(dictinstance)
            nbfcts += 1
            tmp = unsolved.setdefault(i, {})
            tmp['unsoltrials'] = numpy.shape(entry.evals)[1] - 1 # may be modified a posteriori
            tmp['nbtrials'] = numpy.shape(entry.evals)[1] - 1
            tmp['unsolinstances'] = len(dictinstance) # may be modified a posteriori
            tmp['nbinstances'] = len(dictinstance)
            tmp['unsolved'] = True
            tmp['runlengths'] = entry.maxevals

            for l in range(len(entry.evals)):
                tmpline = entry.evals[l]
                if tmpline[0] < allmintarget[t][(entry.funcId, entry.dim)]:
                    solfcts += 1
                    tmp['unsolved'] = False
                    soltrials += numpy.sum(numpy.isfinite(tmpline[1:]))
                    tmp['runlengths'] = entry.maxevals[numpy.isnan(tmpline[1:])]
                    tmp['unsoltrials'] = len(tmp['runlengths'])
                    #TODO: hard to read
                    tmpsolinstances = 0
                    for idx in dictinstance.values():
                        try:
                            if numpy.isfinite(list(tmpline[j+1] for j in idx)).any():
                                tmpsolinstances += 1
                        except IndexError:
                            pass
                            #set_trace() # TODO: problem with the instances... MCS!
                    solinstances += tmpsolinstances
                    tmp['unsolinstances'] = len(dictinstance) - tmpsolinstances
                    erts.append(float(entry.ert[l]) / allertbest[t][(entry.funcId, entry.dim)])
                    break

        if len(erts) > 0:
            erts.sort()
            line = [t]
            line.extend((float(soltrials)/nbtrials*100., float(solinstances)/nbinstances*100.,
                         solfcts, nbfcts))
            line.append(erts[0])
            line.extend(prctile(erts, [10, 25, 50, 75, 90]))
            table.append(line)

    unsolved = unsolved.values()
    unsolvedrl = []
    for i in unsolved:
        unsolvedrl.extend(i['runlengths'])

    if unsolvedrl:
        unsolvedrl.sort()
        if float(sum(i['unsolinstances'] for i in unsolved))/sum(i['nbinstances'] for i in unsolved) > 1:
            #set_trace() # TODO: problem
            pass
        line = [numpy.inf,
                float(sum(i['unsoltrials'] for i in unsolved))/sum(i['nbtrials'] for i in unsolved) * 100,
                float(sum(i['unsolinstances'] for i in unsolved))/sum(i['nbinstances'] for i in unsolved) * 100,
                sum(list(i['unsolved'] for i in unsolved)), len(dsList), unsolvedrl[0]]
        line.extend(prctile(unsolvedrl, [10, 25, 50, 75, 90]))
        table.append(line)

    return table

def generateFigure(dsList, CrE, outputdir, suffix, verbose=True):
    """Generates ERT loss ratio figures.
    dsList is a list of the DataSet instances for a given algorithm in a given
    dimension.
    """

    plt.rc("axes", labelsize=20, titlesize=24)
    plt.rc("xtick", labelsize=20)
    plt.rc("ytick", labelsize=20)
    plt.rc("font", size=20)
    plt.rc("legend", fontsize=20)

    # do not aggregate over dimensions
    D = set(i.dim for i in dsList).pop() # should have only one element
    maxevals = max(max(i.ert[numpy.isinf(i.ert)==False]) for i in dsList)
    EVALS = [2.*D]
    EVALS.extend(numpy.power(10., numpy.arange(1, numpy.ceil(numpy.log10(maxevals))))*D)
    #EVALS.extend(numpy.power(10., numpy.arange(1, 10))*D)
    #set_trace()
    #if D == 3:
        #set_trace()
    data = generateData(dsList, EVALS, CrE)
    #set_trace()
    ydata = []
    for i in range(len(EVALS)):
        #Aggregate over functions.
        ydata.append(numpy.log10(list(data[f][i] for f in data)))

    xdata = numpy.log10(numpy.array(EVALS)/D)
    xticklabels = ['']
    xticklabels.extend('%d' % i for i in xdata[1:])
    plot(xdata, ydata)
    #a = plt.gca()
    #a.set_yscale('log')

    filename = os.path.join(outputdir, 'pplogloss_%s' % suffix)
    plt.xticks(xdata, xticklabels)
    #Is there an upper bound?
    #ymax = max(EVALS)
    #plt.plot(numpy.log10((2, float(ymax)/D)), (D * 2., ymax), color='k',
             #ls=':', zorder=-1)

    if len(set(dsList.dictByFunc().keys())) >= 20:
        #TODO: hopefully this means we are not considering function groups.
        plt.text(0.01, 0.98, 'CrE = %5g' % CrE, fontsize=20,
                 horizontalalignment='left', verticalalignment='top',
                 transform = plt.gca().transAxes,
                 bbox=dict(facecolor='w'))

    plt.axhline(1., color='k', ls='-', zorder=-1)
    plt.axvline(x=numpy.log10(max(i.mMaxEvals()/D for i in dsList)), color='k')
    funcs = set(i.funcId for i in dsList)
    if len(funcs) > 1:
        text = 'f%d-%d' %(min(funcs), max(funcs))
    else:
        text = 'f%d' %(funcs[0])
    plt.text(0.5, 0.93, text, horizontalalignment="center",
             transform=plt.gca().transAxes)
    beautify(filename, fileFormat=figformat, verbose=verbose)

    #plt.show()
    plt.close()

    plt.rcdefaults()

def main(dsList, CrE, outputdir, suffix, verbose=True):

    generateFigure(dsList, CrE, outputdir, suffix, verbose)
    #table = generateTable(dsList, CrE, outputdir, verbose)
    #set_trace()
