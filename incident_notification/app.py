import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from sqlalchemy.orm import sessionmaker

from app.database.sqlite import get_sqlite_session
from app.models import User
from app.services.email_service import send_email
from sqlalchemy import create_engine

from app.services.encryption_service import EncryptionService


class EmailSenderApp:
    def __init__(self, master):
        self.master = master
        master.title("Notificação de Incidente - LGPD")

        # Frame principal
        frame = tk.Frame(master)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Caixa de texto (mensagem)
        self.text_box = ScrolledText(frame, wrap=tk.WORD, width=100, height=40)
        self.text_box.pack(side=tk.LEFT, padx=(0, 10), fill=tk.BOTH, expand=True)
        with open("./incident_notification/mail_message_text.txt", "r") as text:
            self.text_box.insert('1.0', chars=text.read())

        # Lista de e-mails
        self.email_listbox = tk.Listbox(frame, selectmode=tk.EXTENDED, width=40)
        self.email_listbox.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Frame para remetente e senha
        credentials_frame = tk.Frame(master)
        credentials_frame.pack(pady=(10, 0))

        # Campo de e-mail do remetente
        tk.Label(credentials_frame, text="Remetente:").pack(side=tk.LEFT, padx=(0, 5))
        self.sender_email_entry = tk.Entry(credentials_frame, width=30)
        self.sender_email_entry.pack(side=tk.LEFT, padx=(0, 15))

        # Campo de senha
        tk.Label(credentials_frame, text="Senha:").pack(side=tk.LEFT, padx=(0, 5))
        self.sender_password_entry = tk.Entry(credentials_frame, width=30, show="*")
        self.sender_password_entry.pack(side=tk.LEFT)

        # Frame para botões
        button_frame = tk.Frame(master)
        button_frame.pack(pady=(10, 0))

        self.fetch_button = tk.Button(button_frame, text="Obter Emails(DB)", command=self.fetch_emails_from_db)
        self.fetch_button.pack(side=tk.LEFT, padx=5)

        self.import_button = tk.Button(button_frame, text="Importar Emails(File)", command=self.import_emails)
        self.import_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(button_frame, text="Salvar Emails", command=self.save_email_list)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.send_button = tk.Button(button_frame, text="Enviar", command=self.send_messages)
        self.send_button.pack(side=tk.LEFT, padx=5)

    def import_emails(self):
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos de texto", "*.txt")])
        if not file_path:
            return

        try:
            with open(file_path, 'r') as file:
                emails = file.readlines()
            emails = [email.strip() for email in emails if email.strip()]
            self.email_listbox.delete(0, tk.END)  # limpa lista atual
            for email in emails:
                self.email_listbox.insert(tk.END, email)
            messagebox.showinfo("Sucesso", f"{len(emails)} e-mails importados com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar emails:\n{e}")

    def fetch_emails_from_db(self):
        try:
            # Configure conforme suas variáveis de ambiente
            db_user = "postgres"
            db_password = "postgres"
            db_host = "localhost"
            db_port = "5440"
            db_name = "database"

            engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
            Session = sessionmaker(bind=engine)
            session = Session()

            users = session.query(User).all()

            sqlite_session = get_sqlite_session()
            emails = []

            for user in users:
                cursor = sqlite_session.execute(
                    "SELECT private_key FROM user_keys WHERE user_id = ?", (user.id,)
                )
                result = cursor.fetchone()

                if not result:
                    continue

                private_key_pem = result[0]
                try:
                    decrypted_email = EncryptionService.decrypt(private_key_pem, user.email)
                except Exception:
                    continue

                emails.append(decrypted_email)

            self.email_listbox.delete(0, tk.END)
            for email in emails:
                self.email_listbox.insert(tk.END, email)

            session.close()

            messagebox.showinfo("Sucesso", f"{len(emails)} e-mails carregados do banco de dados.")
        except Exception as e:
            messagebox.showerror("Erro ao buscar e-mails", str(e))

    def save_email_list(self):
        emails = self.email_listbox.get(0, tk.END)
        if not emails:
            messagebox.showwarning("Aviso", "A lista de e-mails está vazia.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt")],
            title="Salvar Lista de Emails"
        )

        if not file_path:
            return  # Usuário cancelou

        try:
            with open(file_path, "w") as f:
                for email in emails:
                    f.write(email + "\n")
            messagebox.showinfo("Sucesso", f"Lista de e-mails salva em:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o arquivo:\n{e}")

    def send_messages(self):
        sender = self.sender_email_entry.get()
        password = self.sender_password_entry.get()
        message = self.text_box.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Atenção", "A mensagem está vazia.")
            return

        emails = self.email_listbox.get(0, tk.END)
        if not emails:
            messagebox.showwarning("Atenção", "Nenhum e-mail na lista.")
            return

        for email in emails:
            print(f"Enviando mensagem para {email}.")
            send_email(
                recipient=email,
                subject="Notificação(APENAS UM TESTE - DESCONSIDERE ESTA MENSAGEM)",
                body=message,
                sender=sender,
                password=password
            )
        messagebox.showinfo("Concluído", f"Mensagem enviada para {len(emails)} destinatários.")


if __name__ == "__main__":
    root = tk.Tk()
    app = EmailSenderApp(root)
    root.mainloop()
