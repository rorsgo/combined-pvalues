"""
    %prog [options] files

plot a manhattan plot of the input file(s).
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from itertools import groupby, cycle
from operator import itemgetter
import matplotlib
import scipy.stats as ss
#matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
from cpv._common import bediter, get_col_num

def manhattan(fname, col_num, image_path, no_log, colors, title, lines, ymax):

    xs, ys, cs = [], [], []
    colors = cycle(colors)
    chrom_centers = []

    last_x = 0
    nrows = 0
    for seqid, rlist in groupby(bediter(fname, col_num),
                                key=itemgetter('chrom')):
        color = colors.next()
        rlist = list(rlist)
        nrows += len(rlist)
        # since chroms are on the same plot. add this chrom to the end of the
        # last chrom
        region_xs = [last_x + r['start'] for r in rlist]
        xs.extend(region_xs)
        ys.extend([r['p'] for r in rlist])
        cs.extend([color] * len(rlist))

        # save the middle of the region to place the label
        chrom_centers.append((seqid, (region_xs[0] + region_xs[-1]) / 2))
        # keep track so that chrs don't overlap.
        last_x = xs[-1]

    xs = np.array(xs)
    ys = np.array(ys) if no_log else -np.log10(ys)

    plt.close()
    f = plt.figure()
    ax = f.add_axes((0.1, 0.09, 0.88, 0.85))

    bonferonni_p = 0.05 / nrows

    if title is not None:
        plt.title(title)

    ax.set_ylabel('' if no_log else '-log10(p)')
    if lines:
        ax.vlines(xs, 0, ys, colors=cs, alpha=0.5)
    else:
        ax.scatter(xs, ys, s=2, c=cs, alpha=0.8, edgecolors='none')

    # plot 0.05 line after multiple testing. always nlog10'ed since
    # that's the space we're plotting in.
    ax.axhline(y=-np.log10(bonferonni_p), color='0.5', linewidth=2)
    plt.axis('tight')
    plt.xlim(0, xs[-1])
    plt.ylim(ymin=0)
    if ymax is not None: plt.ylim(ymax=ymax)
    plt.xticks([c[1] for c in chrom_centers], [c[0] for c in chrom_centers], rotation=-90, size=8.5)
    #plt.show()
    print >>sys.stderr, "Bonferonni-corrected p-value for %i rows: %.3g" \
            % (nrows, 0.05 / nrows)
    print >>sys.stderr, "values less than Bonferonni-corrected p-value: %i " \
            % (ys > -np.log10(bonferonni_p)).sum()

    ax_qq = f.add_axes((0.74, 0.12, 0.22, 0.22), alpha=0.2)

    pys = np.sort(10**-ys) # convert back to actual p-values
    qq(pys, ax_qq)

    ax_hist = f.add_axes((0.12, 0.12, 0.22, 0.22), frameon=True, alpha=0.6)
    hist(pys, ax_hist)
    print >>sys.stderr, "saving to: %s" % image_path
    plt.savefig(image_path)

    return

def hist(pys, ax_hist):
    ax_hist.hist(pys, bins=40, color='0.75')
    ax_hist.set_xticks([])
    ax_hist.set_yticks([])



def qq(pys, ax_qq):
    from scikits.statsmodels.graphics.qqplot import qqplot
    qqplot(pys, dist=ss.uniform, line='45')

    ax_qq.lines[0].set_marker(',')
    ax_qq.lines[0].set_markeredgecolor('0.75')
    ax_qq.lines[1].set_linestyle('dashed')
    ax_qq.lines[1].set_color('k')
    ax_qq.set_xticks([])
    ax_qq.set_xlabel('')
    ax_qq.set_ylabel('')
    ax_qq.set_yticks([])
    #ax_qq.lines[0].set_linestyle(None)
    ax_qq.axis('tight')
    ax_qq.axes.set_frame_on(True)

def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument("--no-log", help="don't do -log10(p) on the value",
            action='store_true', default=False)
    p.add_argument("--col", dest="col", help="index of the column containing"
                   " the the p-value", default=-1, type=int)
    p.add_argument("--colors", dest="colors", help="cycle through these colors",
                default="bk")
    p.add_argument("--image", dest="image", help="save the image to this file."
                   " e.g. %(default)s", default="manhattan.png")
    p.add_argument("--title", help="title for the image.", default=None,
                   dest="title")
    p.add_argument("--ymax", help="max (-log) y-value for plot", dest="ymax",
                   type=float)
    p.add_argument("--lines", default=False, dest="lines", action="store_true",
        help="plot the p-values as lines extending from the x-axis rather than"
             " points in space. plotting will take longer with this option.")
    p.add_argument('bed_file', help="bed-file to plot")

    args = p.parse_args()
    if (not args.bed_file):
        sys.exit(not p.print_help())
    column = get_col_num(args.col)
    manhattan(args.bed_file, column, args.image, args.no_log, args.colors,
              args.title, args.lines, args.ymax)

if __name__ == "__main__":
    main()
