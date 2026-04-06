"""
🔐 PassManager - Gestionnaire de mots de passe sécurisé
"""
import customtkinter as ctk
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sqlite3
import hashlib
import base64
from tkinter import messagebox, filedialog, simpledialog
import tkinter as tk
import os
import time
import random
import string
import unicodedata
import sys
import platform

# --- NOUVELLE FONCTION POUR TROUVER LE CHEMIN SÉCURISÉ DE LA DB ---
def get_db_path(db_name="passwords.db", app_name="PassManager"):
    """
    Retourne le chemin complet pour stocker la base de données
    dans le répertoire de données de l'utilisateur (AppData sur Windows, 
    ~/.config sur Linux, ~/Library/Application Support sur macOS).
    """
    if platform.system() == "Windows":
        # Utilise %APPDATA%
        appdata_dir = os.path.join(os.environ.get('APPDATA'), app_name)
    elif platform.system() == "Darwin": # macOS
        # Utilise ~/Library/Application Support
        appdata_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', app_name)
    else: # Linux et autres systèmes Unix
        # Utilise ~/.config
        appdata_dir = os.path.join(os.path.expanduser('~'), '.config', app_name)

    # Crée le dossier s'il n'existe pas
    if not os.path.exists(appdata_dir):
        os.makedirs(appdata_dir)

    return os.path.join(appdata_dir, db_name)

try:
    from PIL import Image
    import pyperclip
except ImportError:
    print(
        "AVERTISSEMENT: Les librairies 'Pillow' (PIL) et 'pyperclip' sont fortement recommandées."
    )
    pyperclip = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

AUTO_LOGOUT_TIME = 60 * 60

PALETTE = {
    "PRIMARY_FG": "#3FA7D6",
    "PRIMARY_HOVER": "#2B8ABF",
    "SECURITY_FG": "#2E8B57",
    "SECURITY_HOVER": "#105F49",
    "DANGER_FG": "#C54F59",
    "DANGER_HOVER": "#9B454B",
    "SECONDARY_FG": "#7A8C99",
    "SECONDARY_HOVER": "#5A6A75",
    "GLOBAL_FG": "#E0A243",
    "GLOBAL_HOVER": "#C1872F",
    "UTILITY_FG": "#6C7079",
    "UTILITY_HOVER": "#52545A",
    # Lignes de la liste
    "ROW_EVEN_BG": "#2b2b2b",
    "ROW_ODD_BG": "#363636",
    # Textes
    "TEXT_PRIMARY": "#ffffff",
    "TEXT_SECONDARY": "#888888",
    "TEXT_ERROR": "#ff4444",
    # Tooltips
    "TOOLTIP_BG": "#333333",
    "TOOLTIP_FG": "#ffffff",
    # Couleurs des icônes Font Awesome
    "ICON_EYE":      "#5BC8F5",  # Bleu clair  — afficher/masquer
    "ICON_USER":     "#BBB6DB",  # Violet      — copier utilisateur
    "ICON_KEY":      "#F5C842",  # Or          — copier mot de passe
    "ICON_TRASH":    "#D69E9E",  # Rouge       — supprimer
    "ICON_GENERATE": "#4CAF82",  # Vert        — générer
    "ICON_UTILITY":  "#AAAAAA",  # Gris        — aide, base de données, effacer
}

# Caractères Unicode Font Awesome 6 Free Solid
FA_ICONS = {
    "eye":      "\uf06e",
    "eye_slash": "\uf070",
    "user":     "\uf007",
    "key":      "\uf084",
    "edit":     "\uf303",
    "trash":    "\uf2ed",
    "check":    "\uf00c",
    "xmark":    "\uf00d",
    "database": "\uf1c0",
    "help":     "\uf059",
    "generate": "\uf0e7",
}

# Fallback si Font Awesome n'est pas disponible
FALLBACK_ICONS = {
    "eye":      "Show",
    "eye_slash": "Hide",
    "user":     "User",
    "key":      "Copy",
    "edit":     "Edit",
    "trash":    "Del",
    "check":    "OK",
    "xmark":    "X",
    "database": "DB",
    "help":     "?",
    "generate": "Gen",
}

class ToolTip:
    """Classe pour créer des tooltips sur les widgets"""
    def __init__(self, widget, text, anchor=None, delay=100, hide_delay=100):
        self.widget = widget
        self.text = text
        self.anchor = anchor        # Si fourni, positionne le tooltip à gauche de cet anchor
        self.delay = delay          # Délai en ms avant affichage
        self.hide_delay = hide_delay  # Délai en ms avant disparition
        self.tooltip_window = None
        self._after_id = None
        self._hide_after_id = None
        self.widget.bind("<Enter>", self._schedule_tooltip)
        self.widget.bind("<Leave>", self._schedule_hide)

    def _schedule_tooltip(self, _event=None):
        self._cancel_hide()
        self._cancel_show()
        self._after_id = self.widget.after(self.delay, self.show_tooltip)

    def _schedule_hide(self, _event=None):
        self._cancel_show()
        self._hide_after_id = self.widget.after(self.hide_delay, self._do_hide)

    def _cancel_show(self):
        if self._after_id is not None:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _cancel_hide(self):
        if self._hide_after_id is not None:
            self.widget.after_cancel(self._hide_after_id)
            self._hide_after_id = None

    def _do_hide(self):
        self._hide_after_id = None
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        label = tk.Label(tw, text=self.text, justify='left',
                        background=PALETTE["TOOLTIP_BG"], foreground=PALETTE["TOOLTIP_FG"],
                        relief='solid', borderwidth=1,
                        font=("Arial", 9))
        label.pack(ipadx=5, ipady=3)
        tw.update_idletasks()  # Calcule la taille réelle du tooltip

        if self.anchor:
            # Positionner à gauche de l'ancre, centré verticalement
            aw = self.anchor
            x = aw.winfo_rootx() - tw.winfo_width() - 20
            y = aw.winfo_rooty() + (aw.winfo_height() - tw.winfo_height()) // 2
        else:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        tw.wm_geometry(f"+{x}+{y}")



