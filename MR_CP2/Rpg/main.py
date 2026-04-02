import pygame
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Callable
from faker import Faker
import random
from datetime import date


Width, Height = 900, 650
BackgroundColor = (18, 18, 24)
TextColor = (210, 210, 220)
PromptColor = (0, 255, 140)
HistoryColor = (170, 170, 190)
ErrorColor = (255, 70, 70)
SuccessColor = (0, 255, 120)

LineHeight = 26
VisibleLines = 19
YStartHistory = 25
CharacterLimit = 280
MaxHistory = 50

FontSize = 18
SmallFont = 15

fake = Faker()

SAVE_PATH = Path("Rpg/savegame.json")
LOGO_PATH = Path("MR_CP2") / "Rpg" / "Pictures" / "73oaud.png"


GameState: Dict[str, Any] = {
    "level": 1, "rank": "Novice", "money": 100, "souls": 0,
    "attributes": [10, 8, 6, 100],
    "inventory": [], "store": {"Sword": 50, "Potion": 10, "Charm": 20, "Key": 30},
    "powerups": [], "skills": [],
    "character": {"type":"Unknown","skin":"Unknown","eyes":"Unknown","height":"Unknown","hunter":"Unknown"}
}

ProgramState = "MAIN_MENU"
History: List[str] = []
Usertext = ""
Running = True
CommandHandle: Dict[str, Callable] = {}

def safe_int(value, minimum=0, default=None):
    try:
        v = int(value)
        return v if v >= minimum else default
    except:
        return default

def safe_text(text, max_len=30):
    return text.strip()[:max_len] if text.strip() else None

def LogCommand(text: str, error=False, success=False):
    History.append(text)
    if len(History) > MaxHistory:
        History[:] = History[-MaxHistory:]

def RegisterCommand(name: str, func: Callable):
    CommandHandle[name.lower()] = func

def detailed_backstory():
    first, last = fake.first_name(), fake.last_name()
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=80)
    age = date.today().year - birthdate.year
    city, country = fake.city(), fake.country()
    job, company = fake.job(), fake.company()
    traits = ["brilliant","reckless","charming","cold","empathetic","manipulative","loyal","ambitious","paranoid","curious"]
    hobbies = ["hiking","reading","coding","traveling","painting","gaming","cooking","collecting rare items","photography"]
    past_events = ["survived a near-fatal accident","won a prestigious award","lost someone important","uncovered a hidden truth","was betrayed by a close friend","grew up in poverty","lived abroad for several years"]
    goals = ["seeking revenge","trying to find purpose","hiding a dangerous secret","searching for a lost loved one","building a legacy","escaping their past"]
    secrets = ["they are not who they claim to be","they are being watched","they once committed a serious crime","they possess forbidden knowledge","their past identity was erased"]

    return (f"{first} {last}, age {age}, born in {city}, {country}.\n"
            f"Known for being {random.choice(traits)}, works as {job} at {company}.\n"
            f"Enjoys {random.choice(hobbies)}. Earlier, they {random.choice(past_events)}.\n"
            f"Currently {random.choice(goals)}. Secretly, {random.choice(secrets)}.\n"
            f"One day, everything changed...")


def CommandHelp(_): LogCommand("Commands: help, save, load, clear, stats")
def CommandSave(_):
    try:
        SAVE_PATH.parent.mkdir(exist_ok=True)
        with SAVE_PATH.open("w") as f:
            json.dump(GameState, f, indent=2)
        LogCommand("Game saved!", success=True)
    except: LogCommand("Save failed", error=True)

def CommandLoad(_):
    try:
        if SAVE_PATH.exists():
            with SAVE_PATH.open() as f:
                GameState.update(json.load(f))
            LogCommand("Game loaded!", success=True)
        else: LogCommand("No save file", error=True)
    except: LogCommand("Load failed", error=True)

