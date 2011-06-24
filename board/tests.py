from board.tools import make_tripcode


def post_description_test():
    pass


def tripcode_test():
    assert make_tripcode("tripcode") == "3GqYIJ3Obs"
    assert make_tripcode("tripcod3") == "U6qBEwdIxU"
    assert make_tripcode("##") == make_tripcode("###")
