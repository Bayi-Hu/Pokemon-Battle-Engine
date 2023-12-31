'''
Project Page - [https://Pokemon-PythonRed.github.io]
Repository   - [https://github.com/Pokemon-PythonRed/Pokemon-PythonRed]
License      - MIT
'''

# import system modules
from json import dumps, loads
from math import ceil, floor, sqrt
from os import path, system
from random import choice, choices, randint
from sys import exit as sysexit, path as syspath, stdout
from time import sleep, time
from typing import Optional, Union


# abort function to be used before functions that require libraries
def abort_early() -> None:
    input(
        'It appears that you are using an unsupported operating system. Please use Windows or Linux.\n\nPress Enter to exit.')
    system.exit()


# import getch according to system
try:
    from msvcrt import getch, getche  # type: ignore
except ImportError:
    try:
        from getch import getch, getche  # type: ignore
    except ImportError:
        abort_early()

# type colours
colours = {
    'NORMAL': '\x1b[0;0m',
    'FIRE': '\x1b[38;5;196m',
    'WATER': '\x1b[38;5;027m',
    'GRASS': '\x1b[38;5;082m',
    'ELECTRIC': '\x1b[38;5;184m',
    'ICE': '\x1b[38;5;159m',
    'FIGHTING': '\x1b[38;5;167m',
    'POISON': '\x1b[38;5;135m',
    'GROUND': '\x1b[38;5;215m',
    'FLYING': '\x1b[38;5;183m',
    'PSYCHIC': '\x1b[38;5;198m',
    'BUG': '\x1b[38;5;028m',
    'ROCK': '\x1b[38;5;179m',
    'GHOST': '\x1b[38;5;126m',
    'DRAGON': '\x1b[38;5;057m',
    'DARK': '\x1b[38;5;095m',
    'STEEL': '\x1b[38;5;250m',
    'FAIRY': '\x1b[38;5;212m',
    'RESET': '\x1b[00;0;000m'
}

# declare timed text output
text = {
    'slow': 0.03,
    'normal': 0.02,
    'fast': 0.01,
    'ultra': 0.005,
    'debug': 0.0
}
text_speed = 'fast'


def reset_sp(speed) -> None:
    global sp, sg

    def sp(text, g=False) -> None:
        for key in colours.keys():
            text = text.replace(f'`{key}`', f'`{colours[key]}{key}{colours["RESET"]}`')
        coloured = False
        colour_char = False
        i = 0
        for char in f'{text}\n':
            if char == '`':
                if not coloured:
                    colour_char = True
                coloured = not coloured
                continue
            elif coloured and char == '[':
                colour_char = True
            elif not colour_char:
                sleep(speed)
            elif i >= 10:
                i = 0
                colour_char = False
                sleep(speed)
            else:
                i += 1
            stdout.write(char)
            stdout.flush()
        if g:
            getch()

    def sg(text) -> None:
        sp(text, g=True)


reset_sp(speed=text[text_speed])

# load screen
sp('Loading...')


# input function:
def get() -> str:
    return input('> ')


# check for required files
if not (path.isfile(path.join(syspath[0], i)) for i in [
    'data/dex.json',
    'data/level.json',
    'data/trainer_types.json',
    'data/types.json',
    'data/moves.json',
    'data/map.json',
    'data/pokemart.json',
    'data/trainers.json',
    'build_to_exe.py'
]):
    get()
    sysexit()


# menu variables
exit = is_debug = menu_open = options_open = False
y, n, yn = ['y'], ['n'], ['y', 'n']
types = ['NORMAL', 'FIRE', 'WATER', 'GRASS', 'ELECTRIC', 'ICE', 'FIGHTING', 'POISON', 'GROUND', 'FLYING', 'PSYCHIC',
         'BUG', 'ROCK', 'GHOST', 'DARK', 'DRAGON', 'STEEL', 'FAIRY']
badges = ['Boulder', 'Cascade', 'Thunder', 'Rainbow', 'Soul', 'Marsh', 'Volcano', 'Earth']

# battle screen variables
name_length = 15
bars_length = 20

# enables ANSI escape codes in Windows
system('')

# decide if damage is critical
def critical() -> bool:
    return randint(0, 255) <= 17


