"""Involute spur-gear tooth profile (shared curve generator).

Engagement-grade approximation of the ISO 53 basic rack generated involute:
true involute flanks between base/root and tip circles, arc-sampled tip land
and root land. Families using it must spot-check derived diameters against a
gear table (e.g. root df = m(z-2.5), tip da = m(z+2)) in their NOTES.md.
"""

import math


def involute_gear_profile(module, z, pressure_angle_deg=20.0, n_flank=8, phase=0.0):
    """Closed CCW polyline of a spur gear outline, as (x, y) tuples.

    Standard proportions: pitch r = m*z/2, tip = r + m, root = r - 1.25*m,
    base = r*cos(alpha). Tooth thickness at the pitch circle = half the pitch
    (backlash-free basic rack).
    """
    alpha = math.radians(pressure_angle_deg)
    r_p = module * z / 2.0
    r_b = r_p * math.cos(alpha)
    r_a = r_p + module
    r_f = max(r_p - 1.25 * module, 0.35 * r_b)

    def inv(a):
        return math.tan(a) - a

    # involute point at radius r (r >= r_b): polar angle relative to involute origin
    def inv_polar(r):
        a = math.acos(r_b / r)
        return inv(a)

    half_tooth = math.pi / (2 * z) + inv(alpha)  # half tooth angle at pitch circle datum
    pts = []
    r_start = max(r_b, r_f)
    for i in range(z):
        base_a = i * (2 * math.pi / z) + phase
        flank_r = [r_start + (r_a - r_start) * j / (n_flank - 1) for j in range(n_flank)]
        # right flank: angles measured from tooth centreline
        right = [
            (r * math.cos(base_a + half_tooth - inv_polar(r)),
             r * math.sin(base_a + half_tooth - inv_polar(r)))
            for r in flank_r
        ]
        left = [
            (r * math.cos(base_a - half_tooth + inv_polar(r)),
             r * math.sin(base_a - half_tooth + inv_polar(r)))
            for r in flank_r
        ]
        # root land between previous tooth's right flank and this tooth's left flank
        gap_start = base_a - (math.pi / z)
        for k in range(3):
            a = gap_start + (k / 2.0) * (base_a - half_tooth - gap_start)
            pts.append((round(r_f * math.cos(a), 4), round(r_f * math.sin(a), 4)))
        for x, y in left:
            pts.append((round(x, 4), round(y, 4)))
        # tip land — midpoint only: its endpoints coincide with the flank
        # ends and duplicated points make zero-length polyline edges (BRep fail)
        a_mid = base_a  # tooth centreline
        pts.append((round(r_a * math.cos(a_mid), 4), round(r_a * math.sin(a_mid), 4)))
        for x, y in reversed(right):
            pts.append((round(x, 4), round(y, 4)))
    return pts
