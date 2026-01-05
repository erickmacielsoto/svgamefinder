"""
Componentes UI reutilizables
"""
import customtkinter as ctk


class CTkTooltip:
    """Clase para crear tooltips (ayuda al hacer hover) en widgets de CustomTkinter"""
    
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self.job_id = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)
    
    def on_enter(self, event=None):
        self.schedule_tooltip()
    
    def on_leave(self, event=None):
        self.unschedule_tooltip()
        self.hide_tooltip()
    
    def on_motion(self, event=None):
        self.unschedule_tooltip()
        self.schedule_tooltip()
    
    def schedule_tooltip(self):
        self.unschedule_tooltip()
        self.job_id = self.widget.after(self.delay, self.show_tooltip)
    
    def unschedule_tooltip(self):
        if self.job_id:
            self.widget.after_cancel(self.job_id)
            self.job_id = None
    
    def show_tooltip(self):
        if self.tooltip:
            return
        
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(
            self.tooltip,
            text=self.text,
            font=("Arial", 10),
            corner_radius=5,
            fg_color=("gray70", "gray30"),
            padx=8,
            pady=4
        )
        label.pack()
        
        # Ajustar posición para que no se salga de la pantalla
        self.tooltip.update_idletasks()
        screen_width = self.tooltip.winfo_screenwidth()
        screen_height = self.tooltip.winfo_screenheight()
        tooltip_width = self.tooltip.winfo_width()
        tooltip_height = self.tooltip.winfo_height()
        
        if x + tooltip_width > screen_width:
            x = screen_width - tooltip_width - 10
        if y + tooltip_height > screen_height:
            y = self.widget.winfo_rooty() - tooltip_height - 5
        
        self.tooltip.wm_geometry(f"+{x}+{y}")
    
    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None