# pokemon class
class Pokemon:

    # set internals
    def __init__(self, species, level, ivs, moves=None, chp=None, current_xp=0, fainted=False,
                 player_pokemon=False) -> None:
        self.species = species
        self.index = dex[self.species]['index']  # type: ignore
        self.name = dex[self.species]['name']  # type: ignore
        self.type = dex[self.species]['type']  # type: ignore
        self.level = level
        self.ivs = ivs if ivs != 'random' else {i: randint(0, 31) for i in ['hp', 'atk', 'def', 'spa', 'spd', 'spe']}
        self.level_type = dex[self.species]['xp']  # type: ignore
        self.total_xp = xp['total'][self.level_type][str(self.level)]  # type: ignore
        self.current_xp = current_xp
        self.moves = moves or find_moves(self.species, self.level)
        self.status = {
            'burn': False,
            'confusion': False,
            'freeze': False,
            'paralysis': False,
            'poison': False,
            'sleep': False
        }

        # initialise stats
        self.reset_stats(chp, fainted, player_pokemon)

    # reset stats
    def reset_stats(self, chp=None, fainted=None, player_pokemon=False) -> None:
        self.stats = {
            'hp': floor(((dex[self.species]['hp'] + self.ivs['hp']) * 2 + floor(
                ceil(sqrt(self.ivs['hp'])) / 4) * self.level) / 100) + self.level + 10,  # type: ignore
            'atk': floor(((dex[self.species]['atk'] + self.ivs['atk']) * 2 + floor(
                ceil(sqrt(self.ivs['atk'])) / 4) * self.level) / 100) + 5,  # type: ignore
            'def': floor(((dex[self.species]['def'] + self.ivs['def']) * 2 + floor(
                ceil(sqrt(self.ivs['def'])) / 4) * self.level) / 100) + 5,  # type: ignore
            'spa': floor(((dex[self.species]['spa'] + self.ivs['spa']) * 2 + floor(
                ceil(sqrt(self.ivs['spa'])) / 4) * self.level) / 100) + 5,  # type: ignore
            'spd': floor(((dex[self.species]['spd'] + self.ivs['spd']) * 2 + floor(
                ceil(sqrt(self.ivs['spd'])) / 4) * self.level) / 100) + 5,  # type: ignore
            'spe': floor(((dex[self.species]['spe'] + self.ivs['spe']) * 2 + floor(
                ceil(sqrt(self.ivs['spe'])) / 4) * self.level) / 100) + 5  # type: ignore
        }
        if player_pokemon == False:
            for move in self.moves:
                move['pp'] = list(filter(lambda m, move=move: m['name'] == move['name'], moves))[0][
                    'pp']  # type: ignore
        self.stats['chp'] = chp or self.stats['hp']
        self.fainted = fainted or self.stats['chp'] <= 0
        if self.fainted:
            self.stats['chp'] = 0

    def check_level_up(self) -> None:
        while self.current_xp >= xp['next'][self.level_type][str(self.level)]:  # type: ignore
            self.current_xp -= xp['next'][self.level_type][str(self.level)]  # type: ignore
            self.level_up(self)
            if self.level == 100:
                sp(f'\nCongratulations, {self.name} has reached level 100!')
                break

    # check if pokemon is fainted
    def check_fainted(self) -> bool:
        if self.stats['chp'] <= 0:
            self.stats['chp'] = 0
            self.fainted = True
            return True
        return False

    # lower chp when pokemon is attacked
    def deal_damage(self, attacker, move) -> Optional[int]:
        move_entry = list(filter(lambda m: m['name'] == move['name'], moves))[0]  # type: ignore
        sp(f'\n{attacker.name} used {move["name"].upper()}!')
        if move_entry['damage_class'] == 'status':
            # TODO: Implement status conditions
            sp(f'(Note: {move["name"].upper()} is a status move)')
        else:
            if randint(1, 100) <= move_entry["accuracy"]:
                return self.damage_calc(move_entry, attacker)
            sp(f'{attacker.name} missed!')
            return 0

    # TODO Rename this here and in `deal_damage`
    def damage_calc(self, move_entry, attacker):
        is_critical = critical()
        attack_defense = ('atk', 'def') if move_entry['damage_class'] == 'physical' else ('spa', 'spd')
        result = floor((((((2 * attacker.level * (2 if is_critical else 1) / 5) + 2) * move_entry['power'] *
                          attacker.stats[attack_defense[0]] / self.stats[attack_defense[1]]) / 50) + 2) * (
                           1.5 if move_entry['type'] == attacker.type else 1) * randint(217, 255) / 255 * (
                           type_effectiveness(move_entry, self) if save['flag']['been_to_route_1'] else 1))

        self.stats['chp'] -= result
        if result > 0:
            sp(f'\n{attacker.name} dealt {result} damage to {self.name}!')
        if is_critical:
            sp('A critical hit!')
        for i in [
            (0, 'It had no effect!'),
            (0.5, 'It\'s super effective!'),
            (2, 'It\'s not very effective!')
        ]:
            if types[self.type][move_entry['type'].upper()] == i[0]:
                sp(f'{i[1]}')
        self.check_fainted()
        if self.fainted:
            sp(f'\n{self.name} fainted!')
        return result

    def deal_struggle_damage(self, damage):
        sp(f'{self.name} is hit with recoil!')
        self.stats['chp'] -= floor(damage / 2)
        self.check_fainted()
        if self.fainted:
            sp(f'\n{self.name} fainted!')

    # calculate xp rewarded after battle
    def calculate_xp(self, battle_type='wild') -> int:
        return ceil((self.total_xp * self.level * (1 if battle_type == 'wild' else 1.5)) / 7)  # type: ignore

    # give xp from opponent pokemon to party in battle
    def give_xp(self, participating_pokemon, type="wild"):
        total_xp = self.calculate_xp(type)  # type: ignore
        debug(f'total xp: {total_xp}')
        if 'EXP. ALL' in save['bag']:
            for p in participating_pokemon:
                save['party'][p].current_xp += floor(total_xp / (len(participating_pokemon) + 1))
                sg(f'{save["party"][p].name} gained {floor(total_xp / (len(participating_pokemon) + 1))} XP!')
                save['party'][p].check_level_up()

            other_pokemon = [pokemon for pokemon in save['party'] if pokemon not in participating_pokemon]
            for o in other_pokemon:
                save['party'][o].current_xp += floor((total_xp / (len(participating_pokemon) + 1)) / len(other_pokemon))
                sg(f'{save["party"][o].name} gained {floor((total_xp / (len(participating_pokemon) + 1)) / len(other_pokemon))} XP!')
                save['party'][o].check_level_up()

        else:
            for p in participating_pokemon:
                save['party'][p].current_xp += floor(total_xp / len(participating_pokemon))
                sg(f'{save["party"][p].name} gained {floor(total_xp / len(participating_pokemon))} XP!')
                save['party'][p].check_level_up()
            sp("")
        sleep(0.5)

    # evolve pokemon
    def evolve(self):
        sp(f'\nWhat? {self.name} is evolving!')
        input_cancel = getch()
        # for _ in range(3):
        if input_cancel in ['e', 'b']:
            sg(f'{self.name} didn\'t evolve')
            return

        sleep(0.5)
        print("...")
        sleep(2)

        self.index += 1
        old_name = self.name
        for p in dex.keys():  # type: ignore
            if dex[p]['index'] == self.index:  # type: ignore
                self.species = p
                self.name = dex[self.species]['name']  # type: ignore
        self.reset_stats()
        sg(f'\n{old_name} evolved into {self.species}!')  # type: ignore

        save['dex'][self.species] = {'seen': True, 'caught': True}
        save['flag']['type'][self.type] = {'seen': True, 'caught': True}
        for move in dex[self.species]['moves']:  # type: ignore
            # TODO: Possibly keep track of moves that were forgotten too and not reprompt to learn as well?
            if move['level'] <= self.level and move['name'] not in (m['name'] for m in self.moves):
                self.learn_move(move)

    def learn_move(self, move):
        if len(self.moves) == 4:
            sg(f'{self.name} wants to learn {move["name"].upper()}!')
            sg(f'But {self.name} already knows 4 moves')
            all_moves = [*self.moves, move]
            move_forgotten = False
            while not move_forgotten:
                sp(f'Which move should {self.name} forget?\n')
                for i in range(5):
                    print(f'[{i + 1}] - {all_moves[i]["name"].upper().replace("-", " ")}')
                forget_move = ''
                while not forget_move:
                    forget_move = get()
                    if forget_move not in ['1', '2', '3', '4', '5']:
                        forget_move = ''
                    else:
                        if forget_move == '5':
                            sp(f'\nAre you sure you want {self.name} to not learn {move["name"].upper()}? (Y/N)')
                        else:
                            sp(f'\nAre you sure you want {self.name} to forget {all_moves[int(forget_move) - 1]["name"].upper()}? (Y/N)')
                        option = ''
                        while option not in ['y', 'n']:
                            option = get()
                        if option in ['y']:
                            if forget_move == '5':
                                sp(f'\n{self.name} didn\'t learn {move["name"].upper()}')
                            else:
                                sp(f'\n{self.name} forgot {all_moves[int(forget_move) - 1]["name"].upper()}\n')
                                sp(f'\n{self.name} learned {move["name"].upper()}!')
                                self.moves = [move for move in self.moves if
                                              move['name'] != all_moves[int(forget_move) - 1]['name']]
                                self.moves.append({"name": move['name'],
                                                   "pp": list(filter(lambda mv: mv['name'] == move['name'], moves))[0][
                                                       'pp']})  # type: ignore
                            move_forgotten = True
        else:
            sg(f'{self.name} learned {move["name"].upper()}')
            self.moves.append({"name": move['name'],
                               "pp": list(filter(lambda mv, move=move: mv['name'] == move['name'], moves))[0][
                                   'pp']})  # type: ignore

    # raw level up
    def level_up(self, pokemon):
        pokemon.level += 1
        pokemon.reset_stats()
        sg(f'{pokemon.name} grew to level {pokemon.level}!')
        if ('evolution' in dex[pokemon.species] and pokemon.level >= dex[pokemon.species]['evolution']):  # type: ignore
            pokemon.evolve()
        for m in dex[pokemon.species]['moves']:  # type: ignore
            if m['level'] == pokemon.level:
                pokemon.learn_move(m)

    # catch Pokemon
    def catch(self, ball: str) -> bool:
        global save
        if max(bool(self.status[i]) for i in ['freeze', 'sleep']):
            status = 25
        elif max(bool(self.status[i]) for i in ['burn', 'poison', 'paralysis']):
            status = 12
        else:
            status = 0

        # find Poke Ball type
        if ball == "Great Ball":
            ball_modifier = 201
        elif ball == "Master Ball":
            pass  # guaranteed catch
        elif ball == "Poke Ball":
            ball_modifier = 256
        elif ball == "Ultra Ball":
            ball_modifier = 151
        else:
            abort(f'Invalid ball: {ball}')

        # decide whether caught
        C = dex[self.species]['catch']  # type: ignore
        if ball == "Master Ball":
            catch = True
        elif self.stats['hp'] / (2 if ball == "Great Ball" else 3) >= self.stats['chp'] and (
                status + C + 1) / ball_modifier >= 1:  # type: ignore
            catch = True
        else:
            X = randint(0, ball_modifier - 1)  # type: ignore
            if X < status:
                catch = True
            elif X > status + C:
                catch = False
            else:
                catch = min(
                    255,
                    self.stats['hp'] * 255 // (8 if ball == "Great Ball" else 12) // max(1,
                                                                                         floor(self.stats['chp'] / 4))
                ) >= randint(0, 255)

        if catch:
            return self.add_caught_pokemon(save)
        wobble_chance = ((C * 100) // ball_modifier * min(255, self.stats['hp'] * 255 // (
            8 if ball == "Great Ball" else 12) // max(1, floor(self.stats['chp'] / 4)))) // 255 + status  # type: ignore
        debug(wobble_chance)

        if wobble_chance >= 0 and wobble_chance < 10:  # No wobbles
            sp('The ball missed the Pokémon!')
        elif wobble_chance >= 10 and wobble_chance < 30:  # 1 wobble
            sp('Darn! The Pokémon broke free!')
        elif wobble_chance >= 30 and wobble_chance < 70:  # 2 wobbles
            sp('Aww! It appeared to be caught!')
        elif wobble_chance >= 70 and wobble_chance <= 100:  # 3 wobbles
            sp('Shoot! It was so close too!')
        return False

    # once pokemon is caught, add to party or box
    def add_caught_pokemon(self, save):
        location = 'party' if len(save['party']) < 6 else 'box'
        save[location].append(self)
        save['dex'][self.species] = {'seen': True, 'caught': True}
        save['flag']['type'][self.type] = {'seen': True, 'caught': True}
        sg(f'\nYou caught {self.name}!')
        sg(f'\n{self.name} (`{self.type}`-type) was added to your {location}.')
        return True


