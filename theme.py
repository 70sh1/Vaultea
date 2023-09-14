import dearpygui.dearpygui as dpg

import helpers


def load_themes() -> None:
    # Colors
    mint, dark_mint = (39, 124, 90), (29, 93, 68)
    kinda_black = (22, 22, 18)
    blue = (58, 86, 131)
    cool_gray = (75, 111, 170)
    dark_turquoise, turquoise, light_turquoise = (
        (17, 81, 85),
        (20, 97, 102),
        (24, 113, 119),
    )
    earthy_yellow = (217, 174, 100)
    red = (196, 69, 54)
    bg_dim = (37, 37, 38, 200)

    with dpg.theme(tag="main_theme"):
        with dpg.theme_component(dpg.mvAll):
            # Window rounding
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6)

            # Hide window border
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)

            # Main colors
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, kinda_black)
            dpg.add_theme_color(dpg.mvThemeCol_Button, dark_turquoise)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, turquoise)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, light_turquoise)
            dpg.add_theme_color(dpg.mvThemeCol_Tab, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, mint)
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, dark_mint)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, cool_gray)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, blue)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, earthy_yellow)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (232, 49, 81))
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (35, 35, 35, 200))

        # Elements rounding
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)

        with dpg.theme_component(dpg.mvCombo):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)

        with dpg.theme_component(dpg.mvImageButton):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)

        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)

        with dpg.theme_component(dpg.mvCollapsingHeader):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)

        with dpg.theme_component(dpg.mvProgressBar):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)

        # 'Reset' button accent color
        with dpg.theme_component(dpg.mvTabButton):
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, red)

        # Disabled button theme
        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (51, 51, 55, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (51, 51, 55, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (51, 51, 55, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Text, (151, 151, 151, 255))

    with dpg.theme(tag="filepick_overlay_theme"):
        with dpg.theme_component():
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ModalWindowDimBg, bg_dim)

    with dpg.theme(tag="popup_theme"):
        with dpg.theme_component():
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)
            dpg.add_theme_color(dpg.mvThemeCol_ModalWindowDimBg, bg_dim)


def load_fonts() -> None:
    path = helpers.resource_path("resources/fonts/JetBrainsMonoNL-Regular.ttf")
    with dpg.font_registry():
        with dpg.font(str(path), 16, tag="JetBrainsMono"):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Vietnamese)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Korean)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Thai)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)


def load_icons() -> None:
    path = helpers.resource_path("resources/icons/checkmark.png")
    width, height, _, data = dpg.load_image(str(path))
    with dpg.texture_registry():
        dpg.add_static_texture(
            width=width, height=height, default_value=data, tag="checkmark"
        )
