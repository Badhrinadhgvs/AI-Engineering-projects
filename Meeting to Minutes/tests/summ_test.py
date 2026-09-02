from app.LLM import MeetLLM


def run_denver():
    m = MeetLLM("denver_extract.mp3")
    res = m.summarize()
    return res if res else None


def run_10():
    m = MeetLLM("10.mp3")
    res = m.summarize()
    return res if res else None


def run_afrikaans1():
    m = MeetLLM("afrikaans1.mp3")
    res = m.summarize()
    return res if res else None


def run_albanian1():
    m = MeetLLM("albanian1.mp3")
    res = m.summarize()
    return res if res else None


def run_arabic102():
    m = MeetLLM("arabic102.mp3")
    res = m.summarize()
    return res if res else None
