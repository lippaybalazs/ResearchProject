import os
import eel
import json
import time
import frequency
import shutil

from typing import List, Tuple

OS = "windows" if os.name == "nt" else "unix"

INSTRUMENTS_DIR = os.path.abspath("instruments")

LOOKAHEAD_BEATS = 4

frequency_map: List[Tuple[str,float]] = frequency.default_frequency_map

class Rail:
    def __init__(self, id: int, column_count: int, column_spacing: int, x: int, y: int, color: str, draw: bool, image: str = None):
        self.id = id
        self.column_count = column_count
        self.column_spacing = column_spacing
        self.x = x
        self.y = y
        self.color = color
        self.draw = draw
        self.image = image

    def to_json(self):
        return {
            "id": self.id,
            "column_count": self.column_count,
            "column_spacing": self.column_spacing,
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "draw": self.draw,
            "image": self.image
        }

class Visual:
    def __init__(self, rail: int, columns: List[int] = []):
        self.rail = rail
        self.columns = columns

    def to_json(self):
        return {
            "rail": self.rail,
            "columns": self.columns
        }

class Note:
    def __init__(self, beat: float, length: float, notes: List[str] = [], visuals: List[Visual] = []):
        self.beat = beat
        self.length = length
        self.notes = notes
        self.visuals = visuals

    def to_json(self):
        return {
            "beat": self.beat,
            "length": self.length,
            "notes": self.notes,
            "visuals": [visual.to_json() for visual in self.visuals]
        }

class Song:
    def __init__(self, title: str, directory: str, instrument: str = None, background: str = None, bpm: int = None, notes: List[Note] = [], image: str = None):
        self.title = title
        self.instrument = instrument
        self.bpm = bpm
        self.notes = notes
        self.image = image
        self.background = background
        self.directory = directory

    def to_json(self):
        return {
            "title": self.title,
            "directory": self.directory,
            "intrument": self.instrument,
            "bpm": self.bpm,
            "notes": [note.to_json() for note in self.notes],
            "image": self.image,
            "background": self.background
        }

class Instrument:
    def __init__(self, name: str, directory: str, rails: List[Rail] = [], songs: List[str] = [], image: str = None):
        self.name = name
        self.directory = directory
        self.rails = rails
        self.songs = songs
        self.image = image

    def to_json(self):
        return {
            "name": self.name,
            "directory": self.directory,
            "rails": [rail.to_json() for rail in self.rails],
            "songs": self.songs,
            "image": self.image,
        }

def parse_instruments() -> List[Instrument]:
    instruments: List[Instrument] = []
    for instrument in os.listdir(INSTRUMENTS_DIR):
        try:
            file = open(os.path.join(INSTRUMENTS_DIR, instrument, "instrument.json"))
            instrument_json = json.loads(file.read())
            file.close()
            image = ""
            image_path = os.path.join(INSTRUMENTS_DIR, instrument, "thumbnail.jpg")
            if os.path.exists(image_path):
                shutil.copyfile(image_path,os.path.join(eel.root_path, "temp", instrument + ".jpg"))
                image = "temp/" + instrument + ".jpg"

            instruments.append(Instrument(
                name = instrument_json["name"], 
                directory = instrument, 
                image = image
            ))
        except Exception:
            pass
    return instruments

def parse_songs(instrument_directory: str) -> List[Song]:
    songs: List[Song] = []
    for song in os.listdir(os.path.join(INSTRUMENTS_DIR, instrument_directory)):
        try:
            file = open(os.path.join(INSTRUMENTS_DIR, instrument_directory, song, "song.json"))
            song_json = json.loads(file.read())
            file.close()

            image = ""
            image_path = os.path.join(INSTRUMENTS_DIR, instrument_directory, song, "thumbnail.jpg")
            if os.path.exists(image_path):
                shutil.copyfile(image_path,os.path.join(eel.root_path, "temp", instrument_directory + "_" + song + ".jpg"))
                image = "temp/" + instrument_directory + "_" + song + ".jpg"


            songs.append(Song(
                title = song_json["title"],
                directory = song,
                image = image
            ))
        except Exception:
            pass
    return songs

