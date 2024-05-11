
class Regression:

    def __init__(self, array):
        self.model = array[1]
        if len(array) > 1:
            self.groups_expected_val = array[0]
        elif len(array) > 2:
            self.R_squared = array[2]
        elif len(array) > 3:
            self.M_error = array[3]
        elif len(array) > 4:
            self.D_error = array[4]

    # TODO: Get Arguments
    #def set_model(file):
