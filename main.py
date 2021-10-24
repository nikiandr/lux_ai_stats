import streamlit as st
from selenium import webdriver
from bs4 import BeautifulSoup
import numpy as np
import time
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')


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
                
    team_name = max(set(team_names), key = team_names.count)
    
    for text in text_select:
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
        
    return team_name, scores, outcomes, scores_delta

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
        team_name, scores, outcomes, scores_delta = getStats(soup)

    info_cols = st.columns(3)
    info_cols[0].subheader(team_name)
    info_cols[1].subheader(f'Current score: {scores[-1]}')
    info_cols[2].subheader(f'Current win rate: {np.mean(outcomes):.3f}')

    plot_cols = st.columns(2)
    figsize = (9, 5)

    plot_cols[0].write('Score growth plot')
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(scores, label='scores')
    ax.hlines(np.mean(scores), 0, len(scores), color='tab:orange', label=f'mean score {np.mean(scores):.2f}')
    ax.hlines(np.median(scores), 0, len(scores), color='tab:olive', label=f'median score {np.median(scores):.0f}')

    ax.scatter(np.argmax(scores), np.max(scores), color='tab:green', label=f'top score {np.max(scores)}')
    ax.legend()
    plot_cols[0].pyplot(fig)

    plot_cols[0].write('Score changes (delta) plot')
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(scores_delta)
    ax.scatter(np.argwhere(scores_delta > 0), scores_delta[scores_delta > 0], c='tab:green', label='Positive')
    ax.scatter(np.argwhere(scores_delta < 0), scores_delta[scores_delta < 0], c='tab:red', label='Negative')
    ax.hlines(0, 0, len(scores_delta), color='black', linestyles='--')
    ax.legend()
    plot_cols[0].pyplot(fig)

    plot_cols[1].write(f'Win/Loss/Tie plot by match')
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(outcomes, c='lightgray', linestyle='--')
    ax.scatter(np.argwhere(outcomes == 1), outcomes[outcomes == 1], c='tab:green', label='Win')
    ax.scatter(np.argwhere(outcomes == 0), outcomes[outcomes == 0], c='tab:red', label='Loss')
    ax.scatter(np.argwhere(outcomes == 0.5), outcomes[outcomes == 0.5], c='tab:blue', label='Tie')
    ax.hlines(np.mean(outcomes), 0, len(outcomes), color='tab:orange', label='win rate')
    ax.legend()
    plot_cols[1].pyplot(fig)

    plot_cols[1].write('Win rate change by match')
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(range(1, len(outcomes)+1), [sum(outcomes[:n])/n for n in range(1, len(outcomes)+1)], label='win rate')
    ax.hlines(np.mean(outcomes), 1, len(outcomes), color='tab:orange', label='current win rate')
    ax.legend()
    plot_cols[1].pyplot(fig)