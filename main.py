from tkinter import Tk, Label, Button, Entry, font
root =Tk()

cf = font.Font(family="Times New Roman", size=12)
root.title("Đăng nhập hệ thống")
title_label = Label(root, text="Đăng nhập", font=("Times New Roman", 20)).place(x=150,y=50)
root.geometry("400x300")
user_name = Label(root, text="Tên đăng nhập:").place(x=50,y=120)
user_password = Label(root,text ="Mật khẩu:").place(x=50,y=150)
user_name_entry = Entry(root)
user_name_entry.place(x=150,y=120)
user_password_entry = Entry(root, show="*")
user_password_entry.place(x=150,y=150)

submit_button = Button(root, text="Đăng nhập", command="").place(x=175,y=190)

root.mainloop()
