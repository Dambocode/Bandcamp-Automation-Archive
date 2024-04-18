


def findAlbum(keyword, albums):
    for album in albums:
        if keyword in album:
            return album
    return None