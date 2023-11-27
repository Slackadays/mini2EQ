import sys

def main():
    if len(sys.argv) < 2:
        print_help_message()
        return

    output_format = ""

    if "--apo" in sys.argv:
        output_format = "apo"
        sys.argv.remove("--apo")

    if output_format == "":
        print_help_message()
        return

    output_file = ""

    if "--output" in sys.argv:
        output_file = sys.argv[sys.argv.index("--output") + 1]
        sys.argv.remove("--output")
        sys.argv.remove(output_file)

    bands = 0

    if "--bands" in sys.argv:
        bands = int(sys.argv[sys.argv.index("--bands") + 1])
        sys.argv.remove("--bands")
        sys.argv.remove(str(bands))

    input_file = sys.argv[1]

    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    with open(input_file, "r") as f:
        lines = f.readlines()

    hertz_db = []

    # parse the input file with this format:
    """
    "Sens Factor =-8.297dB, SERNO: 7001455"
    "Auto-generated 90-degree calibration file"
    10.054	-7.0030
    10.179	-6.8243
    10.306	-6.6488
    10.434	-6.4765
    10.564	-6.3074
    10.696	-6.1413
    10.829	-5.9784
    10.964	-5.8186
    11.100	-5.6618
    """

    for line in lines:
        if line.startswith("\""):
            continue
        else:
            hertz_db.append(line.strip().split("\t"))

    # since our data correlates a hertz range to a test result, flip all test results to get an appropriate equalizer setting in float
    for i in range(len(hertz_db)):
        hertz_db[i][1] = -1 * float(hertz_db[i][1])
        hertz_db[i][0] = float(hertz_db[i][0])
        # also convert the hertz value to a float

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

    # calculate q by comparing the difference between the previous, current, and next hertz values

    if output_format == "apo":
        if output_file == "":
            output_file = input_file.replace(".txt", "-apo.txt")
        
        with open(output_file, "w") as f:
            for i in range(len(hertz_db)):
                previous = None
                next = None

                if i > 0:
                    previous = hertz_db[i - 1][0]
                if i < len(hertz_db) - 1:
                    next = hertz_db[i + 1][0]

                q = ideal_q_setting(previous, hertz_db[i][0], next)

                f.write("Filter {}: ON PK Fc {} Hz Gain {} dB Q {}\n".format(i + 1, hertz_db[i][0], hertz_db[i][1], q))

    print("Done!")


def print_help_message():
    print("mini2EQ: Convert a miniDSP mic calibration file to an EQ preset.")
    print("How to use: python mini2eq.py (format) [options] <input_file> [output_file]")
    print("Formats available: APO (--apo)")
    print("Options available: Number of EQ bands (--bands <n>)")

def ideal_q_setting(previous: float, current: float, next: float) -> float:
    # calculate the ideal q setting based on the previous, current, and next hertz values

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