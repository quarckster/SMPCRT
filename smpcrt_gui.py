#!/usr/bin/env python

import smpcrt
import os
import threading
import ScrolledText
import tkFileDialog
import tkMessageBox
import ttk
import sys
import Tkinter


class StdoutRedirector:

    def __init__(self, text_area):
        self.text_area = text_area

    def write(self, str):
        self.text_area.configure(state=Tkinter.NORMAL)
        self.text_area.insert(Tkinter.END, str)
        self.text_area.see(Tkinter.END)
        self.text_area.configure(state=Tkinter.DISABLED)


class Window(Tkinter.Frame, StdoutRedirector):

    def __init__(self, root):

        Tkinter.Frame.__init__(self, root)

        widgets_opt = {"sticky": Tkinter.W, "padx": 5, "pady": 5}

        estyle = ttk.Style()
        estyle.element_create("plain.field", "from", "clam")
        estyle.layout("EntryStyle.TEntry",
                      [("Entry.plain.field", {"children": [(
                          "Entry.background", {"children": [(
                              "Entry.padding", {"children": [(
                                  "Entry.textarea", {"sticky": "nswe"})],
                                  "sticky": "nswe"})], "sticky": "nswe"})],
                          "border": "2", "sticky": "nswe"})])
        estyle.configure("EntryStyle.TEntry",
                         background="white",
                         foreground="black")
        self.api_key = Tkinter.StringVar()
        self.api_key.set("sample_key")
        self.inputFile = Tkinter.StringVar()
        self.outputFile = Tkinter.StringVar()
        self.inputButton = ttk.Button(self,
                                      text="Choose input file",
                                      width=20,
                                      command=self.askopenfilename)
        self.inputButton.grid(row=0,
                              column=0,
                              **widgets_opt)
        ttk.Entry(self,
                  state="readonly",
                  style="EntryStyle.TEntry",
                  width=50,
                  textvariable=self.inputFile).grid(row=0,
                                                    column=1,
                                                    **widgets_opt)
        self.outputButton = ttk.Button(self,
                                       text="Choose output file",
                                       width=20,
                                       command=self.asksaveasfilename)
        self.outputButton.grid(row=1,
                               column=0,
                               **widgets_opt)
        ttk.Entry(self,
                  state="readonly",
                  style="EntryStyle.TEntry",
                  width=50,
                  textvariable=self.outputFile).grid(row=1,
                                                     column=1,
                                                     **widgets_opt)
        self.getDataButton = ttk.Button(self,
                                        text="Get Data",
                                        width=20,
                                        command=self.getData)
        self.getDataButton.grid(row=3,
                                columnspan=2,
                                padx=5,
                                pady=5)
        ttk.Label(self,
                  text="Insert your api key").grid(row=2,
                                                   column=0,
                                                   **widgets_opt)
        ttk.Entry(self,
                  style="EntryStyle.TEntry",
                  width=50,
                  textvariable=self.api_key).grid(row=2,
                                                  column=1,
                                                  **widgets_opt)
        outputPanel = ScrolledText.ScrolledText(self,
                                                wrap="word",
                                                height=15,
                                                width=50,
                                                state=Tkinter.DISABLED)
        outputPanel.grid(row=5,
                         columnspan=2,
                         sticky="NSWE",
                         padx=5,
                         pady=5)
        sys.stdout = StdoutRedirector(outputPanel)
        self.file_opt = options = {}
        options["defaultextension"] = ".csv"
        options["filetypes"] = [("Comma separated values files", ".csv")]
        options["initialdir"] = os.path.expanduser("~")
        options["parent"] = root
        options["title"] = "Choose file"
        self.emails = []
        self.output = ""

    def askopenfilename(self):
        filename = tkFileDialog.askopenfile(**self.file_opt)
        if filename:
            self.inputFile.set(os.path.normpath(filename.name))
            self.emails = smpcrt.getEmailsFromCsv(filename.name)

    def asksaveasfilename(self):
        filename = tkFileDialog.asksaveasfilename(**self.file_opt)
        if filename:
            self.outputFile.set(os.path.normpath(filename))
            self.output = filename

    def getData(self):
        if self.inputFile.get() == self.outputFile.get() == "":
            tkMessageBox.showerror(
                "Error", "Please choose input and output files")
        else:
            responses = threading.Thread(target=self.wrap)
            responses.start()

    def wrap(self):
        self.inputButton.configure(state=Tkinter.DISABLED)
        self.outputButton.configure(state=Tkinter.DISABLED)
        self.getDataButton.configure(state=Tkinter.DISABLED)
        responses = smpcrt.getPiplObjects(self.emails, self.api_key.get())
        if responses:
            profiles = smpcrt.getProfilesFromResponse(self.emails, responses)
            smpcrt.writeOutputToCsv(profiles, self.output)
        self.inputButton.configure(state=Tkinter.NORMAL)
        self.outputButton.configure(state=Tkinter.NORMAL)
        self.getDataButton.configure(state=Tkinter.NORMAL)

if __name__ == "__main__":
    old_stdout = sys.stdout
    root = Tkinter.Tk()
    root.title("SMPCRT")
    root.resizable(width=Tkinter.FALSE, height=Tkinter.FALSE)
    Window(root).grid()
    root.mainloop()
    sys.stdout = old_stdout
