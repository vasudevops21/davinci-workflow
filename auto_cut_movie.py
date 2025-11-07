"""
Auto-Cut and Delete 1-Second Portions (In-Place)
------------------------------------------------
This script automatically cuts the current timeline every 10 seconds,
deletes the next 1-second portions (no ripple delete, leaves gaps),
and keeps the same timeline length.

✅ Works with DaVinci Resolve Studio 18+
✅ Same format as your old working script
"""

import sys
import os
import time

# Add DaVinci Resolve Script Module Path (adjust if needed)
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

def auto_cut_delete_in_place():
    """Automatically cuts and deletes 1-second portions in-place every 10 seconds."""
    try:
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
    except ImportError as e:
        print(f"❌ Error importing DaVinciResolveScript: {e}")
        print("Make sure:")
        print("1. DaVinci Resolve Studio is installed (not Free version).")
        print("2. Scripting is enabled in Resolve.")
        print("3. The 'Modules' path above is correct.")
        return False

    if not resolve:
        print("❌ Could not connect to DaVinci Resolve. Make sure it’s running.")
        return False

    # Get project and timeline
    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()
    timeline = project.GetCurrentTimeline()

    if not project or not timeline:
        print("❌ No active project or timeline found.")
        return False

    print(f"🎬 Working on timeline: {timeline.GetName()}")

    # Get settings
    settings = timeline.GetSetting()
    frame_rate = float(settings.get('timelineFrameRate', 24))
    segment_seconds = 10
    remove_seconds = 1
    segment_frames = int(segment_seconds * frame_rate)
    remove_frames = int(remove_seconds * frame_rate)

    # Get clips from video track 1
    video_items = timeline.GetItemsInTrack("video", 1)
    if not video_items:
        print("❌ No clips found on video track 1.")
        return False

    print(f"Found {len(video_items)} clip(s) to process.\n")

    total_deleted = 0

    for index, item in enumerate(video_items.values(), start=1):
        clip_name = item.GetName()
        clip_start = item.GetStart()
        clip_end = item.GetEnd()
        clip_duration = int(clip_end - clip_start)

        print(f"✂ Processing Clip {index}: {clip_name} ({clip_duration} frames)")

        current_frame = clip_start
        while (current_frame + segment_frames + remove_frames) <= clip_end:
            delete_start = current_frame + segment_frames
            delete_end = delete_start + remove_frames

            # Convert to timecode
            delete_start_tc = timeline.GetTimecodeFromFrame(delete_start)
            delete_end_tc = timeline.GetTimecodeFromFrame(delete_end)

            # Make two cuts
            timeline.CutAtTimecode(delete_start_tc)
            timeline.CutAtTimecode(delete_end_tc)
            time.sleep(0.1)

            # After cutting, find the middle 1s clip and delete it
            new_items = timeline.GetItemsInTrack("video", 1)
            for clip in new_items.values():
                c_start = clip.GetStart()
                c_end = clip.GetEnd()
                if abs(c_start - delete_start) < (frame_rate / 2):
                    print(f"🗑 Deleting 1s section at {delete_start/frame_rate:.2f}s – {delete_end/frame_rate:.2f}s")
                    clip.Delete(ripple=False)  # ❗ No ripple delete (keeps gap)
                    total_deleted += 1
                    break

            current_frame += segment_frames + remove_frames

    print("\n" + "=" * 60)
    print(f"✅ Auto-Cut Complete! Deleted {total_deleted} sections.")
    print("🕐 Kept 10s segments, deleted 1s between (gaps left in place).")
    print("=============================================================")
    return True


# Entry point
if __name__ == "__main__":
    print("=" * 60)
    print("🎬 DaVinci Resolve Auto-Cut Script (Delete 1-Second In-Place)")
    print("=" * 60)
    print("Make sure Resolve Studio is open with a project and timeline loaded.\n")

    success = auto_cut_delete_in_place()

    if success:
        print("\n✅ Done! Check your current timeline inside DaVinci Resolve.")
    else:
        print("\n❌ Script failed. Please review the messages above.")