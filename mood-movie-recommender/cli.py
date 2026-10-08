"""Command-line version:  python cli.py"""
from llm_client import LLMError
from pipeline import build_recommender


def main():
    rec = build_recommender()
    print("Tell me how you feel (empty line to quit).")
    shown: list[str] = []
    mood = ""
    while True:
        text = input("\nYou: ").strip()
        if not text:
            break
        # Follow-ups like "too slow" refine the earlier request
        mood = f"{mood}. Feedback: {text}" if mood else text
        try:
            profile, results = rec.recommend(mood, exclude_titles=shown)
        except LLMError as err:
            print(f"Error: {err}")
            continue
        print(f"\nUnderstood: {profile.summary}\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['title']} ({r['year']}) - {r['genres']} - {r['runtime']} min - match {r['match_score']}/10")
            print(f"   {r['reason']}")
            shown.append(r["title"])
        print("\nNot quite right? Tell me what to change (e.g. 'too slow', 'something lighter').")


if __name__ == "__main__":
    main()
