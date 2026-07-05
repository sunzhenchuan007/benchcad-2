"""ISO 606 roller-chain sprocket tooth profile (shared curve generator)."""

import math


def sprocket_profile(z, pitch, roller_d, n_arc=8, phase=0.0):
    """Closed CCW polyline of an ISO 606 sprocket outline, as (x, y) tuples.

    Tooth form per ISO 606:2015 §8.2: circular roller-seating arc
    (ri = 0.505*d1) + straight flank + tip-circle midpoint, one continuous
    wire (extrude in one shot — no per-tooth booleans). `phase` rotates the
    whole profile (e.g. to align a tooth tip with a keyway).
    """
    dp = pitch / math.sin(math.pi / z)
    do = dp + 0.68 * roller_d  # tip offset fitted to catalog D columns (ISO band)
    ri = 0.505 * roller_d
    beta_half = math.radians(140 - 90 / z) / 2
    pts = []
    for i in range(z):
        base = i * (2 * math.pi / z) + phase
        cg, sg = math.cos(base), math.sin(base)
        right = []
        for j in range(n_arc):
            a = math.pi - (j / (n_arc - 1)) * beta_half
            right.append((dp / 2 + ri * math.cos(a), ri * math.sin(a)))
        x_re, y_re = right[-1]
        theta_re = math.atan2(y_re, x_re)
        theta_tip = max((math.pi / z) - 0.2 * pitch / do, theta_re + 0.01)
        right.append(((do / 2) * math.cos(theta_tip), (do / 2) * math.sin(theta_tip)))
        right.append(((do / 2) * math.cos(math.pi / z), (do / 2) * math.sin(math.pi / z)))
        gap = [(x, -y) for x, y in reversed(right)][:-1] + right
        for x, y in gap[:-1]:
            pts.append((round(x * cg - y * sg, 4), round(x * sg + y * cg, 4)))
    return pts
