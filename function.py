""" Functions for PySweeper, currently only one. """

def request_size(min_size, max_size):
    """ Get the user disired length of the terrain side
    and return.
    """

    print("Welcome to PySweeper!")
    print(
        "Please pick a terrain size, between {} and {}".format(
            min_size, max_size
        )
    )

    is_answer_gotten = False

    while not is_answer_gotten:
        try:
            size = int(input(
                "How long do you want your terrain side to be? "
            ))
            if size < min_size:
                print("Error: input should be at least", min_size)
            elif size > max_size:
                print("Error: Max size is", max_size)
            else:
                is_answer_gotten = True
        except ValueError:
            print("Error: input should be a number!")
    return size
    