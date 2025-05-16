#================================================
#  ?                    ABOUT
#  @author      : Alexandre T. Enokida, João Pedro da Silva de Andrade
#  @createdOn   : 15 de maio de 2025
#  @description : Atividade do tópico de Reconhecimento de Fala
#================================================

import os

import pyaudio
from pocketsphinx import Decoder, Config

ACOUSTIC_MODEL = os.path.join("model", "pt-br", "cmusphinx-pt-br-5.2")
DICTIONARY = os.path.join("model", "pt-br", "br-pt.dic")
KEYWORDS_FILE = "keywords.list"

def configure_decoder():
  # config = Config()
  # config.set_string('-hmm', ACOUSTIC_MODEL)
  # config.set_string('-dict', DICTIONARY)
  # config.set_string('-kws', KEYWORDS_FILE)
  # config.set_float('-kws_threshold', 1e-20)
  config = Config(
        hmm=ACOUSTIC_MODEL,
        dict=DICTIONARY,
        kws=KEYWORDS_FILE,
        kws_threshold=1e-19,
    )
  decoder = Decoder(config)
  return decoder

def detect_keywords():
  decoder = configure_decoder()
  decoder.start_utt()

  audio = pyaudio.PyAudio()
  stream = audio.open(format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024)
  stream.start_stream()

  try:
    
    while True:
      buf = stream.read(1024, exception_on_overflow=False)
      if buf:
        decoder.process_raw(buf, False, False)
        if decoder.hyp() is not None:
          print(f"Keyword detected: {decoder.hyp().hypstr}")
          decoder.end_utt()
          decoder.start_utt()
          
      else:
        break
      
  except KeyboardInterrupt:
    print("\nExiting...")
    
  finally:
    decoder.end_utt()
    stream.stop_stream()
    stream.close()
    audio.terminate()

if __name__ == "__main__":
  detect_keywords()