def load_instrument(instrument_directory) -> Instrument:
    
    file = open(os.path.join(INSTRUMENTS_DIR, instrument_directory, "instrument.json"))
    instrument_json = json.loads(file.read())
    file.close()

    rails: List[Rail] = []
    for rail in instrument_json["rails"]:
        image = ""
        if rail["image"] is not None:
            image_path = os.path.join(INSTRUMENTS_DIR, instrument_directory, rail["image"])
            if os.path.exists(image_path):
                shutil.copyfile(image_path,os.path.join(eel.root_path, "temp", instrument_directory + "_rail_" + rail["image"]))
                image = "temp/" + instrument_directory + "_rail_" + rail["image"]

        rails.append(Rail(
            id = rail["id"],
            column_count = rail["column_count"],
            column_spacing = rail["column_spacing"],
            x = rail["x"],
            y = rail["y"],
            color = rail["color"],
            draw = rail["draw"],
            image = image
        ))

    return Instrument(
        name = instrument_json["name"],
        directory = instrument_directory,
        rails = rails
    )

def load_song(instrument_directory, song_directory):
    file = open(os.path.join(INSTRUMENTS_DIR, instrument_directory, song_directory, "song.json"))
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

    background = ""
    if song_json["background"] is not None:
        background = song_json["background"]
    if background != "" and background[0] != "#":
        background_path = os.path.join(INSTRUMENTS_DIR, instrument_directory, song_directory, background)
        if os.path.exists(background_path):
            shutil.copyfile(background_path,os.path.join(eel.root_path, "temp", instrument_directory + "_" + song_directory + "_background_" + background))
            background = "temp/" + instrument_directory + "_" + song_directory + "_background_" + background


    song_object = Song(
        title = song_json["title"],
        directory = song_directory,
        instrument = song_json["instrument"],
        bpm = song_json["bpm"],
        notes = notes,
        background = background
    )
    return song_object


def load_instrument_frequency_map(instrument_directory):
    
    global frequency_map
    frequency_map = frequency.default_frequency_map
    try:
        file = open(os.path.join(INSTRUMENTS_DIR, instrument_directory, "correction.json"))
        corrections_json = json.loads(file.read())
        file.close()

        for note in corrections_json.items():
            frequency_map.append((note[0], note[1]))

    except Exception:
        pass


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
                        notes.append(frequency.get_note(freq, frequency_map))
                    
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
                    "length": next_note.length * 4
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
combo = 0
def beat_tick():
    global shedule
    global beat_counter
    global fade_out_beats
    global score
    global combo

    now = time.time()
    eel.sleep(shedule - now)

    if len(note_queue) > 0:
        if beat_counter - LOOKAHEAD_BEATS >= 0:
            requested_note = note_queue[0]
            if requested_note is not None and requested_note.beat == beat_counter - LOOKAHEAD_BEATS:
                notes = []
                for freq in [item for sublist in frequency.frequencies[-5:-1] for item in sublist]:
                    notes.append(frequency.get_note(freq, frequency_map))
                
                if all(item in notes for item in requested_note.notes):
                    combo += 1
                    score += combo + 1
                else:
                    combo = 0  
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
    eel.UpdateScore(score,combo)
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
def load_frequency_map(instrument):
    load_instrument_frequency_map(instrument)

@eel.expose
def get_frequencies():
    notes = [[frequency.get_note(freq, frequency_map) for freq in frequencies] for frequencies in frequency.frequencies]
    return (notes, frequency.frequencies)

@eel.expose
def get_instruments():
    return [instrument.to_json() for instrument in parse_instruments()]

@eel.expose
def get_songs(insturment_name):
    return [song.to_json() for song in parse_songs(insturment_name)]

@eel.expose
def hard_load_instrument(instrument_name):
    return load_instrument(instrument_name).to_json()

@eel.expose
def stop_song():
    global early_stop
    early_stop = True
    try:
        eel.sleep(60 / played_song.bpm)
    except Exception:
        pass
    early_stop = False

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
    load_instrument_frequency_map(instrument)

    early_stop = True
    eel.sleep(60 / played_song.bpm)
    early_stop = False
    
    shedule = time.time()
    eel.spawn(blocker_beat_tick)
    return played_song.to_json()


@eel.expose
def start_song(instrument, song):
    global shedule
    global played_song
    global beat_counter
    global note_queue
    global early_stop
    global fade_out_beats
    global score
    global combo
    combo = 0
    score = 0
    fade_out_beats = 4
    note_queue = []
    beat_counter = 0
    played_song = load_song(instrument, song)
    load_instrument_frequency_map(instrument)

    early_stop = True
    eel.sleep(60 / played_song.bpm)
    early_stop = False
    
    shedule = time.time()
    eel.spawn(beat_tick)
    return played_song.to_json()

eel.start('index.html', port=0, mode='chrome')#, cmdline_args=['--kiosk'])
