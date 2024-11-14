import cv2
import time
import PIL.Image
import PIL.ImageTk
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from threading import Thread
from tkinter import IntVar, StringVar
from collections import deque
from emotion_detection import detect_emotion  # Importing the emotion detection function

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.current_frame = None
        self.nose_tracking_mode = tk.BooleanVar(value=False)
        self.cursor_x = 0
        self.cursor_y = 0
        self.root.title("Emotion-Driven Paint App")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        self.stroke_size = tk.IntVar(value=2)
        self.stroke_color = tk.StringVar(value="black")
        self.prev_x = None
        self.prev_y = None
        self.current_tool = "pencil"
        self.cursor_size = tk.IntVar(value=10)

        # Initialize emotion confidence
        self.emotion_confidence = {
            "Roudra": 0.0,  # Angry
            "Bhayanaka": 0.0,  # Fearful
            "Hasya": 0.0,  # Happy
            "Shanta": 0.0,  # Neutral
            "Karuna": 0.0,  # Sad
            "Adbhuta": 0.0  # Surprised
        }

        self.previous_emotion = None
        self.setup_ui()

        self.cap = cv2.VideoCapture(0)
        self.emotion = "No emotion detected"
        self.current_frame = None

        self.video_thread = Thread(target=self.update_video, daemon=True)
        self.video_thread.start()

        self.nose_tracking_thread = Thread(target=self.nose_tracking, daemon=True)
        self.nose_tracking_thread.start()

    def handle_key_press(self, event):
        # For example, toggle between pencil and eraser on key press
        if event.keysym == 'e':  # 'e' for eraser
            self.use_eraser()
        elif event.keysym == 'p':  # 'p' for pencil
            self.use_pencil()

    def setup_ui(self):
        # Setup the main UI structure
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_frame, bg="#e0e0e0", width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.setup_toolbar(left_frame)
        self.setup_color_palette(left_frame)

        accessibility_frame = tk.Frame(left_frame, bg="#e0e0e0")
        accessibility_frame.pack(pady=(10, 0))

        tk.Scale(accessibility_frame, label="Cursor Size", variable=self.cursor_size, from_=5, to=30, orient=tk.HORIZONTAL, command=self.update_cursor_size).pack()

        right_frame = tk.Frame(main_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(right_frame, bg="white", relief="ridge", bd=2)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.canvas.bind("<B1-Motion>", self.paint_with_mouse)
        self.canvas.bind("<ButtonRelease-1>", self.reset_prev_point)
        self.canvas.bind("<KeyPress>", self.handle_key_press)
        self.canvas.focus_set()

        self.cursor = self.canvas.create_oval(0, 0, self.cursor_size.get(), self.cursor_size.get(), fill="red", outline="red")

        bottom_frame = tk.Frame(right_frame, bg="#f0f0f0")
        bottom_frame.pack(fill=tk.X)

        self.video_frame = tk.Label(bottom_frame, bg="#e0e0e0", relief="sunken", bd=2)
        self.video_frame.pack(side=tk.LEFT, padx=(0, 10))

        self.emotion_label = tk.Label(bottom_frame, text="Emotion: No emotion detected", 
                                      font=("Arial", 14), bg="#e0e0e0", relief="sunken", bd=2)
        self.emotion_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def setup_toolbar(self, parent):
        toolbar = tk.Frame(parent, bg="#e0e0e0")
        toolbar.pack(pady=(0, 10))

        tk.Button(toolbar, text="Pencil", command=self.use_pencil).pack(fill=tk.X)
        tk.Button(toolbar, text="Eraser", command=self.use_eraser).pack(fill=tk.X)
        tk.Button(toolbar, text="Clear", command=self.clear).pack(fill=tk.X)
        tk.Button(toolbar, text="Save", command=self.save_image).pack(fill=tk.X)
        tk.Button(toolbar, text="New", command=self.create_new).pack(fill=tk.X)

        tk.Label(toolbar, text="Stroke Size").pack()
        tk.Scale(toolbar, variable=self.stroke_size, from_=1, to=10, orient=tk.HORIZONTAL).pack()

        tk.Checkbutton(toolbar, text="Eye Tracking", variable=self.nose_tracking_mode).pack()

    def setup_color_palette(self, parent):
        colors = ['black', 'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'brown', 'gray']
        color_frame = tk.Frame(parent, bg="#e0e0e0")
        color_frame.pack(pady=(0, 10))

        for color in colors:
            tk.Button(color_frame, bg=color, width=2, height=1, 
                      command=lambda c=color: self.stroke_color.set(c)).pack(side=tk.LEFT)

        tk.Button(color_frame, text="More Colors", command=self.select_color).pack(side=tk.LEFT)

    def paint_with_mouse(self, event):
        if not self.nose_tracking_mode.get():
            self.paint(event.x, event.y)

    def select_color(self):
        color = colorchooser.askcolor()[1]  # askcolor() returns a tuple (RGB, hex value)
        if color:
            self.stroke_color.set(color)  # Update the stroke color to the selected color

    def paint(self, x, y):
        if self.prev_x is not None and self.prev_y is not None:
            if self.current_tool == "pencil":
                self.canvas.create_line(self.prev_x, self.prev_y, x, y,
                                        fill=self.stroke_color.get(), width=self.stroke_size.get(),
                                        capstyle=tk.ROUND, smooth=tk.TRUE)
            elif self.current_tool == "eraser":
                self.canvas.create_line(self.prev_x, self.prev_y, x, y,
                                        fill="white", width=self.stroke_size.get() * 2,
                                        capstyle=tk.ROUND, smooth=tk.TRUE)

        self.prev_x, self.prev_y = x, y
        self.update_cursor(x, y)

    def update_cursor(self, x, y):
        size = self.cursor_size.get()
        self.canvas.coords(self.cursor, x-size//1.5, y-size//1.5, x+size//1.5, y+size//1.5)

    def update_cursor_size(self, _):
        self.update_cursor(self.cursor_x, self.cursor_y)

    def reset_prev_point(self, event):
        self.prev_x = None
        self.prev_y = None

    def use_pencil(self):
        self.current_tool = "pencil"
        self.canvas.config(cursor="arrow")

    def use_eraser(self):
        self.current_tool = "eraser"
        self.canvas.config(cursor="circle")

    def clear(self):
        self.canvas.delete("all")

    def save_image(self):
        file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if file:
            self.canvas.postscript(file="temp.ps")
            img = PIL.Image.open("temp.ps")
            img.save(file, "PNG")
            os.remove("temp.ps")

    def create_new(self):
        self.canvas.delete("all")

    def update_video(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Convert the frame to RGB for Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = PIL.Image.fromarray(frame_rgb)
            img_tk = PIL.ImageTk.PhotoImage(img)

            # Update the video frame with the new image
            self.video_frame.config(image=img_tk)
            self.video_frame.image = img_tk

            # Detect emotion and update UI
            self.emotion = detect_emotion(frame)
            self.emotion_label.config(text=f"Emotion: {self.emotion}")

            time.sleep(0.03)  # Slight delay to make video feed smooth

    def nose_tracking(self):
        while True:
            if self.nose_tracking_mode.get():
                self.nose_tracking_update()

    def nose_tracking_update(self):
        # Implement your logic for nose tracking and update the cursor position
        pass

# Example of running the app
root = tk.Tk()
app = PaintApp(root)
root.mainloop()