import time
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import plotly.graph_objs as go
from bs4 import BeautifulSoup
from selenium import webdriver


layout = go.Layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
gray_color = "rgba(49,51,63,1)"
gray_color_tr = "rgba(49,51,63,0.5)"


@dataclass
class TeamStats:
    team_name: str
    scores: Sequence
    outcomes: Sequence
    scores_delta: Sequence
    hover_text: Sequence

    @property
    def current_score(self):
        return self.scores[-1]

    @property
    def winrate(self):
        return np.mean(self.outcomes)

    def plot_score_growth(self):
        fig = go.Figure(layout=layout)
        fig.add_trace(go.Scatter(x=np.arange(1, len(self.scores) + 1), y=self.scores, name="scores", line={"color": "#1f77b4"}))
        fig.add_trace(
            go.Scatter(
                mode="lines",
                x=[1, len(self.scores) + 1],
                y=[np.mean(self.scores)] * 2,
                name=f"mean score {np.mean(self.scores):.2f}",
                line={"color": "lightsalmon"},
            )
        )
        fig.add_trace(
            go.Scatter(
                mode="lines",
                x=[1, len(self.scores) + 1],
                y=[np.median(self.scores)] * 2,
                name=f"median score {np.median(self.scores):.2f}",
                line={"color": "lightseagreen"},
            )
        )
        fig.add_trace(
            go.Scatter(
                mode="markers",
                x=[np.argmax(self.scores) + 1],
                y=[np.max(self.scores)],
                marker={"color": "mediumseagreen", "size": 10, "symbol": "circle", "line": {"color": gray_color, "width": 1}},
                name=f"top score {np.max(self.scores)}",
            )
        )
        fig.update_layout(showlegend=True, xaxis_title="Match number", margin=dict(l=0, r=0, b=0, t=0))
        fig.update_xaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr)
        fig.update_yaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr)
        return fig

    def plot_win_loss_tie(self):
        fig = go.Figure(layout=layout)
        fig.add_trace(
            go.Scatter(
                x=np.arange(1, len(self.outcomes) + 1), y=self.outcomes, line={"color": "lightgray", "dash": "dash"}, showlegend=False
            )
        )
        fig.add_trace(
            go.Scatter(
                mode="markers",
                x=np.argwhere(self.outcomes == 1).flatten() + 1,
                y=self.outcomes[self.outcomes == 1],
                text=self.hover_text[self.outcomes == 1],
                hoverinfo="text",
                marker={"color": "mediumseagreen", "size": 10, "symbol": "circle", "line": {"color": gray_color, "width": 1}},
                name="Win",
            )
        )
        fig.add_trace(
            go.Scatter(
                mode="markers",
                x=np.argwhere(self.outcomes == 0).flatten() + 1,
                y=self.outcomes[self.outcomes == 0],
                text=self.hover_text[self.outcomes == 0],
                hoverinfo="text",
                marker={"color": "tomato", "size": 10, "symbol": "circle", "line": {"color": gray_color, "width": 1}},
                name="Loss",
            )
        )
        fig.add_trace(
            go.Scatter(
                mode="markers",
                x=np.argwhere(self.outcomes == 0.5).flatten() + 1,
                y=self.outcomes[self.outcomes == 0.5],
                text=self.hover_text[self.outcomes == 0.5],
                hoverinfo="text",
                marker={"color": "deepskyblue", "size": 10, "symbol": "circle", "line": {"color": gray_color, "width": 1}},
                name="Tie",
            )
        )
        fig.update_layout(showlegend=True, xaxis_title="Match number", margin=dict(l=0, r=0, b=0, t=0))
        fig.update_xaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr)
        fig.update_yaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr)
        return fig

    def plot_score_changes(self):
        fig = go.Figure(layout=layout)
        fig.add_trace(
            go.Scatter(x=np.arange(1, len(self.scores_delta) + 1), y=self.scores_delta, showlegend=False, line={"color": "#1f77b4"})
        )
        fig.add_trace(
            go.Scatter(
                mode="markers",
                x=np.argwhere(self.scores_delta > 0).flatten() + 1,
                y=self.scores_delta[self.scores_delta > 0],
                text=self.hover_text[self.scores_delta > 0],
                hoverinfo="text",
                marker={"color": "mediumseagreen", "size": 10, "symbol": "circle", "line": {"color": gray_color, "width": 1}},
                name="Positive",
            )
        )
        fig.add_trace(
            go.Scatter(
                mode="markers",
                x=np.argwhere(self.scores_delta < 0).flatten() + 1,
                y=self.scores_delta[self.scores_delta < 0],
                text=self.hover_text[self.scores_delta < 0],
                hoverinfo="text",
                marker={"color": "tomato", "size": 10, "symbol": "circle", "line": {"color": gray_color, "width": 1}},
                name="Negative",
            )
        )
        fig.update_layout(showlegend=True, xaxis_title="Match number", margin=dict(l=0, r=0, b=0, t=0))
        fig.update_xaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr)
        fig.update_yaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor="black")
        return fig

    def plot_winrate_change(self):
        alpha_values = np.linspace(0.0, 0.1, 21)[1:]
        fig = go.Figure(layout=layout)
        wr_change = [sum(self.outcomes[:n]) / n for n in range(1, len(self.outcomes) + 1)]

        for alpha in alpha_values:
            fig.add_trace(
                go.Scatter(
                    visible=False,
                    name="win rate EMA",
                    x=np.arange(1, len(self.outcomes) + 1),
                    y=ewma(wr_change, alpha=alpha),
                    line={"color": "#2ca02c"},
                )
            )
        fig.data[len(alpha_values) // 2 - 1].visible = True

        fig.add_trace(go.Scatter(x=np.arange(1, len(self.scores_delta) + 1), y=wr_change, name="win rate", line={"color": "#1f77b4"}))
        fig.data[-1].visible = True

        fig.add_trace(
            go.Scatter(
                mode="lines",
                x=[1, len(self.scores) + 1],
                y=[np.mean(self.outcomes)] * 2,
                name="current winrate",
                line={"color": "lightsalmon"},
            )
        )
        fig.data[-1].visible = True

        steps = []
        for ind, alpha in enumerate(alpha_values):
            step = {"method": "update", "args": [{"visible": [False] * len(fig.data)}], "label": f"{alpha}"}
            step["args"][0]["visible"][ind] = True
            step["args"][0]["visible"][-1] = True
            step["args"][0]["visible"][-2] = True
            steps.append(step)

        sliders = [dict(active=len(alpha_values) // 2 - 1, steps=steps, currentvalue={"prefix": "Smoothing α = "}, pad={"b": 3, "t": 40})]

        fig.update_layout(showlegend=True, xaxis_title="Match number", margin=dict(l=0, r=0, b=10, t=0), sliders=sliders)
        fig.update_xaxes(showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr)
        fig.update_yaxes(
            showline=True, linecolor=gray_color, gridcolor=gray_color_tr, zerolinecolor=gray_color_tr, range=(min(wr_change) - 0.005, 1.005)
        )
        return fig


def get_soup(sub_id):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    browser = webdriver.Chrome(options=options)

    URL = "https://www.kaggle.com/competitions/lux-ai-season-2/leaderboard?dialog=episodes-submission-"

    print("Loading submission page...")
    browser.get(URL + str(sub_id))
    time.sleep(2)

    print("Scrolling results...")
    scrolling_element = browser.find_element(webdriver.common.by.By.XPATH, "//div[@class='mdc-dialog__surface']")
    for k in range(100):
        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrolling_element)
    time.sleep(1)

    print("Parsing page...")
    html_source = browser.page_source
    soup = BeautifulSoup(html_source, "html.parser")
    print("Done!")

    return soup


def get_stats(soup):
    outcomes = []
    scores = []
    scores_delta = []
    hover_text = []

    text_select = []
    team_names = []

    for span in soup.select('span[class*="sc-"]'):
        text = span.get_text()
        if "vs" in text and "[" in text and "ago" not in text:
            text_select.append(text)
            for part in text.split(" vs "):
                part_split = part.split(" ")
                team_name = " ".join(part_split[1:-2])
                team_names.append(team_name)

    team_name = max(set(team_names), key=team_names.count)

    for text in text_select:
        for part in text.split(" vs "):
            if team_name in part:
                result = part.split(" ")
                delta = result[-1].strip("()+")
                if delta != "Validation" and delta != "-NaN":
                    hover_text.append(text.replace(" vs ", "<br>"))
                    scores.append(int(result[-2]))
                    scores_delta.append(int(delta))
                    outcome = result[0].strip("[]")
                    if outcome == "Win":
                        outcomes.append(1)
                    elif outcome == "Loss":
                        outcomes.append(0)
                    else:  # Tie
                        outcomes.append(0.5)

    scores.insert(0, scores[0] + scores_delta[0])
    scores = np.array(scores[::-1])
    outcomes = np.array(outcomes[::-1])
    scores_delta = np.array(scores_delta[::-1])
    hover_text = np.array(hover_text[::-1])

    return TeamStats(team_name, scores, outcomes, scores_delta, hover_text)


def ewma(x, alpha=None):
    """
    Returns the exponentially weighted moving average of x.

    Parameters:
    -----------
    x : array-like
    alpha : float {0 <= alpha <= 1}

    Returns:
    --------
    ewma: numpy array
          the exponentially weighted moving average
    """
    if alpha is None:
        alpha = 2 / (len(x) + 1)
    # Coerce x to an array
    x = np.array(x)
    n = x.size

    # Create an initial weight matrix of (1-alpha), and a matrix of powers
    # to raise the weights by
    w0 = np.ones(shape=(n, n)) * (1 - alpha)
    p = np.vstack([np.arange(i, i - n, -1) for i in range(n)])

    # Create the weight matrix
    w = np.tril(w0**p, 0)

    # Calculate the ewma
    return np.dot(w, x[:: np.newaxis]) / w.sum(axis=1)


def escape_markdown(s):
    markdown_escape_map = {"_": "\\_", "*": "\\*"}
    for search, replace in markdown_escape_map.items():
        s = s.replace(search, replace)
    return s