class PasswordManager:
    """Gestion du chiffrement et de la base de données SQLite."""

    def __init__(self, db_path=None):
        super().__init__()
        # Si aucun chemin n'est fourni, on utilise le chemin AppData sécurisé
        self.db_path = db_path if db_path else get_db_path()
        self.master_key = None
        self.fernet = None
        self.encryption_key = None
        self.cipher = None
        self.init_database()

    def init_database(self):
        """Initialise la base de données SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Activer le mode WAL pour de meilleures performances en écriture
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                master_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_url TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_password TEXT NOT NULL,
                note TEXT,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Index pour accélérer les recherches sur site_url et username
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_site_url ON passwords (site_url COLLATE NOCASE)"
        )

        conn.commit()
        conn.close()

        self._check_and_update_schema()

    def _check_and_update_schema(self):
        """Met à jour le schéma de la BD si nécessaire."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT encrypted_note FROM passwords LIMIT 1")
            cursor.execute("ALTER TABLE passwords DROP COLUMN encrypted_note")
            conn.commit()
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("SELECT note FROM passwords LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE passwords ADD COLUMN note TEXT")
            conn.commit()
            
        conn.close()

    def _normalize_string_for_search(self, text):
        """Convertit une chaîne en minuscules et sans accents pour la recherche."""
        if not text:
            return ""
        normalized = unicodedata.normalize('NFKD', text)
        return "".join(
            [c for c in normalized if not unicodedata.combining(c)]
        ).lower()

    def _get_master_info(self, db_path=None):
        """Récupère le hash et le sel du mot de passe maître."""
        db_path = db_path if db_path else self.db_path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT master_hash, salt FROM users WHERE id = 1")
        result = cursor.fetchone()
        conn.close()
        if result:
            return base64.b64decode(result[0]), base64.b64decode(result[1])
        return None, None

    def _is_master_password_correct(self, master_password):
        """Vérifie le hash pour un mot de passe donné."""
        stored_hash, salt = self._get_master_info()

        if not stored_hash or not salt:
            return False

        test_hash = hashlib.pbkdf2_hmac(
            "sha256", master_password.encode(), salt, 100000
        )
        return test_hash == stored_hash

    def _derive_encryption_key(self, master_password):
        """Dérive une clé de chiffrement et initialise self.cipher."""
        _, salt = self._get_master_info()
        if not salt:
            raise ValueError("Salt non trouvé. Impossible de dériver la clé.")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self.cipher = Fernet(key)

    def set_master_password(self, master_password):
        """Définit le mot de passe maître."""
        salt = os.urandom(16)
        master_hash = hashlib.pbkdf2_hmac(
            "sha256", master_password.encode(), salt, 100000
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        cursor.execute(
            "INSERT INTO users (id, master_hash, salt) VALUES (?, ?, ?)",
            (
                1,
                base64.b64encode(master_hash).decode(),
                base64.b64encode(salt).decode(),
            ),
        )
        conn.commit()
        conn.close()

        self._derive_encryption_key(master_password)

    def verify_master_password(self, master_password):
        """Vérifie et définit la clé de chiffrement si correct."""
        if self._is_master_password_correct(master_password):
            self._derive_encryption_key(master_password)
            return True
        return False

    def has_master_password(self):
        """Vérifie si un mot de passe maître existe."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def encrypt(self, data):
        """Chiffre une chaîne de données."""
        if not self.cipher:
            raise ValueError("Clé de chiffrement non initialisée")
        return self.cipher.encrypt(data.encode("utf-8")).decode("utf-8")

    def decrypt(self, encrypted_data):
        """Déchiffre une chaîne de données."""
        if not self.cipher:
            raise ValueError("Clé de chiffrement non initialisée")
        if not encrypted_data:
            return ""
        return self.cipher.decrypt(encrypted_data.encode("utf-8")).decode("utf-8")

    def change_master_password(self, current_password, new_password):
        """Change le mot de passe maître et RECHIFFRE toutes les entrées."""
        if not self._is_master_password_correct(current_password):
            raise ValueError("Mot de passe maître actuel incorrect.")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, site_url, username, encrypted_password, note FROM passwords"
        )
        all_data = cursor.fetchall()
        decrypted_data = []

        for pid, site, user, encrypted_pwd, note in all_data:
            decrypted_pwd = self.decrypt(encrypted_pwd) 
            decrypted_data.append((pid, site, user, decrypted_pwd, note)) 

        self.set_master_password(new_password)

        for pid, site, user, decrypted_pwd, note in decrypted_data:
            new_encrypted_pwd = self.encrypt(decrypted_pwd) 

            cursor.execute(
                """
                UPDATE passwords SET encrypted_password = ?, note = ? WHERE id = ?
            """,
                (new_encrypted_pwd, note, pid),
            )

        conn.commit()
        conn.close()

    def add_password(self, site_url, username, password, note=""):
        encrypted_pwd = self.encrypt(password)
        note_to_save = note if note else None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO passwords (site_url, username, encrypted_password, note) VALUES (?, ?, ?, ?)",
            (site_url, username, encrypted_pwd, note_to_save),
        )
        conn.commit()
        conn.close()

    def get_all_passwords(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, site_url, username, encrypted_password, note FROM passwords ORDER BY site_url COLLATE NOCASE ASC"
        )
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_password_count(self):
        """Retourne le nombre total d'entrées de mots de passe."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM passwords")
        count = cursor.fetchone()[0]
        conn.close()
        return count


    def update_password(self, password_id, site_url, username, password, note=""):
        encrypted_pwd = self.encrypt(password)
        note_to_save = note if note else None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE passwords SET site_url = ?, username = ?, encrypted_password = ?, note = ? WHERE id = ?",
            (site_url, username, encrypted_pwd, note_to_save, password_id),
        )
        conn.commit()
        conn.close()

    def delete_password(self, password_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM passwords WHERE id = ?", (password_id,))
        conn.commit()
        conn.close()

    def search_passwords(self, query):
        """
        Recherche des mots de passe par site, utilisateur ou Note.
        (Recherche insensible à la casse et aux diacritiques)
        """
        conn = sqlite3.connect(self.db_path)
        # Enregistre la fonction de normalisation directement dans SQLite
        conn.create_function("normalize_text", 1, self._normalize_string_for_search)
        cursor = conn.cursor()

        normalized_like = f"%{self._normalize_string_for_search(query)}%"
        cursor.execute(
            """SELECT id, site_url, username, encrypted_password, note
               FROM passwords
               WHERE normalize_text(site_url) LIKE ?
                  OR normalize_text(username) LIKE ?
                  OR normalize_text(note) LIKE ?
               ORDER BY site_url COLLATE NOCASE ASC""",
            (normalized_like, normalized_like, normalized_like),
        )
        results = cursor.fetchall()
        conn.close()
        return results


class PassManagerApp(ctk.CTk):
    """Application principale avec interface moderne CustomTkinter."""

    def __init__(self):
        super().__init__()

        self.title("PassManager v1.0.0")
        self.geometry("950x650")
        self.minsize(950, 500)

        self.pm = PasswordManager()
        self.edit_mode = False
        self.edit_id = None
        self.is_logged_in = False
        self.last_activity_time = time.time()
        self.show_all_passwords = False
        self.visible_password_ids = set()

        self.fa_font = self._load_fa_font(size=13)
        self.fa_font_sm = self._load_fa_font(size=11)

        self.form_password_visible = False

        if not self.pm.has_master_password():
            self.after(1, self.show_setup_screen)
        else:
            self.after(1, self.show_login_screen)

        self.check_inactivity()

    def _load_fa_font(self, size=13):
        """Charge Font Awesome Free Solid. Cherche d'abord dans les polices système, puis dans le dossier de l'app."""
        from tkinter import font as tkfont
        fa_families = [
            "Font Awesome 6 Free Solid",
            "Font Awesome 5 Free Solid",
            "Font Awesome 6 Free",
            "Font Awesome 5 Free",
        ]
        # Chercher une version déjà installée
        available = tkfont.families()
        for name in fa_families:
            if name in available:
                return ctk.CTkFont(family=name, size=size, weight="normal")

        # Sinon, charger depuis un fichier TTF local
        base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
        for ttf in ("fa-solid-900.ttf", "Font Awesome 6 Free-Solid-900.otf", "Font Awesome 5 Free-Solid-900.otf"):
            fa_file = os.path.join(base, ttf)
            if os.path.exists(fa_file) and platform.system() == "Windows":
                try:
                    import ctypes
                    ctypes.windll.gdi32.AddFontResourceExW(fa_file, 0x10, 0)
                    ctypes.windll.user32.SendMessageW(0xFFFF, 0x001D, 0, 0)
                    # Forcer tkinter à recharger la liste des polices
                    self.update_idletasks()
                    for name in fa_families:
                        if name in tkfont.families():
                            return ctk.CTkFont(family=name, size=size, weight="normal")
                except Exception:
                    pass
        return None

    def _icon(self, name):
        """Retourne le caractère FA ou le texte de fallback pour une icône."""
        if self.fa_font is not None:
            return FA_ICONS.get(name, "?")
        return FALLBACK_ICONS.get(name, "?")

    def _force_dialog_on_top(self, func, title, message=None, **kwargs):
        """Wrapper pour forcer les boîtes de dialogue au-dessus."""
        self.attributes("-topmost", True)
        self.update()

        simple_dialogs = (
            simpledialog.askstring,
            simpledialog.askinteger,
            simpledialog.askfloat,
        )
        file_dialogs = (
            filedialog.asksaveasfilename,
            filedialog.askopenfilename,
            filedialog.askdirectory,
        )

        try:
            if "parent" not in kwargs:
                kwargs["parent"] = self

            if func in simple_dialogs:
                if "title" not in kwargs:
                    kwargs["title"] = title
                if message is not None and "prompt" not in kwargs:
                    kwargs["prompt"] = message
                result = func(**kwargs)

            elif func in file_dialogs:
                if "title" not in kwargs:
                    kwargs["title"] = title
                result = func(**kwargs)

            elif message is not None:
                result = func(title, message, **kwargs)
            else:
                result = func(title, **kwargs)

            return result
        except Exception:
            if (
                func
                in (messagebox.showerror, messagebox.showinfo, messagebox.showwarning)
                and message is not None
            ):
                func(title, message)
            else:
                raise
            return True
        finally:
            self.attributes("-topmost", False)

    def update_activity(self, event=None):
        """Met à jour le temps de la dernière activité."""
        if self.is_logged_in:
            self.last_activity_time = time.time()

    def check_inactivity(self):
        """Vérifie l'inactivité et déconnecte."""
        if self.is_logged_in and (
            time.time() - self.last_activity_time > AUTO_LOGOUT_TIME
        ):
            self.perform_auto_logout()

        self.after(10000, self.check_inactivity)

    def perform_auto_logout(self):
        """Effectue la déconnexion automatique."""
        if self.is_logged_in:
            self.logout(auto=True)
            self._force_dialog_on_top(
                messagebox.showwarning,
                "Déconnexion automatique",
                "Déconnecté après inactivité pour des raisons de sécurité.",
            )

    def logout(self, auto=False):
        """Déconnexion (manuel ou auto)."""
        if auto or self._force_dialog_on_top(
            messagebox.askyesno,
            "Déconnexion",
            "Êtes-vous sûr de vouloir vous déconnecter ?",
        ):
            self.pm.cipher = None
            self.is_logged_in = False
            self.show_all_passwords = False
            self.visible_password_ids = set()
            self.form_password_visible = False

            self.unbind_all("<Key>")
            self.unbind_all("<Button-1>")

            self.show_login_screen()
            """if not auto:
                self._force_dialog_on_top(
                    messagebox.showinfo,
                    "Déconnexion",
                    "Vous avez été déconnecté avec succès.",
                )"""

    def clear_window(self):
        """Efface tous les widgets de la fenêtre."""
        for widget in self.winfo_children():
            widget.destroy()

    def show_setup_screen(self):
        """Écran de configuration initiale."""
        self.clear_window()

        frame = ctk.CTkFrame(self, corner_radius=20)
        frame.pack(expand=True, padx=40, pady=40)

        ctk.CTkLabel(
            frame, text="🔐 Configuration initiale", font=("Arial", 24, "bold")
        ).pack(pady=20, padx=40)

        ctk.CTkLabel(
            frame, text="Créez votre mot de passe maître", font=("Arial", 14)
        ).pack(pady=10)

        self.setup_password_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Mot de passe maître",
            show="•",
            width=300,
            height=40,
        )
        self.setup_password_entry.pack(pady=10, padx=40)

        self.setup_confirm_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Confirmer le mot de passe",
            show="•",
            width=300,
            height=40,
        )
        self.setup_confirm_entry.pack(pady=10, padx=40)

        ctk.CTkButton(
            frame,
            text="Créer",
            command=self.create_master_password,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color=PALETTE["PRIMARY_FG"],
            hover_color=PALETTE["PRIMARY_HOVER"],
        ).pack(pady=20, padx=40)
        
        self.setup_password_entry.focus_set()

    def create_master_password(self):
        """Crée le mot de passe maître."""
        password = self.setup_password_entry.get()
        confirm = self.setup_confirm_entry.get()

        if not password or len(password) < 8:
            self._force_dialog_on_top(
                messagebox.showerror,
                "Erreur",
                "Le mot de passe doit contenir au moins 8 caractères.",
            )
            return

        if password != confirm:
            self._force_dialog_on_top(
                messagebox.showerror,
                "Erreur",
                "Les mots de passe ne correspondent pas.",
            )
            return

        try:
            self.pm.set_master_password(password)
            self._force_dialog_on_top(
                messagebox.showinfo, "Succès", "Mot de passe maître créé avec succès !"
            )
            self.show_main_app()
        except Exception as e:
            self._force_dialog_on_top(
                messagebox.showerror, "Erreur", f"Échec de la création: {str(e)}"
            )

    def show_login_screen(self):
        """Écran de connexion."""
        self.clear_window()

        frame = ctk.CTkFrame(self, corner_radius=20)
        frame.pack(expand=True, padx=40, pady=40)

        ctk.CTkLabel(frame, text="PassManager 🔐", font=("Arial", 28, "bold")).pack(
            pady=20, padx=60
        )

        ctk.CTkLabel(
            frame, text="Entrez votre mot de passe maître", font=("Arial", 14)
        ).pack(pady=10)

        self.login_password_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Mot de passe maître",
            show="•",
            width=300,
            height=40,
        )
        self.login_password_entry.pack(pady=15, padx=60)
        self.login_password_entry.bind("<Return>", lambda e: self.verify_login())
        
        self.after(10, self.login_password_entry.focus_set)

        self.login_error_label = ctk.CTkLabel(frame, text="", text_color=PALETTE["TEXT_ERROR"])
        self.login_error_label.pack()

        ctk.CTkButton(
            frame,
            text="Déverrouiller",
            command=self.verify_login,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color=PALETTE["PRIMARY_FG"],
            hover_color=PALETTE["PRIMARY_HOVER"],
        ).pack(pady=15, padx=60)

    def verify_login(self):
        """Vérifie le mot de passe maître."""
        password = self.login_password_entry.get()

        if self.pm.verify_master_password(password):
            self.show_main_app()
        else:
            self.login_error_label.configure(text="Mot de passe incorrect")

    def show_main_app(self):
        """Interface principale de l'application."""
        self.is_logged_in = True
        self.clear_window()
        self.update_activity()

        self.bind_all("<Key>", self.update_activity)
        self.bind_all("<Button-1>", self.update_activity)

        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        ctk.CTkLabel(
            header_frame, text="PassManager Local", font=("Arial", 20, "bold")
        ).pack(side="left", padx=20)

        # 5. Déconnexion (tout à droite)
        ctk.CTkButton(
            header_frame,
            text="Déconnexion",
            command=self.logout,
            fg_color=PALETTE["DANGER_FG"],
            hover_color=PALETTE["DANGER_HOVER"],
            width=120,
        ).pack(side="right", padx=10, pady=15)

        # 4. Aide et documentation (icône avec tooltip)
        help_btn = ctk.CTkButton(
            header_frame,
            text=self._icon("help"),
            font=self.fa_font,
            text_color=PALETTE["ICON_UTILITY"],
            command=self.show_help,
            fg_color=PALETTE["UTILITY_FG"],
            hover_color=PALETTE["UTILITY_HOVER"],
            width=40,
            height=40,
        )
        help_btn.pack(side="right", padx=5, pady=15)
        ToolTip(help_btn, "Aide et documentation")

        # 3. Exporter la base de données (icône avec tooltip)
        export_db_btn = ctk.CTkButton(
            header_frame,
            text=self._icon("database"),
            font=self.fa_font,
            text_color=PALETTE["ICON_UTILITY"],
            command=self.export_database,
            fg_color=PALETTE["SECONDARY_FG"],
            hover_color=PALETTE["SECONDARY_HOVER"],
            width=40,
            height=40,
        )
        export_db_btn.pack(side="right", padx=5, pady=15)
        ToolTip(export_db_btn, "Exporter la base de données (chiffrée)")

        # 2. Exporter mots de passe
        ctk.CTkButton(
            header_frame,
            text="Exporter Mots de Passe",
            command=self.export_passwords_to_file,
            fg_color=PALETTE["SECONDARY_FG"],
            hover_color=PALETTE["SECONDARY_HOVER"],
            width=150,
        ).pack(side="right", padx=5, pady=15)

        # 1. Changer mot de passe maître
        ctk.CTkButton(
            header_frame,
            text="Changer MdP Maître",
            command=self.show_change_master_password_dialog,
            fg_color=PALETTE["GLOBAL_FG"],
            hover_color=PALETTE["GLOBAL_HOVER"],
            width=150,
        ).pack(side="right", padx=5, pady=15)

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        form_frame = ctk.CTkFrame(main_container, corner_radius=10)
        form_frame.pack(fill="x", pady=(0, 20))

        self.form_title_label = ctk.CTkLabel(
            form_frame, text="Ajouter un mot de passe", font=("Arial", 16, "bold")
        )
        self.form_title_label.pack(pady=15)

        form_fields_frame_1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_fields_frame_1.pack(pady=5)

        self.site_entry = ctk.CTkEntry(
            form_fields_frame_1, placeholder_text="Site (URL/Nom)", width=250, height=35
        )
        self.site_entry.pack(side="left", padx=5)

        self.username_entry = ctk.CTkEntry(
            form_fields_frame_1,
            placeholder_text="Nom d'utilisateur",
            width=250,
            height=35,
        )
        self.username_entry.pack(side="left", padx=5)

        password_input_frame = ctk.CTkFrame(form_fields_frame_1, fg_color="transparent")
        password_input_frame.pack(side="left", padx=5)

        self.password_entry = ctk.CTkEntry(
            password_input_frame,
            placeholder_text="Mot de passe à stocker",
            show="•",
            width=250,
            height=35,
        )
        self.password_entry.pack(side="left")

        self.toggle_form_eye_button = ctk.CTkButton(
            password_input_frame,
            text=self._icon("eye"),
            font=self.fa_font,
            text_color=PALETTE["ICON_EYE"],
            command=lambda: self.toggle_form_password_visibility(),
            width=35,
            height=35,
            fg_color=PALETTE["UTILITY_FG"],
            hover_color=PALETTE["UTILITY_HOVER"],
        )
        self.toggle_form_eye_button.pack(side="left", padx=(5, 0))

        ctk.CTkButton(
            password_input_frame,
            text=self._icon("generate"),
            font=self.fa_font,
            text_color=PALETTE["ICON_GENERATE"],
            command=self.open_password_generator_dialog,
            width=35,
            height=35,
            fg_color=PALETTE["SECURITY_FG"],
            hover_color=PALETTE["SECURITY_HOVER"],
        ).pack(side="left", padx=5)

        form_fields_frame_2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_fields_frame_2.pack(pady=5)

        ctk.CTkLabel(form_fields_frame_2, text="Note :", font=("Arial", 13)).pack(
            side="left", padx=(10, 5)
        )

        self.note_entry = ctk.CTkEntry(
            form_fields_frame_2,
            placeholder_text="Note",
            show="",
            width=600,
            height=35,
        )
        self.note_entry.pack(side="left", padx=5)

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        self.submit_button = ctk.CTkButton(
            button_frame,
            text="Ajouter",
            command=self.submit_password,
            width=100,
            height=35,
            font=("Arial", 13, "bold"),
            fg_color=PALETTE["PRIMARY_FG"],
            hover_color=PALETTE["PRIMARY_HOVER"],
        )
        self.submit_button.pack(side="left", padx=5)

        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="Annuler",
            command=self.cancel_edit,
            fg_color=PALETTE["SECONDARY_FG"],
            hover_color=PALETTE["SECONDARY_HOVER"],
            width=100,
            height=35,
        )
        self.cancel_button.pack(side="left", padx=5)
        self.cancel_button.pack_forget()

        self.clear_form_button = ctk.CTkButton(
            button_frame,
            text="Effacer",
            command=self.clear_form,
            fg_color=PALETTE["SECONDARY_FG"],
            hover_color=PALETTE["SECONDARY_HOVER"],
            width=100,
            height=35,
        )
        self.clear_form_button.pack(side="left", padx=5)

        list_frame = ctk.CTkFrame(main_container, corner_radius=10)
        list_frame.pack(fill="both", expand=True)

        search_options_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        search_options_frame.pack(fill="x", padx=10, pady=10)
        
        search_container = ctk.CTkFrame(search_options_frame, fg_color="transparent")
        search_container.pack(side="left", padx=(5, 10))

        self._search_after_id = None

        self.search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="Rechercher par Site, Utilisateur ou Note...",
            width=350,
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind(
            "<KeyRelease>",
            lambda e: self._debounced_search(),
        )
        
        self.clear_search_button = ctk.CTkButton(
            search_container,
            text=self._icon("xmark"),
            font=self.fa_font,
            command=self.clear_search_and_refresh,
            width=35,
            height=28,
            fg_color=PALETTE["SECONDARY_FG"],
            hover_color=PALETTE["SECONDARY_HOVER"],
            text_color=PALETTE["ICON_UTILITY"],
        )
        self.clear_search_button.pack(side="left", padx=(5, 0))


        self.toggle_all_button = ctk.CTkButton(
            search_options_frame,
            text="Afficher tout les MdP",
            image=None,
            command=self.toggle_all_passwords,
            width=150,
            fg_color=PALETTE["PRIMARY_FG"],
            hover_color=PALETTE["PRIMARY_HOVER"],
        )
        self.toggle_all_button.pack(side="right", padx=5)

        self.list_title_label = ctk.CTkLabel(
            list_frame, text="", font=("Arial", 16, "bold")
        )
        self.list_title_label.pack(pady=(0, 10))

        self.scroll_frame = ctk.CTkScrollableFrame(list_frame, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.refresh_password_list()
        
    def _debounced_search(self):
        """Déclenche la recherche après 200ms d'inactivité clavier (debounce)."""
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(
            200, lambda: self.refresh_password_list(self.search_entry.get())
        )

    def clear_search_and_refresh(self):
        """Vide le champ de recherche et rafraîchit la liste."""
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
            self._search_after_id = None
        self.search_entry.delete(0, "end")
        self.refresh_password_list()


    def toggle_all_passwords(self):
        """Affiche ou masque tous les mots de passe de la liste."""
        self.show_all_passwords = not self.show_all_passwords
        self.update_activity()

        search_query = self.search_entry.get() if hasattr(self, "search_entry") else ""
        passwords = (
            self.pm.search_passwords(search_query)
            if search_query
            else self.pm.get_all_passwords()
        )

        if self.show_all_passwords:
            self.visible_password_ids = {pwd_id for pwd_id, _, _, _, _ in passwords}
            new_text = "Masquer tout les MdP"
        else:
            self.visible_password_ids = set()
            new_text = "Afficher tout les MdP"

        self.toggle_all_button.configure(text=new_text, image=None)

        self.refresh_password_list(search_query)

    def open_password_generator_dialog(self):
        """Ouvre une fenêtre pour configurer et générer un mot de passe."""
        self.update_activity()

        toplevel = ctk.CTkToplevel(self)
        toplevel.title("Générateur de Mot de Passe")
        toplevel.geometry("350x450")
        toplevel.attributes("-topmost", True)

        toplevel.transient(self)
        toplevel.grab_set()

        ctk.CTkLabel(
            toplevel, text="Longueur du mot de passe (8-32):", font=("Arial", 14)
        ).pack(pady=(20, 5))
        self.gen_length_var = ctk.IntVar(value=16)
        self.gen_length_slider = ctk.CTkSlider(
            toplevel,
            from_=8,
            to=32,
            variable=self.gen_length_var,
            command=lambda x: (
                self.gen_length_label.configure(text=f"Longueur: {int(x)}"),
                self._generate_password_display(),
            ),
        )
        self.gen_length_slider.pack(pady=5, padx=20, fill="x")
        self.gen_length_label = ctk.CTkLabel(toplevel, text=f"Longueur: 16", width=20)
        self.gen_length_label.pack(pady=5)

        ctk.CTkLabel(toplevel, text="Options de Complexité:", font=("Arial", 14)).pack(
            pady=(15, 5)
        )
        self.gen_upper_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            toplevel,
            text="Majuscules (A-Z)",
            variable=self.gen_upper_var,
            command=self._generate_password_display,
        ).pack(pady=5, padx=20, anchor="w")
        self.gen_lower_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            toplevel,
            text="Minuscules (a-z)",
            variable=self.gen_lower_var,
            command=self._generate_password_display,
        ).pack(pady=5, padx=20, anchor="w")
        self.gen_digits_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            toplevel,
            text="Chiffres (0-9)",
            variable=self.gen_digits_var,
            command=self._generate_password_display,
        ).pack(pady=5, padx=20, anchor="w")
        self.gen_symbols_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            toplevel,
            text="Symboles (!@#$%)",
            variable=self.gen_symbols_var,
            command=self._generate_password_display,
        ).pack(pady=5, padx=20, anchor="w")

        self.gen_result_entry = ctk.CTkEntry(
            toplevel,
            placeholder_text="Mot de passe généré",
            width=300,
            state="readonly",
        )
        self.gen_result_entry.pack(pady=15, padx=20)

        button_gen_frame = ctk.CTkFrame(toplevel, fg_color="transparent")
        button_gen_frame.pack(pady=10)

        ctk.CTkButton(
            button_gen_frame,
            text="Générer",
            command=self._generate_password_display,
            fg_color=PALETTE["SECURITY_FG"],
            hover_color=PALETTE["SECURITY_HOVER"],
            height=40,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_gen_frame,
            text="Insérer dans le Formulaire",
            command=lambda: self.insert_generated_password(toplevel),
            fg_color=PALETTE["PRIMARY_FG"],
            hover_color=PALETTE["PRIMARY_HOVER"],
            height=40,
        ).pack(side="left", padx=5)

        self._generate_password_display()

    def _generate_password_logic(
        self, length, use_upper, use_lower, use_digits, use_symbols
    ):
        """Logique de génération de mot de passe."""

        characters = ""
        if use_lower:
            characters += string.ascii_lowercase
        if use_upper:
            characters += string.ascii_uppercase
        if use_digits:
            characters += string.digits
        if use_symbols:
            characters += (
                string.punctuation.replace('"', "").replace("'", "").replace("\\", "")
            )

        if not characters:
            return "ERREUR: Sélectionnez au moins un type de caractère."

        password = []
        if use_lower:
            password.append(random.choice(string.ascii_lowercase))
        if use_upper:
            password.append(random.choice(string.ascii_uppercase))
        if use_digits:
            password.append(random.choice(string.digits))
        if use_symbols:
            safe_symbols = "!@#$%^&*()-_+=[]{}|:<>?/.,"
            password.append(random.choice(safe_symbols))

        remaining_length = length - len(password)
        if remaining_length < 0:
            remaining_length = 0
            password = password[:length]

        password += [random.choice(characters) for _ in range(remaining_length)]

        random.shuffle(password)
        return "".join(password)

    def _generate_password_display(self):
        """Génère un mot de passe et l'affiche."""
        try:
            length = self.gen_length_var.get()
            use_upper = self.gen_upper_var.get()
            use_lower = self.gen_lower_var.get()
            use_digits = self.gen_digits_var.get()
            use_symbols = self.gen_symbols_var.get()

            if not any([use_upper, use_lower, use_digits, use_symbols]):
                generated_pwd = "ERREUR: Sélectionnez un type de caractère."
            else:
                generated_pwd = self._generate_password_logic(
                    length, use_upper, use_lower, use_digits, use_symbols
                )

            self.gen_result_entry.configure(state="normal")
            self.gen_result_entry.delete(0, "end")
            self.gen_result_entry.insert(0, generated_pwd)
            self.gen_result_entry.configure(state="readonly")
        except AttributeError:
            pass
        except Exception as e:
            self.gen_result_entry.configure(state="normal")
            self.gen_result_entry.delete(0, "end")
            self.gen_result_entry.insert(0, f"Erreur: {str(e)}")
            self.gen_result_entry.configure(state="readonly")

    def insert_generated_password(self, toplevel):
        """Insère le mot de passe généré dans le formulaire principal."""
        generated_pwd = self.gen_result_entry.get()

        if generated_pwd.startswith("ERREUR"):
            self._force_dialog_on_top(
                messagebox.showerror, "Erreur Générateur", generated_pwd
            )
            return

        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, generated_pwd)

        self.form_password_visible = True
        self.password_entry.configure(show="")
        self.toggle_form_eye_button.configure(text=self._icon("eye_slash"))

        toplevel.destroy()
        """self._force_dialog_on_top(
            messagebox.showinfo,
            "Générateur",
            "Mot de passe inséré dans le formulaire !",
        )"""

    def toggle_form_password_visibility(self):
        """Affiche ou masque le mot de passe dans le champ du formulaire."""
        self.update_activity()
        self.form_password_visible = not self.form_password_visible

        if self.form_password_visible:
            self.password_entry.configure(show="")
            self.toggle_form_eye_button.configure(text=self._icon("eye_slash"))
        else:
            self.password_entry.configure(show="•")
            self.toggle_form_eye_button.configure(
                text=self._icon("eye"),
            )

    def edit_password(self, password_id, site, username, encrypted_pwd, note):
        """Prépare l'édition d'un mot de passe et de sa note."""
        self.update_activity()
        try:
            decrypted_pwd = self.pm.decrypt(encrypted_pwd)
            decrypted_note = note if note else ""

            self.edit_mode = True
            self.edit_id = password_id

            self.site_entry.delete(0, "end")
            self.site_entry.insert(0, site)

            self.username_entry.delete(0, "end")
            self.username_entry.insert(0, username)

            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, decrypted_pwd)
            self.form_password_visible = False
            self.password_entry.configure(show="•")
            self.toggle_form_eye_button.configure(text=self._icon("eye"))

            self.note_entry.delete(0, "end")
            self.note_entry.insert(0, decrypted_note)
            self.note_entry.configure(show="")

            self.form_title_label.configure(text="Modifier un mot de passe")
            self.submit_button.configure(
                text="Enregistrer",
                fg_color=PALETTE["PRIMARY_FG"],
                hover_color=PALETTE["PRIMARY_HOVER"],
            )
            self.cancel_button.configure(
                fg_color=PALETTE["SECONDARY_FG"],
                hover_color=PALETTE["SECONDARY_HOVER"],
            )
            self.cancel_button.pack(side="left", padx=5)

            self.clear_form_button.pack_forget()
            
            self.site_entry.focus_set()

        except Exception as e:
            self._force_dialog_on_top(
                messagebox.showerror, "Erreur", f"Impossible de déchiffrer le mot de passe : {str(e)}"
            )

    def cancel_edit(self):
        """Annule l'édition et réinitialise le formulaire."""
        self.update_activity()
        self.clear_form()

    def clear_form(self):
        """Réinitialise le formulaire."""
        self.edit_mode = False
        self.edit_id = None

        self.site_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.note_entry.delete(0, "end")

        self.password_entry.configure(show="•")
        self.form_password_visible = False
        if hasattr(self, "toggle_form_eye_button"):
            self.toggle_form_eye_button.configure(
                text=self._icon("eye"),
                fg_color=PALETTE["UTILITY_FG"],
                hover_color=PALETTE["UTILITY_HOVER"],
            )

        self.note_entry.configure(show="")

        self.form_title_label.configure(text="Ajouter un mot de passe")
        self.submit_button.configure(
            text="Ajouter",
            fg_color=PALETTE["PRIMARY_FG"],
            hover_color=PALETTE["PRIMARY_HOVER"],
        )
        self.cancel_button.pack_forget()

        self.clear_form_button.configure(
            fg_color=PALETTE["SECONDARY_FG"],
            hover_color=PALETTE["SECONDARY_HOVER"],
        )
        self.clear_form_button.pack(side="left", padx=5)
        
        self.site_entry.focus_set()

    def _set_copy_feedback(self, btn, is_password):
        """Gère le changement de couleur d'un bouton après une copie."""
        original_text = self._icon("key") if is_password else self._icon("user")

        btn.configure(
            text=self._icon("check"),
            fg_color=PALETTE["GLOBAL_FG"],
            hover_color=PALETTE["GLOBAL_HOVER"],
        )

        self.after(
            1500,
            lambda: btn.configure(
                text=original_text,
                fg_color=PALETTE["SECONDARY_FG"],
                hover_color=PALETTE["SECONDARY_HOVER"],
            ),
        )

    def copy_text_to_clipboard(self, text_to_copy, btn):
        """Copie une chaîne de données en clair dans le presse-papiers."""
        if pyperclip is None:
            self._force_dialog_on_top(
                messagebox.showerror,
                "Erreur",
                "La librairie 'pyperclip' n'est pas installée. Impossible de copier.",
            )
            return

        try:
            pyperclip.copy(text_to_copy)
            self.update_activity()
            self._set_copy_feedback(btn, is_password=False)
            
            # Effacer le presse-papier après 30 secondes
            self._schedule_clipboard_clear(text_to_copy)
            
        except Exception as e:
            self._force_dialog_on_top(
                messagebox.showerror, "Erreur", f"Erreur lors de la copie: {str(e)}"
            )

    def copy_password_to_clipboard(self, encrypted_password, btn):
        """Déchiffre et copie le mot de passe dans le presse-papiers."""
        if pyperclip is None:
            self._force_dialog_on_top(
                messagebox.showerror,
                "Erreur",
                "La librairie 'pyperclip' n'est pas installée. Impossible de copier.",
            )
            return

        try:
            decrypted = self.pm.decrypt(encrypted_password)
            pyperclip.copy(decrypted)
            self.update_activity()
            self._set_copy_feedback(btn, is_password=True)
            
            # Effacer le presse-papier après 30 secondes
            self._schedule_clipboard_clear(decrypted)

        except Exception as e:
            self._force_dialog_on_top(
                messagebox.showerror, "Erreur", f"Erreur lors de la copie: {str(e)}"
            )

    def _schedule_clipboard_clear(self, copied_text):
        """Programme l'effacement du presse-papier après 30 secondes si le contenu n'a pas changé."""
        if pyperclip is None:
            return
        
        def clear_clipboard():
            try:
                # Vérifier si le contenu actuel du presse-papier est toujours celui qu'on a copié
                current_clipboard = pyperclip.paste()
                if current_clipboard == copied_text:
                    # Effacer le presse-papier en le remplaçant par une chaîne vide
                    pyperclip.copy("")
            except:
                # En cas d'erreur, ne rien faire
                pass
        
        # Programmer l'effacement après 30 secondes (30000 ms)
        self.after(30000, clear_clipboard)

    def submit_password(self):
        """Ajoute ou modifie un mot de passe et sa note."""
        self.update_activity()
        site = self.site_entry.get()
        username = self.username_entry.get()
        note = self.note_entry.get()
        password = self.password_entry.get()

        if not site or not username or not password:
            self._force_dialog_on_top(
                messagebox.showerror,
                "Erreur",
                "Les champs Site, Utilisateur et Mot de passe sont requis.",
            )
            return

        try:
            if self.edit_mode:
                self.pm.update_password(self.edit_id, site, username, password, note)
                self._force_dialog_on_top(
                    messagebox.showinfo,
                    "Succès",
                    "Mot de passe et Note modifiés avec succès !",
                )
            else:
                self.pm.add_password(site, username, password, note)
                self._force_dialog_on_top(
                    messagebox.showinfo,
                    "Succès",
                    "Mot de passe et Note ajoutés avec succès !",
                )

            self.clear_form()
            self.refresh_password_list(
                self.search_entry.get() if hasattr(self, "search_entry") else ""
            )
        except Exception as e:
            self._force_dialog_on_top(
                messagebox.showerror, "Erreur", f"Erreur lors de l'opération : {str(e)}"
            )

    def delete_password(self, password_id):
        """Supprime un mot de passe."""
        self.update_activity()
        if self._force_dialog_on_top(
            messagebox.askyesno,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer ce mot de passe ?",
        ):
            try:
                self.pm.delete_password(password_id)
                self._force_dialog_on_top(
                    messagebox.showinfo, "Succès", "Mot de passe et Note supprimés"
                )

                if password_id in self.visible_password_ids:
                    self.visible_password_ids.remove(password_id)

                self.refresh_password_list(
                    self.search_entry.get() if hasattr(self, "search_entry") else ""
                )
            except Exception as e:
                self._force_dialog_on_top(
                    messagebox.showerror,
                    "Erreur",
                    f"Erreur lors de la suppression : {str(e)}",
                )

    def export_passwords_to_file(self):
        """Déchiffre et exporte tous les mots de passe vers un fichier choisi."""
        self.update_activity()

        file_path = self._force_dialog_on_top(
            filedialog.asksaveasfilename,
            "Exporter les mots de passe",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
            initialfile="passwords_export.txt",
        )

        if not file_path:
            return

        try:
            passwords = self.pm.get_all_passwords()

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("--- PassManager Exportation Sécurisée ---\n\n")
                f.write("ATTENTION: Ce fichier contient les mots de passe en CLAIR.\n")
                f.write("Ne le stockez pas sans sécurité supplémentaire.\n\n")

                for _, site, username, encrypted_pwd, note in passwords:
                    decrypted_pwd = self.pm.decrypt(encrypted_pwd)
                    decrypted_note = note if note else ""

                    f.write(f"Site: {site}\n")
                    f.write(f"Utilisateur: {username}\n")
                    f.write(f"Mot de passe: {decrypted_pwd}\n")
                    f.write(f"Note: {decrypted_note}\n")
                    f.write("-" * 50 + "\n")

            self._force_dialog_on_top(
                messagebox.showinfo,
                "Succès Exportation",
                f"Tous les mots de passe ont été exportés vers:\n{file_path}",
            )

        except Exception as e:
            self._force_dialog_on_top(
                messagebox.showerror,
                "Erreur Exportation",
                f"Échec de l'exportation: {str(e)}",
            )

    def export_database(self):
        """Exporte la base de données chiffrée (passwords.db) vers un emplacement choisi."""
        self.update_activity()

        file_path = self._force_dialog_on_top(
            filedialog.asksaveasfilename,
            "Exporter la base de données",
            defaultextension=".db",
            filetypes=[
                ("Database files", "*.db"),
                ("All files", "*.*"),
            ],
            initialfile="passwords_backup.db",
        )

        if not file_path:
            return

        try:
            import shutil
            # Copier le fichier de base de données
            shutil.copy2(self.pm.db_path, file_path)

            self._force_dialog_on_top(
                messagebox.showinfo,
                "Succès Exportation",
                f"La base de données a été exportée vers:\n{file_path}\n\n"
                f"Cette copie contient vos mots de passe CHIFFRÉS.\n"
                f"Elle peut être restaurée en la renommant 'passwords.db'.",
            )

        except Exception as e:
            self._force_dialog_on_top(
                messagebox.showerror,
                "Erreur Exportation",
                f"Échec de l'exportation de la base de données: {str(e)}",
            )

    def show_help(self):
        """Affiche une fenêtre d'aide en lisant le fichier AIDE.md."""
        self.update_activity()

        # Créer une fenêtre d'aide
        help_window = ctk.CTkToplevel(self)
        help_window.title("Aide - PassManager")
        help_window.geometry("750x650")
        help_window.transient(self)
        help_window.grab_set()

        # Centrer la fenêtre
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (750 // 2)
        y = (help_window.winfo_screenheight() // 2) - (650 // 2)
        help_window.geometry(f"750x650+{x}+{y}")

        # Titre
        ctk.CTkLabel(
            help_window,
            text="🔐 PassManager - Guide d'utilisation",
            font=("Arial", 20, "bold"),
        ).pack(pady=20)

        # Zone de texte scrollable
        help_frame = ctk.CTkScrollableFrame(help_window, width=700, height=500)
        help_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Lire le fichier AIDE.md
        help_text = ""
        try:
            # Chercher AIDE.md dans le même dossier que l'exécutable
            aide_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AIDE.md")
            
            # Si on est dans un exécutable PyInstaller
            if getattr(sys, 'frozen', False):
                aide_path = os.path.join(os.path.dirname(sys.executable), "AIDE.md")
            
            with open(aide_path, "r", encoding="utf-8") as f:
                help_text = f.read()
        except FileNotFoundError:
            help_text = """
# 🔐 PassManager - Guide d'utilisation

⚠️ Le fichier d'aide (AIDE.md) n'a pas été trouvé.

## Emplacement attendu
Le fichier AIDE.md doit être placé dans le même dossier que l'exécutable PassManager.

## Informations de base

### Emplacement des données (Windows)
```
C:\\Users\\monNomUtilisateur\\AppData\\Roaming\\PassManager\\passwords.db
```

### Fonctionnalités principales
- Ajouter, modifier, supprimer des mots de passe
- Générer des mots de passe sécurisés
- Exporter vos données (texte clair ou DB chiffrée)
- Changer votre mot de passe maître

### Support
Version: 6.0
Développé par: edurel
Usage: Non-commercial uniquement
            """
        except Exception as e:
            help_text = f"Erreur lors de la lecture du fichier d'aide: {str(e)}"

        ctk.CTkLabel(
            help_frame,
            text=help_text,
            font=("Arial", 12),
            justify="left",
            anchor="w",
        ).pack(fill="both", padx=20, pady=10)

        # Bouton de fermeture
        ctk.CTkButton(
            help_window,
            text="Fermer",
            command=help_window.destroy,
            width=150,
            height=40,
            fg_color=PALETTE["PRIMARY_FG"],
            hover_color=PALETTE["PRIMARY_HOVER"],
        ).pack(pady=15)

    def show_change_master_password_dialog(self):
        """Affiche la boîte de dialogue pour changer le mot de passe maître."""
        self.update_activity()

        current_password = self._force_dialog_on_top(
            simpledialog.askstring,
            "Changer le Mot de Passe Maître",
            "MOT DE PASSE MAÎTRE ACTUEL",
            show="*",
        )
        if not current_password:
            return

        if not self.pm._is_master_password_correct(current_password):
            self._force_dialog_on_top(
                messagebox.showerror,
                "Erreur de Vérification",
                "Mot de passe maître actuel incorrect.",
            )
            return

        new_password = self._force_dialog_on_top(
            simpledialog.askstring,
            "Changer le Mot de Passe Maître",
            "NOUVEAU MOT DE PASSE MAÎTRE (min 8 car.)",
            show="*",
        )
        if not new_password or len(new_password) < 8:
            self._force_dialog_on_top(
                messagebox.showerror,
                "Erreur",
                "Le nouveau mot de passe doit contenir au moins 8 caractères.",
            )
            return

        confirm_password = self._force_dialog_on_top(
            simpledialog.askstring,
            "Changer le Mot de Passe Maître",
            "Confirmez le NOUVEAU MOT DE PASSE MAÎTRE",
            show="*",
        )
        if new_password != confirm_password:
            self._force_dialog_on_top(
                messagebox.showerror,
                "Erreur",
                "Les nouveaux mots de passe ne correspondent pas.",
            )
            return

        try:
            self.pm.change_master_password(current_password, new_password)
            self._force_dialog_on_top(
                messagebox.showinfo,
                "Succès",
                "Mot de passe Maître changé, données rechiffrées : reconnectez-vous avec le nouveau mot de passe.",
            )
            self.logout(auto=True)

        except Exception as e:
            self._force_dialog_on_top(
                messagebox.showerror,
                "Erreur Critique",
                f"Échec du rechiffrement des données : {str(e)}\nVos données sont intactes mais le changement a échoué.",
            )

    def refresh_password_list(self, search_query=""):
        """Rafraîchit la liste des mots de passe."""
        self.update_activity()

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if search_query:
            passwords = self.pm.search_passwords(search_query)
            self.list_title_label.configure(text=f"Mots de passe trouvés ({len(passwords)})")
        else:
            passwords = self.pm.get_all_passwords()
            self.list_title_label.configure(text=f"Mots de passe enregistrés ({len(passwords)})")

        if not passwords:
            ctk.CTkLabel(
                self.scroll_frame,
                text="Aucun mot de passe trouvé." if search_query else "Aucun mot de passe enregistré.",
                font=("Arial", 12),
                text_color=PALETTE["TEXT_SECONDARY"],
            ).pack(pady=20)
            return

        for index, (pwd_id, site, username, encrypted_pwd, note) in enumerate(passwords):
            self.create_password_row(pwd_id, site, username, encrypted_pwd, note, index % 2 == 1)

        # Force l'exécution de tous les draw() en attente (CTkButton renders images via after_idle)
        self.update_idletasks()
        self.scroll_frame._parent_canvas.yview_moveto(0)

    def create_password_row(self, pwd_id, site, username, encrypted_pwd, note, is_odd_row):
        """Crée une ligne de mot de passe."""
        bg_color = PALETTE["ROW_ODD_BG"] if is_odd_row else PALETTE["ROW_EVEN_BG"]
        hover_color = PALETTE["SECURITY_HOVER"]

        row_frame = ctk.CTkFrame(self.scroll_frame, corner_radius=8, fg_color=bg_color)
        row_frame.pack(fill="x", pady=2, padx=5)

        info_container = ctk.CTkFrame(row_frame, fg_color="transparent", cursor="hand2")
        info_container.pack(side="left", fill="both", expand=True)

        site_label = ctk.CTkLabel(info_container, text=site, font=("Arial", 12, "bold"), width=100, anchor="w")
        site_label.pack(side="left", padx=(5, 5), pady=10)

        user_label = ctk.CTkLabel(info_container, text=f"👤 {username}", font=("Arial", 10),
                                   width=90, text_color=PALETTE["TEXT_SECONDARY"], anchor="w")
        user_label.pack(side="left", padx=(0, 5), pady=10)

        pwd_note_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        pwd_note_frame.pack(side="left", padx=(0, 5))

        is_visible = pwd_id in self.visible_password_ids
        if is_visible:
            try:
                pwd_txt = f"🔓 {self.pm.decrypt(encrypted_pwd)}"
                pwd_color = PALETTE["TEXT_PRIMARY"]
            except Exception:
                pwd_txt, pwd_color = "❌ Erreur Pwd", PALETTE["TEXT_ERROR"]
        else:
            pwd_txt, pwd_color = "🔒 ********", PALETTE["TEXT_SECONDARY"]

        password_label = ctk.CTkLabel(pwd_note_frame, text=pwd_txt, font=("Arial", 10),
                                       width=120, text_color=pwd_color, anchor="w")
        password_label.pack(anchor="w")

        note_label = ctk.CTkLabel(pwd_note_frame, text=f" {note}" if note else " (Pas de note)",
                                   font=("Arial", 9), width=150, text_color=PALETTE["TEXT_SECONDARY"], anchor="w")
        note_label.pack(anchor="w", pady=(2, 0))

        def on_info_click(event):
            self.edit_password(pwd_id, site, username, encrypted_pwd, note)

        def on_info_enter(event):
            info_container.configure(fg_color=hover_color)
            pwd_note_frame.configure(fg_color=hover_color)

        def on_info_leave(event):
            info_container.configure(fg_color="transparent")
            pwd_note_frame.configure(fg_color="transparent")

        info_widgets = (info_container, site_label, user_label, pwd_note_frame, password_label, note_label)
        for widget in info_widgets:
            widget.bind("<Button-1>", on_info_click)
            widget.bind("<Enter>", on_info_enter)
            widget.bind("<Leave>", on_info_leave)

        button_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=10)

        # Tooltip ancré sur button_frame : s'affiche juste à sa gauche
        for widget in info_widgets:
            ToolTip(widget, "Modifier ce mot de passe", anchor=button_frame)

        def toggle_password():
            self.update_activity()
            if pwd_id in self.visible_password_ids:
                self.visible_password_ids.remove(pwd_id)
                password_label.configure(text="🔒 ********", text_color=PALETTE["TEXT_SECONDARY"])
                show_btn.configure(text=self._icon("eye"))
            else:
                self.visible_password_ids.add(pwd_id)
                try:
                    password_label.configure(text=f"🔓 {self.pm.decrypt(encrypted_pwd)}",
                                             text_color=PALETTE["TEXT_PRIMARY"])
                except Exception:
                    password_label.configure(text="❌ Erreur Pwd", text_color=PALETTE["TEXT_ERROR"])
                show_btn.configure(text=self._icon("eye_slash"))
            self.show_all_passwords = False
            self.toggle_all_button.configure(text="Afficher tout les MdP", image=None)

        show_btn = ctk.CTkButton(button_frame,
                                  text=self._icon("eye_slash") if is_visible else self._icon("eye"),
                                  font=self.fa_font, command=toggle_password,
                                  text_color=PALETTE["ICON_EYE"],
                                  width=32, height=28,
                                  fg_color=PALETTE["UTILITY_FG"], hover_color=PALETTE["UTILITY_HOVER"])
        show_btn.pack(side="left", padx=2)
        ToolTip(show_btn, "Afficher/Masquer le mot de passe")

        user_copy_btn = ctk.CTkButton(button_frame, text=self._icon("user"), font=self.fa_font,
                                       text_color=PALETTE["ICON_USER"],
                                       width=32, height=28,
                                       fg_color=PALETTE["SECONDARY_FG"], hover_color=PALETTE["SECONDARY_HOVER"])
        user_copy_btn.configure(command=lambda btn=user_copy_btn: self.copy_text_to_clipboard(username, btn=btn))
        user_copy_btn.pack(side="left", padx=2)
        ToolTip(user_copy_btn, "Copier l'utilisateur")

        pwd_copy_btn = ctk.CTkButton(button_frame, text=self._icon("key"), font=self.fa_font,
                                      text_color=PALETTE["ICON_KEY"],
                                      width=32, height=28,
                                      fg_color=PALETTE["SECONDARY_FG"], hover_color=PALETTE["SECONDARY_HOVER"])
        pwd_copy_btn.configure(command=lambda btn=pwd_copy_btn: self.copy_password_to_clipboard(encrypted_pwd, btn=btn))
        pwd_copy_btn.pack(side="left", padx=2)
        ToolTip(pwd_copy_btn, "Copier le mot de passe")

        delete_btn = ctk.CTkButton(button_frame, text=self._icon("trash"), font=self.fa_font,
                                    text_color=PALETTE["ICON_TRASH"],
                                    width=32, height=28,
                                    fg_color=PALETTE["DANGER_FG"], hover_color=PALETTE["DANGER_HOVER"],
                                    command=lambda: self.delete_password(pwd_id))
        delete_btn.pack(side="left", padx=2)
        ToolTip(delete_btn, "Supprimer ce mot de passe")


if __name__ == "__main__":
    app = PassManagerApp()
    app.mainloop()
