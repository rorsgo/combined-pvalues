"""
    %prog [options] files

plot a manhattan plot of the input file(s).
"""

import argparse
import sys
from itertools import groupby, cycle
from operator import itemgetter
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
from cpv._common import bediter, get_col_num

def chr_cmp(a, b):
    a = a.lower().replace("_", ""); b = b.lower().replace("_", "")
    achr = a[3:] if a.startswith("chr") else a
    bchr = b[3:] if b.startswith("chr") else b

    try:
        return cmp(int(achr), int(bchr))
    except ValueError:
        if achr.isdigit() and not bchr.isdigit(): return -1
        if bchr.isdigit() and not achr.isdigit(): return 1
        # X Y
        return cmp(achr, bchr)

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

    if title is not None:
        plt.title(title)

    ax.set_ylabel('' if no_log else '-log10(p)')
    if lines:
        ax.vlines(xs, 0, ys, colors=cs, alpha=0.5)
    else:
        ax.scatter(xs, ys, s=2, c=cs, alpha=0.8, edgecolors='none')

    # plot 0.05 line after multiple testing. always nlog10'ed since
    # that's the space we're plotting in.
    ax.axhline(y=-np.log10(0.05 / nrows), color='0.5', linewidth=2)
    plt.axis('tight')
    plt.xlim(0, xs[-1])
    plt.ylim(ymin=0)
    if ymax is not None: plt.ylim(ymax=ymax)
    plt.xticks([c[1] for c in chrom_centers], [c[0] for c in chrom_centers], rotation=-90, size=8.5)
    print >>sys.stderr, "saving to: %s" % image_path
    plt.savefig(image_path)
    #plt.show()
    print >>sys.stderr, "Bonferonni-corrected p-value for %i rows: %.3g" \
            % (nrows, 0.05 / nrows)

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
