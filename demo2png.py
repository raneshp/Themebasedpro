import tkinter as tk
from tkinter import ttk
import os

def create_drive_selector():
    """Create a GUI for selecting drives and file types."""
    converted_drive = ""  # Define converted_drive variable here

    def get_hard_drives():
        """Get a list of all hard drives on the system."""
        drives = []
        for drive in range(65, 91):  # ASCII codes for drive letters (A-Z)
            drive = chr(drive) + ":\\"
            if os.path.exists(drive):
                drives.append(drive)
        return drives

    def on_drive_selected(event):
        """Function to handle drive selection."""
        nonlocal converted_drive  # Use nonlocal keyword to modify outer scope variable
        selected_drive = drive_combo.get()
        converted_drive = "\\\\.\\{}:".format(selected_drive[0])  # Assign value to converted_drive
        print("Selected Drive:", converted_drive)

    def recover_files():
        """Recover files from the specified drive."""
        if not converted_drive:
            print("Please select a drive first.")
            return
        size = 512              # Size of bytes to read
        offs = 0                # Offset location
        drec = False            # Recovery mode
        rcvd = 0                # Recovered file ID
        file_types_mapping = {'JPEG': 'jpg', 'PNG': 'png', 'PDF': 'pdf', 'GIF': 'gif'}
        selected_file_types = [file_type for file_type, var in zip(file_types, file_type_vars) if var.get()]
        with open(converted_drive, "rb") as fileD:
            byte = fileD.read(size) # Read 'size' bytes
            while byte:
                for file_type in selected_file_types:
                    extension = file_types_mapping[file_type]
                    if extension == 'jpg':
                        found = byte.find(b'\xff\xd8\xff\xe0\x00\x10\x4a\x46')
                        end_sig = b'\xff\xd9'
                    elif extension == 'png':
                        found = byte.find(b'\x89PNG\r\n\x1a\n')
                        end_sig = b'\x49\x45\x4E\x44\xAE\x42\x60\x82'
                    elif extension == 'pdf':
                        found = byte.find(b'\x25\x50\x44\x46')
                        end_sig = b'%EOF'
                    elif extension == 'gif':
                        found = byte.find(b'\x47\x49\x46\x38\x37\x61')
                        end_sig = b'\x00\x3B'
                    
                    if found >= 0:
                        drec = True
                        print(f'==== Found {file_type} at location: ' + str(hex(found+(size*offs))) + ' ====')
                        folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_type)
                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)
                            print(f"Folder created: {folder_path}")
                        # Now let's create recovered file and search for ending signature
                        with open(os.path.join(folder_path, f"{rcvd}.{extension}"), "wb") as fileN:
                            fileN.write(byte[found:])
                            while drec:
                                byte = fileD.read(size)
                                end_pos = byte.find(end_sig)
                                if end_pos >= 0:
                                    fileN.write(byte[:end_pos + len(end_sig)])
                                    fileD.seek((offs + 1) * size)
                                    print(f'==== Wrote {file_type} to location: {rcvd}.{extension} ====\n')
                                    drec = False
                                    rcvd += 1
                                else:
                                    fileN.write(byte)
                    byte = fileD.read(size)
                    offs += 1

    def create_folders():
        """Create folders for selected file types."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        selected_file_types = [var.get() for var in file_type_vars]
        for file_type, var in zip(file_types, selected_file_types):
            if var:
                folder_path = os.path.join(script_dir, file_type)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    print(f"Folder created: {folder_path}")

    # Create the main window
    root = tk.Tk()
    root.title("Drive Selector")

    # Get list of hard drives
    hard_drives = get_hard_drives()

    # Create a dropdown list of hard drives
    drive_label = ttk.Label(root, text="Select Drive:")
    drive_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    drive_combo = ttk.Combobox(root, values=hard_drives, width=50)
    drive_combo.grid(row=0, column=1, padx=10, pady=10)
    drive_combo.bind("<<ComboboxSelected>>", on_drive_selected)

    # File types checkboxes
    file_types = ['JPEG', 'PNG', 'PDF', 'GIF']
    file_type_vars = [tk.IntVar() for _ in range(len(file_types))]

    file_frame = ttk.LabelFrame(root, text="Select File Types:")
    file_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    for i, file_type in enumerate(file_types):
        chk = ttk.Checkbutton(file_frame, text=file_type, variable=file_type_vars[i])
        chk.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="w")

    # Button to recover files and create folders
    recover_button = ttk.Button(root, text="Recover Files", command=recover_files)
    recover_button.grid(row=2, column=0, padx=10, pady=10)

    create_button = ttk.Button(root, text="Create Folders", command=create_folders)
    create_button.grid(row=2, column=1, padx=10, pady=10)

    root.mainloop()

# Example usage:
if __name__ == "__main__":
    create_drive_selector()
