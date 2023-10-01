import multiprocessing as mp
import secrets
import sys
import webbrowser
from pathlib import Path
from typing import Any

import dearpygui.dearpygui as dpg
import dearpygui_extend as dpge

import theme
from core import decrypt_files, encrypt_files
from helpers import File, human_readable_size, path_size, resource_path

# Modes: "_enc" = encryption, "_dec" = decryption


def load_wordlist() -> list[str]:
    path = resource_path("resources/wordlist.txt")
    with open(path, "r", encoding="utf-8") as file:
        wordlist = file.read().splitlines()
    return wordlist


def main() -> None:
    App().setup_and_spawn_window()


class App:
    def __init__(self) -> None:
        self.files_in: dict[str, list[File]] = {"_enc": [], "_dec": []}
        self.popup: Popup | None = None
        self.version: str = "1.1"
        self.project_url: str = "https://github.com/70sh1/Vaultea"

    def setup_and_spawn_window(
        self, filebrowser_args: tuple[str, bool, Any] | None = None
    ) -> None:
        dpg.create_context()
        dpg.setup_dearpygui()

        theme.load_themes()
        theme.load_icons()
        theme.load_fonts()

        icon = resource_path("resources/icons/Vaultea.ico")
        if not filebrowser_args:
            viewport_height = 395 if PLATFORM == "linux" else 435
            dpg.create_viewport(
                title="Vaultea",
                large_icon=str(icon),
                small_icon=str(icon),
                width=450,
                height=viewport_height,
                x_pos=735,
                y_pos=320,
            )
            self.main_window()
        else:
            _, output, _ = filebrowser_args
            title = "Select folder..." if output else "Select files..."
            dpg.create_viewport(
                title=title,
                large_icon=str(icon),
                small_icon=str(icon),
                width=750,
                height=555,
                x_pos=585,
                y_pos=260,
            )
            self.filebrowser_window(*filebrowser_args)

        dpg.show_viewport()

        dpg.bind_font("JetBrainsMono")
        dpg.bind_theme("main_theme")

        # dpg.show_style_editor()
        # dpg.show_item_registry()
        # dpg.show_metrics()

        # Main loop of a window
        while dpg.is_dearpygui_running():
            self.update_current_popup_width()
            dpg.render_dearpygui_frame()

    def update_current_popup_width(self):
        if self.popup:
            self.popup.update_width()

    def main_window(self) -> None:
        """Populates main window with widgets."""
        with dpg.window(tag="main_window", no_title_bar=True):
            with dpg.tab_bar():
                # Encrypt tab
                with dpg.tab(label="Encrypt", tag="encrypt_tab"):
                    dpg.add_spacer()
                    dpg.add_text("Input:")
                    dpg.add_collapsing_header(
                        label="No files",
                        tag="input_header_enc",
                    )
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Add",
                            tag="add_files_button_enc",
                            width=-80,
                            callback=self.add_files,
                        )
                        dpg.add_button(
                            label="Clear",
                            tag="clear_button_enc",
                            callback=self.clear_files,
                            width=-1,
                        )

                    dpg.add_spacer()
                    dpg.add_separator()
                    dpg.add_spacer()

                    dpg.add_text("Password:")
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Generate", width=-150, callback=self.passgen_callback
                        )
                        dpg.add_button(
                            label="Copy",
                            tag="pass_copy",
                            width=-80,
                            callback=self.copy_password,
                        )
                        dpg.add_button(
                            label="Show",
                            tag="pass_show_enc",
                            width=-1,
                            callback=self.show_password,
                        )
                    dpg.add_spacer()
                    dpg.add_input_text(
                        width=-1,
                        tag="pass_input_enc",
                        password=True,
                        hint="Password",
                    )
                    dpg.add_input_text(
                        width=-1,
                        tag="confirm_pass_input",
                        password=True,
                        hint="Confirm password",
                    )

                    dpg.add_spacer()
                    dpg.add_separator()
                    dpg.add_spacer()

                    dpg.add_text("Output folder:")
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(
                            hint="default",
                            tag="output_dir_enc",
                            width=-65,
                        )
                        dpg.add_button(
                            label="Browse",
                            tag="output_button_enc",
                            width=-1,
                            callback=self.select_output_dir,
                        )

                    dpg.add_spacer()
                    dpg.add_separator()
                    dpg.add_spacer()

                    dpg.add_button(
                        label="Encrypt",
                        tag="encrypt_button",
                        width=-1,
                        height=75,
                        enabled=False,
                        callback=self.encrypt_callback,
                    )
                    with dpg.tooltip(
                        parent="encrypt_button", tag="encrypt_button_disabled_tooltip"
                    ):
                        dpg.add_text(
                            "Please add file(s) and provide/generate a password.",
                            wrap=310,
                        )
                    with dpg.tooltip(
                        parent="encrypt_button",
                        tag="passwords_do_not_match_tooltip",
                        show=False,
                    ):
                        dpg.add_text(
                            "Passwords do not match.",
                            wrap=310,
                        )

                # Decrypt tab
                with dpg.tab(label="Decrypt", tag="decrypt_tab"):
                    dpg.add_spacer()

                    dpg.add_text("Input:")
                    dpg.add_collapsing_header(
                        label="No files",
                        tag="input_header_dec",
                    )
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Add",
                            tag="add_files_button_dec",
                            width=-80,
                            callback=self.add_files,
                        )
                        dpg.add_button(
                            label="Clear",
                            tag="clear_button_dec",
                            callback=self.clear_files,
                            width=-1,
                        )

                    dpg.add_spacer()
                    dpg.add_separator()
                    dpg.add_spacer()

                    dpg.add_text("Password:")
                    dpg.add_button(
                        label="Show",
                        tag="pass_show_dec",
                        width=-1,
                        callback=self.show_password,
                    )
                    dpg.add_spacer()
                    dpg.add_input_text(
                        width=-1,
                        tag="pass_input_dec",
                        password=True,
                        hint="Password",
                    )

                    dpg.add_spacer()
                    dpg.add_separator()
                    dpg.add_spacer()

                    dpg.add_text("Output folder:")
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(
                            hint="default",
                            tag="output_dir_dec",
                            width=-65,
                        )
                        dpg.add_button(
                            label="Browse",
                            tag="output_button_dec",
                            width=-1,
                            callback=self.select_output_dir,
                        )

                    dpg.add_spacer()
                    dpg.add_separator()
                    dpg.add_spacer(height=26)

                    dpg.add_button(
                        label="Decrypt",
                        tag="decrypt_button",
                        width=-1,
                        height=75,
                        enabled=False,
                        callback=self.decrypt_callback,
                    )
                    with dpg.tooltip(
                        parent="decrypt_button", tag="decrypt_button_disabled_tooltip"
                    ):
                        dpg.add_text(
                            "Please add file(s).",
                            wrap=310,
                        )

                dpg.add_tab_button(label="Reset", callback=self.reset)

                # About tab
                with dpg.tab(label="About", tag="about_tab"):
                    dpg.add_text(f"v{self.version}")
                    dpg.add_button(
                        tag="source_button",
                        label="Source",
                        callback=lambda: webbrowser.open(self.project_url),
                    )
                    with dpg.tooltip(label=self.project_url, parent="source_button"):
                        dpg.add_text(self.project_url)

                # dpg.add_tab_button(label="Debug", callback=self.debug)

        with dpg.item_handler_registry(tag="main_registry"):
            dpg.add_item_edited_handler(callback=self.update_encrypt_button_state)
            dpg.add_item_resize_handler(callback=self.update_current_popup_width)
        dpg.bind_item_handler_registry("pass_input_enc", "main_registry")
        dpg.bind_item_handler_registry("confirm_pass_input", "main_registry")
        dpg.bind_item_handler_registry("main_window", "main_registry")
        dpg.set_primary_window("main_window", True)

    # def debug(self):
    #     pass

    def filebrowser_window(
        self, mode: str, output_select: bool, connection: Any
    ) -> None:
        allow_multi_selection = not output_select
        filetype_filter = None
        filetype_filter_default = 0

        if not output_select:
            if mode == "_dec":
                filetype_filter = [
                    {"label": "All files", "formats": ["*"]},
                    {"label": "Encrypted file", "formats": ["teax"]},
                ]
                filetype_filter_default = 1
        else:
            filetype_filter = [{"label": "Folders", "formats": ["*"]}]

        with dpg.window(tag="fb"):
            dpge.add_file_browser(
                dirs_only=output_select,
                allow_multi_selection=allow_multi_selection,
                collapse_sequences=False,
                collapse_sequences_checkbox=False,
                show_hidden_files=True,
                path_input_style=0,
                expand_sequences_on_callback=False,
                show_ok_cancel=True,
                filetype_filter=filetype_filter,
                filetype_filter_default=filetype_filter_default,
                icon_size=0,
                add_filename_tooltip=False,
                allow_drag=False,
                callback=lambda _, paths, cancel_pressed: self.send_paths(
                    paths, cancel_pressed, connection
                ),
            )
        dpg.set_primary_window("fb", True)

    @staticmethod
    def send_paths(paths: list, cancel_pressed: bool, connection: Any) -> None:
        if cancel_pressed:
            connection.send(None)
        else:
            connection.send(paths)

        connection.close()

    def filebrowser(self, mode: str, output_select: bool = False) -> list[Path]:
        paths = []
        read_conn, write_conn = mp.Pipe(duplex=False)
        filebrowser_args = mode, output_select, write_conn
        file_browser_process = mp.Process(
            target=self.setup_and_spawn_window, args=(filebrowser_args,), daemon=True
        )

        file_browser_process.start()
        while file_browser_process.is_alive():
            if read_conn.poll():
                paths = read_conn.recv()
                file_browser_process.terminate()

        file_browser_process.join()
        write_conn.close()
        read_conn.close()

        if paths:
            paths = [Path(path) for path in paths]  # Convert paths to pathlib Path

        return paths

    def add_files(self, sender: str) -> None:
        dpg.disable_item(sender)
        self.create_filepick_overlay()

        mode = sender[-4:]
        if paths := self.filebrowser(mode, output_select=False):
            self.update_files_list(mode, paths)

        dpg.delete_item("filepick_overlay")
        dpg.enable_item(sender)

        self.update_encrypt_button_state()
        self.update_decrypt_button_state()

    def select_output_dir(self, sender: str) -> None:
        dpg.disable_item(sender)
        self.create_filepick_overlay()

        mode = sender[-4:]
        if path := self.filebrowser(mode, output_select=True):
            path = path[0]
            dpg.set_value("output_dir" + mode, path)
        else:
            dpg.set_value("output_dir" + mode, "")

        dpg.delete_item("filepick_overlay")
        dpg.enable_item(sender)

    @staticmethod
    def create_filepick_overlay() -> None:
        with dpg.window(
            modal=True,
            tag="filepick_overlay",
            no_title_bar=True,
            no_move=True,
            no_resize=True,
            no_close=True,
            autosize=True,
            no_open_over_existing_popup=False,
        ):
            dpg.add_loading_indicator(radius=10, circle_count=4, speed=0.6)
        dpg.bind_item_theme("filepick_overlay", "filepick_overlay_theme")

    def reset(self) -> None:
        modes = ["_enc", "_dec"]
        for mode in modes:
            self.clear_files(mode)
            dpg.set_value("pass_input" + mode, "")
            dpg.configure_item("input_header" + mode, default_open=False)
            dpg.set_value("output_dir" + mode, "")
            self.hide_password(mode)
        dpg.set_value("confirm_pass_input", "")

    def clear_files(self, sender: str) -> None:
        mode = sender[-4:]
        self.files_in[mode] = []
        self.update_header(self.files_in, mode)
        self.update_encrypt_button_state()
        self.update_decrypt_button_state()

    def validate_old_paths(self, mode: str) -> bool:
        """Check that previously added files still exist.
        Remove invalid paths and show notice(s) otherwise."""
        messages = []
        valid_paths = []

        for file in self.files_in[mode]:
            if file.path.exists():
                valid_paths.append(file)
            else:
                messages.append(
                    f"File {file.path} not found. Perhaps it was renamed, moved or deleted."
                    " It is now removed from the input list."
                )

        self.files_in[mode] = valid_paths

        if messages:
            self.update_header(self.files_in, mode)
            self.popup = Popup(
                title="Error",
                messages=messages,
                app=self,
            )
            self.popup.notice()
            return False

        return True

    def update_files_list(self, mode: str, paths: list[Path]) -> None:
        too_big: list[tuple[str, int]] = []
        not_unique: list[str] = []
        doesnt_exist: list[str] = []
        messages: list[str] = []

        if mode == "_dec":
            # The flag indicates that paths list contained folders,
            # which are not allowed in decryption mode.
            folder_flag, paths = self.filter_dirs(paths)

            if folder_flag:
                messages.append("Cannot add folders in decryption mode.")

        for path in paths:
            # Try to get filesize. Also checks if file exists.
            try:
                size = path_size(path)
            except FileNotFoundError:
                doesnt_exist.append(path.name)
                continue

            # Сheck if file is too big.
            if size > MAX_FILESIZE:
                file_info = path.name, size
                too_big.append(file_info)
                continue

            # Сheck if filename is unique.
            currently_added = self.files_in[mode]
            for file in currently_added:
                if file.path.name == path.name:
                    not_unique.append(path.name)
                    break
            else:
                self.files_in[mode].append(File(path, size))

        for i in too_big:
            messages.append(
                f"File/folder '{i[0]}' is too big {human_readable_size(i[1])}."
                "\n\nThe limit is 256 GiB per file/folder."
            )
        for i in not_unique:
            messages.append(
                f"File/folder with name '{i}' is already added."
                " Filenames should be unique.\n\nPlease, consider renaming."
            )
        for i in doesnt_exist:
            messages.append(f"File/folder '{i}' not found.")

        if messages:
            self.popup = Popup(
                title="Warning",
                messages=messages,
                app=self,
            )
            self.popup.notice()

        self.update_header(self.files_in, mode)

    def filter_dirs(self, paths: list[Path]) -> tuple[bool, list[Path]]:
        no_dirs = [path for path in paths if not path.is_dir()]
        return (paths != no_dirs), no_dirs

    @staticmethod
    def update_header(paths: dict[str, list[File]], mode: str) -> None:
        """Repopulate input header with filenames and path tooltips."""
        dpg.delete_item("input_header" + mode, children_only=True)
        total_size = 0
        file_count = 0
        dir_count = 0
        for file in paths[mode]:
            dpg.add_text(file.path.name, wrap=0, parent="input_header" + mode)
            total_size += file.size
            with dpg.tooltip(parent=dpg.last_item()):
                dpg.add_text(str(file.path), wrap=350)

            if file.path.is_file():
                file_count += 1
            elif file.path.is_dir():
                dir_count += 1

        readable_size = human_readable_size(total_size)

        # There is high chance the following part can be written better and more consice
        if dir_count == 1:
            dir_str = "1 folder"
        elif dir_count > 1:
            dir_str = f"{dir_count} folders"
        else:
            dir_str = ""

        if file_count == 1:
            file_str = "1 file"
        elif file_count > 1:
            file_str = f"{file_count} files"
        else:
            file_str = ""

        sep = ", " if dir_str and file_str else ""

        header_label = f"{file_str}{sep}{dir_str}"

        if header_label:
            header_label = f"{header_label} {readable_size}"
        else:
            header_label = "No files"

        dpg.set_item_label("input_header" + mode, label=header_label)

    def update_encrypt_button_state(self) -> None:
        pass_value = dpg.get_value("pass_input_enc")
        confirm_pass_value = dpg.get_value("confirm_pass_input")
        if (pass_value or confirm_pass_value) and self.files_in["_enc"]:
            if pass_value == confirm_pass_value:
                dpg.enable_item("encrypt_button")
                dpg.hide_item("encrypt_button_disabled_tooltip")
                dpg.hide_item("passwords_do_not_match_tooltip")
            else:
                dpg.disable_item("encrypt_button")
                dpg.hide_item("encrypt_button_disabled_tooltip")
                dpg.show_item("passwords_do_not_match_tooltip")
        else:
            dpg.disable_item("encrypt_button")
            dpg.show_item("encrypt_button_disabled_tooltip")
            dpg.hide_item("passwords_do_not_match_tooltip")

    def update_decrypt_button_state(self) -> None:
        if self.files_in["_dec"]:
            dpg.enable_item("decrypt_button")
            dpg.hide_item("decrypt_button_disabled_tooltip")
        else:
            dpg.disable_item("decrypt_button")
            dpg.show_item("decrypt_button_disabled_tooltip")

    def show_password(self, sender: str) -> None:
        mode = sender[-4:]
        dpg.configure_item("pass_input" + mode, password=False)
        if mode == "_enc":
            dpg.configure_item("confirm_pass_input", password=False)
        dpg.configure_item(
            "pass_show" + mode, label="Hide", callback=self.hide_password
        )

    def hide_password(self, sender: str) -> None:
        mode = sender[-4:]
        dpg.configure_item("pass_input" + mode, password=True)
        if mode == "_enc":
            dpg.configure_item("confirm_pass_input", password=True)
        dpg.configure_item(
            "pass_show" + mode, label="Show", callback=self.show_password
        )

    def passgen_callback(self) -> None:
        passphrase = self.generate_passphrase(6)
        dpg.set_value("pass_input_enc", passphrase)
        dpg.set_value("confirm_pass_input", passphrase)
        self.update_encrypt_button_state()

    @staticmethod
    def generate_passphrase(length: int) -> str:
        return "-".join([secrets.choice(WORDLIST) for _ in range(length)])

    @staticmethod
    def copy_password() -> None:
        dpg.set_clipboard_text(dpg.get_value("pass_input_enc"))

    ###############################################################################

    def encrypt_callback(self) -> None:
        dpg.disable_item("encrypt_button")
        output_dir = dpg.get_value("output_dir_enc")
        self.preprocess_files(self.files_in, "_enc", output_dir)

    def decrypt_callback(self) -> None:
        dpg.disable_item("decrypt_button")
        output_dir = dpg.get_value("output_dir_dec")
        self.preprocess_files(self.files_in, "_dec", output_dir)

    def preprocess_files(
        self, files_in: dict[str, list[File]], mode: str, output_dir: Path | None
    ) -> None:
        if not self.validate_old_paths(mode):
            return

        existing_files: list[Path] = []

        # Validate given output path
        if output_dir:
            output_dir = Path(output_dir)
            if not output_dir.is_dir():
                self.popup = Popup(
                    title="Error",
                    messages=["Given output path is invalid."],
                    app=self,
                )
                self.popup.notice()
                return

        self.files_in_out: dict[File, Path] = {}

        # Construct file_out path from input file path
        for file in files_in[mode]:
            file_out = self.derive_path(file.path, mode, output_dir)
            self.files_in_out[file] = file_out
            if file_out.exists():
                existing_files.append(file_out)

        self.mode = mode

        if existing_files:
            self.popup = Popup(
                title="Warning",
                messages=["The following files already exist.\n\nOverwrite?"],
                tag="overwrite_dialog_popup",
                app=self,
            )
            self.popup.overwrite_dialog(existing_files)

            return

        self.process_files(self.files_in_out, self.mode)

    def derive_path(self, path: Path, mode: str, output_dir: Path | None) -> Path:
        if mode == "_enc":
            if path.is_dir():
                file_out = Path(f"{path}.zip.teax")
            else:
                file_out = Path(f"{path}.teax")

        elif mode == "_dec":
            if str(path).endswith(".teax"):
                file_out = path.with_suffix("")  # Remove .teax suffix
            else:
                file_out = path

        else:
            raise RuntimeError

        if output_dir:
            file_out = output_dir / file_out.name

        return file_out

    def overwrite_selection(self, sender: str) -> None:
        self.popup = None
        dpg.delete_item("overwrite_dialog_popup")
        if sender.endswith("confirm"):
            self.process_files(self.files_in_out, self.mode)
        else:
            self.update_encrypt_button_state()
            self.update_decrypt_button_state()

    def process_files(self, files: dict[File, Path], mode: str) -> None:
        dpg.configure_viewport("Vaultea", disable_close=True)

        password = dpg.get_value("pass_input" + mode)

        if mode == "_enc":
            processor = encrypt_files
            message = "Encrypting"
        else:
            processor = decrypt_files
            message = "Decrypting"

        self.popup = Popup(
            title="Processing",
            messages=["Preparing..."],
            tag="progress_bar_popup",
            app=self,
        )
        self.popup.progress_bar()

        skipped_files: list[File] = []
        max_progress = len(files)
        for result in processor(files, password):
            if type(result[0]) in (int, float, complex):
                progress, filename = result
                dpg.set_value("popup_text", f"{message} '{filename}'...")
                dpg.set_value("progress_bar", progress / max_progress)
            elif result[0] is False:
                failed_file = result[1]
                skipped_files.append(failed_file)
            else:
                dpg.delete_item("progress_bar_popup")
                err = repr(result[0])
                failed_file = result[1]
                self.popup = Popup(
                    title="Error",
                    messages=[
                        f"An error occured during the processing of '{failed_file}'"
                        f", all future operations aborted.\n\n{err}"
                    ],
                    app=self,
                )
                self.popup.notice()
                dpg.configure_viewport("Vaultea", disable_close=False)
                return

        dpg.configure_viewport("Vaultea", disable_close=False)
        dpg.set_value("progress_bar", 1)
        dpg.set_value("popup_text", "Done.")
        dpg.delete_item("pb_loading_indicator")
        dpg.add_image("checkmark", parent="pb_row")
        dpg.enable_item("progress_popup_close_button")

        self.files_in[self.mode] = skipped_files
        self.update_header(self.files_in, self.mode)

        if skipped_files:
            dpg.delete_item(self.popup.tag)
            self.popup = Popup(
                title="Error",
                messages=[
                    "Some of the files were skipped due to one of the following "
                    "reasons:\n1. Incorrect password\n2. Corrupt/modified content\n"
                    "3. Not an encrypted file"
                ],
                app=self,
            )
            self.popup.display_skipped_files(skipped_files)
            return


