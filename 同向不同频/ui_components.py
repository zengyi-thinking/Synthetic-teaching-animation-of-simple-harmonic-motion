# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Slider, Button
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MultipleLocator

from config import (
    BACKGROUND_COLOR, GRID_COLOR, TEXT_COLOR, AXIS_COLOR, PANEL_COLOR,
    WAVE1_COLOR, WAVE2_COLOR, COMBINED_WAVE_COLOR, SPEED_COLOR,
    SLIDER_COLOR, SLIDER_HANDLE_COLOR, SLIDER_TRACK_COLOR, SLIDER_AX_COLOR,
    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, BUTTON_ACTIVE_COLOR,
    LEFT_MARGIN, SLIDER_WIDTH, BUTTON_WIDTH, BUTTON_HEIGHT,
    TITLE_FONT, LABEL_FONT, VALUE_FONT1, VALUE_FONT2, VALUE_FONT3, SPEED_FONT,
    INITIAL_PARAMS
) 