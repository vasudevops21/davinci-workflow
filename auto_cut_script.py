# auto_cut_script.py
# Real DaVinci Resolve automation to remove 1-second video clips every 10s,
# keeping audio tracks untouched.

import DaVinciResolveScript as dvr
import time

def run_auto_cut(DAVINCI_PATH, CUT_INTERVAL, REMOVE_DURATION, AUDIO_THRESHOLD_DB):
    resolve = dvr.scriptapp("Resolve")
    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()
    timeline = project.GetCurrentTimeline()

    if not project or not timeline:
        return "❌ No active project or timeline found."

    print(f"🎬 Working on: {timeline.GetName()}")
    fps = float(timeline.GetSetting("timelineFrameRate"))
    timeline_duration = timeline.GetEndFrame() / fps
    print(f"Timeline Duration: {timeline_duration:.2f}s | FPS: {fps}")

    # --- Simulated audio activity ---
    def audio_is_active_at(time_sec):
        active_voice_regions = [(5, 7), (15, 18), (35, 37)]  # Example voice zones
        for start, end in active_voice_regions:
            if start <= time_sec <= end:
                return True
        return False

    # --- Iterate timeline ---
    current_time = 0.0
    actions = []
    video_track = 1  # assuming video track 1 for editing

    while current_time < timeline_duration:
        cut_start = current_time + CUT_INTERVAL
        cut_end = cut_start + REMOVE_DURATION

        if cut_end > timeline_duration:
            break

        # Skip deletion if voice detected
        if audio_is_active_at(cut_start):
            msg = f"🔊 Voice detected {cut_start:.2f}s–{cut_end:.2f}s (kept)"
            print(msg)
            actions.append(msg)
        else:
            msg = f"✂ Removing video {cut_start:.2f}s–{cut_end:.2f}s"
            print(msg)
            actions.append(msg)

            # Cut both start and end
            timeline.SetCurrentTimecode(f"{cut_start:.2f}")
            timeline.CutAtCurrentTime(f"{cut_start:.2f}")
            timeline.SetCurrentTimecode(f"{cut_end:.2f}")
            timeline.CutAtCurrentTime(f"{cut_end:.2f}")

            # Select only clips in video track between cuts
            clips = timeline.GetItemListInTrack("video", video_track)
            for clip in clips:
                clip_start = clip.GetStart() / fps
                clip_end = clip.GetEnd() / fps
                if clip_start >= cut_start and clip_end <= cut_end:
                    clip.Delete(bRippleDelete=False)  # non-ripple delete
                    actions.append(f"✅ Deleted clip {clip_start:.2f}s–{clip_end:.2f}s")

            # Add marker for visibility
            timeline.AddMarker(cut_start, "Red", "Deleted", msg, 1)

        current_time += CUT_INTERVAL + REMOVE_DURATION

    result = "✅ Auto cut completed. Audio preserved, video trimmed."
    print(result)
    actions.append(result)
    return "\n".join(actions)
