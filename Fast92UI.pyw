import os
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

class ConverterApp(ttk.Frame):
    """GUI application for Fastman92 Processor with tabbed interface for Single and Batch conversions."""
    
    def __init__(self, parent):
        super().__init__(parent, padding="10")
        self.parent = parent
        self.parent.title("Fastman92 Processor GUI")
        self.parent.resizable(False, False)
        self.log_queue = queue.Queue()  # For thread-safe log and progress updates
        self.init_vars()
        self.create_widgets()
        self.grid(sticky="nsew")
        self.poll_queue()  # Start polling the queue
    
    def init_vars(self):
        """Initialize tkinter variables and option lists."""
        # Single conversion variables
        self.input_file_var = tk.StringVar()
        self.output_file_var = tk.StringVar()
        self.string_list_var = tk.StringVar()
        self.move_position_var = tk.StringVar()
        self.additional_args_var = tk.StringVar()
        
        # Conversion options (shared)
        self.file_type_var = tk.StringVar(value="ipl")
        self.input_type_var = tk.StringVar(value="binary")
        self.output_type_var = tk.StringVar(value="text")
        # Renamed variable to conversion_game for clarity (if this is truly the game parameter)
        self.conversion_game_var = tk.StringVar(value="GAME_EXACT_GTAIV_PC")
        
        self.file_type_options = ["ipl", "ide", "wpl", "idb"]
        self.input_type_options = ["binary", "text"]
        self.output_type_options = ["binary", "text"]
        self.game_options = [
            "GAME_EXACT_GTAIV_PC",
            "GAME_EXACT_BULLY_SCHOLARSHIP_EDITION_PC",
            "GAME_EXACT_GTASA_PC",
            "GAME_EXACT_GTAVC_PC"
        ]
        
        # Batch conversion variables
        self.batch_files = []
        self.batch_output_folder = tk.StringVar()  # Variable for output folder
        
    def create_widgets(self):
        """Construct the tabbed interface."""
        notebook = ttk.Notebook(self)
        notebook.grid(row=0, column=0, sticky="nsew")
        
        # Create frames for each tab
        self.single_tab = ttk.Frame(notebook, padding="10")
        self.batch_tab = ttk.Frame(notebook, padding="10")
        
        notebook.add(self.single_tab, text="Single Conversion")
        notebook.add(self.batch_tab, text="Batch Conversion")
        
        self.create_single_tab_widgets(self.single_tab)
        self.create_batch_tab_widgets(self.batch_tab)
    
    def create_single_tab_widgets(self, parent):
        """Widgets for the Single Conversion tab."""
        # File Selection Frame
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding="10")
        file_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.create_file_selection_row(file_frame, "Input File:", self.input_file_var, self.browse_input_file, row=0)
        self.create_file_selection_row(file_frame, "Output File:", self.output_file_var, self.browse_output_file, row=1)
        self.create_file_selection_row(file_frame, "String List File (optional):", self.string_list_var, self.browse_string_list_file, row=2)
        
        # Conversion Options Frame
        options_frame = ttk.LabelFrame(parent, text="Conversion Options", padding="10")
        options_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(options_frame, text="File Type:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        ttk.OptionMenu(options_frame, self.file_type_var, self.file_type_var.get(), *self.file_type_options).grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(options_frame, text="Input Type:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        ttk.OptionMenu(options_frame, self.input_type_var, self.input_type_var.get(), *self.input_type_options).grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(options_frame, text="Output Type:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        ttk.OptionMenu(options_frame, self.output_type_var, self.output_type_var.get(), *self.output_type_options).grid(row=2, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(options_frame, text="Conversion Game:").grid(row=3, column=0, sticky="w", padx=5, pady=3)
        ttk.OptionMenu(options_frame, self.conversion_game_var, self.conversion_game_var.get(), *self.game_options).grid(row=3, column=1, sticky="ew", padx=5, pady=3)
        
        # Advanced Options Frame
        advanced_frame = ttk.LabelFrame(parent, text="Advanced Options", padding="10")
        advanced_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(advanced_frame, text="Move Position (X Y Z):").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        ttk.Entry(advanced_frame, textvariable=self.move_position_var, width=40).grid(row=0, column=1, padx=5, pady=3)
        ttk.Label(advanced_frame, text="Additional Args:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        ttk.Entry(advanced_frame, textvariable=self.additional_args_var, width=40).grid(row=1, column=1, padx=5, pady=3)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=3)
        
        # Run Conversion Button
        run_button = ttk.Button(parent, text="Run Conversion", command=self.run_conversion_thread)
        run_button.grid(row=4, column=0, pady=10)
        
        # Log Output Frame
        log_frame = ttk.LabelFrame(parent, text="Log Output", padding="10")
        log_frame.grid(row=5, column=0, sticky="nsew", padx=5, pady=5)
        self.log_text = tk.Text(log_frame, height=10, width=70, wrap="word")
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scroll.set)
    
    def create_batch_tab_widgets(self, parent):
        """Widgets for the Batch Conversion tab."""
        # Batch File Selection Frame
        batch_file_frame = ttk.LabelFrame(parent, text="Batch File Selection", padding="10")
        batch_file_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ttk.Button(batch_file_frame, text="Browse Batch Files", command=self.browse_batch_files).grid(row=0, column=0, padx=5, pady=3)
        self.batch_listbox = tk.Listbox(batch_file_frame, height=5, width=70)
        self.batch_listbox.grid(row=1, column=0, padx=5, pady=3, columnspan=2)
        
        # Batch Output Folder Selection Frame
        batch_output_frame = ttk.LabelFrame(parent, text="Output Folder", padding="10")
        batch_output_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.create_file_selection_row(batch_output_frame, "Output Folder:", self.batch_output_folder, self.browse_batch_output_folder, row=0)
        
        # Batch Conversion Options (shared with single conversion)
        batch_options_frame = ttk.LabelFrame(parent, text="Conversion Options", padding="10")
        batch_options_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(batch_options_frame, text="File Type:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        ttk.OptionMenu(batch_options_frame, self.file_type_var, self.file_type_var.get(), *self.file_type_options).grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(batch_options_frame, text="Input Type:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        ttk.OptionMenu(batch_options_frame, self.input_type_var, self.input_type_var.get(), *self.input_type_options).grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(batch_options_frame, text="Output Type:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        ttk.OptionMenu(batch_options_frame, self.output_type_var, self.output_type_var.get(), *self.output_type_options).grid(row=2, column=1, sticky="ew", padx=5, pady=3)
        ttk.Label(batch_options_frame, text="Conversion Game:").grid(row=3, column=0, sticky="w", padx=5, pady=3)
        ttk.OptionMenu(batch_options_frame, self.conversion_game_var, self.conversion_game_var.get(), *self.game_options).grid(row=3, column=1, sticky="ew", padx=5, pady=3)
        
        # Batch Advanced Options Frame (optional)
        batch_advanced_frame = ttk.LabelFrame(parent, text="Advanced Options", padding="10")
        batch_advanced_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(batch_advanced_frame, text="Move Position (X Y Z):").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        ttk.Entry(batch_advanced_frame, textvariable=self.move_position_var, width=40).grid(row=0, column=1, padx=5, pady=3)
        ttk.Label(batch_advanced_frame, text="Additional Args:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        ttk.Entry(batch_advanced_frame, textvariable=self.additional_args_var, width=40).grid(row=1, column=1, padx=5, pady=3)
        
        # Batch Progress Frame
        batch_progress_frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        batch_progress_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        self.batch_progress_var = tk.DoubleVar()
        self.batch_progress_bar = ttk.Progressbar(batch_progress_frame, variable=self.batch_progress_var, maximum=100)
        self.batch_progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=3)
        
        # Run Batch Conversion Button
        batch_run_button = ttk.Button(parent, text="Run Batch Conversion", command=self.run_batch_conversion_thread)
        batch_run_button.grid(row=5, column=0, pady=10)
    
    def create_file_selection_row(self, parent, label_text, text_variable, browse_command, row):
        """Helper to create file selection rows within a frame."""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=3)
        entry = ttk.Entry(parent, textvariable=text_variable, width=40)
        entry.grid(row=row, column=1, padx=5, pady=3)
        ttk.Button(parent, text="Browse...", command=browse_command).grid(row=row, column=2, padx=5, pady=3)
    
    def browse_input_file(self):
        """Browse for a single input file and auto-suggest an output file name."""
        file_path = filedialog.askopenfilename(title="Select Input File", filetypes=[("All Files", "*.*")])
        if file_path:
            self.input_file_var.set(file_path)
            input_path = Path(file_path)
            new_ext = ".ipl" if self.file_type_var.get() == "ipl" else ".ide"
            suggested_output = input_path.with_suffix(new_ext)
            self.output_file_var.set(str(suggested_output))
    
    def browse_output_file(self):
        """Browse for an output file for single conversion."""
        file_path = filedialog.asksaveasfilename(title="Select Output File", defaultextension=".ipl")
        if file_path:
            self.output_file_var.set(file_path)
    
    def browse_string_list_file(self):
        """Browse for a string list file (optional)."""
        file_path = filedialog.askopenfilename(
            title="Select String List File", 
            filetypes=[("Text files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.string_list_var.set(file_path)
    
    def browse_batch_files(self):
        """Browse for multiple input files for batch conversion."""
        file_paths = filedialog.askopenfilenames(title="Select Batch Input Files", filetypes=[("All Files", "*.*")])
        if file_paths:
            self.batch_files = list(file_paths)
            self.batch_listbox.delete(0, tk.END)
            for file in self.batch_files:
                self.batch_listbox.insert(tk.END, file)
    
    def browse_batch_output_folder(self):
        """Browse for an output folder for batch conversion."""
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.batch_output_folder.set(folder_path)
    
    def log(self, message):
        """Append messages to the log output text widget (called from the main thread)."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def poll_queue(self):
        """Periodically check the queue for messages from worker threads."""
        while not self.log_queue.empty():
            msg_type, content = self.log_queue.get_nowait()
            if msg_type == "log":
                self.log(content)
            elif msg_type == "progress":
                # Expecting a tuple: (progress_type, value)
                target, value = content
                if target == "single":
                    self.progress_var.set(value)
                elif target == "batch":
                    self.batch_progress_var.set(value)
        # Call this method again after 100ms
        self.after(100, self.poll_queue)
    
    def build_command(self):
        """Build the command list based on the current settings."""
        input_file = self.input_file_var.get().strip()
        output_file = self.output_file_var.get().strip()
        file_type = self.file_type_var.get().strip()
        input_type = self.input_type_var.get().strip()
        output_type = self.output_type_var.get().strip()
        conversion_game = self.conversion_game_var.get().strip()
        string_list = self.string_list_var.get().strip()
        move_position = self.move_position_var.get().strip()
        additional_args = self.additional_args_var.get().strip()
        
        if not input_file:
            raise ValueError("Please select an input file.")
        if not output_file:
            raise ValueError("Please select an output file.")
        
        command = [
            "fastman92_processor.exe",
            "/file_type", file_type,
            "/input_type", input_type,
            "/input_game", conversion_game,
            "/input_filename", input_file,
            "/output_type", output_type,
            "/output_game", conversion_game,
            "/output_filename", output_file
        ]
        
        if string_list:
            command.extend(["/string_list", string_list])
        
        if move_position:
            parts = move_position.split()
            if len(parts) != 3:
                raise ValueError("Move Position must contain three values (X Y Z).")
            command.extend(["/move_position"] + parts)
        
        if additional_args:
            command.extend(additional_args.split())
        
        return command
    
    def run_conversion_thread(self):
        """Run single conversion in a separate thread."""
        threading.Thread(target=self.run_conversion, daemon=True).start()
    
    def run_conversion(self):
        """Execute single file conversion and update the UI via the queue."""
        try:
            command = self.build_command()
        except ValueError as ve:
            self.log_queue.put(("log", f"Error: {ve}"))
            self.parent.after(0, messagebox.showerror, "Error", str(ve))
            return
        
        self.log_queue.put(("log", "Running command:"))
        self.log_queue.put(("log", " ".join(command)))
        self.log_queue.put(("progress", ("single", 0)))
        
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # Instead of a busy-wait loop, read output in chunks and update progress intermittently.
            while True:
                retcode = process.poll()
                # Increase progress incrementally (simulate progress) 
                # This value could be updated based on known milestones if available.
                current = self.progress_var.get()
                self.log_queue.put(("progress", ("single", min(100, current + 5))))
                if retcode is not None:
                    break
                threading.Event().wait(0.2)
                
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                self.log_queue.put(("progress", ("single", 100)))
                self.log_queue.put(("log", "Process output:\n" + stdout))
                self.parent.after(0, messagebox.showinfo, "Success", f"Conversion complete!\nOutput file: {self.output_file_var.get()}")
            else:
                error_msg = f"An error occurred:\n{stderr}"
                self.log_queue.put(("log", error_msg))
                self.parent.after(0, messagebox.showerror, "Conversion Error", error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.log_queue.put(("log", error_msg))
            self.parent.after(0, messagebox.showerror, "Conversion Error", error_msg)
    
    def run_batch_conversion_thread(self):
        """Run batch conversion in a separate thread."""
        threading.Thread(target=self.run_batch_conversion, daemon=True).start()
    
    def run_batch_conversion(self):
        """Process each file in the batch list sequentially."""
        if not self.batch_files:
            self.parent.after(0, messagebox.showerror, "Error", "Please select batch files.")
            return
        
        output_folder = self.batch_output_folder.get().strip()
        if not output_folder:
            self.parent.after(0, messagebox.showerror, "Error", "Please select an output folder for batch conversion.")
            return
        
        total_files = len(self.batch_files)
        for idx, input_file in enumerate(self.batch_files, start=1):
            input_path = Path(input_file)
            # Generate output file with '_converted' suffix.
            output_file = str(Path(output_folder) / (input_path.stem + "_converted" + input_path.suffix))
            # Update the UI fields for each conversion (if desired)
            self.input_file_var.set(input_file)
            self.output_file_var.set(output_file)
            
            try:
                command = self.build_command()
            except ValueError as ve:
                self.log_queue.put(("log", f"Skipping file {input_file}: {ve}"))
                continue
            
            self.log_queue.put(("log", f"Running conversion for: {input_file}"))
            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                while True:
                    retcode = process.poll()
                    current = self.batch_progress_var.get()
                    self.log_queue.put(("progress", ("batch", min(100, current + 5))))
                    if retcode is not None:
                        break
                    threading.Event().wait(0.2)
                    
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    self.log_queue.put(("progress", ("batch", 100)))
                    self.log_queue.put(("log", f"Conversion successful for {input_file}.\nOutput:\n{stdout}"))
                else:
                    error_msg = f"Conversion error for {input_file}:\n{stderr}"
                    self.log_queue.put(("log", error_msg))
            except Exception as e:
                self.log_queue.put(("log", f"Unexpected error for {input_file}: {e}"))
            
            # Update overall batch progress
            overall_progress = (idx / total_files) * 100
            self.log_queue.put(("progress", ("batch", overall_progress)))
        
        self.parent.after(0, messagebox.showinfo, "Batch Conversion", "Batch conversion complete!")

def main():
    root = tk.Tk()
    ConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
