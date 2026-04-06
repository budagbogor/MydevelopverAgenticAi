import uiautomation as auto
import time
import os

def dump_trae_tree():
    # Cari jendela Trae
    trae_win = auto.WindowControl(searchDepth=1, Name='Trae')
    if not trae_win.Exists(0):
        # Fuzzy search jika judul berubah (misal: "Project - Trae")
        all_wins = auto.GetRootControl().GetChildren()
        for win in all_wins:
            if 'Trae' in win.Name:
                trae_win = win
                break
    
    if trae_win.Exists(0):
        print(f"Found Trae: {trae_win.Name}")
        trae_win.SetActive()
        # Dump to file
        with open("trae_ui_tree.txt", "w", encoding="utf-8") as f:
            def log_element(control, depth=0):
                try:
                    indent = "  " * depth
                    info = f"{indent}[{control.ControlTypeName}] Name: '{control.Name}', AutomationId: '{control.AutomationId}'\n"
                    f.write(info)
                    for child in control.GetChildren():
                        log_element(child, depth + 1)
                except:
                    pass
            log_element(trae_win)
        print("UI Tree dumped to trae_ui_tree.txt")
    else:
        print("Trae window not found.")

if __name__ == "__main__":
    dump_trae_tree()
