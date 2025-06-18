import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox

def get_html_content():
    mode = mode_var.get()
    if mode == "url":
        url = url_entry.get().strip()
        if not url:
            messagebox.showwarning("Fehler", "Bitte eine URL eingeben.")
            return None
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            messagebox.showerror("Fehler beim Abrufen", str(e))
            return None
    else:
        html = html_text.get("1.0", tk.END).strip()
        if not html:
            messagebox.showwarning("Fehler", "Bitte HTML-Code eingeben.")
            return None
        return html

def extract_texts():
    class_name = class_entry.get().strip()
    if not class_name:
        messagebox.showwarning("Fehler", "Bitte CSS-Klassen angeben.")
        return []

    html = get_html_content()
    if html is None:
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

def toggle_input_fields():
    if mode_var.get() == "url":
        url_entry.config(state="normal")
        html_text.config(state="disabled")
    else:
        url_entry.config(state="disabled")
        html_text.config(state="normal")

# GUI Setup
root = tk.Tk()
root.title("HTML Text Extractor")

mode_var = tk.StringVar(value="url")

tk.Label(root, text="Modus wählen:").pack(anchor="w")
tk.Radiobutton(root, text="Von Webseite laden", variable=mode_var, value="url", command=toggle_input_fields).pack(anchor="w")
tk.Radiobutton(root, text="HTML manuell einfügen", variable=mode_var, value="html", command=toggle_input_fields).pack(anchor="w")

tk.Label(root, text="Webseite URL:").pack(anchor="w")
url_entry = tk.Entry(root, width=80)
url_entry.pack()

tk.Label(root, text="ODER HTML-Code:").pack(anchor="w")
html_text = tk.Text(root, height=10, width=80, state="disabled")
html_text.pack()

tk.Label(root, text="CSS-Klassen (z. B. 'font-mono text-[13px]'):").pack(anchor="w")
class_entry = tk.Entry(root, width=80)
class_entry.pack()

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Speichern", command=scrape_and_save).pack(side="left", padx=5)
tk.Button(button_frame, text="Anzeigen", command=scrape_and_show).pack(side="left", padx=5)

tk.Label(root, text="Ausgabe:").pack(anchor="w")
ausgabe_field = tk.Text(root, height=15, width=80, state="disabled", bg="#f0f0f0")
ausgabe_field.pack()

toggle_input_fields()
root.mainloop()
