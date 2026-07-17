import asyncio
from dataclasses import dataclass, field
from flet.controls.core.column import Column

import flet as ft

from main import download_video, search_and_select, show_formats


@ft.observable
@dataclass
class DownloaderViewModel:
    # --- The Model (Pure State) ---
    search_query: str = ""
    url: str = ""
    format_selection: int | None = None

    search_results: list[dict] | list = field(default_factory=list)
    available_formats: list[dict] | list = field(default_factory=list)

    # UI State Toggles
    is_searching: bool = False
    is_fetching_formats: bool = False
    is_downloading: bool = False
    download_complete: bool = False

    # --- The ViewModel (Logic) ---
    async def process_input(self, input_text: str):
        self.search_query = input_text
        self.reset_states()

        if not input_text.startswith(("http://", "https://", "www.")):
            await self._handle_search(input_text)
        else:
            await self._handle_link(input_text)

    async def _handle_search(self, search_text: str):
        self.is_searching = True
        await asyncio.sleep(1)
        results = search_and_select(search_text, num_results=10, cli=False)
        if results:
            self.search_results = results

        self.is_searching = False

    async def _handle_link(self, link: str):
        self.url = link
        self.is_fetching_formats = True
        await asyncio.sleep(1)
        formats = show_formats(link, cli=False)
        if formats:
            self.available_formats = formats
        self.is_fetching_formats = False

    def select_format(self, format_id: int):
        self.format_selection = format_id

    async def download(self):
        if not self.url or not self.format_selection:
            return
        self.is_downloading = True
        await asyncio.sleep(1)
        ret_val = download_video(self.url, self.format_selection)
        if ret_val:
            self.download_complete = True
        self.is_downloading = False

    def clear_all(self):
        self.search_query = self.url = ""
        self.format_selection = None
        self.reset_states()

    def reset_states(self):
        self.search_results = self.available_formats = []
        self.is_searching = False
        self.is_fetching_formats = False
        self.is_downloading = False
        self.download_complete = False


@ft.component
def SearchTiles(i):
    value, _ = ft.use_state(DownloaderViewModel())

    async def tile_clicked(e: ft.Event[ft.ListTile]):
        value.select_format(e.control.value)

    return ft.ListTile(
        leading=ft.Icon(ft.Icons.SMART_DISPLAY_OUTLINED),
        title=ft.Text(i.get("title"), no_wrap=True, overflow=ft.TextOverflow.FADE),
        subtitle=f"by {i.get('channel')} | (duration: {i.get('duration')})",
        data=i.get("download_url"),
        on_click=tile_clicked,
    )


@ft.component
def SearchView() -> Column:
    value, _ = ft.use_state(DownloaderViewModel())

    async def handle_submit(e: ft.Event[ft.SearchBar]):
        input_str: str = e.data
        print(f"Submit: {input_str}")
        if input_str:
            await value.process_input(input_str)

    return ft.Column(
        [
            ft.SearchBar(
                view_elevation=4,
                bar_hint_text="Search YouTube or Put download link...",
                view_leading=ft.Icon(ft.Icons.SEARCH),
                bar_leading=ft.Icon(ft.Icons.SEARCH),
                on_submit=handle_submit,
                bar_trailing=[
                    ft.Icon(ft.Icons.SEARCH_ROUNDED),
                ],
            ),
            ft.Shimmer(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(height=54, bgcolor=ft.Colors.GREY_300),
                                ft.Column(
                                    controls=[
                                        ft.Container(
                                            height=10, bgcolor=ft.Colors.GREY_300
                                        )
                                        for _ in range(3)
                                    ],
                                ),
                            ],
                        )
                        for _ in range(10)
                    ],
                    scroll=ft.ScrollMode.ALWAYS,
                ),
                base_color=ft.Colors.with_opacity(0.3, ft.Colors.GREY_400),
                highlight_color=ft.Colors.WHITE_60,
                # visible=not value.is_searching,
                visible=True,
            ),
            ft.Column(
                controls=[SearchTiles(i) for i in value.search_results],
                scroll=ft.ScrollMode.ALWAYS,
            ),
        ]
    )


@ft.component
def DownloadOptions(i):
    return ft.DropdownOption(
        text=f"{i.get('resolution'):<10} | {i.get('extension'):<8} | {i.get('size')}",
        key=i.get("id"),
    )


@ft.component
def DownloaderView() -> Column:
    value, _ = ft.use_state(DownloaderViewModel())

    async def format_selected(e):
        value.select_format(e.control.value)

    async def start_download(e):
        await value.download()

    return ft.Column(
        [
            ft.Dropdown(
                options=[DownloadOptions(i) for i in value.available_formats],
                visible=len(value.available_formats) > 0,
                on_select=format_selected,
                label="Select Format",
            ),
            # Download Controls
            ft.Button(
                "Download",
                visible=(
                    value.format_selection is not None
                    and not value.is_downloading
                    and not value.download_complete
                ),
                on_click=start_download,
            ),
            ft.ProgressBar(visible=value.is_downloading),
            ft.Text(
                "✅ Download Completed",
                visible=value.download_complete,
                color=ft.Colors.GREEN,
            ),
            ft.Button(
                "Clear All",
                on_click=lambda e: value.clear_all(),
                visible=len(value.search_results) > 0
                or len(value.available_formats) > 0,
            ),
        ]
    )


# =============== main GUI part ================ #
def main(page: ft.Page):
    page.window.width = 600
    page.window.height = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # page.scroll=ft.ScrollMode.AUTO
    page.appbar = ft.AppBar(title=ft.Text("YouTube Downloader"), center_title=True)

    # ❌ THE ISSUE: page.add() is for the old imperative controls
    # page.add(DownloaderView())

    # ✅ THE FIX: page.render() mounts declarative components
    page.render(SearchView)


if __name__ == "__main__":
    ft.run(main)
