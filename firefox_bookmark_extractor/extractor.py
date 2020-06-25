#!/usr/bin/env python3
#
# Usage: .py
#

import sqlite3
import argparse


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


def get_urls(conn, bookmark_directory_id, recursive):
    if recursive is None:
        recursive = False

    cursor = conn.execute(
        f"SELECT bm.id, bm.type, url FROM moz_bookmarks as bm\
                            LEFT JOIN moz_places as p ON bm.fk = p.id\
                            WHERE parent = {bookmark_directory_id}"
    )

    urls = []

    for row in cursor.fetchall():
        bookmark_id = row[0]
        bookmark_type = row[1]
        bookmark_url = row[2]

        # Parse directories (type 2) recursively if needed
        if bookmark_type == 2 and recursive:
            urls.extend(get_urls(conn, bookmark_id, recursive))
            continue

        urls.append(bookmark_url)

    return urls


def get_args():
    parser = argparse.ArgumentParser(
        description="Tool for extracting bookmarks from Firefox"
    )
    parser.add_argument(
        "firefox_profile_path", type=str, help="Path to Firefox profile directory"
    )
    parser.add_argument(
        "bookmark_path",
        type=str,
        help="Path to directory inside Firefox bookmark hierarchy",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Bookmark directory is extracted recursively",
    )

    return parser.parse_args()


def main():
    args = get_args()

    database_path = f"{args.firefox_profile_path}/places.sqlite"
    conn = sqlite3.connect(database_path)

    bookmark_path_parts = args.bookmark_path.split("/")
    potential_paths = get_potential_bookmark_paths(conn, bookmark_path_parts)

    if len(potential_paths) > 1:
        print(
            "Bookmark path is not unique! Make sure there is not two paths named same way."
        )

    if len(potential_paths) == 0:
        print("No matching bookmark path found!")

    urls = get_urls(conn, potential_paths[0], args.recursive)
    for url in urls:
        print(url)


if __name__ == "__main__":
    main()
