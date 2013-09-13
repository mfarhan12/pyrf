# WSA Constants
MIN_FREQ = 45e6
MAX_FREQ = 8e9
MAX_BW = MAX_FREQ - MIN_FREQ
MIN_BW = 1e5
DEVICE_FULL_SPAN = 125e6
STARTUP_POINTS = 1024
LEVELED_TRIGGER_TYPE = 'LEVEL'
NONE_TRIGGER_TYPE = 'NONE'
MHZ = 1e6
INIT_CENTER_FREQ = 2450 * MHZ
INIT_BANDWIDTH = 100 * MHZ

RBW_VALUES = [488.28, 244.14, 122.07, 61.035, 30.495, 15.258,7.6294]
INIT_BIN_SIZE = DEVICE_FULL_SPAN / (RBW_VALUES[0] * 1e3)
# Plot Constants
PLOT_YMIN = -160
PLOT_YMAX = 20
LNEG_NUM = -5000

# Colors
NORMAL_COLOR = 'NONE'
ORANGE =  'rgb(255,84,0)'
ORANGE_NUM = (255,84,0)
TEAL = 'rgb(0,255,236)'
TEAL_NUM = (0,255,236)
WHITE = 'rgb(255,255,255)'
BLACK = 'rgb(0,0,0)'

PRESSED_BUTTON = 'groove'

# image size of button icons
ICON_SIZE = 20