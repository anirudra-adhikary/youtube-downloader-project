import asyncio

import flet as ft

from main import download_video, search_and_select, show_formats


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
        # print(f"GUI>> {formats}")
        if not formats:
            return
        for i in formats:
            display = f"{i.get('resolution'):<10} |   {i.get('extension'):<8} |   {i.get('content'):<8} |   {i.get('size')}"
            dropdown_format_select.options.append(
                ft.DropdownOption(
                    text=display,
                    key=i.get("id"),
                ),
            )
        dropdown_format_select.visible = True
        page.update()

    def handle_dropdown_select(e):
        nonlocal format_selection
        print(f"GUI event={e}")
        format_selection = e.data
        download_button.visible = True
        page.update()

    async def click_download(e):
        progress_bar.visible = True
        page.update()
        await asyncio.sleep(1)  # time to update ui
        nonlocal url, format_selection
        print(f"GUI>> url={url}, selected_format={format_selection}")
        ret_val = download_video(url, format_selection)
        if ret_val:
            page.add(ft.Text("Download Complete"))
            progress_bar.value = 1.0
            page.update()

    # =============== GUI elements ================ #
    search_link = ft.TextField(
        label="Search YouTube or Put download link",
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
        visible=False,
        text="Select Format",
        on_select=handle_dropdown_select,
    )
    progress_bar = ft.ProgressBar(visible=False)
    download_button = ft.Button(
        content="download",
        visible=False,
        on_click=click_download,
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
