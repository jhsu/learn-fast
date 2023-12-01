import os
from elevenlabs import generate
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

from learn_fast.lesson_planner import LessonPlanner

load_dotenv(find_dotenv(), override=True)

oa = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION_ID"),
)

voice = os.environ.get("ELEVENLABS_VOICE_ID")

assistant_id = os.environ.get("OPENAI_ASSISTANT_ID")

def main():
    topic = input("What topic do you want to learn about?")
    planner = LessonPlanner(client=oa, topic=topic, assistant=assistant_id)
    plan = planner.prepare_lesson_plan()
    print(plan)

    try:
        os.makedirs(f"./lessons/{topic}")
    except FileExistsError:
        print(f"Directory already exists, remove the folder './lessons/{topic}' and try again.")
        raise

    def next_plan():
        lesson = planner.create_next_lesson()
        print(lesson)

        audio_stream = generate(
            text=lesson,
            voice="Bella",
            # model="eleven_multilingual_v2"
            model="eleven_monolingual_v1",
            stream=True,
            api_key=os.environ.get("ELEVENLABS_API_KEY"),
        )
        buffer = []
        for chunk in audio_stream:
            buffer.append(chunk)

        with open(f"./{topic}/lesson{planner.current_lesson}.wav", "wb") as f:
            for chunk in buffer:
                # stream(chunk)
                f.write(chunk)

    next_plan()

    while input("next lesson? [Y/n]") == "Y":
        next_plan()


if __name__ == "__main__":
    main()