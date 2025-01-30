#!/usr/bin/env python3

import requests
import re

PLUGINS = [
    {
        "name": "LuckPerms",
        "platform": "spigot",
        "id": "28140",  # Resource ID on Spigot
        "fallback_version": "Unknown",
        "fallback_game": "UnknownMC"
    },
    {
        "name": "Chunky",
        "platform": "modrinth",
        "id": "fALzjamp",  # Project ID/slug on Modrinth
        "fallback_version": "Unknown",
        "fallback_game": "UnknownMC"
    }
]

def fetch_spigot_version_and_game(plugin_id):
    """
    Uses the Spiget API for Spigot plugins:
      - GET /resources/<id>/versions?size=1&sort=-releaseDate -> latest plugin version name
      - GET /resources/<id> -> 'testedVersions' array (if available) for Minecraft versions
    """
    # 1. Get the latest plugin version name
    versions_url = f"https://api.spiget.org/v2/resources/{plugin_id}/versions"
    plugin_version = "Unknown"
    try:
        resp = requests.get(versions_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            plugin_version = data[-1].get("name", "Unknown")
    except Exception as e:
        print(f"[Error] Failed to fetch Spigot plugin version for {plugin_id}: {e}")

    # 2. Get tested Minecraft versions (if provided by the resource)
    resource_url = f"https://api.spiget.org/v2/resources/{plugin_id}"
    game_version = "UnknownMC"
    try:
        resp = requests.get(resource_url, timeout=10)
        resp.raise_for_status()
        resource_data = resp.json()
        tested = resource_data.get("testedVersions", [])
        if tested:
            game_version = ", ".join(tested)
    except Exception as e:
        print(f"[Error] Failed to fetch Spigot game version for {plugin_id}: {e}")

    return plugin_version, game_version


def fetch_modrinth_version_and_game(plugin_id):
    """
    Modrinth API:
      - GET /project/<id>/version returns an array of version objects
      - Each version object may have "version_number" and "game_versions" array.
      - The first entry in the response is typically the latest version.
    """
    url = f"https://api.modrinth.com/v2/project/{plugin_id}/version"
    plugin_version = "Unknown"
    game_version = "UnknownMC"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            latest = data[0]  # the first entry is presumably the latest
            plugin_version = latest.get("version_number", "Unknown")
            game_versions = latest.get("game_versions", [])
            if game_versions:
                game_version = ", ".join(game_versions)
    except Exception as e:
        print(f"[Error] Failed to fetch Modrinth version for {plugin_id}: {e}")

    return plugin_version, game_version


def main():
    """
    1. Reads current README.md
    2. Builds a new "Latest Plugin Versions" section listing both MC version(s) & plugin version.
    3. Writes it back to README.md (replacing or appending).
    """
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    plugin_lines = []
    for plugin in PLUGINS:
        name = plugin["name"]
        platform = plugin["platform"]
        pid = plugin["id"]

        if platform == "spigot":
            version, game_ver = fetch_spigot_version_and_game(pid)
        elif platform == "modrinth":
            version, game_ver = fetch_modrinth_version_and_game(pid)
        else:
            version, game_ver = ("Unknown", "UnknownMC")

        # If either is "Unknown", apply the fallback
        if version == "Unknown":
            version = plugin.get("fallback_version", "Unknown")
        if game_ver == "UnknownMC":
            game_ver = plugin.get("fallback_game", "UnknownMC")

        # e.g. => "- **LuckPerms** [spigot]: MC 1.19, Plugin v5.4.9"
        plugin_lines.append(f"- **{name}** [{platform}]: MC {game_ver}, Plugin v{version}")

    # Construct the new "Latest Plugin Versions" block
    new_section = "## Latest Plugin Versions\n\n" + "\n".join(plugin_lines) + "\n"

    # Try to replace an existing "## Latest Plugin Versions" section, or append
    pattern = r"(## Latest Plugin Versions[\s\S]*?)(?=\n##|$)"
    if re.search(pattern, readme):
        readme = re.sub(pattern, new_section, readme, count=1)
    else:
        readme += "\n" + new_section

    # Write the updated README
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
