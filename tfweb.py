import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import random


EXCEL_PATH = 'annotated_tf_list.xlsx'  # TODO: 实际路径
MERGE_TOLERANCE = 5

def merge_close(group):
    merged = []
    for _, row in group.iterrows():
        s, e = row['Start'], row['Stop']
        matched = False
        for m in merged:
            if abs(s - m['Start']) <= MERGE_TOLERANCE and abs(e - m['Stop']) <= MERGE_TOLERANCE:
                matched = True
                break
        if not matched:
            merged.append(row)
    return pd.DataFrame(merged)

def load_data():
    df = pd.read_excel(EXCEL_PATH)[['TF', 'Start', 'Stop', 'Pvalue', '调控模式']].dropna()
    df['Start'] = df['Start'].astype(int)
    df['Stop'] = df['Stop'].astype(int)
    df = pd.concat([merge_close(g) for _, g in df.groupby('TF')], ignore_index=True)
    
    
    layers = []
    layer_ids = []
    for _, row in df.iterrows():
        s, e = row['Start'], row['Stop']
        placed = False
        for i, layer in enumerate(layers):
            if all(e < x[0] or s > x[1] for x in layer):
                layer.append((s, e))
                layer_ids.append(i)
                placed = True
                break
        if not placed:
            layers.append([(s, e)])
            layer_ids.append(len(layers) - 1)
    df['Layer'] = layer_ids
    return df

data = load_data()
tf_options = sorted(data['TF'].unique())
mode_options = ['activation', 'repression', '其他', '全部']


app = Dash(__name__)

app.layout = html.Div([
    html.H2("PRMT3", style={"textAlign": "center"}),

    html.Div([
        dcc.Input(id='tf-input', type='text', placeholder='搜索 TF 名称（支持模糊）', style={'width': '30%', 'marginRight': '20px'}),
        dcc.Dropdown(
            id='mode-dropdown',
            options=[{'label': m, 'value': m} for m in mode_options],
            value='全部',
            style={'width': '20%', 'marginRight': '20px'}
        ),
        dcc.RangeSlider(
            id='pval-slider',
            min=0, max=1, step=0.001,
            marks={0: '0', 0.05: '0.05', 0.1: '0.1', 1: '1'},
            value=[0, 1],
            tooltip={'always_visible': False}
        )
    ], style={'display': 'flex', 'alignItems': 'center', 'margin': '20px'}),

    dcc.Graph(id='tf-graph')
])


@app.callback(
    Output('tf-graph', 'figure'),
    Input('tf-input', 'value'),
    Input('mode-dropdown', 'value'),
    Input('pval-slider', 'value')
)
def update_graph(tf_query, mode_filter, pval_range):
    filtered = data.copy()

    if tf_query:
        filtered = filtered[filtered['TF'].str.contains(tf_query, case=False, na=False)]

    if mode_filter != '全部':
        filtered = filtered[filtered['调控模式'].str.lower() == mode_filter.lower()]

    filtered = filtered[(filtered['Pvalue'] >= pval_range[0]) & (filtered['Pvalue'] <= pval_range[1])]

    fig = go.Figure()
    random.seed(42)
    tf_colors = {tf: f'rgba({random.randint(50,200)}, {random.randint(50,200)}, {random.randint(50,200)}, 0.7)' for tf in filtered['TF'].unique()}

    for _, row in filtered.iterrows():
        tf = row['TF']
        start = row['Start']
        stop = row['Stop']
        y = row['Layer']
        pval = row['Pvalue']
        mode = str(row['调控模式']).strip().lower()

        if mode == 'activation':
            mode_color = 'green'
        elif mode == 'repression':
            mode_color = 'red'
        else:
            mode_color = 'black'

        hovertext = (
            f"<b>{tf}</b><br>"
            f"Start: {start}<br>Stop: {stop}<br>Pvalue: {pval}<br>"
            f"<span style='color:{mode_color}'>调控模式: {row['调控模式']}</span><extra></extra>"
        )

        fig.add_trace(go.Scatter(
            x=[start, stop],
            y=[y, y],
            mode='lines',
            line=dict(color=tf_colors[tf], width=8),
            hovertemplate=hovertext,
            showlegend=False
        ))

    fig.update_layout(
        xaxis=dict(title='Sequence Position', rangeslider=dict(visible=True)),
        yaxis=dict(title='Track', showticklabels=False),
        height=min(1000, 30 * filtered['Layer'].nunique() + 100),
        margin=dict(l=40, r=40, t=40, b=40),
        title=f"共 {len(filtered)} 个 TF 区域符合条件"
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
