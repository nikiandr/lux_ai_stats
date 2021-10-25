import streamlit as st
from selenium import webdriver
from bs4 import BeautifulSoup
import numpy as np
import time
import plotly.graph_objs as go
import plotly.express as px

def getSoup(sub_id):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(options=options)

    URL = 'https://www.kaggle.com/c/lux-ai-2021/submissions?dialog=episodes-submission-'

    print('Loading submission page...')
    browser.get(URL + str(sub_id))
    time.sleep(2)

    print('Scrolling results...')
    scrolling_element = browser.find_element(
        webdriver.common.by.By.XPATH,
        "//div[@class='mdc-dialog__surface']")
    for k in range(100):
        browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrolling_element)
    time.sleep(1)

    print('Parsing page...')
    html_source = browser.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    print('Done!')
    
    return soup


def getStats(soup):
    outcomes = []
    scores = []
    scores_delta = []
    hover_text = []
    
    text_select = []
    team_names = []
    
    for span in soup.select('span[class*="sc-"]'):
        text = span.get_text()
        if 'vs' in text and '[' in text and 'ago' not in text:
            text_select.append(text)
            for part in text.split(' vs '):
                part_split = part.split(' ')
                team_name = ' '.join(part_split[1:-2])
                team_names.append(team_name)
                
    team_name = max(set(team_names), key=team_names.count)
    
    for text in text_select:
        if 'Validation' not in text:
            hover_text.append(text.replace(' vs ', '<br>'))
        for part in text.split(' vs '):
            if team_name in part:
                result = part.split(' ')
                delta = result[-1].strip('()+')
                if delta != 'Validation':
                    scores.append(int(result[-2]))
                    scores_delta.append(int(delta))
                    outcome = result[0].strip('[]')
                    if outcome == 'Win':
                        outcomes.append(1)
                    elif outcome == 'Loss':
                        outcomes.append(0)
                    else: # Tie
                        outcomes.append(0.5)
    
    scores.insert(0, scores[0] + scores_delta[0])
    scores = np.array(scores[::-1])
    outcomes = np.array(outcomes[::-1])
    scores_delta = np.array(scores_delta[::-1])
    hover_text = np.array(hover_text[::-1])

    return team_name, scores, outcomes, scores_delta, hover_text

st.set_page_config(page_title='Lux AI stats', 
                   page_icon='🤖',
                   layout='wide',
                   menu_items={
                       'About': 'Submission statistics for Lux AI competition. Made by Yalikesifulei from Team ♂ GARCH ♂.'
                   })

st.title('Lux AI submission statistics')
col1, col2 = st.columns(2)

sub_id = col1.number_input('Submission ID', value=23380527, step=1, key='sub_id')

if col2.button('Get stats', key='run'):
    with st.spinner('Wait for it...'):
        soup = getSoup(sub_id)
        team_name, scores, outcomes, scores_delta, hover_text = getStats(soup)

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
        name='scores'
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
        marker_symbol='circle', marker_size=10, marker_color='palegreen',
        name=f'top score {np.max(scores)}'
    ))
    fig.update_layout(
        showlegend=True, 
        margin=dict(l=0, r=0, b=0, t=0))
    fig.update_xaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, range=(1, len(scores)+1))
    fig.update_yaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr)

    plot_cols[0].plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


    plot_cols[1].write(f'#### Win/Loss/Tie plot by match')
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(
        x=np.arange(1, len(outcomes)+1), y=outcomes,
        name='scores', line={'color': 'lightgray', 'dash': 'dash'}
    ))
    fig.add_trace(go.Scatter(
        mode='markers',
        x=np.argwhere(outcomes == 1).flatten()+1, y=outcomes[outcomes == 1],
        text=hover_text[outcomes == 1],
        hoverinfo='text',
        marker_symbol='circle', marker_size=10, marker_color='palegreen',
        name=f'Win'
    ))
    fig.add_trace(go.Scatter(
        mode='markers',
        x=np.argwhere(outcomes == 0).flatten()+1, y=outcomes[outcomes == 0],
        text=hover_text[outcomes == 0],
        hoverinfo='text',
        marker_symbol='circle', marker_size=10, marker_color='tomato',
        name=f'Loss'
    ))
    fig.add_trace(go.Scatter(
        mode='markers',
        x=np.argwhere(outcomes == 0.5).flatten()+1, y=outcomes[outcomes == 0.5],
        marker_symbol='circle', marker_size=10, marker_color='deepskyblue',
        text=hover_text[outcomes == 0.5],
        hoverinfo='text',
        name=f'Tie'
    ))
    fig.update_layout(
        showlegend=True,
        margin=dict(l=0, r=0, b=0, t=0))
    fig.update_xaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, range=(1, len(scores)+1))
    fig.update_yaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr)

    plot_cols[1].plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


    plot_cols[0].write('#### Score changes (delta) plot')
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(
        x=np.arange(1, len(scores_delta)+1), y=scores_delta,
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        mode='markers',
        x=np.argwhere(scores_delta > 0).flatten()+1, y=scores_delta[scores_delta > 0],
        text=hover_text[scores_delta > 0],
        hoverinfo='text',
        marker_symbol='circle', marker_size=10, marker_color='palegreen',
        name=f'Positive'
    ))
    fig.add_trace(go.Scatter(
        mode='markers',
        x=np.argwhere(scores_delta < 0).flatten()+1, y=scores_delta[scores_delta < 0],
        text=hover_text[scores_delta < 0],
        hoverinfo='text',
        marker_symbol='circle', marker_size=10, marker_color='tomato',
        name=f'Negative'
    ))
    fig.update_layout(
        showlegend=True, 
        margin=dict(l=0, r=0, b=0, t=0))
    fig.update_xaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, range=(1, len(scores)+1))
    fig.update_yaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor='black')

    plot_cols[0].plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


    plot_cols[1].write('#### Win rate change by match')
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(
        x=np.arange(1, len(scores_delta)+1), y=[sum(outcomes[:n])/n for n in range(1, len(outcomes)+1)],
        name='win rate'
    ))
    fig.add_trace(go.Scatter(
        mode='lines',
        x=[1, len(scores)+1], y=[np.mean(outcomes)] * 2,
        name=f'current winrate {np.mean(outcomes):.3f}',
        line={'color':'lightsalmon'}
    ))
    fig.update_layout(
        showlegend=True, 
        margin=dict(l=0, r=0, b=0, t=0))
    fig.update_xaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, range=(1, len(scores)+1))
    fig.update_yaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr)

    plot_cols[1].plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})