import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox

def scrape_and_save():
    url = url_entry.get()
    class_name = class_entry.get()
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Laden der Seite:\n{e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Klassenname splitten (z. B. "font-mono text-[13px]")
    classes = class_name.split()
    # Nur <span>-Tags mit genau diesen Klassen
    elements = soup.find_all("span", class_=lambda value: value and all(c in value for c in classes))
    
    texte = [el.get_text(strip=True) for el in elements]
    
    if not texte:
        messagebox.showinfo("Ergebnis", "Keine passenden Elemente gefunden.")
        return

    with open("ausgabe.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(texte))

    messagebox.showinfo("Erfolg", f"{len(texte)} Einträge in 'ausgabe.txt' gespeichert.")

# GUI Setup
root = tk.Tk()
root.title("HTML Text Extractor")

tk.Label(root, text="Webseite URL:").pack()
url_entry = tk.Entry(root, width=60)
url_entry.pack()

tk.Label(root, text="CSS-Klassen (z. B. 'font-mono text-[13px]'):").pack()
class_entry = tk.Entry(root, width=60)
class_entry.pack()

tk.Button(root, text="Speichern", command=scrape_and_save).pack(pady=10)

root.mainloop()
