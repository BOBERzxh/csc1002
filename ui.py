import string

from bokeh.core.properties import value
from bokeh.io import curdoc, output_file, show
from bokeh.layouts import layout
from bokeh.layouts import widgetbox as wb
from bokeh.models import ColumnDataSource
from bokeh.models import widgets as wd
from bokeh.plotting import figure

import pymssql

global idx_1, idx_2, idx_c, content_1, content_2
idx_1 = idx_2 = 1
idx_c = 0
content_1 = content_2 = ''

#connect server
def connectSQLServer():
    
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

#UI Controls widgets
GroupLetters = wd.RadioButtonGroup(labels=list(string.ascii_uppercase), active=-1)
title_input = wd.TextInput(value='', title='Title', placeholder='search title')
dept_input = wd.TextInput(value="", title='Department', placeholder='search department')
options = wd.RadioGroup(labels=['and','or'], active=0, width=100, inline=True)
button_refresh = wd.Button(label='Refresh')
Group_choices = wd.RadioButtonGroup(name='Title', 
    labels=['begins with...','...contains...','...ends with'], active=1)
Department_choices = wd.RadioButtonGroup(name='Department', 
    labels=['begins with...','...contains...','...ends with'], active=1)
Text_Instruction = wd.Paragraph(text='option')

# Data table in the first page
columns = [
    wd.TableColumn(field='id', title='Course ID'),
    wd.TableColumn(field='title', title='Title'),
    wd.TableColumn(field='dept', title='Department'),
    wd.TableColumn(field='credit', title='Credits'),
    wd.TableColumn(field='instructor', title='Instructor'),
]
data_table = wd.DataTable(columns=columns, source=ColumnDataSource(), width=800)

# department select 
esql = "SELECT dept_name FROM lgu.department "
sqlConn_1 = connectSQLServer()
with sqlConn_1.cursor(as_dict=True) as cursor_1:
    cursor_1.execute(esql)
    departments = cursor_1.fetchall()
departmentlist = ['All']
for dept in departments:
    departmentlist.append(dept['dept_name'])
dept_select = wd.Select(title='Department:', value="All",
            options=departmentlist)

# historgram page in the second page
# inital all the possible grades for gpa
gpa = ['A+','A','B+','B','C+','C','D+','D','F']
years = ['2015','2016','2017']    # inital all possible years
colors = ["#c9d9d3","#718dbf","#e84d60"]    # set the colors for the bar stack

# construct the frame of the figure
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
p.legend.location = "top_right"
p.legend.orientation = "vertical"


# define callback functions
'''
when click each button the button will execute the callback 
function as follows;
for each function executed, the callback function will return
the idx or content to a global variable
'''
def choose(idx):   # for 'and' and 'or' group radio button
    global idx_c
    idx_c = idx

def title_choice(idx=-1):
    global idx_1
    idx_1 = idx

def dept_choice(idx=-1):
    global idx_2
    idx_2 = idx

def title_change(attr,old,new):
    global content_1
    content_1 = new.strip()

def dept_change(attr,old,new):
    global content_2
    content_2 = new.strip()

# on_click and on_change functions callbacks
Group_choices.on_click(title_choice)
Department_choices.on_click(dept_choice)
title_input.on_change('value', title_change)
dept_input.on_change('value', dept_change)
options.on_click(choose)

# show the course by first letter
'''
idx indicates the button of the group radio
button that is clicked
'''
def data_show(idx):
    letter = GroupLetters.labels[idx]
    tsql = "SELECT * FROM lgu.course where title like '{}%'".format(letter)
    sqlConn = connectSQLServer()
    with sqlConn.cursor(as_dict=True) as cursor:
        cursor.execute(tsql)
        rows = cursor.fetchall()
        data={}
        data['id']=[row['course_id'] for row in rows]
        data['title']=[row['title'] for row in rows]
        data['dept']=[row['dept_name'] for row in rows]
        data['credit']=[row['credits'] for row in rows]
        data['instructor']=[row['instructor'] for row in rows]
    data_table.source.data = data

options.on_click(choose)

