import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog
import threading
import datetime

# Global variable to store loaded HTML code
loaded_html_code = ""

def log_action(action, status, extra=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action} - {status}"
    if extra:
        log_entry += f" | {extra}"
    with open("log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry + "\n")

def load_html_from_url():
    global loaded_html_code
    url = url_entry.get().strip()
    if not url:
        status_label.config(text="Bitte eine URL eingeben.", fg="red")
        log_action("HTML laden", "Fehler", "Keine URL angegeben")
        return
    try:
        button_load_html.config(state="disabled")
        status_label.config(text="Lade HTML...", fg="blue")
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
        status_label.config(text="HTML erfolgreich geladen", fg="green")
        log_action("HTML laden", "Erfolg", f"URL: {url}")
    except requests.exceptions.HTTPError as e:
        status_label.config(text=f"HTTP Fehler: {e.response.status_code}", fg="red")
        log_action("HTML laden", "HTTP Fehler", f"Status {e.response.status_code}: {e}")
    except Exception as e:
        status_label.config(text="Fehler beim Laden", fg="red")
        log_action("HTML laden", "Fehler", f"{type(e).__name__}: {e}")
    finally:
        button_load_html.config(state="normal")

def load_html_threaded():
    threading.Thread(target=load_html_from_url).start()

def show_html_popup():
    if not loaded_html_code:
        status_label.config(text="Kein HTML im Speicher", fg="red")
        log_action("HTML anzeigen", "Fehler", "Kein HTML im Speicher")
        return

    html_window = tk.Toplevel(root)
    html_window.title("Geladener HTML-Code")

    scrollbar = tk.Scrollbar(html_window)
    scrollbar.pack(side="right", fill="y")

    text_widget = tk.Text(html_window, wrap="none", yscrollcommand=scrollbar.set)
    text_widget.insert("1.0", loaded_html_code)
    text_widget.config(state="disabled")
    text_widget.pack(expand=True, fill="both")

    scrollbar.config(command=text_widget.yview)
    log_action("HTML anzeigen", "Erfolg")

def toggle_manual_mode():
    if manual_mode_var.get():
        html_text.config(state="normal")
        html_text.delete("1.0", tk.END)
        html_text.insert("1.0", "<!-- Hier eigenen HTML-Code einfügen -->")
    else:
        html_text.delete("1.0", tk.END)
        html_text.config(state="disabled")

def extract_texts():
    tag = tag_var.get()
    search_tag = True if tag == "*" else tag
    search_type = search_type_var.get()
    identifier = identifier_entry.get().strip()

    if not identifier:
        status_label.config(text="Kein Wert für Suche angegeben", fg="red")
        log_action("Extraktion", "Fehler", f"{search_type} leer")
        return []

    html = html_text.get("1.0", tk.END).strip() if manual_mode_var.get() else loaded_html_code.strip()
    if not html:
        status_label.config(text="Kein HTML vorhanden", fg="red")
        log_action("Extraktion", "Fehler", "Kein HTML vorhanden")
        return []

    soup = BeautifulSoup(html, "html.parser")

    if search_type == "class":
        classes = identifier.split()
        elements = soup.find_all(search_tag, class_=lambda value: value and all(c in value for c in classes))
    else:
        elements = soup.find_all(search_tag, id=identifier)

    log_action("Extraktion", "Erfolg", f"Tag: {tag}, {search_type}: {identifier}, Treffer: {len(elements)}")
    return [el.get_text(strip=True) for el in elements]

def scrape_and_save():
    texts = extract_texts()
    if not texts:
        status_label.config(text="Keine passenden Elemente gefunden", fg="orange")
        return

    filepath = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")],
        title="Speichern unter..."
    )
    if not filepath:
        status_label.config(text="Speichern abgebrochen", fg="orange")
        return

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(texts))
        status_label.config(text=f"{len(texts)} Elemente gespeichert", fg="green")
        log_action("Speichern", "Erfolg", f"Datei: {filepath}")
    except Exception as e:
        status_label.config(text="Fehler beim Speichern", fg="red")
        log_action("Speichern", "Fehler", f"{type(e).__name__}: {e}")

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
    log_action("Anzeigen", "Erfolg", f"{len(texts)} Elemente angezeigt")

# GUI Setup
root = tk.Tk()
root.title("HTML Item Extractor")

url_frame = tk.Frame(root)
url_frame.pack(pady=5, anchor="w")

tk.Label(url_frame, text="Webseite URL:").pack(side="left")
url_entry = tk.Entry(url_frame, width=60)
url_entry.pack(side="left", padx=5)

button_load_html = tk.Button(url_frame, text="HTML laden", command=load_html_threaded)
button_load_html.pack(side="left", padx=5)

tk.Button(url_frame, text="HTML anzeigen", command=show_html_popup).pack(side="left")

status_label = tk.Label(url_frame, text="", fg="green")
status_label.pack(side="left", padx=10)

manual_mode_var = tk.BooleanVar(value=False)
tk.Checkbutton(root, text="HTML manuell eingeben", variable=manual_mode_var, command=toggle_manual_mode).pack(anchor="w")

tk.Label(root, text="HTML-Code (optional manuell bearbeitbar):").pack(anchor="w")
html_frame = tk.Frame(root)
html_frame.pack()
html_scrollbar = tk.Scrollbar(html_frame)
html_scrollbar.pack(side="right", fill="y")

html_text = tk.Text(html_frame, height=12, width=90, yscrollcommand=html_scrollbar.set)
html_text.pack(side="left", fill="both", expand=True)
html_scrollbar.config(command=html_text.yview)
html_text.config(state="disabled")

options_frame = tk.Frame(root)
options_frame.pack(pady=5)

tk.Label(options_frame, text="HTML-Tag:").grid(row=0, column=0, sticky="w")
tag_var = tk.StringVar(value="*")
tk.OptionMenu(options_frame, tag_var, "*", "span", "div").grid(row=0, column=1, padx=10)

tk.Label(options_frame, text="Suche nach:").grid(row=0, column=2, sticky="w")
search_type_var = tk.StringVar(value="class")
tk.OptionMenu(options_frame, search_type_var, "class", "id").grid(row=0, column=3, padx=10)

tk.Label(options_frame, text="Wert (z.\u202fB. CSS-Klassen oder ID):").grid(row=1, column=0, sticky="w", pady=5)
identifier_entry = tk.Entry(options_frame, width=60)
identifier_entry.grid(row=1, column=1, columnspan=3, pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text="Speichern", command=scrape_and_save).pack(side="left", padx=5)
tk.Button(button_frame, text="Anzeigen", command=scrape_and_show).pack(side="left", padx=5)

label_output = tk.Label(root, text="Ausgabe (0 Elemente)")
label_output.pack(anchor="w")

output_frame = tk.Frame(root)
output_frame.pack()
output_scrollbar = tk.Scrollbar(output_frame)
output_scrollbar.pack(side="right", fill="y")

textfield_output = tk.Text(output_frame, height=15, width=90, state="disabled", bg="#f0f0f0", yscrollcommand=output_scrollbar.set)
textfield_output.pack(side="left", fill="both", expand=True)
output_scrollbar.config(command=textfield_output.yview)

root.mainloop()
