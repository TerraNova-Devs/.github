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
                "name": "BetonQuest",
                "platform": "spigot",
                "id": "2117",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "Citizens",
                "platform": "spigot",
                "id": "13811",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "CoreProtect",
                "platform": "modrinth",
                "id": "Lu3KuzdV",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "FastAsyncWorldEdit",
                "platform": "spigot",
                "id": "13932",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "GSit",
                "platform": "spigot",
                "id": "62325",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "IllegalStack",
                "platform": "spigot",
                "id": "44411",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "LuckPerms",
                "platform": "spigot",
                "id": "28140",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "Oraxen",
                "platform": "spigot",
                "id": "72448",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "Pl3xMap",
                "platform": "modrinth",
                "id": "34T8oVNY",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "PlaceholderAPI",
                "platform": "spigot",
                "id": "6245",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "ProtocolLib",
                "platform": "spigot",
                "id": "1997",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "RocketJoin",
                "platform": "spigot",
                "id": "82520",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "TAB-Bridge",
                "platform": "spigot",
                "id": "83966",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "Vault",
                "platform": "spigot",
                "id": "34315",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "Vulcan",
                "platform": "spigot",
                "id": "83626",
                "fallback_version": "Unknown",
                "fallback_game": "UnknownMC"
            },
            {
                "name": "WorldGuard",
                "platform": "modrinth",
                "id": "DKY9btbd",
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
                "name": "Chunky",
                "platform": "modrinth",
                "id": "fALzjamp",  # Project ID on Modrinth
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
    with open("profile/README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    # 2. Build our new "Latest Plugin Versions" section
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
                link = f"https://www.spigotmc.org/resources/{pid}/"
            elif platform == "modrinth":
                version, game_ver = fetch_modrinth_version_and_game(pid)
                link = f"https://modrinth.com/project/{pid}"
            else:
                version, game_ver = ("Unknown", "UnknownMC")
                link = "#"

            # If either is "Unknown", apply the fallback
            if version == "Unknown":
                version = plugin.get("fallback_version", "Unknown")
            if game_ver == "UnknownMC":
                game_ver = plugin.get("fallback_game", "UnknownMC")

            # Create hyperlink for plugin name
            plugin_name_column = f"[**{name}**]({link})"
            new_section_lines.append(
                f"| {plugin_name_column} | {platform} | {game_ver} | {version} |\n"
            )

        new_section_lines.append("\n")

    new_section = "".join(new_section_lines)

    # 3. Delete everything AFTER `## Latest Plugin Versions` if found
    heading = "## Latest Plugin Versions"
    idx = readme.find(heading)
    if idx != -1:
        # Slice everything before that heading
        readme = readme[:idx]

    # 4. Append the new section
    # (Ensure a newline if not present)
    if not readme.endswith("\n"):
        readme += "\n"
    readme += new_section

    # 5. Write the updated README
    with open("profile/README.md", "w", encoding="utf-8") as f:
        f.write(readme)


if __name__ == "__main__":
    main()