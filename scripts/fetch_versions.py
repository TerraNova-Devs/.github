#!/usr/bin/env python3

import requests
import re

###################################################
# Define servers and their plugins here
###################################################
SERVERS = [
    {
        "name": "Main",
        "plugins": [
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
                "id": "fALzjamp",  # Project ID on Modrinth
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            }
        ]
    },
    {
        "name": "Farmwelt",
        "plugins": [
            # Add more plugins if you wish
            {
                "name": "LuckPerms",
                "platform": "spigot",
                "id": "28140",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            }
            # etc.
        ]
    },
    {
        "name": "Vorbau",
        "plugins": [
            # Add more plugins if you wish
            {
                "name": "LuckPerms",
                "platform": "spigot",
                "id": "28140",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            }
            # etc.
        ]
    },
    {
        "name": "Proxy",
        "plugins": [
            # Add more plugins if you wish
            {
                "name": "LuckPerms",
                "platform": "spigot",
                "id": "28140",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            }
            # etc.
        ]
    }
]

###################################################
# Fetching helper functions
###################################################
def fetch_spigot_version_and_game(plugin_id):
    """
    Uses the Spiget API for Spigot plugins:
      - GET /resources/<id>/versions?size=1&sort=-releaseDate -> latest plugin version name
      - GET /resources/<id> -> 'testedVersions' array (if available) for Minecraft versions
    """
    plugin_version = "Unknown"
    game_version = "UnknownMC"

    # 1. Get the latest plugin version name
    versions_url = f"https://api.spiget.org/v2/resources/{plugin_id}/versions"
    try:
        resp = requests.get(versions_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            # Spiget returns an array of versions sorted by releaseDate ascending
            # We'll use the last element for the latest version
            plugin_version = data[-1].get("name", "Unknown")
    except Exception as e:
        print(f"[Error] Failed to fetch Spigot plugin version for {plugin_id}: {e}")

    # 2. Get tested Minecraft versions
    resource_url = f"https://api.spiget.org/v2/resources/{plugin_id}"
    try:
        resp = requests.get(resource_url, timeout=10)
        resp.raise_for_status()
        resource_data = resp.json()
        tested = resource_data.get("testedVersions", [])
        if tested:
            game_version = ", ".join(tested)
    except Exception as e:
        print(f"[Error] Failed to fetch Spigot game version for {plugin_id}: {e}")
    
    print(f"[Spigot] Found version={plugin_version}, game={game_version}")
    return plugin_version, game_version


def fetch_modrinth_version_and_game(plugin_id):
    """
    Modrinth API:
      - GET /project/<id>/version returns an array of version objects
      - The first entry in the response is typically the latest version.
      - Each version object may have:
         * "version_number"
         * "game_versions" (array)
    """
    plugin_version = "Unknown"
    game_version = "UnknownMC"
    url = f"https://api.modrinth.com/v2/project/{plugin_id}/version"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            latest = data[0]
            plugin_version = latest.get("version_number", "Unknown")
            game_versions = latest.get("game_versions", [])
            if game_versions:
                game_version = ", ".join(game_versions)
    except Exception as e:
        print(f"[Error] Failed to fetch Modrinth version for {plugin_id}: {e}")

    print(f"[Modrinth] Found version={plugin_version}, game={game_version}")
    return plugin_version, game_version


###################################################
# Main script
###################################################
def main():
    # 1. Read current README
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    # 2. Build a new "Latest Plugin Versions" section with tables
    new_section_lines = ["## Latest Plugin Versions\n"]

    for server in SERVERS:
        server_name = server["name"]
        new_section_lines.append(f"### {server_name}\n")
        # Create table header
        new_section_lines.append("| Plugin     | Platform | MC Versions          | Plugin Version |\n")
        new_section_lines.append("|------------|---------|----------------------|----------------|\n")

        # Fetch plugin info & fill rows
        for plugin in server["plugins"]:
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

            # Add a row to the table
            new_section_lines.append(
                f"| **{name}** | {platform} | {game_ver} | {version} |\n"
            )

        # Add some spacing after each server table
        new_section_lines.append("\n")

    new_section = "".join(new_section_lines)

    # 3. Try to replace an existing "## Latest Plugin Versions" section, or append
    pattern = r"(## Latest Plugin Versions[\s\S]*?)(?=\n##|$)"
    if re.search(pattern, readme):
        # Replace existing block
        readme = re.sub(pattern, new_section, readme, count=1)
    else:
        # Append new block at the end
        readme += "\n" + new_section

    # 4. Write the updated README
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)


if __name__ == "__main__":
    main()
