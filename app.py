import asyncio
from js import document, console, window

# Global app state variables
is_playing = False
total_seconds = 0

# Define the breathing phases
steps = ["Inhale", "Hold", "Exhale", "Wait"]

async def start_breathing(ev):
    global is_playing, total_seconds
    if not is_playing:
        return  # safeguard in case this is called unexpectedly
    total_seconds = 0
    # Retrieve optional time limit input (in minutes)
    time_limit_input = document.getElementById("timeLimit").value
    try:
        time_limit_minutes = int(time_limit_input) if time_limit_input != "" else 0
    except Exception:
        time_limit_minutes = 0
    time_limit_seconds = time_limit_minutes * 60
    step_index = 0

    while is_playing:
        # Update the phase instruction
        instruction = steps[step_index]
        document.getElementById("instruction").innerHTML = instruction
        console.log(f"Step: {instruction}")
        countdown = 4  # each phase lasts 4 seconds
        while countdown > 0 and is_playing:
            document.getElementById("countdown").innerHTML = str(countdown)
            await asyncio.sleep(1)
            countdown -= 1
            total_seconds += 1
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            document.getElementById("timeDisplay").innerHTML = f"{minutes:02d}:{seconds:02d}"
        # Play tone if sound is enabled
        sound_toggle = document.getElementById("soundToggle")
        if sound_toggle.checked:
            play_tone()
        # Move to the next phase
        step_index = (step_index + 1) % len(steps)
        # Check optional time limit and stop if reached
        if time_limit_seconds and total_seconds >= time_limit_seconds:
            is_playing = False
            document.getElementById("instruction").innerHTML = "Complete!"
            document.getElementById("startButton").innerHTML = "Start"
            break

async def stop_breathing(ev):
    global is_playing
    is_playing = False
    document.getElementById("instruction").innerHTML = "Paused"

def play_tone():
    # Use the Web Audio API to play a short tone.
    audio_context = None
    if hasattr(window, "AudioContext"):
        audio_context = window.AudioContext.new()
    elif hasattr(window, "webkitAudioContext"):
        audio_context = window.webkitAudioContext.new()
    if audio_context:
        oscillator = audio_context.createOscillator()
        oscillator.type = "sine"
        oscillator.frequency.value = 440  # A4 frequency
        oscillator.connect(audio_context.destination)
        oscillator.start()
        # Stop oscillator after 0.1 seconds
        def stop_osc():
            oscillator.stop()
        window.setTimeout(stop_osc, 100)

def reset_app(ev):
    global is_playing, total_seconds
    is_playing = False
    total_seconds = 0
    document.getElementById("instruction").innerHTML = "Press start to begin"
    document.getElementById("countdown").innerHTML = "4"
    document.getElementById("timeDisplay").innerHTML = "00:00"
    document.getElementById("startButton").innerHTML = "Start"

def toggle_play(ev):
    global is_playing
    if not is_playing:
        is_playing = True  # Set state immediately to avoid duplicate triggers
        document.getElementById("startButton").innerHTML = "Pause"
        asyncio.ensure_future(start_breathing(ev))
    else:
        document.getElementById("startButton").innerHTML = "Start"
        asyncio.ensure_future(stop_breathing(ev))

# Bind button events using our dedicated toggle functions.
document.getElementById("startButton").addEventListener("click", toggle_play)
document.getElementById("resetButton").addEventListener("click", reset_app)
