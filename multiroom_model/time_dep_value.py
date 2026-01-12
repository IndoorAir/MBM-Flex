# ############################################################################ #
#
# Copyright (c) 2025 Roberto Sommariva, Neil Butcher, Adrian Garcia,
# James Levine, Christian Pfrang.
#
# This file is part of MBM-Flex.
#
# MBM-Flex is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License (https://www.gnu.org/licenses) as
# published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# A copy of the GPLv3 license can be found in the file `LICENSE` at the root of
# the MBM-Flex project.
#
# ############################################################################ #

from typing import List, Tuple


class TimeDependentValue:
    """
        @brief A class recording a variable which varies in time
        Stored in the form of a list of tuples,
        each  tuple has a time and a value
        it can be continuous which means that linear interpolation will be performed between defined times

    """

    def __init__(self, values: List[Tuple[float, float]], continuous):

        # Check that at least some times were provided
        if len(values) == 0:
            raise Exception("no times provided")

        # Check that time provided were in strictly increasing order
        for i in range(len(values)-1):
            if (values[i][0] >= values[i+1][0]):
                raise Exception("times were not in order")

        self._values: List[Tuple[float, float]] = values
        self._continuous = continuous

    def times(self) -> List[float]:
        return [v[0] for v in self._values]

    def values(self) -> List[float]:
        return [v[1] for v in self._values]

    def value_at_time(self, t: float) -> float:
        """
        Returns the value at time t using linear interpolation.
        """
        # Check if the time is before any datapoint
        if t < self._values[0][0]:
            raise Exception("Time is too early")

        # Check if the time is after the last datapoint
        if t > self._values[-1][0]:
            raise Exception("Time is too late")

        # Compare with the exact times
        for t0, v0 in self._values:
            if t == t0:
                return v0

        # Value if between 2 times
        for i in range(len(self._values) - 1):
            t0, v0 = self._values[i]
            t1, v1 = self._values[i + 1]

            if t0 <= t <= t1:
                if(self._continuous):
                    # Linear interpolation if between 2 times
                    return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
                else:
                    # Discrete step if between 2 times
                    return v0

        raise Exception("Invalid time")