def CommandClear(_): History.clear()
def CommandStats(_):
    LogCommand(f"Level {GameState['level']} | ${GameState['money']} | Souls {GameState['souls']}")
    LogCommand(f"STR {GameState['attributes'][0]} INT {GameState['attributes'][1]} SPD {GameState['attributes'][2]} HP {GameState['attributes'][3]}")
    if GameState['inventory']:
        LogCommand(f"Inventory: {', '.join(GameState['inventory'])}")
    else: LogCommand("Inventory empty")

for cmd, func in [("help", CommandHelp),("save",CommandSave),("load",CommandLoad),("clear",CommandClear),("stats",CommandStats)]:
    RegisterCommand(cmd, func)


def SwitchState(state, msg=None):
    global ProgramState
    ProgramState = state
    if msg: LogCommand(msg)

def GetPrompt():
    prompts = {
        "MAIN_MENU":"Choice (1-7 or command): ",
        "STORE":"Buy item or EXIT: ",
        "CREATION_TYPE":"Type (Human/Dog/Goblin/Bear/CUSTOM): ",
        "CREATION_STRENGTH":"Strength: ","CREATION_INTELLIGENCE":"Intelligence: ",
        "CREATION_SPEED":"Speed: ","CREATION_HEALTH":"Health: ",
        "CREATION_SKIN":"Skin: ","CREATION_EYES":"Eyes: ",
        "CREATION_HEIGHT":"Height: ","CREATION_HUNTER":"Hunter: "
    }
    return prompts.get(ProgramState, f"[{ProgramState}] > ")

pygame.init()
screen = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Terminal RPG")
font = pygame.font.SysFont("consolas", FontSize)
small_font = pygame.font.SysFont("consolas", SmallFont)


logo = None
if LOGO_PATH.exists():
    try:
        logo = pygame.image.load(LOGO_PATH).convert_alpha()
        logo = pygame.transform.scale(logo,(180,180))
    except: logo=None

clock = pygame.time.Clock()
last_blink = 0
show_cursor = True


History.extend([
    "╔════════ RPG ════════╗",
    "1. Make Character   2. Store   3. Stats   7. Quit",
    "Type numbers or commands (help, save, load, clear, stats)."
])


