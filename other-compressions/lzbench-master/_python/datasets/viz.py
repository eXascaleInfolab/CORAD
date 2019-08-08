#!/usr/bin/env python

import matplotlib.pyplot as plt

def save_fig_png(path):
    plt.savefig(path, dpi=300, bbox_inches='tight')
