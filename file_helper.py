def is_file_size_ok(file_size: int, limit_in_mb=5) -> bool:
    if not file_size:
        return False

    return bytesto(file_size, to='m') <= limit_in_mb


def bytesto(bytes, to, bsize=1024):
    """convert bytes to megabytes, etc.
       sample code:
           print('mb= ' + str(bytesto(314575262000000, 'm')))
       sample output:
           mb= 300002347.946
    """

    a = {'k': 1, 'm': 2, 'g': 3, 't': 4, 'p': 5, 'e': 6}
    r = float(bytes)
    for i in range(a[to]):
        r = r / bsize

    return (r)
