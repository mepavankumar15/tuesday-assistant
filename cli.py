"""
Grok Assistant — Interactive CLI Chatbot
Run: python cli.py
"""
import sys
import os

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure colorama works on Windows
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    # Fallback: no colors if colorama not installed
    class _Noop:
        def __getattr__(self, _):
            return ""
    Fore = Style = _Noop()

from agent import run_agent


BANNER = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════╗
║                                                      ║
║   {Fore.YELLOW}🤖  G R O K   A S S I S T A N T{Fore.CYAN}                     ║
║   {Fore.WHITE}Alexa-like AI  •  Powered by xAI Grok{Fore.CYAN}              ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║  {Fore.GREEN}Tools:{Fore.WHITE} YouTube • Weather • Forex • News{Fore.CYAN}             ║
║  {Fore.GREEN}Commands:{Fore.WHITE} 'clear' reset  |  'exit' quit{Fore.CYAN}             ║
╚══════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""


def main():
    print(BANNER)

    chat_history: list[dict] = []

    while True:
        try:
            user_input = input(f"{Fore.GREEN}You ❯ {Style.RESET_ALL}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Fore.YELLOW}Goodbye! 👋{Style.RESET_ALL}")
            break

        if not user_input:
            continue

        # --- Special commands ---
        if user_input.lower() in ("exit", "quit", "bye"):
            print(f"\n{Fore.YELLOW}Goodbye! 👋{Style.RESET_ALL}")
            break

        if user_input.lower() == "clear":
            chat_history.clear()
            os.system("cls" if os.name == "nt" else "clear")
            print(BANNER)
            print(f"{Fore.CYAN}Chat history cleared.{Style.RESET_ALL}\n")
            continue

        if user_input.lower() == "help":
            print(f"""
{Fore.CYAN}Available commands:{Style.RESET_ALL}
  {Fore.GREEN}clear{Style.RESET_ALL}   — Reset conversation history
  {Fore.GREEN}exit{Style.RESET_ALL}    — Quit the assistant
  {Fore.GREEN}help{Style.RESET_ALL}    — Show this help message

{Fore.CYAN}Example prompts:{Style.RESET_ALL}
  • "What's the weather in Mumbai?"
  • "Play Coldplay Yellow"
  • "Convert 500 USD to EUR"
  • "Latest news on AI"
  • "Top technology headlines"
  • "What's the capital of Australia?"
""")
            continue

        # --- Send to agent ---
        print(f"{Fore.BLUE}⏳ Thinking...{Style.RESET_ALL}", end="\r")

        try:
            response = run_agent(user_input, chat_history)
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}\n")
            continue

        # Clear the "Thinking..." line
        print(" " * 40, end="\r")

        # --- Handle YouTube actions embedded in response ---
        display_text = response
        if '{"action": "play_youtube"' in response:
            import json
            try:
                start = response.rfind('{"action": "play_youtube"')
                end = response.find("}", start) + 1
                action_json = json.loads(response[start:end])
                video_id = action_json.get("video_id", "")
                title = action_json.get("title", "")
                display_text = response[:start].strip()
                if video_id:
                    display_text += (
                        f"\n\n{Fore.MAGENTA}▶  Now Playing: {title}"
                        f"\n   🔗 https://www.youtube.com/watch?v={video_id}{Style.RESET_ALL}"
                    )
            except Exception:
                pass

        print(f"\n{Fore.CYAN}Grok ❯ {Style.RESET_ALL}{display_text}\n")

        # --- Update history ---
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
