from datetime import datetime
import random
import re

# ---------- data pools ----------
DAD_JOKES = [
    "I used to play piano by ear, but now I use my hands.",
    "I would tell you a joke about UDP, but you might not get it.",
    "I only know 25 letters of the alphabet. I don’t know y.",
    "I’m reading a book about anti-gravity. It’s impossible to put down.",
    "Why don’t programmers like nature? Too many bugs.",
    "I asked my dog what's two minus two. He said nothing.",
    "I used to be addicted to the hokey pokey, but I turned myself around.",
    "Why did the scarecrow win an award? He was outstanding in his field.",
    "I told my computer I needed a break, and it said ‘No problem—I'll go to sleep.’",
    "What do you call 8 hobbits? A hobbyte.",
    "Why did the function break up with the loop? It needed space.",
    "Parallel lines have so much in common… it’s a shame they’ll never meet.",
    "I’m on a seafood diet. I see food and I eat it.",
    "Why did the math book look sad? Because it had too many problems.",
    "I would tell you a joke about construction, but I’m still working on it.",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "I got a reversible jacket for my birthday. I can’t wait to see how it turns out.",
    "What do you call a fake noodle? An impasta.",
    "Why couldn’t the bicycle stand up by itself? It was two-tired.",
    "I’m friends with 25 letters of the alphabet. I don’t know y.",
]

FUN_FACTS = [
    "Honey never spoils. Archaeologists have eaten 3,000-year-old honey.",
    "Octopuses have three hearts and blue blood.",
    "Bananas are berries, but strawberries aren’t.",
    "A day on Venus is longer than a year on Venus.",
    "Hot water can freeze faster than cold water—the Mpemba effect.",
    "Wombat poop is cube-shaped.",
    "There are more possible chess games than atoms in the observable universe (by many estimates).",
    "Sharks existed before trees.",
    "The Eiffel Tower can be 15 cm taller in the summer due to thermal expansion.",
    "Oxford University is older than the Aztec Empire.",
]

MOTIVATION = [
    "You’ve got this. Tiny steps beat standing still.",
    "Progress over perfection. Ship it, then improve.",
    "One focused hour today can save you five tomorrow.",
    "Future you will thank present you for starting now.",
]

COMPLIMENTS = [
    "Clean move. I like your style.",
    "Your keyboard must love you—those commands were crisp.",
    "That was elegant. Chef’s kiss.",
]

# ---------- helpers ----------
def _normalize(text: str) -> str:
    """lowercase + remove punctuation to make matching robust."""
    t = text.lower()
    t = re.sub(r"[^\w\s]", " ", t)  # drop punctuation like ?!,.:
    t = re.sub(r"\s+", " ", t).strip()
    return t

def _any_in(text: str, phrases: list[str]) -> bool:
    t = _normalize(text)
    return any(p in t for p in phrases)

def _token_set(text: str) -> set[str]:
    return set(_normalize(text).split())

def _now_time() -> str:
    now = datetime.now()
    return f"It’s {now.strftime('%H:%M:%S')} on {now.strftime('%Y-%m-%d')}."

# ---------- main entry ----------
def try_smalltalk(text: str) -> str | None:
    t = _normalize(text)
    tokens = set(t.split())

    # greetings
    if _any_in(t, ["hi", "hello", "hey", "yo", "good morning", "good afternoon", "good evening"]):
        return "Hey! Need something launched? Try `r np` or type `help`."

    # who are you / name / creator / what can you do
    if _any_in(t, ["who are you", "what are you"]):
        return "Im Nexa your local pc assisstant."
    if _any_in(t, ["what's your name", "whats your name", "your name"]):
        return "I’m Nexa."
    if _any_in(t, ["who made you", "creator", "who built you"]):
        return "I was created by Silent Dead Studio."
    if _any_in(t, ["what can you do", "help me", "capabilities"]):
        return "I launch programs/URLs via shortcuts, manage plugins/addons, and you can theme me in `nexa_tools`."

    # how are you
    if _any_in(t, ["how are you", "how r u", "how you doing"]):
        return "im good thanks :)"

    # thanks / bye
    if _any_in(t, ["thanks", "thank you", "thx"]):
        return "You're welcome 🙂"
    if _any_in(t, ["bye", "goodbye", "see ya", "see you", "cya"]):
        return "Bye! If you need me, just type `help`."

    # mention
    if "nexa" in tokens:
        return "I'm here. What should I run?"

    # time / date
    if _any_in(t, ["what time", "time is it", "time"]):
        return _now_time()
    if "date" in tokens:
        now = datetime.now()
        return f"Today is {now.strftime('%Y-%m-%d')}."

    # coin flip
    if _any_in(t, ["flip a coin", "coin flip", "flip coin", "heads or tails"]):
        return f"🪙 {random.choice(['Heads', 'Tails'])}"

    # dice roll
    if _any_in(t, ["roll a dice", "roll a die", "roll d6", "roll dice", "dice"]):
        return f"🎲 You rolled a {random.randint(1,6)}"

    # motivation / compliment
    if _any_in(t, ["motivate me", "motivation", "pep talk", "hype me"]):
        return random.choice(MOTIVATION)
    if _any_in(t, ["compliment me", "say something nice", "nice words"]):
        return random.choice(COMPLIMENTS)

    # jokes (dad jokes). accept: "joke", "tell me a joke", "another", "one more"
    if _any_in(t, ["joke", "tell me a joke", "another", "one more", "make me laugh"]):
        return random.choice(DAD_JOKES)

    # fun facts
    if _any_in(t, ["fun fact", "fact", "give me a fact", "hit me with a fact", "random fact"]):
        return "📚 " + random.choice(FUN_FACTS)

    # fallback
    return None
