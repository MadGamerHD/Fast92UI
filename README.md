**FAST92 GUI** is a desktop application designed to provide a user-friendly graphical interface for the Fastman92 Processor. It streamlines the process of converting files by wrapping a command-line tool into an intuitive, multi-tabbed GUI built with Python’s `tkinter` framework. Below is an in-depth description of its functionality and key features:

---

### Overview

The tool is intended for processing game-related files, offering both single file conversions and batch conversion capabilities. Whether you’re working on one file or a whole directory, FAST92 GUI simplifies the task through its clean design, real-time progress updates, and detailed logging.

---

### Key Features

1. **Tabbed Interface**  
   The application organizes its functionalities into two primary tabs:
   - **Single Conversion:**  
     - Allows users to select an input file, automatically suggests an appropriate output file based on the selected file type, and applies conversion settings.
     - Provides options to include a string list file and advanced conversion parameters.
   
   - **Batch Conversion:**  
     - Users can select multiple files at once and specify an output folder.
     - Applies conversion settings uniformly across all files in the batch.
     - Displays a consolidated progress bar and log for all conversions.

2. **Dynamic Command Building**  
   - Based on user inputs, the application constructs a command-line argument list tailored for the Fastman92 Processor.
   - It includes parameters for file type, input/output types, game mode options, and advanced settings such as move position and additional arguments.
   - This dynamic construction ensures flexibility and adaptability for different file conversion requirements.

3. **Progress Monitoring and Logging**  
   - Integrated progress bars (separate for single and batch operations) provide visual feedback on conversion progress. Progress increments are simulated in stages, offering a sense of progress even when the exact status isn’t available from the underlying process.
   - A log output window captures all messages, including executed command lines, process output, and error messages. This logging is implemented via a thread-safe queue to ensure smooth updates without interfering with the GUI responsiveness.

4. **Multithreading Support**  
   - To keep the interface responsive during potentially long-running conversion processes, each conversion (or batch of conversions) runs in a separate thread.
   - Threading is combined with a message queue system to safely relay progress updates and log messages from background threads back to the main GUI thread.

5. **File and Folder Selection**  
   - Users can easily browse for input files, output files, and optional string list files using standard file dialogs.
   - Batch conversion features include selection of multiple files and an output folder where all processed files will be saved.

6. **Advanced Options**  
   - The GUI provides fields for entering advanced parameters such as:
     - **Move Position (X Y Z):** Specify spatial coordinates if the conversion process requires position data.
     - **Additional Arguments:** Append any extra command-line parameters that the user might need for specialized processing scenarios.

---

### How It Works

1. **User Input and Validation:**  
   - The user selects files and sets conversion options through the interface.
   - The application validates the inputs (e.g., ensuring that a valid input and output file are specified and that optional move position values consist of three numbers).

2. **Command Construction:**  
   - With validated inputs, the tool builds a command list that mirrors the configuration settings.
   - This command is tailored for the Fastman92 Processor, specifying details like file types and game-specific parameters.

3. **Execution in a Separate Thread:**  
   - The tool spawns a background thread to execute the constructed command with Python's `subprocess.Popen`.
   - During execution, the thread continuously polls for progress and relays real-time updates and log messages back to the user interface.

4. **Handling Errors and Completion:**  
   - The tool monitors for errors during the conversion process. In case of any issues (like incorrect move position format or process errors), error messages are displayed immediately.
   - Upon successful conversion, a confirmation is shown along with the generated output file path.

---

**FAST92 GUI** thus combines user interface simplicity with robust processing capabilities, making it a practical solution for users who need to manage file conversions for game assets or similar file types without diving into command-line syntax.
