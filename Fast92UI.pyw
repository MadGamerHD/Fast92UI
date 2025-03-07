import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

class ConverterApp(ttk.Frame):
    """Modernized GUI application for Fastman92 Processor with improved usability."""
    
    def __init__(self, parent):
        super().__init__(parent, padding="10 10 10 10")
        self.parent = parent
        self.parent.title("Fastman92 Processor GUI")
        self.parent.resizable(False, False)
        self.init_vars()
        self.create_widgets()
        self.grid(sticky="nsew")
        
    def init_vars(self):
        """Initialize tkinter variables and option lists."""
        self.input_file_var = tk.StringVar()
        self.output_file_var = tk.StringVar()
        self.string_list_var = tk.StringVar()
        self.move_position_var = tk.StringVar()
        self.additional_args_var = tk.StringVar()
        
        self.file_type_var = tk.StringVar(value="ipl")
        self.input_type_var = tk.StringVar(value="binary")
        self.output_type_var = tk.StringVar(value="text")
        # Consolidated conversation game option (applies to both input and output)
        self.conversation_game_var = tk.StringVar(value="GAME_EXACT_GTAIV_PC")
        
        self.file_type_options = ["ipl", "ide"]
        self.input_type_options = ["binary", "text"]
        self.output_type_options = ["binary", "text"]
        self.game_options = [
            "GAME_EXACT_GTAIV_PC",
            "GAME_EXACT_BULLY_SCHOLARSHIP_EDITION_PC",
            "GAME_EXACT_GTASA_PC",
            "GAME_EXACT_GTAVC_PC"
        ]
        
    def create_widgets(self):
        """Construct and place widgets in organized frames."""
        # Frames for organization.
        file_frame = ttk.LabelFrame(self, text="File Selection", padding="10")
        file_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        options_frame = ttk.LabelFrame(self, text="Conversion Options", padding="10")
        options_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        advanced_frame = ttk.LabelFrame(self, text="Advanced Options", padding="10")
        advanced_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        progress_frame = ttk.LabelFrame(self, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        
        log_frame = ttk.LabelFrame(self, text="Log Output", padding="10")
        log_frame.grid(row=4, column=0, sticky="nsew", padx=5, pady=5)
        
        # File Selection Frame
        self.create_file_selection_row(file_frame, "Input File:", self.input_file_var, self.browse_input_file, row=0)
        self.create_file_selection_row(file_frame, "Output File:", self.output_file_var, self.browse_output_file, row=1)
        self.create_file_selection_row(file_frame, "String List File (optional):", self.string_list_var, self.browse_string_list_file, row=2)
        
        # Conversion Options Frame
        ttk.Label(options_frame, text="File Type:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        ttk.OptionMenu(options_frame, self.file_type_var, self.file_type_var.get(), *self.file_type_options).grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        
        ttk.Label(options_frame, text="Input Type:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        ttk.OptionMenu(options_frame, self.input_type_var, self.input_type_var.get(), *self.input_type_options).grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        
        ttk.Label(options_frame, text="Output Type:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        ttk.OptionMenu(options_frame, self.output_type_var, self.output_type_var.get(), *self.output_type_options).grid(row=2, column=1, sticky="ew", padx=5, pady=3)
        
        # Consolidated game selection for conversation.
        ttk.Label(options_frame, text="Conversation Game:").grid(row=3, column=0, sticky="w", padx=5, pady=3)
        ttk.OptionMenu(options_frame, self.conversation_game_var, self.conversation_game_var.get(), *self.game_options).grid(row=3, column=1, sticky="ew", padx=5, pady=3)
        
        # Advanced Options Frame
        ttk.Label(advanced_frame, text="Move Position (X Y Z):").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        ttk.Entry(advanced_frame, textvariable=self.move_position_var, width=40).grid(row=0, column=1, padx=5, pady=3)
        
        ttk.Label(advanced_frame, text="Additional Args:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        ttk.Entry(advanced_frame, textvariable=self.additional_args_var, width=40).grid(row=1, column=1, padx=5, pady=3)
        
        # Progress Frame - adds a progress bar for visual feedback.
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=3)
        
        # Run Conversion Button
        run_button = ttk.Button(self, text="Run Conversion", command=self.run_conversion_thread)
        run_button.grid(row=5, column=0, pady=10)
        
        # Log Output Frame
        self.log_text = tk.Text(log_frame, height=10, width=70, wrap="word")
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scroll.set)
        
    def create_file_selection_row(self, parent, label_text, text_variable, browse_command, row):
        """Helper to create file selection rows within a frame."""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=3)
        entry = ttk.Entry(parent, textvariable=text_variable, width=40)
        entry.grid(row=row, column=1, padx=5, pady=3)
        ttk.Button(parent, text="Browse...", command=browse_command).grid(row=row, column=2, padx=5, pady=3)
        
    def browse_input_file(self):
        """Browse for an input file and auto-suggest an output file name."""
        file_path = filedialog.askopenfilename(title="Select Input File", filetypes=[("All Files", "*.*")])
        if file_path:
            self.input_file_var.set(file_path)
            input_path = Path(file_path)
            new_ext = ".ipl" if self.file_type_var.get() == "ipl" else ".ide"
            suggested_output = input_path.with_suffix(new_ext)
            self.output_file_var.set(str(suggested_output))
        
    def browse_output_file(self):
        """Browse for an output file to save."""
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
        
    def log(self, message):
        """Append messages to the log output text widget."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        
    def build_command(self):
        """Build the command list based on the user input."""
        input_file = self.input_file_var.get().strip()
        output_file = self.output_file_var.get().strip()
        file_type = self.file_type_var.get().strip()
        input_type = self.input_type_var.get().strip()
        output_type = self.output_type_var.get().strip()
        # Use the consolidated conversation game value for both input and output game.
        conversation_game = self.conversation_game_var.get().strip()
        string_list = self.string_list_var.get().strip()
        move_position = self.move_position_var.get().strip()
        additional_args = self.additional_args_var.get().strip()
        
        # Validate required fields.
        if not input_file:
            raise ValueError("Please select an input file.")
        if not output_file:
            raise ValueError("Please select an output file.")
        
        command = [
            "fastman92_processor.exe",
            "/file_type", file_type,
            "/input_type", input_type,
            "/input_game", conversation_game,
            "/input_filename", input_file,
            "/output_type", output_type,
            "/output_game", conversation_game,
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
        """Start the conversion in a separate thread to keep the GUI responsive."""
        thread = threading.Thread(target=self.run_conversion, daemon=True)
        thread.start()
        
    def run_conversion(self):
        """Validate inputs, build the command, execute conversion, update progress, and log output."""
        try:
            command = self.build_command()
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return
        
        self.log("Running command:")
        self.log(" ".join(command))
        
        # Reset progress bar
        self.progress_var.set(0)
        
        try:
            # For demonstration, we simulate progress. In a real-world scenario,
            # you might hook into the subprocess output or use a more granular progress indicator.
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            while True:
                # Poll process status and update progress bar
                retcode = process.poll()
                if retcode is not None:
                    break
                # Increment progress for visual feedback (simulate progress)
                current_progress = self.progress_var.get()
                self.progress_var.set(min(100, current_progress + 5))
                self.parent.update_idletasks()
                threading.Event().wait(0.2)  # pause briefly
                
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                self.progress_var.set(100)
                self.log("Process output:\n" + stdout)
                messagebox.showinfo("Success", f"Conversion complete!\nOutput file: {self.output_file_var.get()}")
            else:
                error_msg = f"An error occurred:\n{stderr}"
                self.log(error_msg)
                messagebox.showerror("Conversion Error", error_msg)
        except subprocess.CalledProcessError as e:
            error_msg = f"An error occurred:\n{e.stderr}"
            self.log(error_msg)
            messagebox.showerror("Conversion Error", error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.log(error_msg)
            messagebox.showerror("Conversion Error", error_msg)

def main():
    root = tk.Tk()
    ConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
