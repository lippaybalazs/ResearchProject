import os
import eel
import json
import time
import frequency

from typing import List

OS = "windows" if os.name == "nt" else "unix"
INSTRUMENTS_DIR = "instruments"

LOOKAHEAD_BEATS = 4

class Rail:
    def __init__(self, id: int, column_count: int, column_width: int, column_spacing: int, x: int, y: int, color: str, draw: bool):
        self.id = id
        self.column_count = column_count
        self.column_width = column_width
        self.column_spacing = column_spacing
        self.x = x
        self.y = y
        self.color = color
        self.draw = draw

class Visual:
    def __init__(self, rail: int, columns: List[int]):
        self.rail = rail
        self.columns = columns

class Note:
    def __init__(self, beat: float, length: float, notes: List[str], visuals: List[Visual]):
        self.beat = beat
        self.length = length
        self.notes = notes
        self.visuals = visuals

class Song:
    def __init__(self, title: str, instrument: str = None, bpm: int = None, notes: List[Note] = None):
        self.title = title
        self.instrument = instrument
        self.bpm = bpm
        self.notes = notes

class Instrument:
    def __init__(self, name: str, rails: List[Rail] = None, songs: List[str] = None):
        self.name = name
        self.rails = rails
        self.songs = songs

def parse_instruments() -> List[Instrument]:
    instruments: List[Instrument] = []
    for instrument in os.listdir(INSTRUMENTS_DIR):
        try:
            file = open(os.path.join(INSTRUMENTS_DIR, instrument, "instrument.json"))
            instrument_json = json.loads(file.read())
            file.close()
            
            instruments.append(Instrument(name = instrument_json["name"]))
        except Exception:
            pass
    return instruments

def parse_songs(instrument_name: str) -> List[Song]:
    songs: List[Song] = []
    for song in os.listdir(os.path.join(INSTRUMENTS_DIR, instrument_name)):
        try:
            file = open(os.path.join(INSTRUMENTS_DIR, instrument_name, song, "song.json"))
            song_json = json.loads(file.read())
            file.close()

            songs.append(Song(
                title = song_json["title"]
            ))
        except Exception:
            pass
    return songs

def load_song(instrument, song):
    file = open(os.path.join(INSTRUMENTS_DIR, instrument, song, "song.json"))
    song_json = json.loads(file.read())
    file.close()

    notes: List[Note] = []
    for note in song_json["notes"]:
        visuals: List[Visual] = []
        for visual in note["visuals"]:
            visuals.append(Visual(
                rail = visual["rail"],
                columns = visual["columns"]
            ))
        notes.append(Note(
            beat = note["beat"],
            length = note["length"],
            notes = note["notes"],
            visuals = visuals
        ))
        notes.sort(key=lambda x: x.beat)
    song_object = Song(
        title = song_json["title"],
        instrument = song_json["instrument"],
        bpm = song_json["bpm"],
        notes = notes
    )
    return song_object

played_song: Song = None
note_queue: List[Note] = []
beat_counter = 0
shedule = 0
early_stop = False
fade_out_beats = 0
def blocker_beat_tick():
    
    global shedule
    global beat_counter
    global fade_out_beats
    now = time.time()
    eel.sleep(shedule - now)

    if len(note_queue) > 0:
        if beat_counter - LOOKAHEAD_BEATS >= 0:
            
            requested_note = note_queue[0]
            if requested_note is not None and requested_note.beat == beat_counter - LOOKAHEAD_BEATS:
                while not early_stop:
                    notes = []
                    for freq in frequency.frequencies[-1]:
                        notes.append(frequency.get_note(freq, frequency.default_frequency_map))
                    
                    if all(item in notes for item in requested_note.notes):
                        shedule = time.time()
                        break
                    eel.sleep(0)  
            del note_queue[0]
        
    if len(played_song.notes) != 0:
        next_note: Note = played_song.notes[0]
        if next_note.beat == beat_counter:
            del played_song.notes[0]
        else:
            next_note = None
    else: 
        next_note = None

    note_queue.append(next_note)
    # eel put next_note
    notes = []
    if next_note is not None:
        for visual in next_note.visuals:
            for column in visual.columns:
                notes.append({
                    "rail_id": visual.rail,
                    "position" : column,
                    "length": 1
                })
    eel.PushBlockerNotes(notes)
    
    done = True
    for note in note_queue:
        if note is not None:
            done = False
            break
    if fade_out_beats > 0 and done:
        fade_out_beats -= 1
        done = False

    if (len(played_song.notes) != 0 or not done) and not early_stop:
        beat_counter += 0.25
        shedule += 60 / played_song.bpm * 0.25
        eel.spawn(blocker_beat_tick)

