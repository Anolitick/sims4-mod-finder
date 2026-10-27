
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser
import urllib.parse
import urllib.request
import json
import html
import re

APP_NAME = "Sims 4 Mod Finder"

CATEGORIES = {
    "Все моды": "The Sims 4 realistic life mods",
    "Реалистичная жизнь": "The Sims 4 realistic gameplay mods",
    "Отношения и романтика": "The Sims 4 relationship romance mods",
    "Семья и беременность": "The Sims 4 pregnancy family mods",
    "Карьера и финансы": "The Sims 4 career banking bills mods",
    "Драма и преступления": "The Sims 4 drama crime mods",
    "Моды 18+": "The Sims 4 adult mods 18+",
    "Одежда и внешность": "The Sims 4 custom content clothes hair",
    "Русификаторы": "The Sims 4 mod Russian translation"
}

def search_web(query):
    url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
    request = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            page = response.read().decode("utf-8", errors="ignore")
        links = re.findall(r'<a href="/url\?q=(https?://[^&"]+)', page)
        results = []
        for link in links:
            link = html.unescape(urllib.parse.unquote(link))
            if not any(domain in link.lower() for domain in
                       ["google.com", "youtube.com", "accounts.google"]):
                if link not in results:
                    results.append(link)
        return results[:15]
    except Exception:
        return []

class ModFinder:
    def __init__(self, root):
        self.root = root
        root.title(APP_NAME)
        root.geometry("850x580")

        ttk.Label(
            root, text="Поиск модов The Sims 4",
            font=("Arial", 18, "bold")
        ).pack(pady=12)

        options = ttk.Frame(root)
        options.pack(fill="x", padx=15)

        ttk.Label(options, text="Категория:").pack(side="left")
        self.category = tk.StringVar(value="Все моды")
        ttk.Combobox(
            options, textvariable=self.category,
            values=list(CATEGORIES.keys()), state="readonly", width=30
        ).pack(side="left", padx=8)

        ttk.Label(options, text="Поиск:").pack(side="left")
        self.query = tk.StringVar()
        ttk.Entry(options, textvariable=self.query, width=25).pack(
            side="left", padx=8
        )

        self.search_button = ttk.Button(
            root, text="Найти моды", command=self.search
        )
        self.search_button.pack(pady=12)

        self.status = tk.StringVar(value="Готов к поиску")
        ttk.Label(root, textvariable=self.status).pack()

        columns = ("name", "url")
        self.results = ttk.Treeview(
            root, columns=columns, show="headings", height=18
        )
        self.results.heading("name", text="Найденная страница")
        self.results.heading("url", text="Ссылка")
        self.results.column("name", width=280)
        self.results.column("url", width=500)
        self.results.pack(fill="both", expand=True, padx=15, pady=10)
        self.results.bind("<Double-1>", self.open_result)

    def search(self):
        category = CATEGORIES[self.category.get()]
        extra = self.query.get().strip()
        query = category + (" " + extra if extra else "")
        self.search_button.config(state="disabled")
        self.status.set("Ищу страницы в интернете...")
        for item in self.results.get_children():
            self.results.delete(item)
        threading.Thread(
            target=self.run_search, args=(query,), daemon=True
        ).start()

    def run_search(self, query):
        links = search_web(query)
        self.root.after(0, self.show_results, links)

    def show_results(self, links):
        for link in links:
            self.results.insert("", "end", values=(link, link))
        self.status.set(
            f"Найдено страниц: {len(links)}. "
            "Дважды нажми на строку, чтобы открыть страницу."
            if links else
            "Результатов нет. Поисковик мог заблокировать запрос."
        )
        self.search_button.config(state="normal")

    def open_result(self, event):
        selected = self.results.selection()
        if selected:
            values = self.results.item(selected[0], "values")
            if len(values) > 1:
                webbrowser.open(values[1])

if __name__ == "__main__":
    root = tk.Tk()
    app = ModFinder(root)
    root.mainloop()
