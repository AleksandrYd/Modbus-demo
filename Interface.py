import tkinter
import tkinter.dnd
from datetime import datetime
from tkinter import *
from tkinter import ttk
from modbus_client import *
from modbus_from_file import *
from PIL import ImageTk, Image
import os


def create_log(array, quantity):
    if os.path.getsize('logs.txt') > 100*1024:
        open('logs.txt', 'w+')
    with open('logs.txt', 'a') as file:
        if len(array[0]) == 3:
            for i in range(quantity):
                file.write(f"{array[i][0]}: {array[i][2]} A - Время - {datetime.now()} \n")
        elif len(array[0]) == 4:
            for i in range(quantity):
                file.write(f"{array[i][0]}: {array[i][3]} A - Время - {datetime.now()} \n")


class MySocket:
    def __init__(self):
        self.client_socket = create_socket('127.0.0.1', 502)


class Const:
    relay_time = 500


class DataFromModbus:
    def __init__(self):
        # reading data from file
        self.mysocket = MySocket()
        self.amperage_adresses_from_file = read_registers_adress_from_file_into_array()
        self.rel_opt_warn_adresses_from_file = read_opt_rel_warn_from_file_into_arrays()
        self.opt_data_description = self.rel_opt_warn_adresses_from_file[0]
        self.opt_adresses = self.rel_opt_warn_adresses_from_file[1]

        self.rel_data_description = self.rel_opt_warn_adresses_from_file[2]
        self.rel_adresses = self.rel_opt_warn_adresses_from_file[3]

        self.warn_data_description = self.rel_opt_warn_adresses_from_file[4]
        self.warn_adresses = self.rel_opt_warn_adresses_from_file[5]

        # quantity of reading coils
        self.quantity_of_amperage_registers = len(self.amperage_adresses_from_file)
        self.quantity_of_rel = len(self.rel_data_description)
        self.quantity_of_rel_reg = len(self.rel_adresses)
        self.quantity_of_opt = len(self.opt_data_description)
        self.quantity_of_opt_reg = len(self.opt_adresses)
        self.quantity_of_warn_reg = len(self.warn_adresses)
        self.quantity_of_warn = len(self.warn_data_description)

    def get_rel_data_from_modbus(self):
        # getting data from modbus
        array = get_arr_relays_from_modbus(self.rel_adresses, self.quantity_of_rel_reg,
                                           self.quantity_of_rel,
                                           self.rel_data_description, self.mysocket.client_socket)
        create_log(array, self.quantity_of_rel)
        return array

    def get_opt_data_from_modbus(self):
        array = get_arr_optrons_from_modbus(self.opt_adresses, self.quantity_of_opt_reg,
                                            self.quantity_of_opt,
                                            self.opt_data_description, self.mysocket.client_socket)
        create_log(array, self.quantity_of_opt)
        return array

    def get_amperage_data_from_modbus(self):
        array = get_arr_amperage_from_modbus(self.amperage_adresses_from_file,
                                            self.quantity_of_amperage_registers,
                                            self.mysocket.client_socket)
        create_log(array, self.quantity_of_amperage_registers)
        return array

    def get_warnings_data_from_modbus(self):
        array = get_arr_warnings_from_modbus(self.warn_adresses, self.quantity_of_warn_reg, self.quantity_of_warn,
                                             self.warn_data_description,
                                             self.mysocket.client_socket)
        create_log(array, self.quantity_of_amperage_registers)
        return array


class Colors:
    bg_frame_info_color = 'MediumPurple3'
    bg_frame_pic_color = 'MediumPurple2'
    bg_frame_buttons_color = 'MediumPurple2'


class MyStyle(ttk.Style):
    buttons_frame_style = 'My1.TFrame'
    info_frame_style = 'My2.TFrame'
    picture_frame_style = 'My3.TFrame'
    treeview_style = 'Treeview'
    treeview_style_2 = 'rel.Treeview'
    rowheight = 20

    def __init__(self):
        # setup
        super().__init__()

    def set_theme(self):
        self.theme_use("clam")

    def set_styles(self):
        # settings
        self.configure('My1.TFrame', background=Colors.bg_frame_buttons_color)
        self.configure('My2.TFrame', background=Colors.bg_frame_info_color)
        self.configure('My3.TFrame', background=Colors.bg_frame_pic_color)
        self.configure('Treeview', backgroung=Colors.bg_frame_info_color, fieldbackground=Colors.bg_frame_info_color,
                       backforeground=Colors.bg_frame_info_color, rowheight=MyStyle.rowheight)


