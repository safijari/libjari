from libjari.jpath import JPath

def test_prefix_suffix():
    path = JPath("/tmp/hey.h5")
    out = path.append_name("_1").str
    print(out)
    assert out == "/tmp/hey_1.h5"