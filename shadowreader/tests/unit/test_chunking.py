from libs import master


def test_generate_chunks():
    load = list(range(0, 1399))
    load_size = len(load)
    chunks, chunk_size = master._generate_chunked_load(load, chunk_max=100)
    print([len(ch) for ch in chunks])
    load_size_after_chunking = sum([len(ch) for ch in chunks])
    assert load_size_after_chunking == load_size
