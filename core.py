import os
import zipfile
from pathlib import Path
from typing import Iterator, Literal

from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Protocol.KDF import scrypt

from helpers import File, path_size

CHUNK_SIZE = 1024 * 1024  # 1 MiB


class Key:
    def __init__(self, password: str) -> None:
        # Key that will be used to encrypt file data
        self.data_key = os.urandom(32)

        # Key that will be used to encrypt the data kay
        key, self.salt = key_derive(password)

        cipher = ChaCha20_Poly1305.new(key=key)
        self.data_key_encrypted = cipher.encrypt(self.data_key)
        self.data_key_tag = cipher.digest()
        self.data_key_nonce = cipher.nonce


def decrypt_key(
    encrypted_key: bytes,
    salt: bytes,
    nonce: bytes,
    tag: bytes,
    password: str,
) -> bytes | Literal[False]:
    """Try to decrypt and verify an encrypted key. Returns False if failed."""
    key, _ = key_derive(password, salt)
    cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
    try:
        decrypted_key = cipher.decrypt_and_verify(encrypted_key, tag)
    except (ValueError, KeyError):
        return False

    return decrypted_key


def key_derive(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    if not salt:
        salt = os.urandom(16)  # 16 cryptographically secure random bytes
    key = scrypt(password, str(salt), key_len=32, N=2**20, r=8, p=1)
    if not isinstance(key, bytes):
        raise TypeError
    return key, salt


def encrypt_files(files: dict[File, Path], password: str) -> Iterator:
    files_processed: int = 0
    for file_in, file_out in files.items():
        header: bytes = b""
        archive_path: Path | None = None
        perfile_progress: int = 0
        display_name: str = file_in.path.name
        try:
            yield files_processed + perfile_progress, display_name
            key = Key(password)
            cipher = ChaCha20_Poly1305.new(key=key.data_key)
            tag_placeholder = os.urandom(16)

            # Build header
            for i in (
                key.salt,  # 16 bytes
                key.data_key_nonce,  # 12 bytes
                key.data_key_tag,  # 16 bytes
                key.data_key_encrypted,  # 32 bytes
                cipher.nonce,  # 12 bytes
                tag_placeholder,  # 16 bytes
            ):
                header += i  # = 104 bytes

            if file_in.path.is_dir():
                archive_path = file_out.with_suffix(".tmp")
                zip_folder(file_in.path, archive_path)
                file_in = File(archive_path, path_size(archive_path))

            file_out = Path(f"{file_out}.tmp")
            with open(file_in.path, "rb") as f_in, open(file_out, "wb") as f_out:
                f_out.write(header)
                while chunk := f_in.read(CHUNK_SIZE):  # Walrus
                    encrypted_chunk = cipher.encrypt(chunk)
                    f_out.write(encrypted_chunk)
                    perfile_progress += len(chunk)
                    try:
                        yield (
                            files_processed + perfile_progress / file_in.size,
                            display_name,
                        )
                    except ZeroDivisionError:  # Empty file or dir
                        pass

                # Get MAC tag of all the data passed through the encryptor
                tag = cipher.digest()
                # Place file handle at the begining of the tag placeholder
                f_out.seek(88)
                f_out.write(tag)  # Overwrite placeholder with the actual tag
            file_out.replace(file_out.with_suffix(""))  # Remove .tmp suffix

        # Something "unexpected" happened
        except Exception as err:
            # Delete tmp file if it exists
            if file_out.exists():
                file_out.unlink()
            yield err, display_name

        # Delete tmp zip archive in any case
        finally:
            if archive_path:
                archive_path.unlink()

        files_processed += 1


def decrypt_files(files: dict[File, Path], password: str) -> Iterator:
    files_processed: int = 0
    for file_in, file_out in files.items():
        perfile_progress: int = 0
        display_name: str = file_in.path.name
        try:
            yield files_processed + perfile_progress, display_name
            file_out = Path(f"{file_out}.tmp")

            with open(file_in.path, "rb") as f_in, open(file_out, "wb") as f_out:
                header = {
                    "key_salt": f_in.read(16),
                    "key_nonce": f_in.read(12),
                    "key_tag": f_in.read(16),
                    "key_encrypted": f_in.read(32),
                    "nonce": f_in.read(12),
                    "tag": f_in.read(16),
                }
                if not (
                    key := decrypt_key(
                        header["key_encrypted"],
                        header["key_salt"],
                        header["key_nonce"],
                        header["key_tag"],
                        password,
                    )
                ):
                    raise KeyError

                cipher = ChaCha20_Poly1305.new(key=key, nonce=header["nonce"])
                while chunk := f_in.read(CHUNK_SIZE):  # Walrus
                    decrypted_chunk = cipher.decrypt(chunk)
                    f_out.write(decrypted_chunk)
                    perfile_progress += len(chunk)
                    yield (
                        files_processed + perfile_progress / file_in.size,
                        display_name,
                    )

                cipher.verify(header["tag"])

            file_out.replace(file_out.with_suffix(""))  # Remove .tmp suffix

        # Decryption failed due to incorrect password or corrupt data
        except (ValueError, KeyError):
            # Delete tmp file if it exists
            if file_out.exists():
                file_out.unlink()
            yield False, file_in

        # Something "unexpected" happened
        except Exception as err:
            # Delete tmp file if it exists
            if file_out.exists():
                file_out.unlink()
            yield err, display_name

        files_processed += 1


def zip_folder(dir_path: Path, archive_path: Path) -> None:
    """Zip folder into archive (archive_path) without compression."""
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_STORED) as archive:
        for path in dir_path.rglob("*"):
            if path == archive_path:
                continue
            archive.write(path, path.relative_to(dir_path))
