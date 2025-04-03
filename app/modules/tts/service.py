import platform
import torch
from pkg.spark_tts.cli.SparkTTS import SparkTTS
from ...config import Config
import os
from datetime import datetime
import soundfile as sf


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

    mm = dict()

    def __init__(self, model_path=Config.MODEL_PATH, default_model=Config.DEFAULT_MODEL_PATH,
                 custom_model=Config.CUSTOM_MODEL_PATH, result_path=Config.RESULT_PATH, with_clean=False):
        self.model_path = model_path
        self.default_model = default_model
        self.custom_model = custom_model
        self.result_path = result_path
        self.with_clean = with_clean

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model path {self.model_path} does not exist")

        if platform.system() == "Darwin" and torch.backends.mps.is_available():
            device = torch.device("mps:0")
        elif torch.cuda.is_available():
            device = torch.device("cuda:0")
        else:
            device = torch.device("cpu")
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
        with torch.no_grad():
            wav = self.model.inference(
                text,
                prompt_speech_path=prompt_speech_path,
                prompt_text=None
            )
            sf.write(save_path, wav, samplerate=16000)

    def check_model(self, model_type):
        return self.mm.get(model_type, None)


tts_impl = TTSImpl()
