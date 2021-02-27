import vamp
import librosa
import struct
import argparse

def process(inputfile, outputfile):
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
process(args.input_file, args.beatgrid_file)
