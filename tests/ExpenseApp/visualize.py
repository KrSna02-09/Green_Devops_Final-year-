import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def show_category_pie_chart(parent_app, data):
    """
    Opens a pop-up window with a pie chart.
    parent_app: The main GUI window (so the popup floats on top)
    data: List of tuples [(Category, Amount), ...]
    """
    if not data:
        return False # Return False to let GUI know there is no data

    cats = [x[0] for x in data]
    amts = [x[1] for x in data]

    # Create Pop-up Window
    chart_window = ctk.CTkToplevel(parent_app)
    chart_window.title("Expense Breakdown")
    chart_window.geometry("600x500")
    
    # Make sure it stays on top
    chart_window.attributes('-topmost', True)

    # Draw Chart using Matplotlib
    fig, ax = plt.subplots(figsize=(6, 5), facecolor="#2b2b2b")
    
    # Customizing the pie chart
    wedges, texts, autotexts = ax.pie(amts, labels=cats, autopct='%1.1f%%', startangle=140, 
                                      textprops={'color':"white"})
    
    ax.set_title("Expenses by Category", color="white", fontsize=14, fontweight='bold')
    
    # Embed in Tkinter Window
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    return True