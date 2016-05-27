import re
from pydub import AudioSegment
from test1 import writeLabelTracks_file
from pydub.silence import split_on_silence, detect_nonsilent, detect_silence
filename_path = 'C:/Users/ok/PycharmProjects/audio_recognize/text/'
file_name = 'NYStories4'
filename_suff = '%s%s' % (filename_path, file_name)
filename_mp3 = "%s.mp3" % filename_suff
filename_aup = "%s.aup" % filename_suff

def splitAudioFile(filename_mp3, in_dir, min_silence_len=400, silence_thresh=-65):

    sound = AudioSegment.from_mp3(filename_mp3)
    nonsilence_range = detect_nonsilent(sound, min_silence_len, silence_thresh)
    chunks_range = []

    for i, chunk in enumerate(nonsilence_range):
        if i==0:
            start = 0.0
            end = (chunk[1] + nonsilence_range[i+1][0])/2
            sound[:end].export(".\\tmp\\%d\\%d.wav" % (in_dir, i), format="wav", bitrate="16k")
        elif i == len(nonsilence_range)-1:
            start = (nonsilence_range[i-1][1] + chunk[0])/2
            end = chunk[1] + 1000.0
            sound[start:].export(".\\tmp\\%d\\%d.wav" % (in_dir, i), format="wav", bitrate="16k")
        else:
            start = (nonsilence_range[i-1][1] + chunk[0])/2
            end = (chunk[1] + nonsilence_range[i+1][0])/2
            sound[start:end].export(".\\tmp\\%d\\%d.wav" % (in_dir, i), format="wav", bitrate="16k")

        start = round(start/1000, 1)
        end = round(end/1000, 1)
        chunks_range.append((start,end))

    return chunks_range
