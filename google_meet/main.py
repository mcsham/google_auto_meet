import os
from asyncio import sleep
from datetime import datetime

import pyperclip
from loguru import logger

from browser import Browser

# init system log traker (error, info)
log_path = os.path.join(os.getcwd(), 'logs')
if not os.path.exists(log_path):
    os.mkdir(log_path)
logger.add(os.path.join(log_path, "file_{time}.log"), format="{time} {level} {message}", level="INFO")


class GoogleMeet(Browser):

    async def _auto_stay(self) -> None:
        """
        Find button I'm staying on and click it
        :return: None
        """
        button_i_stay = self._page.locator('button[data-mdc-dialog-initial-focus=""]')
        if await button_i_stay.is_visible():
            await button_i_stay.click()
            await sleep(0.5)

    async def get_all_people_nickname(self) -> list:
        """
        Find all the people in the meeting and return their nicknames
        :return: List of all nicknames in the meeting
            if list is empty, return empty list
        """
        return [await i.get_attribute('aria-label') for i in await self._page.locator('div[role="listitem"]').all()]

    async def _save_mini_logs(self) -> None:
        """
        Save the mini_logs to a file
            format:
                2025/02/10 12:00 nickname1
                2025/02/10 12:05 nickname2
                ...
        :return:
        """
        with open(self.file_name, 'w') as f:
            f.write('\n'.join(self.peoples))

    async def _wait_new_people(self) -> None:
        """
        Wait until everyone in the meeting has joined.
        :return: None
        """
        while self.count_user > 0:
            await sleep(1)
            try:
                await self._auto_stay()
                all_nicknames_in_room = await self.get_all_people_nickname()
                new_person = self._page.locator('div[role="listitem"] div[data-is-touch-wrapper="true"] button').first
                if not await new_person.is_visible():
                    continue
                new_person_label = await new_person.get_attribute('aria-label')
                for nick_name in all_nicknames_in_room:
                    if nick_name in new_person_label:
                        if not any([nick_name in i for i in self.peoples]):
                            self.peoples.append(f'{datetime.now().strftime("%Y/%m/%d %H:%M:%S")} {nick_name}')
                            logger.info(f'New person {nick_name} found')
                            if self.simple_log:
                                await self._save_mini_logs()
                        await new_person.click()
                        self.count_user -= 1
                        break
            except:
                pass

    async def _off_microphone_and_camera(self) -> None:
        """
        Locates and presses the microphone and camera mute buttons.
        :return: None
        """
        for _ in range(2):
            await self._page.locator('[data-is-muted="false"]').first.click()
            await sleep(0.3)

    async def _join_in_room(self) -> None:
        """
        Find and press the join button.
        :return: None
        """
        await self._page.locator('button[data-promo-anchor-id]').last.click()

    async def _open_people_menu(self) -> None:
        """
        Open the people menu.
        This menu will track the appearance of new meeting participants.
        :return: None
        """
        await self._page.locator('button', has_text='people').click()

    async def _login(self) -> bool:
        """
        Authorization in your Google account
        :return: bool True if the login was successful
            False otherwise
        """
        sing_in = self._page.locator('a[data-g-action="sign in"]').first
        if not await sing_in.is_visible():
            return False
        await sing_in.click()
        await sleep(3)
        login_menu = self._page.locator(f'div[data-identifier="{self._user_login}"]')
        if await login_menu.is_visible():
            await login_menu.click()
        else:
            input_field = self._page.locator('input[aria-label="Email or phone"]')
            await input_field.press_sequentially(self._user_login)
            await input_field.press('Enter')
        await sleep(5)

        input_field = self._page.locator('input[name="Passwd"]')
        if await input_field.is_visible():
            await input_field.press_sequentially(self._user_password)
            await input_field.press('Enter')
            await sleep(5)
            return True
        return False

    async def new_meeting(self) -> None:
        """
        Create a new meeting.
        :return: None
        """
        await self.goto('https://meet.google.com')
        await self._login()
        await self._page.locator('button[autofocus="autofocus"]').click()
        await self._page.locator('li[role="menuitem"]').nth(-2).click()

    async def open_exists_url(self, url) -> None:
        """
        Open an existing url.
        :param url:
        :return:
        """
        await self.goto(url)
        button_back = self._page.locator('button', has_text='Return to home screen')
        if await button_back.is_visible():
            await button_back.click()
            await sleep(2)
            await self._login()
            await self.goto(url)
        await self._join_in_room()

    async def open_meet(self, url: str = None, count_user: int = -1) -> None:
        """
        Open google meet link
        :param url: str or None
            if url is None, it will open the new meet page
        :param count_user: int default = -1
            if count_user is -1, system wait unlimited users (1_000_000)
        :return: None
        """
        if count_user == -1:
            self.count_user = 1_000_000

        await (self.new_meeting() if url is None else self.open_exists_url(url))

        await self._off_microphone_and_camera()
        await self._open_people_menu()
        pyperclip.copy(self._page.url)
        logger.info(f'Meeting url: {self._page.url};')
        logger.info(f'The meeting url is copied to the keyboard buffer;')
        await self._wait_new_people()

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.count_user = 0
        self.peoples = []
        self.simple_log = kwargs.get('simple_log', False)
        self._user_login = kwargs.get('login')
        self._user_password = kwargs.get('password')
        path = os.path.join(os.getcwd(), 'mini_logs')
        if self.simple_log and os.path.exists(path):
            os.makedirs(path)
        self.file_name = os.path.join(path, datetime.now().strftime("%Y_%m_%d_%H_%M_%S.txt"))
