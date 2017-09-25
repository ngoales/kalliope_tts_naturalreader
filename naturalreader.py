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

        self.r = kwargs.get('voice', None)
        if self.voice is None:
            raise MissingTTSParameter("r parameter is required by the NaturalReader TTS")

        # speech rate
        self.s = kwargs.get('s', 180)

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
            "r": "%s" % self.r,
            "s": "%s" % self.s,
            "src": "%s" % self.src
        }
