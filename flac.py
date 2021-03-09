import vamp
import librosa
import struct
import argparse
import mutagen
import base64
import textwrap

def determine_filetype(inputfile):
    audio = mutagen.File(inputfile)
    return audio.mime[0]

def write_flac(flacfile, beatgridfile):
    audio = mutagen.File(flacfile)

    beatgrid_fp = open(beatgridfile, 'rb')
    beatgrid = beatgrid_fp.read()
    beatgrid_fp.close()

    beatgrid2 = b'application/octet-stream' + b'\x00\x00' + b'Serato BeatGrid' + b'\x00' + beatgrid
    audio["SERATO_BEATGRID"] = textwrap.fill(base64.b64encode(beatgrid2).decode('ascii'), width=72)
    audio.save()

def write_mp3(flacfile, beatgridfile):
    audio = mutagen.File(flacfile)

    beatgrid_fp = open(beatgridfile, 'rb')
    beatgrid = beatgrid_fp.read()
    beatgrid_fp.close()

    print(audio.info.length)
    audio["SERATO_BEATGRID"] = base64.b64encode(beatgrid).encode('ascii')
    audio.save()

def gen_beatgrid(inputfile, outputfile):
    data, rate = librosa.load(inputfile)
    params = {}
    beats = vamp.collect(data, rate, "qm-vamp-plugins:qm-barbeattracker")

    fp = open(outputfile, 'wb')

    fp.write(b'\x01\x00')
    fp.write(struct.pack('>i', int(len(beats['list']) / 4 + 1))) # only emit a marker on the '1' of each bar

    lastts = ""

    for item in beats['list']:
        if item['label'] == '1':
            fp.write(struct.pack('>f', item['timestamp']))
            fp.write(b'\x00\x00\x00\x04')
            print(item['timestamp'])
            lastts = item['timestamp']

    fp.write(struct.pack('>f', lastts))
    fp.write(struct.pack('>f', 105))
    fp.write(b'\x37')
    print(len(beats['list']))

parser = argparse.ArgumentParser()
parser.add_argument('input_file', metavar='INFILE', help="the audio file to generate a variable beatgrid for")
parser.add_argument('beatgrid_file', metavar='BGFILE', help="the binary file to write the Serato BeatGrid to")
args = parser.parse_args()

gen_beatgrid(args.input_file, args.beatgrid_file)

filetype = determine_filetype(args.input_file)

print(filetype)

if filetype == 'audio/flac':
    write_flac(args.input_file, args.beatgrid_file)