class RelaysWindow(tkinter.Toplevel):
    def __init__(self, parent):
        # setup
        super().__init__(parent)
        self.mbdata = DataFromModbus()
        self.geometry('350x350')
        self.configure(bg=Colors.bg_frame_info_color)
        self.title('Реле')

        # widgets
        self.relays_table = ttk.Treeview(self, style='Treeview', selectmode='browse')

        # settings
        self.relays_table.configure(height=self.mbdata.quantity_of_rel)
        self.relays_table.tag_configure('mytag', background=Colors.bg_frame_info_color)
        self.relays_table['columns'] = ('Название', 'Состояние')
        self.relays_table.column('#0', width=0, stretch=NO)
        self.relays_table.column('Название', width=100, anchor=CENTER)
        self.relays_table.column('Состояние', width=100, anchor=CENTER)

        self.relays_table.heading('#0', text='')
        self.relays_table.heading('Название', text='Навзвание', anchor=CENTER)
        self.relays_table.heading('Состояние', text='Состояние')
        self.show_data()
        self.relays_table.place(relx=0.2, rely=0.1)
        self.relays_table.after(Const.relay_time, self.show_data)


    def show_data(self):
        for i in self.relays_table.get_children():
            self.relays_table.delete(i)

        relays_data = self.mbdata.get_rel_data_from_modbus()
        if relays_data != 0:
            for i in range(self.mbdata.quantity_of_rel):
                name = str(relays_data[i][0])
                self.relays_table.insert(parent='', index='end', tags='mytag', values=(
                    name, relays_data[i][3]))
        self.relays_table.after(Const.relay_time, self.show_data)


class OptronsWindow(tkinter.Toplevel):
    def __init__(self, parent):
        # setup
        super().__init__(parent)
        self.mbdata = DataFromModbus()
        self.geometry('450x550')
        self.configure(bg=Colors.bg_frame_info_color)
        self.title('Оптроны')

        # widgets
        self.optrons_table = ttk.Treeview(self, style='Treeview', selectmode='browse')

        # settings
        self.optrons_table.configure(height=self.mbdata.quantity_of_opt)
        self.optrons_table.tag_configure('mytag', background=Colors.bg_frame_info_color)
        self.optrons_table['columns'] = ('Название', 'Состояние')
        self.optrons_table.column('#0', width=0, stretch=NO)
        self.optrons_table.column('Название', width=150, anchor=CENTER)
        self.optrons_table.column('Состояние', width=100, anchor=CENTER)

        self.optrons_table.heading('#0', text='')
        self.optrons_table.heading('Название', text='Навзвание', anchor=CENTER)
        self.optrons_table.heading('Состояние', text='Состояние')
        self.show_data()
        self.optrons_table.place(relx=0.2, rely=0.1)
        self.optrons_table.after(Const.relay_time, self.show_data)


    def show_data(self):
        for i in self.optrons_table.get_children():
            self.optrons_table.delete(i)

        optrons_data = self.mbdata.get_opt_data_from_modbus()
        if optrons_data != 0:
            for i in range(self.mbdata.quantity_of_opt):
                name = str(optrons_data[i][0])
                self.optrons_table.insert(parent='', index='end', tags='mytag', values=(
                    name, optrons_data[i][3]))
        self.optrons_table.after(Const.relay_time, self.show_data)


class ErrorsWindow(tkinter.Toplevel):
    def __init__(self, parent):
        # setup
        super().__init__(parent)
        self.mbdata = DataFromModbus()
        scroll_bar = Scrollbar(self, orient='horizontal')

        self.geometry('500x350')
        self.configure(bg=Colors.bg_frame_info_color)
        self.relays_table = ttk.Treeview(self, style='Treeview')
        self.title('Неисправности')

        # widgets
        self.warnings_table = ttk.Treeview(self, style='Treeview', selectmode='browse', yscrollcommand=scroll_bar)

        # settings
        self.warnings_table.configure(height=10)
        self.warnings_table.tag_configure('mytag_red', background='red')
        self.warnings_table.tag_configure('mytag_green', background='green')
        self.warnings_table['columns'] = ('Название', 'Состояние')
        self.warnings_table.column('#0', width=0, stretch=NO)
        self.warnings_table.column('Название', width=150, anchor=CENTER)
        self.warnings_table.column('Состояние', width=100, anchor=CENTER)

        self.warnings_table.heading('#0', text='')
        self.warnings_table.heading('Название', text='Навзвание', anchor=CENTER)
        self.warnings_table.heading('Состояние', text='Состояние')
        self.show_data()
        self.warnings_table.place(relx=0.2, rely=0.1)
        self.warnings_table.after(Const.relay_time, self.show_data)


    def show_data(self):
        for i in self.warnings_table.get_children():
            self.warnings_table.delete(i)

        warnings_data = self.mbdata.get_warnings_data_from_modbus()
        if warnings_data != 0:
            for i in range(self.mbdata.quantity_of_warn):
                name = str(warnings_data[i][0])
                if warnings_data[i][3] == 1:
                    self.warnings_table.insert(parent='', index='end', tags='mytag_red', values=(
                        name, warnings_data[i][3]))
                elif warnings_data[i][3] == 0:
                    self.warnings_table.insert(parent='', index='end', tags='mytag_green', values=(
                        name, warnings_data[i][3]))
        self.warnings_table.after(Const.relay_time, self.show_data)


