import os
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from pymongo import MongoClient
from PIL import Image, ImageTk

#GUI
root=tk.Tk()
root.title("Library Management System")

#connecting database
client=MongoClient("mongodb://localhost:27017/")
db=client["Library"]
collection=db["Records"]

# Get the screen width and height
top_frame_height=30
screen_width=root.winfo_screenwidth()
screen_height=root.winfo_screenheight()
frame_width=(screen_width-20)//3
frame_height=screen_height-top_frame_height

#top frame
top_frame=tk.Frame(root,bg="#33d6ff",height=top_frame_height)
top_frame.pack(fill=X)

#left frame
left_frame=tk.Frame(root,bg="#6699ff",width=frame_width,height=frame_height)
left_frame.pack(side=LEFT,fill=BOTH)

#center frame
center_frame=tk.Frame(root,height=frame_height)
center_frame.pack(side=LEFT,fill=BOTH,expand=YES)

#right frame
right_frame=tk.Frame(root,bg="#ff4d88",width=frame_width,height=frame_height)
right_frame.pack(side=LEFT,fill=BOTH)

#validation function
def validation():
    if (id_entry.get().strip() and name_entry.get().strip())=="" or (author_entry.get().strip() and status_dropdown.get().strip())=="":
        messagebox.showwarning("Warning","Felids Can Not Be Empty.")
        id_entry.focus_set()
    else:
        try:
            if any(ch.isdigit() for ch in (name_entry.get())) or any(ch.isdigit() for ch in (author_entry.get())):
                messagebox.showinfo("Message","Numbers Not Allowed in Names")
            elif any(ch.isalpha() for ch in (id_entry.get())):
                messagebox.showinfo("Message","Alphabetic are Not Allowed in Book ID")
                id_entry.focus_set()
            else:
                add()
        except Exception as ep:
            messagebox.showerror('error',ep)

#functions
tree=None
def add():
    id=id_entry.get()
    name=name_entry.get()
    author=author_entry.get()
    status=status_dropdown.get()
    data={"Book Id":id,"Book Name":name,"Author Name":author,"Status":status}
    collection.insert_one(data)
    messagebox.showinfo("Success","New Book Added.")
    clear()
    refresh_treeview()

def retrieve():
    global tree
    data=collection.find()
    for record in data:
        bookId=record.get("Book Id","")
        bookName=record.get("Book Name","")
        author=record.get("Author Name","")
        status=record.get("Status","")
        tree.insert("","end",values=(bookId,bookName,author,status))
        refresh_treeview()

def refresh_treeview():
    global tree
    # Clear existing items from the tree
    tree.delete(*tree.get_children())
    # Add the updated data to the tree
    for record in collection.find():
        tree.insert("","end",text=record["Book Id"],values=(record["Book Id"],record["Book Name"],record["Author Name"],record["Status"]))

def update():
    global tree
    # Get the selected item from the treeview
    selected_item=tree.selection()
    if selected_item:
        # Get the data associated with the selected item
        item_data=tree.item(selected_item,"values")
        # Extract the record ID
        record_id=item_data[0]
        # Retrieve the record from MongoDB using the record ID
        query={"Book Id":record_id}
        record=collection.find_one(query)
        if record:
            # Update the record fields based on user input
            if id_entry.get().strip()!="":
                record["BookId"]=id_entry.get()
            if name_entry.get().strip()!="":
                record["Book Name"]=name_entry.get()
            if author_entry.get().strip()!="":
                record["Author Name"]=author_entry.get()
            if status_dropdown.get().strip()!="":
                record["Status"]=status_dropdown.get()
            # Perform the update in the database
            collection.replace_one(query,record)
            messagebox.showinfo("Success","Record updated successfully.")
            refresh_treeview()
        else:
            messagebox.showerror("Error","Record not found.")
    else:
        messagebox.showwarning("Warning","Please select a record.")
    clear()

def delete():
    global tree
    # Get the selected items from the treeview
    selected_items=tree.selection()
    if selected_items:
        for item in selected_items:
            # Get the data associated with the selected item
            item_data=tree.item(item,"values")
            # Extract the record ID
            record_id=item_data[0]
            # Delete the record from MongoDB using the record ID
            query={"Book Id":record_id}
            collection.delete_one(query)
            messagebox.showinfo("Delete",f"Record with ID:{record_id} deleted.")
        # Refresh the tree after deletion
        refresh_treeview()
    else:
        messagebox.showwarning("Warning","Please select a record.")

def delete_all():
    result=messagebox.askyesno("Confirmation","Are you sure you want to delete all records?")
    if result:
        del_all=collection.delete_many({})
        messagebox.showinfo("Info",f"{del_all.deleted_count} Records Deleted Successfully")
        refresh_treeview()
    else:
        messagebox.showinfo("Message","Deletion cancelled!!")

def clear():
    id_entry.delete(0,"end")
    name_entry.delete(0,"end")
    author_entry.delete(0,"end")
    search_entry.delete(0,"end")
    search_entry.delete(0,"end")
    status_dropdown["values"]=[]

def search():
    global tree
    query=search_entry.get()
    if query:
        data=collection.find({"$or":[{"Book Id":{"$regex":query,"$options":"i"}},
                                 {"Book Name":{"$regex":query,"$options":"i"}},
                                 {"Author Name":{"$regex":query,"$options":"i"}},
                                 {"Status":{"$regex":query,"$options":"i"}}
                                ]})
        for row in tree.get_children():
            tree.delete(row)
        data_list=list(data)
        if data_list:
            for data in data_list:
                tree.insert("","end",values=(data["Book Id"],data["Book Name"],data["Author Name"],data["Status"]))
        else:
            messagebox.showinfo("Message",f"No Data Found on {query}.")
    else:
        messagebox.showwarning("Warning","Field Is Empty!!")
        search_entry.focus_set()

