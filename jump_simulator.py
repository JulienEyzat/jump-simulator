import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import simulator

app = dash.Dash(__name__)
server = app.server

def create_slider(label, id, min_value, max_value, init_value):
    max_marks = 15
    mark_step = int((max_value - min_value)/max_marks)
    slider = html.Div([
        html.Label(
            children=label,
            style={
                'textAlign': 'center'
            }
        ),
        dcc.Slider(
            id=id,
            min=min_value,
            max=max_value,
            value=init_value,
            marks={str(vx): str(vx) for vx in range(min_value, max_value+1, mark_step)},
        )
    ])
    return slider

def create_radio(label, id, radio_labels, radio_values, init_value):
    radio = html.Div([
        html.Label(label),
        dcc.RadioItems(
            id=id,
            options=[ {"label": radio_label, "value": radio_value} for radio_label, radio_value in zip(radio_labels, radio_values) ],
            value=init_value
        )
    ])
    return radio

def create_app_layout():
    app_layout = html.Div([
        html.Div([
            html.H1("Updates the following variables"),
            create_radio("Is Air", "is-air", ("yes", "no"), ("True", "False"), "True"),
            create_slider("Speed of jump (km/h)", "vx0-slider", 0, 25, 5),
            create_slider("Height of jump (m)", "y0-slider", 0, 15, 10),
            create_radio("Wind direction on x", "windxdir-radio", ("push", "pull"), (1, -1), 1),
            create_slider("Speed of wind in x direction (km/h)", "windx-slider", 0, 100, 0),
            create_radio("Wind direction on y", "windydir-radio", ("up", "down"), (1, -1), 1),
            create_slider("Speed of wind in y direction (km/h)", "windy-slider", 0, 100, 0)
        ]),
        dcc.Graph(id='graph-with-slider')
    ], style={'display': 'flex', 'flex-direction': 'row'})

    return app_layout

@app.callback(
    Output('graph-with-slider', 'figure'),
    Input("is-air", "value"),
    Input('vx0-slider', 'value'),
    Input('y0-slider', 'value'),
    Input("windxdir-radio", "value"),
    Input('windx-slider', 'value'),
    Input("windydir-radio", "value"),
    Input("windy-slider", "value")
)
def update_figure(selected_is_air, selected_vx0, selected_y0, selected_windxdir, selected_windx, selected_windydir, selected_windy):
    is_air = selected_is_air == "True"
    input_constants = {
        "vx0": simulator.kmph_to_mps(selected_vx0),
        "y0": selected_y0,
        "windx_dir": selected_windxdir,
        "windx": simulator.kmph_to_mps(selected_windx),
        "windy_dir": selected_windydir,
        "windy": simulator.kmph_to_mps(selected_windy)
    }
    ts, xs, ys = simulator.simulator(input_constants, is_air)

    fig = px.line(
        x=xs,
        y=ys, 
        title="Jump"
    )

    fig.update_xaxes(range=[0, 20])
    fig.update_yaxes(range=[0, 15])

    fig.update_layout(transition_duration=200)

    return fig

app.layout = create_app_layout()
if __name__ == '__main__':
    app.run_server(debug=True)