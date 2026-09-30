Optional browser-behaviour check (needs Node.js):

    cd ui_check
    npm init -y
    npm install jsdom
    (start the app in another terminal: python run.py)
    node ui.js

It loads the real dashboard, clicks Send / Attack / Receive through the page's
own JavaScript and checks the status chips, steps, verdict boxes and log.
