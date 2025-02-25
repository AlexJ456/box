import asyncio
from js import document, console, window

# Global state variables
is_playing = False
total_seconds = 0
steps = ["Inhale", "Hold", "Exhale", "Wait"]

async def breathing_cycle():
    global total_seconds, is_playing
    # Get optional time limit in seconds (if provided)
    time_limit_input = document.getElementById("timeLimit").value
    try:
        time_limit_sec = int(time_limit_input) * 60 if time_limit_input != "" else 0
    except Exception:
        time_limit_sec = 0

    step_index = 0

    while is_playing:
        # Set the current instruction (breathing phase)
        document.getElementById("instruction").textContent = steps[step_index]
        console.log(f"Phase: {steps[step_index]}")

        # Perform a 4-second countdown for the phase
        countdown = 4
        while countdown > 0 and is_playing:
            document.getElementById("countdown").textContent = str(countdown)
            await asyncio.sleep(1)
            total_seconds += 1
            # Update the total time display
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            document.getElementById("timeDisplay").textContent = f"{minutes:02d}:{seconds:02d}"
            countdown -= 1

        # Play a brief tone if sound is enabled
        if document.getElementById("soundToggle").checked:
            play_tone()

        # Check if a time limit was set and if it has been reached
        if time_limit_sec and total_seconds >= time_limit_sec:
            break

        # Rotate to the next breathing phase
        step_index = (step_index + 1) % len(steps)

    # End of session – update interface accordingly
    if time_limit_sec and total_seconds >= time_limit_sec:
        document.getElementById("instruction").textContent = "Complete!"
    else:
        document.getElementById("instruction").textContent = "Paused"
    document.getElementById("startButton").textContent = "Start"
    is_playing = False

def play_tone():
    # Use the Web Audio API to play a 100ms beep at A4 (440Hz)
    audio_context = None
    if hasattr(window, "AudioContext"):
        audio_context = window.AudioContext.new()
    elif hasattr(window, "webkitAudioContext"):
        audio_context = window.webkitAudioContext.new()
    if audio_context:
        oscillator = audio_context.createOscillator()
        oscillator.type = "sine"
        oscillator.frequency.value = 440  # 440Hz: A4
        oscillator.connect(audio_context.destination)
        oscillator.start()
        def stop_osc():
            oscillator.stop()
        window.setTimeout(stop_osc, 100)

def toggle_play(ev):
    global is_playing, total_seconds
    if not is_playing:
        # Start the session: reset time and update button label
        is_playing = True
        total_seconds = 0
        document.getElementById("startButton").textContent = "Pause"
        document.getElementById("instruction").textContent = "Starting..."
        asyncio.ensure_future(breathing_cycle())
    else:
        # Pause the session
        is_playing = False
        document.getElementById("startButton").textContent = "Start"
        document.getElementById("instruction").textContent = "Paused"

def reset_app(ev):
    global is_playing, total_seconds
    is_playing = False
    total_seconds = 0
    document.getElementById("instruction").textContent = "Press Start to Begin"
    document.getElementById("countdown").textContent = "4"
    document.getElementById("timeDisplay").textContent = "00:00"
    document.getElementById("startButton").textContent = "Start"

# Bind button events
document.getElementById("startButton").addEventListener("click", toggle_play)
document.getElementById("resetButton").addEventListener("click", reset_app)
