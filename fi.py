''''
Here is a Widget I wrote to a Swedish daytrader in <1h
'''
try:
    import Tkinter as tk
    import tkFont
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    import tkinter.font as tkFont
    import tkinter.ttk as ttk

import datetime
import requests
import os
from decimal import *
from bs4 import BeautifulSoup
import locale

locale.setlocale(locale.LC_ALL, '')

class MultiColumnListbox(object):
    """use a ttk.TreeView as a multicolumn ListBox"""

    def __init__(self):
        self.tree = None
        self.msg = None
        self.textBox = None
        self._setup_widgets()
        self._build_tree()

    def _setup_widgets(self):
        s = datetime.datetime.now()
        self.msg = ttk.Label(wraplength="4i", justify="left", anchor="n",
            padding=(10, 2, 10, 6), text=s)
        self.msg.pack(fill='x')
        container = ttk.Frame()
        container.pack(fill='both', expand=True)
        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(columns=car_header, show="headings")
        vsb = ttk.Scrollbar(orient="vertical",
            command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal",
            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
            xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

    def _build_tree(self):
        for col in car_header:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                width=tkFont.Font().measure(col.title()))

        for item in data:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(car_header[ix],width=None)<col_w:
                    self.tree.column(car_header[ix], width=col_w)

    # the test data ...
    def refresh(self):
        try:
            url = "https://marknadssok.fi.se/publiceringsklient/sv-SE/Search/Search?SearchFunctionType=Insyn&Utgivare=&PersonILedandeSt%C3%A4llningNamn=&Transaktionsdatum.From=&Transaktionsdatum.To=&Publiceringsdatum.From=&Publiceringsdatum.To=&button=search&Page=1"  # change to whatever your url is

            response = requests.get(url)
            soup = BeautifulSoup(response.text, features='html.parser')
            data = []

            for tr in soup.find_all('tr')[1:]:
                tds = tr.find_all('td')
                #print (tds[0].text, tds[5].text, '\t->\t', tds[1].text, '(', tds[8].text, ')', '\t\tVol:', tds[9].text, 'Pris:', tds[11].text, '(', tds[3].text, ':',tds[2].text, ')',tds[4].text )
                money = 0
                try:
                    money = round(Decimal(tds[11].text.replace(',','.')) * Decimal(tds[9].text.replace(',','.')))
                except Exception as e:
                    print("type error: " + str(e))
                    money = 0
                values= (tds[0].text, tds[5].text, tds[1].text, tds[8].text, 'Vol: ' + tds[9].text + ' Pris: '+ tds[11].text, "{0:n}".format(money), tds[3].text + ' (' + tds[2].text + ')', tds[13].text, tds[4].text, tds[7].text, tds[10].text, tds[12].text )
                data.append(values)
            root.after(60000, listbox.refresh)
            self.tree.delete(*self.tree.get_children())
            for item in data:
                self.tree.insert('', 'end', values=item)
                # adjust column's width if necessary to fit each value
                for ix, val in enumerate(item):
                    col_w = tkFont.Font().measure(val)
                    if self.tree.column(car_header[ix],width=None)<col_w:
                        self.tree.column(car_header[ix], width=col_w)
            self.msg['text'] = datetime.datetime.now()
        except StopIteration:
            root.destroy()

def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) \
        for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    #data =  change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, \
        int(not descending)))

car_header = ['Datum', 'Trans', 'Aktie', 'Trans datum', 'Vol@Pris', 'Sum', 'Titel (namn)', 'Handelsplats', 'Närstående', 'ISIN', 'Volymsenhet', 'Valuta']
data = []

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Insynslistan")
    listbox = MultiColumnListbox()
    listbox.refresh()
    root.after(60000, listbox.refresh)
    root.mainloop()
