# mini2EQ: Convert a miniDSP mic calibration file to an equalizer preset.
# Copyright 2023 Jackson Huff
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys

def main():
    output_format = ""

    if "--apo" in sys.argv:
        output_format = "apo"
        sys.argv.remove("--apo")

    output_file = ""

    if "--output" in sys.argv:
        output_file = sys.argv[sys.argv.index("--output") + 1]
        sys.argv.remove("--output")
        sys.argv.remove(output_file)

    bands = 0

    if "--bands" in sys.argv:
        bands = int(sys.argv[sys.argv.index("--bands") + 1])
        if bands < 2:
            print("Error! Number of EQ bands must be greater than 1.")
            return
        sys.argv.remove("--bands")
        sys.argv.remove(str(bands))

    if len(sys.argv) < 2 or output_format == "":
        print_help_message()
        return

    input_file = sys.argv[1]

    hertz_db = calibration_data(input_file)

    if bands > len(hertz_db):
        print("Error! Number of EQ bands must be less than or equal to the number of hertz values in the calibration file.")
        return

    if bands != 0:
        # now compress the data into the number of bands specified
        # first, calculate the number of hertz values per band
        hertz_per_band = len(hertz_db) / bands

        # now, compress the data
        new_hertz_db = []

        for i in range(bands):
            # calculate the average hertz value for this band
            average_hertz = 0
            average_db = 0

            for j in range(int(hertz_per_band)):
                average_hertz += hertz_db[int(i * hertz_per_band) + j][0]
                average_db += hertz_db[int(i * hertz_per_band) + j][1]

            average_hertz /= hertz_per_band
            average_db /= hertz_per_band

            new_hertz_db.append([average_hertz, average_db])
        
        hertz_db = new_hertz_db

    # now write a new file with format:
    """
    Filter <n>: ON PK Fc <hz> Hz Gain <db> dB Q <q>
    """

    if output_format == "apo":
        if output_file == "":
            output_file = input_file.replace(".txt", "-apo.txt")
        write_apo(hertz_db, output_file)

def calibration_data(file: str) -> list[float, float]:
    """
    Parse the input file with this format and return the contained calibration data:

    "Sens Factor =-8.297dB, SERNO: 7001234"

    "Auto-generated 90-degree calibration file" [These lines may or may not start with the " character]

    10.054	-7.0030

    10.179	-6.8243

    10.306	-6.6488

    ...
    """

    lines = []
    hertz_db = []

    with open(file, "r") as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith("\"") or line[0].isalpha():
            continue
        else:
            hertz_db.append(line.strip().split())

    for i in range(len(hertz_db)):
        hertz_db[i][0] = float(hertz_db[i][0]) # convert the hertz value to a float
        hertz_db[i][1] = -1 * float(hertz_db[i][1])
        # since our data correlates a hertz range to a test result, flip all test results to get an appropriate equalizer setting in float

    return hertz_db

def write_apo(data: list[float, float], file: str):        
    with open(file, "w") as f:
        for i in range(len(data)):
            previous = None
            next = None

            if i > 0:
                previous = data[i - 1][0]
            if i < len(data) - 1:
                next = data[i + 1][0]

            q = q_setting(previous, data[i][0], next)

            f.write("Filter {}: ON PK Fc {} Hz Gain {} dB Q {}\n".format(i + 1, data[i][0], data[i][1], q))


def print_help_message():
    print("mini2EQ: Convert a miniDSP mic calibration file to an EQ preset.")
    print("How to use: python mini2eq.py (format) [options] <input_file>")
    print("Formats available:")
    print("1. APO | --apo")
    print("Options available:")
    print("1. Number of EQ bands | --bands <n>")
    print("2. Output file | --output <name>")

def q_setting(previous: float, current: float, next: float) -> float:
    """Calculate q by comparing the difference between the previous, current, and next hertz values."""

    # if the previous hertz value is 0, then calculate it based on the current and next hertz values
    if previous == None:
        return current / (next - current)

    # if the next hertz value is 0, then calculate it based on the current and previous hertz values
    if next == None:
        return current / (current - previous)

    # otherwise, calculate it based on the previous and next hertz values
    return current / (next - previous)

if __name__ == "__main__":
    main()