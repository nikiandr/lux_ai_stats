from selenium import webdriver
from bs4 import BeautifulSoup
import numpy as np
import time


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


def ewma(x, alpha=None):
    '''
    Returns the exponentially weighted moving average of x.

    Parameters:
    -----------
    x : array-like
    alpha : float {0 <= alpha <= 1}

    Returns:
    --------
    ewma: numpy array
          the exponentially weighted moving average
    '''
    if alpha is None:
        alpha = 2 / (len(x) + 1)
    # Coerce x to an array
    x = np.array(x)
    n = x.size

    # Create an initial weight matrix of (1-alpha), and a matrix of powers
    # to raise the weights by
    w0 = np.ones(shape=(n,n)) * (1-alpha)
    p = np.vstack([np.arange(i,i-n,-1) for i in range(n)])

    # Create the weight matrix
    w = np.tril(w0**p,0)

    # Calculate the ewma
    return np.dot(w, x[::np.newaxis]) / w.sum(axis=1)