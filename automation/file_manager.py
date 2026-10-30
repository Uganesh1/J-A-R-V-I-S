import os


class FileManager:
    def open_folder(self, name):
        base = os.path.expanduser("~")
        mapping = {
            "downloads": os.path.join(base, "Downloads"),
            "documents": os.path.join(base, "Documents"),
            "desktop": os.path.join(base, "Desktop"),
            "pictures": os.path.join(base, "Pictures"),
            "videos": os.path.join(base, "Videos"),
            "music": os.path.join(base, "Music"),
        }
        path = mapping.get(name.lower())
        if not path:
            return f"Unknown folder: {name}"
        if not os.path.isdir(path):
            return f"Folder does not exist: {path}"
        try:
            os.startfile(path)
            return f"Opening {name} folder."
        except Exception as e:
            return f"Could not open folder: {e}"

    def create_folder(self, name):
        base = os.path.join(os.path.expanduser("~"), "Documents")
        path = os.path.join(base, name)
        try:
            os.makedirs(path, exist_ok=True)
            return f"Folder created: {path}"
        except Exception as e:
            return f"Could not create folder: {e}"