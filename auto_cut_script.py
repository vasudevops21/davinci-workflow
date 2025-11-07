# auto_cut_script.py
# Removes 1-second video clips every 10 seconds unless audio exceeds threshold.
# Keeps timeline duration constant (no ripple delete).

import DaVinciResolveScript as dvr
import time

def run_auto_cut(DAVINCI_PATH, CUT_INTERVAL, REMOVE_DURATION, AUDIO_THRESHOLD_DB):
    # --- Connect to Resolve ---
    resolve = dvr.scriptapp("Resolve")
    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()
    timeline = project.GetCurrentTimeline()

    if not project or not timeline:
        return "❌ No active project or timeline found in DaVinci Resolve."

    print(f"🎬 Working on timeline: {timeline.GetName()}")
    fps = float(timeline.GetSetting("timelineFrameRate"))
    timeline_duration = timeline.GetEndFrame() / fps
    print(f"Timeline Duration: {timeline_duration:.2f}s | FPS: {fps}")

    # --- Simulated voice regions (for testing; replace with real dB-based logic) ---
    def audio_is_active_at(time_sec):
        active_voice_regions = [(5, 7), (15, 18), (35, 37)]  # Example
        for start, end in active_voice_regions:
            if start <= time_sec <= end:
                return True
        return False

    # --- Main processing loop ---
    current_time = 0.0
    actions = []

    while current_time < timeline_duration:
        cut_start = current_time + CUT_INTERVAL
        cut_end = cut_start + REMOVE_DURATION

        if cut_end > timeline_duration:
            break

        if audio_is_active_at(cut_start):
            msg = f"🔊 Voice detected from {cut_start:.2f}s – skipping deletion"
            print(msg)
            actions.append(msg)
        else:
            msg = f"✂ Removing video segment {cut_start:.2f}s–{cut_end:.2f}s"
            print(msg)
            actions.append(msg)

            timeline.SetCurrentTimecode(f"{cut_start:.2f}")
            timeline.AddMarker(cut_start, "Red", "RemoveStart", "Start removing", 1)
            timeline.AddMarker(cut_end, "Red", "RemoveEnd", "End removing", 1)

            # Perform the cut (no ripple delete)
            timeline.CutAtCurrentTime(f"{cut_start:.2f}")
            timeline.CutAtCurrentTime(f"{cut_end:.2f}")
            timeline.DeleteClips(bRippleDelete=False, videoTracks=[1])

        current_time += CUT_INTERVAL + REMOVE_DURATION

    result = "✅ Auto video cut completed successfully (audio preserved)."
    print(result)
    actions.append(result)
    return "\n".join(actions)
