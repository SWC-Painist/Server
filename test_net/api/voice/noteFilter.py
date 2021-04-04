from api.note import pianoNote

def ShortEventFilter(notes : list):
    new_len = 0
    for n in notes:
        if n.end - n.start >= 20:
            notes[new_len] = n
            new_len = new_len + 1

    notes = notes[0:new_len]
    return notes
