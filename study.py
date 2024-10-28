from datetime import datetime, timezone
from fsrs import FSRS, Card, Rating 
import os
from json import JSONEncoder
import json
import re 
import shutil
from collections import deque
import tkinter as tk
from PIL import Image, ImageTk
#from typing import Optional, List 
indexedImages = "./indexedImages/"
unindexedImages = "./images/"
cardsFile = "./cards.json"
subjectsFile ="./subjects.txt"
f = FSRS()
#@dataclass
class RakkiCard:
    card : Card
    time_Created: datetime
    card_key: str
    subject: str
    def due_date(self): 
        return card.due
    def due_date_unix(self): 
        int(self.card.due.timestamp())
    def back(self): 
        return self.card_key+"back.png"
    def front(self): 
        return self.card_key+"front.png"
    def __init__(self, subject, time_created, card_key, card): 
        self.card = card 
        self.card_key = card_key
        self.due_date = card.due
        self.subject = subject 
        self.time_Created = time_created 
    def __str__(self):
        return (f"RakkiCard(subject='{self.subject}', "
                f"due_date='{self.due_date}', "
                f"due_date_unix={self.due_date_unix()}, "
                f"card_key='{self.card_key}')")

    def to_json(self):
        """Convert RakkiCard instance to JSON-compatible dictionary and serialize it to a JSON string."""
        print(self.time_Created)
        data = {
            "card": self.card.to_dict(),  # Assuming card has a to_json method
            "due_date": self.due_date.isoformat(),
            "time_Created": self.time_Created.isoformat(),
            "card_key": self.card_key,
            "subject": self.subject
        }
        return json.dumps(data, indent=4)

def from_json(json_data):
    """Deserialize JSON string into a RakkiCard instance."""
    data = json.loads(json_data)
    card = Card.from_dict(data["card"])  # Assuming card has a from_json method
    due_date = datetime.fromisoformat(data["due_date"])
    time_Created = datetime.fromisoformat(data["time_Created"])
    return RakkiCard(
        subject=data["subject"],
        time_created=time_Created,
        card_key=data["card_key"],
        card=card
    )

def index_images(folder_path: str) -> list[RakkiCard]: #Return a list of unique cards? \
    rakki_cards = [] 
    pattern = re.compile(r'(?P<subject>.+)-(?P<date>\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})-(?P<side>front)')
    for filename in os.listdir(folder_path):
        match = pattern.match(filename)
        if match: 
            subject = match.group('subject') 
            timeCreated = datetime.strptime(match.group('date'), "%Y-%m-%d_%H-%M-%S")
            cardbeg = filename[0:-9]
            current_rakki_card = RakkiCard(
                subject = subject, 
                time_created = timeCreated, 
                card_key = cardbeg, 
                card = Card() 
            )
            print(type(current_rakki_card.time_Created))
            rakki_cards.append(current_rakki_card)
            shutil.move(unindexedImages+cardbeg+"front.png", indexedImages+cardbeg+"front.png")
            shutil.move(unindexedImages+cardbeg+"back.png", indexedImages+cardbeg+"back.png")
    return rakki_cards
def store_cards(card_list:list[RakkiCard], filename:str): 
    """Store a list of cards to a json""" 
    print("Storing cards!")
    tempFile = filename+".bak"
    with open(tempFile,"w") as f: 
        json_data = [card.to_json() for card in card_list]
        f.write(json.dumps(json_data, indent=4))
    shutil.move(tempFile, filename)

def sort_deck(card_list: list[RakkiCard]):
    card_list = sorted(card_list, key=lambda x: x.due_date_unix) 
    return card_list # I think all i need to do is the former command it sorts it and then i dont need to return it, but i realized this later.  

def load_cards(datafile :str) ->dict: 
    """ Loads a list of cards from the json file"""
    card_decks = {}            
    with open(datafile, "r") as f: 
        json_data = json.load(f)
        for card_json in json_data:
            current_rakki_card = from_json(card_json)
            if(not (current_rakki_card.subject in card_decks)): 
                card_decks[current_rakki_card.subject] = []
            card_decks[current_rakki_card.subject].append(current_rakki_card)

    for key in card_decks: #If possible we should have that it is already sorted... 
        card_decks[key] = sort_deck(card_decks[key]) 

    return card_decks

def begin_studying(decks):
    app = ImageSwitcherApp(decks)
    app.mainloop()


def main():  #using main in the middle to seperate card sorting stuff from gui stuff
    card_decks = load_cards("data.json") # loads the existing cards from storage
    rkList = index_images("images") # makes a new list with the newly indexed cards, along with every card from the existing ones
    for key in card_decks:
        rkList += [card for card in card_decks[key]] 
    store_cards(rkList,"data.json") # stores the newly created deck into storage

    card_decks = load_cards("data.json") #remakes the deck as a dictionary, but now it includes the new and the old ones 
    for key in card_decks:  #prints them all out to make sure it works
        [print(card,"\n") for card in card_decks[key]] 
    # Need to rethink how im loading and exporting to json, does not seem efficient  
    
    begin_studying() 


