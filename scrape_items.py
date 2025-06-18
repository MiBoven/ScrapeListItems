import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, filedialog
import threading

# Global variable to store loaded HTML code
loaded_html_code = ""

def load_html_from_url():
    global loaded_html_code
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Fehler", "Bitte eine URL eingeben.")
        return
    try:
        button_load_html.config(state="disabled")
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        loaded_html_code = response.text
        messagebox.showinfo("Erfolg", "HTML wurde erfolgreich geladen.")
    except Exception as e:
        messagebox.showerror("Fehler beim Abrufen", str(e))
    finally:
        button_load_html.config(state="normal")

def load_html_threaded():
    threading.Thread(target=load_html_from_url).start()

def show_html():
    global loaded_html_code
    if not loaded_html_code:
        messagebox.showinfo("Hinweis", "Kein HTML im Speicher. Erst laden.")
        return
    html_text.config(state="normal")
    html_text.delete("1.0", tk.END)
    html_text.insert("1.0", loaded_html_code)
    html_text.config(state="disabled")

def extract_texts():
    tag = tag_var.get()
    search_type = search_type_var.get()
    identifier = identifier_entry.get().strip()

    if not identifier:
        messagebox.showwarning("Fehler", f"Bitte einen {search_type}-Wert angeben.")
        return []

    html = loaded_html_code.strip()
    if not html:
        messagebox.showwarning("Fehler", "Kein HTML-Code im Speicher.")
        return []

    soup = BeautifulSoup(html, "html.parser")

    if search_type == "class":
        classes = identifier.split()
        elements = soup.find_all(tag, class_=lambda value: value and all(c in value for c in classes))
    else:
        elements = soup.find_all(tag, id=identifier)

    return [el.get_text(strip=True) for el in elements]

def scrape_and_save():
    texts = extract_texts()
    if not texts:
        messagebox.showinfo("Ergebnis", "Keine passenden Elemente gefunden.")
        return

    filepath = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")],
        title="Speichern unter..."
    )
    if not filepath:
        return

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(texts))
        messagebox.showinfo("Erfolg", f"{len(texts)} Einträge gespeichert in:\n{filepath}")
    except Exception as e:
        messagebox.showerror("Fehler beim Speichern", str(e))

def scrape_and_show():
    texts = extract_texts()
    textfield_output.config(state="normal")
    textfield_output.delete("1.0", tk.END)
    if texts:
        textfield_output.insert(tk.END, "\n".join(texts))
    else:
        textfield_output.insert(tk.END, "Keine passenden Elemente gefunden.")
    textfield_output.config(state="disabled")
    label_output.config(text=f"Ausgabe ({len(texts)} Elemente)")

# GUI Setup
root = tk.Tk()
root.title("HTML Item Extractor")

# URL column with buttons
url_frame = tk.Frame(root)
url_frame.pack(pady=5, anchor="w")

tk.Label(url_frame, text="Webseite URL:").pack(side="left")
url_entry = tk.Entry(url_frame, width=60)
url_entry.pack(side="left", padx=5)

button_load_html = tk.Button(url_frame, text="HTML laden", command=load_html_threaded)
button_load_html.pack(side="left", padx=5)

tk.Button(url_frame, text="HTML anzeigen", command=show_html).pack(side="left")

# HTML code display area
tk.Label(root, text="HTML-Code (manuell oder über Button anzeigen):").pack(anchor="w")
html_frame = tk.Frame(root)
html_frame.pack()
html_scrollbar = tk.Scrollbar(html_frame)
html_scrollbar.pack(side="right", fill="y")

html_text = tk.Text(html_frame, height=12, width=90, yscrollcommand=html_scrollbar.set)
html_text.pack(side="left", fill="both", expand=True)
html_scrollbar.config(command=html_text.yview)
html_text.config(state="disabled")

# Options for scraping
options_frame = tk.Frame(root)
options_frame.pack(pady=5)

tk.Label(options_frame, text="HTML-Tag:").grid(row=0, column=0, sticky="w")
tag_var = tk.StringVar(value="span")
tk.OptionMenu(options_frame, tag_var, "span", "div").grid(row=0, column=1, padx=10)

tk.Label(options_frame, text="Suche nach:").grid(row=0, column=2, sticky="w")
search_type_var = tk.StringVar(value="class")
tk.OptionMenu(options_frame, search_type_var, "class", "id").grid(row=0, column=3, padx=10)

tk.Label(options_frame, text="Wert (z. B. CSS-Klassen oder ID):").grid(row=1, column=0, sticky="w", pady=5)
identifier_entry = tk.Entry(options_frame, width=60)
identifier_entry.grid(row=1, column=1, columnspan=3, pady=5)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text="Speichern", command=scrape_and_save).pack(side="left", padx=5)
tk.Button(button_frame, text="Anzeigen", command=scrape_and_show).pack(side="left", padx=5)

# Output area
label_output = tk.Label(root, text="Ausgabe (0 Elemente)")
label_output.pack(anchor="w")

output_frame = tk.Frame(root)
output_frame.pack()
output_scrollbar = tk.Scrollbar(output_frame)
output_scrollbar.pack(side="right", fill="y")

textfield_output = tk.Text(output_frame, height=15, width=90, state="disabled", bg="#f0f0f0", yscrollcommand=output_scrollbar.set)
textfield_output.pack(side="left", fill="both", expand=True)
output_scrollbar.config(command=textfield_output.yview)

# Start GUI
root.mainloop()
