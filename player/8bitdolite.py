from approxeng.input import Controller, Button, BinaryAxis

__all__ = ['BitDoLite']

class BitDoLite(Controller):
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
        super(BitDoLite, self).__init__(
				controls=[
					Button("B", 304, sname='cross'),
					Button("A", 305, sname='circle'),
					Button("Y", 306, sname='square'),
					Button("X", 307, sname='triangle'),
					Button("L1", 308, sname='l1'),
					Button("R1", 309, sname='r1'),
					Button("Select", 310, sname='select'),
					Button("Start", 311, sname='start'),
					Button("L2", 2, sname='r1'),
					Button("R2", 5, sname='r2')
					BinaryAxis("D-Pad Vertical", 0, b1name='dup', b2name='ddown'),
					BinaryAxis("D-Pad Vertical", 1, b1name='dleft', b2name='dright')
				],
                dead_zone=dead_zone,
                hot_zone=hot_zone)
	
	@staticmethod
    def registration_ids():
        """
        :return: list of (vendor_id, product_id) for this controller
		MY_VENDOR_ID = 1118
		MY_PRODUCT_ID = 736
        """
		return[(1118, 736)]
	
    def __repr__(self):
        return 'BitDoLite'
