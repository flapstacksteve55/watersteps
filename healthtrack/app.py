from dash import Dash, dash_table,html,dcc,Input,Output,State
import pandas as pd
import sqlite3 
import plotly.express as px
import datetime
import smtplib, ssl
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart


#connect to watersteps db
conn = sqlite3.connect('healthtrack/watersteps.db')
#uncomment out the below 2 lines if you are bulk adding via csv
#df = pd.read_csv('healthtrack/watersteps.csv')
#df.to_sql('steven',conn,if_exists='replace',index=False)

#get the data from the database table for "steven"
df = pd.read_sql("select * FROM steven", conn)
#produce the line charts
stepfig=px.line(df, x='Date', y= 'Steps',markers=True)
stepfig.add_hline(y=6000)
stepfig.update_traces(line_color='orange')
stepfig.update_layout(paper_bgcolor='lightblue')

waterfig=px.line(df, x='Date', y='Water',markers=True)
waterfig.add_hline(y=72)
waterfig.update_traces(line_color='blue')
waterfig.update_layout(paper_bgcolor='lightblue')
#produce the table
df = df.rename({'Water': 'Water (Ounces)'}, axis='columns')
table = df.to_dict('records')

#calculate averages for both measurements
Water_Mean = df['Water (Ounces)'].mean().round(2)
Step_Mean = df["Steps"].mean().round(2)

#determine when steps and water goals were met
steps_met = df[df['Steps']>6000]
water_met = df[df['Water (Ounces)']>70]

#calculate the percentages
water_pct=(len(water_met)/len(df))
water_pct= "{:.2%}".format(water_pct)
steps_pct = len(steps_met)/len(df)
steps_pct="{:.2%}".format(steps_pct)
#how many days were both goals met. 70 ounces of water and 6000 steps in this case
both = df[(df['Steps']>6000) & (df['Water (Ounces)'] >70)]
both_pct=(len(both)/len(df))
both_pct= "{:.2%}".format(both_pct)



app = Dash("Steven's Water Steps")

app.layout = html.Div([html.Img(src=r'assets/waterguy.jpeg', alt='image',className="center"),
    html.H1(children='Water and Steps',style={'text-align':'center'}),
    html.H2(children="By Steven Valentino",style={'text-align':'center'}),
        html.Br(),
        html.Audio(src=r'assets/yes.mp3',id='yes'),
        html.Div(className="myaddinputs",children=[html.P("Date:  "),
        dcc.Input(id='date',value='', type='text'),
        html.P("Steps:  "),
        dcc.Input(id='steps', value='',type='number'),
        html.P("Water (Ounces): "),
        dcc.Input(id='water',value='', type='number'),
        html.Button(id='new', children= 'Submit',n_clicks=None)]),
        html.Div(className="mydelinputs",children=[html.P("Delete Date: "),
        dcc.Input(id='Dated',value='', type='text'),
        html.Button(id='wrong', children= 'Submit',n_clicks=None)]),
        html.Br(),
        html.Br(),
        html.Button(id='email', children= 'SEND EMAIL REPORT',n_clicks=None),
    dash_table.DataTable(id='table',data=table,page_size=5,style_data={
        'color': 'orange',
        'backgroundColor': 'blue',
        'fontWeight': 'bold',
        'border': '2px solid white'},
        style_header={
        'color': 'orange',
        'backgroundColor': 'blue',
        'fontWeight': 'bold',
        'border': '2px solid white'},
        style_cell = {
        'font-size': '20px',
        'text-align': 'center'},
        columns=[
        {'name': 'Date', 'id': 'Date', 'type': 'text'},
        {'name': 'Steps', 'id': 'Steps', 'type': 'numeric'},
        {'name': 'Water (Ounces)', 'id': 'Water (Ounces)', 'type': 'numeric'}]),
    html.Div(children=[dcc.Graph(id='line',figure=stepfig,style={'display': 'inline-block','padding': 5}),
    dcc.Graph(id='line1',figure=waterfig,style={'display': 'inline-block','padding': 5})]),
    html.Div(id='my-div'),
    html.Br(),
    html.Div(id='rando'),
    html.Div(className='data-container',id='info',children=[
    html.Span(id='smeanhead',children='Average of Steps: '),
    html.Span(id='spcthead',children='Percent of Days Steps Goal was Met: '),
    html.Span(id='bpcthead',children='Percent of Days Both Goals were Met: '),
    html.Span(id='wmeanhead',children='Average of Water (Ounces): '),
    html.Span(id='wpcthead',children='Percent of Days Water Goal was Met: ')]),
    html.Div(className='data-container',id='numinfo',children=[
    html.Span(id='smean',children=Step_Mean),
    html.Span(id='spct',children=steps_pct),
    html.Span(id='bpct',children=both_pct),
    html.Span(id='wmean',children=Water_Mean),
    html.Span(id='wpct',children=water_pct)]),
    ])

