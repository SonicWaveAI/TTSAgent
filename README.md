# TTSAgent
基于spark-tts的语音生成代理

## 环境配置
```shell
# 使用conda或者python创建虚拟环境
python3 -m venv venv
./venv/bin/activate

pip install -r  requirements.txt
```

## 下载大模型
```shell
# 在当前虚拟环境下进入python环境
from huggingface_hub import snapshot_download
snapshot_download("SparkAudio/Spark-TTS-0.5B", local_dir="pretrained_models/Spark-TTS-0.5B")
```

## 修改配置文件
```shell
# 修改./app/modules/config.py
# 将当前项目工作目录替换为你的目录
```

## 启动项目
> make run