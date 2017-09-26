import logging
import re

import requests

from kalliope.core import FileManager
from kalliope.core.TTS.TTSModule import TTSModule, FailToLoadSoundFile, MissingTTSParameter

logging.basicConfig()
logger = logging.getLogger("kalliope")

TTS_URL = "https://api.naturalreaders.com/v0/tts/"
TTS_CONTENT_TYPE = "audio/mp3"
TTS_TIMEOUT_SEC = 30
API_KEY = "b98x9xlfs54ws4k0wc0o8g4gwc0w8ss"

VOICE_NAME_DATA = {
    "Sharon"    : {"id": 42, "lang": "en-US"},
    "Ava"       : {"id": 1, "lang": "en-US"},
    "Tracy"     : {"id": 37, "lang": "en-US"},
    "Ryan"      : {"id": 33, "lang": "en-US"},
    "Tom"       : {"id": 0, "lang": "en-US"},
    "Samantha"  : {"id": 2, "lang": "en-US"},
    "Mike"      : {"id": 1, "lang": "en-US"},
    "Rod"       : {"id": 41, "lang": "en-US"},
    "Rachel"    : {"id": 32, "lang": "en-UK"},
    "Peter"     : {"id": 31, "lang": "en-UK"},
    "Graham"    : {"id": 25, "lang": "en-UK"},
    "Serena"    : {"id": 4, "lang": "en-UK"},
    "Daniel"    : {"id": 3, "lang": "en-UK"},
    "Charles"   : {"id": 2, "lang": "en-UK"},
    "Audrey"    : {"id": 3, "lang": "en-UK"},
    "Rosa"      : {"id": 20, "lang": "es-ES"},
    "Alberto"   : {"id": 19, "lang": "es-ES"},
    "Juan"      : {"id": 5, "lang": "es-MX"},
    "Paulina"   : {"id": 6, "lang": "es-MX"},
    "Monica"    : {"id": 7, "lang": "es-ES"},
    "Jorge"     : {"id": 8, "lang": "es-ES"},
    "Alain"     : {"id": 7, "lang": "fr-FR"},
    "Juliette"  : {"id": 8, "lang": "fr-FR"},
    "Nicolas"   : {"id": 9, "lang": "fr-CA"},
    "Chantal"   : {"id": 10, "lang": "fr-CA"},
    "Bruno"     : {"id": 22, "lang": "fr-FR"},
    "Alice"     : {"id": 21, "lang": "fr-FR"},
    "Louice"    : {"id": 43, "lang": "fr-CA"},
    "Reiner"    : {"id": 5, "lang": "de-DE"},
    "Klara"     : {"id": 6, "lang": "de-DE"},
    "Klaus"     : {"id": 28, "lang": "de-DE"},
    "Sarah"     : {"id": 35, "lang": "de-DE"},
    "Yannick"   : {"id": 12, "lang": "de-DE"},
    "Petra"     : {"id": 11, "lang": "de-DE"},
    "Vittorio"  : {"id": 36, "lang": "it-IT"},
    "Chiara"    : {"id": 23, "lang": "it-IT"},
    "Frederica" : {"id": 14, "lang": "it-IT"},
    "Luca"      : {"id": 13, "lang": "it-IT"},
    "Celia"     : {"id": 44, "lang": "pt-PT"},
    "Luciana"   : {"id": 16, "lang": "pt-BR"},
    "Joana"     : {"id": 18, "lang": "pt-PT"},
    "Catarina"  : {"id": 17, "lang": "pt-PT"},
    "Emma"      : {"id": 45, "lang": "sv-SE"},
    "Erik"      : {"id": 46, "lang": "sv-SE"},
    "Oskar"     : {"id": 20, "lang": "sv-SE"},
    "Alva"      : {"id": 19, "lang": "sv-SE"},
    "Claire"    : {"id": 21, "lang": "nl-NL"},
    "Xander"    : {"id": 22, "lang": "nl-NL"}
}



class TCPTimeOutError(Exception):
    """
    This error is raised when the TCP connection has been lost. Probably due to a low internet
    connection while trying to access the remote API.
    """
    pass


class Naturalreader(TTSModule):

    def __init__(self, **kwargs):
        super(Naturalreader, self).__init__(**kwargs)
        self.src = "pw"
        self.voice = kwargs.get('voice', None)

        if self.voice is None:
            raise MissingTTSParameter("voice parameter is required by the NaturalReader TTS")

        if not VOICE_NAME_DATA.has_key( self.voice ):
            raise MissingTTSParameter("Unknow voice")
        # speech rate
        self.speed = kwargs.get('speed', 180)

        self.t = None

    def say(self, words):
        """
        :param words: The sentence to say
        """
        self.t = words
        self.generate_and_play(words, self._generate_audio_file)

    def _generate_audio_file(self):
        """
        Generic method used as a Callback in TTSModule
            - must provided the audio file and write it on the disk

        .. raises:: FailToLoadSoundFile, TCPTimeOutError
        """
        # Prepare payload
        payload = self.get_payload()


        headers = {}
        r = requests.get(TTS_URL, params=payload, headers=headers, timeout=TTS_TIMEOUT_SEC)
        content_type = r.headers['Content-Type']

        # Verify the response status code and the response content type
        if r.status_code != requests.codes.ok or content_type != TTS_CONTENT_TYPE:
            raise FailToLoadSoundFile("NatrualReader : Fail while trying to remotely access the audio file")

        # OK we get the audio we can write the sound file
        FileManager.write_in_file(self.file_path, r.content)

    def get_payload(self):
        """
        Generic method used load the payload used to access the remote api
        :return: Payload to use to access the remote api
        """
        return {
            "t": "%s" % self.t,
            "r": "%s" % VOICE_NAME_DATA[self.voice]["id"],
            "s": "%s" % self.speed,
            "src": "%s" % self.src
        }
