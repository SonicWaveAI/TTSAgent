from pydub import AudioSegment


def m4a2wav(input_file, output_file):
    AudioSegment.from_file(input_file, format='m4a').export(output_file, format='wav')

