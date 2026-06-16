import flet as ft

from main import download_audio, download_video, show_formats


def main(page: ft.Page):
    url = ""
    format_selection = 18

    # =============== Interaction Functions =============== #
    def link_submited():
        nonlocal url
        url = search_link.value
        print(f"GUI> {url}")
        if not url:
            return
        formats = show_formats(url, cli=False)
        print(f"GUI>> {formats}")
        if not formats:
            return
        for i in formats:
            display = f"{i.get('resolution'):<10} |   {i.get('extension'):<8} |   {i.get('content'):<8} |   {i.get('size')}"
            dropdown_format_select.options.append(
                ft.DropdownOption(
                    ## TODO: Adjusting json
                    text=display,
                    key=i.get("id"),
                ),
            )
        dropdown_format_select.disabled = False
        page.update()

    ## TODO
    def handle_search_video():
        pass

    def handle_dropdown_select(e):
        nonlocal format_selection
        print(f"GUI event={e}")
        format_selection = e.data
        download_button.visible = True
        download_button.disabled = False
        page.update()

    def handle_button_click(e):
        progress_bar.visible = True
        page.update()
        nonlocal url, format_selection
        print(f"GUI>> url={url}, selected_format={format_selection}")
        ret_val = download_video(url, format_selection)
        if ret_val:
            page.add(ft.Text("Download Complete"))
            download_button.disabled = True

    # =============== GUI elements ================ #
    search_link = ft.TextField(
        label="Put download link",
        autofocus=True,
        expand=True,
        on_submit=link_submited,
        suffix_icon=ft.IconButton(
            ft.Icons.DOWNLOAD,
            on_click=link_submited,
        ),
    )
    # content_list = (ft.ListView(),) ##TODO
    dropdown_format_select = ft.Dropdown(
        expand=True,
        disabled=True,
        text="Select Format",
        on_select=handle_dropdown_select,
    )
    progress_bar = ft.ProgressBar(visible=False)
    download_button = ft.Button(
        content="download",
        disabled=True,
        expand=True,
        on_click=handle_button_click,
    )

    # =============== main GUI part ================ #
    page.window.width = 600
    page.window.height = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.appbar = ft.AppBar(title="YouTube Downloader", center_title=True)
    page.add(
        search_link,
        dropdown_format_select,
        download_button,
        progress_bar,
    )


ft.run(main=main)
