'''
Project Page - [https://Pokemon-PythonRed.github.io]
Repository   - [https://github.com/Pokemon-PythonRed/Pokemon-PythonRed]
License      - MIT
'''
import random
# import system modules
from json import dumps, loads
from math import ceil, floor, sqrt
from os import path, system
from random import choice, choices, randint
from sys import exit as sysexit, path as syspath, stdout
from time import sleep, time
from typing import Optional, Union
from getch import getch, getche


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
text_speed = "fast"


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

# input function:
def get() -> str:
    return input('> ')

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
    def __init__(self, species, level, ivs="random", evs="even", moves=None, chp=None, fainted=False,
                 player_pokemon=False) -> None:
        self.species = species
        self.index = dex[self.species]['index']  # type: ignore
        self.name = dex[self.species]['name']  # type: ignore
        self.type = dex[self.species]['type']  # type: ignore
        self.level = level
        self.ivs = ivs if ivs != 'random' else {i: randint(0, 31) for i in ['hp', 'atk', 'def', 'spa', 'spd', 'spe']}
        if evs == "even":
            self.evs = {i: 85 for i in ['hp', 'atk', 'def', 'spa', 'spd', 'spe']} # total sum is 510
        elif evs == "zero":
            self.evs = {i: 0 for i in ['hp', 'atk', 'def', 'spa', 'spd', 'spe']}
        else:
            self.evs = evs

        self.moves = moves or find_moves(self.species, self.level)
        self.no_volatile_status = {
            'burn': False,
            'freeze': False,
            'paralysis': False,
            'poison': False,
            'sleep': False
        }
        self.volatile_status = {
            'confusion': False,
            'atk': 0,
            'def': 0,
            'spa': 0,
            'spd': 0,
            'spe': 0,
            'acc': 0
        }

        # initialise stats
        self.reset_stats(chp, fainted, player_pokemon)

    # reset stats
    def reset_stats(self, chp=None, fainted=None, player_pokemon=False) -> None:
        self.stats = {
            "hp": floor(0.01 * (2 * dex[self.species]["hp"] + self.ivs["hp"] + floor(0.25 * self.evs["hp"])) * self.level) + self.level + 10,
            "atk": floor(0.01 * (2 * dex[self.species]["atk"] + self.ivs["atk"] + floor(0.25 * self.evs["atk"])) * self.level) + 5,
            'def': floor(0.01 * (2 * dex[self.species]["def"] + self.ivs["def"] + floor(0.25 * self.evs["def"])) * self.level) + 5,
            'spa': floor(0.01 * (2 * dex[self.species]["spa"] + self.ivs["spa"] + floor(0.25 * self.evs["spa"])) * self.level) + 5,
            'spd': floor(0.01 * (2 * dex[self.species]["spd"] + self.ivs["spd"] + floor(0.25 * self.evs["spd"])) * self.level) + 5,
            'spe': floor(0.01 * (2 * dex[self.species]["spe"] + self.ivs["spe"] + floor(0.25 * self.evs["spe"])) * self.level) + 5,
        }

        if player_pokemon == False:
            for move in self.moves:
                move['pp'] = list(filter(lambda m, move=move: m['name'] == move['name'], moves))[0][
                    'pp']  # type: ignore
        self.stats['chp'] = chp or self.stats['hp']
        self.fainted = fainted or self.stats['chp'] <= 0
        if self.fainted:
            self.stats['chp'] = 0

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

        if move_entry["power"]:
            power = move_entry["power"]
        else:
            power = 0

        base_result = (2/5 * attacker.level * (2 if is_critical else 1) + 2) * (power * attacker.stats[attack_defense[0]] / self.stats[attack_defense[1]]) / 50 + 2
        type_effect = type_effectiveness(move_entry, self)
        stab = 1.5 if move_entry["type"] == attacker.type else 1
        rand_effect = randint(217, 255) / 255
        result = floor(base_result * type_effect * stab * rand_effect)

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
                if save['bag'][item] == 0:
                    save['bag'].pop(item, None)
                return item
            else:
                sp('You have none of that item!')

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
def battle(opponent_party=None, battle_type='wild', name=None, title=None, start_diagloue=None, end_dialouge=None) -> None:
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
        raise ValueError('\nInvalid battle type: neither trainer nor wild.')
    sp(f'\nGo, {save["party"][current].name}!')
    sleep(0.5)
    if battle_type == 'trainer':
        sp(f'\n{name if name else title} sent out {opponent_party[opponent_current].name}!')  # type: ignore

    # battle variables
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
        switched = False
        used_item = False

        # calculate health bars according to ratio (chp:hp)
        bars = ceil((save['party'][current].stats['chp'] / (save['party'][current].stats['hp'])) * bars_length)
        opponent_bars = ceil((opponent_party[opponent_current].stats['chp'] / (
        opponent_party[opponent_current].stats['hp'])) * bars_length)  # type: ignore
        debug(f'Player bars: {bars}\nOpponent bars: {opponent_bars}')
        debug(
            f'Player level: {save["party"][current].level}\nOpponent level: {opponent_party[opponent_current].level}')  # type: ignore
        sp(f'''\n{save["party"][current].name}{' ' * (name_length - len(save['party'][current].name))}[{'=' * bars}{' ' * (bars_length - bars)}] {str(save['party'][current].stats['chp'])}/{save['party'][current].stats['hp']} (`{save["party"][current].type}`) Lv. {save["party"][current].level}\n{opponent_party[opponent_current].name}{' ' * (name_length - len(opponent_party[opponent_current].name))}[{'=' * opponent_bars}{' ' * (bars_length - opponent_bars)}] {opponent_party[opponent_current].stats['chp']}/{opponent_party[opponent_current].stats['hp']} (`{opponent_party[opponent_current].type}`) Lv. {opponent_party[opponent_current].level}''')  # type: ignore
        sp(f'\nWhat should {save["party"][current].name} do?\n\n[1] - Attack\n[2] - Switch\n[3] - Item\n')

        valid_choice = False
        while not valid_choice:
            user_choice = get()
            if user_choice == '2' and len(save['party']) == 1:
                sp('You can\'t switch out your only Pokémon!')
            elif user_choice == '3' and len(save['bag']) == 0:
                sp('You have no items!')
            elif user_choice in ['1', '2', '3']:
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
            elif item == "Full Restore":
                save['party'][current].stats['chp'] = save['party'][current].stats['hp']
                sp(f"{save['party'][current].name} was healed to max health")
                used_item = True

            elif item == "Full Heal":
                # set no-volatile status to false
                # TODO:
                # for save['party'][current].no_volatile_status

                sp(f"{save['party'][current].name} was healed to normal status")
                used_item = True

        # opponent attack
        if not save['party'][current].check_fainted() and not opponent_party[
            opponent_current].check_fainted():  # type: ignore
            save['party'][current].deal_damage(opponent_party[opponent_current],
                                               choice(opponent_party[opponent_current].moves))  # type: ignore
            opponent_attacked_this_turn = True

        # player attack if player speed is lower
        if (not save['party'][current].check_fainted() and
            not opponent_party[opponent_current].check_fainted() and
            not player_attacked_this_turn and
            not used_item and
            not switched):
            damage = opponent_party[opponent_current].deal_damage(save['party'][current], chosen_move)  # type: ignore
            if chosen_move["name"] == "struggle":  # type: ignore
                save['party'][current].deal_struggle_damage(damage)
            else:
                save["party"][current].moves[int(move_choice) - 1]['pp'] -= 1  # type: ignore
            player_attacked_this_turn = True

        # trainer switches pokemon when opponent faints
        if opponent_party[opponent_current].check_fainted():  # type: ignore
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

    # upon winning
    if is_alive(save['party']) and not is_alive(opponent_party):
        sg(f'\n{save["name"]} won the battle!')
        sg(f'\n{name if name else title}: {end_dialouge}')

    # upon losing
    elif is_alive(opponent_party) and (not is_alive(save['party'])):
        sg('You lost the battle!')
        sg('...')
        sg(f'{save["name"]} blacked out!')

        for i in save['party']:
            i.reset_stats()
            sp(f'{i.name} was healed to max health.')

    # if battle is neither won nor lost
    else:
        raise ValueError('\nInvalid battle state; neither won, lost.')

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

    dex = loads(open(path.join(syspath[0], "data", 'dex.json'), encoding="utf8").read())
    items = loads(open(path.join(syspath[0], "data", 'item.json'), encoding="utf8").read())
    moves = loads(open(path.join(syspath[0], "data", "moves.json"), encoding="utf8").read())
    save_template = loads(open(path.join(syspath[0], "data", 'save_template.json'), encoding="utf8").read())
    types = loads(open(path.join(syspath[0], "data", 'types.json'), encoding="utf8").read())

    option = dex_string = ''
    # intro
    save = save_template  # type: ignore
    save["name"] = 'RED'
    save['options']['text_speed'] = 'ultra'
    level = 100
    all_pokemon_specious = list(dex.keys())

    # items
    save["bag"] = {
        "Full Restore": 3,
        "Full Heal": 3
    }
    # status poison, paralysis, sleep, burn, frozen

    for i in range(1):
        idx = randint(0, 155)
        species = all_pokemon_specious[idx]
        save['party'].append(Pokemon(species, level, 'random', "even", find_moves(species, level)))

    opponent_party = []
    for i in range(1):
        idx = randint(0, 155)
        species = all_pokemon_specious[idx]
        opponent_party.append(Pokemon(species, level, 'random', "even", find_moves(species, level)))



    battle(opponent_party, battle_type="trainer", name="Sihao", title="Pokemon Master", start_diagloue="Let's battle!")

# end program