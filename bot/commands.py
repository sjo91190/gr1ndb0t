import time
import os
from random import choice


class BotCommands:
    def __init__(self, logger, sock, channel):
        self.logger = logger
        self.sock = sock
        self.channel = channel

        self.prefix = f"PRIVMSG #{self.channel} :"

    def __clear_chat(self, sender: str) -> bool:
        self.logger.info(f"COMMAND RECEIVED - !clear - Sender: {sender}")
        self.sock.send(f"{self.prefix}/clear\r\n".encode("utf-8"))

        return True

    def __del_message(self, msg: str, sender: str, msg_id: str) -> bool:
        self.sock.send(f"{self.prefix}/delete {msg_id}\r\n".encode("utf-8"))
        self.sock.send(f"{self.prefix}{sender}: MESSAGE DELETED: {msg}\r\n".encode("utf-8"))

        return True

    def lurker(self, msg: str, sender: str) -> bool:
        if msg.startswith("!lurk"):
            self.logger.info(f"COMMAND RECEIVED - !lurk - Sender: {sender}")
            self.sock.send(f"{self.prefix}Yo, {sender}! {self.channel} wanted me to tell you he thinks you're awesome and thanks for the lurk! Hope you can make it back!!!\r\n".encode("utf-8"))

            return True

    def switch_code(self, msg: str, sender: str) -> bool:
        if msg.startswith("!fc"):
            self.logger.info(f"COMMAND RECEIVED - !fc - Sender: {sender}")
            self.sock.send(f"{self.prefix}{self.channel} told me to tell you his Switch Friend Code is: 8562-2808-8201\r\n".encode('utf-8'))

            return True

    def updog(self, msg: str, sender: str) -> bool:
        if "updog" in msg.lower() or "up dog" in msg.lower():
            self.logger.info(f"COMMAND RECEIVED - updog lul - Sender: {sender}")
            self.sock.send(f"{self.prefix}not much, u? {sender}\r\n".encode("utf-8"))

            return True

    def greet(self, sender, greet_data):
        if sender.lower() in greet_data['status'].keys():
            if not greet_data['status'][sender.lower()]:
                self.sock.send(f"{self.prefix}{greet_data['msg'][sender.lower()]}\r\n".encode('utf-8'))
                greet_data['status'][sender.lower()] = True

        return greet_data

    def raid_msg(self, raider: str, raid_party: str):
        self.logger.info(f"RAID RECEIVED - {raider} - {raid_party}")
        self.sock.send(f"{self.prefix}samgri2Raid samgri2Raid Everyone be cool, stay calm, and pretend that you like samgrind because {raid_party}!!! samgri2Raid samgri2Raid\r\n".encode('utf-8'))
        time.sleep(1)
        self.sock.send(f"{self.prefix}We appreciate the raid, {raider} <3 Everyone go and smash that follow button at https://twitch.tv/{raider}\r\n".encode('utf-8'))

    def nightbot(self, sender):
        if sender.lower() == "nightbot":
            response = ['@nightbot chill tf out dude',
                        '@nightbot stop spamming or im going to ban you',
                        '@nightbot theres not enough room here for two bots, scram loser',
                        'thanks @nightbot i love you']
            self.sock.send(f"{self.prefix}{choice(response)}\r\n".encode("utf-8"))


class ChannelRewards(BotCommands):

    def get_reward(self, reward_uuid: str):
        print(f"REWARD ID from commands: {reward_uuid}")
        reward_dict = {
            os.getenv("OUIJA_PHRASE"): self.ouija_phrase,
            os.getenv("HYDRATE"): self.hydrate
        }

        if reward_dict.get(reward_uuid) is not None:
            return reward_dict.get(reward_uuid)
        else:
            self.sock.send(f"{self.prefix}Unknown Reward UUID\r\n".encode("utf-8"))

        return None

    def ouija_phrase(self, msg: str, sender: str) -> bool:
        self.logger.info(f"REDEMPTION RECEIVED - Ouija Phrase - Sender: {sender} - Phrase: {msg}")
        self.sock.send(f"{self.prefix}Phrase submission received! -- {msg}\r\n".encode("utf-8"))

        return True

    def hydrate(self) -> bool:
        self.logger.info(f"REDEMPTION RECEIVED - Hydrate")
        self.sock.send(f"{self.prefix}Hydrate Received!!!\r\n".encode("utf-8"))

        return True


class AllCommands(ChannelRewards):
    pass
