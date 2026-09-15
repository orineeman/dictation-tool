#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
כלי הכתבה מקומי (Push-to-Talk)
לוחצים ומחזיקים את מקש ה-Option הימני (⌥ ימני), מדברים בעברית, משחררים -
הטקסט מתומלל מקומית (Whisper) ומוקלד אוטומטית לתוך השדה הפעיל בכל אפליקציה.
הכל רץ מקומית - שום קול לא נשלח לאינטרנט.
"""
import sys
import tempfile
import threading
import subprocess

import numpy as np
import sounddevice as sd
import soundfile as sf
from pynput import keyboard
from pynput.keyboard import Key, Controller as KeyboardController

import mlx_whisper

SAMPLE_RATE = 16000
MODEL = "mlx-community/whisper-large-v3-turbo"
HOTKEY_KEYS = {Key.alt, Key.alt_l, Key.alt_r}  # any Option key (⌥)
LANGUAGE = "he"

kb_controller = KeyboardController()
# Force pynput to inject text as literal Unicode characters instead of simulated
# keycodes. Otherwise it types via the keyboard layout active when this process
# started, so if Caps Lock later switches the system to the English layout, the
# Hebrew text comes out transliterated by key position (e.g. ח -> j, ל -> k).
kb_controller._mapping = {}

HOTKEY_DEBOUNCE_SEC = 0.15  # delay before actually opening the mic; a real macOS shortcut
                            # (Option+Left, Option+letter, ...) presses the second key almost
                            # immediately, while real dictation is Option held, then a pause, then speech

recording = False
audio_frames = []
lock = threading.Lock()
suppress_hotkey = False  # true while we are injecting text, to ignore our own synthetic keystrokes
other_key_pressed = False  # true if another key was pressed while Option was held (e.g. Option+Left to jump words) -
                            # in that case Option is being used for its normal macOS role, not as our hotkey
option_held = False  # true from Option press to Option release
start_timer = None  # pending timer that will open the mic, unless cancelled by another key press first


def audio_callback(indata, frames, time_info, status):
    if recording:
        audio_frames.append(indata.copy())


current_stream = None


def start_recording():
    global recording, audio_frames, current_stream
    with lock:
        if recording:
            return
        audio_frames = []
        recording = True
    # open the microphone only while actually recording, to save CPU/battery when idle
    current_stream = sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=audio_callback
    )
    current_stream.start()
    print("recording...")


def cancel_recording():
    """Stop the microphone and discard whatever was captured, without transcribing.
    Used when Option was combined with another key (e.g. Option+Left), meaning it
    was being used for its normal macOS role and not as our push-to-talk hotkey."""
    global recording, current_stream
    with lock:
        if not recording:
            return
        recording = False
    if current_stream is not None:
        current_stream.stop()
        current_stream.close()
        current_stream = None
    print("(cancelled - Option was used with another key)")


def stop_recording_and_transcribe():
    global recording, current_stream
    with lock:
        if not recording:
            return
        recording = False
    if current_stream is not None:
        current_stream.stop()
        current_stream.close()
        current_stream = None
    print("transcribing...")

    if not audio_frames:
        print("(no audio captured)")
        return

    audio = np.concatenate(audio_frames, axis=0)
    duration_sec = len(audio) / SAMPLE_RATE
    if duration_sec < 0.3:
        print("(recording too short, ignored)")
        return

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio, SAMPLE_RATE)
        path = f.name

    try:
        result = mlx_whisper.transcribe(
            path, path_or_hf_repo=MODEL, language=LANGUAGE
        )
        text = (result.get("text") or "").strip()
    except Exception as e:
        print(f"transcription error: {e}")
        return

    if not text:
        print("(empty transcription)")
        return

    print(f"text: {text}")
    inject_text(text)


def inject_text(text):
    global suppress_hotkey
    suppress_hotkey = True
    try:
        kb_controller.type(text)
    except Exception as e:
        print(f"auto-type failed ({e}), copying to clipboard instead")
        copy_to_clipboard(text)
    finally:
        suppress_hotkey = False


def copy_to_clipboard(text):
    try:
        subprocess.run("pbcopy", universal_newlines=True, input=text, check=True)
        print("(copied to clipboard - paste with Cmd+V)")
    except Exception as e:
        print(f"clipboard copy also failed: {e}")


def _debounced_start():
    global start_timer
    with lock:
        if not option_held or other_key_pressed:
            return
        start_timer = None
    start_recording()


def on_press(key):
    global other_key_pressed, option_held, start_timer
    if suppress_hotkey:
        return
    if key in HOTKEY_KEYS:
        if option_held:
            return  # key repeat while already held - ignore
        option_held = True
        other_key_pressed = False
        start_timer = threading.Timer(HOTKEY_DEBOUNCE_SEC, _debounced_start)
        start_timer.start()
    elif option_held:
        # some other key was pressed while Option is held down - this is Option being used
        # for its normal macOS role (word-jump, special character, etc), not our hotkey
        other_key_pressed = True
        if start_timer is not None:
            start_timer.cancel()
            start_timer = None


def on_release(key):
    global other_key_pressed, option_held, start_timer
    if suppress_hotkey:
        return
    if key in HOTKEY_KEYS:
        option_held = False
        if start_timer is not None:
            start_timer.cancel()
            start_timer = None
        if other_key_pressed:
            other_key_pressed = False
            cancel_recording()  # no-op if the mic was never actually opened
        else:
            stop_recording_and_transcribe()


def main():
    print("=" * 50)
    print("Local dictation tool starting")
    print(f"Hotkey: Right Option (hold to record, release to transcribe)")
    print("First run downloads the model (~1.6GB) - this can take a few minutes.")
    print("Ctrl+C to quit.")
    print("=" * 50)

    try:
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
