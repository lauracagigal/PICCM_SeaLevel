import matplotlib.colors as mcolors
from matplotlib import cm
import numpy as np

default_colors = [
        "#636EFA",
        "#EF553B",
        "#00CC96",
        "#AB63FA",
        "#FFA15A",
        "#19D3F3",
        "#FF6692",
        "#B6E880",
        "#FF97FF",
        "#FECB52",
    ]


scatter_defaults = {
            "figsize": (9, 8),
            "marker": ".",
            "color_data": "#00CC96",
            "color_subset": "#AB63FA",
            "alpha_data": 0.5,
            "alpha_subset": 0.7,
            "size_data": 10,
            "size_centroid": 70,
            "fontsize": 12,
        }

def get_config_variables():

    config_variables = {}
    
    config_variables['geo500hpa'] = {
                                     'cmap': 'Blues', 
                                     'limits': (45000, 60000),
                                     'label': 'Geo500Hpa [m]'
                                    }
    
    
    config_variables['mslp'] = {
                                'cmap': 'RdBu_r', 
                                'limits': (1014 - 20, 1014 + 20),
                                'label': 'MSLP [mbar]'
                                }
    
    config_variables['mslp_grad'] = {
                                    'cmap': 'BuGn', 
                                    'limits': (0, 100),
                                    'label': 'MSLP - grad [mbar]'
                                    }
    
    config_variables['sst'] = {
                                    'cmap': 'hot_r', 
                                    'limits': (0, 30),
                                    'label': 'SST - [°C]'
                                    }

    config_variables['other'] = {
                                    'cmap': 'rainbow', 
                                    'limits': (None, None),
                                    'label': ' '
                                    }

    return config_variables
