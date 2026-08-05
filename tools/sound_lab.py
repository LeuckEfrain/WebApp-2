import math
import random
import wave
from pathlib import Path


# ============================================================
# Sound Lab
# Dependency-free WAV generator
#
# Uses only Python's standard library.
# ============================================================

SAMPLE_RATE = 44100
OUTPUT_DIR = Path(__file__).resolve().parent / "sound_lab_output"

MASTER_VOLUME = 0.55
SOUND_SET_VERSION = "1.0.0"

# ============================================================
# Basic synthesis
# ============================================================

def envelope(t, duration, attack=0.005, decay=0.08, sustain=0.7, release=0.08):
    """
    Simple ADSR-style envelope.
    """

    if t < attack:
        return t / attack

    decay_start = attack
    decay_end = attack + decay

    if t < decay_end:
        progress = (t - decay_start) / decay
        return 1.0 - ((1.0 - sustain) * progress)

    release_start = max(
        decay_end,
        duration - release
    )

    if t < release_start:
        return sustain

    release_length = duration - release_start

    if release_length <= 0:
        return 0.0

    progress = (t - release_start) / release_length

    return sustain * (1.0 - progress)


def sine(freq, t):
    return math.sin(
        2.0 * math.pi * freq * t
    )


def triangle(freq, t):
    phase = (freq * t) % 1.0

    return (
        4.0 * abs(phase - 0.5)
        - 1.0
    )


def soft_square(freq, t):
    """
    A softened square wave.
    """

    value = sine(freq, t)

    return (
        0.75 * value
        + 0.25 * math.sin(
            2.0 * math.pi * freq * 2.0 * t
        )
    )


def pitch_curve(start, end, progress):
    """
    Exponential pitch interpolation.
    """

    if start <= 0 or end <= 0:
        return start + (
            (end - start) * progress
        )

    return start * (
        (end / start) ** progress
    )


# ============================================================
# WAV writer
# ============================================================

def write_wav(path, samples):
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with wave.open(
        str(path),
        "wb"
    ) as wav:

        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)

        frames = bytearray()

        for sample in samples:

            sample = max(
                -1.0,
                min(1.0, sample)
            )

            value = int(
                sample * 32767
            )

            frames.extend(
                value.to_bytes(
                    2,
                    byteorder="little",
                    signed=True
                )
            )

        wav.writeframes(frames)


def render(duration, generator):
    sample_count = int(
        duration * SAMPLE_RATE
    )

    samples = []

    for i in range(sample_count):

        t = i / SAMPLE_RATE

        value = generator(
            t,
            duration
        )

        samples.append(
            value * MASTER_VOLUME
        )

    return samples


# ============================================================
# 1. Soft UI Click
# ============================================================

def soft_click(t, duration):
    """
    Refined tactile UI click.

    Short, dry, and understated.
    Designed to feel like a physical interface
    with a very subtle electronic character.
    """

    # Very short tonal body.
    body = (
        sine(620, t)
        * math.exp(-t * 65)
        * 0.18
    )

    # Higher-frequency transient gives the click
    # a little definition without sounding harsh.
    transient = (
        sine(1850, t)
        * math.exp(-t * 115)
        * 0.10
    )

    # Extremely brief noise component gives it
    # the tactile quality of a physical button.
    noise = (
        random.uniform(-1.0, 1.0)
        * math.exp(-t * 180)
        * 0.055
    )

    return body + transient + noise

# ============================================================
# 2. Refined Selection
# ============================================================

def selection(t, duration):
    """
    A short click followed by a tiny tonal confirmation.
    """

    click = (
        sine(720, t)
        * math.exp(-t * 50)
        * 0.20
    )

    tone_start = 0.035

    if t < tone_start:
        tone = 0.0

    else:

        local = t - tone_start

        tone = (
            sine(1047, local)
            * math.exp(-local * 18)
            * 0.25
        )

    return click + tone


# ============================================================
# 3. Menu Open
# ============================================================

def menu_open(t, duration):
    """
    Gentle ascending two-tone system sound.
    """

    split = 0.085

    if t < split:

        local = t

        env = envelope(
            local,
            split,
            attack=0.008,
            decay=0.035,
            sustain=0.45,
            release=0.035
        )

        return (
            sine(660, local)
            * env
            * 0.22
        )

    local = t - split

    env = envelope(
        local,
        duration - split,
        attack=0.008,
        decay=0.05,
        sustain=0.45,
        release=0.06
    )

    return (
        sine(880, local)
        * env
        * 0.22
    )


# ============================================================
# 4. Menu Close
# ============================================================

def menu_close(t, duration):
    """
    Descending counterpart to menu_open.
    """

    split = 0.085

    if t < split:

        local = t

        env = envelope(
            local,
            split,
            attack=0.008,
            decay=0.035,
            sustain=0.45,
            release=0.035
        )

        return (
            sine(880, local)
            * env
            * 0.22
        )

    local = t - split

    env = envelope(
        local,
        duration - split,
        attack=0.008,
        decay=0.05,
        sustain=0.45,
        release=0.06
    )

    return (
        sine(660, local)
        * env
        * 0.22
    )


