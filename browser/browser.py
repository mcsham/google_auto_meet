from loguru import logger
from playwright.async_api import async_playwright, Page, BrowserContext
from .install import install


class Browser:
    def __init__(self):
        self._playwright = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def exit(self):
        try:
            if self._page:
                await self._page.close()
            if self._context:
                await self._context.close()
        except Exception as e:
            pass

    async def init_browser(self, name='Chrome', headless=False, proxy: dict = None) -> None:
        """
        Initialise the browser.
        :param name: Chrome, Firefox
        :param headless: True or False
        :param proxy: example {'server': 'socks5://127.0.0.1:1234',},
        :return: None
        """
        await self.exit()
        try:
            if self._playwright is None:
                self._playwright = await async_playwright().start()
            arg = {
                'headless': headless,
                'locale': "en-EN",
                'user_data_dir': './user_data',
                'args': ["--start-maximized"],
                'no_viewport': True,

            }
            if proxy is not None:
                arg['proxy'] = proxy
            match name:
                case 'Chrome':
                    install(self._playwright.chromium)
                    self._context = await self._playwright.chromium.launch_persistent_context(**arg)
                case 'Firefox':
                    install(self._playwright.firefox)
                    self._context = await self._playwright.firefox.launch_persistent_context(**arg)
                case 'Webkit':
                    install(self._playwright.webkit)
                    self._context = await self._playwright.webkit.launch_persistent_context(**arg)
            await self._context.grant_permissions(permissions=['microphone','camera'])
            self._page = self._context.pages[0]
        except Exception as e:
            logger.error(f'Init browser is fail {e}')

    async def is_browser_close(self):
        return not self._page or self._page.is_closed()

    async def goto(self, url: str):
        try:
            await self._page.goto(url)
            return True
        except Exception as e:
            logger.error(f'Open url failed: {e}')
            return False
