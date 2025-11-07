"""
Auto-Cut and Keep Gaps Script for DaVinci Resolve Studio
--------------------------------------------------------
This script automatically cuts a timeline every N seconds,
creates M-second gaps between those cuts (keeps them as empty spaces),
and creates a new timeline with the separated clips stitched with gaps.

✅ Works with DaVinci Resolve Studio 18+
✅ Parameters configurable at the top
"""

import sys
import os

# ==============================================================
# 🔧 USER SETTINGS — Change these before running
# ==============================================================

SEGMENT_SECONDS = 10   # ⏱ Duration to KEEP per segment
GAP_SECONDS = 1        # ⏳ Duration of EMPTY GAP between segments

# ==============================================================

# Add DaVinci Resolve Scripting Path (adjust if needed)
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

def auto_cut_and_keep_gaps(segment_seconds=SEGMENT_SECONDS, gap_seconds=GAP_SECONDS):
    """Automatically cuts and keeps gaps between segments."""

    # Try to connect to DaVinci Resolve
    try:
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
    except ImportError as e:
        print(f"❌ Error importing DaVinciResolveScript: {e}")
        print("Make sure:")
        print("1. DaVinci Resolve Studio is installed.")
        print("2. Scripting is enabled in Resolve.")
        print("3. The path above points to the 'Modules' folder.")
        return False

    if not resolve:
        print("❌ Could not connect to DaVinci Resolve. Make sure it’s running.")
        return False

    # Get current project and timeline
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
    segment_frames = int(segment_seconds * frame_rate)
    gap_frames = int(gap_seconds * frame_rate)

    # Get clips from video track 1
    video_items = timeline.GetItemListInTrack("video", 1)
    if not video_items:
        print("❌ No clips found on video track 1.")
        return False

    print(f"Found {len(video_items)} clip(s) to process.")
    print(f"🕐 Keeping {segment_seconds}s per segment, leaving {gap_seconds}s gaps.\n")

    media_pool = project.GetMediaPool()

    # Prepare new timeline
    new_timeline_name = f"{timeline.GetName()}_AutoCutWithGaps"
    new_timeline = media_pool.CreateEmptyTimeline(new_timeline_name)

    if not new_timeline:
        print("❌ Could not create new timeline.")
        return False

    project.SetCurrentTimeline(new_timeline)
    print(f"✅ Created new timeline: {new_timeline_name}")

    # Process each clip
    current_timeline_frame = 0
    total_segments = 0

    for item in video_items:
        media_item = item.GetMediaPoolItem()
        clip_name = item.GetName()
        clip_duration = item.GetDuration()

        print(f"\n✂ Cutting clip: {clip_name} ({clip_duration} frames)")

        cycle = segment_frames + gap_frames
        position = 0

        while position < clip_duration:
            segment_start = position
            segment_end = min(position + segment_frames, clip_duration)

            # Add segment
            if segment_start < clip_duration:
                added = media_pool.AppendToTimeline([{
                    'mediaPoolItem': media_item,
                    'startFrame': segment_start,
                    'endFrame': segment_end,
                    'mediaType': 1,
                    'trackIndex': 1,
                    'recordFrame': current_timeline_frame
                }])

                if added:
                    added_duration = segment_end - segment_start
                    current_timeline_frame += added_duration
                    total_segments += 1
                    print(f"  ✅ Added {segment_seconds}s segment ({segment_start}-{segment_end})")

            # Move ahead by one cycle (adds gap)
            position += cycle
            current_timeline_frame += gap_frames  # leaves empty space (gap)

        print(f"  → Finished cutting {clip_name}")

    print("\n" + "=" * 60)
    print(f"🎞️  Auto-Cut Completed (with {gap_seconds}s gaps)!")
    print(f"📄  New timeline: {new_timeline_name}")
    print(f"📸  Total segments added: {total_segments}")
    print(f"🕐  Each segment: {segment_seconds}s (kept {gap_seconds}s gaps between each)")
    print("=" * 60)
    return True


# Entry point
if __name__ == "__main__":
    print("=" * 60)
    print("🎬 DaVinci Resolve Auto-Cut Script (Keep Gaps)")
    print("=" * 60)
    print(f"⏱ Using Settings → Keep: {SEGMENT_SECONDS}s | Gap: {GAP_SECONDS}s")
    print("Make sure Resolve Studio is open with a project and timeline loaded.\n")

    success = auto_cut_and_keep_gaps()

    if success:
        print("\n✅ Done! Check your new timeline inside DaVinci Resolve.")
    else:
        print("\n❌ Script failed. Please review the messages above.")