# check if party is alive
def is_alive(self) -> bool:
    return any(not i.fainted for i in self)


# use item from bag
def use_item(battle=False) -> str:  # type: ignore
    global save
    item_used = False
    sp('\nPlease choose an item to use.')
    if battle:
        sp('\n'.join(f'{key}: {save["bag"][key]}' for key in save['bag'] if items[key]['battle']))  # type: ignore
    else:
        sp('\n'.join(f'{key}: {save["bag"][key]}' for key in save['bag']))
    sp('[e] - Back\n')
    while not item_used:
        item = ''
        while not item:
            item = get()
        if item == "e":
            return "exit"
        if item in save['bag']:
            if save['bag'][item] > 0:
                save['bag'][item] -= 1
                # exec(items[item]['command']) # type: ignore
                return item
            else:
                sp('You have none of that item!')


# randomise escape
def escape(pokemon, opponent, escape_attempts) -> bool:
    return floor(
        (pokemon.stats['spe'] * 32) / (floor(opponent.stats['spe'] / 4) % 256)) + 30 * escape_attempts > 255 or floor(
        opponent.stats['spe'] / 4) % 256 == 0


# calculate type effectiveness
def type_effectiveness(move, defender) -> float:
    return types[move['type'].upper()][defender.type]  # type: ignore


