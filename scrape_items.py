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
    tag = tag_var.get()
    search_type = search_type_var.get()
    identifier = identifier_entry.get().strip()

    if not identifier:
        messagebox.showwarning("Fehler", f"Bitte einen {search_type}-Wert angeben.")
        return []

    html = html_text.get("1.0", tk.END).strip()
    if not html:
        messagebox.showwarning("Fehler", "Kein HTML-Code vorhanden.")
        return []

    soup = BeautifulSoup(html, "html.parser")

    if search_type == "class":
        classes = identifier.split()
        elements = soup.find_all(tag, class_=lambda value: value and all(c in value for c in classes))
    else:  # id
        elements = soup.find_all(tag, id=identifier)

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

# HTML-Code mit Scrollbar
tk.Label(root, text="HTML-Code (manuell oder automatisch geladen):").pack(anchor="w")
html_frame = tk.Frame(root)
html_frame.pack()
html_scrollbar = tk.Scrollbar(html_frame)
html_scrollbar.pack(side="right", fill="y")

html_text = tk.Text(html_frame, height=12, width=90, yscrollcommand=html_scrollbar.set)
html_text.pack(side="left", fill="both", expand=True)
html_scrollbar.config(command=html_text.yview)

# Optionen: Tag + Suchtyp
options_frame = tk.Frame(root)
options_frame.pack(pady=5)

# HTML-Tag Dropdown
tk.Label(options_frame, text="HTML-Tag:").grid(row=0, column=0, sticky="w")
tag_var = tk.StringVar(value="span")
tag_menu = tk.OptionMenu(options_frame, tag_var, "span", "div")
tag_menu.grid(row=0, column=1, padx=10)

# Suchtyp Dropdown
tk.Label(options_frame, text="Suche nach:").grid(row=0, column=2, sticky="w")
search_type_var = tk.StringVar(value="class")
search_type_menu = tk.OptionMenu(options_frame, search_type_var, "class", "id")
search_type_menu.grid(row=0, column=3, padx=10)

# Klassen- oder ID-Wert
tk.Label(options_frame, text="Wert (z. B. CSS-Klassen oder ID):").grid(row=1, column=0, sticky="w", pady=5)
identifier_entry = tk.Entry(options_frame, width=60)
identifier_entry.grid(row=1, column=1, columnspan=3, pady=5)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text="Speichern", command=scrape_and_save).pack(side="left", padx=5)
tk.Button(button_frame, text="Anzeigen", command=scrape_and_show).pack(side="left", padx=5)

# Ausgabe mit Scrollbar
tk.Label(root, text="Ausgabe:").pack(anchor="w")
output_frame = tk.Frame(root)
output_frame.pack()
output_scrollbar = tk.Scrollbar(output_frame)
output_scrollbar.pack(side="right", fill="y")

ausgabe_field = tk.Text(output_frame, height=15, width=90, state="disabled", bg="#f0f0f0", yscrollcommand=output_scrollbar.set)
ausgabe_field.pack(side="left", fill="both", expand=True)
output_scrollbar.config(command=ausgabe_field.yview)

# Start GUI
root.mainloop()