# refresh data table
'''
when click the 'refresh' button , the refresh
will execute refreshtable() function to execute 
the search results
'''
def refreshtable():
    global idx_1, idx_2, idx_c,content_1,content_2
    tsql="SELECT * FROM lgu.course where"

    if content_1 != '':
        if idx_1 == 0:
            tsql += " title like '{}%'" .format(content_1)
        elif idx_1 == 1:
            tsql += " title like '%{}%'" .format(content_1)
        elif idx_1 == 2:
            tsql += " title like '%{}'" .format(content_1)

    if  content_1 != '' and content_2 != '':
        if idx_c == 0:
            tsql += " and" 
        elif idx_c == 1:
            tsql += " or"

    if  content_2 !='':
        if idx_2 == 0:
            tsql += " dept_name like '{}%'" .format(content_2)
        elif idx_2 == 1:
            tsql += " dept_name like '%{}%'" .format(content_2)
        elif idx_2 == 2:
            tsql += " dept_name like '%{}'" .format(content_2)

    sqlConn = connectSQLServer()
    with sqlConn.cursor(as_dict=True) as cursor:
        cursor.execute(tsql)
        rows = cursor.fetchall()
        data={}
        data['id']=[row['course_id'] for row in rows]
        data['title']=[row['title'] for row in rows]
        data['dept']=[row['dept_name'] for row in rows]
        data['credit']=[row['credits'] for row in rows]
        data['instructor']=[row['instructor'] for row in rows]
    data_table.source.data = data

# groupletterbuttons and refresh button callbacks
GroupLetters.on_click(data_show)
button_refresh.on_click(refreshtable)

# department selection callback functions
'''
when click each of department, the program will execute the select_on_change() 
function, and the stack bar chart will show the gpa count statistics by year
'''
def select_on_change(attr,old,new):
    tsql_2015 = "select gpa, count(*) as nums from lgu.student where year='2015' "
    tsql_2016 = "select gpa, count(*) as nums from lgu.student where year='2016' "
    tsql_2017 = "select gpa, count(*) as nums from lgu.student where year='2017' "

    if new != 'All':
        tsql_2015 += "and dept_name = '{}' ".format(new)
        tsql_2016 += "and dept_name = '{}' ".format(new)
        tsql_2017 += "and dept_name = '{}' ".format(new)
    
    tsql_2015 += 'group by gpa'
    tsql_2016 += 'group by gpa'
    tsql_2017 += 'group by gpa'

    sqlConn = connectSQLServer()
    with sqlConn.cursor(as_dict=True) as cursor:
        cursor.execute(tsql_2015)
        gpa_2015 = cursor.fetchall()
        cursor.execute(tsql_2016)
        gpa_2016 = cursor.fetchall()
        cursor.execute(tsql_2017)
        gpa_2017 = cursor.fetchall()
    
    grade_2015 = list()
    grade_2016 = list()
    grade_2017 = list()
    count_2015 = list()
    count_2016 = list()
    count_2017 = list()

    for row in gpa_2015:
        grade_2015.append(row['gpa'])
        count_2015.append(row['nums'])
    for row in gpa_2016:
        grade_2016.append(row['gpa'])
        count_2016.append(row['nums'])
    for row in gpa_2017:
        grade_2017.append(row['gpa'])
        count_2017.append(row['nums'])
    
    new_data = {}
    new_data['gpa'] = ['A','A+','B','B+','C','C+','D','D+','F']
    new_data['2015'] = check_zero(grade_2015,count_2015)
    new_data['2016'] = check_zero(grade_2016,count_2016)
    new_data['2017'] = check_zero(grade_2017,count_2017)
    
    source.data = new_data

dept_select.on_change("value",select_on_change)

# in case of absence of a grade:
'''
some number of grade for certain departments' are missing, and SQL won't return 0
so this function will default such case, and return 0 if such number of grade is missing
parameters:
grade: type<list>:the grade exist for each department
count: type<list>:the number of people corresponding to each grade
'''
def check_zero(grade,count):
    standard = ['A','A+','B','B+','C','C+','D','D+','F']
    for i in range(9):
        if standard[i] not in grade :
            count.insert(i,0)
    return count

#Screen Pages Layout
layout_query = layout(
    [
        [wb(GroupLetters,width=1000)],
        [wb(Group_choices,width=400),wb(Department_choices)],
        [wb(title_input),wb(Text_Instruction, options, width=100),wb(dept_input)],
        [wb(button_refresh, width=100)],
        [wb(data_table)],
    ]
)

layout_chart = layout(
    [
        [wb(dept_select),p],
    ]
)

#Tab Layout
tab1 = wd.Panel(child=layout_query,title='Course Info')
tab2 = wd.Panel(child=layout_chart,title='Statistics')
tabs = wd.Tabs(tabs=[tab1,tab2])

#Display Interaction
curdoc().add_root(tabs)