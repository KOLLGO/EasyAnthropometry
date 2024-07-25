import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import time

filename = None
root = None
screenheight = None
screenwidth = None
scroll_canvas = None

class ZoomableCanvas(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        super().__init__( parent, *args, **kwargs)
        self.parent = parent

        if filename:
            self.original_image = Image.open(filename)
            self.image = ImageTk.PhotoImage(self.original_image)
            self.image_id = self.create_image(0, 0, anchor='nw', image=self.image)

            self.scale = 1.0
            self.bind("<Control-MouseWheel>", self.zoom)
            self.last_zoom_time = 0

    def zoom(self, event):
        current_time = time.time()
        if current_time - self.last_zoom_time < 0.1:
            return

        self.last_zoom_time = current_time

        if event.delta:
            scale_factor = 1.1 if event.delta > 0 else 0.9
        else:
            scale_factor = 1.1 if event.num == 5 else 0.9

        self.scale *= scale_factor

        width, height = int(self.original_image.width * self.scale), int(self.original_image.height * self.scale)
        resized_image = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(resized_image)

        self.delete(self.image_id)
        self.image_id = self.create_image(0, 0, anchor='nw', image=self.image)
        self.configure(scrollregion=self.bbox(self.image_id))

class AutoScrollbar(tk.Scrollbar):
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        tk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError("Cannot use pack with this widget")

    def place(self, **kw):
        raise tk.TclError("Cannot use place with this widget")

class ScrollableCanvas(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.image_path = filename

        # Create the canvas
        self.canvas = ZoomableCanvas(self, self, bd=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.original_image = Image.open(filename)
        self.image = ImageTk.PhotoImage(self.original_image)
        self.canvas.config(width=screenwidth, height=screenheight)

        # Create horizontal and vertical scrollbars
        self.v_scrollbar = AutoScrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.h_scrollbar = AutoScrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Configure scroll region
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        # Bind mouse wheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self.on_shift_mouse_wheel)

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_shift_mouse_wheel(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

class Toolbar(tk.Menu):
    def initToolbar(self):
        #-----------Menu---------------
        menu = tk.Menu(root)
        root.config(menu=menu)
        file_menu = tk.Menu(menu)
        tools_menu = tk.Menu(menu)

        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.openFile)
        file_menu.add_command(label="Export as CSV", command=self.exportFile)
        file_menu.add_separator()
        file_menu.add_command(label="Close", command=self.closeFile)

        menu.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Select (S)", command=self.toolSelect)
        tools_menu.add_command(label="Move (M)", command=self.toolMove)
        tools_menu.add_command(label="Draw (D)", command=self.toolDraw)

    def openFile(self):
        global filename
        filename = filedialog.askopenfilename(initialdir="./", title="Choose an Image")
        global scroll_canvas
        scroll_canvas = ScrollableCanvas(root)
        scroll_canvas.grid(row=0, column=0, sticky="nsew")

    def exportFile(self):
        pass

    def closeFile(self):
        exit()

    def toolSelect(self):
        pass

    def toolMove(self):
        pass

    def toolDraw(self):
        pass

def main():
    global root
    root = tk.Tk()

    global screenwidth
    screenwidth = root.winfo_screenwidth()

    global screenheight
    screenheight = root.winfo_screenheight()

    root.geometry(str(screenwidth) + "x" + str(screenheight))
    root.title("Easy Anthropometry")
    root.iconbitmap('./assets/EasyAnthropometryLogo.ico')

    global filename
    filename = filedialog.askopenfilename(initialdir="./", title="Choose an Image")

    toolbar = Toolbar(root)
    toolbar.initToolbar()

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    global scroll_canvas
    scroll_canvas = ScrollableCanvas(root)
    scroll_canvas.grid(row=0, column=0, sticky="nsew")

    root.mainloop()


if __name__ == "__main__":
    main()