@app.callback(
     Output(component_id='rando',component_property='children'),
    Input(component_id='email', component_property='n_clicks'),
    prevent_initial_call=True,
    )

def sendupdate(n):
    
    conn = sqlite3.connect('healthtrack/watersteps.db')
    #get the data from the database table for "steven"
    df = pd.read_sql("select * FROM steven", conn)
    #produce the line charts
    stepfig=px.line(df, x='Date', y= 'Steps',markers=True)
    stepfig.add_hline(y=6000)
    stepfig.update_traces(line_color='orange')
    stepfig.update_layout(paper_bgcolor='lightblue')

    waterfig=px.line(df, x='Date', y='Water',markers=True)
    waterfig.add_hline(y=72)
    waterfig.update_traces(line_color='blue')
    waterfig.update_layout(paper_bgcolor='lightblue')
    #produce the table
    df = df.rename({'Water': 'Water (Ounces)'}, axis='columns')
    table = df.to_dict('records')

    #calculate averages for both measurements
    Water_Mean = df['Water (Ounces)'].mean().round(2)
    Step_Mean = df["Steps"].mean().round(2)
    #connect to the gmail server
    s = smtplib.SMTP('smtp.gmail.com', 587)

    #Start TLS for security purposes
    s.starttls()

    #provide the passowrd

    load_dotenv("healthtrack/cred.env")
    password = os.environ.get("password")

    #create the subject and message we want and send from/to the correct addresses

    SUBJECT = "Your Latest Water and Steps Report!"

    sender_email = os.environ.get("sender_email")
    receiver_email = os.environ.get("recepient_email")

    #log in
    s.login(sender_email, password)

    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = sender_email
    msg['To'] = receiver_email
    
    html = """\
    <html>
  <head></head>
  <body>
    {0} You have averaged {1} steps! Your water average (in ounces) is {2}.
  </body>
</html>
""".format(df.to_html(),Step_Mean,Water_Mean)

    part1 = MIMEText(html, 'html')
    msg.attach(part1)
    
    

    #send mail
    s.send_message(msg)

    #quit server
    s.quit()
    
    txt = ""
    return txt

@app.callback(
    Output(component_id='yes',component_property= 'children'),
    Output(component_id='smean',component_property= 'children'),
    Output(component_id='spct',component_property= 'children'),
    Output(component_id='bpct',component_property= 'children'),
    Output(component_id='wmean',component_property= 'children'),
    Output(component_id='wpct',component_property= 'children'),
    Output(component_id='line',component_property= 'figure'),
    Output(component_id='line1',component_property= 'figure'),
    Output(component_id='table',component_property = 'data'),
    State(component_id='date', component_property='value'),
    State(component_id='steps', component_property='value'),
    State(component_id='water', component_property='value'),
    Input(component_id='new', component_property='n_clicks'),
    prevent_initial_call=True,
    )

