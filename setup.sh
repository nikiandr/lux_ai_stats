apt-get update -y
apt-get install chromium-chromedriver
apt-get install python-selenium python3-selenium
mkdir -p ~/.streamlit/
echo "\
[theme]\n\
base=\"light\"\n\
primaryColor=\"#20beff\"\n\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml