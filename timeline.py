import sys
import os

# ✅ Add Resolve scripting module path
resolve_script_path = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
if resolve_script_path not in sys.path:
    sys.path.append(resolve_script_path)

try:
    import DaVinciResolveScript
except ImportError:
    print("❌ Could not import DaVinciResolveScript. Check the path above.")
    sys.exit()

# ✅ Connect to DaVinci Resolve
resolve = DaVinciResolveScript.scriptapp("Resolve")
if not resolve:
    print("❌ Could not connect to DaVinci Resolve. Make sure Resolve is open.")
    sys.exit()

# ✅ Access Project Manager and Current Project
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()

if not project:
    print("❌ No active project found.")
    sys.exit()

# ✅ Access the Media Pool
media_pool = project.GetMediaPool()
if not media_pool:
    print("❌ Could not access Media Pool.")
    sys.exit()

# ✅ Create a new timeline
timeline_name = f"New_Timeline_{project.GetName()}_{os.getpid()}"
print(f"🕓 Creating new timeline: {timeline_name}")

# 👉 Correct API call — CreateEmptyTimeline is part of MediaPool, not Project
new_timeline = media_pool.CreateEmptyTimeline(timeline_name)

if new_timeline:
    print(f"✅ Successfully created new timeline: {timeline_name}")
    # Optional: Set this timeline as current
    project.SetCurrentTimeline(new_timeline)
    print(f"🎬 Switched to new timeline: {timeline_name}")
else:
    print("❌ Failed to create new timeline.")
