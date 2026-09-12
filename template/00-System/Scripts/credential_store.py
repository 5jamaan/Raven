"""Secrets live only in Windows Credential Manager; never in the vault."""
import ctypes, ctypes.wintypes as w, sys
class CREDENTIAL(ctypes.Structure):
    _fields_=[('Flags',w.DWORD),('Type',w.DWORD),('TargetName',w.LPWSTR),('Comment',w.LPWSTR),('LastWritten',w.FILETIME),('CredentialBlobSize',w.DWORD),('CredentialBlob',ctypes.POINTER(ctypes.c_ubyte)),('Persist',w.DWORD),('AttributeCount',w.DWORD),('Attributes',ctypes.c_void_p),('TargetAlias',w.LPWSTR),('UserName',w.LPWSTR)]
api=ctypes.WinDLL('Advapi32.dll',use_last_error=True)
api.CredReadW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]; api.CredReadW.restype=w.BOOL
api.CredWriteW.argtypes=[ctypes.POINTER(CREDENTIAL),w.DWORD]; api.CredWriteW.restype=w.BOOL
api.CredFree.argtypes=[ctypes.c_void_p]
def read(service):
    p=ctypes.POINTER(CREDENTIAL)()
    if not api.CredReadW('RavenOS/'+service,1,0,ctypes.byref(p)): raise ValueError('Windows Kimlik Bilgisi Yöneticisinde bağlantı yok')
    try: return ctypes.string_at(p.contents.CredentialBlob,p.contents.CredentialBlobSize).decode('utf-16-le')
    finally: api.CredFree(p)
def save(service,value):
    if service not in ('mem0',): raise ValueError('Desteklenmeyen servis')
    encoded=value.encode('utf-16-le'); buf=(ctypes.c_ubyte*len(encoded)).from_buffer_copy(encoded)
    c=CREDENTIAL(); c.Type=1; c.TargetName='RavenOS/'+service; c.CredentialBlobSize=len(encoded); c.CredentialBlob=buf; c.Persist=2; c.UserName='RavenOS'
    if not api.CredWriteW(ctypes.byref(c),0): raise ValueError('Kimlik bilgisi kaydedilemedi')
def prompt():
    import tkinter as tk
    from tkinter import messagebox
    root=tk.Tk(); root.title('RavenOS — Mem0 güvenli bağlantı'); root.geometry('560x230')
    tk.Label(root,text='Mem0 API anahtarını yalnız bu yerel alana yapıştır.\nAnahtar Windows Kimlik Bilgisi Yöneticisine kaydedilir.\nSohbete, vault dosyalarına veya Git’e yazılmaz.',wraplength=530,pady=20).pack()
    entry=tk.Entry(root,show='•',width=58); entry.pack(); entry.focus_set()
    def submit():
        value=entry.get().strip()
        if len(value)<12: messagebox.showerror('Bağlantı','Anahtar biçimini kontrol et'); return
        try: save('mem0',value)
        except ValueError: messagebox.showerror('Bağlantı','Güvenli kayıt başarısız'); return
        entry.delete(0,tk.END); root.destroy()
    tk.Button(root,text='Güvenli kaydet',command=submit,padx=15,pady=8).pack(pady=16)
    root.mainloop()
if __name__=='__main__': prompt()
