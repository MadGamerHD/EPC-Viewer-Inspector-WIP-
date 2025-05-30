import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import io
from PIL import Image, ImageTk

TEXTURE_EXTS = ('.dds', '.tga', '.png', '.jpg', '.bmp')

class EPCTextureExporter:
    def __init__(self, master):
        master.title(".epc Texture Exporter")
        master.geometry("800x600")

        # Toolbar
        toolbar = tk.Frame(master)
        toolbar.pack(fill='x', padx=5, pady=5)
        tk.Button(toolbar, text="Open .epc File", command=self.load_file).pack(side='left')
        tk.Button(toolbar, text="Analyze File", command=self.analyze_file).pack(side='left', padx=5)
        tk.Button(toolbar, text="Preview Selected Texture", command=self.preview_selected).pack(side='left', padx=5)
        tk.Button(toolbar, text="Export All Textures", command=self.batch_export).pack(side='right')
        self.file_label = tk.Label(toolbar, text="No file loaded")
        self.file_label.pack(side='left', padx=10)

        # Main layout
        paned = ttk.PanedWindow(master, orient='horizontal')
        paned.pack(fill='both', expand=True)

        # Left: texture list
        left = ttk.Frame(paned)
        self.texture_list = tk.Listbox(left)
        self.texture_list.pack(fill='both', expand=True)
        paned.add(left, weight=1)

        # Right: info pane
        right = ttk.Frame(paned)
        self.info_text = tk.Text(right, wrap='none', state='disabled')
        self.info_text.pack(fill='both', expand=True)
        paned.add(right, weight=2)

        self.data = b''
        self.filepath = None
        self.textures = []  # list of (name_offset, name)

    def load_file(self):
        fp = filedialog.askopenfilename(title='Select .epc file', filetypes=[('EPC','*.epc')])
        if not fp:
            return
        self.filepath = fp
        self.file_label.config(text=os.path.basename(fp))
        with open(fp, 'rb') as f:
            self.data = f.read()
        self.scan_textures()

    def scan_textures(self):
        """Find embedded texture names and offsets."""
        self.texture_list.delete(0, tk.END)
        self.textures.clear()
        buf, start = [], None
        for i, b in enumerate(self.data + b'\x00'):
            if 32 <= b < 127:
                if start is None:
                    start = i
                buf.append(chr(b))
            else:
                if start is not None:
                    s = ''.join(buf)
                    ext = os.path.splitext(s)[1].lower()
                    if ext in TEXTURE_EXTS:
                        self.textures.append((start, s))
                        self.texture_list.insert(tk.END, f"0x{start:08X}: {s}")
                    buf, start = [], None
        if not self.textures:
            messagebox.showinfo("Scan Complete", "No texture references found.")

    def get_texture_blob(self, name_off, name):
        """Extract raw blob immediately after the name string until the next texture name."""
        bs = name.encode('ascii', errors='ignore') + b'\x00'
        occs = []
        pos = 0
        while True:
            pos = self.data.find(bs, pos)
            if pos < 0:
                break
            occs.append(pos)
            pos += 1
        occs = sorted(occs)
        if not occs:
            return None
        # use the first occurrence
        start = occs[0] + len(bs)
        # find next texture name occurrence offset that is > start
        next_offsets = [off for off, _ in self.textures if off > start]
        end = min(next_offsets) if next_offsets else len(self.data)
        if end <= start:
            return None
        return self.data[start:end]

    def analyze_file(self):
        """Dump basic texture names and offsets to a .txt next to the .epc."""
        if not self.filepath or not self.data:
            messagebox.showwarning("Analyze", "Load a file first.")
            return
        txt_path = self.filepath + '_scan.txt'
        try:
            with open(txt_path, 'w') as out:
                out.write(f"EPC Scan Report for {os.path.basename(self.filepath)}\n")
                out.write(f"Total textures found: {len(self.textures)}\n\n")
                for idx, (off, name) in enumerate(self.textures, 1):
                    out.write(f"{idx}. {name} @ 0x{off:08X}\n")
            messagebox.showinfo("Analyze Complete", f"Scan data written to:\n{txt_path}")
        except Exception as e:
            messagebox.showerror("Analyze Error", f"Failed to write scan file: {e}")

    def preview_selected(self):
        sel = self.texture_list.curselection()
        if not sel:
            messagebox.showwarning("Preview", "Select a texture first.")
            return
        off, name = self.textures[sel[0]]
        blob = self.get_texture_blob(off, name)
        if not blob:
            messagebox.showerror("Preview", "Could not extract texture data.")
            return
        try:
            img = Image.open(io.BytesIO(blob))
        except Exception as e:
            messagebox.showerror("Preview", f"Failed to load image: {e}")
            return
        win = tk.Toplevel()
        win.title(f"Preview: {os.path.basename(name)}")
        w, h = img.size
        max_w, max_h = 600, 600
        if w > max_w or h > max_h:
            ratio = min(max_w/w, max_h/h)
            img = img.resize((int(w*ratio), int(h*ratio)), Image.ANTIALIAS)
        tk_img = ImageTk.PhotoImage(img)
        lbl = tk.Label(win, image=tk_img)
        lbl.image = tk_img
        lbl.pack()

    def batch_export(self):
        if not self.textures or not self.filepath:
            messagebox.showwarning("Export", "Load a file and ensure textures found first.")
            return
        out_dir = self.filepath + '_textures'
        os.makedirs(out_dir, exist_ok=True)
        count = 0
        for off, name in self.textures:
            ext = os.path.splitext(name)[1].lower()
            if ext not in TEXTURE_EXTS:
                continue
            blob = self.get_texture_blob(off, name)
            if not blob:
                continue
            fname = os.path.splitext(os.path.basename(name))[0] + ext
            path = os.path.join(out_dir, fname)
            try:
                with open(path, 'wb') as f:
                    f.write(blob)
                count += 1
            except Exception as e:
                print(f"Failed to write {path}: {e}")
        messagebox.showinfo("Export Complete", f"Exported {count} files to:\n{out_dir}")

if __name__ == '__main__':
    root = tk.Tk()
    app = EPCTextureExporter(root)
    root.mainloop()
