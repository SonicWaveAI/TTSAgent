import platform
import torch
from pkg.spark_tts.cli.SparkTTS import SparkTTS
from ...config import Config
import os
from datetime import datetime
import soundfile as sf
from .segment import split_text_no_overlap, crossfade, fade_audio
import numpy as np
import threading
from pkg.util.sound_convert import m4a2wav


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class TTSImpl:
    model = None
    model_path = ""
    default_model = ""
    custom_model = ""
    result_path = ""
    with_clean = False
    device_name = "mps:0"

    mm = dict()

    def __init__(self, model_path=Config.MODEL_PATH, default_model=Config.DEFAULT_MODEL_PATH,
                 custom_model=Config.CUSTOM_MODEL_PATH, result_path=Config.RESULT_PATH, with_clean=False):
        self.model_path = model_path
        self.default_model = default_model
        self.custom_model = custom_model
        self.result_path = result_path
        self.with_clean = with_clean
        self.infer_lock = threading.Lock()

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model path {self.model_path} does not exist")

        if platform.system() == "Darwin" and torch.backends.mps.is_available():
            device = torch.device("mps:0")
            self.device_name = "mps:0"
        elif torch.cuda.is_available():
            device = torch.device("cuda:0")
            self.device_name = "cuda:0"
        else:
            device = torch.device("cpu")
            self.device_name = "cpu"
        self.model = SparkTTS(self.model_path, device)
        self.mm = self.__init_default_models_map()

    def get_models(self):
        models = []
        for item in os.listdir(self.default_model):
            if os.path.isdir(os.path.join(self.default_model, item)):
                models.append(item)
        return models

    def generate_voice(self, model_type, text):
        prompt_speech_path = self.__get_prompt_speech_path(model_type)
        save_path = self.__generate_voice_file_path()
        self.__gen(text, prompt_speech_path, save_path)
        return save_path

    def generate_voice_custom(self, custom_id, text):
        save_path = self.__generate_voice_file_path()
        prompt_speech_path = self.__get_prompt_speech_path_custom(custom_id)
        self.__gen(text, prompt_speech_path, save_path)
        return save_path

    def __init_default_models_map(self):
        models_map = dict()
        for item in os.listdir(self.default_model):
            sub_path = os.path.join(self.default_model, item)
            if os.path.isdir(sub_path):
                audio_files = [f for f in os.listdir(sub_path) if f.endswith('.wav')]
                if not audio_files:
                    continue
                models_map[item] = os.path.join(self.default_model, item, audio_files[0])
        return models_map

    def __get_prompt_speech_path(self, model_type):
        return self.mm.get(model_type, None)

    def __get_prompt_speech_path_custom(self, custom_id):
        sub_path = os.path.join(self.custom_model, custom_id)
        audio_files = [f for f in os.listdir(sub_path) if f.endswith(".wav")]
        return os.path.join(sub_path, audio_files[0])

    def __generate_voice_file_path(self):
        return os.path.join(self.result_path, f"{datetime.now().strftime('%Y%m%d%H%M%S')}.wav")

    def read_clean(self, file_path):
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk
        if self.with_clean:
            os.remove(file_path)

    def __gen(self, text, prompt_speech_path, save_path):
        segments = split_text_no_overlap(text, max_len=180)

        all_wavs = []

        print("\n========== 文本分段预览 ==========")
        for i, ctx, main in segments:
            print(f"[段{i}] 上下文: {ctx}")
            print(f"[段{i}] 主句  : {main}")
        print("==================================\n")

        for i, context_text, main_text in segments:
            full_text = f"{context_text}{main_text}"
            with self.infer_lock:
                wav = self.model.inference(
                    full_text,
                    prompt_speech_path=prompt_speech_path,
                    prompt_text=None,
                    speed="moderate",
                    temperature=0.3

                )
            wav_np = wav if isinstance(wav, np.ndarray) else wav.detach().cpu().numpy()

            context_chars = len(context_text)
            full_chars = len(full_text)
            if context_chars > 0 and full_chars > 0:
                cut_len = int(len(wav_np) * context_chars / full_chars)
                wav_np = wav_np[cut_len:]

            wav_np = fade_audio(wav_np, fade_len=1600)
            all_wavs.append((i, wav_np))

        all_wavs.sort(key=lambda x: x[0])

        if not all_wavs:
            return
        full_wav = all_wavs[0][1]
        for i in range(1, len(all_wavs)):
            full_wav = crossfade(full_wav, all_wavs[i][1], fade_len=1600)

        sf.write(save_path, full_wav, samplerate=16000)

    def check_model(self, model_type):
        return self.mm.get(model_type, None)

    def upload_voice(self, voice_file):
        unique_id = datetime.now().strftime('%Y%m%d%H%M%S')
        voice_dir = os.path.join(self.custom_model, unique_id)
        os.makedirs(voice_dir, exist_ok=True)
        original_filename = voice_file.filename
        file_ext = os.path.splitext(original_filename)[1]
        voice_path = os.path.join(voice_dir, f'voice{file_ext}')
        voice_file.save(voice_path)
        if file_ext == ".m4a":
            m4a2wav(voice_path, os.path.join(voice_dir, "voice.wav"))
        return unique_id


tts_impl = TTSImpl()
