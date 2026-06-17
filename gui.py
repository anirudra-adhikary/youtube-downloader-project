import asyncio

import flet as ft

from main import download_video, search_and_select, show_formats


def main(page: ft.Page):
    url = ""
    format_selection = 18

    # =============== Interaction Functions =============== #
    async def process_input_is_link_or_search():
        user_input = search_link.value
        if not user_input.startswith(("http://", "https://", "www.")):
            loading_shimmer.visible = True
            page.update()
            await asyncio.sleep(3)  # time to reflect loading_shimmer
            search_string_submited()  # search & select video link
            loading_shimmer.visible = False
        else:
            loading_circle.visible = True
            page.update()
            await asyncio.sleep(3)  # time to reflect loading_circle
            link_submited()  # select format then download
            loading_circle.visible = False
        page.update()

    def search_string_submited():
        search = search_link.value
        if not search:
            return
        result = search_and_select(search, cli=False)
        if not result:
            return
        for i in result:
            # i = {"title": title,"channel": uploader,"duration": duration,"download_url": entry.get("url")}
            videos_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SMART_DISPLAY_OUTLINED),
                    title=ft.Text(
                        i.get("title"), no_wrap=True, overflow=ft.TextOverflow.FADE
                    ),
                    subtitle=f"by {i.get('channel')} | (duration: {i.get('duration')})",
                    data=i.get("download_url"),
                    on_click=handle_tile_click,
                )
            )
        videos_list.visible = True
        page.update()

    async def handle_tile_click(e):
        print(e)
        print(e.control)
        url = e.control.data
        print(url)
        search_link.value = url
        await process_input_is_link_or_search()

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
            download_complete_indicator.visible = True
            progress_bar.value = 1.0
            page.update()

    def clear_all():
        progress_bar.visible = False
        download_button.visible = False
        videos_list.controls.clear()
        dropdown_format_select.visible = False
        download_complete_indicator.visible = False
        search_link.value = ""
        page.update()

    # =============== GUI elements ================ #
    search_link = ft.TextField(
        label="Search YouTube or Put download link",
        autofocus=True,
        expand=True,
        on_submit=process_input_is_link_or_search,
        suffix_icon=ft.IconButton(
            ft.Icons.SEARCH,
            on_click=process_input_is_link_or_search,
        ),
    )
    videos_list = ft.ListView(
        divider_thickness=10,
        scroll=ft.ScrollMode.AUTO,
    )
    loading_shimmer = ft.Shimmer(
        base_color=ft.Colors.with_opacity(0.3, ft.Colors.GREY_400),
        visible=False,
        highlight_color=ft.Colors.WHITE_60,
        content=ft.Column(
            [ft.Container(height=54, bgcolor=ft.Colors.GREY_300) for _ in range(5)]
        ),
    )
    loading_circle = ft.ProgressRing(visible=False)
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
    download_complete_indicator = ft.Text(
        "Download Completed",
        visible=False,
    )
    clear_button = ft.Button("Clear All", on_click=clear_all)

    # =============== main GUI part ================ #
    page.window.width = 600
    page.window.height = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.appbar = ft.AppBar(title="YouTube Downloader", center_title=True)
    page.add(
        search_link,
        loading_shimmer,
        videos_list,
        loading_circle,
        dropdown_format_select,
        download_button,
        progress_bar,
        download_complete_indicator,
        clear_button,
    )


ft.run(main=main)