# calculate prize money
def prize_money(party=None, type='Pokémon Trainer') -> int:
    return floor(trainer_types[type] * max(i.level for i in (party or save['party'])))  # type: ignore


# find moves of a wild pokemon
def find_moves(name, level) -> list:
    learned_moves = [{**move, "pp": list(filter(lambda m, move=move: m['name'] == move['name'], moves))[0]['pp']} for
                     move in dex[name]['moves'] if move['level'] <= level]  # type: ignore

    learned_moves = sorted(learned_moves, key=lambda m: m['level'], reverse=True)
    if len(learned_moves) >= 4:
        return list(map(lambda m: {"name": m['name'], "pp": m["pp"]}, learned_moves[:4]))
    else:
        return list(map(lambda m: {"name": m['name'], "pp": m["pp"]}, learned_moves))


# switch pokemon in battle
def switch_pokemon(party_length: int) -> Union[int, str]:
    sp(f'''\nWhich Pokémon should you switch to?\n\n{
    chr(10).join(f'{f"[{i + 1}]" if not save["party"][i].check_fainted() else "FAINTED"} - {save["party"][i].name} ({save["party"][i].stats["chp"]}/{save["party"][i].stats["hp"]}) - Level {save["party"][i].level} ({colours[save["party"][i].type.upper()]}{save["party"][i].type}{colours["NORMAL"]})' for i in range(party_length))
    }''')
    sp('[e] - Back\n')
    switch_choice = ''
    while not switch_choice:
        while switch_choice == '':
            switch_choice = get()
        if switch_choice == 'e':
            return 'exit'
        try:
            if switch_choice not in [str(i + 1) for i in range(party_length)]:
                switch_choice = ''
                sp('\nInvalid choice.')
            elif save['party'][int(switch_choice) - 1].check_fainted():
                switch_choice = ''
                sp('That Pokémon is fainted!')
        except (TypeError, ValueError):
            switch_choice = ''
            sp('\nInvalid choice.')
    return int(switch_choice)


