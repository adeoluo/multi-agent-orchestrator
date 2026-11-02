# Records docs/demo/compare.gif from a real run: `vhs docs/demo/compare.tape` from the repo root.
Output docs/demo/compare.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 560
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 22ms

Hide
Type `export PS1='$ ' && uv sync -q && source .venv/bin/activate && clear` Enter
Sleep 10s
Show
Type `python -m multi_agent_orchestrator compare` Enter
Sleep 3s
Type `python -m multi_agent_orchestrator durable` Enter
Sleep 3s
