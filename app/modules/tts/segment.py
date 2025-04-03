import re
import numpy as np


def split_text_with_context(text, max_len=300, context_len=1):
    return split_text_no_overlap(text, max_len)


def fade_audio(wav, fade_len=1600):
    if len(wav) < 2 * fade_len:
        return wav
    fade_in = np.linspace(0.0, 1.0, fade_len)
    fade_out = np.linspace(1.0, 0.0, fade_len)
    wav[:fade_len] *= fade_in
    wav[-fade_len:] *= fade_out
    return wav


def crossfade(wav1, wav2, fade_len=1600):
    if len(wav1) < fade_len or len(wav2) < fade_len:
        return np.concatenate([wav1, wav2])
    fade_out = np.linspace(1.0, 0.0, fade_len)
    fade_in = np.linspace(0.0, 1.0, fade_len)
    overlap1 = wav1[-fade_len:] * fade_out
    overlap2 = wav2[:fade_len] * fade_in
    cross = overlap1 + overlap2
    return np.concatenate([wav1[:-fade_len], cross, wav2[fade_len:]])


def split_text_no_overlap(text, max_len=300):
    sentences = re.split(r'([。！？])', text)
    sentence_groups = []
    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i] + sentences[i + 1]
        sentence_groups.append(sentence)

    segments = []
    current_segment = ""
    for sentence in sentence_groups:
        if len(current_segment) + len(sentence) <= max_len:
            current_segment += sentence
        else:
            segments.append(current_segment)
            current_segment = sentence
    if current_segment:
        segments.append(current_segment)

    return [(i, "", seg) for i, seg in enumerate(segments)]
