from bokeh.layouts import widgetbox, layout
from bokeh.plotting import curdoc
from bokeh.models.widgets import RadioButtonGroup

import string

btnGroupLetters = RadioButtonGroup(labels=list(string.ascii_uppercase), active=-1)

page = layout(
    [widgetbox(btnGroupLetters, width=1000)]        
)

curdoc().add_root(page)
