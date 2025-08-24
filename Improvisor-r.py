from music21 import *
from itertools import permutations
import random

def generate_melodic_cell(cell_numbers, key, quality='major'):
    """
    Generate a melodic cell based on scale degrees and key/quality.
    
    Args:
        cell_numbers: List of scale degrees (1-8 for current octave, >8 for higher, <0 for lower)
        key: The tonic key for the scale
        quality: Scale quality ('major', 'minor', or 'dominant')
    
    Returns:
        List of Note objects representing the melodic cell
    """
    # Determine the appropriate scale based on quality
    if quality == 'major':
        base_scale = scale.MajorScale(key).getPitches('C4', 'C5')
    elif quality == 'minor':
        base_scale = scale.DorianScale(key).getPitches()
    elif quality == 'dominant':
        base_scale = scale.MixolydianScale(key).getPitches()
    else:
        raise ValueError(f"Invalid quality: {quality}")
    
    melodic_cell = []
    for degree in cell_numbers:
        if degree >= 8:
            # Transpose up an octave for degrees 8+
            note_pitch = base_scale[(degree) % 8].transpose('P8')
        elif degree < 0:
            # Transpose down an octave for negative degrees
            note_pitch = base_scale[(degree % 8) - 1].transpose('-P8')
        else:
            # Use normal scale degrees
            note_pitch = base_scale[degree - 1]
        
        melodic_cell.append(note.Note(note_pitch))
    
    return melodic_cell


def generate_inversions(cell):
    """
    Generate all inversions of a melodic cell by rotating and transposing.
    
    Args:
        cell: List of Note objects representing the original cell
    
    Returns:
        List of inverted cells
    """
    inversions_list = [cell]
    
    for i in range(len(cell) - 1):
        # Rotate the cell and transpose the moved note by an octave
        rotated_cell = inversions_list[i][1:] + [inversions_list[i][0].transpose('P8')]
        inversions_list.append(rotated_cell)
    
    return inversions_list


def parse_chord_symbol(chord_symbol):
    """
    Parse a chord symbol into its root and quality.
    
    Args:
        chord_symbol: String representation of chord (e.g., 'Am', 'D7', 'GMaj')
    
    Returns:
        Tuple of (key, quality) or -1 if invalid
    """
    # Handle accidentals in the root
    if len(chord_symbol) > 1 and (chord_symbol[1] == '-' or chord_symbol[1] == '#'):
        root = chord_symbol[:2]
        quality_suffix = chord_symbol[2:]
    else:
        root = chord_symbol[0]
        quality_suffix = chord_symbol[1:]
    
    # Map suffixes to qualities
    quality_mapping = {
        'm': 'minor',
        '7': 'dominant', 
        'Maj': 'major'
    }
    
    if quality_suffix not in quality_mapping:
        return -1
    
    return root, quality_mapping[quality_suffix]


def parse_chord_progression(progression_string):
    """
    Parse a chord progression string into root/quality pairs.
    
    Args:
        progression_string: Comma-separated chord symbols
    
    Returns:
        List of (root, quality) tuples
    """
    chord_symbols = progression_string.split(',')
    roots_and_qualities = []
    
    for chord_symbol in chord_symbols:
        parsed_chord = parse_chord_symbol(chord_symbol)
        if parsed_chord != -1:
            roots_and_qualities.append(parsed_chord)
    
    return roots_and_qualities


def generate_voiceleading_targets(roots_and_qualities):
    """
    Generate target chord tones for voice leading.
    
    Args:
        roots_and_qualities: List of (root, quality) tuples
    
    Returns:
        List of target chord tones for each chord
    """
    voiceleading_targets = []
    
    for root, quality in roots_and_qualities:
        # Use root, third, and fifth as target chord tones
        voiceleading_targets.append(generate_melodic_cell([1, 3, 5], root, quality))
    
    return voiceleading_targets


def voice_lead_note(source_note, target_chord):
    """
    Voice lead a note to the nearest chord tone.
    
    Args:
        source_note: Note to voice lead
        target_chord: List of target chord tones
    
    Returns:
        Voice-led note or -1 if no valid voice leading found
    """
    half_step_options = []
    whole_step_options = []
    unison_options = []
    
    for chord_tone in target_chord:
        interval = abs(source_note.pitch.midi - chord_tone.pitch.midi) % 12
        
        if interval == 0:  # Unison
            unison_options.append(source_note)
        elif interval == 1 or interval == 11:  # Half step
            if interval == 1:
                half_step_options.append(source_note.transpose('-m2'))
            else:
                half_step_options.append(source_note.transpose('m2'))
        elif interval == 2 or interval == 10:  # Whole step
            if interval == 2:
                whole_step_options.append(source_note.transpose('-M2'))
            else:
                whole_step_options.append(source_note.transpose('M2'))
    
    # Prefer smaller intervals
    if half_step_options:
        return random.choice(half_step_options)
    if whole_step_options:
        return random.choice(whole_step_options)
    if unison_options:
        return source_note
    
    return -1