# create battle process
def battle(opponent_party=None, battle_type='wild', name=None, title=None, start_diagloue=None, end_dialouge=None,
           earn_xp=True) -> None:
    global save
    debug('Entered battle!')
    debug(f'Party: {[i.name for i in save["party"]]}')
    party_length = len(save['party'])
    current = ''
    opponent_current = 0
    for i in range(party_length):
        if not save['party'][i].check_fainted():
            debug(f'{save["party"][i].name} is the first alive Pokemon in the party.')
            current = i
            break

    # battle intro
    if battle_type == 'trainer':
        sg(f'\n{name if name else title}: {start_diagloue}')
        sg(f'\n{title} {name + " " if name else ""}wants to fight!')
    elif battle_type == 'wild':
        sp(f'\nA wild {opponent_party[opponent_current].name} appeared!')  # type: ignore
    else:
        abort('\nInvalid battle type: neither trainer nor wild.')
    sp(f'\nGo, {save["party"][current].name}!')
    sleep(0.5)
    if battle_type == 'trainer':
        sp(f'\n{name if name else title} sent out {opponent_party[opponent_current].name}!')  # type: ignore

    # battle variables
    escaped_from_battle = False
    escape_attempts = 0
    caught = False
    catch_attempt = False
    switched = False
    participating_pokemon = [current]

    # check if parties are alive
    debug(f'\nPlayer party alive: {is_alive(save["party"])}\nOpponent party alive: {is_alive(opponent_party)}')

    # battle loop
    while is_alive(save['party']) and is_alive(opponent_party):

        # player turn
        debug('Turn start!')
        player_attacked_this_turn = False
        opponent_attacked_this_turn = False
        catch_attempt = False
        switched = False

        # calculate health bars according to ratio (chp:hp)
        bars = ceil((save['party'][current].stats['chp'] / (save['party'][current].stats['hp'])) * bars_length)
        opponent_bars = ceil((opponent_party[opponent_current].stats['chp'] / (
        opponent_party[opponent_current].stats['hp'])) * bars_length)  # type: ignore
        debug(f'Player bars: {bars}\nOpponent bars: {opponent_bars}')
        debug(
            f'Player level: {save["party"][current].level}\nOpponent level: {opponent_party[opponent_current].level}')  # type: ignore
        sp(f'''\n{save["party"][current].name}{' ' * (name_length - len(save['party'][current].name))}[{'=' * bars}{' ' * (bars_length - bars)}] {str(save['party'][current].stats['chp'])}/{save['party'][current].stats['hp']} (`{save["party"][current].type}`) Lv. {save["party"][current].level}\n{opponent_party[opponent_current].name}{' ' * (name_length - len(opponent_party[opponent_current].name))}[{'=' * opponent_bars}{' ' * (bars_length - opponent_bars)}] {opponent_party[opponent_current].stats['chp']}/{opponent_party[opponent_current].stats['hp']} (`{opponent_party[opponent_current].type}`) Lv. {opponent_party[opponent_current].level}''')  # type: ignore
        sp(f'\nWhat should {save["party"][current].name} do?\n\n[1] - Attack\n[2] - Switch\n[3] - Item\n[4] - Run\n')

        valid_choice = False
        while not valid_choice:
            user_choice = get()
            if user_choice == '2' and len(save['party']) == 1:
                sp('You can\'t switch out your only Pokémon!')
            elif user_choice == '3' and len(save['bag']) == 0:
                sp('You have no items!')
            elif user_choice == '4' and battle_type == 'trainer':
                sp('You can\'t run from a trainer battle!')
            elif user_choice in ['1', '2', '3', '4']:
                valid_choice = True

        # choose attack
        if user_choice == '1':  # type: ignore
            struggle = True
            for move_iter in save['party'][current].moves:
                if move_iter['pp'] > 0:
                    struggle = False
            if struggle:
                sp(f'{save["party"][current].name} has no moves left!')
                chosen_move = {'name': 'struggle'}
            else:
                options = []
                sp('')
                move_names = []
                type_names = []
                for i in save['party'][current].moves:
                    move_names.append(i['name'])
                    type_names.append(
                        list(filter(lambda m, i=i: m['name'] == i['name'], moves))[0]['type'])  # type: ignore
                longest_move_name_length = len(max(move_names, key=len))
                longest_type_name_length = len(max(type_names, key=len))

                for i in range(len(save['party'][current].moves)):
                    move_entry = \
                    list(filter(lambda m, i=i: m['name'] == save['party'][current].moves[i]['name'], moves))[
                        0]  # type: ignore
                    sp(f'[{i + 1}] - {save["party"][current].moves[i]["name"].upper().replace("-", " ")}{" " * (longest_move_name_length - len(save["party"][current].moves[i]["name"].upper().replace("-", " ")))} | `{move_entry["type"].upper()}`{" " * (longest_type_name_length - len(move_entry["type"].upper()))} - {save["party"][current].moves[i]["pp"]}/{move_entry["pp"]}')
                    options.append(str(i + 1))
                sp(f'[e] - Back\n')
                valid_choice = False
                while not valid_choice:
                    move_choice = get()
                    if move_choice in options:
                        if save['party'][current].moves[int(move_choice) - 1]['pp'] == 0:
                            sp(f'{save["party"][current].name} cannot use {save["party"][current].moves[int(move_choice) - 1]["name"]}')
                        else:
                            valid_choice = True
                    elif move_choice == "e":
                        valid_choice = True
                if move_choice == "e":  # type: ignore
                    continue

                chosen_move = save["party"][current].moves[int(move_choice) - 1]  # type: ignore

            if save['party'][current].stats['spe'] >= opponent_party[opponent_current].stats['spe']:  # type: ignore
                damage = opponent_party[opponent_current].deal_damage(save['party'][current],
                                                                      chosen_move)  # type: ignore
                if chosen_move["name"] == "struggle":
                    save['party'][current].deal_struggle_damage(damage)
                else:
                    save["party"][current].moves[int(move_choice) - 1]['pp'] -= 1  # type: ignore

                player_attacked_this_turn = True

        # choose switch
        elif user_choice == '2':  # type: ignore
            switch_choice = switch_pokemon(party_length)

            if switch_choice == "exit":
                continue

            if int(switch_choice) - 1 == current:
                continue

            current = int(switch_choice) - 1
            switched = True
            if int(switch_choice) - 1 not in participating_pokemon:
                participating_pokemon.append(current)

        # choose item
        elif user_choice == '3':  # type: ignore
            item = use_item(battle=True)
            if item == "exit":
                continue
            if (
                    item == 'Poke Ball' or item == 'Great Ball' or item == 'Ultra Ball' or item == 'Master Ball') and battle_type == 'trainer':
                sp("You can't catch another trainer's Pokémon!")
            elif item == 'Poke Ball':
                if opponent_party[opponent_current].catch("Poke Ball"):  # type: ignore
                    caught = True
                    break
                else:
                    catch_attempt = True
            elif item == 'Great Ball':
                if opponent_party[opponent_current].catch("Great Ball"):  # type: ignore
                    caught = True
                    break
                else:
                    catch_attempt = True
            elif item == 'Ultra Ball':
                if opponent_party[opponent_current].catch("Ultra Ball"):  # type: ignore
                    caught = True
                    break
                else:
                    catch_attempt = True
            elif item == 'Master Ball':
                if opponent_party[opponent_current].catch("Master Ball"):  # type: ignore
                    caught = True
                    break
                else:
                    catch_attempt = True

        # choose run
        elif user_choice == '4':  # type: ignore
            if escape(save['party'][current], opponent_party[opponent_current], escape_attempts):  # type: ignore
                escaped_from_battle = True
                break
            else:
                escape_attempts += 1

        # reset consecutive escape attempts
        if user_choice != '4':  # type: ignore
            escape_attempts = 0

        # opponent attack
        if not save['party'][current].check_fainted() and not opponent_party[
            opponent_current].check_fainted():  # type: ignore
            save['party'][current].deal_damage(opponent_party[opponent_current],
                                               choice(opponent_party[opponent_current].moves))  # type: ignore
            opponent_attacked_this_turn = True

        # player attack if player speed is lower
        if save['party'][current].check_fainted() and opponent_party[
            opponent_current].check_fainted() and not player_attacked_this_turn and escape_attempts == 0 and not catch_attempt and not switched:  # type: ignore
            damage = opponent_party[opponent_current].deal_damage(save['party'][current], chosen_move)  # type: ignore
            if chosen_move["name"] == "struggle":  # type: ignore
                save['party'][current].deal_struggle_damage(damage)
            else:
                save["party"][current].moves[int(move_choice) - 1]['pp'] -= 1  # type: ignore
            player_attacked_this_turn = True

        # give XP when opponent faints
        if opponent_party[opponent_current].check_fainted() and earn_xp == True:  # type: ignore
            opponent_party[opponent_current].give_xp(participating_pokemon, battle_type)  # type: ignore
            if battle_type == "trainer" and is_alive(opponent_party):
                opponent_current += 1
                sp(f'\n{name if name else title} sent out {opponent_party[opponent_current].name}!')  # type: ignore

        # end battle if player wins or loses
        if is_alive(save['party']) and not is_alive(opponent_party) or not is_alive(save['party']):
            break

        if save['party'][current].check_fainted():
            participating_pokemon = list(
                filter(lambda p, current=current: save['party'][p].name != save['party'][current].name,
                       participating_pokemon))
            switch_choice = switch_pokemon(party_length)
            current = int(switch_choice) - 1
            switched = True
            if int(switch_choice) - 1 not in participating_pokemon:
                participating_pokemon.append(current)

        # display turn details
        debug(
            f'Higher Speed: {"Player" if save["party"][current].stats["spe"] > opponent_party[opponent_current].stats["spe"] else "Opponent"}\nPlayer Attacked: {player_attacked_this_turn}\nOpponent Attacked: {opponent_attacked_this_turn}\n')  # type: ignore

    # upon escaping
    if escaped_from_battle:
        sp('You escaped!')

    # upon catching
    elif caught:
        # TODO: earn xp
        pass  # type: ignore

    # upon winning
    elif is_alive(save['party']) and not is_alive(opponent_party):
        if save['flag']['been_to_route_1']:
            if battle_type == 'trainer':
                sg(f'\n{save["name"]} won the battle!')
                save['money'] += prize_money(opponent_party, title)  # type: ignore
                sg(f'You recieved ¥{prize_money(opponent_party, title)} as prize money.')  # type: ignore
                sg(f'\n{name if name else title}: {end_dialouge}')
        else:
            save['flag']['won_first_battle'] = True

    # upon losing
    elif is_alive(opponent_party) and (not is_alive(save['party'])):
        if battle_type == 'trainer':
            if save['flag']['been_to_route_1']:
                sg('You lost the battle!')
                sg(f'You gave ¥{round(save["money"] / 2)} as prize money.')
            else:
                save['flag']['won_first_battle'] = False
        sg('...')
        sg(f'{save["name"]} blacked out!')
        save['money'] = round(save['money'] / 2)
        save['location'] = save['recent_center']

        for i in save['party']:
            i.reset_stats()
            sp(f'{i.name} was healed to max health.')


    # if battle is neither won nor lost
    else:
        abort('\nInvalid battle state; neither won, lost, caught, nor escaped. Could not load player turn.')