# ============================================================
# 5. Success Chime
# ============================================================

def success(t, duration):
    """
    Light two-note confirmation.
    """

    first_duration = 0.12

    if t < first_duration:

        local = t

        env = envelope(
            local,
            first_duration,
            attack=0.008,
            decay=0.05,
            sustain=0.35,
            release=0.04
        )

        return (
            sine(784, local)
            * env
            * 0.20
        )

    local = t - first_duration

    env = envelope(
        local,
        duration - first_duration,
        attack=0.008,
        decay=0.08,
        sustain=0.40,
        release=0.10
    )

    return (
        sine(1047, local)
        * env
        * 0.22
    )


# ============================================================
# 6. Error
# ============================================================

def error(t, duration):
    """
    Subdued negative response.
    Not an alarm.
    """

    split = 0.10

    if t < split:

        local = t

        env = envelope(
            local,
            split,
            attack=0.005,
            decay=0.035,
            sustain=0.35,
            release=0.04
        )

        return (
            sine(440, local)
            * env
            * 0.22
        )

    local = t - split

    env = envelope(
        local,
        duration - split,
        attack=0.005,
        decay=0.05,
        sustain=0.35,
        release=0.08
    )

    return (
        sine(330, local)
        * env
        * 0.20
    )


# ============================================================
# 7. Search
# ============================================================

def search(t, duration):
    """
    Search / processing sound.

    A tiny tactile activation followed by a very
    subtle electronic response. Designed to feel
    like a refined system interface rather than
    a sci-fi scanner.
    """

    # --------------------------------------------------------
    # Initial tactile activation
    # --------------------------------------------------------

    activation = (
        sine(680, t)
        * math.exp(-t * 75)
        * 0.14
    )

    # Tiny high-frequency transient.
    transient = (
        sine(1450, t)
        * math.exp(-t * 120)
        * 0.045
    )

    # --------------------------------------------------------
    # Delayed processing response
    # --------------------------------------------------------

    response_start = 0.075

    if t < response_start:
        response = 0.0
    else:

        local = t - response_start

        response_env = (
            math.exp(-local * 24)
        )

        response = (
            sine(920, local)
            * response_env
            * 0.075
        )

        # Very subtle second harmonic.
        response += (
            sine(1840, local)
            * response_env
            * 0.012
        )

    return (
        activation
        + transient
        + response
    )
# ============================================================
# 8. Download Complete
# ============================================================

def download_complete(t, duration):
    """
    Slightly more substantial completion sound.
    Still restrained.
    """

    notes = [
        (0.00, 659),
        (0.105, 784),
        (0.21, 988),
    ]

    value = 0.0

    for start, freq in notes:

        if t < start:
            continue

        local = t - start

        env = math.exp(
            -local * 14
        )

        value += (
            sine(freq, local)
            * env
            * 0.15
        )

    return value


# ============================================================
# Generate reference set
# ============================================================

SOUNDS = [
    {
        "filename": "01_soft_click.wav",
        "duration": 0.16,
        "generator": soft_click,
        "purpose": "Basic interface interaction",
    },
    {
        "filename": "02_selection.wav",
        "duration": 0.22,
        "generator": selection,
        "purpose": "Selection confirmation",
    },
    {
        "filename": "03_menu_open.wav",
        "duration": 0.22,
        "generator": menu_open,
        "purpose": "Opening menus or panels",
    },
    {
        "filename": "04_menu_close.wav",
        "duration": 0.22,
        "generator": menu_close,
        "purpose": "Closing menus or panels",
    },
    {
        "filename": "05_success.wav",
        "duration": 0.32,
        "generator": success,
        "purpose": "Successful operation",
    },
    {
        "filename": "06_error.wav",
        "duration": 0.30,
        "generator": error,
        "purpose": "Failed or rejected operation",
    },
    {
        "filename": "07_search.wav",
        "duration": 0.30,
        "generator": search,
        "purpose": "Search or processing started",
    },
    {
        "filename": "08_download_complete.wav",
        "duration": 0.45,
        "generator": download_complete,
        "purpose": "Download or data transfer completed",
    },
]

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print("=" * 60)
    print("WEBAPP SOUND LAB")
    print("=" * 60)
    print()
    print("Generating reference sounds...")
    print()

    print(
    f"Sound set version: {SOUND_SET_VERSION}"
    )
print()

for sound in SOUNDS:

    filename = sound["filename"]
    duration = sound["duration"]
    generator = sound["generator"]
    purpose = sound["purpose"]

    path = (
        OUTPUT_DIR
        / filename
    )

    samples = render(
        duration,
        generator
    )

    write_wav(
        path,
        samples
    )

    print(
        f"Created: {filename}"
    )
    print(
        f"  Purpose: {purpose}"
    )
    print()
    print("Done.")
    print()
    print(
        f"Sounds are in:\n"
        f"  {OUTPUT_DIR}"
    )
    print()


if __name__ == "__main__":
    main()