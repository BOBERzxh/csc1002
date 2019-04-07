from bokeh.io import show, curdoc,output_file
from bokeh.plotting import figure
from bokeh.layouts import widgetbox as wb, layout
from bokeh.models import widgets as wd, ColumnDataSource
from bokeh.core.properties import value
import string
import pymssql

paragraph = wd.Paragraph(text="option")
optionGroup = wd.RadioGroup(labels=["and", "or"], active=0, width=100, inline=True)
btnGroupLetters = wd.RadioButtonGroup(labels=list(string.ascii_uppercase), active=-1)
title_input = wd.TextInput(value="", title="Title:", placeholder="comtains....")
dept_input = wd.TextInput(value="",title="Department", placeholder="contains....")
btnGroupTitle = wd.RadioButtonGroup(name='title',
     labels=["begin with...", "...comtains...", "...ends with"], active=1)
refresh = wd.Button(label="Refresh")
btnGroupDept = wd.RadioButtonGroup(name='dept',
     labels=["begin with...", "...contains...", "...end with"], active=1)

def  connectSQLServer():
    attr = dict(
        server = '10.20.213.10',
        database = 'csc1002',
        user = 'csc1002',
        password = 'csc1002',
        port = 1433,
        as_dict = True
    )
    try:
        return pymssql.connect(**attr)
    except Exception as e:
        print(e)
        quit()

tsql = "SELECT dept_name FROM lgu.department"
sqlConn = connectSQLServer()
with sqlConn.cursor(as_dict=True) as cursor:
    cursor.execute(tsql)
    departments = cursor.fetchall()
deptlist = ['All']    
for dept in departments:
        deptlist.append(dept['dept_name'])
deptSelect = wd.Select(title='Department', value='All', options= deptlist)

global idx_a, idx_b, idx_c, event_a, event_b
event_a = event_b = ""
idx_a = idx_b = 1
idx_c = 0  

def titleChoice(idx=-1):
    global idx_a
    idx_a = idx

def deptChoice(idx=-1):
    global idx_b
    idx_b = idx

def titleChange(attr, old, new):
    global event_a
    event_a = new.strip()

def deptChange(attr, old, new):
    global event_b
    event_b = new.strip()

def choose(idx):
    global idx_c
    idx_c = idx    


btnGroupTitle.on_click(titleChoice)
btnGroupDept.on_click(deptChoice)
optionGroup.on_click(choose)

title_input.on_change("value", titleChange)
dept_input.on_change("value", deptChange)

columns = [
    wd.TableColumn(field="id", title="Course ID"),
    wd.TableColumn(field="title", title="Title"),
    wd.TableColumn(field="dept", title="department"),
    wd.TableColumn(field="credit", title="Credit"),
    wd.TableColumn(field="instructor", title="Instructor"),
]
table = wd.DataTable(source= ColumnDataSource(),
    columns=columns, width=800)

def dataShow(idx):
    letter = btnGroupLetters.labels[idx]
    tsql = "SELECT * FROM lgu.course where title like '{}%'".format(letter)
    sqlConn = connectSQLServer()
    with sqlConn.cursor(as_dict=True) as cursor:
        cursor.execute(tsql)
        rows = cursor.fetchall()
        data={}
        data['id'] = [row['course_id'] for row in rows]
        data['title'] = [row['title'] for row in rows]
        data['instructor'] = [row['instructor'] for row in rows]
        data['credit'] = [row['credits'] for row in rows]
        data['dept'] = [row['dept_name'] for row in rows]
    table.source.data = data
optionGroup.on_click(choose)

def checkZero(grade,count):
    list = ['A','A+','B','B+','C','C+','D','D+','F']
    for i in range(9):
        if list[i] not in grade :
            count.insert(i,0)
    return count

def selectOnChange(attr,old,new):
    tsql2015 = "select gpa, count(*) as nums from lgu.student where year='2015' "
    tsql2016 = "select gpa, count(*) as nums from lgu.student where year='2016' "
    tsql2017 = "select gpa, count(*) as nums from lgu.student where year='2017' "

    if new != 'All':
        tsql2015 += "and dept_name = '{}' ".format(new)
        tsql2016 += "and dept_name = '{}' ".format(new)
        tsql2017 += "and dept_name = '{}' ".format(new)
    
    tsql2015 += 'group by gpa'
    tsql2016 += 'group by gpa'
    tsql2017 += 'group by gpa'

    sqlConn = connectSQLServer()
    with sqlConn.cursor(as_dict=True) as cursor:
        cursor.execute(tsql2015)
        gpa2015 = cursor.fetchall()
        cursor.execute(tsql2016)
        gpa2016 = cursor.fetchall()
        cursor.execute(tsql2017)
        gpa2017 = cursor.fetchall()
    
    grade2015 = list()
    grade2016 = list()
    grade2017 = list()
    count2015 = list()
    count2016 = list()
    count2017 = list()

    for row in gpa2015:
        grade2015.append(row['gpa'])
        count2015.append(row['nums'])
    for row in gpa2016:
        grade2016.append(row['gpa'])
        count2016.append(row['nums'])
    for row in gpa2017:
        grade2017.append(row['gpa'])
        count2017.append(row['nums'])
    
    data = {}
    data['gpa'] = ['A','A+','B','B+','C','C+','D','D+','F']
    data['2015'] = checkZero(grade2015,count2015)
    data['2016'] = checkZero(grade2016,count2016)
    data['2017'] = checkZero(grade2017,count2017)
    
    source.data = data

deptSelect.on_change("value",selectOnChange)




gpa = ['A+','A','B+','B','C+','C','D+','D','F']
years = ['2015','2016','2017']    
colors = ["#c9d9d3","#718dbf","#e84d60"]   

data = {}
data['gpa'] = []
for yr in years:
    data[yr] = []

source = ColumnDataSource(data=data)

p = figure(x_range=gpa, plot_height=500, plot_width=800, title='GPA count by year',
        toolbar_location=None, tools="")

p.vbar_stack(years,x='gpa', width=0.9, color=colors, source=source,
        legend=[value(x) for x in years])

p.y_range.start = 0
p.legend.location = "top_center"
p.legend.orientation = "vertical"

layout_query = layout(
    [
        [wb(btnGroupLetters, width=1000)],
        [wb(btnGroupTitle), wb(btnGroupDept)],
        [wb(title_input), wb(paragraph, optionGroup, width=100), wb(dept_input)],
        [wb(refresh, width=100)],
        [wb(table)],
    ]
)

layout_chart = layout(
    [
        [wb(deptSelect),p]
    ]
)

tab1 = wd.Panel(child=layout_query, title="Course Info")
tab2 = wd.Panel(child=layout_chart, title="Statistics")
tabs = wd.Tabs( tabs = [tab1,tab2] )

curdoc().add_root(tabs)