import PySimpleGUI as sg
import os.path
import numpy as np
from matplotlib.widgets  import RectangleSelector
import matplotlib.figure as figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import pyperclip

# instantiate backend class and functions
with open("AlphaStepBackend.py") as f:
    exec(f.read())

# instantiate matplotlib figure
fig = figure.Figure()
DPI = fig.get_dpi()
fig.set_size_inches(300 * 2 / float(DPI), 607 / float(DPI))

# ------------------------------- This is to include a matplotlib figure in a Tkinter canvas
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


def line_select_callback(eclick, erelease):
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata

class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)


# ==================================================================
#################################################################### PySimpleGUI CODE
# ==================================================================


############################################################### Loading Data Tab
# =============================================================


load_data_tab = [
    [
        sg.Text("Select Data File"),
        # sg.In(size=(25,1), enable_events=True, key="-FOLDER-"),
        sg.FileBrowse(key = "-IN-"),
    ],
    [sg.Column(
        layout = [
            [sg.Text("Partition Data")],
            [sg.Text("Starting Point: "),sg.In(key = "-DATA START-", size = (5,1))],
            [sg.Text("Ending Point: "), sg.In(key = "-DATA END-", size = (5,1))],
        ]
    ),
    sg.VSeparator(),
    sg.Column(
        layout = [
            [sg.B("Load", key ="load")],
            [sg.B("Visualize", key = "-VIZ-")],
        ]
    )
    ],
]

smoothing_options = ["Savitzky-Golay", "Boxcar", "Cubic Spline"]


############################################################### Preprocessing Tab
# =============================================================


preprocessing_tab = [
    [
        sg.Text("Choose Preprocessing Options"),
    ],
    [
        sg.Column(
            layout = [
                [sg.Text("Determine Fitting Parameters")],
                [sg.B("Ideal SG Factor", key = "-IDEAL SG-"), sg.Text("Not Determined", key = "-IDEAL SG OUT-")],
                [sg.B("Ideal T-test Window", key = "-IDEAL T WIN-"), sg.Text("Not Determined", key = "-IDEAL T WIN OUT-")]
            ]
        ),
        
        sg.VSeparator(),
        
        sg.Column(
            layout = [
                [sg.Text("Padding")],
                [sg.Text("Front Padding"), sg.In(key = "-FRONT PAD-", size = (5,1))],
                [sg.Text("End Padding"), sg.In(key = "-END PAD-", size = (5,1))],
                [sg.B("Perform Padding", key = "-DO PAD-")]
            ]
        ),
        
        sg.VSeparator(),
        
        sg.Column(
            layout = [
                [sg.Text("Select Smoothing Option")],
                [sg.Combo(smoothing_options, key = "-SMOOTHING METHOD-", readonly=True, enable_events=True)],
                [sg.Text("Enter Smoothing Factor"),sg.In(key = "-SMOOTHING FACTOR-", size=(5,1)), sg.B("Smooth", key = "-SMOOTH COMMAND-")],
                [sg.B("Add Smoothed Data To Plot", key = "-ADD SMOOTHED-"),sg.B("Plot Smoothed Alone", key = "-SMOOTH ALONE-")]
            ]
    ),
    ]
]


############################################################### Fitting Tab
# =============================================================

filter_options = ["SG", "Boxcar", "None"]
output_options = ["Yes","No"]
data_options = ["Raw","Smoothed"]
fitting_tab = [
    [sg.Text('Choose Fitting Options')],
    [sg.Column(
        layout = [
            [sg.Text("T-test Window Size"), sg.In(key = "-T TEST WIN-", size = (5,1))],
            [sg.Text("Set the dt"), sg.In(key = "-DT-", size = (5,1))],
            [sg.Text("Minimum p-Value"), sg.In(key = "-MIN P-", size = (5,1))],
            [sg.Text("Maximum p-Value"), sg.In(key = "-MAX P-", size = (5,1))]
        ]
    ),
    sg.VSeparator(),
    sg.Column(
        layout = [
            [sg.Text("Set Exclusion Value"), sg.In(key = "-EXCLUSION-",size = (5,1))],
            [sg.Text("Include Filter On Graph?"), sg.Combo(filter_options, key = "-PLOT FILTER-", readonly = True, enable_events = True)],
            [sg.Text("Output Results?"), sg.Combo(output_options, key = "-FINAL OUT-", readonly = True, enable_events = True)]
        ]
    ),
    sg.VSeparator(),
    sg.Column(
        layout = [
            [sg.B("Use Default Parameters", key = "-DEFAULTS-")],
            [sg.Text("Data To Be Fit: "), sg.Combo(data_options,key = "-FIT TYPE-", readonly = True, enable_events = True)],
            [sg.B("Perform T-test & Fitting", key = "-DO FIT-")],
        ]
    ),
    sg.VSeparator(),
    sg.Column(
        layout = [
            [sg.Text("Output File Name"), sg.In(key = "-OUTPUT FILE NAME-")],
            [sg.B("Save Output", key = "-SAVE OUTPUT-")]
        ]
    ),
    ],
]

             
############################################################### MultiGaussian Tab
# =============================================================

