from api import note
from piano_transcription_inference import PianoTranscription, sample_rate, load_audio
import mido

transer = PianoTranscription(device='cuda')

def GetMidiEvents(path : str) -> list:
    '''
    Function to get midi object from audio file

    Args:

    path : audio file path
    '''
    (audio,_) = load_audio(path, sr=sample_rate, mono=True)
    res_dict = transer.transcribe(audio,False)

    return res_dict['est_note_events']

def AudioAnalysis(path : str) -> list:
    '''
    Function to generate a list of notes

    Args:

    path : audio file path
    '''
    noteList = GetMidiEvents(path)
    noteList.sort(key = lambda note : note['onset_time'])
    ans = [note.pianoNote(i['midi_note'],int(i['onset_time']*1000),int(i['offset_time']*1000),i['velocity']) for i in noteList]
    return ans

if __name__ == '__main__':
    pass