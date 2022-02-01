
# -*- coding: utf-8 -*-
import os
import asyncio
import aiohttp
from aiohttp import web
from cbpi.api.step import CBPiStep, StepResult
from cbpi.api.timer import Timer
from cbpi.api.dataclasses import Kettle, Props
from datetime import datetime
import time
from cbpi.api import *
import logging
from unittest.mock import MagicMock, patch
from socket import timeout
from typing import KeysView
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase
from voluptuous.schema_builder import message
from cbpi.api.dataclasses import NotificationAction, NotificationType
import requests
import warnings

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
        current_time = now.strftime("%H")
        self.summary='Brew time scheduled for '+self.props.get("scheduleTime", "00")
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
            if self.props.get("scheduleTime", "21") == current_time and self.timer.is_running is not True:
                self.timer.start()
                self.timer.is_running = True
        await self.push_update()
        return StepResult.DONE
    
    async def reset(self):
        self.timer = Timer(1 ,on_update=self.on_timer_update, on_done=self.on_timer_done)

def setup(cbpi):
    cbpi.plugin.register("StepSchedule", StepSchedule)
    pass