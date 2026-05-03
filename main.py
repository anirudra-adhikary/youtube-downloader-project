import flet as ft
from ytdlp_impl import download_video


def main(page: ft.Page):
    page.title = "Youtube Downloader"
    page.window.width, page.window.height = 500, 580

    url = ft.TextField(label="Enter the Link", expand=True)
    status = ft.Text("", alignment=ft.Alignment.CENTER)

    def on_dl(e):
        if not url.value:
            return
        status.value = "Downloading..."
        page.update()
        try:
            download_video(url.value)
            status.value = "✅ Successfully downloaded!"
            status.color = ft.Colors.GREEN
        except Exception as ex:
            status.value = f"❌ Error: {ex}"
            status.color = ft.Colors.RED
        page.update()

    page.add(
        ft.Column(
            [
                url,
                ft.Button(
                    "Download",
                    on_click=on_dl,
                ),
                status,
            ]
        )
    )


if __name__ == "__main__":
    ft.run(main)
