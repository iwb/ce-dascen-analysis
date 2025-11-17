"""
Visualization Constants

All styling and configuration constants for visualizations.
This file contains NO logic - only constant definitions.
"""

from pathlib import Path

# ====================
# DIRECTORY PATHS
# ====================
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
CONFIG_DIR = DATA_DIR / 'config'
ATTRIBUTES_DIR = DATA_DIR / 'attributes'
OUTPUT_DIR = BASE_DIR / 'output'
VIZ_OUTPUT_DIR = OUTPUT_DIR / 'visualizations'

# ====================
# CONFIGURATION FILES
# ====================
CONFIG_VIZ_FILE = 'config_visualizations.json'
CONFIG_INDICATORS_FILE = 'config_indicators.json'
CONFIG_MAPPINGS_FILE = 'config_mappings.json'
DOE_EXPERIMENTS_FILE = 'doe_full_factorial_experiments.csv'
ATTRIBUTES_PATHS_FILE = 'attributes_disassembly_paths.json'

# ====================
# PLOT SETTINGS
# ====================
DEFAULT_DPI = 300
DEFAULT_FIGURE_DPI = 300
DEFAULT_SAVEFIG_DPI = 300
DEFAULT_FONT_SIZE = 10
DEFAULT_TITLE_FONTSIZE = 14
DEFAULT_LABEL_FONTSIZE = 12
DEFAULT_LEGEND_FONTSIZE = 10
DEFAULT_TICK_FONTSIZE = 11
DEFAULT_ANNOTATION_FONTSIZE = 11
DEFAULT_INFO_FONTSIZE = 7
DEFAULT_FONTWEIGHT_BOLD = 'bold'
DEFAULT_GRID_ALPHA = 0.3
DEFAULT_PAD = 20

# ====================
# FIGURE SIZES
# ====================
DEFAULT_FIGSIZE = (10, 6)
LARGE_FIGSIZE = (12, 8)
XLARGE_FIGSIZE = (18, 14)
XXLARGE_FIGSIZE = (18, 18)
SPIDER_FIGSIZE = (12, 10)
HEATMAP_FIGSIZE_BASE = (8, 6)
HEATMAP_SIZE_MULTIPLIER = 2.5
GRID_FIGSIZE = (16, 6)
BAR_SUBPLOT_WIDTH = 5
BAR_SUBPLOT_HEIGHT = 4
FACET_SUBPLOT_WIDTH = 5
FACET_SUBPLOT_HEIGHT = 4

# ====================
# MARKER SIZES
# ====================
DEFAULT_MARKER_SIZE = 120
DEFAULT_SCATTER_MIN_SIZE = 50
DEFAULT_SCATTER_MAX_SIZE = 300
SPIDER_MARKER_SIZE = 8
DEFAULT_LINE_MARKER = 'o'
ERROR_BAR_MARKERSIZE = 6

# ====================
# COLOR SETTINGS
# ====================
DEFAULT_PALETTE = 'Set2'
DEFAULT_COLORMAP = 'RdYlGn_r'
DEFAULT_ALPHA = 0.7
HEATMAP_LINEWIDTH = 2
HEATMAP_LINECOLOR = 'black'

# Table colors
TABLE_HEADER_COLOR = '#4472C4'
TABLE_ROW_LABEL_COLOR = '#D9E2F3'
TABLE_EVEN_ROW_COLOR = '#F2F2F2'
TABLE_ODD_ROW_COLOR = 'white'
TABLE_TEXT_COLOR_WHITE = 'white'

# ====================
# LINE PLOT SETTINGS
# ====================
ERROR_BAR_CAPSIZE = 5
ERROR_BAR_LINEWIDTH = 2
LEGEND_SHADOW = True
LEGEND_FANCYBOX = True
LEGEND_FRAMEON = True

# ====================
# SPIDER PLOT SETTINGS
# ====================
SPIDER_R_MIN = -0.2
SPIDER_R_MAX = 1.2
SPIDER_TICK_VALUES = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

# ====================
# BRANCH MARKERS
# ====================
BRANCH_MARKERS = {
    'main': 'D',           # Diamond for pre-split
    'front_axis': 'o',     # Circle for front axis
    'rear_axis': 's'       # Square for rear axis
}

# ====================
# MARKER STYLES
# ====================
MARKER_STYLES = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']

# ====================
# FOOTER & LEGEND SETTINGS
# ====================
DEFAULT_BOTTOM_MARGIN = 0.15
DEFAULT_TOP_MARGIN = 0.95
DEFAULT_COLUMNS = 4
TABLE_LEGEND_FONTSIZE = 10
TABLE_LEGEND_LINEWIDTH = 1.0
TABLE_LEGEND_ALPHA = 1.0
TABLE_LEGEND_BOX_PAD = 0.8
TABLE_LEGEND_BOX_STYLE = 'round,pad=0.8'
TABLE_LEGEND_FACECOLOR = 'white'
TABLE_LEGEND_EDGECOLOR = 'gray'
TABLE_LEGEND_FAMILY = 'monospace'

# ====================
# TABLE STYLING
# ====================
TABLE_FONT_SIZE = 11
TABLE_HEADER_FONT_SIZE = 12
TABLE_ROW_LABEL_FONT_SIZE = 11
TABLE_TITLE_FONT_SIZE = 13
TABLE_SCALE_X = 1
TABLE_SCALE_Y = 2.5
TABLE_CELL_PAD = 0.08
TABLE_HEADER_HEIGHT = 0.15
TABLE_BBOX_HEIGHT = 0.92
TABLE_TITLE_Y_POS = 0.99
TABLE_SUBPLOT_ROWS = 3
TABLE_SUBPLOT_COLS = 1
TABLE_SUBPLOT_POS = 3

# ====================
# TEXT POSITIONS
# ====================
INFO_BOX_X = 0.02
INFO_BOX_Y = 0.98

# ====================
# OUTPUT SETTINGS
# ====================
VIZ_SUMMARY_FILE = 'visualization_summary.txt'
