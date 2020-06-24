#!/usr/bin/env python3
#
# Usage: .py
#

from sys import argv
from sys import exit
import sqlite3


class Settings:
    def __init__(self, firefox_profile_path, bookmark_path):
        self.database_path = '{firefox_profile}/places.sqlite'
        self.bookmark_path_parts = bookmark_path.split("/")


def get_settings():
    if len(argv) < 3:
        print("Arguments missing")
        exit(1)

    firefox_profile = argv[1]
    bookmark_path = argv[2]

    if len(firefox_profile) == 0 or len(bookmark_path) == 0:
        print("Argument missing")

    return Settings(firefox_profile, bookmark_path)


def get_potential_bookmark_paths(conn, bookmark_path_parts):
    # Get all matching bookmarks for last part of the bookmark path
    cursor = conn.execute(
        f"SELECT * FROM moz_bookmarks\
                            WHERE title = '{bookmark_path_parts[-1]}'"
    )
    matching_places = cursor.fetchall()

    potential_paths = []

    # Iterate thought all potential matches to find unique matches
    for match in matching_places:
        # Set second to last part of the bookmark path as starting point
        part_index = len(bookmark_path_parts) - 2
        parent_id = match[3]

        # Follow the bookmark path and try to find matches to required path until
        # root bookmark is reached or when path has been found
        while part_index >= 0:
            current_part = bookmark_path_parts[part_index]
            cursor = conn.execute(
                f"SELECT * FROM moz_bookmarks WHERE id = {parent_id}\
                                    AND title = '{current_part}'"
            )
            parent = cursor.fetchone()

            if parent is None:
                break

            parent_id = parent[3]

            if parent_id == 1:
                potential_paths.append(match[0])
                break

            part_index -= 1

    return potential_paths


def get_urls(conn, bookmark_directory_id):
    cursor = conn.execute(
        f"SELECT url FROM moz_bookmarks as bm\
                            LEFT JOIN moz_places as p ON bm.fk = p.id\
                            WHERE parent = {bookmark_directory_id} AND type = 1"
    )

    return [row[0] for row in cursor.fetchall()]


def main():
    settings = get_settings()

    conn = sqlite3.connect(settings.database_path)

    potential_paths = get_potential_bookmark_paths(conn, settings.bookmark_path_parts)

    if len(potential_paths) > 1:
        print(
            "Bookmark path is not unique! Make sure there is not two paths named same way."
        )

    if len(potential_paths) == 0:
        print("No matching bookmark path found!")

    urls = get_urls(conn, potential_paths[0])
    for url in urls:
        print(url)


if __name__ == "__main__":
    main()
