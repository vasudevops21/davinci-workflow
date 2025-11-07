"""
Smart Auto-Cut (Video Only, Keep Audio Intact)
-----------------------------------------------
Cuts the video track every N seconds and removes M-second portions —
but only if there is no voice activity in that audio range.

✅ Keeps audio track fully untouched
✅ Deletes only video track sections
✅ Detects voice activity using decibel threshold
✅ Works in-place (same timeline)
"""

import sys
import os
import time
from pydub import AudioSegment

# --- CONFIGURABLE PARAMETERS ---
# Adjust these values before running
DAVINCI_PATH = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
AUDIO_EXPORT_PATH = r"C:\Temp\resolve_audio.wav"
SEGMENT_SECONDS = 10
REMOVE_SECONDS = 1
VOICE_THRESHOLD_DB = -40.0   # -40dB = low, -30dB = more sensitive


# Add scripting path
sys.path.append(DAVINCI_PATH)


def analyze_audio_activity(audio_path, segment_seconds, remove_seconds, threshold_db):
    """Analyze exported audio and find time ranges (in seconds) with voice activity."""
    print("🔊 Analyzing audio waveform for voice detection...")
    audio = AudioSegment.from_wav(audio_path)

    voice_segments = []
    segment_len = (segment_seconds + remove_seconds) * 1000
    gap_len = remove_seconds * 1000
    position = 0

    while position + segment_len <= len(audio):
        gap_start = position + (segment_seconds * 1000)
        gap_end = gap_start + gap_len
        gap_audio = audio[gap_start:gap_end]

        db = gap_audio.dBFS if gap_audio.dBFS != float("-inf") else -90.0
        if db > threshold_db:
            voice_segments.append((gap_start / 1000, gap_end / 1000))
            print(f"🗣 Voice detected between {gap_start/1000:.2f}s–{gap_end/1000:.2f}s (avg {db:.1f} dB)")

        position += segment_len

    print(f"✅ Audio scan complete. Found {len(voice_segments)} voiced sections.")
    return voice_segments


def auto_cut_video_keep_audio():
    """Auto-cuts video and deletes 1s silent portions — keeps audio intact."""
    try:
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
    except ImportError as e:
        print(f"❌ Error importing DaVinciResolveScript: {e}")
        print("Please verify DaVinci scripting module path.")
        return False

    if not resolve:
        print("❌ Could not connect to DaVinci Resolve.")
        return False

    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    timeline = project.GetCurrentTimeline()

    if not project or not timeline:
        print("❌ No active project or timeline found.")
        return False

    print(f"🎬 Working on timeline: {timeline.GetName()}")

    # Get timeline settings
    settings = timeline.GetSetting()
    frame_rate = float(settings.get('timelineFrameRate', 24))
    segment_frames = int(SEGMENT_SECONDS * frame_rate)
    remove_frames = int(REMOVE_SECONDS * frame_rate)

    # Export full audio from timeline
    print("🎧 Exporting audio track for voice analysis...")
    timeline.ExportAudio(AUDIO_EXPORT_PATH, "WAV")
    print(f"✅ Exported audio to: {AUDIO_EXPORT_PATH}")

    # Analyze voice sections
    voice_segments = analyze_audio_activity(
        AUDIO_EXPORT_PATH,
        SEGMENT_SECONDS,
        REMOVE_SECONDS,
        VOICE_THRESHOLD_DB
    )

    # Work on video track only
    video_items = timeline.GetItemsInTrack("video", 1)
    if not video_items:
        print("❌ No clips found on video track 1.")
        return False

    print(f"Found {len(video_items)} video clip(s). Beginning cuts...\n")

    total_deleted = 0

    for index, item in enumerate(video_items.values(), start=1):
        clip_name = item.GetName()
        clip_start = item.GetStart()
        clip_end = item.GetEnd()
        clip_duration = int(clip_end - clip_start)
        print(f"🎞 Processing: {clip_name} ({clip_duration} frames)")

        current_frame = clip_start
        while (current_frame + segment_frames + remove_frames) <= clip_end:
            delete_start = current_frame + segment_frames
            delete_end = delete_start + remove_frames

            delete_start_sec = delete_start / frame_rate
            delete_end_sec = delete_end / frame_rate

            # Check if this gap contains voice
            has_voice = any(vs <= delete_start_sec <= ve for vs, ve in voice_segments)
            if has_voice:
                print(f"🔈 Skipped deletion {delete_start_sec:.2f}s–{delete_end_sec:.2f}s (voice detected)")
                current_frame += segment_frames + remove_frames
                continue

            # Make two cuts
            timeline.CutAtTimecode(timeline.GetTimecodeFromFrame(delete_start))
            timeline.CutAtTimecode(timeline.GetTimecodeFromFrame(delete_end))
            time.sleep(0.1)

            # Delete only the middle section (video only, no ripple)
            new_items = timeline.GetItemsInTrack("video", 1)
            for clip in new_items.values():
                if abs(clip.GetStart() - delete_start) < (frame_rate / 2):
                    clip.Delete(ripple=False)
                    total_deleted += 1
                    print(f"🗑 Deleted silent section {delete_start_sec:.2f}s–{delete_end_sec:.2f}s")
                    break

            current_frame += segment_frames + remove_frames

    print("\n" + "=" * 60)
    print(f"✅ Smart Auto-Cut Complete! Deleted {total_deleted} silent sections.")
    print("🎧 Audio track was preserved — only video trimmed.")
    print("=============================================================")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("🎬 Smart Auto-Cut Script (Video Only, Keep Audio Intact)")
    print("=" * 60)
    print("Make sure Resolve Studio is open with a loaded timeline.\n")

    success = auto_cut_video_keep_audio()

    if success:
        print("\n✅ Done! Check your current timeline inside DaVinci Resolve.")
    else:
        print("\n❌ Script failed. Please review messages above.")
