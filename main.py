import os
import json
from typing import TypedDict
from elevenlabs import generate
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

from learn_fast.lesson_planner import LessonPlanner

load_dotenv(find_dotenv(), override=True)

oa = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION_ID"),
)

voice: str = os.environ.get("ELEVENLABS_VOICE_ID", "Bella")

assistant_id: str = os.environ.get("OPENAI_ASSISTANT_ID", "")

BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), './lessons')

class Metadata(TypedDict):
    topic: str
    assistant_id: str
    voice: str
    thread_id: str | None

def main():
    topic = input("What topic do you want to learn about? ")

    if not os.path.exists(os.path.join(BASE_PATH, topic)):
        os.makedirs(os.path.join(BASE_PATH, topic))
    else:
        print('continuing existing topic')

    config_path = os.path.join(BASE_PATH, topic, "metadata.json")
    # check if the config exists
    metadata: Metadata = {
        "topic": topic,
        "assistant_id": assistant_id,
        "voice": voice,
        "thread_id": None,
    }

    new_plan = True
    if os.path.exists(config_path):
        metadata = json.load(open(config_path, "r"))
        new_plan = False
    # TODO: need to figure out what the latest lesson number is
    planner = LessonPlanner(client=oa, topic=metadata["topic"], assistant=metadata["assistant_id"], thread_id=metadata["thread_id"])
    if new_plan:
        plan = planner.prepare_lesson_plan()
        print(plan)
        metadata["thread_id"] = planner.thread_id
        json.dump(metadata, open(config_path, "w"))

    def next_plan():
        lesson = planner.create_next_lesson()
        print(lesson)

        audio_stream = generate(
            text=lesson,
            voice=voice,
            model="eleven_monolingual_v1", # English
            stream=True,
            api_key=os.environ.get("ELEVENLABS_API_KEY"),
        )
        buffer: list[bytes] = []
        for chunk in audio_stream:
            buffer.append(chunk)

        lesson_path = os.path.join(BASE_PATH, topic, f"lesson{planner.current_lesson}.wav")
        with open(lesson_path, "wb") as f:
            for chunk in buffer:
                f.write(chunk)

    next_plan()

    while input("next lesson? [Y/n] ") == "Y":
        next_plan()


if __name__ == "__main__":
    main()