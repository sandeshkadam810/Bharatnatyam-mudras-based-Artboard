import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import PIL.ImageGrab as ImageGrab
import PIL.Image
import PIL.ImageTk
import cv2
from threading import Thread
import numpy as np
import time

class PaintApp:
    def __init__(self, root, face_detector):
        self.root = root
        self.face_detector = face_detector
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

        self.setup_ui()
        
        self.cap = cv2.VideoCapture(0)
        self.emotion = "No emotion detected"
        self.current_frame = None
        
        self.video_thread = Thread(target=self.update_video, daemon=True)
        self.video_thread.start()

        self.nose_tracking_thread = Thread(target=self.nose_tracking, daemon=True)
        self.nose_tracking_thread.start()

    def setup_ui(self):
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
        self.canvas.coords(self.cursor, x-size//2, y-size//2, x+size//2, y+size//2)

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
        self.canvas.config(cursor="dotbox")

    def select_color(self):
        color = colorchooser.askcolor(title="Select Color")[1]
        if color:
            self.stroke_color.set(color)

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png")
        if file_path:
            x = self.root.winfo_rootx() + self.canvas.winfo_x()
            y = self.root.winfo_rooty() + self.canvas.winfo_y()
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height()
            ImageGrab.grab().crop((x, y, x1, y1)).save(file_path)

    def create_new(self):
        if messagebox.askyesno("New Canvas", "Do you want to save before creating a new canvas?"):
            self.save_image()
        self.clear()

    def clear(self):
        self.canvas.delete("all")
        self.cursor = self.canvas.create_oval(0, 0, self.cursor_size.get(), self.cursor_size.get(), fill="red", outline="red")
        print("Canvas cleared")

    def update_video(self):
        while True:
            try:
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame = frame
                    face_data = self.face_detector.process_frame(frame)
                    if face_data['emotion']:
                        self.emotion = face_data['emotion']
                        self.update_tool_based_on_emotion(self.emotion)
                    
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (200, 150))
                    photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                    
                    self.video_frame.config(image=photo)
                    self.video_frame.image = photo
                    self.emotion_label.config(text=f"Emotion: {self.emotion}")
                else:
                    print("Failed to capture frame")
            except Exception as e:
                print(f"Error in video processing: {str(e)}")
            
            time.sleep(0.01)

    def update_tool_based_on_emotion(self, emotion):
        if emotion in ['angry', 'neutral','happy']:
            self.use_pencil()
        elif emotion == 'sad':
            self.use_eraser()
        elif emotion in [ 'surprise']:
            self.clear()

    def nose_tracking(self):
        while True:
            if self.nose_tracking_mode.get() and self.current_frame is not None:
                face_data = self.face_detector.process_frame(self.current_frame)
                if face_data['landmarks']:
                    nose_tip = face_data['landmarks'].landmark[4]
                    x = int((1 - nose_tip.x) * self.canvas.winfo_width())
                    y = int(nose_tip.y * self.canvas.winfo_height())

                    new_x = max(0, min(x, self.canvas.winfo_width()))
                    new_y = max(0, min(y, self.canvas.winfo_height()))

                    self.paint(new_x, new_y)
                    self.cursor_x, self.cursor_y = new_x, new_y

            time.sleep(0.01)

    def handle_key_press(self, event):
        if event.char == 'p':
            self.use_pencil()
        elif event.char == 'e':
            self.use_eraser()
        elif event.char == 'c':
            self.select_color()
        elif event.char == 's':
            self.save_image()
        elif event.char == 'n':
            self.create_new()

    def run(self):
         self.root.mainloop()