# AxisSel = ["On","Off"]
# AxesThick = ["Normal", "Thin", "Thick"]
# TickLocs = ["Inside","Mixed","Outside"]
# TickThick = ["Normal", "Thin"]
# MultiGauss_tab = [
#     [sg.Text('Set Plotting Parameters')],
#     [sg.Column(
#         layout = [
#             [sg.Text("Axes lines to display")],
#             [sg.Text("Left:"), sg.Combo(AxisSel, key = "-Axis L-", readonly = True, enable_events = True),
#              sg.Text("Right:"), sg.Combo(AxisSel, key = "-Axis R-", readonly = True, enable_events = True),
#              sg.Text("Top:"), sg.Combo(AxisSel, key = "-Axis T-", readonly = True, enable_events = True),
#              sg.Text("Bottom:"), sg.Combo(AxisSel, key = "-Axis B-", readonly = True, enable_events = True)],
#             [sg.Text("Axes thickness"), sg.Combo(AxesThick, key = "-Axes Thickness-", readonly = True, enable_events = True)] 
#             [sg.Text("Axis tick location"), sg.Combo(TickLocs, key = "-Tick Location-", readonly = True, enable_events = True)],
#             [sg.Text("Tick thickness"), sg.Combo(TickThick, key = "-Tick Thickness-", readonly = True, enable_events = True)],
#             [sg.Text("Plotted line thickness"), sg.Combo(TickThick, key = "-Line Thickness-", readonly = True, enable_events = True)]
#         ]
#     )
#     ],
#     sg.VSeparator(),
#     sg.Column(
#         layout = [
#             [sg.Text("Grid"), sg.Combo(AxisSel, key = "-Grid-", readonly = True, enable_events = True)],
            
        
            
table_headings = ["step height", 
                  "step width", 
                  "dwell time",
                  "step rate",
                  "step start",
                  "Processivity",
                  "dwell position",
                  "step position",
                  "average rate",
                  "average dwell",
                  "average width",
                  "overall dwell",
                  "overall turns",
                  "overall rate"]
               
############################################################### Plotting Tab                
# =============================================================


results_table = sg.Table(values =[[0,1,0,1],[0,1,0,1],[0,1,0,1],[0,1,0,1]], headings = table_headings, 
                         key = "-RESULTS TABLE-", 
                         auto_size_columns=True,
                         display_row_numbers=False,
                         justification='center',
                         selected_row_colors='red on yellow',
                         enable_events=True,
                         expand_x=True,
                         expand_y=True,
                         enable_click_events=True)
                
plot_tab = [
    [sg.Canvas(key='controls_cv')],
    [sg.Column(
        layout=[
            [sg.Canvas(key='fig_cv',
                       # it's important that you set this size
                       size=(300 * 2, 600)
                       )]
        ],
        background_color='#DAE0E6',
        pad=(0, 0)
    ),
    sg.VSeparator(),
    sg.Column(
        layout = [
            [results_table]
        ]
    )]
]

              
############################################################### Defining Layouts of The Window                
# =============================================================

#-------------------------------------------------------------- Defines the parameter tabs layout

layout = [
    [sg.TabGroup([
        [sg.Tab('Load Data', load_data_tab)],
        [sg.Tab('Preprocessing', preprocessing_tab)],
        [sg.Tab('Fitting', fitting_tab, key = "-FIT TAB-")],
    ])],
    [sg.B("Clear Plotting Area", key = "-CLEAR PLOT-")]
]

#-------------------------------------------------------------- Defines the plotting tabs layout

layout2 = [
    [sg.TabGroup([
        [sg.Tab('Plots',plot_tab)]
        ],
        key = "Plot Tabs")
    ]
]


############################################################### Initializing The Window                
# =============================================================
                
