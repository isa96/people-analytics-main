# -------------------1. IMPORT DASH--------------------------
## Import Library
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# color theme for PLN
color_pln = ['#f7e82e','#4ca8e0','#e72a2b']

# ------- DATA PREPARATION ---------
# read the data
promotion = pd.read_csv('data_input/promotion_clean.csv')

# rename categorical values
promotion['KPIs_met >80%'] = promotion['KPIs_met >80%'].map({0: 'No', 1: 'Yes'})
promotion['awards_won?'] = promotion['awards_won?'].map({0: 'No', 1: 'Yes'})
promotion['is_promoted'] = promotion['is_promoted'].map({0: 'No', 1: 'Yes'})
promotion['gender'] = promotion['gender'].map({'m': 'Male', 'f': 'Female'})

# change data types
promotion[['date_of_birth','join_date']] = promotion[['date_of_birth','join_date']].astype('datetime64')

promotion[['department',
           'region',
           'education',
           'gender',
           'recruitment_channel',
           'KPIs_met >80%',
           'awards_won?',
           'is_promoted']] = promotion[['department',
                                        'region',
                                        'education',
                                        'gender',
                                        'recruitment_channel',
                                        'KPIs_met >80%',
                                        'awards_won?',
                                        'is_promoted']].astype('category')

# ------ CARD VALUE COMPONENT --------
# card value from sum_promoted
promoted_employee = promotion[promotion['is_promoted'] == 'Yes']
sum_promoted = promoted_employee.shape[0]

# card information
card_content = [
    dbc.CardHeader("Information"),
    dbc.CardBody(
        [
            html.P(
                "This is the information of employeed in our Start-up. help to indentify who is a potential candidate for promotion",
                className="card-text",
            ),
        ]
    ),
]

# card number of employee who have been promoted
card_promoted = [
    dbc.CardHeader("Who is Promoted?"),
    dbc.CardBody(
        [
            html.H2(sum_promoted)
        ]
    ),
]


# ------- DROPDOWN COMPONENT ----------
# DROPDOWN VALUE (HAVE HIGEST PROMOTION RATE) -> ROW 2
list_category = [
            {'label': 'Department', 'value': 'department'},
            {'label': 'Gender', 'value': 'gender'},
            {'label': 'Region', 'value': 'region'},
            {'label': 'Recruitment Channel', 'value': 'requirement_channel'},
            {'label': 'KPI Met >80%', 'value': 'KPIs_met >80%'},
            {'label': 'Awards Won?', 'value': 'awards_won?'}
        ]


# DROPDOWN VALUE (PREVIOUS RATING AND EDUCATION) -> ROW 3
list_department=[
            {'label': 'Finance', 'value': 'Finance'},
            {'label': 'Sales & Marketing', 'value': 'Sales & Marketing'},
            {'label': 'Technology', 'value': 'Technology'},
            {'label': 'Operations', 'value': 'Operations'},
            {'label': 'Procurements', 'value': 'Procurements'},
            {'label': 'Analytics', 'value': 'Analytics'},
            {'label': 'HR', 'value': 'HR'},
            {'label': 'R&D', 'value': 'R&D'},
            {'label': 'Legal', 'value': 'Legal'}
]

# ---------------------------- 2. CREATE DASH APP INSTANCE ---------------------------
# THEME
app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])
app.title = 'Employee Promotion'
server = app.server

# LAYOUT    
app.layout = html.Div(children=[
    # TITLE
    html.H1("Employee Promotion Analysis"),
    html.Br(),

    # ROW 1 -> CARD COMPONENT
    dbc.Row(
        [
            dbc.Col(dbc.Card(card_content, color="primary", outline=True), width = 6),
            dbc.Col(dbc.Card(card_promoted, color="warning", inverse=True), width = 2),
            dbc.Col(dbc.Card(card_promoted, color="info", inverse=True), width = 2),
            dbc.Col(dbc.Card(card_promoted, color="danger", inverse=True), width = 2)
        ]
    ),
    html.Hr(), html.Br(),

    # ROW 2 -> DROPDOWN LIST CATEGORY
    dbc.Row(
        dcc.Dropdown(
            id = 'id_list_category',
            options = list_category,
            value='department'

        )
    ), html.Br(),

    # ROW 3 -> VISUALIZATION HIGEST PROMOTION RATE
    dbc.Row(
        dcc.Graph(
            id = 'highest_promotion_rate'
        )
    ),

    # ROW 4 -> DROPDOWN DEPARTMENT
    dbc.Row(
        dcc.Dropdown(
            id = 'department_category',
            options = list_department,
            value = 'Finance'
        )
    ),

    # ROW 5 -> VISUALIZATION HEATMAP AND SCATTER
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id = 'heatmap_viz'), width=6),
            dbc.Col(dcc.Graph(id = 'scatter_viz'), width=6)
        ]
    )

])



# CALLBACK DROPDOWN HIGEST PROMOTION RATE
@app.callback(
    Output(component_id='highest_promotion_rate', component_property='figure'),
    Input(component_id='id_list_category', component_property='value')
)
# VISUALIZATION HIGHEST PROMOTION RATE
def update_bar_plot(category_value):
    promot_gender = pd.crosstab(
        index = promoted_employee[category_value],
        columns = 'Percentage',
        normalize = True
    ).round(2).reset_index().sort_values(by='Percentage', ascending=False)
    bar_plot = px.bar(
        promot_gender,
        x = promot_gender[category_value],
        y = promot_gender['Percentage'],
        labels = {
            category_value : str(category_value.title())
        },
        title = 'Which gender have the highest promotion rate?',
        color_discrete_sequence= ['#e72a2b']
    )

    return bar_plot



# CALLBACK DROPDOWN EMPLOYEE DEPARTMENT RATING AND EDUCATION
@app.callback(
    Output(component_id='heatmap_viz', component_property='figure'),
    Output(component_id='scatter_viz', component_property='figure'),
    Input(component_id='department_category', component_property='value')
)
# VISUALIZATION HEATMAP EMPLOYEE DEPARTMENT RATING AND EDUCATION
def heatmap_scatter_viz(depart_val):
    department_agg = promotion[promotion['department'] == depart_val]
    heatmap = px.density_heatmap(
        department_agg,
        x = 'previous_year_rating',
        y = 'education',
        title = 'Number of Employee by Previous Rating and Education',
        labels={
            'previous_year_rating' : 'Previous Year Rating',
            'education' : 'Education'
        },
        template='ggplot2',
        color_continuous_scale= color_pln
    )
# VISUALIZATION SCATTER EMPLOYEE DEPARTMENT RATING AND EDUCATION
    scatter = px.scatter(department_agg,
          x='avg_training_score',
          y='length_of_service',
          title='Correlation between Avg Training Score and Length of Service',
          labels={
              'avg_training_score' : 'Average Training Score',
              'length_of_service' : 'Length of Service',
              'KPIs_met >80%': 'KPIs met >80%?',
              'no_of_trainings': 'No. of Trainings',
              'is_promoted': 'Promoted Status'
          },
          facet_col='is_promoted',
          color='KPIs_met >80%',
          size='no_of_trainings',
          hover_name='employee_id',
          color_discrete_sequence= color_pln)

    return [heatmap,scatter]



# ------------------ 3. START DASH SERVER --------------------------------
if __name__ == "__main__":
    app.run_server()