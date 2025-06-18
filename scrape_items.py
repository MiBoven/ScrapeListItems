import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox

def lade_html_von_url():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Fehler", "Bitte eine URL eingeben.")
        return
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_text.config(state="normal")
        html_text.delete("1.0", tk.END)
        html_text.insert("1.0", response.text)
    except Exception as e:
        messagebox.showerror("Fehler beim Abrufen", str(e))

def extract_texts():
    class_name = class_entry.get().strip()
    if not class_name:
        messagebox.showwarning("Fehler", "Bitte CSS-Klassen angeben.")
        return []

    html = html_text.get("1.0", tk.END).strip()
    if not html:
        messagebox.showwarning("Fehler", "Kein HTML-Code vorhanden.")
        return []

    classes = class_name.split()
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.find_all("span", class_=lambda value: value and all(c in value for c in classes))
    return [el.get_text(strip=True) for el in elements]

def scrape_and_save():
    texte = extract_texts()
    if not texte:
        messagebox.showinfo("Ergebnis", "Keine passenden Elemente gefunden.")
        return
    with open("ausgabe.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(texte))
    messagebox.showinfo("Erfolg", f"{len(texte)} Einträge in 'ausgabe.txt' gespeichert.")

def scrape_and_show():
    texte = extract_texts()
    ausgabe_field.config(state="normal")
    ausgabe_field.delete("1.0", tk.END)
    if texte:
        ausgabe_field.insert(tk.END, "\n".join(texte))
    else:
        ausgabe_field.insert(tk.END, "Keine passenden Elemente gefunden.")
    ausgabe_field.config(state="disabled")

# GUI Setup
root = tk.Tk()
root.title("HTML Text Extractor")

# URL-Zeile mit Button
url_frame = tk.Frame(root)
url_frame.pack(pady=5, anchor="w")

tk.Label(url_frame, text="Webseite URL:").pack(side="left")
url_entry = tk.Entry(url_frame, width=60)
url_entry.pack(side="left", padx=5)

tk.Button(url_frame, text="HTML anzeigen", command=lade_html_von_url).pack(side="left")

# HTML-Code-Eingabe
tk.Label(root, text="HTML-Code (manuell oder automatisch geladen):").pack(anchor="w")
html_text = tk.Text(root, height=12, width=90)
html_text.pack()

# CSS-Klassen
tk.Label(root, text="CSS-Klassen (z. B. 'font-mono text-[13px]'):").pack(anchor="w")
class_entry = tk.Entry(root, width=90)
class_entry.pack()

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Speichern", command=scrape_and_save).pack(side="left", padx=5)
tk.Button(button_frame, text="Anzeigen", command=scrape_and_show).pack(side="left", padx=5)

# Ausgabe
tk.Label(root, text="Ausgabe:").pack(anchor="w")
ausgabe_field = tk.Text(root, height=15, width=90, state="disabled", bg="#f0f0f0")
ausgabe_field.pack()

root.mainloop()
