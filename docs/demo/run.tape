# Records docs/demo/run.gif from a real run: `vhs docs/demo/run.tape` from the repo root.
Output docs/demo/run.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 480
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 22ms

Hide
Type `export PS1='$ ' && uv sync -q && source .venv/bin/activate && clear` Enter
Sleep 10s
Show
Type `python -m multi_agent_orchestrator run "research the topic and then write the report"` Enter
Sleep 3.5s
