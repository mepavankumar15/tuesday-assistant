"""
Automated CLI Test Runner for Alex Assistant (Multi-Agent System)
Runs test queries across:
1. Supervisor (General Conversation directly without delegation)
2. Finance & Weather Specialist Sub-Agent (`get_weather` + `get_forex_rate`)
3. Media Specialist Sub-Agent (`search_youtube`)
4. News Specialist Sub-Agent (`get_top_headlines`)
"""
import sys
import colorama
from colorama import Fore, Style
from agents.supervisor_agent import run_agent

colorama.init(autoreset=True)
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

def run_test(title, query):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}🧪 TEST: {title}")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.WHITE}Query ❯ {query}\n")
    
    try:
        response = run_agent(query, [])
        print(f"{Fore.GREEN}Alex ❯ {Style.RESET_ALL}{response}\n")
        print(f"{Fore.GREEN}✔ Test Passed!{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}✖ Test Failed with error: {e}{Style.RESET_ALL}")
        return False

def main():
    print(f"{Fore.MAGENTA}\n🚀 Starting Multi-Agent Architecture CLI Tests...\n")
    
    tests = [
        ("General Conversation (No Delegation)", "Hello Alex! Who are you and how are you feeling today?"),
        ("Finance & Weather Specialist Delegation", "What is the current weather in Sydney, Australia?"),
        ("Media Specialist Delegation", "Search YouTube and find the song Yellow by Coldplay"),
        ("News Specialist Delegation", "What are the top technology news headlines today?")
    ]
    
    passed = 0
    for title, query in tests:
        if run_test(title, query):
            passed += 1
            
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.WHITE}📊 Test Results Summary: {Fore.GREEN}{passed}/{len(tests)} tests passed successfully!")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    if passed == len(tests):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
