import cv2
import numpy
import PIL
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window
from datetime import datetime

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

Window.size = (500,500)

cap = cv2.VideoCapture(0)   

class FilterSelection(BoxLayout):
    def __init__(self):
        self.type = 'none'
        self.orientation = 'vertical'
        self.options = ['Mustache', 'Glasses', 'Beard']
        super().__init__()

        for i in self.options:
            button = Button(text=i, background_color=(0,0,1,0.5), font_size=50)
            self.add_widget(button)
            button.bind(on_press=self.change)

        self.capture = Button(text='CAPTURE', background_color=(1,0,0,0.5), font_size=50)
        self.add_widget(self.capture)
        self.capture.bind(on_press=self.click)
        Clock.schedule_interval(self.display, 0.05)

    def change(self, button):
        self.type = button.text
    
    def click(self, button):
        current_time = datetime.now()
        date_and_time = current_time.strftime("%H: %M: %S")
        name = f'{date_and_time} filter.jpg'
        cv2.imwrite(name, cv2.cvtColor(numpy.array(self.frame), cv2.COLOR_RGB2BGR))
    
    def display(self, *args):
        ret, frame = cap.read()
        self.frame = frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:
            if self.type == 'Glasses':
                img = PIL.Image.open('glasses.png')
                img = img.convert("RGBA")
                new_image = img.resize((w, int(1/2 * h)))
                frame = PIL.Image.fromarray(frame)
                frame.paste(new_image, (x, y+int(1/6 * h)), new_image)
                self.frame = frame
                frame = numpy.array(frame)
            elif self.type == 'Beard':
                img = PIL.Image.open('beard.png')
                img = img.convert("RGBA")
                new_image = img.resize((int(w * 9.5/10), h))
                frame = PIL.Image.fromarray(frame)
                frame.paste(new_image, (x, int(y + (h/4))), new_image)
                self.frame = frame
                frame = numpy.array(frame)

            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.3, 3)
            mouth = smile_cascade.detectMultiScale(roi_gray, 2, 11)

            for (ex, ey, ew, eh) in eyes:
                for (mx, my, mw, mh) in mouth:
                    if my > ey and mx > ex and mx < ex + ew:
                        if self.type == 'Mustache':
                            img = PIL.Image.open('mustache.png')
                            img = img.convert("RGBA")
                            new_image = img.resize((mw, mh))
                            roi_color = PIL.Image.fromarray(numpy.asarray(roi_color))
                            roi_color.paste(new_image, (mx, int(my-(mh/2))), new_image)
                            frame = PIL.Image.fromarray(frame)
                            frame.paste(roi_color, (x,y))
                            self.frame = frame
                            frame = numpy.array(frame)

        frame = numpy.array(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.namedWindow('View', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('View', 888, 500)
        cv2.imshow('View', frame)

class FilterSelectApp(App):
    def build(self) -> FilterSelection:
        return FilterSelection()

FilterSelectApp().run()