while Running:
    current_time = pygame.time.get_ticks()/1000.0
    if current_time-last_blink>0.5:
        show_cursor = not show_cursor
        last_blink=current_time
    question = GetPrompt()

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            CommandSave("")
            Running=False
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_RETURN:
                cmd = Usertext.strip()
                LogCommand(f"{question}{cmd}")
                lower_cmd = cmd.lower()
                if lower_cmd in CommandHandle:
                    CommandHandle[lower_cmd](cmd)
                    Usertext=""
                    continue


                if ProgramState=="MAIN_MENU":
                    if cmd=="1": SwitchState("CREATION_TYPE","Character creation started")
                    elif cmd=="2": SwitchState("STORE")
                    elif cmd=="3": CommandStats("")
                    elif cmd=="7": CommandSave(""); Running=False
                    else: LogCommand("Invalid choice", error=True)

              
                elif ProgramState=="STORE":
                    if cmd.upper()=="EXIT": SwitchState("MAIN_MENU")
                    elif cmd in GameState["store"]:
                        price=GameState["store"][cmd]
                        if GameState["money"]>=price:
                            GameState["money"]-=price
                            GameState["inventory"].append(cmd)
                            LogCommand(f"Bought {cmd}",success=True)
                        else: LogCommand("Not enough money", error=True)
                    else: LogCommand("Item not found", error=True)


                elif ProgramState=="CREATION_TYPE":
                    if cmd.lower() in ["human","dog","goblin","bear"]:
                        GameState["character"]["type"]=cmd.title()
                        SwitchState("CREATION_STRENGTH")
                    elif cmd.lower()=="custom":
                        SwitchState("CREATION_STRENGTH")
                    else:
                        LogCommand("Invalid type",error=True)

                elif ProgramState=="CREATION_STRENGTH":
                    val=safe_int(cmd,0)
                    if val is None:
                        LogCommand("Enter number", error=True)
                    else:
                        GameState["attributes"][0] = val
                        SwitchState("CREATION_INTELLIGENCE")

                elif ProgramState=="CREATION_INTELLIGENCE":
                    val=safe_int(cmd,0)
                    if val is None:
                        LogCommand("Enter number", error=True)
                    else:
                        GameState["attributes"][1] = val
                        SwitchState("CREATION_SPEED")

                elif ProgramState=="CREATION_SPEED":
                    val=safe_int(cmd,0)
                    if val is None:
                        LogCommand("Enter number", error=True)
                    else:
                        GameState["attributes"][2] = val
                        SwitchState("CREATION_HEALTH")

                elif ProgramState=="CREATION_HEALTH":
                    val=safe_int(cmd,1)
                    if val is None:
                        LogCommand("Must be >=1", error=True)
                    else:
                        GameState["attributes"][3] = val
                        SwitchState("CREATION_SKIN")

                elif ProgramState=="CREATION_SKIN":
                    val = safe_text(cmd)
                    if val:
                        GameState["character"]["skin"] = val
                        SwitchState("CREATION_EYES")
                    else:
                        LogCommand("Invalid text", error=True)

                elif ProgramState=="CREATION_EYES":
                    val = safe_text(cmd)
                    if val:
                        GameState["character"]["eyes"] = val
                        SwitchState("CREATION_HEIGHT")
                    else:
                        LogCommand("Invalid text", error=True)

                elif ProgramState=="CREATION_HEIGHT":
                    val = safe_text(cmd)
                    if val:
                        GameState["character"]["height"] = val
                        SwitchState("CREATION_HUNTER")
                    else:
                        LogCommand("Invalid text", error=True)

                elif ProgramState=="CREATION_HUNTER":
                    val = safe_text(cmd)
                    if val:
                        GameState["character"]["hunter"] = val
                        LogCommand("Character created!", success=True)
                        for line in detailed_backstory().split("\n"):
                            LogCommand(line)
                        SwitchState("MAIN_MENU")
                    else:
                        LogCommand("Invalid text", error=True)

                Usertext=""

            elif event.key==pygame.K_BACKSPACE:
                Usertext=Usertext[:-1]

            elif event.key==pygame.K_ESCAPE:
                if ProgramState != "MAIN_MENU":
                    SwitchState("MAIN_MENU", "Cancelled")
                else:
                    CommandSave("")
                    Running = False

            elif event.unicode.isprintable() and len(Usertext)<CharacterLimit:
                Usertext+=event.unicode


    screen.fill(BackgroundColor)
    y_pos=YStartHistory
    start_idx=max(0,len(History)-VisibleLines)
    for i in range(VisibleLines):
        if start_idx+i>=len(History): break
        line=History[start_idx+i]
        color = ErrorColor if any(x in line.lower() for x in ["invalid","failed","error"]) else SuccessColor if "!" in line else HistoryColor
        screen.blit(font.render(line,True,color),(30,y_pos))
        y_pos+=LineHeight

    screen.blit(font.render(question,True,PromptColor),(30,y_pos))
    y_pos+=LineHeight
    cursor="_" if show_cursor else " "
    screen.blit(font.render("> "+Usertext+cursor,True,TextColor),(30,y_pos))


    if logo: screen.blit(logo,(Width-logo.get_width()-20,15))

    status=f"LVL:{GameState['level']} SOULS:{GameState['souls']} $:{GameState['money']} INV:{len(GameState['inventory'])} STATE:{ProgramState}"
    screen.blit(small_font.render(status,True,(90,90,110)),(30,Height-55))
    screen.blit(small_font.render("ESC=Cancel | Ctrl+V Paste | Ctrl+C Copy",True,(70,70,90)),(30,Height-32))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()