apt-get update -y
apt install -y chromium-driver
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