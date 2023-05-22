# from channels.generic.websocket import WebsocketConsumer,AsyncJsonWebsocketConsumer
# from channels.db import database_sync_to_async
# from asgiref.sync import async_to_sync
# import json


# # @database_sync_to_async
# # def create_notification(receiver,typeof="task_created",status="unread"):
# #     notification_to_create=notifications.objects.create(user_revoker=receiver,type_of_notification=typeof)
# #     print('I am here to help')
# #     return (notification_to_create.user_revoker.username,notification_to_create.type_of_notification)

# class NewConsumer(AsyncJsonWebsocketConsumer):
#     async def connect(self):
#         self.room_name = 'test_consumer'
#         self.room_group_name = 'test_consumer_group'
#         await(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()
#         await self.send(text_data=json.dumps({'status' : 'connected from django channel'}))

#     async def receive(self, text_data):
#         print(text_data)
#         await self.send(text_data = json.dumps({'status':'We got you'}))

#     async def disconnect(self, *args, **kwargs):
#         print('disconnected')

#     async def send_notification(self, event):
#         print('send_notification')
#         print(event)
#         data = json.loads(event.get('value'))
#         await self.send(text_data = json.dump(data))
#         print('send_notification')





# myapp/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the "notification" group
        await self.channel_layer.group_add("notification", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the "notification" group
        await self.channel_layer.group_discard("notification", self.channel_name)

    async def notify_manager(self, event):
        # Send a notification to the manager
        await self.send(text_data=json.dumps({
            "type": "notification",
            "message": event["message"],
        }))
    async def notify_customer(self, event):
        # Send a notification to the manager
        await self.send(text_data=json.dumps({
            "type": "notification",
            "customer": event["customer"],
            "status":event["status"]
        }))