class App(Tk):
    first_run = True

    def __init__(self, title, sizex, sizey):
        # setup
        super().__init__()
        self.title(title)
        self.geometry(f'{sizex}x{sizey}')
        self.configure(bg='MediumPurple3')
        self.minsize(width=750, height=600)

        # widgets
        self.style = MyStyle()
        self.style.set_theme()
        self.style.set_styles()
        self.frm_info = InfoFrame(self, MyStyle.info_frame_style)
        self.frm_buttons = ButtonFrame(self, MyStyle.buttons_frame_style)
        self.frm_picture = PictureFrame(self, MyStyle.picture_frame_style)

        self.frm_picture.after(Const.relay_time, self.refresh_frames)
        App.first_run = False

    def refresh_frames(self):
        self.frm_picture.destroy()
        self.frm_info.destroy()
        self.frm_picture = PictureFrame(self, MyStyle.picture_frame_style)
        self.frm_info = InfoFrame(self, MyStyle.info_frame_style)
        self.frm_picture.after(Const.relay_time, self.refresh_frames)


class InfoFrame(ttk.Frame):

    def __init__(self, parent, mystyle):
        # setup
        super().__init__(parent, style=mystyle)
        self.place(relx=0.4, rely=0, relwidth=0.40, relheight=1)
        self.mbdata = DataFromModbus()

        # widgets
        self.amperage_table = ttk.Treeview(self, style=MyStyle.treeview_style, selectmode='browse')

        # settings
        self.amperage_table.configure(height=self.mbdata.quantity_of_amperage_registers // 2)
        self.amperage_table.tag_configure('mytag', background=Colors.bg_frame_info_color)
        self.amperage_table['columns'] = ('phase', 'Модуль тока', 'После поворота')
        self.amperage_table.column('#0', width=0, stretch=NO)
        self.amperage_table.column('phase', width=40, anchor=CENTER)
        self.amperage_table.column('Модуль тока', width=100, anchor=CENTER)
        self.amperage_table.column('После поворота', width=100, anchor=CENTER)

        self.amperage_table.heading('#0', text='')
        self.amperage_table.heading('phase', text='Фаза', anchor=CENTER)
        self.amperage_table.heading('Модуль тока', text='Модуль тока', anchor=CENTER)
        self.amperage_table.heading('После поворота', text='После поворота')
        self.amperage_table.place(relx=0.05, rely=0.35)
        self.update_data()

    def update_data(self):
        amperage_data = self.mbdata.get_amperage_data_from_modbus()
        if amperage_data != 0:
            for i in range(self.mbdata.quantity_of_amperage_registers // 4):
                name = str(amperage_data[i][0])
                self.amperage_table.insert(parent='', index='end', tags='mytag', values=(
                    name.removeprefix('Модуль тока фазы '), amperage_data[i][2], amperage_data[i + 3][2]))
            for i in range(6, 9):
                name = str(amperage_data[i][0])
                self.amperage_table.insert(parent='', index='end', tags='mytag', values=(
                    name.removeprefix('Модуль тока фазы '), amperage_data[i][2], amperage_data[i + 3][2]))


class ButtonFrame(ttk.Frame):
    def __init__(self, parent, mystyle):
        # setup
        self.parent = parent
        super().__init__(parent, style=mystyle)
        self.place(relx=0.80, rely=0, relwidth=0.2, relheight=1)

        # buttons
        self.btn_relay = ttk.Button(self, command=self.show_relays, text='Реле')
        self.btn_optrons = ttk.Button(self, command=self.show_optrons, text='Оптроны')
        self.btn_errors = ttk.Button(self, command=self.show_errors, text='Неисправности')

        # settings
        self.btn_errors.place(relx=0.01, rely=0.2)
        self.btn_optrons.place(relx=0.05, rely=0.4)
        self.btn_relay.place(relx=0.05, rely=0.6)

    def show_relays(self):
        newwindow = RelaysWindow(self.parent)
        newwindow.mainloop()

    def show_optrons(self):
        newwindow = OptronsWindow(self.parent)
        newwindow.mainloop()

    def show_errors(self):
        newwindow = ErrorsWindow(self.parent)
        newwindow.mainloop()


class PictureFrame(ttk.Frame):
    def __init__(self, parent, mystyle):
        # setup
        super().__init__(parent, style=mystyle)
        mbdata = DataFromModbus()
        flag = True
        self.img_warning = ImageTk.PhotoImage(Image.open('pic_red.png').resize((650, 500)))
        self.img_default = ImageTk.PhotoImage(Image.open('pic_green.png').resize((650, 500)))

        # widgets
        self.label = Label(self, image=self.img_default, bg=Colors.bg_frame_pic_color)

        # settings
        self.label.pack()
        self.label.place(x=0, y=-50, width=280, relheight=1)
        try:
            array = mbdata.get_warnings_data_from_modbus()
            for i in range(mbdata.quantity_of_warn):
                if array[i][3] == 1:
                    flag = False
        except:
            self.label_error = Label(self, bg=Colors.bg_frame_pic_color, text='Ошибка чтения данных')
            self.label_error.place(rely=0.9, relx=0.3)

        if flag == False:
            self.label.configure(image=self.img_warning)
        else:
            self.label.configure(image=self.img_default)

        self.place(relx=0, rely=0, relwidth=0.35, relheight=1)


app = App('My window', 750, 600)
app.mainloop()
