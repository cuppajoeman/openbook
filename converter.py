import re

dry_run = False

# song_name = "i_could_write_a_book"
song_name = "there_will_never_be_another_you"
filename = f"src/openbook/{song_name}.ly.mako"
out_filename = f"src/openbook-KIN/{song_name}.ly.mako"

lilypond_accidental_to_canonical_accidental = {"is": "#", "es": "b"}
note_to_number = { "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, \
                   "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11, }

def convert_lilypond_note_to_number(lily_note: str) -> int:
    note = lily_note[0].upper()
    if len(lily_note) > 1:
        accidental = lilypond_accidental_to_canonical_accidental[lily_note[1:]]
    else:
        accidental = ""
    return note_to_number[note + accidental]


text = open(filename).read()

# Only get the melody
song_reg = re.compile("% if part=='Voice(.|\n)+?% endif")
song = song_reg.search(text).group()

# Find the key of the song and get it as a number
key_reg = re.compile(r"\\key (([abcdefg])(is|es)?).*")
key_result = key_reg.search(song)

key = key_result.group(2) + (key_result.group(3) if key_result.group(3) else "")
key_number = convert_lilypond_note_to_number(key)

def allow_dynamic_numbering_position(melody):
    "Adds some data underneath the key_match to do it"
    modified = key_reg.sub(r"\g<0>\n\t\\override Fingering.staff-padding =  #'()", melody.group())
    return modified

def convert_match_to_lily_note(note_match):
    return note_match.group(2) + (note_match.group(3) if note_match.group(3) else "")

def replace_match_by_key_interval(note_match) -> str:
    lily_note = convert_match_to_lily_note(note_match)
    key_interval = (convert_lilypond_note_to_number(lily_note) - key_number + 12)  % 12
    return note_match.group()[:-1] + f"-{str(key_interval)} "

def convert_note_line_to_key_interval_line(note_line):
    note_reg = re.compile(r"(([abcdefg])(is|es)?([\,'])?(\d)?(\.)?(\~)?( ))")
    modified = note_reg.sub(replace_match_by_key_interval, note_line.group())
    return modified

# Convert all lines containing | to use key interval notation
def convert_melody_to_key_interval_melody(melody):
    note_lines = re.compile(".*\|")
    key_interval_melody = note_lines.sub(convert_note_line_to_key_interval_line, melody.group())
    return key_interval_melody

def full_conversion(whole_file_text):
    result = song_reg.sub(convert_melody_to_key_interval_melody, whole_file_text, re.MULTILINE)
    result = song_reg.sub(allow_dynamic_numbering_position, result, re.MULTILINE)
    return result

# print(full_conversion(text))


if not dry_run:
    f = open(out_filename,"w")
    f.write(full_conversion(text))


