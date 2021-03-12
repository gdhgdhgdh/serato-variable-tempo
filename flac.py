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
    print(audio)

    beatgrid_fp = open(beatgridfile, 'rb')
    beatgrid = beatgrid_fp.read()
    beatgrid_fp.close()

    beatgrid = b'application/octet-stream' + b'\x00\x00' + b'Serato BeatGrid' + b'\x00' + beatgrid
    audio["SERATO_BEATGRID"] = textwrap.fill(base64.b64encode(beatgrid).decode('ascii'), width=72)
    audio.save()

def write_mp3(mp3file, beatgridfile):
    audio = mutagen.id3.ID3(mp3file)

    beatgrid_fp = open(beatgridfile, 'rb')
    beatgrid = beatgrid_fp.read()
    beatgrid_fp.close()

    audio['GEOB:Serato BeatGrid'] = mutagen.id3.GEOB(
        encoding=0,
        mime='application/octet-stream',
        desc='Serato BeatGrid',
        data=beatgrid,
    )
    audio.save()

def gen_beatgrid(inputfile, outputfile):
    data, rate = librosa.load(inputfile, sr=None)
    params = {}
#    tempo, beats = librosa.beat.beat_track(data, units='time', sr=rate)
    avg_tempo = librosa.beat.tempo(data)[0]
    beats = vamp.collect(data, rate, "qm-vamp-plugins:qm-barbeattracker")

#    print(beats)
#    exit()

    fp = open(outputfile, 'wb')

    fp.write(b'\x01\x00')
    print(int(len(beats['list']) / 8 + 1))

    fp.write(struct.pack('>i', int(len(beats['list']) / 8 + 1))) # only emit a marker on the '1' of each bar

    lastts = ""
    process_beat = True

    for count, item in enumerate(beats['list']):
        if count == 1016: # serato only allows 128 markers - leave one space for the termination marker
            break
#        print(f'pb: {process_beat} item: {item} lastts: {lastts}')
        if item['label'] == '1' and not process_beat:
            process_beat = True
            continue
        if item['label'] == '1' and process_beat:
#            print(f"Writing beat at {item['timestamp']}")
            fp.write(struct.pack('>f', item['timestamp']))
            fp.write(b'\x00\x00\x00\x08')
#            print(item['timestamp'])
            lastts = item['timestamp']
            process_beat = False
            continue

    print(lastts)
    fp.write(struct.pack('>f', lastts))
    fp.write(struct.pack('>f', avg_tempo))
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
elif filetype == 'audio/mp3':
    write_mp3(args.input_file, args.beatgrid_file)
else:
    print(f'Sorry, {filetype} files are not supported')
