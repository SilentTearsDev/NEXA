from speech.skills.smalltalk import try_smalltalk

def respond(text: str) -> str|None:
    for skill in (try_smalltalk,):
        ans = skill(text)
        if ans:
            return ans
    return None
