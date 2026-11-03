import asyncio
from dataclasses import dataclass, field
import logging

import flet as ft
from flet.controls.core.column import Column

from main import download_video, search_and_select, show_formats

logging.basicConfig(level=logging.INFO)
logging.getLogger("flet").setLevel(logging.DEBUG)


@ft.observable
@dataclass
class DownloaderViewModel:
    # --- The Model (Pure State) ---
    search_query: str = ""
    url: str = ""
    selected_download_format: str | None = None  # Changed to str to support formats like "137+140"

    search_results: list = field(default_factory=list)
    available_formats: list = field(default_factory=list)

    # UI State Toggles
    is_searching: bool = False
    is_fetching_formats: bool = False
    is_downloading: bool = False
    download_complete: bool = False

    # --- The ViewModel (Logic) ---

    async def _handle_search(self, search_text: str):
        self.search_query = search_text
        self.is_searching = True
        
        # Pushes the blocking network call to a background thread
        results = await asyncio.to_thread(search_and_select, search_text, 10, False)
        
        if results:
            self.search_results = results

        self.is_searching = False

    async def _handle_link(self, link: str):
        self.url = link
        self.is_fetching_formats = True
        
        # Pushes the blocking network call to a background thread
        formats = await asyncio.to_thread(show_formats, link, False)
        
        if formats and formats != ["no data"]:
            self.available_formats = formats
            
        self.is_fetching_formats = False

    def select_format(self, format_id: str):
        self.selected_download_format = format_id

    async def download(self):
        storage = ft.StoragePaths()
        if not self.url or not self.selected_download_format:
            return
        
        self.is_downloading = True
        sys_download_path = await storage.get_downloads_directory()
        print(sys_download_path)
        
        # Pushes the blocking download to a background thread
        ret_val = await asyncio.to_thread(
            download_video, self.url, self.selected_download_format, False, str(sys_download_path)
        )
        
        if ret_val:
            self.download_complete = True
            
        self.is_downloading = False

    def clear_all(self):
        self.search_query = self.url = ""
        self.selected_download_format = None
        self.reset_states()

    def reset_states(self):
        self.search_results = []
        self.available_formats = []
        self.is_searching = False
        self.is_fetching_formats = False
        self.is_downloading = False
        self.download_complete = False


@ft.component
def SearchTiles(i, app_state: DownloaderViewModel):
    async def tile_clicked(e: ft.Event[ft.ListTile]):
        print("click", e.control.data)
        ft.context.page.navigate("/download")
        await app_state._handle_link(e.control.data)

    return ft.ListTile(
        leading=ft.Icon(ft.Icons.SMART_DISPLAY_OUTLINED),
        title=ft.Text(i.get("title"), no_wrap=True, overflow=ft.TextOverflow.FADE),
        subtitle=f"by {i.get('channel')} | (duration: {i.get('duration')})",
        data=i.get("download_url"),
        on_click=tile_clicked,
    )


@ft.component
def SearchView(app_state: DownloaderViewModel) -> Column:
    async def handle_submit(e: ft.Event[ft.SearchBar]):
        app_state.reset_states()
        input_str = str(e.data)
        print(f"Submit: {input_str}")
        
        if input_str and not input_str.startswith(("http://", "https://", "www.")):
            await app_state._handle_search(input_str)
        else:
            ft.context.page.navigate("/download")
            await app_state._handle_link(input_str)

    return ft.Column(
        spacing=25,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.SearchBar(
                view_elevation=4,
                bar_hint_text="Search YouTube or Put download link...",
                bar_leading=ft.Icon(ft.Icons.SEARCH, margin=ft.Margin(12, 1, 5)),
                autofocus=True,
                on_submit=handle_submit,
            ),
            ft.Shimmer(
                ft.Column(
                    controls=[
                        ft.Container(height=50, bgcolor=ft.Colors.GREY_300)
                        for _ in range(10)
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    margin=ft.Margin(8, 0, 8),
                    expand=True,
                ),
                base_color=ft.Colors.with_opacity(0.3, ft.Colors.GREY_400),
                highlight_color=ft.Colors.WHITE_60,
                visible=app_state.is_searching,
            ),
            ft.Column(
                controls=[SearchTiles(i, app_state) for i in app_state.search_results],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
        ],
    )


@ft.component
def DownloadOptions(i):
    return ft.DropdownOption(
        text=f"{i.get('resolution'):<10} | {i.get('extension'):<8} | {i.get('size'):<8} | {i.get('content')}",
        key=i.get("id"),
    )


@ft.component
def DownloaderView(app_state: DownloaderViewModel) -> Column:
    def format_selected(e):
        app_state.select_format(e.control.value)

    async def start_download(e):
        try:
            await app_state.download()
        except Exception as ex:  # Fixed exception shadowing syntax error here
            ft.context.page.show_dialog(
                ft.SnackBar(ft.Text(f"Error Downloading: {ex}", color=ft.Colors.RED))
            )
            app_state.clear_all()

    def reset_click(e):
        app_state.clear_all()
        ft.context.page.navigate("/")

    return ft.Column(
        spacing=30,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[  # pyright: ignore[reportArgumentType]
            ft.ProgressRing(
                visible=app_state.is_fetching_formats,
                padding=90,
                tooltip="fetching available formats ...",
            ),
            ft.Dropdown(
                options=[DownloadOptions(i) for i in app_state.available_formats],
                visible=len(app_state.available_formats) > 0,
                margin=ft.Margin(0, 30, 0, 20),
                on_select=format_selected,
                label="Select Format",
                value=str(app_state.selected_download_format) if app_state.selected_download_format else None,
            ),
            ft.Button(
                "Download",
                visible=(
                    app_state.selected_download_format is not None
                    and not app_state.is_downloading
                    and not app_state.download_complete
                ),
                on_click=start_download,
            ),
            ft.ProgressBar(
                visible=app_state.is_downloading,
                tooltip="downloading...",
                height=20,
                margin=25,
            ),
            ft.Text(
                "✅ Download Completed",
                visible=app_state.download_complete,
                color=ft.Colors.GREEN,
            ),
            ft.Button(
                "Clear All",
                on_click=reset_click,
            ),
        ],
    )


# =============== main App View ================ #
@ft.component
def App():
    app_state, _ = ft.use_state(lambda: DownloaderViewModel())
    return ft.SafeArea(
        ft.Router(
            [
                ft.Route(index=True, component=lambda: SearchView(app_state)),
                ft.Route(path="download", component=lambda: DownloaderView(app_state)),
            ],
        ),
        expand=True,  # need for scroll
    )


def main(page: ft.Page):
    page.window.width = 500
    page.window.height = 700
    page.title = "Savit: YT Downloader"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.appbar = ft.AppBar(title=ft.Text("YouTube Downloader"), center_title=True)
    page.render(App)


if __name__ == "__main__":
    ft.run(main)