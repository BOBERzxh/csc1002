from bokeh.io import show, curdoc
from bokeh.models import widgets as wd
from bokeh.layouts import widgetbox as wb, layout
import random
import time

# Login
btnLogin = wd.Button(label="Login")
btnReset = wd.Button(label="Reset")
name = wd.TextInput(title="Name", 
    placeholder="enter name ....")
pwd = wd.TextInput(title="Password", 
    placeholder="enter password ....")

# Study
majors = wd.RadioButtonGroup(labels=["CS", "Stat", "Math", "EIE", "Energy", "HSS", "SME"])
text = wd.Paragraph(text="Press button to start .... ")
answer = wd.Paragraph(text="")
btnRandom = wd.Button(label="Choose For Me")

login = layout( [
        [ wb(name) ],
        [ wb(pwd) ],
        [ wb(btnLogin), wb(btnReset) ]  # side by side
    ] )

major = layout( [
        [ wb(majors, width=800) ],
        [ wb(text, btnRandom, answer) ]
    ] )

page1 = wd.Panel(child=login, title="Login")
page2 = wd.Panel(child=major, title="Major")

tabs = wd.Tabs( tabs=[page1, page2] )

def choose():
    cnt=5
    for i in range(cnt):
        answer.text = "your answer is .... {}".format(cnt-i)
        time.sleep(2)
        idx = random.randint(0,len(majors.labels)-1)
        majors.active = idx
    answer.text = "your answer is " + majors.labels[idx]

btnRandom.on_click(choose)

# show(tabs)
curdoc().add_root(tabs)

