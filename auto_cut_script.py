"""
Auto-Cut and Keep Gaps Script for DaVinci Resolve Studio
--------------------------------------------------------
This script automatically cuts a timeline every X seconds,
creates Y-second gaps between those cuts,
and creates a new timeline with the separated clips stitched with gaps.
"""

import sys
import os

# Default DaVinci Resolve Scripting Path
DAVINCI_PATH = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
sys.path.append(DAVINCI_PATH)


def auto_cut_and_keep_gaps(segment_seconds=10, remove_seconds=1):
    """Automatically cuts and keeps gaps between segments."""

    try:
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
    except ImportError as e:
        print(f"❌ Error importing DaVinciResolveScript: {e}")
        return {"success": False, "message": str(e)}

    if not resolve:
        return {"success": False, "message": "Could not connect to DaVinci Resolve. Make sure it’s running."}

    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()
    timeline = project.GetCurrentTimeline()

    if not project or not timeline:
        return {"success": False, "message": "No active project or timeline found."}

    print(f"🎬 Working on timeline: {timeline.GetName()}")
    settings = timeline.GetSetting()
    frame_rate = float(settings.get('timelineFrameRate', 24))
    segment_frames = int(segment_seconds * frame_rate)
    remove_frames = int(remove_seconds * frame_rate)

    video_items = timeline.GetItemListInTrack("video", 1)
    if not video_items:
        return {"success": False, "message": "No clips found on video track 1."}

    media_pool = project.GetMediaPool()
    new_timeline_name = f"{timeline.GetName()}_AutoCutWithGaps"
    new_timeline = media_pool.CreateEmptyTimeline(new_timeline_name)

    if not new_timeline:
        return {"success": False, "message": "Could not create new timeline."}

    project.SetCurrentTimeline(new_timeline)

    current_timeline_frame = 0
    total_segments = 0

    for item in video_items:
        media_item = item.GetMediaPoolItem()
        clip_duration = item.GetDuration()
        position = 0
        cycle = segment_frames + remove_frames

        while position < clip_duration:
            segment_start = position
            segment_end = min(position + segment_frames, clip_duration)

            media_pool.AppendToTimeline([{
                'mediaPoolItem': media_item,
                'startFrame': segment_start,
                'endFrame': segment_end,
                'mediaType': 1,
                'trackIndex': 1,
                'recordFrame': current_timeline_frame
            }])

            added_duration = segment_end - segment_start
            current_timeline_frame += added_duration + remove_frames
            position += cycle
            total_segments += 1

    return {
        "success": True,
        "timeline": new_timeline_name,
        "segments": total_segments,
        "segment_seconds": segment_seconds,
        "gap_seconds": remove_seconds
    }


if __name__ == "__main__":
    result = auto_cut_and_keep_gaps()
    print(result)
