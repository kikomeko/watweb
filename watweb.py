from tkinter import *
root = Tk()
root.title("watweb")

def Sendbtn():
	if text != "":
		text1 = text.get()
		listbox.insert(END, text1)
		text.delete(0, END)
	else:
		listbox.insert(END, "send button pressed")
	

label = Label(root, text="CHAT WITH US")
text = Entry(root)
sendbtn = Button(root, text="send", command =Sendbtn)
scrollbar = Scrollbar(root, orient=VERTICAL)
listbox = Listbox(root, yscrollcommand= scrollbar.set)
scrollbar.configure(command= listbox.yview)

label.pack()
text.pack()
sendbtn.pack()
listbox.pack()
scrollbar.pack()


root.mainloop()