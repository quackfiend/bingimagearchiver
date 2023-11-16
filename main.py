import json
import os
import tkinter as tk
import tkinter.font as font
import uuid
from datetime import datetime
from tkinter import messagebox, ttk

from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD


class ImageTextApp:
    def __init__(self, master):
        self.master = master
        self.configure_root()
        self.initialize_gallery_attributes()
        self.set_custom_font()
        self.create_widgets()

    def set_custom_font(self):
        custom_font = font.nametofont("TkDefaultFont").copy()
        custom_font.configure(family="Arial", size=12)
        self.master.option_add("*Font", custom_font)

    def configure_root(self):
        self.master.title("Image and Text Storage App")
        self.center_window(self.master)
        self.status_label = tk.Label(self.master, text="", fg="green")
        self.status_label.pack(pady=10)

    def create_widgets(self):
        self.create_drop_area()
        self.create_text_box()
        self.create_buttons()
        self.create_gallery_widgets()

    def create_drop_area(self):
        self.drop_area = tk.Frame(self.master, width=400, height=200, bg="light blue",
                                  highlightbackground="gray", highlightthickness=1,
                                  relief="ridge", borderwidth=1, pady=20)
        self.drop_area.pack(padx=10, pady=10)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.handle_drop)
        self.drop_label = tk.Label(self.drop_area, text="Drop Image Here", bg="light blue",
                                   font=("Arial", 14), padx=10, pady=10, relief="ridge",
                                   borderwidth=1, cursor="hand2")
        self.drop_label.pack(expand=True)

    def create_text_box(self):
        self.text_box_frame = tk.Frame(self.master)
        self.text_box_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.text_label = tk.Label(self.text_box_frame, text="Enter Text:", font=("Arial", 14))
        self.text_label.pack()
        self.text_box = tk.Text(self.text_box_frame, height=5, width=60, borderwidth=1, relief="solid")
        self.text_box.pack(fill="both", expand=True)
    def create_buttons(self):
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(pady=10)
        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_data,
                                     font=("Arial", 14))
        self.save_button.pack(side="left", padx=10)
        self.browse_button = tk.Button(self.button_frame, text="Browse Images",
                                       command=self.browse_images, font=("Arial", 14))
        self.browse_button.pack(side="left", padx=10)

    def create_gallery_widgets(self):
        self.gallery_window = None  # Initialize gallery_window as None
        self.image_frame = None
        self.gallery_text_box = None
        self.delete_button = None
        self.back_button = None
        self.next_button = None
        self.image_counter_label = None

    def center_window(self, window):
        window.update_idletasks()
        width, height = window.winfo_width(), window.winfo_height()
        screen_width, screen_height = window.winfo_screenwidth(), window.winfo_screenheight()
        x, y = (screen_width - width) // 2, (screen_height - height) // 2
        window.geometry(f"+{x}+{y}")

    def handle_drop(self, event):
        file_path = event.data
        if file_path and os.path.isfile(file_path):
            self.current_image_path = file_path
            self.show_image_preview(file_path)
        else:
            messagebox.showerror("Error", "Invalid file dropped.")

    def show_image_preview(self, image_path):
        # Load the image and create a thumbnail
        img = Image.open(image_path)
        thumbnail_size = (100, 100)  # Adjust the size as needed
        img.thumbnail(thumbnail_size)

        img = ImageTk.PhotoImage(img)
        self.preview_label = tk.Label(self.drop_area, image=img)
        self.preview_label.image = img
        self.preview_label.pack(expand=True)
        self.drop_label.pack_forget()  # Hide the "Drop Image Here" label
    def save_data(self):
        if hasattr(self, 'current_image_path') and self.text_box.get("1.0", "end-1c"):
            self.save_image_and_text()
            self.update_status("Image and text saved successfully.")
            self.reset_fields()
            self.refresh_gallery()  # Refresh the gallery after saving
        else:
            self.update_status("Please drop an image and enter some text.", "red")

    def update_status(self, message, color="green"):
        self.status_label.config(text=message, fg=color)

    def save_image_and_text(self):
        unique_filename = self.generate_unique_filename(os.path.basename(self.current_image_path))
        new_path = os.path.join("stored_images", unique_filename)
        os.makedirs("stored_images", exist_ok=True)
        os.rename(self.current_image_path, new_path)
        self.save_text_data(unique_filename, self.text_box.get("1.0", "end-1c"))

    def generate_unique_filename(self, original_name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        uid = uuid.uuid4().hex
        extension = os.path.splitext(original_name)[1]
        return f"{timestamp}_{uid}{extension}"

    def save_text_data(self, image_name, text_content):
        json_path = os.path.join("stored_images", "data.json")
        data = {}
        if os.path.exists(json_path):
            with open(json_path, "r") as file:
                data = json.load(file)
        data[image_name] = text_content
        with open(json_path, "w") as file:
            json.dump(data, file)

    def reset_fields(self):
        self.current_image_path = None
        self.drop_label.pack(expand=True)
        self.preview_label.pack_forget()
        self.text_box.delete("1.0", "end")
    def initialize_gallery_attributes(self):
        self.gallery_window = None   # Initialize gallery_window as None
        self.image_frame = None
        self.text_label = None
        self.delete_button = None
        self.back_button = None
        self.next_button = None
        self.image_counter_label = None
        self.images = []
        self.current_image_index = 0

    def browse_images(self):
        if self.gallery_window is None or not self.gallery_window.winfo_exists():
            # If the gallery window is not initialized or doesn't exist, create it
            self.gallery_window = tk.Toplevel(self.master)
            self.gallery_window.title("Image Gallery")
            self.setup_gallery_ui()
            self.load_gallery_images()
            self.center_window(self.gallery_window)
        else:
            # The gallery window is already open, you can choose to do something here
            pass

    def setup_gallery_ui(self):
        self.image_frame = tk.Frame(self.gallery_window)
        self.image_frame.pack()
        self.gallery_text_box = tk.Text(self.gallery_window, height=5, width=60, wrap="word",
                                        state="disabled", bg=self.gallery_window.cget("bg"))
        self.gallery_text_box.pack()
        self.delete_button = tk.Button(self.gallery_window, text="Delete", command=self.delete_image)
        self.delete_button.pack(side="left")
        self.create_gallery_buttons()
        self.image_counter_label = tk.Label(self.gallery_window, text="", font=("Arial", 12))
        self.image_counter_label.pack()

    def create_gallery_buttons(self):
        self.back_button = tk.Button(self.gallery_window, text="<< Back",
                                     command=self.previous_image)
        self.back_button.pack(side="left")
        self.next_button = tk.Button(self.gallery_window, text="Next >>",
                                     command=self.next_image)
        self.next_button.pack(side="right")
        self.bind_navigation_keys()
        self.create_tooltips()


    def bind_navigation_keys(self):
        self.gallery_window.bind("<Left>", lambda e: self.previous_image())
        self.gallery_window.bind("<Right>", lambda e: self.next_image())
        self.gallery_window.bind("j", lambda e: self.previous_image())
        self.gallery_window.bind("k", lambda e: self.next_image())

    def create_tooltips(self):
        self.create_tooltip(self.back_button, "Previous Image (Left Arrow or 'j')")
        self.create_tooltip(self.next_button, "Next Image (Right Arrow or 'k')")
        self.create_tooltip(self.delete_button, "Delete Image")

    def create_tooltip(self, widget, text):
        tooltip = Tooltip(widget, text)
        widget.bind("<Enter>", tooltip.showtip)
        widget.bind("<Leave>", tooltip.hidetip)
    def load_gallery_images(self):
        json_path = os.path.join("stored_images", "data.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as file:
                self.data = json.load(file)
            self.images = [os.path.join("stored_images", f) for f in os.listdir("stored_images")
                           if f.endswith(tuple(".png .jpg .jpeg .gif .bmp".split())) and f != "data.json"]
        if self.images:
            self.show_image(0)
        else:
            self.gallery_text_box.config(state="normal")
            self.gallery_text_box.delete("1.0", "end")
            self.gallery_text_box.insert("1.0", "No images found.")
            self.gallery_text_box.config(state="disabled")
        self.update_image_counter(self.current_image_index)

    def refresh_gallery(self):
        self.load_gallery_images()
        self.update_image_counter(self.current_image_index)

    def show_image(self, index):
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        image_path = self.images[index]
        img = Image.open(image_path)
        img = ImageTk.PhotoImage(img)
        panel = tk.Label(self.image_frame, image=img)
        panel.image = img
        panel.pack()
        image_name = os.path.basename(self.images[index])
        text_content = self.data.get(image_name, "")
        self.gallery_text_box.config(state="normal")
        self.gallery_text_box.delete("1.0", "end")
        self.gallery_text_box.insert("1.0", text_content)
        self.gallery_text_box.config(state="disabled")
        self.update_image_counter(index)

    def update_image_counter(self, index):
        total_images = len(self.images)
        if total_images > 0:
            counter_text = f"Image {index + 1} of {total_images}"
            self.image_counter_label.config(text=counter_text)
        else:
            self.image_counter_label.config(text="")



    def next_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.show_image(self.current_image_index)
            self.update_image_counter(self.current_image_index)

    def previous_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self.show_image(self.current_image_index)

    def delete_image(self):
        if self.images:
            image_path = self.images[self.current_image_index]
            image_name = os.path.basename(image_path)

            # Remove the image file
            if os.path.exists(image_path):
                os.remove(image_path)

            # Remove the text associated with the image
            json_path = os.path.join("stored_images", "data.json")
            if os.path.exists(json_path):
                with open(json_path, "r") as file:
                    data = json.load(file)
                if image_name in data:
                    del data[image_name]
                    with open(json_path, "w") as file:
                        json.dump(data, file)

            # Remove the image from the list
            del self.images[self.current_image_index]

            if len(self.images) == 0:
                self.gallery_text_box.config(state="normal")
                self.gallery_text_box.delete("1.0", "end")
                self.gallery_text_box.insert("1.0", "No images found.")
                self.gallery_text_box.config(state="disabled")
                self.current_image_index = 0  # Set index to zero when no images are left
                self.image_frame.pack_forget()  # Hide the image frame
            else:
                if self.current_image_index >= len(self.images):
                    self.current_image_index = len(self.images) - 1  # Adjust index if out of bounds
                self.show_image(self.current_image_index)

            self.update_image_counter(self.current_image_index)  # Update the image counter

    def bind_navigation_keys(self):
        self.gallery_window.bind("<Left>", lambda e: self.previous_image())
        self.gallery_window.bind("<Right>", lambda e: self.next_image())
        self.gallery_window.bind("j", lambda e: self.previous_image())
        self.gallery_window.bind("k", lambda e: self.next_image())

    def create_tooltips(self):
        self.create_tooltip(self.back_button, "Previous Image (Left Arrow or 'j')")
        self.create_tooltip(self.next_button, "Next Image (Right Arrow or 'k')")
        self.create_tooltip(self.delete_button, "Delete Image")

    def create_tooltip(self, widget, text):
        tooltip = Tooltip(widget, text)
        widget.bind("<Enter>", tooltip.showtip)
        widget.bind("<Leave>", tooltip.hidetip)

class Tooltip:
    def __init__(self, widget, text, **kwargs):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.kwargs = kwargs  # Store additional keyword arguments

    def showtip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(tw, text=self.text, justify='left',
                          background="#ffffe0", relief='solid', borderwidth=1,
                          font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ImageTextApp(root)
    root.mainloop()