window = sg.Window('Step Finding T-test', layout + layout2, resizable = True, finalize = True)
window.bind("<Control-C>", "Control-C")
window.bind("<Control-c>", "Control-C")
index = 1
while True:
    event, values = window.read()
    if event == "load":
        if values["-IN-"] != '':
            if values["-DATA START-"]  != '' and values["-DATA END-"] != '':
                start = int(values["-DATA START-"])
                end = int(values["-DATA END-"])
                num_rows = end-start
                print(f"NOTE: data start index at {start}")
                print(f"NOTE: data end index at {end}")
                data = np.loadtxt(values["-IN-"],skiprows = start, max_rows = num_rows)           
            elif values["-DATA START-"] == '' and values["-DATA END-"] != '':
                end = int(values["-DATA END-"])
                print("NOTE: no start index give, choosing 0")
                print(f"NOTE: data end index at {end}")
                data = np.loadtxt(values["-IN-"],skiprows = 0, max_rows = end)  
            elif values["-DATA END-"] == '' and values["-DATA START-"]  != '':    
                start = int(values["-DATA START-"])
                print(f"NOTE: data start index at {start}")
                print(f"NOTE: data end index at {end}")
                data = np.loadtxt(values["-IN-"],skiprows = start)
                print("NOTE: no endpoint specified, using whole trace from starting point")
            elif values["-DATA END-"] == '' and values["-DATA START-"]  == '':
                data = np.loadtxt(values["-IN-"])
                print("NOTE: loading whole trace")
            print("NOTE: data loaded successfully")
        elif values["-IN-"] == '':
            print("ERROR: no input file selected")
    
    elif event == "-IDEAL SG-":
        N = FindSGWindowSize(dat = data)
        window["-IDEAL SG OUT-"].update(value = N)
        
    
    elif event == "-CLEAR PLOT-":
        fig.delaxes(ax)
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)

    elif event == "-DO PAD-":
        if values["-FRONT PAD-"] == '':
            values["-FRONT PAD-"] = 0
        if values["-END PAD-"] == '':
            values["-END PAD-"] = 0
        data = Pad_Data(data, int(values["-FRONT PAD-"]), int(values["-END PAD-"]))
        fig.delaxes(ax)
        ax = fig.add_subplot(111)
        padded_data, = ax.plot(data)
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
    
    elif event == "-SMOOTH ALONE-":
        fig.delaxes(ax)
        ax = fig.add_subplot(111)
        smoothed_plot, = ax.plot(smoothed_data)
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
    
    elif event == "-IDEAL T WIN-":
        avg, bic, aic = BestTWindow(data)
        window["-IDEAL T WIN OUT-"].update(value = "BIC: {}, AIC: {}, AVG: {}".format(bic,aic,avg))
        
    elif event == "-SMOOTH COMMAND-":
        if values["-SMOOTHING METHOD-"] == "Savitzky-Golay":
            smooth_factor = int(values["-SMOOTHING FACTOR-"])
            if (smooth_factor % 2) != True:
                smooth_factor += 1
            smoothed_data = SG_Smoothing(data, win = smooth_factor, order = 4)
                                         
    elif event == "-ADD SMOOTHED-":
        smoothed_line, = ax.plot(smoothed_data)
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
    
    elif event == sg.WIN_CLOSED:
        break
    
    elif event == "-VIZ-":
        ax = fig.add_subplot(111)
        line, = ax.plot(data)
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
    
    elif event == "-DO FIT-":
        if values["-FIT TYPE-"] == "Raw":
            fs = fit_signal(trace = data, dt = float(values["-DT-"]), 
                        window_length = int(values["-T TEST WIN-"]), 
                        min_threshold = float(values["-MIN P-"]), 
                        max_threshold = float(values["-MAX P-"]),
                        exclusion = float(values["-EXCLUSION-"]))
        elif values["-FIT TYPE-"] == "Smoothed":
            fs = fit_signal(trace = smoothed_data, dt = float(values["-DT-"]), 
                        window_length = int(values["-T TEST WIN-"]), 
                        min_threshold = float(values["-MIN P-"]), 
                        max_threshold = float(values["-MAX P-"]),
                        exclusion = float(values["-EXCLUSION-"]))
        for i in range(1,11):
            if i == 1:
                fit = fs.fit(float(values["-DT-"]), maxiter = i*1500)
            elif i!=1 and i!=10:
                fit = fs.fit(float(values["-DT-"]), refitted = True, maxiter = i*2000)
            elif i == 10:
                fit = fs.fit(float(values["-DT-"]), refitted = True, results = True)
        fig = fs.plot(raw = data, colors = None, replotted = True, filtersize = smooth_factor, filtertype = 'SG')
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
        fit_results = fit.values.tolist()
        window["-RESULTS TABLE-"].update(values = fit_results)
        
    elif event == '-SAVE OUTPUT-':
        FullTable = [table_headings]
        FullTable.extend(fit_results)
        WriteOutFile2(FullTable, str(values["-OUTPUT FILE NAME-"]))

    elif event == '-DEFAULTS-':
        active_tab_layout = window[event].select()[0]
        for elem in active_tab_layout:
            if isinstance(elem, sg.In) and values[elem_key] == '':
                print(f"'{elem_key}' on Tab 1 has an empty string value")
                # change the element's value to None
                elem.update(None) 
        
    elif event == "Control-C":
        items = values['-RESULTS TABLE-']                           # Indexes for selection
        lst = list(map(lambda x:' '.join(str(fit_results[x])), items))  # Get data list for selection
        text = "\n".join(lst)                               # Each line for one selected row in table
        pyperclip.copy(text)
window.close()