from approxeng.input import Controller, Button

MY_VENDOR_ID = 1118
MY_PRODUCT_ID = 


class MyNewController(Controller):
    """
    Driver for my new controller type
    """

    def __init__(self, dead_zone=0.05, hot_zone=0.0):
        """
        Axis and button definitions for my new controller class

        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` in the controller.
        """
        super(MyNewController, self).__init__(vendor_id=MY_VENDOR_ID,
                                              product_id=MY_PRODUCT_ID,
                                              controls=[],
                                              dead_zone=dead_zone,
                                              hot_zone=hot_zone)

    def __repr__(self):
        return 'My new controller'
