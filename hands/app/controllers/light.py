import asyncio
from kasa import Discover

class Light:

  def __init__(self, host, username, password):
    self.host = host
    self.username = username
    self.password = password

  async def _get_instance(self):
    dev = await Discover.discover_single(host=self.host, username=self.username, password=self.password)
    return dev
  
  async def _handle_state(self, state):
    dev = await self._get_instance()
    if state == 'on':
      await dev.turn_on()
      await dev.update()
    elif state == 'off':
      await dev.turn_off()
      await dev.update()
    else:
      if dev.is_on:
        await dev.turn_off()
        await dev.update()
      else:
        await dev.turn_on()
        await dev.update()
    await dev.disconnect()

  def turn_on(self):
    asyncio.run(self._handle_state("on"))

  def turn_off(self):
    asyncio.run(self._handle_state("off"))

  def toggle(self):
    asyncio.run(self._handle_state("toggle"))