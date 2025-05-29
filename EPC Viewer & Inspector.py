import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class EPCViewerApp:
    def __init__(self, master):
        master.title(".epc Viewer & Inspector")
        master.geometry("800x600")

        # File selection
        top = tk.Frame(master)
        top.pack(fill='x', padx=5, pady=5)
        tk.Button(top, text="Open .epc File", command=self.load_file).pack(side='left')
        self.file_label = tk.Label(top, text="No file loaded")
        self.file_label.pack(side='left', padx=10)
        tk.Button(top, text="Extract Selected Record", command=self.extract_record).pack(side='right')

        # Paned layout: left list, right with tabs
        paned = ttk.PanedWindow(master, orient='horizontal')
        paned.pack(fill='both', expand=True)

        # Left: strings list
        left_frame = ttk.Frame(paned)
        self.listbox = tk.Listbox(left_frame)
        self.listbox.pack(fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        paned.add(left_frame, weight=1)

        # Right: notebook for details
        right_frame = ttk.Frame(paned)
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill='both', expand=True)
        # Tab1: String Details
        self.detail_text = tk.Text(self.notebook, wrap='none')
        self.notebook.add(self.detail_text, text='String Detail')
        # Tab2: Reference Records
        self.ref_list = tk.Listbox(self.notebook)
        self.ref_list.bind('<<ListboxSelect>>', self.on_ref_select)
        self.notebook.add(self.ref_list, text='Index Records')
        # Tab3: Record Detail
        self.record_text = tk.Text(self.notebook, wrap='none')
        self.notebook.add(self.record_text, text='Record Detail')

        paned.add(right_frame, weight=3)

        self.filepath = None
        self.data = b''
        self.strings = []
        self.current_string = None
        self.records = []
        self.current_record_offset = None

    def load_file(self):
        fp = filedialog.askopenfilename(title='Select .epc file', filetypes=[('EPC','*.epc')])
        if not fp:
            return
        self.filepath = fp
        self.file_label.config(text=os.path.basename(fp))
        with open(fp, 'rb') as f:
            self.data = f.read()
        self.scan_strings()
        self.notebook.select(0)

    def scan_strings(self):
        self.listbox.delete(0, tk.END)
        self.strings.clear()
        buf = []
        start = None
        for i, b in enumerate(self.data + b'\x00'):
            if 32 <= b < 127:
                if start is None: start = i
                buf.append(chr(b))
            else:
                if start is not None and len(buf) >= 4:
                    s = ''.join(buf)
                    if any(c in s for c in './\\_') or s.isalnum():
                        self.strings.append((start, s))
                buf, start = [], None
        for off, s in self.strings:
            self.listbox.insert(tk.END, f"0x{off:08X}: {s}")

    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        idx = sel[0]
        offset, s = self.strings[idx]
        self.current_string = (offset, s)
        # show details
        self.detail_text.delete('1.0', tk.END)
        info = [f"String: {s}", f"Offset: 0x{offset:08X}", '']
        # hex around
        start = max(offset-32, 0)
        chunk = self.data[start:offset+32]
        for i in range(0, len(chunk), 16):
            row = chunk[i:i+16]
            hex_str = ' '.join(f"{b:02X}" for b in row)
            info.append(f"{start+i:08X}: {hex_str}")
        self.detail_text.insert(tk.END, '\n'.join(info))
        # find index record references
        self.find_records(offset)
        self.notebook.select(1)

    def find_records(self, name_offset):
        self.ref_list.delete(0, tk.END)
        self.records.clear()
        pat = struct.pack('<I', name_offset)
        idx = 0
        data = self.data
        while True:
            idx = data.find(pat, idx)
            if idx < 0: break
            if idx+12 < len(data):
                self.records.append(idx)
                self.ref_list.insert(tk.END, f"Record @ 0x{idx:08X}")
            idx += 4

    def on_ref_select(self, event):
        sel = self.ref_list.curselection()
        if not sel: return
        idx = sel[0]
        rec_off = self.records[idx]
        self.current_record_offset = rec_off
        # parse record: name_off, data_off
        name_off = struct.unpack_from('<I', self.data, rec_off)[0]
        data_off = struct.unpack_from('<I', self.data, rec_off+8)[0]
        # display
        self.record_text.delete('1.0', tk.END)
        info = [f"Record Offset: 0x{rec_off:08X}", f"Name Offset: 0x{name_off:08X}", f"Data Offset: 0x{data_off:08X}", '']
        seq = self.data[rec_off:rec_off+16]
        hex_str = ' '.join(f"{b:02X}" for b in seq)
        info.append(f"Raw Record (16b): {hex_str}")
        self.record_text.insert(tk.END, '\n'.join(info))
        self.notebook.select(2)

    def extract_record(self):
        if self.current_record_offset is None:
            messagebox.showwarning("Export", "Select a record first.")
            return
        rec = self.current_record_offset
        try:
            name_off = struct.unpack_from('<I', self.data, rec)[0]
            data_off = struct.unpack_from('<I', self.data, rec+8)[0]
        except Exception:
            messagebox.showerror("Error", "Failed to read record data.")
            return
        # find name string
        end = self.data.find(b'\x00', name_off)
        name = self.data[name_off:end].decode('ascii', errors='ignore')
        # guess size: next record or EOF
        idx = self.records.index(rec)
        if idx+1 < len(self.records):
            next_rec = self.records[idx+1]
            next_data_off = struct.unpack_from('<I', self.data, next_rec+8)[0]
            size = next_data_off - data_off
        else:
            size = len(self.data) - data_off
        if size <= 0:
            messagebox.showerror("Error", "Invalid blob size.")
            return
        blob = self.data[data_off:data_off+size]
        # write
        out_dir = self.filepath + '_export'
        os.makedirs(out_dir, exist_ok=True)
        name = os.path.basename(name) or f'record_{rec:08X}'
        out_path = os.path.join(out_dir, name)
        with open(out_path, 'wb') as f:
            f.write(blob)
        messagebox.showinfo("Saved", f"Saved to:\n{out_path}")

if __name__ == '__main__':
    root = tk.Tk()
    app = EPCViewerApp(root)
    root.mainloop()