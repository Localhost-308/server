# app/services/user_service.py

from app.models.user import User
from app.database import db
from app.services.encryption_service import EncryptionService
from app.database.sqlite import get_sqlite_session
from sqlalchemy.exc import SQLAlchemyError

class UserService:
    @staticmethod
    def create_user(first_name, last_name, email, password, cargo, company_id):
        """
        Cria um novo usuário, criptografa dados sensíveis e salva chave no SQLite.
        """

        # 1. Gerar chave pública e privada
        private_key_pem, public_key_pem = EncryptionService.generate_keys()

        # 2. Criptografar dados sensíveis usando a chave pública
        encrypted_first_name = EncryptionService.encrypt(public_key_pem, first_name)
        encrypted_last_name = EncryptionService.encrypt(public_key_pem, last_name)
        encrypted_email = EncryptionService.encrypt(public_key_pem, email)

        # 3. Criar novo usuário
        new_user = User(
            first_name=encrypted_first_name,
            last_name=encrypted_last_name,
            email=encrypted_email,
            password=password,  # A senha já deve estar com bcrypt no controller
            cargo=cargo,
            company_id=company_id
        )

        try:
            db.session.add(new_user)
            db.session.commit()

            # 4. Salvar a chave privada no SQLite
            sqlite_session = get_sqlite_session()
            sqlite_session.execute(
                "INSERT INTO user_keys (user_id, private_key) VALUES (?, ?)",
                (new_user.id, private_key_pem)
            )
            sqlite_session.commit()
            sqlite_session.close()

            return new_user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_user(user_id):
        """
        Deleta o usuário no Postgres e remove a chave no SQLite.
        """
        user = User.query.get(user_id)
        if not user:
            return None

        try:
            db.session.delete(user)
            db.session.commit()

            sqlite_session = get_sqlite_session()
            sqlite_session.execute(
                "DELETE FROM user_keys WHERE user_id = ?",
                (user_id,)
            )
            sqlite_session.commit()
            sqlite_session.close()

            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
