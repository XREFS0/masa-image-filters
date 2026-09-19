"""
MASA 09_Image Filtering App Using Tkinter in Python with Source Code
Developer: MASA
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageOps, ImageEnhance

class ImageFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Filtering App")
        self.root.geometry("1500x750")
        self.root.configure(bg="#eaeaea")

        self.original_image = None
        self.image = None
        self.tk_original = None
        self.tk_filtered = None

        # History: [(image, description, thumbnail)]
        self.history = []
        self.future = []
        self.history_thumbnails = []  # keep references

        # Last slider values
        self.last_slider_values = (0, 1.0, 1.0)

        btn_frame = tk.Frame(root, bg="#eaeaea")
        btn_frame.pack(side=tk.TOP, pady=10)

        tk.Button(btn_frame, text="Open Image", command=self.open_image).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Grayscale", command=lambda: self.apply_filter("Grayscale", lambda img: ImageOps.grayscale(img).convert("RGB"))).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Invert", command=lambda: self.apply_filter("Invert", lambda img: ImageOps.invert(img))).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Sharpen", command=lambda: self.apply_filter("Sharpen", lambda img: img.filter(ImageFilter.SHARPEN))).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Edge Enhance", command=lambda: self.apply_filter("Edge Enhance", lambda img: img.filter(ImageFilter.EDGE_ENHANCE))).grid(row=0, column=4, padx=5)
        tk.Button(btn_frame, text="Reset Image", command=self.reset_image, bg="#f39c12", fg="white").grid(row=0, column=5, padx=5)
        tk.Button(btn_frame, text="Undo", command=self.undo, bg="#3498db", fg="white").grid(row=0, column=6, padx=5)
        tk.Button(btn_frame, text="Redo", command=self.redo, bg="#9b59b6", fg="white").grid(row=0, column=7, padx=5)
        tk.Button(btn_frame, text="Save Image", command=self.save_image, bg="#4CAF50", fg="white").grid(row=0, column=8, padx=5)

        # Sliders
        slider_frame = tk.Frame(root, bg="#eaeaea")
        slider_frame.pack(side=tk.TOP, pady=10)

        tk.Label(slider_frame, text="Blur", bg="#eaeaea").grid(row=0, column=0)
        self.blur_slider = tk.Scale(slider_frame, from_=0, to=10, orient=tk.HORIZONTAL, command=self.adjust_filters)
        self.blur_slider.grid(row=0, column=1, padx=10)

        tk.Label(slider_frame, text="Brightness", bg="#eaeaea").grid(row=0, column=2)
        self.brightness_slider = tk.Scale(slider_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, command=self.adjust_filters)
        self.brightness_slider.set(1.0)
        self.brightness_slider.grid(row=0, column=3, padx=10)

        tk.Label(slider_frame, text="Contrast", bg="#eaeaea").grid(row=0, column=4)
        self.contrast_slider = tk.Scale(slider_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, command=self.adjust_filters)
        self.contrast_slider.set(1.0)
        self.contrast_slider.grid(row=0, column=5, padx=10)

        # Canvas for Original and Filtered
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.create_text(300, 30, text="Original Image", font=("Arial", 14, "bold"))
        self.canvas.create_text(850, 30, text="Filtered Image", font=("Arial", 14, "bold"))

        # History Panel with thumbnails
        history_frame = tk.Frame(root, bg="#dcdcdc", width=280)
        history_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(history_frame, text="History", bg="#dcdcdc", font=("Arial", 14, "bold")).pack(pady=5)

        self.history_canvas = tk.Canvas(history_frame, bg="#f5f5f5", width=260)
        self.history_scrollbar = tk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_canvas.yview)
        self.scrollable_frame = tk.Frame(self.history_canvas, bg="#f5f5f5")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))
        )
        self.history_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.history_canvas.configure(yscrollcommand=self.history_scrollbar.set)

        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_to_history_panel(self, desc, img_copy):
        thumb = img_copy.copy()
        thumb.thumbnail((80, 80))
        tk_thumb = ImageTk.PhotoImage(thumb)
        self.history_thumbnails.append(tk_thumb)  # prevent garbage collection

        frame = tk.Frame(self.scrollable_frame, bg="#eeeeee", bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.X, padx=5, pady=3)

        lbl_img = tk.Label(frame, image=tk_thumb, bg="#eeeeee")
        lbl_img.pack(side=tk.LEFT, padx=5, pady=5)

        lbl_text = tk.Label(frame, text=desc, bg="#eeeeee", anchor="w", font=("Arial", 9))
        lbl_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # clicking on thumbnail jumps to history
        frame.bind("<Button-1>", lambda e, idx=len(self.history)-1: self.jump_to_history(idx))
        lbl_img.bind("<Button-1>", lambda e, idx=len(self.history)-1: self.jump_to_history(idx))
        lbl_text.bind("<Button-1>", lambda e, idx=len(self.history)-1: self.jump_to_history(idx))

    def push_history(self, description):
        if self.image:
            self.history.append((self.image.copy(), description))
            self.future.clear()
            self.add_to_history_panel(description, self.image)

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg *.bmp")])
        if file_path:
            self.original_image = Image.open(file_path).convert("RGB")
            self.image = self.original_image.copy()
            self.history.clear()
            self.future.clear()
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.history_thumbnails.clear()
            self.push_history("Opened Image")
            self.display_images()

    def display_images(self):
        if self.original_image:
            max_w, max_h = 400, 500
            orig_copy = self.original_image.copy()
            orig_copy.thumbnail((max_w, max_h))
            self.tk_original = ImageTk.PhotoImage(orig_copy)

            filt_copy = self.image.copy()
            filt_copy.thumbnail((max_w, max_h))
            self.tk_filtered = ImageTk.PhotoImage(filt_copy)

            self.canvas.delete("all")
            self.canvas.create_text(300, 30, text="Original Image", font=("Arial", 14, "bold"))
            self.canvas.create_text(850, 30, text="Filtered Image", font=("Arial", 14, "bold"))
            self.canvas.create_image(300, 300, image=self.tk_original)
            self.canvas.create_image(850, 300, image=self.tk_filtered)

    def apply_filter(self, description, filter_func):
        if self.image:
            self.push_history(description)
            self.image = filter_func(self.image)
            self.display_images()

    def adjust_filters(self, event=None):
        if self.original_image:
            current_values = (self.blur_slider.get(), self.brightness_slider.get(), self.contrast_slider.get())
            if current_values != self.last_slider_values:
                desc = f"Blur={current_values[0]}, Brightness={current_values[1]}, Contrast={current_values[2]}"
                self.push_history(desc)
                self.last_slider_values = current_values

            img = self.original_image.copy()
            if current_values[0] > 0:
                img = img.filter(ImageFilter.GaussianBlur(current_values[0]))
            img = ImageEnhance.Brightness(img).enhance(current_values[1])
            img = ImageEnhance.Contrast(img).enhance(current_values[2])
            self.image = img
            self.display_images()

    def reset_image(self):
        if self.original_image:
            self.push_history("Reset Image")
            self.image = self.original_image.copy()
            self.blur_slider.set(0)
            self.brightness_slider.set(1.0)
            self.contrast_slider.set(1.0)
            self.last_slider_values = (0, 1.0, 1.0)
            self.display_images()

    def undo(self):
        if len(self.history) > 1:
            self.future.append(self.history.pop())
            self.image = self.history[-1][0].copy()
            self.display_images()

            # remove last thumbnail
            self.scrollable_frame.winfo_children()[-1].destroy()
            self.history_thumbnails.pop()

    def redo(self):
        if self.future:
            img, desc = self.future.pop()
            self.history.append((img, desc))
            self.image = img.copy()
            self.add_to_history_panel(desc, img)
            self.display_images()

    def jump_to_history(self, idx):
        if 0 <= idx < len(self.history):
            self.image = self.history[idx][0].copy()
            self.display_images()

    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("BMP files", "*.bmp")])
            if file_path:
                self.image.save(file_path)
                messagebox.showinfo("Image Saved", f"Image successfully saved at:\n{file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageFilterApp(root)
    root.mainloop()