class Popup:
    """Create base popup window.

    Some methods in this class represent popup type which
    can be called later to add specific elements to the base popup window."""

    def __init__(
        self, title: str, messages: list[str], app: App, tag: str = "default_popup_tag"
    ) -> None:
        self.label = title
        self.tag = tag
        self.messages_iter = iter(messages)
        self.app = app
        with dpg.window(
            label=self.label,
            tag=self.tag,
            modal=True,
            no_move=True,
            no_resize=True,
            no_close=True,
            no_open_over_existing_popup=False,
            pos=[0, 125],
        ):
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=-1)
                dpg.add_text(next(self.messages_iter), wrap=0, tag="popup_text")

        dpg.bind_item_theme(self.tag, "popup_theme")

    def close(self) -> None:
        self.app.popup = None
        dpg.delete_item(self.tag)

        self.app.update_decrypt_button_state()
        self.app.update_encrypt_button_state()

    def display_skipped_files(self, skipped_files: list[File]) -> None:
        with dpg.collapsing_header(
            label=f"({len(skipped_files)})",
            parent=self.tag,
        ):
            for file in skipped_files:
                dpg.add_text(file.path.name, wrap=0)

        dpg.add_button(
            parent=self.tag,
            label="Close",
            width=-1,
            callback=self.close,
        )
        self.update_height()

    def notice(self) -> None:
        dpg.add_button(
            parent=self.tag,
            label="OK",
            width=-1,
            callback=self.next_message,
        )
        self.update_height()

    def next_message(self) -> None:
        message = next(self.messages_iter, None)
        if not message:
            self.close()
            return

        dpg.set_value("popup_text", message)
        self.update_height()

    def overwrite_dialog(self, existing_files: list[Path]) -> None:
        dpg.add_button(
            label="Yes",
            tag="overwrite_confirm",
            width=-1,
            parent=self.tag,
            callback=self.app.overwrite_selection,
        )
        dpg.add_button(
            label="No",
            tag="overwrite_cancel",
            width=-1,
            parent=self.tag,
            callback=self.app.overwrite_selection,
        )
        with dpg.collapsing_header(
            label=f"({len(existing_files)})",
            parent=self.tag,
            before="overwrite_confirm",
        ):
            for file in existing_files:
                dpg.add_text(file.name, wrap=0)
        self.update_height()

    def progress_bar(self) -> None:
        with dpg.group(tag="pb_row", parent=self.tag, horizontal=True):
            dpg.add_progress_bar(tag="progress_bar", width=-25)
            dpg.add_loading_indicator(tag="pb_loading_indicator", radius=1.3, style=1)
        dpg.add_spacer(height=10, parent=self.tag)
        dpg.add_button(
            parent=self.tag,
            label="Close",
            tag="progress_popup_close_button",
            width=-1,
            enabled=False,
            callback=self.close,
        )
        self.update_height()

    def update_width(self) -> None:
        width = dpg.get_viewport_client_width() - 6
        dpg.configure_item(self.tag, width=width)

    def update_height(self) -> None:
        dpg.split_frame()
        dpg.configure_item(self.tag, height=0)


if __name__ == "__main__":
    mp.freeze_support()  # Required for correct filebrowser spawn when run from dist
    mp.set_start_method("spawn")  # Required for filebrowser spawn on linux
    WORDLIST: list[str] = load_wordlist()
    MAX_FILESIZE: int = 524_288**2  # 256 GiB
    PLATFORM = sys.platform
    main()
