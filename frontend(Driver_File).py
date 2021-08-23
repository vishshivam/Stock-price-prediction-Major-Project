# This is the driver file. Start this script

import PySimpleGUI as psg
import simulator as sim
import threading
import sys
import subprocess
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
import nSentiment as ns

plt.ion()


def gui():
    psg.theme("LOL")

    layout = [

        [psg.Text('Ticker', justification='left') ],
        [psg.InputText(justification='left', key='ticker', default_text="TSLA")],
        [psg.Text('Start Date  ', justification='left')],
        [psg.InputText(justification='left', key='s_Date',default_text="2015-3-1")],

        [psg.Text('Number of Days', justification='left')],
        [psg.InputText(justification='left',  key='days', default_text='2')],

        [psg.Text('Iterations', justification='left')],
        [psg.InputText(justification='left', key='iterations', visible=True, default_text='30')],
        [psg.Text("Enable Market Sentiment Analyzer?", justification='left')],
        [psg.Combo(["YES", "NO"], default_value="NO", key='sentiment', readonly=True,
                   enable_events=True)],

        [psg.Text("Verbosity", key="verbosity"),
         psg.Radio("ON", "verbosity", key='verbose_ON', enable_events=True, default=False),
         psg.Radio("OFF", "verbosity", key="verbose_OFF", enable_events=True, default=True)],
        [psg.Button("Run"), psg.Button("Cancel")],
        [psg.Output(size=(85, 10), background_color='white', text_color='black', key='Status_Box', visible=False)],
        [psg.B('Plot')],
        [psg.Text('Controls:')],
        [psg.Canvas(key='controls_cv')],

        [psg.T('Figure:')],
        [psg.Column(
            layout=[
                [psg.Canvas(key='fig_cv',
                           # it's important that you set this size
                           size=(300 * 2, 300))]],
            background_color='#DAE0E6', pad=(0, 0))],


        #[psg.Output(size=(110, 10), background_color='black', text_color='white', key='Status_Box', visible=False)],
        # [psg.T('Prompt>'), psg.Input(key='-IN-', do_not_clear=False)],


 ]

    window = psg.Window('Market Prediction ',  resizable=True).Layout(layout)

    results = ['temp']
    while True:
        event, values = window.read()
        if event == psg.WIN_CLOSED or event == 'Cancel':
            break
        if event == 'Run':

            t1 = threading.Thread(target=sim.simulate_mc, args=(values,results, ), daemon=True)
            #t = threading.Thread(target=test3.func, args=(results,0,), daemon=True)
            t1.start()
            t1.join(1)
            print("Working...")
            if values["sentiment"] == "YES":
                #t2 = threading.Thread(target=ns.sentimentAnalysis, args=(str(values['ticker']),), daemon=True)
                # t = threading.Thread(target=test3.func, args=(results,0,), daemon=True)
                t2 = threading.Thread(target=ns.sentimentAnalysis, args=(str(values['ticker']),), daemon=True)
                t2.start()
                t2.join(1)
                print("[INFO] Market Sentiment Analysis started simultaneously.")
            else:
                print('[INFO] Not Using Current Market Analysis.')

            # ------------------------------- PASTE YOUR MATPLOTLIB CODE HERE


        if values["verbose_ON"] == True:

            window.Element("Status_Box").Update(visible=True)

        if values["verbose_OFF"] == True:

            window.Element("Status_Box").Update(visible=False)

        verbosity = values['verbose_ON']

        if event == 'Plot':
            graph_data = results[0] # Extracting data to plot a graph
            plt.figure(figsize=(10, 6))
            fig = plt.gcf()
            DPI = fig.get_dpi()
            # ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
            fig.set_size_inches(604 * 2 / float(DPI), 604 / float(DPI))
            # -------------------------------
            # x = np.linspace(0, 2 * np.pi)
            # y = np.sin(x)
            # x = xy[0]
            # y = xy[1]
            # plt.plot(x, y)
            # plt.title('y=sin(x)')
            # plt.xlabel('X')
            # plt.ylabel('Y')
            # plt.grid()
            print("[INFO] Plotting is in Progress. Application may show status as 'Not Responding'. Please DO NOT Close it.")
            plt.plot(graph_data)


            # ------------------------------- Instead of plt.show()
            draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
            print("[INFO] Plotting Done. You may have to wait for few moments to let the application load the graph in case of High iterations and number of Days.")








# Showing status in the command line in GUI environment
def runCommand(cmd, timeout=None, window=None):
    nop = None
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ''
    for line in p.stdout:
        line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
        output += line
        print(line)
        window.refresh() if window else nop  # yes, a 1-line if, so shoot me

    retval = p.wait(timeout)
    return (retval, output)


# This part contains the plotting of the graph in GUI itself

def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)

class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)


gui()