#image
def set_image_opacity(image,opacity):
    # Create a copy of the image with alpha channel
    image_with_alpha=image.copy()
    alpha = int(opacity*255)
    image_with_alpha.putalpha(alpha)

    # Convert the Image object into a Tkinter-compatible photo image
    photo_image=ImageTk.PhotoImage(image_with_alpha)
    return photo_image

# Get the screen width and height
image_width=center_frame.winfo_screenwidth()
image_height=center_frame.winfo_screenheight()

# Open and resize the image to match the screen size
image=Image.open("images/library.jpg")
image=image.resize((image_width,image_height),Image.LANCZOS)

# Set the opacity of the image (value between 0.0 and 1.0)
opacity=0.7

# Set image opacity
background_image=set_image_opacity(image,opacity)

# Create a label with the background image
background_label=tk.Label(center_frame,image=background_image)
background_label.place(x=0,y=0,relwidth=1,relheight=1)

#frame for search
frame=tk.Frame(center_frame,bg='lightgreen')
frame.pack(anchor="nw")

#title 
Label(top_frame,text='LIBRARY MANAGEMENT SYSTEM',font=('Times New Roman',20,'bold'),bg='#33d6ff',fg='#ff0066').pack()

#fields
book_id=tk.Label(left_frame,text="Book ID",font=('Georgia',15),bg="#6699ff")
book_id.pack(padx=10,pady=10)

id_entry=tk.Entry(left_frame,width=20,font="Tahoma",fg="#0000e6")
id_entry.pack(padx=10,pady=10)

book_name=tk.Label(left_frame,text="Book Name",font=('Georgia',15),bg="#6699ff")
book_name.pack(padx=10,pady=10)

name_entry=tk.Entry(left_frame,width=20,font="Tahoma",fg="#0000e6")
name_entry.pack(padx=10,pady=10)

author_name=tk.Label(left_frame,text="Author_Name",font=('Georgia',15),bg="#6699ff")
author_name.pack(padx=10,pady=10)

author_entry=tk.Entry(left_frame,width=20,font="Tahoma",fg="#0000e6")
author_entry.pack(padx=10,pady=10)

status_label=tk.Label(left_frame,text="Status Of Book",font=('Georgia',15),bg="#6699ff")
status_label.pack()

status_dropdown=ttk.Combobox(left_frame,values=["Available","Issued","Out of Stock"],width=20,font="Tahoma",state="readonly")
status_dropdown.pack(padx=10,pady=10)

#search entry
search_entry=tk.Entry(frame,width=35,font="Tahoma",fg="#1f7a7a")
search_entry.grid(row=0,column=0,padx=10,pady=10,columnspan=5)

#search Button
search_btn=tk.Button(frame,text="Search",font=('Georgia',12,'bold'),bg="#990000",fg="white",activebackground="#990000",activeforeground="white",bd=5,command=search)
search_btn.grid(row=0,column=7,padx=10,pady=10)

#center frame fields
Label(center_frame,text="INFORMATION ABOUT ALL BOOKS",font=('Times New Roman',25,'bold'),bg='#ffb3b3',fg="#9900ff").pack(fill=X)

# Create a custom style for the Treeview
style=ttk.Style()
style.theme_use("default")
style.configure("Treeview",
    background="#ffe5b4",
    foreground="#e60000",
    fieldbackground="#ffe5b4")

#create a color for selection
style.map('Treeview',background=[('selected','lightcoral')])
tree=ttk.Treeview(center_frame,columns=("Book Id","Book Name","Author Name","Status"),show="headings")
tree.heading("Book Id",text="Book Id")
tree.heading("Book Name",text="Book Name")
tree.heading("Author Name",text="Author Name")
tree.heading("Status",text="Status")
tree.pack(padx=10,pady=10)

# Configure column widths to center-align content
for column in ("Book Id","Book Name","Author Name","Status"):
    tree.column(column,anchor="center")

#buttons
add_book=tk.Button(left_frame,text="Add Books",font=('Times New Roman',15),bg="#3385ff",fg="white",activebackground="#6699ff",activeforeground="white",bd=5,command=validation)
add_book.pack(padx=10,pady=10)

clear_fields=tk.Button(left_frame,text="Clear Fields",font=('Times New Roman',15),bg="#3385ff",fg="white",activebackground="#6699ff",activeforeground="white",bd=5,command=clear)
clear_fields.pack(padx=10,pady=10)

view_record=tk.Button(right_frame,text="View Records",font=('Times New Roman',15),bg="#ff1a66",fg="white",activebackground="#ff4d88",activeforeground="white",bd=5,command=retrieve)
view_record.pack(padx=10,pady=10)

update_book=tk.Button(right_frame,text="Update Record",font=('Times New Roman',15),bg="#ff1a66",fg="white",activebackground="#ff4d88",activeforeground="white",bd=5,command=update)
update_book.pack(padx=10,pady=10)

delete_book=tk.Button(right_frame,text="Delete Record",font=('Times New Roman',15),bg="#ff1a66",fg="white",activebackground="#ff4d88",activeforeground="white",bd=5,command=delete)
delete_book.pack(padx=10,pady=10)

delete_all_book=tk.Button(right_frame,text="Delete All Records",font=('Times New Roman',15),bg="#ff1a66",fg="white",activebackground="#ff4d88",activeforeground="white",bd=5,command=delete_all)
delete_all_book.pack(padx=10,pady=10)

root.mainloop()
client.close()