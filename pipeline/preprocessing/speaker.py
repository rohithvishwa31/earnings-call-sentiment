def get_speaker_type(speaker, exec_names):

    if speaker == "operator":
        return "operator"
    elif speaker in exec_names:
        return "executive"
    else:
        return "analyst"