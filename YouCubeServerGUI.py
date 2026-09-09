import os, sys, socket, subprocess, threading, queue, shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

BASE = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
SERVER = BASE / "server-src"
TOOLS = BASE / "tools"

def find_exe(name):
    local = TOOLS / (name + ".exe")
    if local.exists():
        return str(local)
    return shutil.which(name) or ""

def lan_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(("8.8.8.8",80))
        ip=s.getsockname()[0]; s.close(); return ip
    except: return "127.0.0.1"

class App:
    def __init__(self, root):
        self.root=root; self.proc=None; self.q=queue.Queue()
        root.title("YouCube Backend Server"); root.geometry("760x540")
        self.host=tk.StringVar(value="0.0.0.0")
        self.port=tk.StringVar(value="5000")
        self.ffmpeg=tk.StringVar(value=find_exe("ffmpeg"))
        self.sanjuuni=tk.StringVar(value=find_exe("sanjuuni"))
        self.status=tk.StringVar(value="Stopped")
        self.ip=tk.StringVar(value=lan_ip())
        self.cache_size=tk.StringVar(value="0 B")
        self.ui()
        self.refresh_cache_size()
        root.after(100,self.pump)
        root.after(3000,self.cache_tick)
        root.protocol("WM_DELETE_WINDOW",self.close)

    def ui(self):
        f=ttk.Frame(self.root,padding=10); f.pack(fill="x")
        ttk.Label(f,text="YouCube Backend Server",font=("Segoe UI",16,"bold")).grid(row=0,column=0,columnspan=4,sticky="w")
        ttk.Label(f,text="LAN IP").grid(row=1,column=0,sticky="w",pady=(10,0))
        ttk.Label(f,textvariable=self.ip).grid(row=1,column=1,sticky="w",pady=(10,0))
        ttk.Label(f,text="Status").grid(row=1,column=2,sticky="w",pady=(10,0))
        ttk.Label(f,textvariable=self.status).grid(row=1,column=3,sticky="w",pady=(10,0))
        ttk.Label(f,text="Host").grid(row=2,column=0,sticky="w",pady=(8,0))
        ttk.Entry(f,textvariable=self.host,width=18).grid(row=2,column=1,sticky="w",pady=(8,0))
        ttk.Label(f,text="Port").grid(row=2,column=2,sticky="w",pady=(8,0))
        ttk.Entry(f,textvariable=self.port,width=10).grid(row=2,column=3,sticky="w",pady=(8,0))

        d=ttk.LabelFrame(self.root,text="Dependencies",padding=10); d.pack(fill="x",padx=10,pady=6)
        d.columnconfigure(1,weight=1)
        ttk.Label(d,text="FFmpeg").grid(row=0,column=0,sticky="w")
        ttk.Entry(d,textvariable=self.ffmpeg).grid(row=0,column=1,sticky="ew",padx=6)
        ttk.Button(d,text="Browse",command=lambda:self.browse(self.ffmpeg)).grid(row=0,column=2)
        ttk.Label(d,text="Sanjuuni").grid(row=1,column=0,sticky="w",pady=(8,0))
        ttk.Entry(d,textvariable=self.sanjuuni).grid(row=1,column=1,sticky="ew",padx=6,pady=(8,0))
        ttk.Button(d,text="Browse",command=lambda:self.browse(self.sanjuuni)).grid(row=1,column=2,pady=(8,0))

        cache=ttk.LabelFrame(self.root,text="Media Cache",padding=10)
        cache.pack(fill="x",padx=10,pady=(0,6))
        ttk.Label(cache,text="Cache Size").pack(side="left")
        ttk.Label(cache,textvariable=self.cache_size).pack(side="left",padx=(8,18))
        ttk.Button(cache,text="Open Cache",command=self.open_cache).pack(side="left")
        ttk.Button(cache,text="Clear Cache",command=self.clear_cache).pack(side="left",padx=8)
        ttk.Label(
            cache,
            text="Cached by video ID + render size",
            foreground="#666"
        ).pack(side="right")

        b=ttk.Frame(self.root,padding=10); b.pack(fill="x")
        self.start=ttk.Button(b,text="Start Server",command=self.start_server); self.start.pack(side="left")
        self.stop=ttk.Button(b,text="Stop Server",command=self.stop_server,state="disabled"); self.stop.pack(side="left",padx=8)
        ttk.Button(b,text="Check Setup",command=self.check).pack(side="left")
        ttk.Button(b,text="Copy CC Command",command=self.copy_cmd).pack(side="right")

        lf=ttk.LabelFrame(self.root,text="Server Log",padding=6); lf.pack(fill="both",expand=True,padx=10,pady=(0,10))
        self.log=tk.Text(lf,state="disabled",wrap="word",font=("Consolas",9)); self.log.pack(fill="both",expand=True)

    def cache_dir(self):
        return SERVER / "src" / "youcube" / "data"

    def format_bytes(self, size):
        value = float(size)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if value < 1024 or unit == "TB":
                if unit == "B":
                    return f"{int(value)} {unit}"
                return f"{value:.1f} {unit}"
            value /= 1024
        return f"{int(size)} B"

    def get_cache_size(self):
        folder = self.cache_dir()
        if not folder.exists():
            return 0

        total = 0
        try:
            for p in folder.rglob("*"):
                if p.is_file():
                    try:
                        total += p.stat().st_size
                    except OSError:
                        pass
        except OSError:
            pass
        return total

    def refresh_cache_size(self):
        self.cache_size.set(self.format_bytes(self.get_cache_size()))

    def cache_tick(self):
        self.refresh_cache_size()
        self.root.after(3000, self.cache_tick)

    def open_cache(self):
        folder = self.cache_dir()
        folder.mkdir(parents=True, exist_ok=True)

        if os.name == "nt":
            os.startfile(folder)
        else:
            messagebox.showinfo("Cache folder", str(folder))

    def clear_cache(self):
        folder = self.cache_dir()

        if not folder.exists():
            self.refresh_cache_size()
            messagebox.showinfo("Cache", "The YouCube cache is already empty.")
            return

        if not messagebox.askyesno(
            "Clear YouCube Cache",
            "Delete all cached converted video frames and audio?\n\n"
            "The next playback of each video will need to download and convert again."
        ):
            return

        deleted = 0
        failed = []

        for p in list(folder.rglob("*")):
            if p.is_file():
                try:
                    p.unlink()
                    deleted += 1
                except OSError as e:
                    failed.append(f"{p.name}: {e}")

        # Remove any empty subfolders, but keep the cache root.
        for p in sorted(folder.rglob("*"), key=lambda x: len(x.parts), reverse=True):
            if p.is_dir():
                try:
                    p.rmdir()
                except OSError:
                    pass

        self.refresh_cache_size()

        if failed:
            messagebox.showwarning(
                "Cache partially cleared",
                f"Deleted {deleted} cached files.\n\n"
                "Some files could not be removed, usually because they are in use:\n"
                + "\n".join(failed[:8])
            )
        else:
            messagebox.showinfo(
                "Cache cleared",
                f"Deleted {deleted} cached files."
            )

    def browse(self,var):
        p=filedialog.askopenfilename(filetypes=[("Executables","*.exe"),("All files","*.*")])
        if p: var.set(p)

    def py(self):
        p=BASE/".venv"/"Scripts"/"python.exe"
        return p if p.exists() else Path(sys.executable)

    def entry(self):
        # YouCube's archived repository has existed in more than one
        # source layout. Detect both known locations, then fall back
        # to a recursive search.
        candidates = [
            SERVER / "src" / "youcube.py",
            SERVER / "src" / "youcube" / "youcube.py",
            SERVER / "src" / "youcube" / "__main__.py",
        ]

        for p in candidates:
            if p.exists():
                return p

        if SERVER.exists():
            matches = list(SERVER.rglob("youcube.py"))
            if matches:
                # Prefer the shortest path (normally the main server file).
                matches.sort(key=lambda p: (len(p.parts), str(p).lower()))
                return matches[0]

        return None

    def check(self,quiet=False):
        probs=[]
        if not self.entry(): probs.append("YouCube server source was not found under server-src. Run SETUP_SERVER.bat again.")
        if not Path(self.ffmpeg.get()).exists(): probs.append("FFmpeg missing.")
        if not Path(self.sanjuuni.get()).exists(): probs.append("Sanjuuni missing.")
        if probs:
            if not quiet: messagebox.showerror("Setup incomplete","\n\n".join(probs))
            return False
        if not quiet: messagebox.showinfo("Setup","Ready.")
        return True

    def start_server(self):
        if self.proc and self.proc.poll() is None: return
        if not self.check(True): self.check(); return
        env=os.environ.copy()
        env.update(
            HOST=self.host.get() or "0.0.0.0",
            PORT=self.port.get() or "5000",
            FFMPEG_PATH=self.ffmpeg.get(),
            SANJUUNI_PATH=self.sanjuuni.get(),
            NO_COLOR="True",
            PYTHONUTF8="1",
            PYTHONIOENCODING="utf-8",
            SANIC_WORKERS="1",
            WEB_CONCURRENCY="1"
        )
        try:
            self.proc=subprocess.Popen([str(self.py()),str(self.entry())],cwd=str(SERVER),
                stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
        except Exception as e:
            messagebox.showerror("Start failed",str(e)); return
        self.status.set("Running"); self.start.config(state="disabled"); self.stop.config(state="normal")
        threading.Thread(target=self.reader,daemon=True).start()

    def reader(self):
        for line in self.proc.stdout: self.q.put(line.rstrip())
        self.q.put("[Server stopped]")
        self.root.after(0,lambda:(self.status.set("Stopped"),self.start.config(state="normal"),self.stop.config(state="disabled")))

    def stop_server(self):
        if not self.proc or self.proc.poll() is not None:
            self.status.set("Stopped")
            self.start.config(state="normal")
            self.stop.config(state="disabled")
            return

        pid = self.proc.pid
        self.q.put(f"Stopping YouCube process tree (PID {pid})...")

        if os.name == "nt":
            # Sanic spawns worker child processes. Terminating only the parent
            # leaves those Python workers behind, so kill the full process tree.
            try:
                result = subprocess.run(
                    ["taskkill", "/PID", str(pid), "/T", "/F"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                if result.stdout.strip():
                    self.q.put(result.stdout.strip())

                if result.stderr.strip():
                    self.q.put(result.stderr.strip())

            except Exception as e:
                self.q.put(f"taskkill failed: {e}")

                try:
                    self.proc.terminate()
                    self.proc.wait(timeout=3)
                except Exception:
                    try:
                        self.proc.kill()
                    except Exception:
                        pass
        else:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=5)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass

        self.proc = None
        self.status.set("Stopped")
        self.start.config(state="normal")
        self.stop.config(state="disabled")

    def pump(self):
        try:
            while True:
                s=self.q.get_nowait(); self.log.config(state="normal"); self.log.insert("end",s+"\n"); self.log.see("end"); self.log.config(state="disabled")
        except queue.Empty: pass
        self.root.after(100,self.pump)

    def copy_cmd(self):
        cmd=f'settings.set("youcube.server", "ws://{self.ip.get()}:{self.port.get()}")\nsettings.save()'
        self.root.clipboard_clear(); self.root.clipboard_append(cmd)
        messagebox.showinfo("Copied","CC:Tweaked command copied.")

    def close(self):
        self.stop_server(); self.root.destroy()

if __name__=="__main__":
    r=tk.Tk(); App(r); r.mainloop()
