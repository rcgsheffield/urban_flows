import itertools


def iter_chunks(iterable: iter, size: int):
    """
    Iterate over fixed-size chunks of an iterable.

    https://alexwlchan.net/2018/12/iterating-in-fixed-size-chunks/

    :param iterable: a collection or generator
    :param size: the number of items in each chunk
    :returns: iter[tuple]
    """

    it = iter(iterable)

    while True:
        chunk = tuple(itertools.islice(it, size))

        yield chunk