score = 0
def beat_tick():
    global shedule
    global beat_counter
    global fade_out_beats
    global score

    now = time.time()
    eel.sleep(shedule - now)

    if len(note_queue) > 0:
        if beat_counter - LOOKAHEAD_BEATS >= 0:
            requested_note = note_queue[0]
            if requested_note is not None and requested_note.beat == beat_counter - LOOKAHEAD_BEATS:
                notes = []
                for freq in [item for sublist in frequency.frequencies[-5:-1] for item in sublist]:
                    notes.append(frequency.get_note(freq, frequency.default_frequency_map))
                
                if all(item in notes for item in requested_note.notes):
                    score += 1  
            del note_queue[0]
        
    if len(played_song.notes) != 0:
        next_note: Note = played_song.notes[0]
        if next_note.beat == beat_counter:
            del played_song.notes[0]
        else:
            next_note = None
    else: 
        next_note = None

    note_queue.append(next_note)
    # eel put next_note
    notes = []
    if next_note is not None:
        for visual in next_note.visuals:
            for column in visual.columns:
                notes.append({
                    "rail_id": visual.rail,
                    "position" : column,
                    "length": next_note.length * 4
                })
    eel.UpdateScore(score)
    eel.PushNotes(notes)
    
    done = True
    for note in note_queue:
        if note is not None:
            done = False
            break
    if fade_out_beats > 0 and done:
        fade_out_beats -= 1
        done = False

    if (len(played_song.notes) != 0 or not done) and not early_stop:
        beat_counter += 0.25
        shedule += 60 / played_song.bpm * 0.25
        eel.spawn(beat_tick)


eel.init('web')

@eel.expose
def get_instruments():
    instruments_json = []
    for instrument in parse_instruments():
        instruments_json.append({
            "name": instrument.name
        })
    return instruments_json

@eel.expose
def get_songs(insturment_name):
    songs_json = []
    for song in parse_songs(insturment_name):
        songs_json.append({
            "title": song.title
        })
    return songs_json

@eel.expose
def load_instrument(instrument_name):
    
    file = open(os.path.join(INSTRUMENTS_DIR, instrument_name, "instrument.json"))
    instrument_json = json.loads(file.read())
    file.close()
    
    return instrument_json

@eel.expose
def start_blocker_song(instrument, song):
    global shedule
    global played_song
    global beat_counter
    global note_queue
    global early_stop
    global fade_out_beats
    fade_out_beats = 4
    note_queue = []
    beat_counter = 0
    played_song = load_song(instrument, song)

    early_stop = True
    eel.sleep(60 / played_song.bpm)
    early_stop = False
    
    shedule = time.time()
    eel.spawn(blocker_beat_tick)


@eel.expose
def start_song(instrument, song):
    global shedule
    global played_song
    global beat_counter
    global note_queue
    global early_stop
    global fade_out_beats
    global score
    score = 0
    fade_out_beats = 4
    note_queue = []
    beat_counter = 0
    played_song = load_song(instrument, song)

    early_stop = True
    eel.sleep(60 / played_song.bpm)
    early_stop = False
    
    shedule = time.time()
    eel.spawn(beat_tick)

eel.start('index.html', port=0, mode='chrome')#, cmdline_args=['--kiosk'])