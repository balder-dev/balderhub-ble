from typing import Union, Any

import asyncio
import threading
import time

import logging

logger = logging.getLogger(__name__)


class AsyncManagerThread:
    """
    Base AsyncManagerThread that is used to manage the async Bleak library within a sync context that is required for
    Balder.

    This thread can be created multiple times within one instance of this object. Nevertheless it needs to be shut down
    before it can be started again.
    """

    def __init__(self):
        self._async_loop = asyncio.new_event_loop()
        self._thread: Union[threading.Thread, None] = None

    def is_alive(self):
        """
        :return: returns true if the thread is alive, False otherwise
        """
        return self._thread.is_alive()

    def __threaded_method(self):
        asyncio.set_event_loop(self._async_loop)
        self._async_loop.run_forever()

    def start(self) -> None:
        """
        This method starts the async manager thread. It raises an ValueError in case the thread is already running.
        """
        if self._thread is not None:
            raise ValueError('thread was already started before -> can not restart it')
        self._thread = threading.Thread(target=self.__threaded_method, daemon=True)  # TODO should we use deamon??
        self._thread.start()

    def run_in_async_thread_and_wait_for_result(self, async_callback, *args) -> Any:
        """
        Helper method to run any async callback within the special async manager thread
        :param async_callback: the async callback to run
        :param args: all arguments to pass to the async callback
        :return: the result of the async callback
        """
        async def execute():
            await asyncio.sleep(0.01)
            result = await async_callback(*args)
            await asyncio.sleep(0.01)
            return result

        future = asyncio.run_coroutine_threadsafe(execute(), self._async_loop)
        return future.result()

    def _run_stop_command(self, timout_sec: float = 10) -> None:
        start_time = time.perf_counter()
        async def execute():
            await asyncio.sleep(0.01)
            tasks = [t for t in asyncio.all_tasks(self._async_loop) if t is not asyncio.current_task()]
            logger.debug(f'found {len(tasks)} active tasks -> cancel them')
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.debug('all active tasks canceled')
            return None

        future = asyncio.run_coroutine_threadsafe(execute(), self._async_loop)
        future.result()
        logger.debug('shutdown finished')
        logger.debug('stop loop from main thread too')
        self._async_loop.call_soon_threadsafe(self._async_loop.stop)
        logger.debug('loop from main thread stopped')

        # wait for loop
        while self._async_loop.is_running():
            if time.perf_counter() - start_time > timout_sec:
                raise TimeoutError('was unable to stop async-thread')
            time.sleep(0.01)
        self._async_loop.close()

    def stop_and_wait_for_thread(self, timeout: float = 10) -> None:
        """
        This method stops the async manager thread and waits for its termination.

        :param timeout: maximum time in seconds to wait for thread
        """
        start_time = time.perf_counter()
        self._run_stop_command()
        self._thread.join(timeout=timeout - (time.perf_counter() - start_time))
        if self._thread.is_alive():
            raise TimeoutError('was unable to stop async-thread')