class ImageSwitcherApp(tk.Tk):
    def __init__(self,decks):
        self.decks = decks 
        self.subjects = [key for key in self.decks]
        self.subjectIndex = 0 


        super().__init__()
        self.title("Image Switcher")
        self.geometry("800x600")  # Initial size

        # Load images
        self.image1 = Image.open("./images/image1.png")  # First image
        self.image2 = Image.open("./images/image2.png")  # Second image
        next_card() #this is going to instantly change what the former two are. 

        # Create a label to display the first image
        self.image_label = tk.Label(self)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Bind spacebar key event
        self.bind("<space>", self.update_state("space"))

        # Create buttons frame
        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create buttons
        self.buttons = []
        for text in ["Easy", "Good", "Hard", "Again"]:
            button = tk.Button(self.buttons_frame, text=text, command=lambda t=text: self.update_state(t))
            button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Keep track of the currently displayed image
        self.current_image = self.image1
        self.update_image(self.current_image)

        # Bind resize event
        self.bind("<Configure>", self.resize_components)


    def update_state(self, input: str): 
        #self.current_card will be the current card? 
        rating = Rating.Good 
        match input: 
            case "Good": 
                rating = Rating.Good
            case "Easy": 
                rating = rating.Easy
            case "Hard": 
                rating = rating.Hard
            case "Again": 
                rating = rating.Again
            case "Space": 
                self.current_image = image2
                update_image(self, self.current_image)
                #figure out edvutually how to make it show the buttons and have them disabled before 
            case "Stop":
                exit_game() 
            case _: 
                print("Invalid option?")
        self.current_card,review_log = f.review_card(card,rating) #idk what review_log is but it was in the github example for this 
        self.resortCards() 
        self.next_card() 

    def resortCard(self): 
        currentDeck = self.decks[self.subjects[self.subjectIndex]]
        sort_deck(currentDeck) #running just sort_deck should sort it, but ill need to make sure of this somehow
    def next_card(self): 
        cardNotFound = True 
        initializeIndex = self.subjectIndex 
        current_unix_time = init(datetime.now().timestamp())
        tolerance = 0 #will be used for determining weather you can study cards not yet due
        while(cardNotFound): 
            self.subjectIndex+=1 % len(self.subjects)
            currentDeck = self.decks[self.subjects[self.subjectIndex]]
            if(currentDeck[0].due_date_unix<=current_unix_time+tolerance): 
                cardNotFound = False 
                self.current_card = currentDeck[0]
                self.image1 = Image.open(self.current_card.front())  # First image
                self.current_image = image1 
                update_image(self,self.current_image)
                self.image2 = Image.open(self.current_card.back())  # Second image
                break 
            #need to go over the order at which things happen in this loop later to make sure its what i want 
            if(self.subjectIndex == initializeIndex): 
                tolerance+=86400 # Increments by One Day, this will edventually be customizable 
            if(tolerance>=86400*10): 
                #after tolerence increase by 10 days, itll probably be time to rest. But this will be subject to change 
                print("You finished!")
                exit_game() 

    def exit_game(self): 
        print("goodbye")
    def update_image(self, image):
        # Get the current dimensions of the window
        window_width = self.winfo_width()
        window_height = self.winfo_height() - 50  # Subtract space for buttons

        # Ensure that the dimensions are greater than zero
        if window_width <= 0 or window_height <= 0:
            return

        aspect_ratio = image.width / image.height
        if window_width / window_height > aspect_ratio:
            new_height = window_height
            new_width = int(aspect_ratio * new_height)
        else:
            new_width = window_width
            new_height = int(new_width / aspect_ratio)

        # Ensure that new dimensions are positive
        new_width = max(new_width, 1)
        new_height = max(new_height, 1)

        resized_image = image.resize((new_width, new_height))
        self.photo = ImageTk.PhotoImage(resized_image)
        self.image_label.config(image=self.photo)
        self.image_label.image = self.photo  # Keep a reference to avoid garbage collection

    def show_second_image(self, event):
        self.current_image = self.image2  # Switch to the second image
        self.update_image(self.current_image)  # Update the displayed image
        self.buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)  # Show buttons

    def resize_components(self, event):
        # Update the displayed image on resize
        self.update_image(self.current_image)

    def on_button_click(self, text):
        print(f"{text} button clicked!")
    def deckPrinter(self):
        for key in self.decks:  #prints them all out to make sure it works
            [print(card,"\n") for card in card_decks[key]]
main()
