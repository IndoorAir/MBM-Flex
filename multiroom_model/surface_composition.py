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

from typing import Optional


class SurfaceComposition:
    """
        @brief A class recording the composition of surface materials (in percentages) in a single room,

        The sum of the values should be equal to 100 (percent)

        If you leave "other" undefined, then it will be calculated so the values sum to 100%

    """
    soft: float
    paint: float
    wood: float
    metal: float
    concrete: float
    paper: float
    lino: float
    plastic: float
    glass: float
    human: float
    other: float

    def __init__(self,
                 soft: float = 0,
                 paint: float = 0,
                 wood: float = 0,
                 metal: float = 0,
                 concrete: float = 0,
                 paper: float = 0,
                 lino: float = 0,
                 plastic: float = 0,
                 human: float = 0,
                 glass: float = 0,
                 other: Optional[float] = None):
        self.soft = soft
        self.paint = paint
        self.wood = wood
        self.metal = metal
        self.concrete = concrete
        self.paper = paper
        self.lino = lino
        self.plastic = plastic
        self.glass = glass
        self.human = human
        self.other = other if other is not None else 100-soft-paint-wood-metal-concrete-paper-lino-plastic-glass-human

        if self.other < 0:
            self.other = 0

        total = sum(self.surface_area_dictionary(100.0).values())

        # Check that the sum of % areas is near 100
        if total > 100+1.0e-12 or total < 100-1.0e-12:
            raise ValueError("The total did not come to 100% (if you leave \"other\" undefined it will be calculated)")

        # Check that no individual % is above 100 or below 0
        for name, value in self.surface_area_dictionary(100.0).items():
            if value < 0 or value > 100:
                raise ValueError(f"{name} must be a percentage between 0 and 100 (got {value})")

    def surface_area_dictionary(self, total_surface_area):
        """
            @brief Creates a dictionary of absolute surface areas
            Uses the percentages stored in the class along with the total area, pass in as a parameter

        """
        return {
            'SOFT': total_surface_area*self.soft/100.0,
            'PAINT': total_surface_area*self.paint/100.0,
            'WOOD': total_surface_area*self.wood/100.0,
            'METAL': total_surface_area*self.metal/100.0,
            'CONCRETE': total_surface_area*self.concrete/100.0,
            'PAPER': total_surface_area*self.paper/100.0,
            'LINO': total_surface_area*self.lino/100.0,
            'PLASTIC': total_surface_area*self.plastic/100.0,
            'GLASS': total_surface_area*self.glass/100.0,
            'HUMAN': total_surface_area*self.human/100.0,
            'OTHER': total_surface_area*self.other/100.0
        }