def generate_possible_cells(key, quality, cell_patterns):
    """
    Generate all possible cells for a given chord, including permutations and inversions.
    
    Args:
        key: Chord root
        quality: Chord quality
        cell_patterns: List of cell patterns to use
    
    Returns:
        List of all possible cells for the chord
    """
    possible_cells = []
    
    # Generate all permutations of each cell pattern
    for pattern in cell_patterns:
        for permuted_pattern in permutations(pattern):
            # Generate cell in original octave
            cell = generate_melodic_cell(list(permuted_pattern), key, quality)
            possible_cells.append(cell)
            
            # Generate cell transposed down an octave
            transposed_cell = [note.transpose('-P8') for note in cell]
            possible_cells.append(transposed_cell)
    
    # Add all inversions
    all_cells_with_inversions = []
    for cell in possible_cells:
        all_cells_with_inversions.extend(generate_inversions(cell))
    
    return all_cells_with_inversions


def main():
    """Main function to generate melodic lines over chord progressions."""
    # Chord progression (Giant Steps)
    progression_string = 'D-Maj,E7,AMaj,C7,FMaj,FMaj,Bm,E7,AMaj,C7,FMaj,A-7,D-Maj,D-Maj,Gm,C7,FMaj,FMaj,Bm,E7,AMaj,E-m,A-7,D-Maj,D-Maj,Gm,C7,FMaj,FMaj,E-m,A-7'
    
    # Cell patterns to use
    cell_patterns = [
        [1, 2, 3, 5],
        [1, -2, -1, 1],
        [1, 3, 5, -1],
        [4, 3, 2, 1],
        [5, 4, 3, 1],
        [1, 2, 3, 1],
        [3, 2, 1, -1],
        [5, 6, 7, 8],
        [3, 4, 5, 7],
        [9, 7, 5, 3],
        [5, 7, 9, 11],
        [5, 6, 7, 8]
    ]
    
    # Parse chord progression
    roots_and_qualities = parse_chord_progression(progression_string)
    voiceleading_targets = generate_voiceleading_targets(roots_and_qualities)
    
    # Generate possible cells for each chord
    possible_cells_per_chord = []
    for root, quality in roots_and_qualities:
        possible_cells_per_chord.append(
            generate_possible_cells(root, quality, cell_patterns)
        )
    
    # Create output stream
    composition = stream.Stream()
    
    # Start with a random cell for the first chord
    current_cell = random.choice(possible_cells_per_chord[0])
    composition.append(current_cell)
    
    # Generate melody for multiple choruses
    num_choruses = 5
    
    for chorus in range(num_choruses):
        for chord_index in range(len(roots_and_qualities) - 1):
            # Try to voice lead the last note of current cell
            led_note = voice_lead_note(current_cell[3], voiceleading_targets[chord_index + 1])
            
            # If no voice leading found, try the first note
            if led_note == current_cell[3]:
                led_note = voice_lead_note(current_cell[0], voiceleading_targets[chord_index + 1])
            
            # Find cells that start with the voice-led note
            possible_next_cells = []
            for cell in possible_cells_per_chord[chord_index + 1]:
                if cell[0].pitch.midi == led_note.pitch.midi:
                    possible_next_cells.append(cell)
            
            # If no cells found, try again with first note voice leading
            if not possible_next_cells:
                led_note = voice_lead_note(current_cell[0], voiceleading_targets[chord_index + 1])
                for cell in possible_cells_per_chord[chord_index + 1]:
                    if cell[0].pitch.midi == led_note.pitch.midi:
                        possible_next_cells.append(cell)
            
            # Fallback to current cell if still no options
            if not possible_next_cells:
                possible_next_cells.append(current_cell)
            
            # Choose next cell
            next_cell = random.choice(possible_next_cells)
            
            # Add to composition with proper rhythm
            cell_stream = stream.Stream()
            for note_obj in next_cell:
                cell_stream.append(note.Note(note_obj.pitch, quarterLength=0.5))
            
            composition.append(cell_stream)
            current_cell = next_cell
    
    # Display the composition
    composition.show()


if __name__ == "__main__":
    main()