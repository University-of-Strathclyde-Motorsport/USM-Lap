"""
This script converts track data from Excel to JSON.
"""

from usmlap.track import save_track_data
from usmlap.track.track_data import load_track_from_spreadsheet

EXCEL_TRACK_FILE = "FS AutoX Germany 2012.xlsx"

TRACKS = [
    "Acceleration.xlsx",
    "Autodromo Nazionale Monza.xlsx",
    "Donington Park.xlsx",
    "FS AutoX Nebraska 2013.xlsx",
    "FS Endurance Australia 2011.xlsx",
    "FS Endurance Austria 2012.xlsx",
    "FS Endurance Germany 2010.xlsx",
    "FS Endurance Michigan 2012.xlsx",
    "FS Endurance Michigan 2014.xlsx",
    "Indianapolis Motor Speedway.xlsx",
    "Spa-Francorchamps.xlsx",
]

for track in TRACKS:
    try:
        track_data = load_track_from_spreadsheet(track)
        save_track_data(track_data)
    except FileExistsError:
        continue
