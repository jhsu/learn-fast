from typing import Optional
from elevenlabs import Voice


class Podcaster:
    def __init__(self, voice: Optional[str]) -> None:
        if voice:
            self.voice = pick_voice(voice)


def pick_voice(voice: Optional[str]):
    return Voice(
        voice_id=voice
        if voice
        else "Pufl6aWbxUNdekXBSSum",  # Victoria - classy and mature
    )
