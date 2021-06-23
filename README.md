# serato-variable-tempo

## Intro

I needed to move from Mixxx DJ to Serato and was really surprised that the BPM detection in the latter had no support for tracks whose tempo changed over time. After reading reverse-engineered info on the Serato ID3 tags by [Jan Holthuis](https://github.com/Holzhaus/serato-tags), I had the pieces needed to prepare tracks for Serato's use.

Serato does have an 'Edit Grid' feature where you can manually set grid points, and I use this in conjunction with the [Queen Mary Vamp Plugins](https://vamp-plugins.org/plugin-doc/qm-vamp-plugins.html) that Mixxx uses already for variable tempo detection.

This early work uses the output of the [Bar and Beat Tracker](https://vamp-plugins.org/plugin-doc/qm-vamp-plugins.html#qm-barbeattracker) to insert a grid point every eight beats (Serato only supports 128 markers per track!)

## Usage

You'll need `ffmpeg` installed if you want to read anything other than uncompressed WAV files. Try `apt install ffmpeg` on Ubuntu or `brew install ffmpeg` on MacOS.

```
$ python3 -mvenv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ python serato_beatgrid.py /path/to/input/file.mp3 /tmp/beatgrid.dat 
```

This will work for MP3 and FLAC files since those are the two types I tend to use.

## Old Stuff

You can also use the `serato_beatgrid_old.py` to generate only a standalone beatgrid file. It will not update any MP3 or ID3 tags in the source audio file.

Once you have the `beatgrid.dat` output file, you'll want to add it as metadata to your original track. I've only tried MP3 files so far, and here's how I do it. You'll need to install the `eyeD3` tool since it's by far the most comprehensive ID3 tag editor available.

```
eyeD3 --add-object /path/to/beatgrid.dat:application/octet-stream:Serato\ BeatGrid: /path/to/input/file.mp3
```

