import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from pdf2image import convert_from_path

class PDFBoundingBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Bounding Box Tool")

        # Frame for canvas and scrollbars
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame, cursor="cross", bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        self.v_scroll = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.h_scroll = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.canvas.bind('<Configure>', self.update_scroll_region)

        # Menu
        self.menu = tk.Menu(root)
        self.menu.add_command(label="Open PDF", command=self.open_pdf)
        self.root.config(menu=self.menu)

        self.tk_image = None
        self.image = None
        self.rect = None
        self.start_x = self.start_y = 0

        # Mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not path:
            return

        try:
            print("📄 Loading page 33...")
            pages = convert_from_path(path, dpi=200, first_page=33, last_page=33)
            self.image = pages[0]
        except Exception as e:
            print("❌ Failed to load PDF:", e)
            return

        self.show_image()

    def show_image(self):
        self.canvas.delete("all")
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_mouse_down(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_up(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        box = (
            int(min(self.start_x, end_x)),
            int(min(self.start_y, end_y)),
            int(max(self.start_x, end_x)),
            int(max(self.start_y, end_y)),
        )
        print(f"📦 Bounding Box: {box}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFBoundingBoxApp(root)
    root.mainloop()
