class PermissionManager:
    """Every destructive action must pass through here."""

    RESTRICTED = {
        "delete_file", "delete_folder", "install_software",
        "run_script", "modify_system_settings", "send_external"
    }

    def __init__(self):
        self._granted = set()

    def require(self, action: str, details: str = ""):
        if action not in self.RESTRICTED:
            return True
        # In a full UI this would pop a confirmation dialog.
        # For safety, default DENY unless explicitly granted at runtime.
        if action in self._granted:
            return True
        print(f"[PERMISSION DENIED] {action}: {details}")
        return False

    def grant(self, action: str):
        if action in self.RESTRICTED:
            self._granted.add(action)