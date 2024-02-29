#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AQ6370D(Instrument):
    """
    Represents a Yokogawa AQ6370D Optical Spectrum Analyzer.
    """

    def __init__(self, adapter, name="Yokogawa AQ3670D OSA", **kwargs):
        super().__init__(adapter, name, includeSCPI=True, **kwargs)

    # Initiate and abort sweep ---------------------------------------------------------------------

    def abort(self):
        """Stop operations such as measurements and calibration."""
        self.write(":ABORt")

    def initiate(self):
        """Initiate a sweep."""
        self.write(":INITiate:IMMediate")

    # Leveling -------------------------------------------------------------------------------------

    reference_level = Instrument.control(
        ":DISPlay:TRACe:Y1:SCALe:RLEVel?",
        ":DISPlay:TRACe:Y1:SCALe:RLEVel %g",
        "Control the reference level of main scale of level axis (float in dBm).",
        validator=strict_range,
        values=[-100, 20],
    )

    level_position = Instrument.control(
        ":DISPlay:TRACe:Y1:RPOSition?",
        ":DISPlay:TRACe:Y1:RPOSition %g",
        """Control the reference level position regarding divisions
        (int, smaller than total number of divisions which is either 8, 10 or 12).""",
        validator=strict_range,
        values=[0, 12],
    )

    def level_position_max(self):
        """Set the reference level position to the maximum value."""
        self.write(":CALCulate:MARKer:MAXimum:SRLevel")

    # Sweep settings -------------------------------------------------------------------------------

    sweep_mode = Instrument.control(
        ":INITiate:SMODe?",
        ":INITiate:SMODe %s",
        "Control the sweep mode (str 'SINGLE', 'REPEAT', 'AUTO', 'SEGMENT').",
        validator=strict_discrete_set,
        map_values=True,
        values={"SINGLE": 1, "REPEAT": 2, "AUTO": 3, "SEGMENT": 4},
    )

    sweep_speed = Instrument.control(
        ":SENSe:SETTing:SPEed?",
        ":SENSe:SWEep:SPEed %d",
        "Control the sweep speed (str '1x' or '2x' for double speed).",
        validator=strict_discrete_set,
        map_values=True,
        values={"1x": 0, "2x": 1},
    )

    sweep_time_interval = Instrument.control(
        ":SENSe:SWEep:TIME:INTerval?",
        ":SENSe:SWEep:TIME:INTerval %g",
        "Control the sweep time interval (int from 0 to 99999 s).",
        validator=strict_range,
        values=[0, 99999],
    )

    # Wavelength settings (all assuming wavelength mode, not frequency mode) -----------------------

    wavelength_center = Instrument.control(
        ":SENSe:WAVelength:CENTer?",
        ":SENSe:WAVelength:CENTer %g",
        """Control measurement condition center wavelength (float in m).""",
        validator=strict_range,
        values=[50e-9, 2250e-9],
    )

    wavelength_span = Instrument.control(
        ":SENSe:WAVelength:SPAN?",
        ":SENSe:WAVelength:SPAN %g",
        """Control wavelength span (float from 0 to 3e-7 m).""",
        validator=strict_range,
        values=[0, 1100e-9],
    )

    wavelength_start = Instrument.control(
        ":SENSe:WAVelength:STARt?",
        ":SENSe:WAVelength:STARt %g",
        """Control the measurement start wavelength (float in m).""",
        validator=strict_range,
        values=[50e-9, 2250e-9],
    )

    wavelength_stop = Instrument.control(
        ":SENSe:WAVelength:STOP?",
        ":SENSe:WAVelength:STOP %g",
        """Control the measurement stop wavelength (float in m).""",
        validator=strict_range,
        values=[50e-9, 2250e-9],
    )

    # Trace operations -----------------------------------------------------------------------------

    active_trace = Instrument.control(
        ":TRACe:ACTive?",
        ":TRACe:ACTive %d",
        "Control the active trace (str 'TRA', 'TRB', 'TRC', ...).",
    )

    def copy_trace(self, source, destination):
        """
        Copy the data of specified trace to the another trace.

        :param source: Source trace (str 'TRA', 'TRB', 'TRC', ...).
        :param destination: Destination trace (str 'TRA', 'TRB', 'TRC', ...).
        """
        self.write(f":TRACe:COPY {source},{destination}")

    def delete_trace(self, trace):
        """
        Delete the specified trace.

        :param trace: Trace to be deleted (str 'ALL', 'TRA', 'TRB', 'TRC', ...).
        """
        if trace == "ALL":
            self.write(":TRACe:DELete:ALL")
        else:
            self.write(f":TRACe:DELete {trace}")

    def get_xdata(self, trace="TRA"):
        """
        Measure the x-axis data of specified trace, output wavelength in m.

        :param trace: Trace to measure (str 'TRA', 'TRB', 'TRC', ...).
        :return: The x-axis data of specified trace.
        """
        return self.values(f":TRACe:X? {trace}")

    def get_ydata(self, trace="TRA"):
        """
        Measure the y-axis data of specified trace, output power in dBm.

        :param trace: Trace to measure (str 'TRA', 'TRB', 'TRC', ...).
        :return: The y-axis data of specified trace.
        """
        return self.values(f":TRACe:Y? {trace}")

    # Resolution -----------------------------------------------------------------------------------

    resolution_bandwidth = Instrument.control(
        ":SENSe:BWIDth:RESolution?",
        ":SENSe:BWIDth:RESolution %g",
        """Control the measurement resolution (float in m,
        discrete values: [0.02, 0.05, 0.1, 0.2, 0.5, 1, 2] nm).""",
        validator=strict_range,
        values=[0.02e-9, 2e-9],
    )
