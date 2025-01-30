#!/usr/bin/env python3

import requests
import re

# 1) Define the plugins you want to check, with enough info to build API URLs.
#    Adjust to match your actual IDs or slugs on each platform.
PLUGINS = [
    {
        "name": "LuckPerms",
        "platform": "spigot",
        "id": "28140",  # Resource ID on Spigot
    },
    {
        "name": "Chunky",
        "platform": "modrinth",
        "id": "fALzjamp",
    },
    {
        "name": "WorldGuard",
        "platform": "bukkit",
        "id": "31054",  # Or CurseForge project ID
    }
    #{
    #    "name": "ExamplePolymartPlugin",
    #    "platform": "polymart",
    #    "id": "5678",
    #}
]

def fetch_spigot_version(plugin_id):
    """
    Example: For Spigot, we can use the Spiget API:
      GET https://api.spiget.org/v2/resources/<id>/versions?size=1&sort=-releaseDate
    """
    url = f"https://api.spiget.org/v2/resources/{plugin_id}/versions?size=1&sort=-releaseDate"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0].get("name", "Unknown")
    except Exception as e:
        print(f"[Error] Failed to fetch Spigot version: {e}")
    return "Unknown"


def fetch_modrinth_version(plugin_id):
    """
    Example: For Modrinth, you can query the project versions:
      GET https://api.modrinth.com/v2/project/<id>/version
    The returned JSON is a list of versions, usually sorted by release date (descending).
    """
    url = f"https://api.modrinth.com/v2/project/{plugin_id}/version"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            # The first item should be the latest version if the list is sorted
            return data[0].get("version_number", "Unknown")
    except Exception as e:
        print(f"[Error] Failed to fetch Modrinth version: {e}")
    return "Unknown"


def fetch_bukkit_version(plugin_id):
    """
    Bukkit/CurseForge typically needs an API key to be set in headers.
    For example, CurseForge API docs:
      https://docs.curseforge.com/#get-the-latest-file
    This snippet uses a placeholder example.
    """
    # Replace with your real API key and endpoints
    api_key = "YOUR_CURSEFORGE_API_KEY"  # or read from environment variable
    url = f"https://api.curseforge.com/v1/mods/{plugin_id}/files?pageSize=1"
    headers = {"x-api-key": api_key}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Adjust parsing based on the actual structure returned
        if "data" in data and data["data"]:
            latest_file = data["data"][0]
            return latest_file.get("displayName", "Unknown")
    except Exception as e:
        print(f"[Error] Failed to fetch Bukkit/CurseForge version: {e}")
    return "Unknown"


def fetch_polymart_version(plugin_id):
    """
    Polymart has an API:
      https://polymart.org/resources/api-documentation
    Example of a resource info endpoint:
      POST https://api.polymart.org/v1/getResourceInfo?resource_id=XXX
    Typically done via POST with JSON.
    """
    url = "https://api.polymart.org/v1/getResourceInfo"
    payload = {"resource_id": plugin_id}
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Parse the version from the JSON structure
        # For example: data["response"]["versions"] ...
        if "response" in data and "versions" in data["response"]:
            versions = data["response"]["versions"]
            # Sort by release date or pick the highest version name, etc.
            # This is left as an exercise for your actual resource
            latest = versions[0]  # Just an example
            return latest.get("version", "Unknown")
    except Exception as e:
        print(f"[Error] Failed to fetch Polymart version: {e}")
    return "Unknown"


def main():
    """
    1. Read current README
    2. Build a new section that lists each plugin and its version
    3. Rewrite the README (updating or creating a placeholder section)
    """
    # Read your existing README.md
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    plugin_lines = []
    for plugin in PLUGINS:
        name = plugin["name"]
        platform = plugin["platform"]
        pid = plugin["id"]

        if platform == "spigot":
            version = fetch_spigot_version(pid)
        elif platform == "modrinth":
            version = fetch_modrinth_version(pid)
        elif platform == "bukkit":
            version = fetch_bukkit_version(pid)
        elif platform == "polymart":
            version = fetch_polymart_version(pid)
        else:
            version = "Unknown"

        plugin_lines.append(f"- **{name}** [{platform}]: {version}")

    # Construct a block of text showing plugin versions
    new_section = "## Latest Plugin Versions\n\n" + "\n".join(plugin_lines) + "\n"

    # We'll look for an existing "## Latest Plugin Versions" section and replace it.
    # If it doesn't exist, we append it at the end of the file.
    pattern = r"(## Latest Plugin Versions[\s\S]*?)(?=\n##|$)"
    if re.search(pattern, readme):
        # Update existing section
        readme = re.sub(pattern, new_section, readme, count=1)
    else:
        # Append
        readme += "\n" + new_section

    # Write changes back to README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)


if __name__ == "__main__":
    main()
