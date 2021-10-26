import streamlit as st
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from tools import getSoup, getStats, ewma

st.set_page_config(page_title='Lux AI stats', 
                   page_icon='🤖',
                   layout='wide',
                   menu_items={
                       'About': 'Submission statistics for Lux AI competition. Made by Yalikesifulei from Team ♂ GARCH ♂.'
                   })

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer:after {
            content: 'Submission statistics for Lux AI competition. Made by Yalikesifulei from Team ♂ GARCH ♂.'; 
            visibility: visible;
            display: block;
            position: relative;
            padding: 5px;
            top: 2px;
        }</style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.title('Lux AI submission statistics')
col1, col2 = st.columns(2)

sub_id = col1.number_input('Submission ID', value=23032370, step=1, key='sub_id')

if col2.button('Get stats', key='run'):
    with st.spinner('Wait for it...'):
        try:
            soup = getSoup(sub_id)
            team_name, scores, outcomes, scores_delta, hover_text = getStats(soup)
            is_ok = True
        except ValueError:
            is_ok = False
            st.error('**Error:** wrong submission ID!')

    if is_ok:
        info_cols = st.columns(3)
        info_cols[0].subheader(team_name)
        info_cols[1].subheader(f'Current score: {scores[-1]}')
        info_cols[2].subheader(f'Current win rate: {np.mean(outcomes):.3f}')

        plot_cols = st.columns(2)
        layout = go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        gray_color = 'rgba(49,51,63,1)'
        gray_color_tr = 'rgba(49,51,63,0.5)'

        plot_cols[0].write('#### Score growth plot')
        
        fig = go.Figure(layout=layout)
        fig.add_trace(go.Scatter(
            x=np.arange(1, len(scores)+1), y=scores,
            name='scores',
            line={'color': '#1f77b4'}
        ))
        fig.add_trace(go.Scatter(
            mode='lines',
            x=[1, len(scores)+1], y=[np.mean(scores)] * 2,
            name=f'mean score {np.mean(scores):.2f}',
            line={'color':'lightsalmon'}
        ))
        fig.add_trace(go.Scatter(
            mode='lines',
            x=[1, len(scores)+1], y=[np.median(scores)] * 2,
            name=f'median score {np.median(scores):.2f}',
            line={'color':'lightseagreen'}
        ))
        fig.add_trace(go.Scatter(
            mode='markers',
            x=[np.argmax(scores)+1], y=[np.max(scores)],
            marker={
                'color': 'mediumseagreen',
                'size': 10,
                'symbol': 'circle',
                'line': {'color': gray_color, 'width': 1}
            },
            name=f'top score {np.max(scores)}'
        ))
        fig.update_layout(
            showlegend=True,
            xaxis_title='Match number',
            margin=dict(l=0, r=0, b=0, t=0))
        fig.update_xaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr)
        fig.update_yaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr)

        plot_cols[0].plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


        plot_cols[1].write(f'#### Win/Loss/Tie plot by match')
        fig = go.Figure(layout=layout)
        fig.add_trace(go.Scatter(
            x=np.arange(1, len(outcomes)+1), y=outcomes,
            line={'color': 'lightgray', 'dash': 'dash'},
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            mode='markers',
            x=np.argwhere(outcomes == 1).flatten()+1, y=outcomes[outcomes == 1],
            text=hover_text[outcomes == 1],
            hoverinfo='text',
            marker={
                'color': 'mediumseagreen',
                'size': 10,
                'symbol': 'circle',
                'line': {'color': gray_color, 'width': 1}
            },
            name=f'Win'
        ))
        fig.add_trace(go.Scatter(
            mode='markers',
            x=np.argwhere(outcomes == 0).flatten()+1, y=outcomes[outcomes == 0],
            text=hover_text[outcomes == 0],
            hoverinfo='text',
            marker={
                'color': 'tomato',
                'size': 10,
                'symbol': 'circle',
                'line': {'color': gray_color, 'width': 1}
            },
            name=f'Loss'
        ))
        fig.add_trace(go.Scatter(
            mode='markers',
            x=np.argwhere(outcomes == 0.5).flatten()+1, y=outcomes[outcomes == 0.5],
            text=hover_text[outcomes == 0.5],
            hoverinfo='text',
            marker={
                'color': 'deepskyblue',
                'size': 10,
                'symbol': 'circle',
                'line': {'color': gray_color, 'width': 1}
            },
            name=f'Tie'
        ))
        fig.update_layout(
            showlegend=True,
            xaxis_title='Match number',
            margin=dict(l=0, r=0, b=0, t=0))
        fig.update_xaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr)
        fig.update_yaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr)

        plot_cols[1].plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


        plot_cols[0].write('#### Score changes (delta) plot')
        fig = go.Figure(layout=layout)
        fig.add_trace(go.Scatter(
            x=np.arange(1, len(scores_delta)+1), y=scores_delta,
            showlegend=False,
            line={'color': '#1f77b4'}
        ))
        fig.add_trace(go.Scatter(
            mode='markers',
            x=np.argwhere(scores_delta > 0).flatten()+1, y=scores_delta[scores_delta > 0],
            text=hover_text[scores_delta > 0],
            hoverinfo='text',
            marker={
                'color': 'mediumseagreen',
                'size': 10,
                'symbol': 'circle',
                'line': {'color': gray_color, 'width': 1}
            },
            name=f'Positive'
        ))
        fig.add_trace(go.Scatter(
            mode='markers',
            x=np.argwhere(scores_delta < 0).flatten()+1, y=scores_delta[scores_delta < 0],
            text=hover_text[scores_delta < 0],
            hoverinfo='text',
            marker={
                'color': 'tomato',
                'size': 10,
                'symbol': 'circle',
                'line': {'color': gray_color, 'width': 1}
            },
            name=f'Negative'
        ))
        fig.update_layout(
            showlegend=True, 
            xaxis_title='Match number',
            margin=dict(l=0, r=0, b=0, t=0))
        fig.update_xaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr)
        fig.update_yaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor='black')

        plot_cols[0].plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


        plot_cols[1].write('#### Win rate change by match')
        alpha_values = np.linspace(0.0, 0.1, 21)[1:]
        fig = go.Figure(layout=layout)
        wr_change = [sum(outcomes[:n])/n for n in range(1, len(outcomes)+1)]

        for alpha in alpha_values:
            fig.add_trace(go.Scatter(
                visible=False,
                name=f'win rate EMA',
                x=np.arange(1, len(outcomes)+1),
                y=ewma(wr_change, alpha=alpha),
                line={'color': '#2ca02c'}
            ))
        fig.data[len(alpha_values)//2 - 1].visible = True

        fig.add_trace(go.Scatter(
            x=np.arange(1, len(scores_delta)+1), y=wr_change,
            name='win rate',
            line={'color': '#1f77b4'}
        ))
        fig.data[-1].visible = True

        fig.add_trace(go.Scatter(
            mode='lines',
            x=[1, len(scores)+1], y=[np.mean(outcomes)] * 2,
            name=f'current winrate',
            line={'color':'lightsalmon'}
        ))
        fig.data[-1].visible = True

        steps = []
        for ind, alpha in enumerate(alpha_values):
            step = {
                'method': 'update',
                'args': [{'visible': [False]*len(fig.data)}],
                'label': f'{alpha}'
            }
            step['args'][0]['visible'][ind] = True
            step['args'][0]['visible'][-1] = True
            step['args'][0]['visible'][-2] = True
            steps.append(step)

        sliders = [dict(
            active=len(alpha_values)//2 - 1,
            steps=steps,
            currentvalue={'prefix': 'Smoothing α = '},
            pad={'b': 3, 't': 40}
        )]

        fig.update_layout(
            showlegend=True,
            xaxis_title='Match number',
            margin=dict(l=0, r=0, b=10, t=0),
            sliders=sliders)
        fig.update_xaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr)
        fig.update_yaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr, range=(min(wr_change)-0.005, 1.005))

        plot_cols[1].plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})