
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
         "01",
         "02",
         "03",
         "04",
         "05",
         "06",
         "07",
         "08",
         "09",
         "10",
         "11",
         "12",
         "13",
         "14",
         "15",
         "16",
         "17",
         "18",
         "19",
         "20",
         "21",
         "22",
         "23",
     ], description="Select a time for the brew steps to start running."),
     Property.Select(label="AutoNext",options=["Yes","No"], description="Automatically move to next step (Yes) or pause after Notification (No)")
])

class StepSchedule(CBPiStep):
    
    async def NextStep(self, **kwargs):
        await self.next()

    async def on_timer_done(self,timer):
        self.summary = 'Brew time!'

        if self.AutoNext == True:
            self.cbpi.notify(self.name, 'Moving to the next step.', NotificationType.INFO)
            await self.next()
        else:
            self.cbpi.notify(self.name, 'Brew time. Hit the next step!', NotificationType.INFO, action=[NotificationAction("Next Step", self.NextStep)])
            await self.push_update()

    async def on_timer_update(self,timer, seconds):
        await self.push_update()

    async def on_start(self):
        self.summary='Waiting to brew...'
        self.AutoNext = False if self.props.get("AutoNext", "No") == "No" else True
        if self.timer is None:
            self.timer = Timer(1 ,on_update=self.on_timer_update, on_done=self.on_timer_done)
        await self.push_update()

    async def on_stop(self):
        await self.timer.stop()
        self.summary = 'Not ready yet.'
        await self.push_update()

    async def run(self):
        while self.running == True:
            await asyncio.sleep(1)
            current_time = now.strftime("%H")
            if self.props.get("scheduleTime", "00") == current_time and self.timer.is_running is not True:
                self.timer.start()
                self.timer.is_running = True

        return StepResult.DONE

def setup(cbpi):
    cbpi.plugin.register("Schedule Steps", StepSchedule)
    pass