
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.api import *
from cbpi.api.step import CBPiStep, StepResult
from cbpi.api.dataclasses import NotificationAction, NotificationType
from datetime import datetime

logger = logging.getLogger(__name__)

@parameters([
     Property.Select(label="scheduleTime", options=[
         "01:00:00",
         "02:00:00",
         "03:00:00",
         "04:00:00",
         "05:00:00",
         "06:00:00",
         "07:00:00",
         "08:00:00",
         "09:00:00",
         "10:00:00",
         "11:00:00",
         "12:00:00",
         "13:00:00",
         "14:00:00",
         "15:00:00",
         "16:00:00",
         "17:00:00",
         "18:00:00",
         "19:00:00",
         "20:00:00",
         "21:00:00",
         "22:00:00",
         "23:00:00",
     ], description="Select a time for the brew steps to start running.")
])

class StepSchedule(CBPiStep):
    
    async def NextStep(self, **kwargs):
        await self.next()

    async def on_start(self):
        await self.push_update()

    async def run(self):
        while self.running == True:
            await asyncio.sleep(1)
            current_time = now.strftime("%H")
            if current_time == scheduleTime[:2]:
                self.cbpi.notify(self.name, "It's brew time!", NotificationType.INFO)
                await self.next()

def setup(cbpi):
    cbpi.plugin.register("Schedule Steps", StepSchedule)
    pass