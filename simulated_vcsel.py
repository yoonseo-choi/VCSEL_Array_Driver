#!/usr/bin/env python3
"""Simulating a VCSEL array interface."""

import msgpack
import numpy as np
import scipy.interpolate as interpolate
import pandas as pd

class VCSELArray:
    """A simulated VCSEL array connected up to a simulated microcontroller interface."""
    # Current applied currents to VCSELs 1 and 2
    i1 = 0
    i2 = 0
    # Interpolator functions for calculating the voltages across VCSELs 1 and 2
    v1interp = None
    v2interp = None

    def __init__(self, filename):
        """Create a simulated VCSEL array based on the provided `filename` measurements."""
        # Read and parse the MsgPack file
        data = pd.read_msgpack(filename)
        # Read the currents and determine the current ranges for the measurement
        currents = data["currents"]
        self.i1rng = sorted({i[0] for i in currents})
        self.i2rng = sorted({i[1] for i in currents})
        # Pre-allocate the voltage arrays
        v1 = np.zeros((len(self.i1rng), len(self.i2rng)))
        v2 = np.zeros((len(self.i1rng), len(self.i2rng)))
        # Iterate through each voltage measurement
        for (i, v) in enumerate(data["voltages"]):
            # Determine the index in the array of the current measurement
            idx1, idx2 = self.i1rng.index(currents[i][0]), self.i2rng.index(
                currents[i][1])
            # And put the measurement in the correct array
            v1[idx1, idx2] = v[0]
            v2[idx1, idx2] = v[1]
        # Convert from the measured units of A to mA
        self.i1rng = 1000 * np.array(self.i1rng)
        self.i2rng = 1000 * np.array(self.i2rng)
        # Create a set of interpolators for the voltage measurements
        self.v1interp = interpolate.interp2d(self.i1rng, self.i2rng, v1)
        self.v2interp = interpolate.interp2d(self.i1rng, self.i2rng, v2)
        print("Loaded measurement " + filename)

    def set_current1(self, current):
        """Set the current (in mA) to VCSEL 1."""
        self.i1 = current

    def set_current2(self, current):
        """Set the current (in mA) to VCSEL 2."""
        self.i2 = current

    def read_voltage1(self):
        """Read the voltage (in V) across VCSEL 1."""
        return self.v1interp(self.i1, self.i2)[0]

    def read_voltage2(self):
        """Read the voltage (in V) across VCSEL 2."""
        return self.v2interp(self.i1, self.i2)[0]
