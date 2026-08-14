"""Three-degree-of-freedom sampling contract for the reconstructed holder."""

from part import _BASE_NECK_D, _BASE_BODY_D, _D2_MAX


PARAM_SPEC = {
    "body_d": dict(
        desc="cylindrical holder-body diameter behind the source-locked V-flange",
        unit="mm",
        range={"easy": (41.0, 43.0), "medium": (39.0, 45.0), "hard": (37.0, 47.0)},
        source="proportion (42 mm baseline measured from supplied human STEP; KTA D2 <= 50 mm)",
    ),
    "body_length": dict(
        desc="straight product-body length behind the flange",
        unit="mm",
        range={"easy": (44.0, 50.0), "medium": (40.0, 54.0), "hard": (34.0, 60.0)},
        source="proportion (46.9 mm baseline measured from supplied human STEP)",
    ),
    "nose_d": dict(
        desc="outside diameter of the six-slot ER25-style product end",
        unit="mm",
        range={"easy": (41.0, 43.0), "medium": (39.0, 46.0), "hard": (40.0, 49.0)},
        source="proportion (42 mm baseline measured from supplied human STEP)",
    ),
}


def check(p: dict) -> list[str]:
    bad = []
    # KTA p.101 marks D2=50 mm as the maximum SK40 rear clearance envelope.
    if p["body_d"] > _D2_MAX:
        bad.append("body_d > KTA p.101 D2 max (50 mm): rear clearance envelope")

    # neck_d is derived from the baseline ratio 33/42.  Retain at least the
    # reconstructed 3 mm diametral shoulder before the slotted nose.
    neck_d = p["body_d"] * _BASE_NECK_D / _BASE_BODY_D
    if p["nose_d"] < neck_d + 3.0:
        bad.append("nose_d < derived neck_d + 3 mm: supplied-reconstruction shoulder disappears")
    return bad
