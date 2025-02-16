from app import app

if __name__ == "__main__":
    print("Initiating app...")
    calculator : app = app()
    
    print("app initiated!")
    calculator.mainloop()
    
    print("app closed...")