def get_encounter(loc, type) -> dict:
    pokemon = []
    weights = []
    for chance in rates[loc][type]:  # type: ignore
        for i in range(len(rates[loc][type][chance])):  # type: ignore
            pokemon.append(rates[loc][type][chance][i])  # type: ignore
            weights.append(int(chance) / 255)
    return choices(pokemon, weights)[0]

def debug(text) -> None:
    if is_debug:
        sp(f'{colours["GROUND"]}Debug: {text}{colours["RESET"]}')

# main loop
if __name__ == '__main__':

    # load data from files
    # for i in [
    #     ['dex', 'dex.json'],
    #     ['items', 'item.json'],
    #     ['moves', 'moves.json'],
    #     ['rates', 'map.json'],
    #     ['save_template', 'save_template.json'],
    #     ['trainer_types', 'trainer_types.json'],
    #     ['types', 'types.json'],
    #     ['xp', 'level.json'],
    #     ['pokemart', 'pokemart.json'],
    #     ['trainers', 'trainers.json']
    # ]:
    #     try:
    #         exec(
    #             f'{i[0]} = loads(open(path.join(syspath[0], "data", "{i[1]}"), encoding="utf8").read())\nopen(path.join(syspath[0], "data", "{i[1]}")).close()')
    #     except Exception:
    #         abort(f'Failed to load {i[1]}!')

    dex = loads(open(path.join(syspath[0], "data", 'dex.json'), encoding="utf8").read())
    items = loads(open(path.join(syspath[0], "data", 'item.json'), encoding="utf8").read())
    moves = loads(open(path.join(syspath[0], "data", "moves.json"), encoding="utf8").read())
    rates = loads(open(path.join(syspath[0], "data", "map.json"), encoding="utf8").read())
    save_template = loads(open(path.join(syspath[0], "data", 'save_template.json'), encoding="utf8").read())
    trainer_types = loads(open(path.join(syspath[0], "data", 'trainer_types.json'), encoding="utf8").read())
    types = loads(open(path.join(syspath[0], "data", 'types.json'), encoding="utf8").read())
    xp = loads(open(path.join(syspath[0], "data", "level.json"), encoding="utf8").read())
    pokemart = loads(open(path.join(syspath[0], "data", "pokemart.json"), encoding="utf8").read())
    trainers = loads(open(path.join(syspath[0], "data", "trainers.json"), encoding="utf8").read())

    option = dex_string = ''
    # intro
    playerName = 'RED'
    save = save_template  # type: ignore
    save['options']['text_speed'] = 'normal'
    # save['starter'] = 'CHARMANDER'
    save['starter'] = 'MEW'
    save['dex'] = {save['starter']: {'seen': True, 'caught': True}}
    save['flag']['type'] = {
        dex[save['starter']]['type']: {'seen': True, 'caught': True}}  # type: ignore

    level = 50

    save['party'].append(Pokemon(save['starter'], level, 'random', find_moves(save['starter'], level)))

    # encounter = get_encounter('route1-n', 'tall-grass')
    # battle([Pokemon(encounter['pokemon'], encounter['l1evel'], 'random')])

    battle([Pokemon("MEWTWO", level, 'random', find_moves("MEWTWO", level))])

# end program