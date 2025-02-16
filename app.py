from tkinter import *

class app(Tk):
    def __init__(self) -> None:
        super().__init__()
        
        icon : PhotoImage = PhotoImage(file = "./calc.png")
        self.iconphoto(False, icon, icon)
        
        self.SetConfig()
        self.LoadSettings()
        self.LoadTabs()
        self.LoadDisplay()
        self.LoadHistory()
        
    def SetConfig(self) -> None:
        self.title("Calculator (Taha Ouroui)")
        self.geometry("300x400")
        self.resizable(False, False)
        self.bind("<KeyPress>", lambda event: self.OnKeyPressEvent(event))
        
    def LoadSettings(self) -> None:
        self.expression : str = ""
        self.clearNextInsertion : bool = False
        self.maxCharacters : int = 19
        self.maxHistoryLabels : int = 17
        self.history : list[tuple] = []
        self.historyLabels : list[Label] = []
        self.historyIndex : int = 0
        
    def LoadTabs(self) -> None:
        self.calcTab : Frame = Frame(self)
        self.calcTab.grid(row = 0, column = 0, columnspan = 4, sticky = "nsew")
        
        self.historyTab : Frame = Frame(self)
        self.historyTab.grid_forget()
        
        self.currentTab = self.calcTab
            
    def LoadDisplay(self) -> None:
        self.display : Label = Label(self.calcTab, font = ("Arial", 20, "bold"), fg = "black")
        self.display.grid(row = 0, column = 0, columnspan = 4, sticky = "e") # take the whole horizontal space
        
        buttons : list[tuple] = [ # a tuple of buttons (buttonText, row column, optional: colspan)
            ("7", 1, 0, "gray72"), ("8", 1, 1, "gray72"), ("9", 1, 2, "gray72"), ("/", 1, 3, "orange"),
            ("4", 2, 0, "gray72"), ("5", 2, 1, "gray72"), ("6", 2, 2, "gray72"), ("*", 2, 3, "orange"),
            ("1", 3, 0, "gray72"), ("2", 3, 1, "gray72"), ("3", 3, 2, "gray72"), ("-", 3, 3, "orange"),
            ("0", 4, 0, "gray72"), (".", 4, 1, "orange"), ("( )", 4, 2, "orange"), ("+", 4, 3, "orange"),
            ("C", 5, 0, "red2"), ("Del", 5, 1, "red2"), ("=", 5, 2, "DarkOrange1", 2)
        ]
        
        self.keymap : str = ""

        for text, row, col, bg, *extra in buttons:
            self.keymap += text if len(text) == 1 else ""
            colspan = extra[0] if len(extra) > 0 else 1
            self.CreateButton(text, row, col, bg, colspan)
            
    def LoadHistory(self) -> None:
        self.historyFrame : Frame = Frame(self.historyTab)
        self.historyFrame.grid(row = 0, column = 0, sticky="nsew")
        
    def CreateButton(self, text : str, row : int, col : int, bg : str, colspan : int = 1) -> None:
        btn : Button = Button(self.calcTab, text = text, font = ("Times new Roman", 18), width = 5, height = 2, bg = bg, fg = "black", command = lambda: self.OnButtonClick(text))
        btn.grid(row = row, column = col, columnspan = colspan, sticky="nsew")
        
        for i in range(6):
            self.grid_rowconfigure(i, weight = 1)
        for i in range(4):
            self.grid_columnconfigure(i, weight = 1)
            
    def IsUserInputFull(self) -> bool:
        return len(self.expression) >= self.maxCharacters

    def OnButtonClick(self, char : str) -> None:
        match char:
            case "C":
                self.SetEntryText("")
            case "Del":
                self.SetEntryText(self.expression[0:-1] if not self.clearNextInsertion else "")
            case "=":
                self.clearNextInsertion = True
                self.CalculateOperation()
            case "( )" | "(" | ")":
                if self.IsUserInputFull():
                    return
                
                self.AddParanthesis()
            case _: # has to be a regular digit
                if self.IsUserInputFull() or not char in self.keymap:
                    return

                self.SetEntryText(self.expression + char if not self.clearNextInsertion else char)
                self.clearNextInsertion = False
                
    def AddParanthesis(self) -> None:
        open_count = self.expression.count("(")
        close_count = self.expression.count(")")

        if open_count > close_count:
            # if there are more open parentheses then we add a closing one
            self.SetEntryText(self.expression + ")")
        else:
            # else, add an opening parenthesis
            self.SetEntryText(self.expression + "(")
            
    def CalculateOperation(self) -> None:
        try:
            result : str = str(eval(self.expression))
            self.AddToHistory(self.expression, result)
            self.SetEntryText("=" + result, "forest green")
        except Exception as e:
            if isinstance(e, ZeroDivisionError):
                self.SetEntryText("Can't do Zero Division", "red")
            elif isinstance(e, SyntaxError):
                self.SetEntryText("Invalid Syntax!", "red")
            else:
                print(f"LOG: Error occured of type ({type(e)}) {e}")
                self.SetEntryText("Something went wrong!", "red")
        
    def SetEntryText(self, text : str, color : str = "black") -> None:
        self.expression = text
        self.display.config(fg = color, text = text)
        
    def AddToHistory(self, operation : str, result : str) -> None:
        self.historyIndex += 1
        self.history.append((self.historyIndex, operation, result))
        
        if len(self.history) >= self.maxHistoryLabels:
            self.history.pop(0)
        
    def OnKeyPressEvent(self, event : Event) -> None:
        match event.keysym:
            case "h":
                self.ToggleTab()
            case "BackSpace":
                self.OnButtonClick("Del")
            case "Return":
                self.OnButtonClick("=")
            case "Delete":
                self.OnButtonClick("C")
            case _:
                self.OnButtonClick(event.char.lower())
                
    def ToggleTab(self):
        if self.currentTab == self.calcTab:
            self.calcTab.grid_forget()
            self.historyTab.grid(row = 0, column = 0, columnspan = 4, sticky = "nsew")
            self.currentTab = self.historyTab
            self.UpdateHistoryDisplay()
        else:
            self.historyTab.grid_forget()
            self.calcTab.grid(row = 0, column = 0, columnspan = 4, sticky = "nsew")
            self.currentTab = self.calcTab     

    def UpdateHistoryDisplay(self) -> None:
        for label in self.historyLabels:
            label.destroy()

        self.historyLabels.clear()
        
        for i in range(0, len(self.history)):
            operationTuple : tuple = self.history[i]
            label_text : str = f"{operationTuple[0]}. {operationTuple[1]} = {operationTuple[2]}"
            label : Label = Label(self.historyFrame, text = label_text, font=("Arial", 12, "bold"), fg = "forest green")
            label.grid(row = i, column = 0, sticky = "w")
            self.historyLabels.append(label)