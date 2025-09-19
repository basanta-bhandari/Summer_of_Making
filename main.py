

import json
import random
import datetime
import os
import sys
from utils import *
from game_data import *
from save_system import *

def main():
    clear_terminal()
    print("Starting Terminal Speil...")
    
    # GLOBAL VARIABLES/DEFINES
    start_time = datetime.datetime.now()
    completed_quests = []
    time_of_day = "morning"
    weather = "clear"
    gold = 500  # Enough to start with basic items but still need quests for powerful allies
    cart = ["healing potion"]
    game_ended = False
    days_passed = 0
    german_arrival_day = random.randint(5, 9)  # Random arrival between 5-9 days
    reputation = 0  # New reputation system for unlocking allies
    energy = 100  # New energy system
    quests_needed_for_battle = 2  # Must complete some quests before final battle
    player_name = ""
    shop_visited = False  # Track if player has visited shop
    
    # Nickname tracking
    nickname_stats = {
        'quests': 0,
        'gold_spent': 0,
        'deaths_avoided': 0,
        'successful_raids': 0,
        'current_nickname': None
    }
    
    # MAIN CODE
    print("""
    '########:'########:'########::'##::::'##:'####:'##::: ##::::'###::::'##:::::::::::'######::'########::'########:'####:'##:::::::
    ... ##..:: ##.....:: ##.... ##: ###::'###:. ##:: ###:: ##:::'## ##::: ##::::::::::'##... ##: ##.... ##: ##.....::. ##:: ##:::::::
    ::: ##:::: ##::::::: ##:::: ##: ####'####:: ##:: ####: ##::'##:. ##:: ##:::::::::: ##:::..:: ##:::: ##: ##:::::::: ##:: ##:::::::
    ::: ##:::: ######::: ########:: ## ### ##:: ##:: ## ## ##:'##:::. ##: ##::::::::::. ######:: ########:: ######:::: ##:: ##:::::::
    ::: ##:::: ##...:::: ##.. ##::: ##. #: ##:: ##:: ##. ####: #########: ##:::::::::::..... ##: ##.....::: ##...::::: ##:: ##:::::::
    ::: ##:::: ##::::::: ##::. ##:: ##:.:: ##:: ##:: ##:. ###: ##.... ##: ##::::::::::'##::: ##: ##:::::::: ##:::::::: ##:: ##:::::::
    ::: ##:::: ########: ##:::. ##: ##:::: ##:'####: ##::. ##: ##:::: ##: ########::::. ######:: ##:::::::: ########:'####: ########:
    :::..:::::........::..:::::..::..:::::..::....::..::::..::..:::::..::........::::::......:::..:::::::::........::....::........::
    """)
    
    # Check if any save files exist
    save_manager = SaveSlotManager(max_slots=5)   
    save_info = save_manager.get_all_save_info()

    has_saves = any(info['exists'] for info in save_info)
    if has_saves:
        load_choice = get_valid_input("Found saved games! Load one? (y/n): ", ['y', 'n'])
        if load_choice == 'y':
            save_data = handle_load_menu(save_manager)
            if save_data:
                player_name = save_data.get('player_name', '')
                gold = save_data.get('gold', 10000)
                cart = save_data.get('cart', ["healing potion"])
                completed_quests = save_data.get('completed_quests', [])
                days_passed = save_data.get('days_passed', 0)
                time_of_day = save_data.get('time_of_day', 'morning')
                weather = save_data.get('weather', 'clear')
                german_arrival_day = save_data.get('german_arrival_day', random.randint(5, 9))
                shop_visited = save_data.get('shop_visited', False)
                reputation = save_data.get('reputation', 0)  # Load reputation from save
                energy = save_data.get('energy', 100)  # Load energy from save
                # Load nickname stats
                if 'nickname_stats' in save_data:
                    nickname_stats.update(save_data['nickname_stats'])
                print(f"Welcome back, Sir {player_name}!")
    
    if not player_name: 
        # Get start game input
        start_choice = get_valid_input("Shall we begin our adventure? (y/n): ", ['y', 'n'])
        if start_choice == 'n':
            print("Game cancelled!")
            sys.exit()

        # Get player name
        player_name = input("Enter character name: ").strip()
        if not player_name:
            player_name = "Hero"

    # Show opening intro
    show_opening_intro(player_name)
    
    # Show current time
    current_hour = datetime.datetime.now().hour
    current_time = datetime.datetime.now()
    print(f"Adventure starts at: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Show appropriate atmosphere based on real time, but start game in morning
    if days_passed == 0:
        time_of_day = "morning"  # Always start in morning for gameplay purposes
        # Just display the current time atmosphere for immersion
        current_time_desc = ""
        if current_hour < 6:
            current_time_desc = "It's early in the night"
        elif current_hour < 12:
            current_time_desc = "It's morning"
        elif current_hour < 18:
            current_time_desc = "It's afternoon"
        else:
            current_time_desc = "It's evening"
        print(f"\n{current_time_desc}, but your adventure begins as the sun rises...")

    # Main game loop
    while not game_ended:
        # Show daily interlude at the start of each day
        if time_of_day == "morning":
            show_daily_interlude(days_passed + 1, player_name)
        
        # Check if Germans have arrived
        if days_passed >= german_arrival_day:
            show_final_battle_intro(player_name)
            
            battle_choice = get_valid_input("Face the Germans in battle? (yes/flee): ", ['yes', 'flee'])
            if battle_choice == 'flee':
                print("You flee the village in shame...")
                reputation -= 2  # Lose reputation for cowardice
                print("You lost 2 reputation for your cowardice!")
                print("COWARD'S ENDING: The villagers are left to their fate.")
                print("Thanks for playing!")
                game_ended = True
                break
            else:
                game_ended = handle_final_battle(cart, player_name, completed_quests, days_passed)
                break

        # Weather changes
        if random.random() < 0.2:
            old_weather = weather
            weather = random.choice(["clear", "cloudy", "rainy", "foggy"])
            if weather != old_weather:
                print(f"\nThe weather changes to {weather}...")

        # Show atmosphere and status
        show_atmosphere(time_of_day, weather)
        if time_of_day == "evening":
            print("\nThe sun is setting. You should find a place to rest soon...")
        elif time_of_day == "night":
            print("\nIt's dark. Most activities are unavailable until morning.")
        
        # Show main menu with all stats
        print("\n╔════════════════════════ STATUS ═══════════════════════╗")
        print(f"║  Day: {days_passed + 1:<2}    Time: {time_of_day.title():<8}    Weather: {weather:<6}         ║")
        print("╠═══════════════════════════════════════════════════════╣")
        print(f"║  Gold: {gold:<4}    Energy: {energy:>3}/100    Reputation: {reputation:<2}      ║")
        print(f"║  Items: {len(cart):<2}     Quests: {len(completed_quests):<2}    Germans arrive in:{german_arrival_day - days_passed:>2} days║")
        print("╠═══════════════════════════════════════════════════════╣")
        print("║                    ACTIONS AVAILABLE                  ║")
        print("╟───────────────────────────────────────────────────────╢")
        print("║  [i]    Check Inventory                               ║")
        energy_color = '\033[91m' if energy < 30 else '\033[92m'  # Red if tired, green if ok
        print(f"║  [q]    Village Quests          {energy_color}(30 energy)\033[0m{' [TOO TIRED]' if energy < 30 else '          '} ║")
        energy_color = '\033[91m' if energy < 20 else '\033[92m'
        print(f"║  [s]    Visit Shops             {energy_color}(20 energy)\033[0m{' [TOO TIRED]' if energy < 20 else '          '} ║")
        energy_color = '\033[91m' if energy < 50 else '\033[92m'
        print(f"║  [b]    Battle Germans          {energy_color}(50 energy)\033[0m{' [TOO TIRED]' if energy < 50 else '          '} ║")
        if days_passed + 1 >= 3:  # Check current day number
            energy_color = '\033[91m' if energy < 50 else '\033[92m'
            print(f"║  [r]    Raid German Camp        {energy_color}(50 energy)\033[0m{' [TOO TIRED]' if energy < 50 else '      '} ║")
        else:
            print("║  [r]    \033[90m[unlocks on day 3]\033[0m                            ║")
        print("║  [save] Save Game                                     ║")
        print("║  [x]    Quit Game                                     ║")
        if energy < 80:  # Show sleep option when tired
            print(f"║  [sleep] Rest & Recover         (+30 energy)         ║")
        print("╚═══════════════════════════════════════════════════════╝")
        
        # Random events
        if random.random() < 0.1:
            event = random.choice(RANDOM_EVENTS)
            print(f"\n--- RANDOM EVENT ---")
            print(f"{event['event']}")
            gold += event['gold']
            print(f"You gained {event['gold']} gold!")
            
            # 30% chance to gain reputation from random events
            if random.random() < 0.3:
                reputation += 1
                print("\033[1;36mYour good deed earned you 1 reputation!\033[0m")  # Cyan highlight for consistency
            
            input("Press Enter to continue...")
            
        # Get main menu choice
        # Only allow sleep after shopping at least once
        available_options = ['i', 'q', 's', 'b', 'r', 'save', 'x']
        if shop_visited:
            available_options.append('sleep')
        
        main_choice = get_valid_input("Choose an option: ", available_options)
        
        # Force sleep if energy is too low (below lowest action requirement)
        if energy < 20:  # 20 is minimum for shopping
            print("\nYou're exhausted and must rest...")
            input("Press Enter to sleep...")
            time_of_day = handle_sleep(player_name)
            energy = min(100, energy + 30)  # Restore 30 energy
            days_passed += 1
            continue
            
        if main_choice == 'sleep':
            time_of_day = handle_sleep(player_name)
            energy = min(100, energy + 30)  # Restore 30 energy
            days_passed += 1
            continue
            
        if main_choice == 'x':
            save_choice = get_valid_input(f"Save before quitting? (y/n): ", ['y', 'n'])
            if save_choice == 'y':
                handle_save_menu(save_manager, player_name, gold, cart, completed_quests, 
                        days_passed, time_of_day, weather, german_arrival_day, start_time, 
                        nickname_stats=nickname_stats, reputation=reputation, energy=energy)
                print(f"Thanks for playing, Sir {player_name}!")
            game_ended = True
            
        elif main_choice == 'save':
            handle_save_menu(save_manager, player_name, gold, cart, completed_quests, 
                            days_passed, time_of_day, weather, german_arrival_day, start_time,
                            nickname_stats=nickname_stats, reputation=reputation, energy=energy)

            
        elif main_choice == 'i':
            show_inventory(gold, cart, completed_quests, nickname_stats, reputation, energy)
            
        elif main_choice == 'q':  # Village Quests
            # Quest selection and completion moved from shop to here
            quest_result = handle_quest_selection(gold, cart, completed_quests, player_name, reputation)
            
            # Energy check for the selected quest
            if quest_result.get('energy_cost', 0) > 0:
                if energy < quest_result['energy_cost']:
                    print(f"You're too tired for this quest! (Need {quest_result['energy_cost']} energy)")
                    print("Get some rest first.")
                    input("Press Enter to continue...")
                    continue
                    
                energy -= quest_result['energy_cost']  # Deduct quest's specific energy cost
            if quest_result['completed']:
                reputation_gain = 1
                reputation += reputation_gain
                print(f"\nYou gained {reputation_gain} reputation for completing the quest!")
                completed_quests = quest_result['completed_quests']
                nickname_stats['quests'] = len(completed_quests)
                # Check for new nickname
                nickname_message = update_nickname(nickname_stats)
                if nickname_message:
                    print(nickname_message)
            
            gold = quest_result['gold']
            cart = quest_result['cart']
            
            # Advance time after completing a quest
            time_of_day = advance_time(time_of_day)
            if time_of_day == "morning":
                days_passed += 1
            
        elif main_choice == 'r':
            if days_passed + 1 >= 3:  # Check actual day number
                if energy < 50:
                    print("You're too tired to go raiding! Get some sleep first.")
                    input("Press Enter to continue...")
                    continue
                    
                energy -= 50  # Raiding costs lots of energy
                raid_result = handle_german_raid(cart, player_name)  # Removed weather parameter
                if raid_result == 'victory':
                    german_arrival_day += 2
                    nickname_stats['successful_raids'] += 1
                    reputation += 1  # Gain reputation for successful raid
                    print("Your successful raid has delayed the German attack by 2 days!")
                    print("You gained 1 reputation for your bravery!")
                    nickname_message = update_nickname(nickname_stats)
                    if nickname_message:
                        print(nickname_message)
                elif raid_result == 'death':
                    # Small reputation gain for bravely attempting a raid, even if it failed
                    reputation += 1
                    print("You gained 1 reputation for your brave attempt!")
                    death_handled = handle_death_alternatives(cart, player_name)
                    if death_handled:
                        nickname_stats['deaths_avoided'] += 1
                        nickname_message = update_nickname(nickname_stats)
                        if nickname_message:
                            print(nickname_message)
                    else:
                        game_ended = True
                        break
                days_passed += 1
            else:
                print("You need to wait until day 3 before attempting a raid!")
                print(f"Current day: {days_passed + 1}/3")
                input("Press Enter to continue...")
                
        elif main_choice == 'b':
            # Check if it's too dark to battle
            if not check_time_restrictions(time_of_day, "battle"):
                continue
                
            # Check battle ready
            battle_items = ['brian', 'black knight', 'grim reaper', 'god', 'mage', 'nordic', 'biccus diccus', 'raddragonore']
            has_ally = any(item in cart for item in battle_items)
            
            if not has_ally:
                print("You need a battle companion before you can face the Germans!")
                print("Visit the Freelancers Guild to recruit an ally.")
                input("Press Enter to continue...")
                continue
                
            if len(completed_quests) < quests_needed_for_battle:
                print(f"You need to complete at least {quests_needed_for_battle} quests before challenging the Germans!")
                print(f"Quests completed: {len(completed_quests)}/{quests_needed_for_battle}")
                input("Press Enter to continue...")
                continue
            
            if energy >= 50:
                print("You decide to face the Germanic threat head-on!")
                game_ended = handle_final_battle(cart, player_name, completed_quests, days_passed)
            else:
                print("You need allies or powerful weapons before you can battle the Germans!")
                print("Visit the Freelancers Guild or Antique Shop to prepare.")
                input("Press Enter to continue...")
                
        elif main_choice == 's':
            # Check if shops are open
            if not check_time_restrictions(time_of_day, "shop"):
                continue
                
            # Check energy
            if energy < 20:
                print("You're too tired to go shopping! Get some sleep first.")
                input("Press Enter to continue...")
                continue
            
            energy -= 20  # Shopping costs energy
                
            # Shop selection
            shop_result = handle_shop_selection(gold, cart, completed_quests, player_name, nickname_stats, reputation)
            # Track gold spent
            if gold > shop_result['gold']:
                nickname_stats['gold_spent'] += (gold - shop_result['gold'])
            gold = shop_result['gold']
            cart = shop_result['cart'] 
            # Shop actions are now purely for buying/selling items
            
            if shop_result['game_ended']:
                game_ended = True
                break
            
            # Mark that shopping has occurred and advance time
            shop_visited = True
            time_of_day = advance_time(time_of_day)
            if time_of_day == "morning":
                days_passed += 1

if __name__ == "__main__":
    main()