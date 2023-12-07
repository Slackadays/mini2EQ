# mini2EQ

**mini2EQ** is a cute little website and standalone program that let you convert a miniDSP calibration microphone's factory calibration file to an equalizer preset that you can import to your favorite software.

## The Problem

I want to use one of MDSP's [calibration mics](https://www.minidsp.com/products/acoustic-measurement/umik-1) to ensure a flat response in my sound systems. To make sure these mics are perfectly flat, you can get a factory calibration file customized for your exact one. Unfortunately, I couldn't get this data working in any of my favorite free and open-source software using a more common format, so I just made mini2EQ to do this conversion for me.

With mini2EQ, you can now use this calibration file in anything that supports its output formats, such as EasyEffects and Peace EQ.

## Prerequisite

You'll need at least Python 3.7 to run mini2EQ locally.

## How To Use

Only read this section if you're using the local Python version of mini2EQ.

### 1. Download

Click the `mini2eq.py` file here in GitHub and use the download button on its page to download it.

### 2. Run it

In your favorite terminal or command prompt, run this command:

```sh
python mini2eq.py (format) <input_file>
```

Replace `(format)` with one of the available formats below:

- APO: `--apo`

Optionally, add any of the options below:

- Number of EQ bands: `--bands <n>`
- Custom output file: `--output <file>`

### 3. Import the result

You'll see a new file with the converted data. Import this into your favorite equalizer software and get calibrating!