def addtodb(date,steps,water,n_clicks):
    
    conn = sqlite3.connect('healthtrack/watersteps.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO steven (date,steps,water) values (?,?,?)",(date,steps,water))
    conn.commit()
    
    df = pd.read_sql("select * FROM steven", conn)
    
    stepfig=px.line(df, x='Date', y= 'Steps',markers=True)
    stepfig.add_hline(y=6000)
    stepfig.update_traces(line_color='orange')
    stepfig.update_layout(paper_bgcolor='lightblue')
    waterfig=px.line(df, x='Date', y='Water',markers=True)
    waterfig.add_hline(y=72)
    waterfig.update_traces(line_color='purple')
    waterfig.update_layout(paper_bgcolor='lightblue')
    df = df.rename({'Water': 'Water (Ounces)'}, axis='columns')
    table = df.to_dict('records')
    
    #calculate averages for both measurements
    Water_Mean = df["Water (Ounces)"].mean().round(2)
    Step_Mean = df["Steps"].mean().round(2)

    #determine when steps and water goals were met
    steps_met = df[df['Steps']>6000]
    water_met = df[df['Water (Ounces)']>70]

    #calculate the percentages
    water_pct=(len(water_met)/len(df))
    water_pct= "{:.2%}".format(water_pct)
    steps_pct = len(steps_met)/len(df)
    steps_pct="{:.2%}".format(steps_pct)
    #how many days were both goals met
    both = df[(df['Steps']>6000) & (df['Water (Ounces)'] >70)]
    both_pct=(len(both)/len(df))
    both_pct= "{:.2%}".format(both_pct)
    if steps > 6000 and water >= 72: 
        return html.Audio(src=r'assets/yes.mp3',id='yes',autoPlay=True),Step_Mean,steps_pct,both_pct,Water_Mean,water_pct,stepfig,waterfig,table
    else:
        return html.Audio(src=r'assets/aintso.mp3',id='yes',autoPlay=True,hidden=True),Step_Mean,steps_pct,both_pct,Water_Mean,water_pct,stepfig,waterfig,table
    
        
    

@app.callback(
    Output(component_id='smean',component_property= 'children',allow_duplicate=True),
    Output(component_id='spct',component_property= 'children',allow_duplicate=True),
    Output(component_id='bpct',component_property= 'children',allow_duplicate=True),
    Output(component_id='wmean',component_property= 'children',allow_duplicate=True),
    Output(component_id='wpct',component_property= 'children',allow_duplicate=True),
    Output(component_id='line',component_property= 'figure',allow_duplicate=True),
    Output(component_id='line1',component_property= 'figure',allow_duplicate=True),
    Output(component_id='table',component_property = 'data',allow_duplicate=True), 
    State(component_id='Dated', component_property='value'),
    Input(component_id='wrong', component_property='n_clicks'),
    prevent_initial_call=True,
    ) 

def deletefromdb(Dated,n_clicks):
    conn = sqlite3.connect('healthtrack/watersteps.db')
    format = "%Y-%m-%d"
    cursor = conn.cursor()
    if Dated is None:
        pass
    elif bool(datetime.datetime.strptime(Dated, format))==False:
        pass
    # Deleting records with the DATE entered
    cursor.execute("""DELETE FROM steven WHERE Date = (?)""", (Dated,))
    conn.commit()

    df = pd.read_sql("select * FROM steven", conn)

    stepfig=px.line(df, x='Date', y= 'Steps',markers=True)
    stepfig.add_hline(y=6000)
    stepfig.update_traces(line_color='orange')
    stepfig.update_layout(paper_bgcolor='lightblue')
    waterfig=px.line(df, x='Date', y='Water',markers=True)
    waterfig.add_hline(y=72)
    waterfig.update_traces(line_color='purple')
    waterfig.update_layout(paper_bgcolor='lightblue')
    df = df.rename({'Water': 'Water (Ounces)'}, axis='columns')
    table = df.to_dict('records')
    
    #calculate averages for both measurements
    Water_Mean = df["Water (Ounces)"].mean().round(2)
    Step_Mean = df["Steps"].mean().round(2)

    #determine when steps and water goals were met
    steps_met = df[df['Steps']>6000]
    water_met = df[df['Water (Ounces)']>70]

    #calculate the percentages
    water_pct=(len(water_met)/len(df))
    water_pct= "{:.2%}".format(water_pct)
    steps_pct = len(steps_met)/len(df)
    steps_pct="{:.2%}".format(steps_pct)
    #how many days were both goals met
    both = df[(df['Steps']>6000) & (df['Water (Ounces)'] >70)]
    both_pct=(len(both)/len(df))
    both_pct= "{:.2%}".format(both_pct)
    
    return Step_Mean,steps_pct,both_pct,Water_Mean,water_pct,stepfig,waterfig,table
    
if __name__ == '__main__':
    app.run_server(debug=True)