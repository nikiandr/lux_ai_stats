import streamlit as st

from tools import escape_markdown, get_soup, get_stats

HIDE_MENU_STYLE = """
    <style>
    #MainMenu {visibility: hidden;}
    footer:after {
        content: 'Submission statistics for Lux AI competition. Made by Team ♂ GARCH ♂.';
        visibility: visible;
        display: block;
        position: relative;
        padding: 0px;
        top: 2px;
    }</style>
"""
DEFAULT_SUB_ID = 33605309
DEFAULT_COMPETITION_URL = "https://www.kaggle.com/competitions/lux-ai-season-2-neurips-stage-2"


def display_stats(sub_id):
    with st.spinner("Wait for it..."):
        try:
            soup = get_soup(DEFAULT_COMPETITION_URL, sub_id)
            stats = get_stats(soup)
            is_ok = True
        except ValueError as e:
            print(e)
            is_ok = False
            st.error("**Error:** wrong submission ID!")

    if is_ok:
        info_cols = st.columns(3)
        info_cols[0].subheader(escape_markdown(stats.team_name))
        info_cols[1].subheader(f"Current score: {stats.current_score}")
        info_cols[2].subheader(f"Current win rate: {stats.winrate:.3f}")

        plot_cols = st.columns(2)

        plot_cols[0].write("#### Score growth plot")
        fig = stats.plot_score_growth()
        plot_cols[0].plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        plot_cols[1].write("#### Win/Loss/Tie plot by match")
        fig = stats.plot_win_loss_tie()
        plot_cols[1].plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        plot_cols[0].write("#### Score changes (delta) plot")
        fig = stats.plot_score_changes()
        plot_cols[0].plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        plot_cols[1].write("#### Win rate change by match")
        fig = stats.plot_winrate_change()
        plot_cols[1].plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


if __name__ == "__main__":
    query_params = st.experimental_get_query_params()
    if "run_immediately" not in st.session_state:
        st.session_state["run_immediately"] = "id" in query_params.keys()

    st.set_page_config(
        page_title="Lux AI stats",
        page_icon="🤖",
        layout="wide",
        menu_items={"About": "Submission statistics for Lux AI competition. Made by Team ♂ GARCH ♂."},
    )

    st.markdown(HIDE_MENU_STYLE, unsafe_allow_html=True)
    st.title("Lux AI submission statistics")
    col1, col2 = st.columns(2)

    sub_id = col1.text_input("Submission ID", value=int(query_params.get("id", [DEFAULT_SUB_ID])[0]), key="sub_id")

    if col2.button("Get stats", key="run") or st.session_state.get("run_immediately"):
        st.experimental_set_query_params(**{"id": str(sub_id)})
        display_stats(sub_id)
        st.session_state["run_immediately"] = False
