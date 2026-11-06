#!/usr/bin/env python3
"""Convert silicon DCM Bragg angle (degrees) <-> photon energy (keV)."""

import argparse
import math

# Physical constants
HC_KEV_ANGSTROM = 12.39841984332
SI_LATTICE_ANGSTROM = 5.431  # Approximate room-temperature value

REFLECTIONS = {
    "111": (1, 1, 1),
    "113": (1, 1, 3),
    "333": (3, 3, 3),
}


def d_spacing(reflection):
    """Return the interplanar spacing in angstroms."""
    if reflection not in REFLECTIONS:
        raise ValueError("Reflection must be '111', '113', or '333'.")

    h, k, l = REFLECTIONS[reflection]
    return SI_LATTICE_ANGSTROM / math.sqrt(h*h + k*k + l*l)


def angle_to_energy(angle_deg, reflection="111"):
    """Convert Bragg angle in degrees to energy in keV."""
    if not math.isfinite(angle_deg) or not 0 < angle_deg <= 90:
        raise ValueError("Bragg angle must be greater than 0 and at most 90°.")

    d = d_spacing(reflection)
    theta = math.radians(angle_deg)
    return HC_KEV_ANGSTROM / (2 * d * math.sin(theta))


def energy_to_angle(energy_kev, reflection="111"):
    """Convert energy in keV to Bragg angle in degrees."""
    if not math.isfinite(energy_kev) or energy_kev <= 0:
        raise ValueError("Energy must be a positive, finite number.")

    d = d_spacing(reflection)
    minimum_energy = HC_KEV_ANGSTROM / (2 * d)

    if energy_kev < minimum_energy:
        raise ValueError(
            f"Energy is too low for Si({reflection}). "
            f"Minimum possible energy is {minimum_energy:.9f} keV "
            f"(at θ = 90°)."
        )

    sin_theta = minimum_energy / energy_kev
    return math.degrees(math.asin(sin_theta))


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Convert silicon DCM Bragg angle (degrees) "
            "to energy (keV), or vice versa."
        )
    )
    parser.add_argument(
        "--hkl",
        choices=REFLECTIONS.keys(),
        default="111",
        help="Silicon reflection: 111, 113, or 333 (default: 111).",
    )

    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument(
        "--angle", type=float, help="Bragg angle θ in degrees."
    )
    inputs.add_argument(
        "--energy", type=float, help="Photon energy in keV."
    )

    args = parser.parse_args()

    try:
        if args.angle is not None:
            angle = args.angle
            energy = angle_to_energy(angle, args.hkl)
        else:
            energy = args.energy
            angle = energy_to_angle(energy, args.hkl)
    except ValueError as exc:
        parser.error(str(exc))

    print(f"Crystal:     Si({args.hkl})")
    print(f"d-spacing:   {d_spacing(args.hkl):.9f} Å")
    print(f"Bragg angle: {angle:.9f} degrees")
    print(f"Energy:      {energy:.9f} keV")


if __name__ == "__main__":
    main()